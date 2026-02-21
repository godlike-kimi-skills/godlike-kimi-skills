"""
Static Analysis Unit Tests
==========================

Comprehensive test suite for static-analysis skill.

Author: Godlike Kimi Skills
License: MIT
"""

import ast
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import (
    AnalysisConfig,
    AnalysisReport,
    ComplexityAnalyzer,
    ComplexityMetrics,
    FileMetrics,
    PythonFileCollector,
    ReportGenerator,
    SecurityIssue,
    SecurityScanner,
    StaticAnalyzer,
    StyleChecker,
    StyleIssue,
    generate_config_template,
)


class TestAnalysisConfig(unittest.TestCase):
    """分析配置类测试"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = AnalysisConfig()
        self.assertEqual(config.output_dir, "./analysis-results")
        self.assertEqual(config.min_complexity, 10)
        self.assertEqual(config.max_line_length, 100)
        self.assertFalse(config.strict_mode)
        self.assertEqual(config.format, "html")
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = AnalysisConfig(
            target="./src",
            min_complexity=5,
            max_line_length=80,
            strict_mode=True,
            format="json"
        )
        self.assertEqual(config.target, "./src")
        self.assertEqual(config.min_complexity, 5)
        self.assertEqual(config.max_line_length, 80)
        self.assertTrue(config.strict_mode)
        self.assertEqual(config.format, "json")
    
    def test_to_dict(self):
        """测试转换为字典"""
        config = AnalysisConfig(target="./src")
        config_dict = config.to_dict()
        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict['target'], "./src")
        self.assertEqual(config_dict['min_complexity'], 10)


class TestComplexityMetrics(unittest.TestCase):
    """复杂度指标类测试"""
    
    def test_metrics_creation(self):
        """测试创建复杂度指标"""
        metrics = ComplexityMetrics(
            file_path="test.py",
            function_name="test_func",
            line_number=10,
            cyclomatic_complexity=15,
            lines_of_code=20
        )
        self.assertEqual(metrics.file_path, "test.py")
        self.assertEqual(metrics.function_name, "test_func")
        self.assertEqual(metrics.line_number, 10)
        self.assertEqual(metrics.cyclomatic_complexity, 15)
        self.assertEqual(metrics.lines_of_code, 20)
    
    def test_to_dict(self):
        """测试转换为字典"""
        metrics = ComplexityMetrics(
            file_path="test.py",
            function_name="test_func",
            line_number=10,
            cyclomatic_complexity=15
        )
        metrics_dict = metrics.to_dict()
        self.assertIsInstance(metrics_dict, dict)
        self.assertEqual(metrics_dict['cyclomatic_complexity'], 15)


class TestSecurityIssue(unittest.TestCase):
    """安全问题类测试"""
    
    def test_issue_creation(self):
        """测试创建安全问题"""
        issue = SecurityIssue(
            file_path="test.py",
            line_number=5,
            issue_type="dangerous_function",
            severity="critical",
            message="Use of eval() is dangerous"
        )
        self.assertEqual(issue.severity, "critical")
        self.assertEqual(issue.issue_type, "dangerous_function")
    
    def test_severity_levels(self):
        """测试严重级别"""
        severities = ["critical", "high", "medium", "low"]
        for sev in severities:
            issue = SecurityIssue(
                file_path="test.py",
                line_number=1,
                issue_type="test",
                severity=sev,
                message="Test"
            )
            self.assertEqual(issue.severity, sev)


class TestStyleIssue(unittest.TestCase):
    """风格问题类测试"""
    
    def test_issue_creation(self):
        """测试创建风格问题"""
        issue = StyleIssue(
            file_path="test.py",
            line_number=10,
            column=50,
            code="E501",
            message="Line too long"
        )
        self.assertEqual(issue.code, "E501")
        self.assertEqual(issue.column, 50)
    
    def test_severity(self):
        """测试严重程度"""
        issue = StyleIssue(
            file_path="test.py",
            line_number=1,
            column=1,
            code="E101",
            message="Test",
            severity="error"
        )
        self.assertEqual(issue.severity, "error")


class TestFileMetrics(unittest.TestCase):
    """文件指标类测试"""
    
    def test_metrics_creation(self):
        """测试创建文件指标"""
        metrics = FileMetrics(
            file_path="test.py",
            lines_of_code=100,
            blank_lines=20,
            comment_lines=10,
            functions_count=5,
            classes_count=2,
            imports_count=3
        )
        self.assertEqual(metrics.lines_of_code, 100)
        self.assertEqual(metrics.functions_count, 5)
        self.assertEqual(metrics.classes_count, 2)
    
    def test_calculated_fields(self):
        """测试计算字段"""
        metrics = FileMetrics(
            file_path="test.py",
            lines_of_code=100,
            blank_lines=20,
            comment_lines=10,
            functions_count=5,
            classes_count=2,
            imports_count=3,
            average_complexity=8.5,
            maintainability_index=75.0
        )
        self.assertEqual(metrics.average_complexity, 8.5)
        self.assertEqual(metrics.maintainability_index, 75.0)


class TestPythonFileCollector(unittest.TestCase):
    """Python文件收集器测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.collector = PythonFileCollector(['__pycache__', '*.pyc'])
    
    def tearDown(self):
        """测试后置清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_should_exclude(self):
        """测试排除逻辑"""
        self.assertTrue(self.collector.should_exclude(Path('test/__pycache__/file.py')))
        self.assertTrue(self.collector.should_exclude(Path('test/file.pyc')))
        self.assertFalse(self.collector.should_exclude(Path('test/file.py')))
    
    def test_collect_single_file(self):
        """测试收集单个文件"""
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('hello')")
        
        files = self.collector.collect(str(test_file))
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0], test_file)
    
    def test_collect_directory(self):
        """测试收集目录"""
        # 创建测试文件
        (Path(self.temp_dir) / "file1.py").write_text("print('1')")
        (Path(self.temp_dir) / "file2.py").write_text("print('2')")
        (Path(self.temp_dir) / "not_python.txt").write_text("text")
        
        # 创建排除目录
        pycache = Path(self.temp_dir) / "__pycache__"
        pycache.mkdir()
        (pycache / "cached.pyc").write_text("")
        
        files = self.collector.collect(self.temp_dir)
        self.assertEqual(len(files), 2)
        self.assertTrue(all(f.suffix == '.py' for f in files))


class TestComplexityAnalyzer(unittest.TestCase):
    """复杂度分析器测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = ComplexityAnalyzer(min_complexity=5)
    
    def tearDown(self):
        """测试后置清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_simple_function(self):
        """测试简单函数"""
        test_file = Path(self.temp_dir) / "simple.py"
        test_file.write_text("""
