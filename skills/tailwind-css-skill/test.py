#!/usr/bin/env python3
"""Tailwind CSS Skill - 测试文件"""

import unittest
import sys
sys.path.insert(0, '.')

from main import TailwindGenerator, ComponentPresets


class TestTailwindGenerator(unittest.TestCase):
    """测试TailwindGenerator类"""
    
    def setUp(self):
        self.generator = TailwindGenerator()
    
    def test_generate_component_button(self):
        """测试生成按钮组件"""
        classes = self.generator.generate_component("button", "primary", "md")
        self.assertIn("bg-blue-600", classes)
        self.assertIn("hover:bg-blue-700", classes)
        self.assertIn("text-white", classes)
        self.assertIn("px-4", classes)
        self.assertIn("py-2", classes)
    
    def test_generate_component_card(self):
        """测试生成卡片组件"""
        classes = self.generator.generate_component("card", "elevated", "lg")
        self.assertIn("bg-white", classes)
        self.assertIn("rounded-xl", classes)
        self.assertIn("shadow-lg", classes)
        self.assertIn("p-8", classes)
    
    def test_generate_component_input(self):
        """测试生成输入框组件"""
        classes = self.generator.generate_component("input", "error", "md")
        self.assertIn("border-red-500", classes)
        self.assertIn("focus:ring-red-500", classes)
        self.assertIn("w-full", classes)
    
    def test_generate_component_badge(self):
        """测试生成标签组件"""
        classes = self.generator.generate_component("badge", "success", "md")
        self.assertIn("bg-green-100", classes)
        self.assertIn("text-green-800", classes)
        self.assertIn("rounded-full", classes)
    
    def test_generate_responsive(self):
        """测试生成响应式类名"""
        classes = {
            "default": "grid-cols-1",
            "md": "grid-cols-2",
            "lg": "grid-cols-4"
        }
        result = self.generator.generate_responsive(classes)
        self.assertIn("grid-cols-1", result)
        self.assertIn("md:grid-cols-2", result)
        self.assertIn("lg:grid-cols-4", result)
    
    def test_generate_grid(self):
        """测试生成网格布局"""
        cols = {"default": 1, "md": 2, "lg": 4}
        result = self.generator.generate_grid(cols, "6")
        self.assertIn("grid", result)
        self.assertIn("grid-cols-1", result)
        self.assertIn("md:grid-cols-2", result)
        self.assertIn("lg:grid-cols-4", result)
        self.assertIn("gap-6", result)
    
    def test_generate_flex(self):
        """测试生成Flex布局"""
        result = self.generator.generate_flex(
            direction="col",
            justify="center",
            align="center",
            gap="4"
        )
        self.assertIn("flex", result)
        self.assertIn("flex-col", result)
        self.assertIn("justify-center", result)
        self.assertIn("items-center", result)
        self.assertIn("gap-4", result)
    
    def test_generate_color(self):
        """测试生成颜色类名"""
        bg_class = self.generator.generate_color("blue", 500, "bg")
        self.assertEqual(bg_class, "bg-blue-500")
        
        text_class = self.generator.generate_color("red", 600, "text")
        self.assertEqual(text_class, "text-red-600")
        
        border_class = self.generator.generate_color("green", 500, "border", 50)
        self.assertEqual(border_class, "border-green-500/50")
    
    def test_generate_spacing(self):
        """测试生成间距类名"""
        m = self.generator.generate_spacing("4", "m", "all")
        self.assertEqual(m, "m-4")
        
        px = self.generator.generate_spacing("6", "p", "x")
        self.assertEqual(px, "px-6")
        
        mt = self.generator.generate_spacing("8", "m", "t")
        self.assertEqual(mt, "mt-8")
    
    def test_generate_config(self):
        """测试生成配置文件"""
        config = self.generator.generate_config(
            content=["./src/**/*.{js,ts}"],
            theme_extensions={"colors": {"brand": "#3B82F6"}},
            plugins=["@tailwindcss/forms"]
        )
        self.assertIn("content", config)
        self.assertIn("theme", config)
        self.assertIn("plugins", config)
        self.assertEqual(config["content"][0], "./src/**/*.{js,ts}")
    
    def test_generate_typography(self):
        """测试生成排版类名"""
        classes = self.generator.generate_typography(
            size="xl",
            weight="bold",
            color="gray-800",
            align="center"
        )
        self.assertIn("text-xl", classes)
        self.assertIn("font-bold", classes)
        self.assertIn("text-gray-800", classes)
        self.assertIn("text-center", classes)
    
    def test_optimize_classes(self):
        """测试优化类名"""
        original = "px-4 py-2 px-4 bg-blue-500 text-white"
        optimized = self.generator.optimize_classes(original)
        self.assertEqual(optimized.count("px-4"), 1)
        self.assertIn("px-4", optimized)
        self.assertIn("py-2", optimized)
        self.assertIn("bg-blue-500", optimized)
    
    def test_validate_classes(self):
        """测试验证类名"""
        classes = "bg-blue-500 text-white px-4 invalid-class-123"
        result = self.generator.validate_classes(classes)
        
        self.assertIn("bg-blue-500", result["valid"])
        self.assertIn("text-white", result["valid"])
        self.assertIn("px-4", result["valid"])
        self.assertIn("invalid-class-123", result["invalid"])
        self.assertEqual(result["valid_count"], 3)
        self.assertEqual(result["invalid_count"], 1)
    
    def test_get_suggestions(self):
        """测试获取类名建议"""
        color_suggestions = self.generator.get_suggestions("bg")
        self.assertGreater(len(color_suggestions), 0)
        self.assertTrue(all(s.startswith("bg-") for s in color_suggestions))
        
        spacing_suggestions = self.generator.get_suggestions("p")
        self.assertGreater(len(spacing_suggestions), 0)
        self.assertTrue(all(s.startswith("p-") for s in spacing_suggestions))
    
    def test_invalid_component_type(self):
        """测试无效组件类型"""
        with self.assertRaises(ValueError):
            self.generator.generate_component("invalid-type")
    
    def test_component_presets(self):
        """测试组件预设"""
        self.assertIn("button", self.generator.presets)
        self.assertIn("card", self.generator.presets)
        self.assertIn("input", self.generator.presets)
        self.assertIn("badge", self.generator.presets)
        self.assertIn("alert", self.generator.presets)


