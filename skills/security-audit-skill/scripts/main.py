#!/usr/bin/env python3
"""
Security Audit Skill - Main Module
Automated code security auditing for Python, JavaScript, and Java.

Use when auditing code security, scanning for vulnerabilities, or when user 
mentions 'security', 'vulnerability', 'CVE'.
"""

import os
import re
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class Vulnerability:
    id: str
    severity: str
    type: str
    file: str
    line: int
    column: int
    description: str
    recommendation: str
    code_snippet: str
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None


class SecurityAuditor:
    """Main security auditor class for multi-language code analysis."""
    
    SEVERITY_WEIGHTS = {
        "CRITICAL": 5,
        "HIGH": 4,
        "MEDIUM": 3,
        "LOW": 2,
        "INFO": 1
    }
    
    def __init__(self, language: str, verbose: bool = False):
        self.language = language.lower()
        self.verbose = verbose
        self.vulnerabilities: List[Vulnerability] = []
        self.scanned_files = 0
        self.total_lines = 0
        
        # Initialize pattern databases
        self._init_patterns()
    
    def _init_patterns(self):
        """Initialize vulnerability patterns based on language."""
        self.patterns = {
            "python": self._get_python_patterns(),
            "javascript": self._get_js_patterns(),
            "java": self._get_java_patterns()
        }
    
    def _get_python_patterns(self) -> List[Dict]:
        """Get Python-specific vulnerability patterns."""
        return [
            {
                "id": "PY-001",
                "type": "sql_injection",
                "severity": "HIGH",
                "pattern": r'(?:execute|cursor\.execute)\s*\(\s*["\'].*?%s.*?["\']',
                "description": "Potential SQL injection using string formatting",
                "recommendation": "Use parameterized queries with placeholders",
                "cwe": "CWE-89",
                "owasp": "A03:2021 - Injection"
            },
            {
                "id": "PY-002",
                "type": "command_injection",
                "severity": "CRITICAL",
                "pattern": r'(?:os\.system|subprocess\.call|subprocess\.Popen)\s*\([^)]*(?:%s|%\(|\.format|f["\'])',
                "description": "Potential command injection vulnerability",
                "recommendation": "Use subprocess with list arguments, avoid shell=True",
                "cwe": "CWE-78",
                "owasp": "A03:2021 - Injection"
            },
            {
                "id": "PY-003",
                "type": "hardcoded_secret",
                "severity": "HIGH",
                "pattern": r'(?:password|secret|token|key|api_key)\s*=\s*["\'][^"\']{8,}["\']',
                "description": "Potential hardcoded secret detected",
                "recommendation": "Use environment variables or secure vault",
                "cwe": "CWE-798",
                "owasp": "A07:2021 - Identification and Authentication Failures"
            },
            {
                "id": "PY-004",
                "type": "unsafe_deserialization",
                "severity": "CRITICAL",
                "pattern": r'pickle\.(?:loads|load)\s*\(',
                "description": "Unsafe deserialization with pickle",
                "recommendation": "Use json or safe serialization alternatives",
                "cwe": "CWE-502",
                "owasp": "A08:2021 - Software and Data Integrity Failures"
            },
            {
                "id": "PY-005",
                "type": "path_traversal",
                "severity": "MEDIUM",
                "pattern": r'open\s*\([^)]*(?:\+|\%s|%\()',
                "description": "Potential path traversal vulnerability",
                "recommendation": "Validate and sanitize file paths",
                "cwe": "CWE-22",
                "owasp": "A01:2021 - Broken Access Control"
            },
            {
                "id": "PY-006",
                "type": "weak_hash",
                "severity": "MEDIUM",
                "pattern": r'(?:hashlib\.)?(?:md5|sha1)\s*\(',
                "description": "Weak cryptographic hash function",
                "recommendation": "Use SHA-256 or stronger hash functions",
                "cwe": "CWE-327",
                "owasp": "A02:2021 - Cryptographic Failures"
            },
            {
                "id": "PY-007",
                "type": "debug_mode",
                "severity": "MEDIUM",
                "pattern": r'debug\s*=\s*True',
                "description": "Debug mode enabled in production code",
                "recommendation": "Set debug=False in production",
                "cwe": "CWE-489",
                "owasp": "A05:2021 - Security Misconfiguration"
            },
            {
                "id": "PY-008",
                "type": "insecure_temp",
                "severity": "LOW",
                "pattern": r'mktemp\s*\(',
                "description": "Insecure temporary file creation",
                "recommendation": "Use mkstemp() instead of mktemp()",
                "cwe": "CWE-377",
                "owasp": "A01:2021 - Broken Access Control"
            }
        ]
    
    def _get_js_patterns(self) -> List[Dict]:
        """Get JavaScript-specific vulnerability patterns."""
        return [
            {
                "id": "JS-001",
                "type": "xss_vulnerability",
                "severity": "HIGH",
                "pattern": r'(?:innerHTML|outerHTML)\s*=\s*[^;]*(?:\+|`)',
                "description": "Potential XSS via innerHTML assignment",
                "recommendation": "Use textContent or sanitize HTML",
                "cwe": "CWE-79",
                "owasp": "A03:2021 - Injection"
            },
            {
                "id": "JS-002",
                "type": "eval_usage",
                "severity": "CRITICAL",
                "pattern": r'(?:eval|setTimeout|setInterval)\s*\(\s*["\']',
                "description": "Dangerous eval() or similar function usage",
                "recommendation": "Avoid eval(), use JSON.parse for JSON data",
                "cwe": "CWE-95",
                "owasp": "A03:2021 - Injection"
            },
            {
                "id": "JS-003",
                "type": "prototype_pollution",
                "severity": "HIGH",
                "pattern": r'(?:__proto__|constructor\.prototype)\s*=',
                "description": "Potential prototype pollution",
                "recommendation": "Use Object.freeze() or validate property names",
                "cwe": "CWE-1321",
                "owasp": "A08:2021 - Software and Data Integrity Failures"
            },
            {
                "id": "JS-004",
                "type": "insecure_random",
                "severity": "MEDIUM",
                "pattern": r'Math\.random\s*\(\)',
                "description": "Insecure random number generation",
                "recommendation": "Use crypto.getRandomValues() for security purposes",
                "cwe": "CWE-338",
                "owasp": "A02:2021 - Cryptographic Failures"
            },
            {
                "id": "JS-005",
                "type": "hardcoded_secret",
                "severity": "HIGH",
                "pattern": r'(?:password|secret|token|key|apiKey)\s*[:=]\s*["\'][^"\']{8,}["\']',
                "description": "Potential hardcoded secret",
                "recommendation": "Use environment variables",
                "cwe": "CWE-798",
                "owasp": "A07:2021 - Identification and Authentication Failures"
            },
            {
                "id": "JS-006",
                "type": "no_sql_injection",
                "severity": "HIGH",
                "pattern": r'\$where\s*:',
                "description": "Potential NoSQL injection",
                "recommendation": "Validate and sanitize user input",
                "cwe": "CWE-943",
                "owasp": "A03:2021 - Injection"
            },
            {
                "id": "JS-007",
                "type": "cors_misconfig",
                "severity": "MEDIUM",
                "pattern": r'Access-Control-Allow-Origin.*\*',
                "description": "Permissive CORS configuration",
                "recommendation": "Restrict CORS to specific origins",
                "cwe": "CWE-942",
                "owasp": "A05:2021 - Security Misconfiguration"
            }
        ]
    
    def _get_java_patterns(self) -> List[Dict]:
        """Get Java-specific vulnerability patterns."""
        return [
            {
                "id": "JAVA-001",
                "type": "sql_injection",
                "severity": "HIGH",
                "pattern": r'(?:Statement|createStatement)\s*.*\.execute(?:Query|Update)\s*\(',
                "description": "Potential SQL injection using Statement",
                "recommendation": "Use PreparedStatement with parameterized queries",
                "cwe": "CWE-89",
                "owasp": "A03:2021 - Injection"
            },
            {
                "id": "JAVA-002",
                "type": "xxe_vulnerability",
                "severity": "CRITICAL",
                "pattern": r'DocumentBuilderFactory|SAXParserFactory|XMLReader',
                "description": "Potential XXE vulnerability",
                "recommendation": "Disable external entity processing",
                "cwe": "CWE-611",
                "owasp": "A05:2021 - Security Misconfiguration"
            },
            {
                "id": "JAVA-003",
                "type": "weak_cryptography",
                "severity": "MEDIUM",
                "pattern": r'(?:MessageDigest\.getInstance\s*\(\s*["\'](?:MD5|SHA-1)["\']|DES|RC4)',
                "description": "Weak cryptographic algorithm",
                "recommendation": "Use AES or SHA-256",
                "cwe": "CWE-327",
                "owasp": "A02:2021 - Cryptographic Failures"
            },
            {
                "id": "JAVA-004",
                "type": "insecure_random",
                "severity": "MEDIUM",
                "pattern": r'new\s+Random\s*\(',
                "description": "Insecure random number generator",
                "recommendation": "Use SecureRandom for security purposes",
                "cwe": "CWE-338",
                "owasp": "A02:2021 - Cryptographic Failures"
            },
            {
                "id": "JAVA-005",
                "type": "unsafe_reflection",
                "severity": "HIGH",
                "pattern": r'(?:Class\.forName|\.getMethod|\.invoke)\s*\([^)]*\+',
                "description": "Unsafe use of reflection",
                "recommendation": "Validate class/method names before reflection",
                "cwe": "CWE-470",
                "owasp": "A03:2021 - Injection"
            },
            {
                "id": "JAVA-006",
                "type": "path_traversal",
                "severity": "MEDIUM",
                "pattern": r'new\s+File\s*\([^)]*(?:\+|\$\{)',
                "description": "Potential path traversal",
                "recommendation": "Validate file paths",
                "cwe": "CWE-22",
                "owasp": "A01:2021 - Broken Access Control"
            },
            {
                "id": "JAVA-007",
                "type": "deserialization",
                "severity": "CRITICAL",
                "pattern": r'(?:ObjectInputStream|readObject)\s*\(',
                "description": "Unsafe object deserialization",
                "recommendation": "Implement look-ahead deserialization or avoid",
                "cwe": "CWE-502",
                "owasp": "A08:2021 - Software and Data Integrity Failures"
            }
        ]
    
    def audit(self, target_path: str) -> Dict[str, Any]:
        """Run security audit on target directory or file."""
        target = Path(target_path)
        
        if not target.exists():
            raise FileNotFoundError(f"Target not found: {target_path}")
        
        self.vulnerabilities = []
        self.scanned_files = 0
        self.total_lines = 0
        
        if target.is_file():
            self._scan_file(target)
        else:
            self._scan_directory(target)
        
        return self._build_result()
    
    def _scan_directory(self, directory: Path):
        """Recursively scan directory for vulnerabilities."""
        extensions = {
            "python": [".py"],
            "javascript": [".js", ".jsx", ".ts", ".tsx"],
            "java": [".java"]
        }
        
        ext_list = extensions.get(self.language, [])
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix in ext_list:
                self._scan_file(file_path)
    
    def _scan_file(self, file_path: Path):
        """Scan a single file for vulnerabilities."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                self.scanned_files += 1
                self.total_lines += len(lines)
                
                patterns = self.patterns.get(self.language, [])
                
                for pattern_def in patterns:
                    self._check_pattern(file_path, content, lines, pattern_def)
                    
        except Exception as e:
            if self.verbose:
                print(f"Error scanning {file_path}: {e}")
    
    def _check_pattern(self, file_path: Path, content: str, lines: List[str], pattern_def: Dict):
        """Check content against a specific vulnerability pattern."""
        regex = re.compile(pattern_def["pattern"], re.IGNORECASE)
        
        for line_num, line in enumerate(lines, 1):
            if regex.search(line):
                # Get surrounding context
                start = max(0, line_num - 2)
                end = min(len(lines), line_num + 1)
                code_snippet = '\n'.join(lines[start:end])
                
                vuln = Vulnerability(
                    id=pattern_def["id"],
                    severity=pattern_def["severity"],
                    type=pattern_def["type"],
                    file=str(file_path),
                    line=line_num,
                    column=line.find(regex.search(line).group()) + 1 if regex.search(line) else 0,
                    description=pattern_def["description"],
                    recommendation=pattern_def["recommendation"],
                    code_snippet=code_snippet.strip(),
                    cwe_id=pattern_def.get("cwe"),
                    owasp_category=pattern_def.get("owasp")
                )
                self.vulnerabilities.append(vuln)
    
    def _build_result(self) -> Dict[str, Any]:
        """Build the final audit result."""
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        
        for vuln in self.vulnerabilities:
            severity_counts[vuln.severity] += 1
        
        return {
            "scan_info": {
                "target": None,
                "language": self.language,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "total_files": self.scanned_files,
                "total_lines": self.total_lines
            },
            "vulnerabilities": [asdict(v) for v in self.vulnerabilities],
            "summary": severity_counts,
            "risk_score": self._calculate_risk_score(severity_counts)
        }
    
    def _calculate_risk_score(self, severity_counts: Dict[str, int]) -> float:
        """Calculate overall risk score (0-100)."""
        total_weighted = sum(
            count * self.SEVERITY_WEIGHTS[sev]
            for sev, count in severity_counts.items()
        )
        
        # Normalize to 0-100 scale
        max_possible = self.total_lines * 0.1  # Assume max 10% of lines vulnerable
        if max_possible == 0:
            return 0.0
        
        score = min(100, (total_weighted / max(self.total_lines, 1)) * 100)
        return round(score, 2)
    
    def generate_report(self, results: Dict[str, Any], output_path: str):
        """Generate audit report to file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        if self.verbose:
            print(f"Report saved to: {output_path}")
    
    def print_summary(self, results: Dict[str, Any]):
        """Print summary to console."""
        summary = results["summary"]
        
        print("\n" + "="*60)
        print("SECURITY AUDIT REPORT")
        print("="*60)
        print(f"Language: {results['scan_info']['language']}")
        print(f"Files scanned: {results['scan_info']['total_files']}")
        print(f"Lines scanned: {results['scan_info']['total_lines']}")
        print(f"Risk score: {results['risk_score']}/100")
        print("\nVULNERABILITIES FOUND:")
        print(f"  CRITICAL: {summary['CRITICAL']}")
        print(f"  HIGH:     {summary['HIGH']}")
        print(f"  MEDIUM:   {summary['MEDIUM']}")
        print(f"  LOW:      {summary['LOW']}")
        print(f"  INFO:     {summary['INFO']}")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Security Audit Skill")
    parser.add_argument("--target", "-t", required=True, help="Path to code directory or file")
    parser.add_argument("--language", "-l", required=True, choices=["python", "javascript", "java"],
                        help="Programming language")
    parser.add_argument("--output", "-o", help="Output report path (JSON)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    auditor = SecurityAuditor(language=args.language, verbose=args.verbose)
    results = auditor.audit(args.target)
    results["scan_info"]["target"] = args.target
    
    auditor.print_summary(results)
    
    if args.output:
        auditor.generate_report(results, args.output)
    
    # Return exit code based on severity
    critical_high = results["summary"]["CRITICAL"] + results["summary"]["HIGH"]
    return 1 if critical_high > 0 else 0


if __name__ == "__main__":
    exit(main())
