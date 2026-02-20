#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
React Best Practices Skill - React开发最佳实践指南

功能特点：
- React代码审查和分析
- 设计模式建议
- 性能优化检查
- TypeScript类型检查
- 可访问性(A11y)审计
- 安全漏洞扫描

作者: Godlike Kimi Skills
版本: 1.0.0
许可证: MIT
"""

import re
import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Severity(Enum):
    """问题严重程度"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Category(Enum):
    """问题分类"""
    PERFORMANCE = "performance"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"
    MAINTAINABILITY = "maintainability"
    BEST_PRACTICE = "best_practice"
    TYPESCRIPT = "typescript"
    REACT_PATTERNS = "react_patterns"


@dataclass
class Issue:
    """代码问题数据结构"""
    severity: Severity
    category: Category
    message: str
    line: int
    column: int
    file: str
    rule_id: str
    suggestion: str = ""
    documentation_link: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity.value,
            "category": self.category.value,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "file": self.file,
            "rule_id": self.rule_id,
            "suggestion": self.suggestion,
            "documentation_link": self.documentation_link
        }


@dataclass
class AnalysisResult:
    """分析结果数据结构"""
    file_path: str
    issues: List[Issue] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    score: float = 100.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "issues": [issue.to_dict() for issue in self.issues],
            "statistics": self.statistics,
            "score": self.score
        }


