"""
Static Analysis Skill
=====================

专业的Python代码静态分析工具，支持代码质量检查、复杂度分析、
安全检查、风格检查和自动生成报告。

Author: Godlike Kimi Skills
License: MIT
Version: 1.0.0
"""

import argparse
import ast
import hashlib
import json
import logging
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class AnalysisConfig:
    """分析配置数据类"""
    target: str = ""
    output_dir: str = "./analysis-results"
    exclude_patterns: List[str] = field(default_factory=lambda: [
        '__pycache__', '*.pyc', '.git', '.venv', 'venv', 'env',
        '.pytest_cache', '.mypy_cache', 'node_modules', '.tox'
    ])
    min_complexity: int = 10
    max_line_length: int = 100
    strict_mode: bool = False
    baseline_path: Optional[str] = None
    format: str = "html"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class ComplexityMetrics:
    """复杂度指标数据类"""
    file_path: str
    function_name: str
    line_number: int
    cyclomatic_complexity: int
    cognitive_complexity: int = 0
    lines_of_code: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class SecurityIssue:
    """安全问题数据类"""
    file_path: str
    line_number: int
    issue_type: str
    severity: str  # critical, high, medium, low
    message: str
    confidence: str = "medium"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class StyleIssue:
    """风格问题数据类"""
    file_path: str
    line_number: int
    column: int
    code: str
    message: str
    severity: str = "warning"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class FileMetrics:
    """文件指标数据类"""
    file_path: str
    lines_of_code: int
    blank_lines: int
    comment_lines: int
    functions_count: int
    classes_count: int
    imports_count: int
    average_complexity: float = 0.0
    maintainability_index: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class AnalysisReport:
    """分析报告数据类"""
    timestamp: str
    target: str
    total_files: int
    total_lines: int
    complexity_issues: List[ComplexityMetrics] = field(default_factory=list)
    security_issues: List[SecurityIssue] = field(default_factory=list)
    style_issues: List[StyleIssue] = field(default_factory=list)
    file_metrics: List[FileMetrics] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'timestamp': self.timestamp,
            'target': self.target,
            'total_files': self.total_files,
            'total_lines': self.total_lines,
            'complexity_issues': [c.to_dict() for c in self.complexity_issues],
            'security_issues': [s.to_dict() for s in self.security_issues],
            'style_issues': [s.to_dict() for s in self.style_issues],
            'file_metrics': [f.to_dict() for f in self.file_metrics],
            'summary': self.summary
        }


class PythonFileCollector:
    """Python文件收集器"""
    
    def __init__(self, exclude_patterns: List[str]):
        self.exclude_patterns = exclude_patterns
    
    def should_exclude(self, path: Path) -> bool:
        """检查是否应该排除"""
        path_str = str(path)
        for pattern in self.exclude_patterns:
            if pattern in path_str:
                return True
            if path.match(pattern):
                return True
        return False
    
    def collect(self, target: str) -> List[Path]:
        """
        收集Python文件
        
        Args:
            target: 目标路径（文件或目录）
            
        Returns:
            Python文件路径列表
        """
        target_path = Path(target)
        files = []
        
        if target_path.is_file() and target_path.suffix == '.py':
            files.append(target_path)
        elif target_path.is_dir():
            for py_file in target_path.rglob('*.py'):
                if not self.should_exclude(py_file):
                    files.append(py_file)
        
        return sorted(files)


