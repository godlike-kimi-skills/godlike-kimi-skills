#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDD Skill 基础测试
测试驱动开发Skill的自我测试
"""

import unittest
import sys
import os
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import TDDManager, TDD_WORKFLOW_GUIDE, TEST_FRAMEWORKS, TEST_TEMPLATES


class TestTDDManager(unittest.TestCase):
    """测试 TDDManager 类"""
    
    def setUp(self):
        """测试前准备"""
        self.tdd = TDDManager(language="python", test_framework="pytest")
    
    def tearDown(self):
        """测试后清理"""
        pass
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.tdd.language, "python")
        self.assertEqual(self.tdd.test_framework, "pytest")
    
    def test_show_workflow_guide(self):
        """测试工作流指导输出"""
        guide = self.tdd.show_workflow_guide("测试功能")
        self.assertIn("TDD", guide)
        self.assertIn("测试功能", guide)
        self.assertIn("红-绿-重构", guide)
    
    def test_generate_test_cases(self):
        """测试生成测试用例"""
        feature = "计算购物车总价"
        result = self.tdd.generate_test_cases(feature)
        self.assertIn(feature, result)
        self.assertIn("正常路径测试", result)
        self.assertIn("边界值测试", result)
        self.assertIn("异常情况测试", result)
    
    def test_generate_test_template(self):
        """测试生成测试模板"""
        output_dir = "./test_output"
        os.makedirs(output_dir, exist_ok=True)
        
        result_path = self.tdd.generate_test_template(
            class_name="Calculator",
            method_name="add",
            output_dir=output_dir
        )
        
        self.assertTrue(os.path.exists(result_path))
        self.assertIn("test_calculator.py", result_path)
        
        # 读取并验证内容
        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Calculator", content)
            self.assertIn("add", content)
        
        # 清理
        os.remove(result_path)
        os.rmdir(output_dir)
    
    def test_analyze_coverage(self):
        """测试覆盖率分析"""
        result = self.tdd.analyze_coverage(
            source_path="src/calc.py",
            test_path="tests/test_calc.py",
            threshold=80.0
        )
        
        self.assertEqual(result["source_path"], "src/calc.py")
        self.assertEqual(result["test_path"], "tests/test_calc.py")
        self.assertEqual(result["threshold"], 80.0)
        self.assertIn("details", result)
        self.assertIn("command", result)
    
    def test_red_green_refactor_guide(self):
        """测试红绿重构指导"""
        guide = self.tdd.red_green_refactor_guide()
        self.assertIn("Red", guide)
        self.assertIn("Green", guide)
        self.assertIn("Refactor", guide)
        self.assertIn("阶段一", guide)
        self.assertIn("阶段二", guide)
        self.assertIn("阶段三", guide)


class TestConstants(unittest.TestCase):
    """测试常量定义"""
    
    def test_tdd_workflow_guide(self):
        """测试工作流指导内容"""
        self.assertIn("TDD", TDD_WORKFLOW_GUIDE)
        self.assertIn("Red", TDD_WORKFLOW_GUIDE)
        self.assertIn("Green", TDD_WORKFLOW_GUIDE)
        self.assertIn("Refactor", TDD_WORKFLOW_GUIDE)
    
    def test_test_frameworks(self):
        """测试测试框架配置"""
        self.assertIn("python", TEST_FRAMEWORKS)
        self.assertIn("javascript", TEST_FRAMEWORKS)
        self.assertIn("java", TEST_FRAMEWORKS)
        
        # 验证 Python 配置
        self.assertIn("pytest", TEST_FRAMEWORKS["python"])
        self.assertIn("unittest", TEST_FRAMEWORKS["python"])
    
    def test_test_templates(self):
        """测试测试模板"""
        self.assertIn("python", TEST_TEMPLATES)
        self.assertIn("javascript", TEST_TEMPLATES)
        self.assertIn("java", TEST_TEMPLATES)
        
        # 验证 Python pytest 模板
        self.assertIn("pytest", TEST_TEMPLATES["python"])


class TestTDDManagerWithDifferentLanguages(unittest.TestCase):
    """测试不同语言和框架的组合"""
    
    def test_javascript_jest(self):
        """测试 JavaScript + Jest"""
        tdd = TDDManager(language="javascript", test_framework="jest")
        self.assertEqual(tdd.language, "javascript")
        self.assertEqual(tdd.test_framework, "jest")
        
        result = tdd.generate_test_cases("API请求")
        self.assertIn("API请求", result)
    
    def test_java_junit(self):
        """测试 Java + JUnit"""
        tdd = TDDManager(language="java", test_framework="junit")
        self.assertEqual(tdd.language, "java")
        self.assertEqual(tdd.test_framework, "junit")
    
    def test_typescript_jest(self):
        """测试 TypeScript + Jest"""
        tdd = TDDManager(language="typescript", test_framework="jest")
        self.assertEqual(tdd.language, "typescript")


class TestEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    def test_empty_feature(self):
        """测试空功能描述"""
        tdd = TDDManager()
        result = tdd.generate_test_cases("")
        self.assertIn("功能描述", result)
    
    def test_unsupported_combination(self):
        """测试不支持的框架组合"""
        tdd = TDDManager(language="python", test_framework="nonexistent")
        # 应该能正常工作，只是模板可能不可用
        guide = tdd.show_workflow_guide()
        self.assertIn("TDD", guide)


if __name__ == '__main__':
    unittest.main()
