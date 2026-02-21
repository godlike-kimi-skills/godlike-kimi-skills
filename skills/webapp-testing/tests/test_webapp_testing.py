"""
Webapp Testing Unit Tests
=========================

Comprehensive test suite for webapp-testing skill.

Author: Godlike Kimi Skills
License: MIT
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from PIL import Image

from main import (
    PerformanceMetrics,
    ScreenshotComparisonResult,
    TestConfig,
    TestReporter,
    VisualComparator,
    generate_config_template,
)


class TestTestConfig(unittest.TestCase):
    """测试配置类测试"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = TestConfig()
        self.assertEqual(config.browser, "chromium")
        self.assertTrue(config.headless)
        self.assertEqual(config.viewport_width, 1920)
        self.assertEqual(config.viewport_height, 1080)
        self.assertEqual(config.timeout, 30000)
        self.assertEqual(config.threshold, 0.1)
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = TestConfig(
            url="https://example.com",
            browser="firefox",
            headless=False,
            viewport_width=1280,
            viewport_height=720,
            threshold=0.05
        )
        self.assertEqual(config.url, "https://example.com")
        self.assertEqual(config.browser, "firefox")
        self.assertFalse(config.headless)
        self.assertEqual(config.viewport_width, 1280)
        self.assertEqual(config.viewport_height, 720)
        self.assertEqual(config.threshold, 0.05)
    
    def test_to_dict(self):
        """测试转换为字典"""
        config = TestConfig(url="https://example.com")
        config_dict = config.to_dict()
        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict['url'], "https://example.com")
        self.assertEqual(config_dict['browser'], "chromium")


class TestPerformanceMetrics(unittest.TestCase):
    """性能指标类测试"""
    
    def test_default_metrics(self):
        """测试默认性能指标"""
        metrics = PerformanceMetrics(
            url="https://example.com",
            timestamp="2026-02-21T10:00:00",
            load_time_ms=1000.0,
            dom_content_loaded_ms=500.0
        )
        self.assertEqual(metrics.url, "https://example.com")
        self.assertEqual(metrics.load_time_ms, 1000.0)
        self.assertEqual(metrics.dom_content_loaded_ms, 500.0)
        self.assertIsNone(metrics.first_paint_ms)
    
    def test_full_metrics(self):
        """测试完整性能指标"""
        metrics = PerformanceMetrics(
            url="https://example.com",
            timestamp="2026-02-21T10:00:00",
            load_time_ms=1200.0,
            dom_content_loaded_ms=600.0,
            first_paint_ms=400.0,
            first_contentful_paint_ms=550.0,
            largest_contentful_paint_ms=1100.0,
            time_to_interactive_ms=900.0,
            total_resource_size_kb=2048.5,
            resource_count=50,
            error_count=0
        )
        self.assertEqual(metrics.total_resource_size_kb, 2048.5)
        self.assertEqual(metrics.resource_count, 50)
        self.assertEqual(metrics.error_count, 0)
    
    def test_to_dict(self):
        """测试转换为字典"""
        metrics = PerformanceMetrics(
            url="https://example.com",
            timestamp="2026-02-21T10:00:00",
            load_time_ms=1000.0,
            dom_content_loaded_ms=500.0
        )
        metrics_dict = metrics.to_dict()
        self.assertIsInstance(metrics_dict, dict)
        self.assertEqual(metrics_dict['url'], "https://example.com")
        self.assertEqual(metrics_dict['load_time_ms'], 1000.0)


class TestScreenshotComparisonResult(unittest.TestCase):
    """截图对比结果类测试"""
    
    def test_passed_result(self):
        """测试通过的对比结果"""
        result = ScreenshotComparisonResult(
            baseline_path="./baseline.png",
            current_path="./current.png",
            diff_path=None,
            similarity_score=0.98,
            pixel_diff_count=100,
            passed=True,
            threshold=0.1
        )
        self.assertTrue(result.passed)
        self.assertEqual(result.similarity_score, 0.98)
        self.assertIsNone(result.diff_path)
    
    def test_failed_result(self):
        """测试失败的对比结果"""
        result = ScreenshotComparisonResult(
            baseline_path="./baseline.png",
            current_path="./current.png",
            diff_path="./diff.png",
            similarity_score=0.85,
            pixel_diff_count=15000,
            passed=False,
            threshold=0.1
        )
        self.assertFalse(result.passed)
        self.assertEqual(result.diff_path, "./diff.png")
    
    def test_to_dict(self):
        """测试转换为字典"""
        result = ScreenshotComparisonResult(
            baseline_path="./baseline.png",
            current_path="./current.png",
            diff_path=None,
            similarity_score=0.95,
            pixel_diff_count=500,
            passed=True,
            threshold=0.1
        )
        result_dict = result.to_dict()
        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict['similarity_score'], 0.95)