def simple_func():
    return 42
""")
        
        issues = self.analyzer.analyze_file(test_file)
        # 简单函数复杂度为1，低于阈值，不应报告
        self.assertEqual(len(issues), 0)
    
    def test_complex_function(self):
        """测试复杂函数"""
        test_file = Path(self.temp_dir) / "complex.py"
        test_file.write_text("""
def complex_func(x):
    if x > 0:
        if x > 10:
            if x > 100:
                return "large"
            return "medium"
        return "small"
    elif x < 0:
        return "negative"
    else:
        return "zero"
""")
        
        issues = self.analyzer.analyze_file(test_file)
        # 应该检测到高复杂度函数
        self.assertGreater(len(issues), 0)
        self.assertGreater(issues[0].cyclomatic_complexity, 5)
    
    def test_calculate_cyclomatic_complexity(self):
        """测试圈复杂度计算"""
        code = """
def test(x):
    if x > 0:
        return 1
    return 0
"""
        tree = ast.parse(code)
        func = tree.body[0]
        complexity = self.analyzer._calculate_cyclomatic_complexity(func)
        # if语句增加1，基础为1，总共为2
        self.assertEqual(complexity, 2)


class TestSecurityScanner(unittest.TestCase):
    """安全扫描器测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.scanner = SecurityScanner()
    
    def tearDown(self):
        """测试后置清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_dangerous_eval(self):
        """测试eval检测"""
        test_file = Path(self.temp_dir) / "dangerous.py"
        test_file.write_text("""
result = eval(user_input)
""")
        
        issues = self.scanner.scan_file(test_file)
        self.assertGreater(len(issues), 0)
        self.assertTrue(any('eval' in i.issue_type for i in issues))
    
    def test_dangerous_exec(self):
        """测试exec检测"""
        test_file = Path(self.temp_dir) / "dangerous.py"
        test_file.write_text("""
exec(code_string)
""")
        
        issues = self.scanner.scan_file(test_file)
        self.assertGreater(len(issues), 0)
        self.assertTrue(any('exec' in i.issue_type for i in issues))
    
    def test_safe_code(self):
        """测试安全代码"""
        test_file = Path(self.temp_dir) / "safe.py"
        test_file.write_text("""
def safe_function():
    return 42
