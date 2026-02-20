#!/usr/bin/env python3
"""
Security Audit System - Production Grade
借鉴: Lynis, OpenVAS, CIS Benchmarks

实现:
- 模块化审计引擎
- CIS合规检查
- CVSS风险评分
- 加固建议生成
"""

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import winreg
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional


class Severity(Enum):
    """CVSS v3.1 风险等级"""
    CRITICAL = ('Critical', '🔴', 9.0, 10.0)
    HIGH = ('High', '🟠', 7.0, 8.9)
    MEDIUM = ('Medium', '🟡', 4.0, 6.9)
    LOW = ('Low', '🟢', 0.1, 3.9)
    INFO = ('Info', '⚪', 0.0, 0.0)
    
    def __init__(self, label: str, icon: str, min_score: float, max_score: float):
        self.label = label
        self.icon = icon
        self.min_score = min_score
        self.max_score = max_score
    
    @classmethod
    def from_cvss(cls, score: float) -> 'Severity':
        for sev in [cls.CRITICAL, cls.HIGH, cls.MEDIUM, cls.LOW]:
            if sev.min_score <= score <= sev.max_score:
                return sev
        return cls.INFO


@dataclass
class Finding:
    """审计发现"""
    id: str
    title: str
    severity: Severity
    cvss_score: float
    category: str
    description: str
    remediation: str
    reference: str
    checked_value: str = ""
    expected_value: str = ""
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'severity': self.severity.label,
            'cvss_score': self.cvss_score,
            'category': self.category,
            'description': self.description,
            'remediation': self.remediation,
            'reference': self.reference,
            'checked_value': self.checked_value,
            'expected_value': self.expected_value,
        }