class ComplexityAnalyzer:
    """复杂度分析器"""
    
    def __init__(self, min_complexity: int = 10):
        self.min_complexity = min_complexity
    
    def analyze_file(self, file_path: Path) -> List[ComplexityMetrics]:
        """
        分析文件复杂度
        
        Args:
            file_path: Python文件路径
            
        Returns:
            复杂度指标列表
        """
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # 计算圈复杂度
                    complexity = self._calculate_cyclomatic_complexity(node)
                    
                    if complexity >= self.min_complexity:
                        metrics = ComplexityMetrics(
                            file_path=str(file_path),
                            function_name=node.name,
                            line_number=node.lineno,
                            cyclomatic_complexity=complexity,
                            lines_of_code=len(node.body)
                        )
                        issues.append(metrics)
                
                elif isinstance(node, ast.ClassDef):
                    # 分析类中的方法
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            complexity = self._calculate_cyclomatic_complexity(item)
                            
                            if complexity >= self.min_complexity:
                                metrics = ComplexityMetrics(
                                    file_path=str(file_path),
                                    function_name=f"{node.name}.{item.name}",
                                    line_number=item.lineno,
                                    cyclomatic_complexity=complexity,
                                    lines_of_code=len(item.body)
                                )
                                issues.append(metrics)
        
        except Exception as e:
            logger.error(f"Failed to analyze complexity for {file_path}: {e}")
        
        return issues
    
    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """
        计算圈复杂度
        
        Args:
            node: AST节点
            
        Returns:
            圈复杂度值
        """
        complexity = 1  # 基础复杂度
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity


class SecurityScanner:
    """安全扫描器"""
    
    # 危险函数和模式
    DANGEROUS_PATTERNS = {
        'eval': ('critical', 'Use of eval() is dangerous and should be avoided'),
        'exec': ('critical', 'Use of exec() is dangerous and should be avoided'),
        'compile': ('high', 'Dynamic code compilation can be unsafe'),
        '__import__': ('medium', 'Dynamic imports can be unsafe'),
        'subprocess.call': ('medium', 'Shell execution can be dangerous'),
        'os.system': ('medium', 'Shell execution can be dangerous'),
        'pickle.loads': ('high', 'Deserializing untrusted data is dangerous'),
        'yaml.load': ('high', 'Unsafe YAML loading, use yaml.safe_load() instead'),
        'input': ('low', 'input() can be unsafe in Python 2 compatibility mode'),
    }
    
    def __init__(self):
        self.issues: List[SecurityIssue] = []
    
    def scan_file(self, file_path: Path) -> List[SecurityIssue]:
        """
        扫描文件安全问题
        
        Args:
            file_path: Python文件路径
            
        Returns:
            安全问题列表
        """
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            for node in ast.walk(tree):
                # 检查危险函数调用
                if isinstance(node, ast.Call):
                    issue = self._check_dangerous_call(node, file_path)
                    if issue:
                        issues.append(issue)
                
                # 检查硬编码密码/密钥
                if isinstance(node, ast.Assign):
                    issue = self._check_hardcoded_secrets(node, file_path)
                    if issue:
                        issues.append(issue)
            
            # 使用正则表达式检查SQL注入模式
            issues.extend(self._check_sql_injection(source, file_path))
        
        except Exception as e:
            logger.error(f"Failed to scan security for {file_path}: {e}")
        
        return issues
    
    def _check_dangerous_call(self, node: ast.Call, file_path: Path) -> Optional[SecurityIssue]:
        """检查危险函数调用"""
        func_name = None
        
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        if func_name and func_name in self.DANGEROUS_PATTERNS:
            severity, message = self.DANGEROUS_PATTERNS[func_name]
            return SecurityIssue(
                file_path=str(file_path),
                line_number=getattr(node, 'lineno', 0),
                issue_type=f'dangerous_function_{func_name}',
                severity=severity,
                message=message
            )
        
        return None
    
    def _check_hardcoded_secrets(self, node: ast.Assign, file_path: Path) -> Optional[SecurityIssue]:
        """检查硬编码密钥"""
        secret_patterns = [
            r'password\s*=',
            r'secret\s*=',
            r'api_key\s*=',
            r'token\s*=',
            r'private_key\s*=',
        ]
        
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id.lower()
                if any(pattern.replace('\\s*=', '') in name for pattern in secret_patterns):
                    # 检查是否是字符串赋值
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        if len(node.value.value) > 8:  # 忽略短字符串
                            return SecurityIssue(
                                file_path=str(file_path),
                                line_number=node.lineno,
                                issue_type='hardcoded_secret',
                                severity='high',
                                message=f'Possible hardcoded secret in variable: {target.id}'
                            )
        
        return None
    
    def _check_sql_injection(self, source: str, file_path: Path) -> List[SecurityIssue]:
        """检查SQL注入风险"""
        issues = []
        
        # 简单的字符串拼接SQL检测
        sql_patterns = [
            (r'execute\s*\(\s*["\'].*%s', 'potential_sql_injection_format'),
            (r'execute\s*\(\s*f["\']', 'potential_sql_injection_fstring'),
            (r'\.format\s*\(.*\).*SELECT|INSERT|UPDATE|DELETE', 'potential_sql_injection_format'),
        ]
        
        lines = source.split('\n')
        for i, line in enumerate(lines, 1):
            for pattern, issue_type in sql_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(SecurityIssue(
                        file_path=str(file_path),
                        line_number=i,
                        issue_type=issue_type,
                        severity='high',
                        message='Potential SQL injection vulnerability detected'
                    ))
        
        return issues


