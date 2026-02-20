#!/usr/bin/env python3
"""ESLint Prettier Skill - 测试文件"""

import unittest
import sys
sys.path.insert(0, '.')

from main import ESLintGenerator, PrettierGenerator, IntegrationHelper, ESLintPresets, PrettierPresets


class TestESLintGenerator(unittest.TestCase):
    """测试ESLintGenerator类"""
    
    def setUp(self):
        self.generator = ESLintGenerator()
    
    def test_generate_config_vanilla(self):
        """测试Vanilla配置生成"""
        config = self.generator.generate_config(framework="vanilla")
        self.assertIn("env", config)
        self.assertIn("extends", config)
        self.assertIn("eslint:recommended", config["extends"])
        self.assertIn("rules", config)
    
    def test_generate_config_react(self):
        """测试React配置生成"""
        config = self.generator.generate_config(framework="react")
        self.assertIn("plugin:react/recommended", config["extends"])
        self.assertIn("react", config["plugins"])
        self.assertIn("react-hooks/rules-of-hooks", config["rules"])
    
    def test_generate_config_react_typescript(self):
        """测试React+TypeScript配置生成"""
        config = self.generator.generate_config(framework="react", typescript=True)
        self.assertIn("plugin:react/recommended", config["extends"])
        self.assertIn("@typescript-eslint/recommended", config["extends"])
        self.assertIn("@typescript-eslint/parser", config.get("parser", ""))
        self.assertIn("@typescript-eslint", config["plugins"])
    
    def test_generate_config_vue(self):
        """测试Vue配置生成"""
        config = self.generator.generate_config(framework="vue")
        self.assertIn("plugin:vue/vue3-recommended", config["extends"])
        self.assertIn("vue", config["plugins"])
    
    def test_generate_config_vue_typescript(self):
        """测试Vue+TypeScript配置生成"""
        config = self.generator.generate_config(framework="vue", typescript=True)
        self.assertIn("plugin:vue/vue3-recommended", config["extends"])
        self.assertIn("@vue/typescript/recommended", config["extends"])
    
    def test_generate_config_with_custom_rules(self):
        """测试自定义规则"""
        custom_rules = {"no-console": "off", "custom-rule": "error"}
        config = self.generator.generate_config(rules=custom_rules)
        self.assertEqual(config["rules"]["no-console"], "off")
        self.assertEqual(config["rules"]["custom-rule"], "error")
    
    def test_generate_flat_config(self):
        """测试Flat Config生成"""
        config = self.generator.generate_flat_config(framework="react", typescript=True)
        self.assertIn("import js from '@eslint/js'", config)
        self.assertIn("import ts from 'typescript-eslint'", config)
        self.assertIn("import react from 'eslint-plugin-react'", config)
        self.assertIn("export default", config)
    
    def test_generate_ignore_config(self):
        """测试忽略文件配置"""
        ignores = self.generator.generate_ignore_config()
        self.assertIn("node_modules/", ignores)
        self.assertIn("dist/", ignores)
        self.assertIn("build/", ignores)
    
    def test_get_install_command_npm(self):
        """测试npm安装命令"""
        cmd = self.generator.get_install_command("react", typescript=True, package_manager="npm")
        self.assertIn("npm install", cmd)
        self.assertIn("eslint", cmd)
        self.assertIn("eslint-plugin-react", cmd)
        self.assertIn("@typescript-eslint", cmd)
    
    def test_get_install_command_yarn(self):
        """测试yarn安装命令"""
        cmd = self.generator.get_install_command("vue", typescript=False, package_manager="yarn")
        self.assertIn("yarn add", cmd)
        self.assertIn("eslint-plugin-vue", cmd)


