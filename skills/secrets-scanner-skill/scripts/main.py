#!/usr/bin/env python3
"""
Secrets Scanner Skill - Main Module
Automated sensitive information scanner for API keys, passwords, tokens.

Use when auditing code security, scanning for vulnerabilities, or when user 
mentions 'security', 'vulnerability', 'CVE'.
"""

import os
import re
import math
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum


class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class SecretFinding:
    id: str
    type: str
    severity: str
    file: str
    line: int
    column: int
    match: str
    context: str
    entropy: float
    verified: bool = False
    remediation: str = ""


class SecretsScanner:
    """Advanced secrets scanner with entropy analysis and git history support."""
    
    # Entropy threshold for high-entropy string detection
    ENTROPY_THRESHOLD = 4.5
    
    # File extensions to exclude
    EXCLUDED_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.ico', '.svg',
        '.mp3', '.mp4', '.avi', '.mov',
        '.zip', '.tar', '.gz', '.rar',
        '.exe', '.dll', '.so', '.dylib',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx'
    }
    
    # Directories to exclude
    EXCLUDED_DIRS = {
        '.git', '.svn', '.hg', 'node_modules', 'vendor',
        '__pycache__', '.pytest_cache', '.tox', 'venv',
        'env', '.env', 'dist', 'build'
    }
    
    def __init__(self, verbose: bool = False, entropy_check: bool = True):
        self.verbose = verbose
        self.entropy_check = entropy_check
        self.findings: List[SecretFinding] = []
        self.files_scanned = 0
        
        # Initialize secret patterns
        self.patterns = self._init_patterns()
    
    def _init_patterns(self) -> List[Dict]:
        """Initialize secret detection patterns."""
        return [
            {
                "id": "AWS-001",
                "type": "aws_access_key",
                "severity": "CRITICAL",
                "pattern": r'AKIA[0-9A-Z]{16}',
                "description": "AWS Access Key ID",
                "remediation": "Remove key and rotate credentials immediately"
            },
            {
                "id": "AWS-002",
                "type": "aws_secret_key",
                "severity": "CRITICAL",
                "pattern": r'[\w/+=]{40}',
                "description": "AWS Secret Access Key (high entropy)",
                "entropy_check": True,
                "remediation": "Remove key and rotate credentials immediately"
            },
            {
                "id": "GITHUB-001",
                "type": "github_token",
                "severity": "HIGH",
                "pattern": r'gh[pousr]_[A-Za-z0-9_]{36,}',
                "description": "GitHub Personal Access Token",
                "remediation": "Revoke token and generate new one"
            },
            {
                "id": "SLACK-001",
                "type": "slack_token",
                "severity": "HIGH",
                "pattern": r'xox[baprs]-[0-9a-zA-Z-]+',
                "description": "Slack API Token",
                "remediation": "Revoke token in Slack admin dashboard"
            },
            {
                "id": "PRIVATE-001",
                "type": "private_key",
                "severity": "CRITICAL",
                "pattern": r'-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----',
                "description": "Private Key",
                "remediation": "Remove key, revoke and regenerate"
            },
            {
                "id": "API-001",
                "type": "generic_api_key",
                "severity": "HIGH",
                "pattern": r'(?:api[_-]?key|apikey)[\s]*[:=][\s]*["\']?[a-zA-Z0-9_\-]{16,}["\']?',
                "description": "Generic API Key",
                "remediation": "Move to environment variables or secure vault"
            },
            {
                "id": "PASS-001",
                "type": "password",
                "severity": "MEDIUM",
                "pattern": r'(?:password|passwd|pwd)[\s]*[:=][\s]*["\'][^"\']{8,}["\']',
                "description": "Hardcoded Password",
                "remediation": "Use environment variables or configuration management"
            },
            {
                "id": "JWT-001",
                "type": "jwt_token",
                "severity": "MEDIUM",
                "pattern": r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
                "description": "JWT Token",
                "remediation": "Verify token is not sensitive; rotate if necessary"
            },
            {
                "id": "DB-001",
                "type": "database_url",
                "severity": "HIGH",
                "pattern": r'(mongodb|mysql|postgresql|postgres|redis)://[^\s:"\']+:[^\s@"\']+@[^\s"\']+',
                "description": "Database Connection String with Credentials",
                "remediation": "Move credentials to environment variables"
            },
            {
                "id": "BEARER-001",
                "type": "bearer_token",
                "severity": "HIGH",
                "pattern": r'[Bb]earer\s+[a-zA-Z0-9_\-\.]{20,}',
                "description": "Bearer Token",
                "remediation": "Move to secure storage; rotate token"
            },
            {
                "id": "STRIPE-001",
                "type": "stripe_key",
                "severity": "CRITICAL",
                "pattern": r'sk_live_[0-9a-zA-Z]{24,}',
                "description": "Stripe Live Secret Key",
                "remediation": "Revoke key immediately in Stripe dashboard"
            },
            {
                "id": "SENDGRID-001",
                "type": "sendgrid_key",
                "severity": "HIGH",
                "pattern": r'SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}',
                "description": "SendGrid API Key",
                "remediation": "Revoke and regenerate API key"
            }
        ]
    
    def calculate_entropy(self, string: str) -> float:
        """Calculate Shannon entropy of a string."""
        if not string:
            return 0.0
        
        entropy = 0.0
        length = len(string)
        
        for char in set(string):
            count = string.count(char)
            p = count / length
            if p > 0:
                entropy -= p * math.log2(p)
        
        return entropy
    
    def scan_directory(self, target_path: str, include_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Scan directory for secrets."""
        target = Path(target_path)
        
        if not target.exists():
            raise FileNotFoundError(f"Target not found: {target_path}")
        
        self.findings = []
        self.files_scanned = 0
        
        if target.is_file():
            self._scan_file(target)
        else:
            self._scan_directory_recursive(target, include_patterns)
        
        return self._build_results(target_path)
    
    def _scan_directory_recursive(self, directory: Path, include_patterns: Optional[List[str]] = None):
        """Recursively scan directory."""
        for item in directory.rglob("*"):
            if item.is_file():
                # Check exclude directories
                if any(excluded in item.parts for excluded in self.EXCLUDED_DIRS):
                    continue
                
                # Check file extension
                if item.suffix.lower() in self.EXCLUDED_EXTENSIONS:
                    continue
                
                # Check include patterns
                if include_patterns:
                    if not any(item.match(p) for p in include_patterns):
                        continue
                
                self._scan_file(item)
    
    def _scan_file(self, file_path: Path):
        """Scan a single file for secrets."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                self.files_scanned += 1
                
                for pattern_def in self.patterns:
                    self._check_pattern(file_path, content, lines, pattern_def)
                
                # Additional entropy-based detection
                if self.entropy_check:
                    self._check_entropy(file_path, content, lines)
                    
        except Exception as e:
            if self.verbose:
                print(f"Error scanning {file_path}: {e}")
    
    def _check_pattern(self, file_path: Path, content: str, lines: List[str], pattern_def: Dict):
        """Check content against a secret pattern."""
        regex = re.compile(pattern_def["pattern"], re.IGNORECASE)
        
        for line_num, line in enumerate(lines, 1):
            for match in regex.finditer(line):
                match_str = match.group()
                
                # Check entropy if required
                if pattern_def.get("entropy_check"):
                    entropy = self.calculate_entropy(match_str)
                    if entropy < self.ENTROPY_THRESHOLD:
                        continue
                else:
                    entropy = self.calculate_entropy(match_str)
                
                # Get context
                start = max(0, line_num - 2)
                end = min(len(lines), line_num + 1)
                context = '\n'.join(lines[start:end])
                
                finding = SecretFinding(
                    id=pattern_def["id"],
                    type=pattern_def["type"],
                    severity=pattern_def["severity"],
                    file=str(file_path),
                    line=line_num,
                    column=match.start() + 1,
                    match=match_str[:50] + "..." if len(match_str) > 50 else match_str,
                    context=context.strip(),
                    entropy=round(entropy, 2),
                    verified=False,
                    remediation=pattern_def["remediation"]
                )
                
                self.findings.append(finding)
    
    def _check_entropy(self, file_path: Path, content: str, lines: List[str]):
        """Check for high-entropy strings that might be secrets."""
        # Pattern for potential hex/base64 encoded strings
        entropy_pattern = re.compile(r'\b[a-f0-9]{32,64}\b|\b[A-Za-z0-9+/]{40,}={0,2}\b')
        
        for line_num, line in enumerate(lines, 1):
            for match in entropy_pattern.finditer(line):
                match_str = match.group()
                entropy = self.calculate_entropy(match_str)
                
                if entropy >= self.ENTROPY_THRESHOLD:
                    # Skip if already detected by specific pattern
                    if any(f.line == line_num and f.file == str(file_path) for f in self.findings):
                        continue
                    
                    start = max(0, line_num - 1)
                    end = min(len(lines), line_num + 1)
                    context = '\n'.join(lines[start:end])
                    
                    finding = SecretFinding(
                        id="ENTROPY-001",
                        type="high_entropy_string",
                        severity="LOW",
                        file=str(file_path),
                        line=line_num,
                        column=match.start() + 1,
                        match=match_str[:30] + "..." if len(match_str) > 30 else match_str,
                        context=context.strip(),
                        entropy=round(entropy, 2),
                        verified=False,
                        remediation="Review if this is a secret; move to secure storage if so"
                    )
                    
                    self.findings.append(finding)
    
    def scan_git_history(self, repo_path: str, max_commits: int = 100) -> List[Dict[str, Any]]:
        """Scan git commit history for secrets."""
        findings = []
        
        try:
            # Check if it's a git repo
            git_dir = Path(repo_path) / ".git"
            if not git_dir.exists():
                if self.verbose:
                    print(f"Not a git repository: {repo_path}")
                return findings
            
            # Get commit history
            result = subprocess.run(
                ["git", "-C", repo_path, "log", "--format=%H", f"-n{max_commits}"],
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = result.stdout.strip().split('\n')
            
            for commit in commits:
                if not commit:
                    continue
                
                # Get diff for this commit
                diff_result = subprocess.run(
                    ["git", "-C", repo_path, "show", commit, "--format="],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                diff_content = diff_result.stdout
                
                # Scan diff for secrets
                for pattern_def in self.patterns:
                    regex = re.compile(pattern_def["pattern"], re.IGNORECASE)
                    for match in regex.finditer(diff_content):
                        findings.append({
                            "commit": commit[:8],
                            "type": pattern_def["type"],
                            "severity": pattern_def["severity"],
                            "match": match.group()[:30] + "..."
                        })
        
        except subprocess.CalledProcessError as e:
            if self.verbose:
                print(f"Git command failed: {e}")
        except FileNotFoundError:
            if self.verbose:
                print("Git not found in PATH")
        
        return findings
    
    def _build_results(self, target_path: str) -> Dict[str, Any]:
        """Build final scan results."""
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
        for finding in self.findings:
            severity_counts[finding.severity] += 1
        
        return {
            "scan_info": {
                "target": target_path,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "files_scanned": self.files_scanned
            },
            "findings": [asdict(f) for f in self.findings],
            "summary": severity_counts
        }
    
    def generate_report(self, results: Dict[str, Any], output_path: str):
        """Generate JSON report."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        if self.verbose:
            print(f"Report saved to: {output_path}")
    
    def print_summary(self, results: Dict[str, Any]):
        """Print summary to console."""
        summary = results["summary"]
        total = sum(summary.values())
        
        print("\n" + "="*60)
        print("SECRETS SCANNER REPORT")
        print("="*60)
        print(f"Target: {results['scan_info']['target']}")
        print(f"Files scanned: {results['scan_info']['files_scanned']}")
        print(f"Total findings: {total}")
        print("\nFINDINGS BY SEVERITY:")
        print(f"  CRITICAL: {summary['CRITICAL']}")
        print(f"  HIGH:     {summary['HIGH']}")
        print(f"  MEDIUM:   {summary['MEDIUM']}")
        print(f"  LOW:      {summary['LOW']}")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Secrets Scanner Skill")
    parser.add_argument("--target", "-t", required=True, help="Path to scan")
    parser.add_argument("--include", help="Comma-separated file patterns to include")
    parser.add_argument("--scan-history", action="store_true", help="Scan git history")
    parser.add_argument("--max-commits", type=int, default=100, help="Max commits to scan")
    parser.add_argument("--no-entropy", action="store_true", help="Disable entropy checks")
    parser.add_argument("--output", "-o", help="Output report path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    include_patterns = None
    if args.include:
        include_patterns = [p.strip() for p in args.include.split(',')]
    
    scanner = SecretsScanner(
        verbose=args.verbose,
        entropy_check=not args.no_entropy
    )
    
    # Main scan
    results = scanner.scan_directory(args.target, include_patterns)
    
    # Git history scan
    if args.scan_history:
        history_findings = scanner.scan_git_history(args.target, args.max_commits)
        results["git_history_findings"] = history_findings
    
    scanner.print_summary(results)
    
    if args.output:
        scanner.generate_report(results, args.output)
    
    # Exit with error if critical findings
    critical_count = results["summary"]["CRITICAL"]
    return 1 if critical_count > 0 else 0


if __name__ == "__main__":
    exit(main())