class StyleChecker:
    """风格检查器"""
    
    def __init__(self, max_line_length: int = 100):
        self.max_line_length = max_line_length
    
    def check_file(self, file_path: Path) -> List[StyleIssue]:
        """
        检查文件风格
        
        Args:
            file_path: Python文件路径
            
        Returns:
            风格问题列表
        """
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # 检查行长度
                if len(line.rstrip()) > self.max_line_length:
                    issues.append(StyleIssue(
                        file_path=str(file_path),
                        line_number=i,
                        column=self.max_line_length,
                        code='E501',
                        message=f'Line too long ({len(line.rstrip())} > {self.max_line_length} characters)',
                        severity='warning'
                    ))
                
                # 检查尾随空格
                if line.rstrip() != line.rstrip(' \n') and line.strip():
                    issues.append(StyleIssue(
                        file_path=str(file_path),
                        line_number=i,
                        column=len(line.rstrip(' \n')) + 1,
                        code='W291',
                        message='Trailing whitespace',
                        severity='info'
                    ))
                
                # 检查缩进（应该是4个空格）
                if line.strip() and line[0] == '\t':
                    issues.append(StyleIssue(
                        file_path=str(file_path),
                        line_number=i,
                        column=1,
                        code='W191',
                        message='Indentation contains tabs',
                        severity='warning'
                    ))
                elif line.strip() and len(line) - len(line.lstrip()) % 4 != 0:
                    # 非4的倍数缩进
                    stripped = line.lstrip()
                    if stripped and not line.strip().startswith('#'):
                        issues.append(StyleIssue(
                            file_path=str(file_path),
                            line_number=i,
                            column=1,
                            code='E111',
                            message='Indentation is not a multiple of 4',
                            severity='warning'
                        ))
                
                # 检查导入格式
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    if not line.strip().endswith(')') and ' import ' in line and ',' in line:
                        issues.append(StyleIssue(
                            file_path=str(file_path),
                            line_number=i,
                            column=1,
                            code='E401',
                            message='Multiple imports on one line',
                            severity='warning'
                        ))
        
        except Exception as e:
            logger.error(f"Failed to check style for {file_path}: {e}")
        
        return issues