class TestPrettierGenerator(unittest.TestCase):
    """测试PrettierGenerator类"""
    
    def setUp(self):
        self.generator = PrettierGenerator()
    
    def test_generate_config_default(self):
        """测试默认配置"""
        config = self.generator.generate_config()
        self.assertTrue(config["semi"])
        self.assertTrue(config["singleQuote"])
        self.assertEqual(config["tabWidth"], 2)
        self.assertEqual(config["trailingComma"], "es5")
    
    def test_generate_config_custom(self):
        """测试自定义配置"""
        config = self.generator.generate_config(
            semi=False,
            single_quote=False,
            tab_width=4,
            print_width=120
        )
        self.assertFalse(config["semi"])
        self.assertFalse(config["singleQuote"])
        self.assertEqual(config["tabWidth"], 4)
        self.assertEqual(config["printWidth"], 120)
    
    def test_generate_from_preset(self):
        """测试预设配置"""
        config = self.generator.generate_from_preset("airbnb")
        self.assertEqual(config["trailingComma"], "all")
        
        config = self.generator.generate_from_preset("minimal")
        self.assertFalse(config["semi"])
        self.assertEqual(config["trailingComma"], "none")
    
    def test_generate_ignore_config(self):
        """测试忽略文件配置"""
        ignores = self.generator.generate_ignore_config()
        self.assertIn("node_modules/", ignores)
        self.assertIn("dist/", ignores)
        self.assertIn("package-lock.json", ignores)
    
    def test_generate_integrated_script(self):
        """测试集成脚本"""
        scripts = self.generator.generate_integrated_script("npm")
        self.assertIn("format", scripts)
        self.assertIn("format:check", scripts)
        self.assertIn("lint", scripts)
        self.assertIn("lint:fix", scripts)


class TestIntegrationHelper(unittest.TestCase):
    """测试IntegrationHelper类"""
    
    def test_generate_prettier_eslint_config(self):
        """测试Prettier集成配置"""
        config = IntegrationHelper.generate_prettier_eslint_config("react", typescript=True)
        self.assertIn("prettier", config["extends"])
        self.assertIn("prettier", config["plugins"])
        self.assertEqual(config["rules"]["prettier/prettier"], "error")
    
    def test_get_recommended_deps(self):
        """测试推荐依赖"""
        deps = IntegrationHelper.get_recommended_deps("react", typescript=True)
        self.assertIn("eslint", deps["eslint"])
        self.assertIn("prettier", deps["prettier"])
        self.assertIn("eslint-plugin-react", deps["eslint"])
        self.assertIn("@typescript-eslint/parser", deps["eslint"])
    
    def test_generate_setup_guide(self):
        """测试设置指南"""
        guide = IntegrationHelper.generate_setup_guide("vue", typescript=False)
        self.assertTrue(any("Install dependencies" in line for line in guide))
        self.assertTrue(any("eslint-plugin-vue" in line for line in guide))


class TestESLintPresets(unittest.TestCase):
    """测试ESLintPresets类"""
    
    def test_react_rules_exist(self):
        """测试React规则存在"""
        self.assertIn("react/prop-types", ESLintPresets.REACT_RULES)
        self.assertIn("react-hooks/rules-of-hooks", ESLintPresets.REACT_RULES)
    
    def test_vue_rules_exist(self):
        """测试Vue规则存在"""
        self.assertIn("vue/html-self-closing", ESLintPresets.VUE_RULES)
        self.assertIn("vue/max-attributes-per-line", ESLintPresets.VUE_RULES)
    
    def test_typescript_rules_exist(self):
        """测试TypeScript规则存在"""
        self.assertIn("@typescript-eslint/no-unused-vars", ESLintPresets.TYPESCRIPT_RULES)
        self.assertIn("@typescript-eslint/no-explicit-any", ESLintPresets.TYPESCRIPT_RULES)
    
    def test_best_practices_exist(self):
        """测试最佳实践规则存在"""
        self.assertIn("no-console", ESLintPresets.BEST_PRACTICES)
        self.assertIn("no-var", ESLintPresets.BEST_PRACTICES)
        self.assertIn("eqeqeq", ESLintPresets.BEST_PRACTICES)


class TestPrettierPresets(unittest.TestCase):
    """测试PrettierPresets类"""
    
    def test_default_preset(self):
        """测试默认预设"""
        preset = PrettierPresets.get_preset("default")
        self.assertTrue(preset["semi"])
        self.assertEqual(preset["tabWidth"], 2)
    
    def test_airbnb_preset(self):
        """测试Airbnb预设"""
        preset = PrettierPresets.get_preset("airbnb")
        self.assertEqual(preset["trailingComma"], "all")
    
    def test_invalid_preset(self):
        """测试无效预设返回默认值"""
        preset = PrettierPresets.get_preset("nonexistent")
        self.assertEqual(preset, PrettierPresets.DEFAULT)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestESLintGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestPrettierGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationHelper))
    suite.addTests(loader.loadTestsFromTestCase(TestESLintPresets))
    suite.addTests(loader.loadTestsFromTestCase(TestPrettierPresets))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