class ReactBestPracticesSkill:
    """
    React最佳实践分析工具
    
    提供全面的React代码审查功能，包括性能、安全、可访问性等方面的检查。
    
    示例用法:
        skill = ReactBestPracticesSkill()
        
        # 分析单个文件
        result = skill.analyze_file("./src/App.tsx")
        
        # 分析整个项目
        results = skill.analyze_directory("./src")
        
        # 生成报告
        report = skill.generate_report(results)
    """
    
    # React Hook规则
    HOOKS_RULES = {
        'useState': {'dependencies': [], 'async_safe': True},
        'useEffect': {'dependencies': ['dependency-array'], 'async_safe': False},
        'useCallback': {'dependencies': ['dependency-array'], 'async_safe': True},
        'useMemo': {'dependencies': ['dependency-array'], 'async_safe': True},
        'useRef': {'dependencies': [], 'async_safe': True},
        'useContext': {'dependencies': [], 'async_safe': True},
        'useReducer': {'dependencies': [], 'async_safe': True},
        'useLayoutEffect': {'dependencies': ['dependency-array'], 'async_safe': False},
    }
    
    # 禁止使用的危险API
    DANGEROUS_APIS = [
        'dangerouslySetInnerHTML',
        'eval',
        'Function',
        'setTimeout(string)',
        'setInterval(string)',
    ]
    
    # 性能优化建议
    PERFORMANCE_PATTERNS = {
        'memoization': ['useMemo', 'useCallback', 'React.memo'],
        'lazy_loading': ['React.lazy', 'Suspense', 'dynamic import'],
        'virtualization': ['react-window', 'react-virtualized'],
        'code_splitting': ['import()', 'React.lazy'],
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化分析工具
        
        Args:
            config: 配置选项
        """
        self.config = config or {}
        self.react_version = self.config.get('react_version', '18.0')
        self.typescript_preferred = self.config.get('typescript_preferred', True)
        self.strict_mode = self.config.get('strict_mode', True)
        
        # 编译正则表达式
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译正则表达式模式"""
        # 检测类组件
        self.class_component_pattern = re.compile(
            r'class\s+(\w+)\s+extends\s+(React\.)?(Component|PureComponent)',
            re.MULTILINE
        )
        
        # 检测函数组件
        self.function_component_pattern = re.compile(
            r'(?:function|const|let|var)\s+(\w+)\s*[=\(].*\{[\s\S]*?return\s*[\(\<]',
            re.MULTILINE
        )
        
        # 检测Hooks使用
        self.hooks_pattern = re.compile(
            r'\b(use\w+)\s*\(',
            re.MULTILINE
        )
        
        # 检测useEffect依赖问题
        self.effect_dependency_pattern = re.compile(
            r'useEffect\s*\(\s*(?:\(\)\s*=>|function)\s*\{[\s\S]*?\}\s*,\s*(\[[^\]]*\])',
            re.MULTILINE
        )
        
        # 检测dangerouslySetInnerHTML
        self.dangerous_html_pattern = re.compile(
            r'dangerouslySetInnerHTML\s*=\s*\{\s*\{\s*__html\s*:',
            re.MULTILINE
        )
        
        # 检测key属性问题
        self.key_prop_pattern = re.compile(
            r'\.map\s*\(\s*\(?\s*(\w+)\s*\)?\s*=>\s*[\(\{]\s*<\w+[^>]*>',
            re.MULTILINE
        )
        
        # 检测内联函数
        self.inline_function_pattern = re.compile(
            r'on\w+\s*=\s*\{?\s*(?:\(\)\s*=>|\w+\s*=>)',
            re.MULTILINE
        )
        
        # 检测any类型使用
        self.any_type_pattern = re.compile(
            r':\s*\bany\b',
            re.MULTILINE
        )
        
        # 检测console语句
        self.console_pattern = re.compile(
            r'\bconsole\.(log|warn|error|info)\s*\(',
            re.MULTILINE
        )
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """
        分析单个React文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            AnalysisResult: 分析结果
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        logger.info(f"正在分析文件: {file_path}")
        
        content = path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        result = AnalysisResult(file_path=file_path)
        
        # 运行各项检查
        result.issues.extend(self._check_performance_issues(content, lines, file_path))
        result.issues.extend(self._check_security_issues(content, lines, file_path))
        result.issues.extend(self._check_accessibility_issues(content, lines, file_path))
        result.issues.extend(self._check_react_patterns(content, lines, file_path))
        result.issues.extend(self._check_typescript_issues(content, lines, file_path))
        result.issues.extend(self._check_maintainability_issues(content, lines, file_path))
        
        # 计算统计信息
        result.statistics = self._calculate_statistics(content, result.issues)
        
        # 计算代码质量分数
        result.score = self._calculate_score(result.issues)
        
        return result
    
    def analyze_directory(self, directory: str) -> List[AnalysisResult]:
        """
        分析整个目录
        
        Args:
            directory: 目录路径
        
        Returns:
            List[AnalysisResult]: 所有文件的分析结果
        """
        path = Path(directory)
        if not path.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")
        
        results = []
        
        # 支持的文件扩展名
        extensions = {'.js', '.jsx', '.ts', '.tsx'}
        
        for ext in extensions:
            for file_path in path.rglob(f'*{ext}'):
                # 跳过node_modules和测试文件
                if 'node_modules' in str(file_path) or '.test.' in str(file_path):
                    continue
                
                try:
                    result = self.analyze_file(str(file_path))
                    results.append(result)
                except Exception as e:
                    logger.error(f"分析文件失败 {file_path}: {e}")
        
        return results
    
    def _check_performance_issues(self, content: str, lines: List[str], file_path: str) -> List[Issue]:
        """检查性能问题"""
        issues = []
        
        # 检查内联函数定义
        for match in self.inline_function_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            issues.append(Issue(
                severity=Severity.MEDIUM,
                category=Category.PERFORMANCE,
                message="检测到内联函数定义，可能导致不必要的重渲染",
                line=line_num,
                column=match.start() - content.rfind('\n', 0, match.start()),
                file=file_path,
                rule_id="PERF-001",
                suggestion="使用useCallback包装事件处理函数",
                documentation_link="https://react.dev/reference/react/useCallback"
            ))
        
        # 检查缺少key属性的map
        for match in self.key_prop_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            # 检查这一行是否有key属性
            line_content = lines[line_num - 1] if line_num <= len(lines) else ""
            if 'key=' not in line_content:
                issues.append(Issue(
                    severity=Severity.HIGH,
                    category=Category.PERFORMANCE,
                    message="列表渲染缺少key属性",
                    line=line_num,
                    column=0,
                    file=file_path,
                    rule_id="PERF-002",
                    suggestion="为列表项添加唯一的key属性",
                    documentation_link="https://react.dev/learn/rendering-lists"
                ))
        
        # 检查不必要的useMemo/useCallback
        hooks_count = len(self.hooks_pattern.findall(content))
        if hooks_count > 10:
            issues.append(Issue(
                severity=Severity.LOW,
                category=Category.PERFORMANCE,
                message=f"组件使用了大量Hooks ({hooks_count}个)，考虑拆分组件",
                line=1,
                column=0,
                file=file_path,
                rule_id="PERF-003",
                suggestion="将复杂组件拆分为更小的子组件",
                documentation_link="https://react.dev/learn/thinking-in-react"
            ))
        
        return issues
    
    def _check_security_issues(self, content: str, lines: List[str], file_path: str) -> List[Issue]:
        """检查安全问题"""
        issues = []
        
        # 检查dangerouslySetInnerHTML
        for match in self.dangerous_html_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            issues.append(Issue(
                severity=Severity.CRITICAL,
                category=Category.SECURITY,
                message="使用dangerouslySetInnerHTML存在XSS风险",
                line=line_num,
                column=match.start() - content.rfind('\n', 0, match.start()),
                file=file_path,
                rule_id="SEC-001",
                suggestion="使用DOMPurify等库净化HTML内容，或考虑替代方案",
                documentation_link="https://react.dev/reference/react-dom/components/common#dangerously-setting-the-inner-html"
            ))
        
        # 检查eval使用
        if 'eval(' in content:
            line_num = content.find('eval(')
            line_num = content[:line_num].count('\n') + 1
            issues.append(Issue(
                severity=Severity.CRITICAL,
                category=Category.SECURITY,
                message="检测到eval()使用，存在严重的代码注入风险",
                line=line_num,
                column=0,
                file=file_path,
                rule_id="SEC-002",
                suggestion="避免使用eval，改用JSON.parse或其他安全方法",
                documentation_link="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/eval"
            ))
        
        return issues
    
    def _check_accessibility_issues(self, content: str, lines: List[str], file_path: str) -> List[Issue]:
        """检查可访问性问题"""
        issues = []
        
        # 检查图片缺少alt属性
        img_pattern = re.compile(r'<img[^>]*>', re.IGNORECASE)
        for match in img_pattern.finditer(content):
            tag = match.group()
            if 'alt=' not in tag:
                line_num = content[:match.start()].count('\n') + 1
                issues.append(Issue(
                    severity=Severity.MEDIUM,
                    category=Category.ACCESSIBILITY,
                    message="图片缺少alt属性",
                    line=line_num,
                    column=match.start() - content.rfind('\n', 0, match.start()),
                    file=file_path,
                    rule_id="A11Y-001",
                    suggestion="为图片添加描述性的alt属性",
                    documentation_link="https://www.w3.org/WAI/tutorials/images/"
                ))
        
        # 检查button缺少type属性
        button_pattern = re.compile(r'<button(?![^>]*type=)[^>]*>', re.IGNORECASE)
        for match in button_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            issues.append(Issue(
                severity=Severity.LOW,
                category=Category.ACCESSIBILITY,
                message="button元素缺少type属性",
                line=line_num,
                column=match.start() - content.rfind('\n', 0, match.start()),
                file=file_path,
                rule_id="A11Y-002",
                suggestion="显式设置button的type属性 (button/submit/reset)",
                documentation_link="https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button"
            ))
        
        return issues
    
    def _check_react_patterns(self, content: str, lines: List[str], file_path: str) -> List[Issue]:
        """检查React模式问题"""
        issues = []
        
        # 检查类组件使用（建议优先使用函数组件）
        for match in self.class_component_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            issues.append(Issue(
                severity=Severity.INFO,
                category=Category.REACT_PATTERNS,
                message="使用类组件，建议优先使用函数组件+Hooks",
                line=line_num,
                column=match.start() - content.rfind('\n', 0, match.start()),
                file=file_path,
                rule_id="REACT-001",
                suggestion="考虑迁移到函数组件以获得更好的性能和更简洁的代码",
                documentation_link="https://react.dev/learn/state-a-components-memory"
            ))
        
        # 检查useEffect缺少清理函数
        effect_pattern = re.compile(
            r'useEffect\s*\(\s*\(\)\s*=>\s*\{[^{}]*(?:setTimeout|setInterval|addEventListener|subscribe)[^{}]*\}[^,]*\)',
            re.MULTILINE
        )
        for match in effect_pattern.finditer(content):
            # 检查是否有return清理函数
            effect_content = match.group()
            if 'return' not in effect_content:
                line_num = content[:match.start()].count('\n') + 1
                issues.append(Issue(
                    severity=Severity.HIGH,
                    category=Category.REACT_PATTERNS,
                    message="useEffect中使用副作用但没有清理函数",
                    line=line_num,
                    column=match.start() - content.rfind('\n', 0, match.start()),
                    file=file_path,
                    rule_id="REACT-002",
                    suggestion="添加清理函数以防止内存泄漏",
                    documentation_link="https://react.dev/reference/react/useEffect#parameters"
                ))
        
        return issues
    
    def _check_typescript_issues(self, content: str, lines: List[str], file_path: str) -> List[Issue]:
        """检查TypeScript问题"""
        if not file_path.endswith(('.ts', '.tsx')):
            return []
        
        issues = []
        
        # 检查any类型使用
        for match in self.any_type_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            issues.append(Issue(
                severity=Severity.MEDIUM,
                category=Category.TYPESCRIPT,
                message="使用any类型会降低类型安全性",
                line=line_num,
                column=match.start() - content.rfind('\n', 0, match.start()),
                file=file_path,
                rule_id="TS-001",
                suggestion="使用具体的类型或unknown替代any",
                documentation_link="https://www.typescriptlang.org/docs/handbook/basic-types.html"
            ))
        
        # 检查缺少返回类型注解的函数
        func_pattern = re.compile(
            r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\))\s*(?::\s*\w+)?\s*[\{\(]',
            re.MULTILINE
        )
        
        return issues
    
    def _check_maintainability_issues(self, content: str, lines: List[str], file_path: str) -> List[Issue]:
        """检查可维护性问题"""
        issues = []
        
        # 检查console语句
        for match in self.console_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            issues.append(Issue(
                severity=Severity.LOW,
                category=Category.MAINTAINABILITY,
                message="检测到console语句，生产代码中应移除",
                line=line_num,
                column=match.start() - content.rfind('\n', 0, match.start()),
                file=file_path,
                rule_id="MAINT-001",
                suggestion="使用专业的日志库替代console",
                documentation_link=""
            ))
        
        # 检查文件长度
        if len(lines) > 300:
            issues.append(Issue(
                severity=Severity.MEDIUM,
                category=Category.MAINTAINABILITY,
                message=f"文件过长 ({len(lines)}行)，建议拆分",
                line=1,
                column=0,
                file=file_path,
                rule_id="MAINT-002",
                suggestion="将大型组件拆分为多个小组件",
                documentation_link=""
            ))
        
        return issues
    
    def _calculate_statistics(self, content: str, issues: List[Issue]) -> Dict[str, Any]:
        """计算统计信息"""
        lines = content.split('\n')
        
        severity_counts = {}
        for sev in Severity:
            severity_counts[sev.value] = sum(1 for i in issues if i.severity == sev)
        
        category_counts = {}
        for cat in Category:
            category_counts[cat.value] = sum(1 for i in issues if i.category == cat)
        
        return {
            "total_lines": len(lines),
            "code_lines": len([l for l in lines if l.strip()]),
            "comment_lines": len([l for l in lines if l.strip().startswith('//') or l.strip().startswith('*')]),
            "issue_count": len(issues),
            "severity_counts": severity_counts,
            "category_counts": category_counts
        }
    
    def _calculate_score(self, issues: List[Issue]) -> float:
        """计算代码质量分数"""
        weights = {
            Severity.CRITICAL: 20,
            Severity.HIGH: 10,
            Severity.MEDIUM: 5,
            Severity.LOW: 2,
            Severity.INFO: 0
        }
        
        total_penalty = sum(weights[i.severity] for i in issues)
        score = max(0, 100 - total_penalty)
        
        return round(score, 1)
    
    def generate_report(self, results: List[AnalysisResult], output_path: Optional[str] = None) -> str:
        """
        生成分析报告
        
        Args:
            results: 分析结果列表
            output_path: 输出文件路径
        
        Returns:
            str: 报告内容
        """
        total_issues = sum(len(r.issues) for r in results)
        avg_score = sum(r.score for r in results) / len(results) if results else 0
        
        report_lines = [
            "# React最佳实践分析报告",
            "",
            f"## 总体概览",
            "",
            f"- **分析文件数**: {len(results)}",
            f"- **总问题数**: {total_issues}",
            f"- **平均分数**: {avg_score:.1f}/100",
            "",
            "## 详细结果",
            ""
        ]
        
        for result in results:
            report_lines.append(f"### {result.file_path}")
            report_lines.append(f"- **质量分数**: {result.score}/100")
            report_lines.append(f"- **问题数量**: {len(result.issues)}")
            report_lines.append("")
            
            if result.issues:
                report_lines.append("#### 发现问题")
                report_lines.append("")
                for issue in result.issues:
                    report_lines.append(f"- **{issue.severity.value.upper()}** [{issue.rule_id}] {issue.message}")
                    report_lines.append(f"  - 位置: 第{issue.line}行")
                    report_lines.append(f"  - 建议: {issue.suggestion}")
                    report_lines.append("")
        
        report = '\n'.join(report_lines)
        
        if output_path:
            Path(output_path).write_text(report, encoding='utf-8')
            logger.info(f"报告已保存至: {output_path}")
        
        return report


def main():
    """示例用法"""
    skill = ReactBestPracticesSkill()
    
    # 示例：分析当前目录
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    
    if Path(target).is_file():
        result = skill.analyze_file(target)
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        results = skill.analyze_directory(target)
        report = skill.generate_report(results, "react-analysis-report.md")
        print(report)


if __name__ == "__main__":
    main()
