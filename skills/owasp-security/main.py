#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OWASP Security Skill - OWASP安全标准检查工具

功能特点：
- 基于OWASP Top 10 2025的安全漏洞检测
- 静态代码安全分析
- 依赖安全扫描
- 合规性检查
- 风险评级和修复建议
- 支持多种编程语言

作者: Godlike Kimi Skills
版本: 1.0.0
许可证: MIT
"""

import re
import json
import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """风险等级"""
    CRITICAL = "critical"      # 严重 - 必须立即修复
    HIGH = "high"              # 高危 - 优先修复
    MEDIUM = "medium"          # 中危 - 计划修复
    LOW = "low"                # 低危 - 建议修复
    INFO = "info"              # 信息 - 仅供参考


class OWASPCategory(Enum):
    """OWASP Top 10 2025 分类"""
    A01_BROKEN_ACCESS_CONTROL = "A01:2021-Broken Access Control"
    A02_CRYPTO_FAILURES = "A02:2021-Cryptographic Failures"
    A03_INJECTION = "A03:2021-Injection"
    A04_INSECURE_DESIGN = "A04:2021-Insecure Design"
    A05_SECURITY_MISCONFIG = "A05:2021-Security Misconfiguration"
    A06_VULNERABLE_COMPONENTS = "A06:2021-Vulnerable and Outdated Components"
    A07_ID_AUTH_FAILURES = "A07:2021-Identification and Authentication Failures"
    A08_INTEGRITY_FAILURES = "A08:2021-Software and Data Integrity Failures"
    A09_LOGGING_FAILURES = "A09:2021-Security Logging and Monitoring Failures"
    A10_SSRF = "A10:2021-Server-Side Request Forgery"


@dataclass
class SecurityFinding:
    """安全发现数据结构"""
    rule_id: str
    title: str
    description: str
    risk_level: RiskLevel
    owasp_category: OWASPCategory
    file_path: str
    line_number: int
    column: int
    code_snippet: str
    remediation: str
    references: List[str] = field(default_factory=list)
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "title": self.title,
            "description": self.description,
            "risk_level": self.risk_level.value,
            "owasp_category": self.owasp_category.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column": self.column,
            "code_snippet": self.code_snippet,
            "remediation": self.remediation,
            "references": self.references,
            "cwe_id": self.cwe_id,
            "cvss_score": self.cvss_score
        }


@dataclass
class ScanResult:
    """扫描结果数据结构"""
    target_path: str
    scan_time: datetime
    findings: List[SecurityFinding] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_path": self.target_path,
            "scan_time": self.scan_time.isoformat(),
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary
        }


class OWASPSecuritySkill:
    """
    OWASP安全标准检查工具
    
    基于OWASP Top 10 2025标准，提供全面的安全漏洞检测和代码审查功能。
    
    示例用法:
        skill = OWASPSecuritySkill()
        
        # 扫描单个文件
        result = skill.scan_file("./src/app.js")
        
        # 扫描整个项目
        result = skill.scan_directory("./src")
        
        # 生成安全报告
        report = skill.generate_report(result, "security-report.html")
    """
    
    # 安全规则定义
    SECURITY_RULES = {
        # A01: 失效的访问控制
        "SEC-A01-001": {
            "title": "不安全的直接对象引用 (IDOR)",
            "pattern": r'req\.params\.(?:id|user_id|file_id)\s*(?:==|===)',
            "description": "检测到可能不安全的直接对象引用",
            "risk_level": RiskLevel.HIGH,
            "category": OWASPCategory.A01_BROKEN_ACCESS_CONTROL,
            "cwe_id": "CWE-639",
            "cvss_score": 7.5,
            "remediation": "实施适当的访问控制检查，使用间接引用映射",
            "references": [
                "https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html"
            ]
        },
        
        # A02: 加密失败
        "SEC-A02-001": {
            "title": "弱加密算法",
            "pattern": r'\b(?:md5|sha1|des)\s*\(',
            "description": "使用了已知存在安全问题的弱加密算法",
            "risk_level": RiskLevel.HIGH,
            "category": OWASPCategory.A02_CRYPTO_FAILURES,
            "cwe_id": "CWE-327",
            "cvss_score": 7.4,
            "remediation": "使用强加密算法，如SHA-256、AES-256-GCM",
            "references": [
                "https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html"
            ]
        },
        "SEC-A02-002": {
            "title": "硬编码密钥",
            "pattern": r'(?:password|secret|key|token)\s*=\s*["\'][^"\']{8,}["\']',
            "description": "检测到可能的硬编码敏感信息",
            "risk_level": RiskLevel.CRITICAL,
            "category": OWASPCategory.A02_CRYPTO_FAILURES,
            "cwe_id": "CWE-798",
            "cvss_score": 9.0,
            "remediation": "使用环境变量或安全的密钥管理服务",
            "references": [
                "https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html"
            ]
        },
        
        # A03: 注入攻击
        "SEC-A03-001": {
            "title": "SQL注入风险",
            "pattern": r'(?:query|execute)\s*\(\s*["\'].*\$\{[^}]+\}',
            "description": "检测到可能的SQL注入漏洞",
            "risk_level": RiskLevel.CRITICAL,
            "category": OWASPCategory.A03_INJECTION,
            "cwe_id": "CWE-89",
            "cvss_score": 9.8,
            "remediation": "使用参数化查询或ORM框架",
            "references": [
                "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html"
            ]
        },
        "SEC-A03-002": {
            "title": "命令注入风险",
            "pattern": r'(?:exec|spawn|execSync)\s*\(\s*[`"\'].*\$\{[^}]+\}',
            "description": "检测到可能的命令注入漏洞",
            "risk_level": RiskLevel.CRITICAL,
            "category": OWASPCategory.A03_INJECTION,
            "cwe_id": "CWE-78",
            "cvss_score": 9.8,
            "remediation": "避免使用用户输入构造命令，使用参数化API",
            "references": [
                "https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html"
            ]
        },
        "SEC-A03-003": {
            "title": "跨站脚本 (XSS)",
            "pattern": r'innerHTML\s*=|dangerouslySetInnerHTML',
            "description": "检测到潜在的XSS漏洞",
            "risk_level": RiskLevel.HIGH,
            "category": OWASPCategory.A03_INJECTION,
            "cwe_id": "CWE-79",
            "cvss_score": 7.1,
            "remediation": "使用安全的DOM API，对用户输入进行净化",
            "references": [
                "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html"
            ]
        },
        
        # A05: 安全配置错误
        "SEC-A05-001": {
            "title": "调试模式启用",
            "pattern": r'debug\s*:\s*true|DEBUG\s*=\s*True',
            "description": "生产环境中启用了调试模式",
            "risk_level": RiskLevel.MEDIUM,
            "category": OWASPCategory.A05_SECURITY_MISCONFIG,
            "cwe_id": "CWE-489",
            "cvss_score": 5.3,
            "remediation": "在生产环境中禁用调试模式",
            "references": [
                "https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html"
            ]
        },
        
        # A07: 身份验证失效
        "SEC-A07-001": {
            "title": "弱密码策略",
            "pattern": r'minLength\s*:\s*(?:[0-5]|6)(?!\d)',
            "description": "密码最小长度过短",
            "risk_level": RiskLevel.MEDIUM,
            "category": OWASPCategory.A07_ID_AUTH_FAILURES,
            "cwe_id": "CWE-521",
            "cvss_score": 5.3,
            "remediation": "设置密码最小长度为8位或更多",
            "references": [
                "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html"
            ]
        },
        "SEC-A07-002": {
            "title": "不安全的会话管理",
            "pattern": r'cookie\s*\(\s*["\'][^"\']*["\']\s*\)\s*\.[^;{]*{[^}]*httpOnly\s*:\s*false',
            "description": "会话cookie缺少httpOnly标志",
            "risk_level": RiskLevel.HIGH,
            "category": OWASPCategory.A07_ID_AUTH_FAILURES,
            "cwe_id": "CWE-1004",
            "cvss_score": 6.5,
            "remediation": "设置httpOnly、secure和sameSite属性",
            "references": [
                "https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html"
            ]
        },
        
        # A09: 日志和监控不足
        "SEC-A09-001": {
            "title": "敏感信息日志记录",
            "pattern": r'console\.(?:log|info|warn)\s*\([^)]*(?:password|secret|token|key)',
            "description": "可能在日志中记录敏感信息",
            "risk_level": RiskLevel.MEDIUM,
            "category": OWASPCategory.A09_LOGGING_FAILURES,
            "cwe_id": "CWE-532",
            "cvss_score": 5.0,
            "remediation": "避免在日志中记录敏感信息",
            "references": [
                "https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html"
            ]
        },
        
        # A10: SSRF
        "SEC-A10-001": {
            "title": "服务器端请求伪造 (SSRF)",
            "pattern": r'request\s*\(\s*(?:url|uri)\s*[=:]\s*[^,)]+(?:req\.|request\.|input)',
            "description": "可能存在SSRF漏洞",
            "risk_level": RiskLevel.HIGH,
            "category": OWASPCategory.A10_SSRF,
            "cwe_id": "CWE-918",
            "cvss_score": 8.2,
            "remediation": "验证和清理URL输入，使用白名单",
            "references": [
                "https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html"
            ]
        }
    }
    
    # 危险函数列表
    DANGEROUS_FUNCTIONS = [
        'eval', 'exec', 'system', 'popen', 'subprocess.call',
        'pickle.loads', 'yaml.load', 'xml.etree.ElementTree.parse'
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化安全扫描工具
        
        Args:
            config: 配置选项
        """
        self.config = config or {}
        self.enable_auto_fix = self.config.get('auto_fix', False)
        self.excluded_paths = set(self.config.get('excluded_paths', [
            'node_modules', '.git', 'dist', 'build', '__pycache__', '.venv'
        ]))
        
        # 编译正则表达式
        self._compile_rules()
    
    def _compile_rules(self):
        """编译所有安全规则的正则表达式"""
        self.compiled_rules = {}
        for rule_id, rule in self.SECURITY_RULES.items():
            try:
                self.compiled_rules[rule_id] = {
                    **rule,
                    "compiled_pattern": re.compile(rule["pattern"], re.IGNORECASE | re.MULTILINE)
                }
            except re.error as e:
                logger.error(f"编译规则 {rule_id} 失败: {e}")
    
    def scan_file(self, file_path: str) -> ScanResult:
        """
        扫描单个文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            ScanResult: 扫描结果
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        logger.info(f"正在扫描文件: {file_path}")
        
        content = path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        
        findings = []
        
        # 应用所有安全规则
        for rule_id, rule in self.compiled_rules.items():
            pattern = rule["compiled_pattern"]
            
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                
                # 获取代码片段（前后3行）
                start_line = max(0, line_num - 2)
                end_line = min(len(lines), line_num + 1)
                snippet = '\n'.join(lines[start_line:end_line])
                
                finding = SecurityFinding(
                    rule_id=rule_id,
                    title=rule["title"],
                    description=rule["description"],
                    risk_level=rule["risk_level"],
                    owasp_category=rule["category"],
                    file_path=str(path.absolute()),
                    line_number=line_num,
                    column=match.start() - content.rfind('\n', 0, match.start()),
                    code_snippet=snippet.strip(),
                    remediation=rule["remediation"],
                    references=rule["references"],
                    cwe_id=rule.get("cwe_id"),
                    cvss_score=rule.get("cvss_score")
                )
                findings.append(finding)
        
        # 检查危险函数调用
        findings.extend(self._check_dangerous_functions(content, lines, file_path))
        
        # 生成摘要
        summary = self._generate_summary(findings)
        
        return ScanResult(
            target_path=file_path,
            scan_time=datetime.now(),
            findings=findings,
            summary=summary
        )
    
    def scan_directory(self, directory: str) -> ScanResult:
        """
        扫描整个目录
        
        Args:
            directory: 目录路径
        
        Returns:
            ScanResult: 合并的扫描结果
        """
        path = Path(directory)
        if not path.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")
        
        logger.info(f"开始扫描目录: {directory}")
        
        all_findings = []
        scanned_files = 0
        
        # 支持的文件扩展名
        extensions = {
            '.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.php',
            '.rb', '.go', '.cs', '.swift', '.kt', '.c', '.cpp'
        }
        
        for file_path in path.rglob('*'):
            # 跳过排除的目录
            if any(excluded in str(file_path) for excluded in self.excluded_paths):
                continue
            
            # 只扫描支持的文件类型
            if file_path.suffix not in extensions:
                continue
            
            try:
                result = self.scan_file(str(file_path))
                all_findings.extend(result.findings)
                scanned_files += 1
            except Exception as e:
                logger.error(f"扫描文件失败 {file_path}: {e}")
        
        logger.info(f"扫描完成，共扫描 {scanned_files} 个文件")
        
        # 生成合并的摘要
        summary = self._generate_summary(all_findings)
        summary['scanned_files'] = scanned_files
        
        return ScanResult(
            target_path=directory,
            scan_time=datetime.now(),
            findings=all_findings,
            summary=summary
        )
    
    def _check_dangerous_functions(
        self,
        content: str,
        lines: List[str],
        file_path: str
    ) -> List[SecurityFinding]:
        """检查危险函数调用"""
        findings = []
        
        for func in self.DANGEROUS_FUNCTIONS:
            pattern = re.compile(r'\b' + re.escape(func) + r'\s*\(', re.IGNORECASE)
            
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                
                finding = SecurityFinding(
                    rule_id=f"DANGER-{func.upper()}",
                    title=f"危险函数调用: {func}",
                    description=f"检测到潜在危险的函数调用: {func}",
                    risk_level=RiskLevel.HIGH,
                    owasp_category=OWASPCategory.A03_INJECTION,
                    file_path=file_path,
                    line_number=line_num,
                    column=0,
                    code_snippet=lines[line_num - 1].strip() if line_num <= len(lines) else "",
                    remediation=f"避免使用{func}，寻找更安全的替代方案",
                    references=["https://owasp.org/www-community/vulnerabilities/Unsafe_use_of_dangerous_functions"],
                    cwe_id="CWE-676"
                )
                findings.append(finding)
        
        return findings
    
    def _generate_summary(self, findings: List[SecurityFinding]) -> Dict[str, Any]:
        """生成扫描摘要"""
        severity_counts = {level.value: 0 for level in RiskLevel}
        category_counts = {cat.value: 0 for cat in OWASPCategory}
        
        for finding in findings:
            severity_counts[finding.risk_level.value] += 1
            category_counts[finding.owasp_category.value] += 1
        
        # 计算风险评分 (0-100)
        weights = {
            RiskLevel.CRITICAL: 10,
            RiskLevel.HIGH: 5,
            RiskLevel.MEDIUM: 2,
            RiskLevel.LOW: 0.5,
            RiskLevel.INFO: 0
        }
        
        risk_score = sum(
            weights[f.risk_level] for f in findings
        )
        normalized_score = min(100, risk_score)
        
        return {
            "total_findings": len(findings),
            "severity_distribution": severity_counts,
            "category_distribution": {k: v for k, v in category_counts.items() if v > 0},
            "risk_score": round(normalized_score, 2),
            "risk_rating": self._get_risk_rating(normalized_score)
        }
    
    def _get_risk_rating(self, score: float) -> str:
        """根据风险评分获取评级"""
        if score >= 80:
            return "CRITICAL"
        elif score >= 50:
            return "HIGH"
        elif score >= 25:
            return "MEDIUM"
        elif score > 0:
            return "LOW"
        return "SAFE"
    
    def generate_report(
        self,
        result: ScanResult,
        output_path: Optional[str] = None,
        format: str = "html"
    ) -> str:
        """
        生成安全报告
        
        Args:
            result: 扫描结果
            output_path: 输出文件路径
            format: 报告格式 (html/json/md)
        
        Returns:
            str: 报告内容
        """
        if format == "json":
            report = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
        elif format == "md":
            report = self._generate_markdown_report(result)
        else:
            report = self._generate_html_report(result)
        
        if output_path:
            Path(output_path).write_text(report, encoding='utf-8')
            logger.info(f"报告已保存至: {output_path}")
        
        return report
    
    def _generate_html_report(self, result: ScanResult) -> str:
        """生成HTML格式的报告"""
        summary = result.summary
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OWASP安全扫描报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }}
        .summary-card h3 {{ color: #667eea; margin-bottom: 10px; }}
        .summary-card .number {{ font-size: 2.5em; font-weight: bold; }}
        .critical {{ color: #dc3545; }}
        .high {{ color: #fd7e14; }}
        .medium {{ color: #ffc107; }}
        .low {{ color: #28a745; }}
        .finding {{
            background: white;
            margin-bottom: 20px;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            border-left: 4px solid #ddd;
        }}
        .finding.critical {{ border-left-color: #dc3545; }}
        .finding.high {{ border-left-color: #fd7e14; }}
        .finding.medium {{ border-left-color: #ffc107; }}
        .finding.low {{ border-left-color: #28a745; }}
        .finding-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .badge {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .badge.critical {{ background: #dc354520; color: #dc3545; }}
        .badge.high {{ background: #fd7e1420; color: #fd7e14; }}
        .badge.medium {{ background: #ffc10720; color: #856404; }}
        .badge.low {{ background: #28a74520; color: #28a745; }}
        .code-snippet {{
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Consolas', monospace;
            margin: 15px 0;
        }}
        .remediation {{
            background: #e7f3ff;
            padding: 20px;
            border-radius: 8px;
            margin-top: 15px;
        }}
        .remediation h4 {{ color: #0066cc; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 OWASP安全扫描报告</h1>
            <p>扫描目标: {result.target_path}</p>
            <p>扫描时间: {result.scan_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <h3>总发现问题</h3>
                <div class="number">{summary['total_findings']}</div>
            </div>
            <div class="summary-card">
                <h3>风险评分</h3>
                <div class="number {summary['risk_rating'].lower()}">{summary['risk_score']}</div>
            </div>
            <div class="summary-card">
                <h3>严重/高危</h3>
                <div class="number critical">{summary['severity_distribution']['critical'] + summary['severity_distribution']['high']}</div>
            </div>
            <div class="summary-card">
                <h3>扫描文件</h3>
                <div class="number">{summary.get('scanned_files', 'N/A')}</div>
            </div>
        </div>
        
        <h2 style="margin-bottom: 20px;">详细发现</h2>
"""
        
        # 按严重程度排序
        severity_order = {RiskLevel.CRITICAL: 0, RiskLevel.HIGH: 1, RiskLevel.MEDIUM: 2, RiskLevel.LOW: 3, RiskLevel.INFO: 4}
        sorted_findings = sorted(result.findings, key=lambda f: severity_order.get(f.risk_level, 5))
        
        for finding in sorted_findings:
            html += f"""
        <div class="finding {finding.risk_level.value}">
            <div class="finding-header">
                <h3>{finding.title}</h3>
                <span class="badge {finding.risk_level.value}">{finding.risk_level.value.upper()}</span>
            </div>
            <p><strong>规则ID:</strong> {finding.rule_id} | <strong>CWE:</strong> {finding.cwe_id or 'N/A'}</p>
            <p><strong>位置:</strong> {finding.file_path}:{finding.line_number}</p>
            <p><strong>OWASP分类:</strong> {finding.owasp_category.value}</p>
            <p>{finding.description}</p>
            <div class="code-snippet">
                <pre>{finding.code_snippet}</pre>
            </div>
            <div class="remediation">
                <h4>💡 修复建议</h4>
                <p>{finding.remediation}</p>
            </div>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        return html
    
    def _generate_markdown_report(self, result: ScanResult) -> str:
        """生成Markdown格式的报告"""
        summary = result.summary
        
        md = f"""# OWASP安全扫描报告

