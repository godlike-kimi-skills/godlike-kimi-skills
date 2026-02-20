#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
React Best Practices Skill - 基础测试

测试内容：
- 枚举类型
- 配置和数据模型
- 规则匹配
- 分析功能

运行方式：
    python -m pytest tests/test_basic.py -v
"""

import pytest
import tempfile
from pathlib import Path
import sys

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import (
    ReactBestPracticesSkill,
    Severity,
    Category,
    Issue,
    AnalysisResult
)


class TestEnums:
    """测试枚举类型"""
    
    def test_severity_values(self):
        """测试严重程度枚举"""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"
        assert Severity.INFO.value == "info"
    
    def test_category_values(self):
        """测试分类枚举"""
        assert Category.PERFORMANCE.value == "performance"
        assert Category.SECURITY.value == "security"
        assert Category.ACCESSIBILITY.value == "accessibility"


class TestDataModels:
    """测试数据模型"""
    
    def test_issue_creation(self):
        """测试问题对象创建"""
        issue = Issue(
            severity=Severity.HIGH,
            category=Category.SECURITY,
            message="发现安全问题",
            line=10,
            column=5,
            file="test.tsx",
            rule_id="SEC-001",
            suggestion="修复建议",
            documentation_link="https://example.com"
        )
        assert issue.severity == Severity.HIGH
        assert issue.line == 10
        assert issue.to_dict()["severity"] == "high"
    
    def test_analysis_result_creation(self):
        """测试分析结果创建"""
        result = AnalysisResult(
            file_path="./test.tsx",
            issues=[],
            score=95.0
        )
        assert result.file_path == "./test.tsx"
        assert result.score == 95.0


class TestSkillInitialization:
    """测试技能初始化"""
    
    def test_default_initialization(self):
        """测试默认初始化"""
        skill = ReactBestPracticesSkill()
        assert skill.react_version == "18.0"
        assert skill.typescript_preferred is True
        assert skill.strict_mode is True
    
    def test_custom_initialization(self):
        """测试自定义配置初始化"""
        config = {
            'react_version': '17.0',
            'typescript_preferred': False,
            'strict_mode': False
        }
        skill = ReactBestPracticesSkill(config)
        assert skill.react_version == "17.0"
        assert skill.typescript_preferred is False
        assert skill.strict_mode is False


class TestPatternMatching:
    """测试模式匹配"""
    
    def test_class_component_pattern(self):
        """测试类组件模式匹配"""
        skill = ReactBestPracticesSkill()
        
        code = "class MyComponent extends Component {"
        match = skill.class_component_pattern.search(code)
        assert match is not None
        assert match.group(1) == "MyComponent"
        
        code = "class App extends React.Component {"
        match = skill.class_component_pattern.search(code)
        assert match is not None
        assert match.group(1) == "App"
    
    def test_hooks_pattern(self):
        """测试Hooks模式匹配"""
        skill = ReactBestPracticesSkill()
        
        code = "const [state, setState] = useState(0)"
        matches = skill.hooks_pattern.findall(code)
        assert "useState" in matches
    
    def test_dangerous_html_pattern(self):
        """测试危险HTML模式"""
        skill = ReactBestPracticesSkill()
        
        code = 'element.innerHTML = {__html: content}'
        match = skill.dangerous_html_pattern.search(code)
        assert match is not None
    
    def test_console_pattern(self):
        """测试console模式"""
        skill = ReactBestPracticesSkill()
        
        code = "console.log('debug message')"
        match = skill.console_pattern.search(code)
        assert match is not None
    
    def test_any_type_pattern(self):
        """测试any类型模式"""
        skill = ReactBestPracticesSkill()
        
        code = "const data: any = {}"
        match = skill.any_type_pattern.search(code)
        assert match is not None


class TestAnalysisFunctions:
    """测试分析功能"""
    
    def test_security_issues_detection(self):
        """测试安全问题检测"""
        skill = ReactBestPracticesSkill()
        
        code = "eval(userInput)"
        lines = code.split('\n')
        issues = skill._check_security_issues(code, lines, "test.js")
        
        # 应该检测到eval使用
        eval_issues = [i for i in issues if 'eval' in i.message]
        assert len(eval_issues) > 0
        assert eval_issues[0].severity == Severity.CRITICAL
    
    def test_maintainability_issues_detection(self):
        """测试可维护性问题检测"""
        skill = ReactBestPracticesSkill()
        
        code = "console.log('debug')"
        lines = code.split('\n')
        issues = skill._check_maintainability_issues(code, lines, "test.js")
        
        assert len(issues) > 0
        assert issues[0].category == Category.MAINTAINABILITY
    
    def test_score_calculation(self):
        """测试分数计算"""
        skill = ReactBestPracticesSkill()
        
        # 无问题，满分
        score = skill._calculate_score([])
        assert score == 100.0
        
        # 严重问题扣20分
        issues = [
            Issue(
                severity=Severity.CRITICAL,
                category=Category.SECURITY,
                message="Critical issue",
                line=1, column=0, file="test.js", rule_id="TEST-001"
            )
        ]
        score = skill._calculate_score(issues)
        assert score == 80.0


class TestFileAnalysis:
    """测试文件分析"""
    
    def test_analyze_nonexistent_file(self):
        """测试分析不存在的文件"""
        skill = ReactBestPracticesSkill()
        
        with pytest.raises(FileNotFoundError):
            skill.analyze_file("/nonexistent/file.tsx")
    
    def test_analyze_sample_file(self):
        """测试分析示例文件"""
        skill = ReactBestPracticesSkill()
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.tsx',
            delete=False
        ) as f:
            f.write("""