class MetricsCollector:
    """指标收集器"""
    
    def collect_file_metrics(self, file_path: Path) -> FileMetrics:
        """
        收集文件指标
        
        Args:
            file_path: Python文件路径
            
        Returns:
            文件指标
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
                lines = source.split('\n')
            
            tree = ast.parse(source)
            
            # 基础统计
            total_lines = len(lines)
            blank_lines = sum(1 for line in lines if not line.strip())
            comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
            
            # AST统计
            functions_count = sum(1 for node in ast.walk(tree) 
                                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))
            classes_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
            imports_count = sum(1 for node in ast.walk(tree) 
                              if isinstance(node, (ast.Import, ast.ImportFrom)))
            
            # 计算平均复杂度和可维护性指数
            complexity_analyzer = ComplexityAnalyzer(min_complexity=1)
            complexities = complexity_analyzer.analyze_file(file_path)
            
            avg_complexity = 0.0
            if complexities:
                avg_complexity = sum(c.cyclomatic_complexity for c in complexities) / len(complexities)
            
            # 简化的可维护性指数计算
            # MI = 171 - 5.2 * ln(Halstead Volume) - 0.23 * CC - 16.2 * ln(Lines)
            # 这里使用简化版本
            maintainability_index = max(0, min(100, 100 - avg_complexity * 5 - (total_lines / 100)))
            
            return FileMetrics(
                file_path=str(file_path),
                lines_of_code=total_lines - blank_lines - comment_lines,
                blank_lines=blank_lines,
                comment_lines=comment_lines,
                functions_count=functions_count,
                classes_count=classes_count,
                imports_count=imports_count,
                average_complexity=round(avg_complexity, 2),
                maintainability_index=round(maintainability_index, 2)
            )
        
        except Exception as e:
            logger.error(f"Failed to collect metrics for {file_path}: {e}")
            return FileMetrics(
                file_path=str(file_path),
                lines_of_code=0,
                blank_lines=0,
                comment_lines=0,
                functions_count=0,
                classes_count=0,
                imports_count=0
            )


class ReportGenerator:
    """报告生成器"""
    
    @staticmethod
    def generate_html_report(report: AnalysisReport, output_path: str) -> str:
        """
        生成HTML报告
        
        Args:
            report: 分析报告
            output_path: 输出路径
            
        Returns:
            报告文件路径
        """
        severity_colors = {
            'critical': '#dc2626',
            'high': '#ea580c',
            'medium': '#ca8a04',
            'low': '#16a34a',
            'info': '#0891b2',
            'warning': '#ca8a04'
        }
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Static Analysis Report - {report.target}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .card h3 {{
            margin-top: 0;
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
        }}
        .card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }}
        .section {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .section h2 {{
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #666;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .severity {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            color: white;
        }}
        .complexity-high {{ background: #dc2626; }}
        .complexity-medium {{ background: #ca8a04; }}
        .complexity-low {{ background: #16a34a; }}
        .maintainability-good {{ color: #16a34a; }}
        .maintainability-moderate {{ color: #ca8a04; }}
        .maintainability-poor {{ color: #dc2626; }}
        .timestamp {{ color: #999; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Static Analysis Report</h1>
        <p>Target: {report.target}</p>
        <p class="timestamp">Generated: {report.timestamp}</p>
    </div>
    
    <div class="summary">
        <div class="card">
            <h3>Total Files</h3>
            <div class="value">{report.total_files}</div>
        </div>
        <div class="card">
            <h3>Total Lines</h3>
            <div class="value">{report.total_lines:,}</div>
        </div>
        <div class="card">
            <h3>Complexity Issues</h3>
            <div class="value" style="color: {'#dc2626' if len(report.complexity_issues) > 10 else '#ca8a04' if len(report.complexity_issues) > 0 else '#16a34a'}">{len(report.complexity_issues)}</div>
        </div>
        <div class="card">
            <h3>Security Issues</h3>
            <div class="value" style="color: {'#dc2626' if len(report.security_issues) > 0 else '#16a34a'}">{len(report.security_issues)}</div>
        </div>
        <div class="card">
            <h3>Style Issues</h3>
            <div class="value" style="color: {'#ca8a04' if len(report.style_issues) > 20 else '#16a34a'}">{len(report.style_issues)}</div>
        </div>
    </div>
"""
        
        # 复杂度问题
        if report.complexity_issues:
            html_content += """
    <div class="section">
        <h2>🔄 Complexity Issues</h2>
        <table>
            <thead>
                <tr>
                    <th>File</th>
                    <th>Function</th>
                    <th>Line</th>
                    <th>Cyclomatic Complexity</th>
                    <th>Lines of Code</th>
                </tr>
            </thead>
            <tbody>
"""
            for issue in sorted(report.complexity_issues, key=lambda x: x.cyclomatic_complexity, reverse=True):
                complexity_class = 'complexity-high' if issue.cyclomatic_complexity >= 20 else 'complexity-medium' if issue.cyclomatic_complexity >= 10 else 'complexity-low'
                html_content += f"""
                <tr>
                    <td>{issue.file_path}</td>
                    <td>{issue.function_name}</td>
                    <td>{issue.line_number}</td>
                    <td><span class="severity {complexity_class}">{issue.cyclomatic_complexity}</span></td>
                    <td>{issue.lines_of_code}</td>
                </tr>
"""
            html_content += """
            </tbody>
        </table>
    </div>
"""
        
        # 安全问题
        if report.security_issues:
            html_content += """
    <div class="section">
        <h2>🔒 Security Issues</h2>
        <table>
            <thead>
                <tr>
                    <th>Severity</th>
                    <th>Type</th>
                    <th>File</th>
                    <th>Line</th>
                    <th>Message</th>
                </tr>
            </thead>
            <tbody>
"""
            for issue in sorted(report.security_issues, key=lambda x: ['critical', 'high', 'medium', 'low'].index(x.severity)):
                color = severity_colors.get(issue.severity, '#666')
                html_content += f"""
                <tr>
                    <td><span class="severity" style="background: {color}">{issue.severity.upper()}</span></td>
                    <td>{issue.issue_type}</td>
                    <td>{issue.file_path}</td>
                    <td>{issue.line_number}</td>
                    <td>{issue.message}</td>
                </tr>
"""
            html_content += """
            </tbody>
        </table>
    </div>
"""
        
        # 风格问题
        if report.style_issues:
            html_content += """
    <div class="section">
        <h2>🎨 Style Issues</h2>
        <table>
            <thead>
                <tr>
                    <th>Code</th>
                    <th>File</th>
                    <th>Line</th>
                    <th>Column</th>
                    <th>Message</th>
                </tr>
            </thead>
            <tbody>
"""
            for issue in report.style_issues[:50]:  # 限制显示数量
                html_content += f"""
                <tr>
                    <td><code>{issue.code}</code></td>
                    <td>{issue.file_path}</td>
                    <td>{issue.line_number}</td>
                    <td>{issue.column}</td>
                    <td>{issue.message}</td>
                </tr>
"""
            if len(report.style_issues) > 50:
                html_content += f"""
                <tr>
                    <td colspan="5" style="text-align: center; color: #666;">
                        ... and {len(report.style_issues) - 50} more issues
                    </td>
                </tr>
"""
            html_content += """
            </tbody>
        </table>
    </div>
"""
        
        # 文件指标
        if report.file_metrics:
            html_content += """
    <div class="section">
        <h2>📊 File Metrics</h2>
        <table>
            <thead>
                <tr>
                    <th>File</th>
                    <th>Lines</th>
                    <th>Code</th>
                    <th>Blank</th>
                    <th>Comments</th>
                    <th>Functions</th>
                    <th>Classes</th>
                    <th>Avg Complexity</th>
                    <th>Maintainability</th>
                </tr>
            </thead>
            <tbody>
"""
            for metric in sorted(report.file_metrics, key=lambda x: x.lines_of_code, reverse=True):
                mi_class = 'maintainability-poor' if metric.maintainability_index < 50 else 'maintainability-moderate' if metric.maintainability_index < 80 else 'maintainability-good'
                html_content += f"""
                <tr>
                    <td>{metric.file_path}</td>
                    <td>{metric.lines_of_code + metric.blank_lines + metric.comment_lines}</td>
                    <td>{metric.lines_of_code}</td>
                    <td>{metric.blank_lines}</td>
                    <td>{metric.comment_lines}</td>
                    <td>{metric.functions_count}</td>
                    <td>{metric.classes_count}</td>
                    <td>{metric.average_complexity}</td>
                    <td class="{mi_class}">{metric.maintainability_index}</td>
                </tr>
"""
            html_content += """
            </tbody>
        </table>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {output_path}")
        return output_path
    
    @staticmethod
    def generate_json_report(report: AnalysisReport, output_path: str) -> str:
        """生成JSON报告"""
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"JSON report generated: {output_path}")
        return output_path
    
    @staticmethod
    def generate_markdown_report(report: AnalysisReport, output_path: str) -> str:
        """生成Markdown报告"""
        content = f"""# Static Analysis Report