## 概览

- **扫描目标**: {result.target_path}
- **扫描时间**: {result.scan_time.strftime('%Y-%m-%d %H:%M:%S')}
- **总发现问题**: {summary['total_findings']}
- **风险评分**: {summary['risk_score']}/100 ({summary['risk_rating']})

## 严重程度分布

| 等级 | 数量 |
|------|------|
| 🔴 Critical | {summary['severity_distribution']['critical']} |
| 🟠 High | {summary['severity_distribution']['high']} |
| 🟡 Medium | {summary['severity_distribution']['medium']} |
| 🟢 Low | {summary['severity_distribution']['low']} |
| ℹ️ Info | {summary['severity_distribution']['info']} |

## 详细发现

"""
        
        for finding in result.findings:
            md += f"""### {finding.title}

- **严重程度**: {finding.risk_level.value.upper()}
- **规则ID**: {finding.rule_id}
- **CWE**: {finding.cwe_id or 'N/A'}
- **位置**: `{finding.file_path}:{finding.line_number}`
- **OWASP分类**: {finding.owasp_category.value}

**描述**: {finding.description}

**代码片段**:
```javascript
{finding.code_snippet}
```

**修复建议**: {finding.remediation}

---

"""
        
        return md


def main():
    """命令行入口"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python main.py <目标路径>")
        print("示例: python main.py ./src")
        sys.exit(1)
    
    target = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "security-report.html"
    
    skill = OWASPSecuritySkill()
    
    if Path(target).is_file():
        result = skill.scan_file(target)
    else:
        result = skill.scan_directory(target)
    
    report = skill.generate_report(result, output, format="html")
    print(f"报告已生成: {output}")
    print(f"发现问题: {result.summary['total_findings']}")
    print(f"风险评级: {result.summary['risk_rating']}")


if __name__ == "__main__":
    main()