class TestComponentPresets(unittest.TestCase):
    """测试组件预设"""
    
    def test_button_presets(self):
        """测试按钮预设"""
        preset = ComponentPresets.BUTTON
        self.assertIn("primary", preset.variants)
        self.assertIn("danger", preset.variants)
        self.assertIn("md", preset.sizes)
        self.assertIn("disabled", preset.states)
    
    def test_card_presets(self):
        """测试卡片预设"""
        preset = ComponentPresets.CARD
        self.assertIn("default", preset.variants)
        self.assertIn("elevated", preset.variants)
        self.assertIn("interactive", preset.variants)
    
    def test_input_presets(self):
        """测试输入框预设"""
        preset = ComponentPresets.INPUT
        self.assertIn("error", preset.variants)
        self.assertIn("success", preset.variants)
        self.assertIn("focus", preset.states)
    
    def test_badge_presets(self):
        """测试标签预设"""
        preset = ComponentPresets.BADGE
        self.assertIn("default", preset.variants)
        self.assertIn("success", preset.variants)
        self.assertIn("purple", preset.variants)
    
    def test_alert_presets(self):
        """测试警告框预设"""
        preset = ComponentPresets.ALERT
        self.assertIn("info", preset.variants)
        self.assertIn("error", preset.variants)
        self.assertIn("warning", preset.variants)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestTailwindGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestComponentPresets))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