""")
        
        issues = self.scanner.scan_file(test_file)
        # 安全代码不应有问题
        self.assertEqual(len(issues), 0)


class TestStyleChecker(unittest.TestCase):
    """风格检查器测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.checker = StyleChecker(max_line_length=50)
    
    def tearDown(self):
        """测试后置清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_line_too_long(self):
        """测试行过长检测"""
        test_file = Path(self.temp_dir) / "long_lines.py"
        test_file.write_text("x = 'this is a very long line that exceeds the maximum allowed length'\n")
        
        issues = self.checker.check_file(test_file)
        self.assertGreater(len(issues), 0)
        self.assertTrue(any(i.code == 'E501' for i in issues))
    
    def test_trailing_whitespace(self):
        """测试尾随空格检测"""
        test_file = Path(self.temp_dir) / "whitespace.py"
        test_file.write_text("x = 1   \n")
        
        issues = self.checker.check_file(test_file)
        self.assertGreater(len(issues), 0)
        self.assertTrue(any(i.code == 'W291' for i in issues))
    
    def test_valid_code(self):
        """测试有效代码"""
        test_file = Path(self.temp_dir) / "valid.py"
        test_file.write_text("x = 1\ny = 2\n")
        
        issues = self.checker.check_file(test_file)
        # 有效代码不应有问题
        self.assertEqual(len(issues), 0)


class TestReportGenerator(unittest.TestCase):
    """报告生成器测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后置清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_html_report(self):
        """测试生成HTML报告"""
        report = AnalysisReport(
            timestamp="2026-02-21T10:00:00",
            target="./src",
            total_files=10,
            total_lines=1000,
            complexity_issues=[
                ComplexityMetrics("test.py", "func", 10, 15, 20)
            ],
            security_issues=[
                SecurityIssue("test.py", 5, "eval", "critical", "Dangerous")
            ],
            style_issues=[]
        )
        
        output_path = os.path.join(self.temp_dir, "report.html")
        result_path = ReportGenerator.generate_html_report(report, output_path)
        
        self.assertEqual(result_path, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Static Analysis Report", content)
            self.assertIn("test.py", content)
    
    def test_generate_json_report(self):
        """测试生成JSON报告"""
        report = AnalysisReport(
            timestamp="2026-02-21T10:00:00",
            target="./src",
            total_files=5,
            total_lines=500
        )
        
        output_path = os.path.join(self.temp_dir, "report.json")
        result_path = ReportGenerator.generate_json_report(report, output_path)
        
        self.assertEqual(result_path, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        import json
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(data['total_files'], 5)
            self.assertEqual(data['total_lines'], 500)
    
    def test_generate_markdown_report(self):
        """测试生成Markdown报告"""
        report = AnalysisReport(
            timestamp="2026-02-21T10:00:00",
            target="./src",
            total_files=3,
            total_lines=300
        )
        
        output_path = os.path.join(self.temp_dir, "report.md")
        result_path = ReportGenerator.generate_markdown_report(report, output_path)
        
        self.assertEqual(result_path, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("# Static Analysis Report", content)
            self.assertIn("./src", content)


class TestStaticAnalyzer(unittest.TestCase):
    """静态分析器集成测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后置清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_analyze_single_file(self):
        """测试分析单个文件"""
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("""
def simple_func():
    return 42

class MyClass:
    def method(self):
        return self
""")
        
        config = AnalysisConfig(target=str(test_file))
        analyzer = StaticAnalyzer(config)
        report = analyzer.analyze()
        
        self.assertEqual(report.total_files, 1)
        self.assertEqual(report.target, str(test_file))
        self.assertEqual(len(report.file_metrics), 1)
    
    def test_analyze_directory(self):
        """测试分析目录"""
        # 创建多个测试文件
        (Path(self.temp_dir) / "file1.py").write_text("def f1(): pass")
        (Path(self.temp_dir) / "file2.py").write_text("def f2(): pass")
        
        config = AnalysisConfig(target=self.temp_dir)
        analyzer = StaticAnalyzer(config)
        report = analyzer.analyze()
        
        self.assertEqual(report.total_files, 2)
        self.assertEqual(len(report.file_metrics), 2)


class TestConfigTemplate(unittest.TestCase):
    """配置文件模板测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后置清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_config_template(self):
        """测试生成配置模板"""
        output_path = os.path.join(self.temp_dir, "config.json")
        result_path = generate_config_template(output_path)
        
        self.assertEqual(result_path, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        import json
        with open(output_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.assertIn('target', config)
            self.assertIn('exclude_patterns', config)
            self.assertIn('min_complexity', config)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_end_to_end_workflow(self):
        """测试完整工作流程"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试文件
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text("""
def complex_function(x):
    if x > 0:
        if x > 10:
            return x * 2
    return 0

password = "secret123"  # Hardcoded secret
""")
            
            # 配置
            config = AnalysisConfig(
                target=str(test_file),
                min_complexity=5,
                output_dir=temp_dir
            )
            
            # 分析
            analyzer = StaticAnalyzer(config)
            report = analyzer.analyze()
            
            # 验证结果
            self.assertEqual(report.total_files, 1)
            
            # 生成报告
            html_path = os.path.join(temp_dir, "report.html")
            ReportGenerator.generate_html_report(report, html_path)
            self.assertTrue(os.path.exists(html_path))


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestAnalysisConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestComplexityMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityIssue))
    suite.addTests(loader.loadTestsFromTestCase(TestStyleIssue))
    suite.addTests(loader.loadTestsFromTestCase(TestFileMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestPythonFileCollector))
    suite.addTests(loader.loadTestsFromTestCase(TestComplexityAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityScanner))
    suite.addTests(loader.loadTestsFromTestCase(TestStyleChecker))
    suite.addTests(loader.loadTestsFromTestCase(TestReportGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestStaticAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigTemplate))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
