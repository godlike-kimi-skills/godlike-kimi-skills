#!/usr/bin/env python3
"""
Jest Skill 测试套件
"""

import unittest
import json
import os
import tempfile
from main import JestSkill, TestConfig, MockConfig, CoverageReport


class TestJestSkill(unittest.TestCase):
    """Jest Skill 测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.skill = JestSkill()
        self.config = TestConfig()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.skill.config)
        self.assertIsNotNone(self.skill.templates)
        self.assertIn("basic_test", self.skill.templates)
    
    def test_generate_test_basic_function(self):
        """测试生成基本函数测试"""
        source = """
function add(a, b) {
    return a + b;
}
"""
        test_code = self.skill.generate_test(source, test_type="unit")
        
        self.assertIn("describe('add'", test_code)
        self.assertIn("test('should handle basic case", test_code)
        self.assertIn("const result = add(", test_code)
    
    def test_generate_test_arrow_function(self):
        """测试生成箭头函数测试"""
        source = """
const multiply = (a, b) => a * b;
"""
        test_code = self.skill.generate_test(source, test_type="unit")
        
        self.assertIn("describe('multiply'", test_code)
    
    def test_generate_test_async_function(self):
        """测试生成异步函数测试"""
        source = """
async function fetchData(url) {
    const response = await fetch(url);
    return response.json();
}
"""
        test_code = self.skill.generate_test(source, test_type="unit")
        
        self.assertIn("async", test_code)
        self.assertIn("await", test_code)
    
    def test_generate_snapshot_test(self):
        """测试生成Snapshot测试"""
        source = """
function formatUser(user) {
    return { name: user.name, age: user.age };
}
"""
        test_code = self.skill.generate_test(source, test_type="snapshot")
        
        self.assertIn("toMatchSnapshot()", test_code)
        self.assertIn("Snapshots", test_code)
    
    def test_generate_mock(self):
        """测试生成Mock代码"""
        mock_code = self.skill.generate_mock(
            module_name="axios",
            methods=["get", "post"]
        )
        
        self.assertIn("jest.mock('axios'", mock_code)
        self.assertIn("get: jest.fn()", mock_code)
        self.assertIn("post: jest.fn()", mock_code)
    
    def test_generate_mock_with_return_values(self):
        """测试生成带返回值的Mock"""
        config = MockConfig(
            module_name="api",
            methods=["fetchData"],
            return_values={"fetchData": "{ data: [] }"}
        )
        mock_code = self.skill.generate_mock(
            module_name="api",
            methods=["fetchData"],
            config=config
        )
        
        self.assertIn("mockReturnValue", mock_code)
    
    def test_generate_spy(self):
        """测试生成Spy代码"""
        spy_code = self.skill.generate_spy("console", "log")
        
        self.assertIn("jest.spyOn", spy_code)
        self.assertIn("mockRestore", spy_code)
    
    def test_analyze_coverage_empty(self):
        """测试空覆盖率分析"""
        report = self.skill.analyze_coverage()
        
        self.assertEqual(report.total_statements, 0)
        self.assertEqual(report.statement_coverage, 100.0)
    
    def test_analyze_coverage_with_data(self):
        """测试覆盖率分析"""
        coverage_data = {
            "/src/utils.js": {
                "statementMap": {"0": {"start": {}}, "1": {"start": {}}},
                "s": {"0": 1, "1": 0},
                "branchMap": {"0": {"line": 1, "type": "if", "locations": [{}, {}]}},
                "b": {"0": [1, 0]},
                "fnMap": {"0": {"name": "add", "line": 1}},
                "f": {"0": 1}
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(coverage_data, f)
            temp_path = f.name
        
        try:
            report = self.skill.analyze_coverage(temp_path)
            
            self.assertEqual(report.total_statements, 2)
            self.assertEqual(report.covered_statements, 1)
            self.assertEqual(report.statement_coverage, 50.0)
        finally:
            os.unlink(temp_path)
    
    def test_coverage_report_properties(self):
        """测试覆盖率报告属性"""
        report = CoverageReport(
            total_statements=100,
            covered_statements=80,
            total_branches=50,
            covered_branches=40,
            total_functions=20,
            covered_functions=18,
            total_lines=100,
            covered_lines=80
        )
        
        self.assertEqual(report.statement_coverage, 80.0)
        self.assertEqual(report.branch_coverage, 80.0)
        self.assertEqual(report.function_coverage, 90.0)
        self.assertEqual(report.line_coverage, 80.0)
    
    def test_generate_coverage_config(self):
        """测试生成覆盖率配置"""
        config = self.skill.generate_coverage_config()
        
        self.assertIn("coverageThreshold", config)
        self.assertIn("collectCoverage", config)
        self.assertIn("coverageReporters", config)
    
    def test_optimize_tests(self):
        """测试测试优化"""
        test_code = """
