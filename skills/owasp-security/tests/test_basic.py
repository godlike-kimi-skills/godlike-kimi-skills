#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OWASP Security Skill - 基础测试

测试内容：
- 枚举类型
- 安全规则
- 漏洞检测
- 报告生成

运行方式：
    python -m pytest tests/test_basic.py -v
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
import sys

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import (
    OWASPSecuritySkill,
    RiskLevel,
    OWASPCategory,
    SecurityFinding,
    ScanResult
)


class TestEnums:
    """测试枚举类型"""
    
    def test_risk_level_values(self):
        """测试风险等级枚举"""
        assert RiskLevel.CRITICAL.value == "critical"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.INFO.value == "info"
    
    def test_owasp_category_values(self):
        """测试OWASP分类枚举"""
        assert "Broken Access Control" in OWASPCategory.A01_BROKEN_ACCESS_CONTROL.value
        assert "Injection" in OWASPCategory.A03_INJECTION.value
        assert "Cryptographic" in OWASPCategory.A02_CRYPTO_FAILURES.value


class TestDataModels:
    """测试数据模型"""
    
    def test_security_finding_creation(self):
        """测试安全发现对象创建"""
        finding = SecurityFinding(
            rule_id="SEC-001",
            title="SQL注入",
            description="发现SQL注入漏洞",
            risk_level=RiskLevel.CRITICAL,
            owasp_category=OWASPCategory.A03_INJECTION,
            file_path="/app.js",
            line_number=10,
            column=5,
            code_snippet="query(`SELECT * FROM users WHERE id = ${id}`)",
            remediation="使用参数化查询",
            cwe_id="CWE-89",
            cvss_score=9.8
        )
        assert finding.rule_id == "SEC-001"
        assert finding.risk_level == RiskLevel.CRITICAL
        assert finding.to_dict()["risk_level"] == "critical"
    
    def test_scan_result_creation(self):
        """测试扫描结果创建"""
        result = ScanResult(
            target_path="./src",
            scan_time=datetime.now(),
            findings=[],
            summary={"total": 0}
        )
        assert result.target_path == "./src"
        assert isinstance(result.scan_time, datetime)


class TestSkillInitialization:
    """测试技能初始化"""
    
    def test_default_initialization(self):
        """测试默认初始化"""
        skill = OWASPSecuritySkill()
        assert skill.enable_auto_fix is False
        assert "node_modules" in skill.excluded_paths
    
    def test_custom_initialization(self):
        """测试自定义配置初始化"""
        config = {
            'auto_fix': True,
            'excluded_paths': ['vendor', 'cache']
        }
        skill = OWASPSecuritySkill(config)
        assert skill.enable_auto_fix is True
        assert 'vendor' in skill.excluded_paths


class TestRuleCompilation:
    """测试规则编译"""
    
    def test_rules_compiled(self):
        """测试规则是否正确编译"""
        skill = OWASPSecuritySkill()
        
        # 检查规则是否已编译
        assert len(skill.compiled_rules) > 0
        
        # 检查每个规则都有编译后的模式
        for rule_id, rule in skill.compiled_rules.items():
            assert "compiled_pattern" in rule


class TestSecurityDetection:
    """测试安全检测"""
    
    def test_sql_injection_detection(self):
        """测试SQL注入检测"""
        skill = OWASPSecuritySkill()
        
        code = "db.query(`SELECT * FROM users WHERE id = ${userId}`)"
        lines = code.split('\n')
        
        # 扫描文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            result = skill.scan_file(temp_path)
            
            # 应该检测到SQL注入
            sql_issues = [f for f in result.findings if 'SQL' in f.title]
            assert len(sql_issues) > 0
            assert sql_issues[0].risk_level == RiskLevel.CRITICAL
            assert sql_issues[0].cwe_id == "CWE-89"
        finally:
            Path(temp_path).unlink()
    
    def test_xss_detection(self):
        """测试XSS检测"""
        skill = OWASPSecuritySkill()
        
        code = "element.innerHTML = userInput"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            result = skill.scan_file(temp_path)
            
            # 应该检测到XSS
            xss_issues = [f for f in result.findings if 'XSS' in f.title]
            assert len(xss_issues) > 0
            assert xss_issues[0].risk_level == RiskLevel.HIGH
        finally:
            Path(temp_path).unlink()
    
    def test_weak_crypto_detection(self):
        """测试弱加密算法检测"""
        skill = OWASPSecuritySkill()
        
        code = "const hash = md5(password)"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            result = skill.scan_file(temp_path)
            
            # 应该检测到弱加密
            crypto_issues = [f for f in result.findings if '加密' in f.title or 'crypto' in f.title.lower()]
            assert len(crypto_issues) > 0
        finally:
            Path(temp_path).unlink()
    
    def test_hardcoded_secret_detection(self):
        """测试硬编码密钥检测"""
        skill = OWASPSecuritySkill()
        
        code = 'const apiKey = "sk-1234567890abcdef1234567890"'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            result = skill.scan_file(temp_path)
            
            # 应该检测到硬编码密钥
            secret_issues = [f for f in result.findings if '硬编码' in f.title or 'hardcoded' in f.title.lower()]
            assert len(secret_issues) > 0
            assert secret_issues[0].risk_level == RiskLevel.CRITICAL
        finally:
            Path(temp_path).unlink()
    
    def test_eval_detection(self):
        """测试eval检测"""
        skill = OWASPSecuritySkill()
        
        code = "eval(userInput)"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            result = skill.scan_file(temp_path)
            
            # 应该通过危险函数检测发现eval
            eval_issues = [f for f in result.findings if 'eval' in f.title or 'EVAL' in f.rule_id]
            assert len(eval_issues) > 0
        finally:
            Path(temp_path).unlink()