class AuditModule:
    """审计模块基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.findings: List[Finding] = []
    
    def run(self) -> List[Finding]:
        raise NotImplementedError
    
    def add_finding(self, finding: Finding):
        self.findings.append(finding)


class SystemInfoModule(AuditModule):
    """系统信息收集"""
    
    def __init__(self):
        super().__init__('system', 'System Information')
    
    def run(self) -> List[Finding]:
        findings = []
        sys_info = {
            'os': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
        }
        
        if sys_info['os'] == 'Windows':
            build = sys_info['version']
            if '10.0' in build:
                build_parts = build.split('.')
                build_num = int(build_parts[-1]) if build_parts[-1].isdigit() else 0
                if build_num < 19041:
                    findings.append(Finding(
                        id='SYS-001',
                        title='Windows version outdated',
                        severity=Severity.HIGH,
                        cvss_score=7.5,
                        category='System',
                        description=f'Windows Build: {build_num}, upgrade recommended',
                        remediation='Upgrade to Windows 10 22H2 or Windows 11',
                        reference='Microsoft Security Baseline',
                        checked_value=str(build_num),
                        expected_value='>= 19041'
                    ))
        return findings


class PasswordPolicyModule(AuditModule):
    """密码策略审计"""
    
    def __init__(self):
        super().__init__('password', 'Password Policy')
    
    def run(self) -> List[Finding]:
        findings = []
        try:
            temp_dir = os.environ.get('TEMP', 'C:\\Windows\\Temp')
            policy_file = Path(temp_dir) / 'secpol.cfg'
            
            subprocess.run(
                ['secedit', '/export', '/cfg', str(policy_file), '/areas', 'SECURITYPOLICY'],
                capture_output=True,
                shell=True
            )
            
            if policy_file.exists():
                try:
                    with open(policy_file, 'r', encoding='utf-16') as f:
                        policy_content = f.read()
                except:
                    with open(policy_file, 'r') as f:
                        policy_content = f.read()
                
                if 'PasswordComplexity = 0' in policy_content:
                    findings.append(Finding(
                        id='AUTH-001',
                        title='Password complexity disabled',
                        severity=Severity.HIGH,
                        cvss_score=7.5,
                        category='Authentication',
                        description='System allows weak passwords without complexity requirements',
                        remediation='Enable password complexity in Local Security Policy',
                        reference='CIS 1.1.1',
                        checked_value='Disabled',
                        expected_value='Enabled'
                    ))
                
                min_len_match = re.search(r'MinimumPasswordLength\s*=\s*(\d+)', policy_content)
                if min_len_match:
                    min_len = int(min_len_match.group(1))
                    if min_len < 14:
                        findings.append(Finding(
                            id='AUTH-002',
                            title='Password minimum length too short',
                            severity=Severity.MEDIUM,
                            cvss_score=5.3,
                            category='Authentication',
                            description=f'Minimum length is {min_len}, should be at least 14',
                            remediation='Set MinimumPasswordLength to 14 or higher',
                            reference='CIS 1.1.2',
                            checked_value=str(min_len),
                            expected_value='>= 14'
                        ))
                
                policy_file.unlink(missing_ok=True)
                
        except Exception as e:
            findings.append(Finding(
                id='AUTH-ERR',
                title='Cannot read password policy',
                severity=Severity.INFO,
                cvss_score=0.0,
                category='Authentication',
                description=f'Error reading security policy: {str(e)}',
                remediation='Run as administrator',
                reference='N/A'
            ))
        
        return findings


class FirewallModule(AuditModule):
    """防火墙审计"""
    
    def __init__(self):
        super().__init__('firewall', 'Firewall Status')
    
    def run(self) -> List[Finding]:
        findings = []
        try:
            result = subprocess.run(
                ['netsh', 'advfirewall', 'show', 'currentprofile'],
                capture_output=True,
                text=True,
                shell=True
            )
            
            output = result.stdout.lower()
            
            if 'off' in output or 'state                                 off' in output:
                findings.append(Finding(
                    id='NET-001',
                    title='Windows Firewall disabled',
                    severity=Severity.CRITICAL,
                    cvss_score=9.0,
                    category='Network',
                    description='Firewall is disabled, system exposed to network threats',
                    remediation='Enable firewall: netsh advfirewall set allprofiles state on',
                    reference='CIS 9.1',
                    checked_value='Disabled',
                    expected_value='Enabled'
                ))
                
        except Exception as e:
            pass
        
        return findings


class UACModule(AuditModule):
    """用户账户控制审计"""
    
    def __init__(self):
        super().__init__('uac', 'User Account Control')
    
    def run(self) -> List[Finding]:
        findings = []
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                r'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System') as key:
                
                try:
                    enable_lua, _ = winreg.QueryValueEx(key, 'EnableLUA')
                    if enable_lua == 0:
                        findings.append(Finding(
                            id='UAC-001',
                            title='UAC disabled',
                            severity=Severity.CRITICAL,
                            cvss_score=9.5,
                            category='Authorization',
                            description='UAC completely disabled, malware can gain admin silently',
                            remediation='Enable UAC: Set EnableLUA = 1',
                            reference='CIS 2.3.17'
                        ))
                except FileNotFoundError:
                    pass
                    
        except Exception as e:
            pass
        
        return findings


class AuditEngine:
    """审计引擎"""
    
    def __init__(self):
        self.modules: List[AuditModule] = []
        self.findings: List[Finding] = []
        self._register_modules()
    
    def _register_modules(self):
        self.modules = [
            SystemInfoModule(),
            PasswordPolicyModule(),
            FirewallModule(),
            UACModule(),
        ]
    
    def run_audit(self, modules: Optional[List[str]] = None) -> List[Finding]:
        self.findings = []
        for module in self.modules:
            if modules is None or module.name in modules:
                print(f"[*] Auditing: {module.name} - {module.description}")
                try:
                    findings = module.run()
                    self.findings.extend(findings)
                    print(f"    Found {len(findings)} issues")
                except Exception as e:
                    print(f"    Audit failed: {e}")
        return self.findings
    
    def generate_report(self, output_format: str = 'json') -> str:
        severity_count = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'Info': 0}
        for finding in self.findings:
            severity_count[finding.severity.label] = severity_count.get(finding.severity.label, 0) + 1
        
        total_weight = sum(f.cvss_score for f in self.findings)
        max_possible = len(self.findings) * 10 if self.findings else 1
        hardening_index = max(0, 100 - (total_weight / max_possible * 100))
        
        report = {
            'scan_id': f'sec-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
            'timestamp': datetime.now().isoformat(),
            'system': {
                'os': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
            },
            'summary': {
                'total_checks': len(self.modules),
                'total_findings': len(self.findings),
                'severity_distribution': severity_count,
                'hardening_index': round(hardening_index, 1),
            },
            'findings': [f.to_dict() for f in sorted(self.findings, key=lambda x: x.cvss_score, reverse=True)],
        }
        
        if output_format == 'json':
            return json.dumps(report, indent=2, ensure_ascii=False)
        
        lines = [
            '=' * 60,
            'SECURITY AUDIT REPORT',
            '=' * 60,
            f"Scan ID: {report['scan_id']}",
            f"Timestamp: {report['timestamp']}",
            f"Hardening Index: {report['summary']['hardening_index']}/100",
            '',
            'SUMMARY:',
            f"  Total Checks: {report['summary']['total_checks']}",
            f"  Findings: {report['summary']['total_findings']}",
        ]
        
        for sev, count in severity_count.items():
            if count > 0:
                lines.append(f"  {sev}: {count}")
        
        lines.extend(['', 'FINDINGS:', '-' * 60])
        
        for finding in report['findings']:
            lines.extend([
                f"[{finding['severity']}] {finding['id']}: {finding['title']}",
                f"  CVSS: {finding['cvss_score']}",
                f"  Description: {finding['description']}",
                f"  Remediation: {finding['remediation']}",
                '',
            ])
        
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Security Audit System')
    parser.add_argument('--level', choices=['1', '2', 'full'], default='full',
                       help='Audit level: 1=Basic, 2=Deep, full=All')
    parser.add_argument('--module', help='Specific module to run (comma-separated)')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format')
    parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    engine = AuditEngine()
    
    modules = None
    if args.module:
        modules = [m.strip() for m in args.module.split(',')]
    elif args.level == '1':
        modules = ['system', 'password', 'firewall', 'uac']
    
    print("=" * 60)
    print("Security Audit Starting...")
    print("=" * 60)
    
    findings = engine.run_audit(modules)
    
    report = engine.generate_report(args.format)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n[+] Report saved to: {args.output}")
    else:
        print("\n" + report)

if __name__ == '__main__':
    main()
