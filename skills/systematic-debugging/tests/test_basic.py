#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Systematic Debugging - 基础测试

测试核心功能的正确性和稳定性。
"""

import sys
import unittest
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import (
    SystematicDebugger,
    DebugAction,
    DebugStrategy,
    SeverityLevel,
    DebugResult,
    format_output,
)


class TestSystematicDebugger(unittest.TestCase):
    """测试系统化调试器"""
    
    def setUp(self):
        """测试前置设置"""
        self.debugger = SystematicDebugger("python")
    
    def test_init_valid_language(self):
        """测试使用有效语言初始化"""
        debugger = SystematicDebugger("python")
        self.assertEqual(debugger.language, "python")
        
        debugger = SystematicDebugger("javascript")
        self.assertEqual(debugger.language, "javascript")
    
    def test_init_invalid_language(self):
        """测试使用无效语言初始化"""
        with self.assertRaises(ValueError):
            SystematicDebugger("invalid_lang")
    
    def test_supported_languages(self):
        """测试支持的语言列表"""
        self.assertIn("python", SystematicDebugger.SUPPORTED_LANGUAGES)
        self.assertIn("javascript", SystematicDebugger.SUPPORTED_LANGUAGES)
        self.assertIn("java", SystematicDebugger.SUPPORTED_LANGUAGES)
        self.assertIn("cpp", SystematicDebugger.SUPPORTED_LANGUAGES)
    
    def test_analyze_error_none(self):
        """测试分析空错误"""
        result = self.debugger.analyze_error(None)
        self.assertEqual(result["error_type"], "Unknown")
        self.assertEqual(result["confidence"], 0.0)
    
    def test_analyze_error_empty(self):
        """测试分析空字符串错误"""
        result = self.debugger.analyze_error("")
        self.assertEqual(result["error_type"], "Unknown")
    
    def test_analyze_error_indexerror(self):
        """测试分析 IndexError"""
        error = "IndexError: list index out of range"
        result = self.debugger.analyze_error(error)
        self.assertEqual(result["error_type"], "IndexError")
        self.assertGreater(result["confidence"], 0)
        self.assertIn("索引", result["description"])
    
    def test_analyze_error_keyerror(self):
        """测试分析 KeyError"""
        error = "KeyError: 'user_id'"
        result = self.debugger.analyze_error(error)
        self.assertEqual(result["error_type"], "KeyError")
        self.assertGreater(result["confidence"], 0)
        self.assertIn("字典", result["description"])
    
    def test_analyze_error_attributeerror(self):
        """测试分析 AttributeError"""
        error = "AttributeError: 'NoneType' object has no attribute 'split'"
        result = self.debugger.analyze_error(error)
        self.assertEqual(result["error_type"], "AttributeError")
        self.assertGreater(result["confidence"], 0)
        self.assertIn("空值", result["description"])
    
    def test_analyze_error_typeerror(self):
        """测试分析 TypeError"""
        error = "TypeError: unsupported operand type(s)"
        result = self.debugger.analyze_error(error)
        self.assertEqual(result["error_type"], "TypeError")
    
    def test_analyze_error_valueerror(self):
        """测试分析 ValueError"""
        error = "ValueError: invalid literal for int()"
        result = self.debugger.analyze_error(error)
        self.assertEqual(result["error_type"], "ValueError")
    
    def test_analyze_error_zero(self):
        """测试分析 ZeroDivisionError"""
        error = "ZeroDivisionError: division by zero"
        result = self.debugger.analyze_error(error)
        self.assertEqual(result["error_type"], "ZeroDivisionError")
        self.assertEqual(result["severity"], "high")
    
    def test_analyze_error_with_context(self):
        """测试带上下文的错误分析"""
        error = "IndexError: list index out of range"
        context = "data = [1, 2, 3]\nvalue = data[10]"
        result = self.debugger.analyze_error(error, context)
        self.assertEqual(result["error_type"], "IndexError")
        self.assertIn("context_hints", result)
    
    def test_analyze_context_long_code(self):
        """测试长代码上下文分析"""
        context = "if x:\n" * 60  # 长代码
        result = self.debugger.analyze_error("Error", context)
        self.assertIn("context_hints", result)
        self.assertTrue(len(result["context_hints"]) > 0)
    
    def test_recommend_strategy(self):
        """测试策略推荐"""
        error_analysis = {
            "error_type": "IndexError",
            "severity": "high",
        }
        result = self.debugger.recommend_strategy(error_analysis)
        self.assertIn("recommended_strategy", result)
        self.assertIn("steps", result)
        self.assertIn("name", result)
        self.assertIn("description", result)
        self.assertIn("best_for", result)
    
    def test_recommend_strategy_with_preference(self):
        """测试带偏好的策略推荐"""
        error_analysis = {"error_type": "TestError"}
        result = self.debugger.recommend_strategy(error_analysis, "binary_search")
        self.assertEqual(result["recommended_strategy"], "binary_search")
    
    def test_recommend_strategy_deductive(self):
        """测试演绎推理策略推荐"""
        error_analysis = {"error_type": "TestError"}
        result = self.debugger.recommend_strategy(error_analysis, "deductive")
        self.assertEqual(result["name"], "演绎推理")
    
    def test_select_best_strategy_critical(self):
        """测试严重错误的策略选择"""
        error_analysis = {"severity": "critical"}
        strategy = self.debugger._select_best_strategy(error_analysis)
        self.assertEqual(strategy, DebugStrategy.BACKWARD)
    
    def test_select_best_strategy_null_error(self):
        """测试空值错误的策略选择"""
        error_analysis = {"error_type": "AttributeError", "severity": "high"}
        strategy = self.debugger._select_best_strategy(error_analysis)
        self.assertEqual(strategy, DebugStrategy.BACKWARD)
    
    def test_select_best_strategy_index(self):
        """测试索引错误的策略选择"""
        error_analysis = {"error_type": "IndexError", "severity": "high"}
        strategy = self.debugger._select_best_strategy(error_analysis)
        self.assertEqual(strategy, DebugStrategy.FORWARD)
    
    def test_select_best_strategy_unknown(self):
        """测试未知错误的策略选择"""
        error_analysis = {"error_type": "Unknown", "severity": "medium"}
        strategy = self.debugger._select_best_strategy(error_analysis)
        self.assertEqual(strategy, DebugStrategy.DIVIDE_CONQUER)
    
    def test_root_cause_analysis(self):
        """测试根因分析"""
        error = "IndexError: list index out of range"
        result = self.debugger.root_cause_analysis(error)
        self.assertEqual(result["method"], "5 Whys")
        self.assertIn("analysis", result)
        self.assertIn("root_cause", result)
        self.assertIn("recommendations", result)
        self.assertTrue(len(result["analysis"]) > 0)
    
    def test_root_cause_analysis_with_context(self):
        """测试带上下文的根因分析"""
        error = "NullPointerException"
        context = "user.getProfile().getName()"
        stack = "at Line 10"
        result = self.debugger.root_cause_analysis(error, context, stack)
        self.assertEqual(result["method"], "5 Whys")
    
    def test_suggest_fix_indexerror(self):
        """测试 IndexError 修复建议"""
        error_analysis = {"error_type": "IndexError"}
        suggestions = self.debugger.suggest_fix(error_analysis)
        self.assertTrue(len(suggestions) > 0)
        self.assertIn("title", suggestions[0])
        self.assertIn("code", suggestions[0])
        self.assertIn("priority", suggestions[0])
    
    def test_suggest_fix_keyerror(self):
        """测试 KeyError 修复建议"""
        error_analysis = {"error_type": "KeyError"}
        suggestions = self.debugger.suggest_fix(error_analysis)
        self.assertTrue(len(suggestions) > 0)
        self.assertIn("使用get方法", suggestions[0]["title"])
    
    def test_suggest_fix_attribute(self):
        """测试 AttributeError 修复建议"""
        error_analysis = {"error_type": "AttributeError"}
        suggestions = self.debugger.suggest_fix(error_analysis)
        self.assertTrue(len(suggestions) > 0)
    
    def test_suggest_fix_unknown(self):
        """测试未知错误的修复建议"""
        error_analysis = {"error_type": "UnknownError"}
        suggestions = self.debugger.suggest_fix(error_analysis)
        self.assertTrue(len(suggestions) > 0)
        self.assertIn("title", suggestions[0])
    
    def test_full_diagnosis(self):
        """测试完整诊断"""
        error = "ZeroDivisionError: division by zero"
        context = "result = 10 / 0"
        result = self.debugger.full_diagnosis(error, context)
        
        self.assertIsInstance(result, DebugResult)
        self.assertEqual(result.action, "full_diagnosis")
        self.assertEqual(result.language, "python")
        self.assertEqual(result.error, error)
        self.assertIsNotNone(result.analysis)
        self.assertIsNotNone(result.strategy)
        self.assertIsNotNone(result.root_cause)
        self.assertIsNotNone(result.fix_suggestions)
        self.assertIsNotNone(result.timestamp)
    
    def test_full_diagnosis_minimal(self):
        """测试最小参数的完整诊断"""
        result = self.debugger.full_diagnosis(None)
        self.assertEqual(result.error, None)
        self.assertEqual(result.analysis["error_type"], "Unknown")


class TestJavaScriptDebugger(unittest.TestCase):
    """测试 JavaScript 调试器"""
    
    def setUp(self):
        self.debugger = SystematicDebugger("javascript")
    
    def test_analyze_js_undefined_error(self):
        """测试 JS undefined 错误分析"""
        error = "Cannot read property 'name' of undefined"
        result = self.debugger.analyze_error(error)
        self.assertEqual(result["error_type"], "TypeError")
        self.assertGreater(result["confidence"], 0)
    
    def test_analyze_js_not_function(self):
        """测试 JS 非函数错误"""
        error = "x is not a function"
        result = self.debugger.analyze_error(error)
        self.assertEqual(result["error_type"], "TypeError")
    
    def test_analyze_js_promise(self):
        """测试 JS Promise 错误"""
        error = "Unhandled Promise rejection"
        result = self.debugger.analyze_error(error)
        self.assertEqual(result["error_type"], "PromiseError")


class TestJavaDebugger(unittest.TestCase):
    """测试 Java 调试器"""
    
    def setUp(self):
        self.debugger = SystematicDebugger("java")
    
    def test_analyze_java_npe(self):
        """测试 Java 空指针异常"""
        error = "NullPointerException"
        result = self.debugger.analyze_error(error)
        self.assertEqual(result["error_type"], "NullPointerException")
        self.assertGreater(result["confidence"], 0)
    
    def test_analyze_java_array_bounds(self):
        """测试 Java 数组越界"""
        error = "ArrayIndexOutOfBoundsException"
        result = self.debugger.analyze_error(error)
        self.assertEqual(result["error_type"], "ArrayIndexOutOfBoundsException")
    
    def test_analyze_java_class_not_found(self):
        """测试 Java 类未找到"""
        error = "ClassNotFoundException"
        result = self.debugger.analyze_error(error)
        self.assertEqual(result["error_type"], "ClassNotFoundException")
        self.assertEqual(result["severity"], "critical")


class TestCppDebugger(unittest.TestCase):
    """测试 C++ 调试器"""
    
    def setUp(self):
        self.debugger = SystematicDebugger("cpp")
    
    def test_analyze_cpp_seg_fault(self):
        """测试 C++ 段错误"""
        error = "segmentation fault"
        result = self.debugger.analyze_error(error)
        self.assertEqual(result["error_type"], "SegmentationFault")
        self.assertEqual(result["severity"], "critical")


class TestFormatOutput(unittest.TestCase):
    """测试输出格式化"""
    
    def setUp(self):
        self.result = DebugResult(
            action="test",
            language="python",
            error="TestError",
            analysis={"error_type": "Test", "description": "Test desc", 
                     "severity": "medium", "confidence": 0.85},
        )
    
    def test_format_json(self):
        """测试 JSON 格式输出"""
        output = format_output(self.result, "json")
        self.assertIn("action", output)
        self.assertIn("language", output)
        import json
        data = json.loads(output)
        self.assertEqual(data["action"], "test")
        self.assertEqual(data["language"], "python")
    
    def test_format_markdown(self):
        """测试 Markdown 格式输出"""
        output = format_output(self.result, "markdown")
        self.assertIn("# 系统化调试报告", output)
        self.assertIn("## 错误分析", output)
        self.assertIn("TestError", output)
        self.assertIn("python", output)
    
    def test_format_text(self):
        """测试文本格式输出"""
        output = format_output(self.result, "text")
        self.assertIn("DebugResult", output)
    
    def test_format_markdown_full(self):
        """测试完整的 Markdown 格式输出"""
        result = DebugResult(
            action="full_diagnosis",
            language="python",
            error="TestError",
            analysis={"error_type": "Test", "description": "Test desc",
                     "severity": "high", "confidence": 0.9,
                     "common_causes": ["原因1", "原因2"]},
            strategy={"name": "测试策略", "description": "测试描述",
                     "steps": ["步骤1", "步骤2"]},
            root_cause={"method": "5 Whys", "root_cause": "根本原因",
                       "analysis": [{"level": 1, "question": "Q", "answer": "A"}]},
            fix_suggestions=[{"title": "建议1", "priority": "high",
                            "description": "描述", "code": "code"}],
        )
        output = format_output(result, "markdown")
        self.assertIn("# 系统化调试报告", output)
        self.assertIn("## 推荐调试策略", output)
        self.assertIn("## 根因分析", output)
        self.assertIn("## 修复建议", output)


class TestDebugStrategies(unittest.TestCase):
    """测试调试策略定义"""
    
    def test_all_strategies_defined(self):
        """测试所有策略都有定义"""
        debugger = SystematicDebugger("python")
        for strategy in DebugStrategy:
            self.assertIn(strategy, debugger.STRATEGIES)
    
    def test_strategy_structure(self):
        """测试策略结构完整性"""
        debugger = SystematicDebugger("python")
        for strategy_name, strategy_info in debugger.STRATEGIES.items():
            self.assertIn("name", strategy_info)
            self.assertIn("description", strategy_info)
            self.assertIn("steps", strategy_info)
            self.assertIn("best_for", strategy_info)
            self.assertIsInstance(strategy_info["steps"], list)
            self.assertIsInstance(strategy_info["best_for"], list)
    
    def test_strategy_binary_search(self):
        """测试二分查找策略"""
        debugger = SystematicDebugger("python")
        info = debugger.STRATEGIES[DebugStrategy.BINARY_SEARCH]
        self.assertEqual(info["name"], "二分查找法")
        self.assertTrue(len(info["steps"]) >= 4)
    
    def test_strategy_backward(self):
        """测试反向追踪策略"""
        debugger = SystematicDebugger("python")
        info = debugger.STRATEGIES[DebugStrategy.BACKWARD]
        self.assertEqual(info["name"], "反向追踪")


class TestEnumValues(unittest.TestCase):
    """测试枚举值"""
    
    def test_debug_action_values(self):
        """测试 DebugAction 枚举值"""
        self.assertEqual(DebugAction.ANALYZE.value, "analyze")
        self.assertEqual(DebugAction.STRATEGY.value, "strategy")
        self.assertEqual(DebugAction.ROOT_CAUSE.value, "root_cause")
        self.assertEqual(DebugAction.SUGGEST_FIX.value, "suggest_fix")
        self.assertEqual(DebugAction.FULL_DIAGNOSIS.value, "full_diagnosis")
    
    def test_debug_strategy_values(self):
        """测试 DebugStrategy 枚举值"""
        self.assertEqual(DebugStrategy.BINARY_SEARCH.value, "binary_search")
        self.assertEqual(DebugStrategy.FORWARD.value, "forward")
        self.assertEqual(DebugStrategy.BACKWARD.value, "backward")
        self.assertEqual(DebugStrategy.DEDUCTIVE.value, "deductive")
        self.assertEqual(DebugStrategy.INDUCTIVE.value, "inductive")
        self.assertEqual(DebugStrategy.DIVIDE_CONQUER.value, "divide_conquer")
    
    def test_severity_level_values(self):
        """测试 SeverityLevel 枚举值"""
        self.assertEqual(SeverityLevel.CRITICAL.value, "critical")
        self.assertEqual(SeverityLevel.HIGH.value, "high")
        self.assertEqual(SeverityLevel.MEDIUM.value, "medium")
        self.assertEqual(SeverityLevel.LOW.value, "low")


class TestErrorPatterns(unittest.TestCase):
    """测试错误模式库"""
    
    def test_python_patterns_exist(self):
        """测试 Python 错误模式存在"""
        debugger = SystematicDebugger("python")
        self.assertIn("python", debugger.ERROR_PATTERNS)
        self.assertTrue(len(debugger.ERROR_PATTERNS["python"]) > 0)
    
    def test_javascript_patterns_exist(self):
        """测试 JavaScript 错误模式存在"""
        debugger = SystematicDebugger("javascript")
        self.assertIn("javascript", debugger.ERROR_PATTERNS)
    
    def test_java_patterns_exist(self):
        """测试 Java 错误模式存在"""
        debugger = SystematicDebugger("java")
        self.assertIn("java", debugger.ERROR_PATTERNS)
    
    def test_pattern_structure(self):
        """测试错误模式结构"""
        debugger = SystematicDebugger("python")
        pattern = debugger.ERROR_PATTERNS["python"][0]
        # pattern 是元组 (pattern, error_type, description, causes, severity, fixes)
        self.assertEqual(len(pattern), 6)
        self.assertIsInstance(pattern[0], str)  # regex pattern
        self.assertIsInstance(pattern[1], str)  # error_type
        self.assertIsInstance(pattern[2], str)  # description
        self.assertIsInstance(pattern[3], list)  # causes
        self.assertIsInstance(pattern[4], str)  # severity
        self.assertIsInstance(pattern[5], list)  # fixes


class TestCommandLine(unittest.TestCase):
    """测试命令行接口"""
    
    def test_import_main(self):
        """测试 main 模块可导入"""
        import main as main_module
        self.assertTrue(hasattr(main_module, 'main'))
        self.assertTrue(hasattr(main_module, 'SystematicDebugger'))
    
    def test_debug_result_dataclass(self):
        """测试 DebugResult 数据类"""
        result = DebugResult(action="test", language="python", error="err")
        self.assertEqual(result.action, "test")
        self.assertEqual(result.language, "python")
        self.assertEqual(result.error, "err")
        self.assertIsInstance(result.timestamp, str)


if __name__ == "__main__":
    unittest.main(verbosity=2)
