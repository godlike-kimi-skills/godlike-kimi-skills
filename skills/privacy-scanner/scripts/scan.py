#!/usr/bin/env python3
"""
Privacy Scanner Tool
Based on Exodus Privacy and GDPR patterns
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set


class PrivacyScanner:
    """Scans for privacy issues"""

    PII_PATTERNS = {
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'phone': r'\b\d{3}-\d{3}-\d{4}\b',
    }

    TRACKING_DOMAINS = [
        'google-analytics.com',
        'facebook.com/tr',
        'doubleclick.net',
    ]

    def __init__(self):
        self.findings: List[Dict] = []
        self.risk_score = 0

    def scan_file(self, filepath: str) -> Dict:
        """Scan a file for PII"""
        path = Path(filepath)
        if not path.exists():
            return {'error': f'File not found: {filepath}'}

        findings = []
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
            for pii_type, pattern in self.PII_PATTERNS.items():
                matches = re.findall(pattern, content)
                if matches:
                    findings.append({
                        'type': pii_type,
                        'count': len(matches),
                        'sample': matches[0] if matches else None
                    })
                    self.risk_score += len(matches) * 10
        except Exception as e:
            findings.append({'error': str(e)})

        return {
            'file': filepath,
            'findings': findings
        }

    def scan_directory(self, directory: str, recursive: bool = False) -> Dict:
        """Scan directory for privacy issues"""
        path = Path(directory)
        if not path.exists():
            return {'error': f'Directory not found: {directory}'}

        results = []
        pattern = '**/*' if recursive else '*'
        for file_path in path.glob(pattern):
            if file_path.is_file():
                result = self.scan_file(str(file_path))
                if result.get('findings'):
                    results.append(result)

        return {
            'directory': directory,
            'files_scanned': len(list(path.glob(pattern))),
            'results': results,
            'total_risk_score': self.risk_score
        }

    def generate_report(self, output: str = None) -> str:
        """Generate privacy report"""
        report = {
            'scanner': 'PrivacyScanner',
            'version': '2.0.0',
            'timestamp': datetime.now().isoformat(),
            'risk_score': self.risk_score,
            'findings': self.findings
        }

        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)

        return json.dumps(report, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Privacy Scanner')
    parser.add_argument('--path', required=True, help='File or directory to scan')
    parser.add_argument('--recursive', action='store_true', help='Scan recursively')
    parser.add_argument('--output', help='Output file')
    args = parser.parse_args()

    scanner = PrivacyScanner()
    path = Path(args.path)

    if path.is_file():
        result = scanner.scan_file(args.path)
    else:
        result = scanner.scan_directory(args.path, args.recursive)

    print(json.dumps(result, indent=2))

    if args.output:
        scanner.generate_report(args.output)
        print(f'Report saved to: {args.output}')


if __name__ == '__main__':
    main()