import React from 'react';

// 使用console（可维护性问题）
console.log('debug');

// 使用any类型（TypeScript问题）
const data: any = {};

// 类组件（模式建议）
class MyComponent extends React.Component {
    render() {
        return <div>Hello</div>;
    }
}

export default MyComponent;
""")
            temp_path = f.name
        
        try:
            result = skill.analyze_file(temp_path)
            
            assert result.file_path == temp_path
            assert isinstance(result.score, float)
            assert isinstance(result.issues, list)
            assert isinstance(result.statistics, dict)
            
            # 应该检测到问题
            assert len(result.issues) > 0
            
        finally:
            Path(temp_path).unlink()


class TestReportGeneration:
    """测试报告生成"""
    
    def test_generate_report(self):
        """测试报告生成"""
        skill = ReactBestPracticesSkill()
        
        result = AnalysisResult(
            file_path="test.tsx",
            issues=[],
            score=95.0
        )
        
        report = skill.generate_report([result])
        
        assert "React最佳实践分析报告" in report
        assert "test.tsx" in report
        assert "95.0" in report or "95" in report


# 示例React代码用于测试
SAMPLE_REACT_CODE = """
import React, { useState, useEffect } from 'react';

// 性能问题：内联函数
function App() {
    const [count, setCount] = useState(0);
    
    // 安全问题：console语句
    console.log('render');
    
    // TypeScript问题：使用any
    const data: any = { value: 123 };
    
    return (
        <div>
            {/* 可访问性问题：图片缺少alt */}
            <img src="logo.png" />
            
            {/* 性能问题：内联函数 */}
            <button onClick={() => setCount(c => c + 1)}>
                Count: {count}
            </button>
            
            {/* 性能问题：缺少key */}
            {[1, 2, 3].map(n => <span>{n}</span>)}
        </div>
    );
}

export default App;
"""


class TestIntegration:
    """集成测试"""
    
    def test_analyze_sample_code(self):
        """测试分析示例代码"""
        skill = ReactBestPracticesSkill()
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.tsx',
            delete=False
        ) as f:
            f.write(SAMPLE_REACT_CODE)
            temp_path = f.name
        
        try:
            result = skill.analyze_file(temp_path)
            
            # 验证检测到不同类型的问题
            categories = set(issue.category for issue in result.issues)
            
            # 应该检测到性能、安全和可维护性问题
            assert len(categories) >= 2
            
            # 分数应该低于100
            assert result.score < 100
            
        finally:
            Path(temp_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