describe('test', () => {
  beforeEach(() => {});
  beforeEach(() => {});
  
  test('test1', () => {});
  test('test2', () => {});
  
  test('long test', () => {
    // Line 1
    // Line 2
    // ... many lines
  });
});
"""
        optimized = self.skill.optimize_tests(test_code)
        
        # 应该包含优化建议
        self.assertIn("优化建议", optimized)
    
    def test_setup_test_environment(self):
        """测试设置测试环境"""
        files = self.skill.setup_test_environment("./test-project")
        
        self.assertIn("jest.config.js", files)
        self.assertIn("setupTests.js", files)
        self.assertIn("testUtils.js", files)
    
    def test_create_test_suite(self):
        """测试创建测试套件"""
        functions = [
            {"name": "add", "params": ["a", "b"]},
            {"name": "subtract", "params": ["a", "b"]}
        ]
        
        suite = self.skill.create_test_suite("math", functions)
        
        self.assertIn("import { add, subtract }", suite)
        self.assertIn("describe('add'", suite)
        self.assertIn("describe('subtract'", suite)
    
    def test_parse_function_with_params(self):
        """测试解析带参数的函数"""
        source = "function calculate(x, y, z) { return x + y + z; }"
        info = self.skill._parse_function(source)
        
        self.assertEqual(info["name"], "calculate")
        self.assertEqual(len(info["params"]), 3)
    
    def test_parse_function_without_params(self):
        """测试解析无参函数"""
        source = "function init() { console.log('init'); }"
        info = self.skill._parse_function(source)
        
        self.assertEqual(info["name"], "init")
        self.assertEqual(info["params"], [])
    
    def test_parse_async_function(self):
        """测试解析异步函数"""
        source = "async function loadData() { return await fetch(); }"
        info = self.skill._parse_function(source)
        
        self.assertTrue(info["is_async"])
    
    def test_config_dataclass(self):
        """测试配置数据类"""
        config = TestConfig(
            test_environment="node",
            coverage_threshold=90.0
        )
        
        self.assertEqual(config.test_environment, "node")
        self.assertEqual(config.coverage_threshold, 90.0)
        self.assertIsNotNone(config.test_match)
    
    def test_mock_config(self):
        """测试Mock配置"""
        config = MockConfig(
            module_name="test-module",
            methods=["method1", "method2"],
            return_values={"method1": "'value1'"}
        )
        
        self.assertEqual(config.module_name, "test-module")
        self.assertEqual(len(config.methods), 2)


class TestJestSkillIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        self.skill = JestSkill()
    
    def test_full_workflow(self):
        """测试完整工作流"""
        # 1. 生成测试
        source = """
export function divide(a, b) {
    if (b === 0) throw new Error('Division by zero');
    return a / b;
}
"""
        test_code = self.skill.generate_test(source, test_type="unit")
        self.assertIsNotNone(test_code)
        
        # 2. 生成mock
        mock_code = self.skill.generate_mock("api", ["fetchData"])
        self.assertIsNotNone(mock_code)
        
        # 3. 设置环境
        files = self.skill.setup_test_environment(".")
        self.assertEqual(len(files), 3)


def run_tests():
    """运行测试套件"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestJestSkill))
    suite.addTests(loader.loadTestsFromTestCase(TestJestSkillIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