class TestSummaryGeneration:
    """测试摘要生成"""
    
    def test_empty_findings_summary(self):
        """测试空发现摘要"""
        skill = OWASPSecuritySkill()
        summary = skill._generate_summary([])
        
        assert summary['total_findings'] == 0
        assert summary['risk_score'] == 0.0
        assert summary['risk_rating'] == 'SAFE'
    
    def test_critical_findings_summary(self):
        """测试严重问题摘要"""
        skill = OWASPSecuritySkill()
        
        findings = [
            SecurityFinding(
                rule_id="TEST-001",
                title="Test",
                description="Test",
                risk_level=RiskLevel.CRITICAL,
                owasp_category=OWASPCategory.A03_INJECTION,
                file_path="test.js",
                line_number=1,
                column=0,
                code_snippet="test",
                remediation="fix"
            )
        ]
        
        summary = skill._generate_summary(findings)
        
        assert summary['total_findings'] == 1
        assert summary['severity_distribution']['critical'] == 1
        assert summary['risk_score'] > 0
        assert summary['risk_rating'] in ['HIGH', 'CRITICAL']


class TestRiskRating:
    """测试风险评级"""
    
    def test_risk_rating_safe(self):
        """测试安全评级"""
        skill = OWASPSecuritySkill()
        assert skill._get_risk_rating(0) == "SAFE"
    
    def test_risk_rating_low(self):
        """测试低风险评级"""
        skill = OWASPSecuritySkill()
        assert skill._get_risk_rating(10) == "LOW"
    
    def test_risk_rating_medium(self):
        """测试中风险评级"""
        skill = OWASPSecuritySkill()
        assert skill._get_risk_rating(30) == "MEDIUM"
    
    def test_risk_rating_high(self):
        """测试高风险评级"""
        skill = OWASPSecuritySkill()
        assert skill._get_risk_rating(60) == "HIGH"
    
    def test_risk_rating_critical(self):
        """测试严重风险评级"""
        skill = OWASPSecuritySkill()
        assert skill._get_risk_rating(90) == "CRITICAL"


class TestReportGeneration:
    """测试报告生成"""
    
    def test_html_report_generation(self):
        """测试HTML报告生成"""
        skill = OWASPSecuritySkill()
        
        result = ScanResult(
            target_path="./test",
            scan_time=datetime.now(),
            findings=[],
            summary={
                'total_findings': 0,
                'risk_score': 0.0,
                'risk_rating': 'SAFE',
                'severity_distribution': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0},
                'category_distribution': {}
            }
        )
        
        report = skill.generate_report(result, format="html")
        
        assert "<!DOCTYPE html>" in report
        assert "OWASP安全扫描报告" in report
    
    def test_markdown_report_generation(self):
        """测试Markdown报告生成"""
        skill = OWASPSecuritySkill()
        
        result = ScanResult(
            target_path="./test",
            scan_time=datetime.now(),
            findings=[],
            summary={
                'total_findings': 0,
                'risk_score': 0.0,
                'risk_rating': 'SAFE',
                'severity_distribution': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0},
                'category_distribution': {}
            }
        )
        
        report = skill.generate_report(result, format="md")
        
        assert "# OWASP安全扫描报告" in report
        assert "## 概览" in report
    
    def test_json_report_generation(self):
        """测试JSON报告生成"""
        skill = OWASPSecuritySkill()
        
        result = ScanResult(
            target_path="./test",
            scan_time=datetime.now(),
            findings=[],
            summary={'total_findings': 0}
        )
        
        report = skill.generate_report(result, format="json")
        
        import json
        data = json.loads(report)
        assert data['target_path'] == "./test"


# 示例漏洞代码用于测试
SAMPLE_VULNERABLE_CODE = """
// 硬编码密钥（严重）
const API_KEY = "sk-1234567890abcdef1234567890abcdef";

// SQL注入（严重）
app.get('/user', (req, res) => {
    const query = `SELECT * FROM users WHERE id = ${req.query.id}`;
    db.query(query);
});

// XSS（高危）
app.get('/search', (req, res) => {
    res.send(`<div>Results: ${req.query.q}</div>`);
});

// 弱加密（高危）
const passwordHash = md5(userPassword);

// 调试模式（中危）
const config = {
    debug: true
};

// 敏感信息日志（中危）
console.log('User password:', password);

// 正常代码
function safeFunction() {
    return "Hello World";
}
"""


class TestIntegration:
    """集成测试"""
    
    def test_scan_vulnerable_code(self):
        """测试扫描漏洞代码"""
        skill = OWASPSecuritySkill()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(SAMPLE_VULNERABLE_CODE)
            temp_path = f.name
        
        try:
            result = skill.scan_file(temp_path)
            
            # 验证检测到多种类型的问题
            assert len(result.findings) >= 5
            
            # 验证摘要信息
            assert result.summary['total_findings'] >= 5
            assert result.summary['risk_score'] > 0
            assert result.summary['risk_rating'] in ['HIGH', 'CRITICAL']
            
            # 验证严重程度分布
            severity_dist = result.summary['severity_distribution']
            assert severity_dist['critical'] >= 1
            assert severity_dist['high'] >= 1
            
        finally:
            Path(temp_path).unlink()
    
    def test_scan_directory(self):
        """测试目录扫描"""
        skill = OWASPSecuritySkill()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建多个测试文件
            for i in range(3):
                with open(f"{tmpdir}/test{i}.js", 'w') as f:
                    f.write(f"eval('test{i}')")  # 危险代码
            
            result = skill.scan_directory(tmpdir)
            
            assert result.summary['scanned_files'] == 3
            assert len(result.findings) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
