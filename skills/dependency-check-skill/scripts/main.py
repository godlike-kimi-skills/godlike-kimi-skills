#!/usr/bin/env python3
"""
Dependency Check Skill - Main Module
Automated dependency vulnerability scanner for multiple package formats.

Use when auditing code security, scanning for vulnerabilities, or when user 
mentions 'security', 'vulnerability', 'CVE'.
"""

import os
import re
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from packaging.version import Version, parse as parse_version


@dataclass
class Vulnerability:
    cve_id: str
    severity: str
    description: str
    fixed_in: Optional[str]
    cvss_score: Optional[float] = None
    references: List[str] = field(default_factory=list)


@dataclass
class Dependency:
    name: str
    version: str
    latest_version: Optional[str] = None
    license: Optional[str] = None
    outdated: bool = False
    vulnerabilities: List[Vulnerability] = field(default_factory=list)


class DependencyChecker:
    """Dependency vulnerability checker supporting multiple formats."""
    
    # CVE API endpoints
    NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    PYPI_API_BASE = "https://pypi.org/pypi"
    NPM_REGISTRY_BASE = "https://registry.npmjs.org"
    
    # Severity mapping from CVSS score
    SEVERITY_RANGES = {
        "CRITICAL": (9.0, 10.0),
        "HIGH": (7.0, 8.9),
        "MEDIUM": (4.0, 6.9),
        "LOW": (0.1, 3.9),
        "INFO": (0.0, 0.0)
    }
    
    def __init__(self, verbose: bool = False, cache_dir: Optional[str] = None):
        self.verbose = verbose
        self.cache_dir = cache_dir or os.path.expanduser("~/.dependency_check_cache")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "DependencyCheckSkill/1.0.0"
        })
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load cached CVE database
        self.cve_cache = self._load_cve_cache()
    
    def _load_cve_cache(self) -> Dict:
        """Load cached CVE data."""
        cache_file = os.path.join(self.cache_dir, "cve_cache.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_cve_cache(self):
        """Save CVE cache to disk."""
        cache_file = os.path.join(self.cache_dir, "cve_cache.json")
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.cve_cache, f)
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not save cache: {e}")
    
    def scan_file(self, file_path: str, format_type: Optional[str] = None) -> Dict[str, Any]:
        """Scan a dependency file for vulnerabilities."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Auto-detect format if not specified
        if not format_type:
            format_type = self._detect_format(path)
        
        # Parse dependencies
        dependencies = self._parse_file(path, format_type)
        
        if self.verbose:
            print(f"Found {len(dependencies)} dependencies in {file_path}")
        
        # Check each dependency
        checked_deps = []
        for dep in dependencies:
            checked_dep = self._check_dependency(dep, format_type)
            checked_deps.append(checked_dep)
        
        # Build results
        results = self._build_results(file_path, format_type, checked_deps)
        
        # Save cache
        self._save_cve_cache()
        
        return results
    
    def _detect_format(self, path: Path) -> str:
        """Auto-detect dependency file format."""
        name = path.name.lower()
        
        if name == "package.json":
            return "npm"
        elif name.startswith("requirements") and name.endswith(".txt"):
            return "requirements"
        elif name == "pipfile.lock":
            return "pipfile"
        elif name == "go.mod":
            return "gomod"
        elif name == "pom.xml":
            return "maven"
        else:
            raise ValueError(f"Cannot auto-detect format for: {name}")
    
    def _parse_file(self, path: Path, format_type: str) -> List[Dependency]:
        """Parse dependency file based on format."""
        parsers = {
            "requirements": self._parse_requirements,
            "npm": self._parse_npm,
            "pipfile": self._parse_pipfile,
            "gomod": self._parse_gomod,
            "maven": self._parse_maven
        }
        
        parser = parsers.get(format_type)
        if not parser:
            raise ValueError(f"Unsupported format: {format_type}")
        
        return parser(path)
    
    def _parse_requirements(self, path: Path) -> List[Dependency]:
        """Parse requirements.txt file."""
        dependencies = []
        
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse package==version or package>=version
                match = re.match(r'^([a-zA-Z0-9_-]+)\s*([<>=!~]+)?\s*([0-9.]+)?', line)
                if match:
                    name = match.group(1)
                    version = match.group(3) or "0.0.0"
                    dependencies.append(Dependency(name=name, version=version))
        
        return dependencies
    
    def _parse_npm(self, path: Path) -> List[Dependency]:
        """Parse package.json file."""
        dependencies = []
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Combine dependencies and devDependencies
        all_deps = {}
        all_deps.update(data.get("dependencies", {}))
        all_deps.update(data.get("devDependencies", {}))
        
        for name, version_spec in all_deps.items():
            # Remove ^ and ~ prefixes
            version = version_spec.lstrip('^~>=<')
            dependencies.append(Dependency(name=name, version=version))
        
        return dependencies
    
    def _parse_pipfile(self, path: Path) -> List[Dependency]:
        """Parse Pipfile.lock."""
        dependencies = []
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        default_deps = data.get("default", {})
        for name, info in default_deps.items():
            version = info.get("version", "0.0.0").lstrip('=')
            dependencies.append(Dependency(name=name, version=version))
        
        return dependencies
    
    def _parse_gomod(self, path: Path) -> List[Dependency]:
        """Parse go.mod file."""
        dependencies = []
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Match require statements
        require_pattern = r'require\s+\(\s*([^)]+)\)'
        matches = re.findall(require_pattern, content, re.DOTALL)
        
        for match in matches:
            for line in match.strip().split('\n'):
                parts = line.strip().split()
                if len(parts) >= 2:
                    name = parts[0]
                    version = parts[1].lstrip('v')
                    dependencies.append(Dependency(name=name, version=version))
        
        return dependencies
    
    def _parse_maven(self, path: Path) -> List[Dependency]:
        """Parse pom.xml file."""
        import xml.etree.ElementTree as ET
        
        dependencies = []
        
        tree = ET.parse(path)
        root = tree.getroot()
        
        # Define namespace
        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
        
        for dep in root.findall('.//m:dependency', ns):
            group_id = dep.find('m:groupId', ns)
            artifact_id = dep.find('m:artifactId', ns)
            version = dep.find('m:version', ns)
            
            if group_id is not None and artifact_id is not None:
                name = f"{group_id.text}:{artifact_id.text}"
                ver = version.text if version is not None else "0.0.0"
                dependencies.append(Dependency(name=name, version=ver))
        
        return dependencies
    
    def _check_dependency(self, dep: Dependency, format_type: str) -> Dependency:
        """Check a single dependency for vulnerabilities."""
        # Get latest version
        dep.latest_version = self._get_latest_version(dep.name, format_type)
        dep.outdated = self._is_outdated(dep.version, dep.latest_version)
        
        # Check for vulnerabilities
        dep.vulnerabilities = self._check_vulnerabilities(dep.name, dep.version, format_type)
        
        return dep
    
    def _get_latest_version(self, name: str, format_type: str) -> Optional[str]:
        """Get the latest version of a package."""
        try:
            if format_type == "requirements":
                url = f"{self.PYPI_API_BASE}/{name}/json"
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return data["info"]["version"]
            
            elif format_type == "npm":
                url = f"{self.NPM_REGISTRY_BASE}/{name}"
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("dist-tags", {}).get("latest")
        
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not get latest version for {name}: {e}")
        
        return None
    
    def _is_outdated(self, current: str, latest: Optional[str]) -> bool:
        """Check if current version is outdated."""
        if not latest:
            return False
        
        try:
            return parse_version(current) < parse_version(latest)
        except Exception:
            return current != latest
    
    def _check_vulnerabilities(self, name: str, version: str, format_type: str) -> List[Vulnerability]:
        """Check for known vulnerabilities in a dependency."""
        vulnerabilities = []
        
        # Build cache key
        cache_key = f"{format_type}:{name}:{version}"
        
        # Check cache first
        if cache_key in self.cve_cache:
            cached = self.cve_cache[cache_key]
            return [Vulnerability(**v) for v in cached]
        
        try:
            # Query NVD API
            keyword = f"{name} {version}"
            params = {
                "keywordSearch": keyword,
                "resultsPerPage": 20
            }
            
            response = self.session.get(
                self.NVD_API_BASE,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get("vulnerabilities", []):
                    cve = item.get("cve", {})
                    cve_id = cve.get("id", "UNKNOWN")
                    
                    # Get description
                    descriptions = cve.get("descriptions", [])
                    description = ""
                    for desc in descriptions:
                        if desc.get("lang") == "en":
                            description = desc.get("value", "")
                            break
                    
                    # Get CVSS score and severity
                    metrics = cve.get("metrics", {})
                    cvss_data = metrics.get("cvssMetricV31", [{}])[0] or metrics.get("cvssMetricV30", [{}])[0]
                    cvss_score = None
                    severity = "UNKNOWN"
                    
                    if cvss_data:
                        cvss_score = cvss_data.get("cvssData", {}).get("baseScore")
                        severity = cvss_data.get("cvssData", {}).get("baseSeverity", "UNKNOWN")
                    
                    # Get references
                    refs = cve.get("references", [])
                    references = [r.get("url") for r in refs if r.get("url")]
                    
                    vuln = Vulnerability(
                        cve_id=cve_id,
                        severity=severity,
                        description=description[:200] + "..." if len(description) > 200 else description,
                        fixed_in=None,  # Would need additional parsing
                        cvss_score=cvss_score,
                        references=references[:3]
                    )
                    vulnerabilities.append(vuln)
        
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not check vulnerabilities for {name}: {e}")
        
        # Cache results
        self.cve_cache[cache_key] = [asdict(v) for v in vulnerabilities]
        
        return vulnerabilities
    
    def _build_results(self, file_path: str, format_type: str, dependencies: List[Dependency]) -> Dict[str, Any]:
        """Build final scan results."""
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        outdated_count = 0
        
        for dep in dependencies:
            if dep.outdated:
                outdated_count += 1
            for vuln in dep.vulnerabilities:
                sev = vuln.severity.upper()
                if sev in severity_counts:
                    severity_counts[sev] += 1
                else:
                    severity_counts["INFO"] += 1
        
        return {
            "scan_info": {
                "file": file_path,
                "format": format_type,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "total_dependencies": len(dependencies)
            },
            "dependencies": [asdict(d) for d in dependencies],
            "summary": {
                **severity_counts,
                "outdated": outdated_count,
                "up_to_date": len(dependencies) - outdated_count
            }
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
        total_vulns = sum(v for k, v in summary.items() if k not in ["outdated", "up_to_date"])
        
        print("\n" + "="*60)
        print("DEPENDENCY CHECK REPORT")
        print("="*60)
        print(f"File: {results['scan_info']['file']}")
        print(f"Format: {results['scan_info']['format']}")
        print(f"Total dependencies: {results['scan_info']['total_dependencies']}")
        print(f"Outdated: {summary['outdated']}")
        print("\nVULNERABILITIES:")
        print(f"  CRITICAL: {summary['CRITICAL']}")
        print(f"  HIGH:     {summary['HIGH']}")
        print(f"  MEDIUM:   {summary['MEDIUM']}")
        print(f"  LOW:      {summary['LOW']}")
        print(f"  Total:    {total_vulns}")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Dependency Check Skill")
    parser.add_argument("--file", "-f", required=True, help="Path to dependency file")
    parser.add_argument("--format", choices=["requirements", "npm", "pipfile", "gomod", "maven"],
                        help="Dependency file format (auto-detect if not specified)")
    parser.add_argument("--output", "-o", help="Output report path (JSON)")
    parser.add_argument("--check-outdated", action="store_true", help="Check for outdated packages")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    checker = DependencyChecker(verbose=args.verbose)
    results = checker.scan_file(args.file, args.format)
    
    checker.print_summary(results)
    
    if args.output:
        checker.generate_report(results, args.output)
    
    # Exit with error if vulnerabilities found
    summary = results["summary"]
    critical_high = summary.get("CRITICAL", 0) + summary.get("HIGH", 0)
    return 1 if critical_high > 0 else 0


if __name__ == "__main__":
    exit(main())