class TestVisualComparator(unittest.TestCase):
    """视觉对比器测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.test_dir = Path(__file__).parent / "test_images"
        self.test_dir.mkdir(exist_ok=True)
        
        # 创建测试图片
        self.baseline_path = self.test_dir / "baseline.png"
        self.current_path = self.test_dir / "current.png"
        
        # 创建完全相同的图片
        img = Image.new('RGB', (100, 100), color='red')
        img.save(self.baseline_path)
        img.save(self.current_path)
    
    def tearDown(self):
        """测试后置清理"""
        # 清理测试文件
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_compare_identical_images(self):
        """测试比较完全相同的图片"""
        result = VisualComparator.compare_images(
            str(self.baseline_path),
            str(self.current_path),
            str(self.test_dir),
            threshold=0.1
        )
        self.assertTrue(result.passed)
        self.assertEqual(result.similarity_score, 1.0)
        self.assertEqual(result.pixel_diff_count, 0)
        self.assertIsNone(result.diff_path)
    
    def test_compare_different_images(self):
        """测试比较不同的图片"""
        # 创建不同的图片
        current_img = Image.new('RGB', (100, 100), color='blue')
        current_img.save(self.current_path)
        
        result = VisualComparator.compare_images(
            str(self.baseline_path),
            str(self.current_path),
            str(self.test_dir),
            threshold=0.1
        )
        self.assertFalse(result.passed)
        self.assertLess(result.similarity_score, 1.0)
        self.assertGreater(result.pixel_diff_count, 0)
        self.assertIsNotNone(result.diff_path)
    
    def test_compare_different_sizes(self):
        """测试比较不同尺寸的图片"""
        # 创建不同尺寸的图片
        current_img = Image.new('RGB', (150, 150), color='red')
        current_img.save(self.current_path)
        
        result = VisualComparator.compare_images(
            str(self.baseline_path),
            str(self.current_path),
            str(self.test_dir),
            threshold=0.1
        )
        # 应该自动调整大小并比较
        self.assertIsInstance(result.similarity_score, float)
    
    def test_file_not_found(self):
        """测试文件不存在的情况"""
        with self.assertRaises(FileNotFoundError):
            VisualComparator.compare_images(
                "./nonexistent_baseline.png",
                str(self.current_path),
                str(self.test_dir)
            )
    
    def test_compare_multiple(self):
        """测试批量比较"""
        # 创建多对测试图片
        for i in range(3):
            img = Image.new('RGB', (100, 100), color='red')
            img.save(self.test_dir / f"baseline_{i}.png")
            img.save(self.test_dir / f"current_{i}.png")
        
        results = VisualComparator.compare_multiple(
            str(self.test_dir),
            str(self.test_dir),
            str(self.test_dir)
        )
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertTrue(result.passed)


class TestTestReporter(unittest.TestCase):
    """测试报告生成器测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.test_dir = Path(__file__).parent / "test_reports"
        self.test_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """测试后置清理"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_generate_html_report(self):
        """测试生成HTML报告"""
        results = {
            'total': 10,
            'passed': 8,
            'failed': 2,
            'success': False,
            'steps': [
                {'step': 1, 'action': 'navigate', 'status': 'passed'},
                {'step': 2, 'action': 'click', 'status': 'passed'},
                {'step': 3, 'action': 'assert', 'status': 'failed', 'error': 'Element not found'}
            ]
        }
        
        output_path = str(self.test_dir / "report.html")
        result_path = TestReporter.generate_html_report(results, output_path, "Test Report")
        
        self.assertEqual(result_path, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        # 验证文件内容
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Test Report", content)
            self.assertIn("Total Tests", content)
            self.assertIn("10", content)
    
    def test_generate_json_report(self):
        """测试生成JSON报告"""
        results = {
            'total': 5,
            'passed': 5,
            'failed': 0,
            'success': True
        }
        
        output_path = str(self.test_dir / "report.json")
        result_path = TestReporter.generate_json_report(results, output_path)
        
        self.assertEqual(result_path, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        # 验证JSON内容
        import json
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn('timestamp', data)
            self.assertIn('results', data)
            self.assertEqual(data['results']['total'], 5)


class TestConfigTemplate(unittest.TestCase):
    """配置文件模板测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.test_dir = Path(__file__).parent / "test_config"
        self.test_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """测试后置清理"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_generate_config_template(self):
        """测试生成配置模板"""
        output_path = str(self.test_dir / "test-config.json")
        result_path = generate_config_template(output_path)
        
        self.assertEqual(result_path, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        # 验证JSON内容
        import json
        with open(output_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.assertIn('name', config)
            self.assertIn('base_url', config)
            self.assertIn('browsers', config)
            self.assertIn('tests', config)
            self.assertIn('visual_testing', config)
            self.assertIn('performance', config)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_end_to_end_workflow(self):
        """测试完整工作流程"""
        # 创建配置
        config = TestConfig(
            url="https://example.com",
            browser="chromium",
            headless=True,
            output_dir="./test-results"
        )
        
        # 验证配置
        self.assertEqual(config.url, "https://example.com")
        self.assertTrue(config.headless)
        
        # 转换为字典
        config_dict = config.to_dict()
        self.assertIsInstance(config_dict, dict)
    
    def test_performance_thresholds(self):
        """测试性能阈值"""
        # 良好性能
        good_metrics = PerformanceMetrics(
            url="https://example.com",
            timestamp="2026-02-21T10:00:00",
            load_time_ms=1200.0,
            dom_content_loaded_ms=600.0,
            first_contentful_paint_ms=800.0,
            largest_contentful_paint_ms=2000.0
        )
        self.assertLess(good_metrics.largest_contentful_paint_ms or 0, 2500)
        
        # 差性能
        poor_metrics = PerformanceMetrics(
            url="https://example.com",
            timestamp="2026-02-21T10:00:00",
            load_time_ms=5000.0,
            dom_content_loaded_ms=3000.0,
            largest_contentful_paint_ms=5000.0
        )
        self.assertGreater(poor_metrics.largest_contentful_paint_ms or 0, 4000)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestTestConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestScreenshotComparisonResult))
    suite.addTests(loader.loadTestsFromTestCase(TestVisualComparator))
    suite.addTests(loader.loadTestsFromTestCase(TestTestReporter))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigTemplate))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