**Target:** {report.target}  
**Generated:** {report.timestamp}

## Summary

| Metric | Value |
|--------|-------|
| Total Files | {report.total_files} |
| Total Lines | {report.total_lines:,} |
| Complexity Issues | {len(report.complexity_issues)} |
| Security Issues | {len(report.security_issues)} |
| Style Issues | {len(report.style_issues)} |

"""
        
        if report.complexity_issues:
            content += "\n## Complexity Issues\n\n"
            content += "| File | Function | Line | Complexity |\n"
            content += "|------|----------|------|------------|\n"
            for issue in sorted(report.complexity_issues, key=lambda x: x.cyclomatic_complexity, reverse=True)[:20]:
                content += f"| {issue.file_path} | {issue.function_name} | {issue.line_number} | {issue.cyclomatic_complexity} |\n"
        
        if report.security_issues:
            content += "\n## Security Issues\n\n"
            content += "| Severity | Type | File | Line | Message |\n"
            content += "|----------|------|------|------|---------|\n"
            for issue in sorted(report.security_issues, key=lambda x: ['critical', 'high', 'medium', 'low'].index(x.severity)):
                content += f"| {issue.severity} | {issue.issue_type} | {issue.file_path} | {issue.line_number} | {issue.message} |\n"
        
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Markdown report generated: {output_path}")
        return output_path


class StaticAnalyzer:
    """静态分析器主类"""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.file_collector = PythonFileCollector(config.exclude_patterns)
        self.complexity_analyzer = ComplexityAnalyzer(config.min_complexity)
        self.security_scanner = SecurityScanner()
        self.style_checker = StyleChecker(config.max_line_length)
        self.metrics_collector = MetricsCollector()
    
    def analyze(self) -> AnalysisReport:
        """
        执行完整分析
        
        Returns:
            分析报告
        """
        logger.info(f"Starting analysis of: {self.config.target}")
        
        # 收集文件
        files = self.file_collector.collect(self.config.target)
        logger.info(f"Found {len(files)} Python files")
        
        report = AnalysisReport(
            timestamp=datetime.now().isoformat(),
            target=self.config.target,
            total_files=len(files),
            total_lines=0
        )
        
        # 分析每个文件
        for file_path in files:
            logger.debug(f"Analyzing: {file_path}")
            
            # 复杂度分析
            complexity_issues = self.complexity_analyzer.analyze_file(file_path)
            report.complexity_issues.extend(complexity_issues)
            
            # 安全扫描
            security_issues = self.security_scanner.scan_file(file_path)
            report.security_issues.extend(security_issues)
            
            # 风格检查
            style_issues = self.style_checker.check_file(file_path)
            report.style_issues.extend(style_issues)
            
            # 指标收集
            metrics = self.metrics_collector.collect_file_metrics(file_path)
            report.file_metrics.append(metrics)
            report.total_lines += metrics.lines_of_code + metrics.blank_lines + metrics.comment_lines
        
        # 生成汇总
        report.summary = self._generate_summary(report)
        
        logger.info("Analysis completed")
        return report
    
    def _generate_summary(self, report: AnalysisReport) -> Dict[str, Any]:
        """生成汇总信息"""
        return {
            'complexity_score': len(report.complexity_issues),
            'security_score': len(report.security_issues),
            'style_score': len(report.style_issues),
            'avg_maintainability': round(
                sum(f.maintainability_index for f in report.file_metrics) / max(len(report.file_metrics), 1), 2
            ),
            'avg_complexity': round(
                sum(f.average_complexity for f in report.file_metrics) / max(len(report.file_metrics), 1), 2
            ),
            'total_functions': sum(f.functions_count for f in report.file_metrics),
            'total_classes': sum(f.classes_count for f in report.file_metrics),
        }


def generate_config_template(output_path: str = './analysis-config.json') -> str:
    """生成配置文件模板"""
    template = {
        'target': './src',
        'output_dir': './analysis-results',
        'exclude_patterns': [
            '__pycache__',
            '*.pyc',
            '.git',
            'venv',
            '.venv',
            'node_modules'
        ],
        'min_complexity': 10,
        'max_line_length': 100,
        'strict_mode': False,
        'format': 'html'
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Config template generated: {output_path}")
    return output_path


def compare_reports(baseline_path: str, current_path: str) -> Dict[str, Any]:
    """对比两份报告"""
    with open(baseline_path, 'r', encoding='utf-8') as f:
        baseline = json.load(f)
    with open(current_path, 'r', encoding='utf-8') as f:
        current = json.load(f)
    
    comparison = {
        'baseline_timestamp': baseline.get('timestamp'),
        'current_timestamp': current.get('timestamp'),
        'differences': {
            'total_files': current.get('total_files', 0) - baseline.get('total_files', 0),
            'total_lines': current.get('total_lines', 0) - baseline.get('total_lines', 0),
            'complexity_issues': len(current.get('complexity_issues', [])) - len(baseline.get('complexity_issues', [])),
            'security_issues': len(current.get('security_issues', [])) - len(baseline.get('security_issues', [])),
            'style_issues': len(current.get('style_issues', [])) - len(baseline.get('style_issues', [])),
        }
    }
    
    return comparison


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(description='Python Static Analysis Tool')
    parser.add_argument('--action', required=True,
                       choices=['analyze', 'complexity', 'security', 'style', 'compare', 'generate-config'],
                       help='Action to perform')
    parser.add_argument('--target', help='Target file or directory to analyze')
    parser.add_argument('--output-dir', default='./analysis-results',
                       help='Output directory for reports')
    parser.add_argument('--exclude-patterns',
                       help='Comma-separated exclude patterns')
    parser.add_argument('--min-complexity', type=int, default=10,
                       help='Minimum complexity threshold')
    parser.add_argument('--max-line-length', type=int, default=100,
                       help='Maximum line length')
    parser.add_argument('--strict-mode', action='store_true',
                       help='Enable strict mode')
    parser.add_argument('--baseline-path', help='Baseline report path for comparison')
    parser.add_argument('--format', default='html',
                       choices=['html', 'json', 'markdown'],
                       help='Report format')
    
    args = parser.parse_args()
    
    if args.action == 'generate-config':
        path = generate_config_template()
        print(f"Configuration template generated: {path}")
        return
    
    if not args.target:
        parser.error("--target is required for this action")
    
    # 创建配置
    exclude_patterns = None
    if args.exclude_patterns:
        exclude_patterns = [p.strip() for p in args.exclude_patterns.split(',')]
    
    config = AnalysisConfig(
        target=args.target,
        output_dir=args.output_dir,
        exclude_patterns=exclude_patterns or AnalysisConfig.exclude_patterns,
        min_complexity=args.min_complexity,
        max_line_length=args.max_line_length,
        strict_mode=args.strict_mode,
        format=args.format
    )
    
    # 执行分析
    analyzer = StaticAnalyzer(config)
    report = analyzer.analyze()
    
    # 生成报告
    os.makedirs(config.output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if config.format == 'html':
        output_path = os.path.join(config.output_dir, f'report_{timestamp}.html')
        ReportGenerator.generate_html_report(report, output_path)
    elif config.format == 'json':
        output_path = os.path.join(config.output_dir, f'report_{timestamp}.json')
        ReportGenerator.generate_json_report(report, output_path)
    elif config.format == 'markdown':
        output_path = os.path.join(config.output_dir, f'report_{timestamp}.md')
        ReportGenerator.generate_markdown_report(report, output_path)
    
    # 对比报告
    if args.baseline_path and args.action == 'compare':
        current_path = os.path.join(config.output_dir, f'report_{timestamp}.json')
        ReportGenerator.generate_json_report(report, current_path)
        comparison = compare_reports(args.baseline_path, current_path)
        print("\nComparison with baseline:")
        print(json.dumps(comparison, indent=2, ensure_ascii=False))
    
    # 打印摘要
    print("\n" + "=" * 50)
    print("Analysis Summary")
    print("=" * 50)
    print(f"Total Files: {report.total_files}")
    print(f"Total Lines: {report.total_lines:,}")
    print(f"Complexity Issues: {len(report.complexity_issues)}")
    print(f"Security Issues: {len(report.security_issues)}")
    print(f"Style Issues: {len(report.style_issues)}")
    print(f"\nReport saved to: {output_path}")
    
    # 根据问题数量设置退出码
    exit_code = 0
    if report.security_issues:
        exit_code = 2
    elif report.complexity_issues or report.style_issues:
        exit_code = 1
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
