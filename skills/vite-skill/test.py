#!/usr/bin/env python3
"""Vite Skill - 测试文件"""

import unittest
import sys
sys.path.insert(0, '.')

from main import ViteGenerator, VitePlugins, VitePlugin


class TestViteGenerator(unittest.TestCase):
    """测试ViteGenerator类"""
    
    def setUp(self):
        self.generator = ViteGenerator()
    
    def test_generate_config_react(self):
        """测试React配置生成"""
        config = self.generator.generate_config(framework="react")
        self.assertIn("import { defineConfig }", config)
        self.assertIn("import react from", config)
        self.assertIn("plugins: [", config)
        self.assertIn("react()", config)
    
    def test_generate_config_vue(self):
        """测试Vue配置生成"""
        config = self.generator.generate_config(framework="vue")
        self.assertIn("import vue from", config)
        self.assertIn("vue()", config)
    
    def test_generate_config_with_base(self):
        """测试带base路径的配置"""
        config = self.generator.generate_config(base="/app/")
        self.assertIn('base: "/app/"', config)
    
    def test_generate_config_with_plugins(self):
        """测试带额外插件的配置"""
        config = self.generator.generate_config(
            framework="vanilla",
            plugins=["legacy", "pwa"]
        )
        self.assertIn("legacy", config)
        self.assertIn("VitePWA", config)
    
    def test_generate_package_json_react(self):
        """测试React项目package.json"""
        pkg = self.generator.generate_package_json("my-app", "react")
        self.assertEqual(pkg["name"], "my-app")
        self.assertIn("react", pkg["dependencies"])
        self.assertIn("react-dom", pkg["dependencies"])
    
    def test_generate_package_json_vue(self):
        """测试Vue项目package.json"""
        pkg = self.generator.generate_package_json("my-app", "vue-ts")
        self.assertIn("vue", pkg["dependencies"])
        self.assertIn("typescript", pkg["devDependencies"])
    
    def test_generate_env_development(self):
        """测试开发环境变量"""
        env = self.generator.generate_env("development")
        self.assertIn("NODE_ENV=development", env)
        self.assertIn("VITE_APP_BASE_URL", env)
    
    def test_generate_env_production(self):
        """测试生产环境变量"""
        env = self.generator.generate_env("production", {"API_KEY": "secret"})
        self.assertIn("NODE_ENV=production", env)
        self.assertIn("API_KEY=secret", env)
    
    def test_generate_env_types(self):
        """测试环境变量类型声明"""
        types = self.generator.generate_env_types(["VITE_API_URL", "VITE_APP_TITLE"])
        self.assertIn("interface ImportMetaEnv", types)
        self.assertIn("readonly VITE_API_URL: string", types)
        self.assertIn("readonly VITE_APP_TITLE: string", types)
    
    def test_get_project_commands(self):
        """测试项目创建命令"""
        commands = self.generator.get_project_commands("my-app", "react-ts")
        self.assertTrue(any("create vite" in cmd for cmd in commands))
        self.assertTrue(any("my-app" in cmd for cmd in commands))
        self.assertTrue(any("react-ts" in cmd for cmd in commands))
    
    def test_get_project_commands_invalid_template(self):
        """测试无效模板"""
        with self.assertRaises(ValueError):
            self.generator.get_project_commands("my-app", "invalid-template")
    
    def test_generate_proxy_config(self):
        """测试代理配置"""
        proxies = {
            "/api": "http://localhost:3000",
            "/ws": "ws://localhost:3001"
        }
        config = self.generator.generate_proxy_config(proxies)
        self.assertIn("/api", config)
        self.assertEqual(config["/api"]["target"], "http://localhost:3000")
        self.assertTrue(config["/api"]["changeOrigin"])
    
    def test_get_optimization_suggestions(self):
        """测试优化建议"""
        suggestions = self.generator.get_optimization_suggestions()
        self.assertGreater(len(suggestions), 0)
        for sugg in suggestions:
            self.assertIn("category", sugg)
            self.assertIn("tip", sugg)
            self.assertIn("example", sugg)
    
    def test_generate_html_template(self):
        """测试HTML模板生成"""
        html = self.generator.generate_html_template("My App", "zh-CN")
        self.assertIn("<!doctype html>", html)
        self.assertIn('<html lang="zh-CN">', html)
        self.assertIn("<title>My App</title>", html)
        self.assertIn('<div id="root"></div>', html)
    
    def test_dict_to_ts(self):
        """测试字典转TypeScript"""
        data = {"target": "es2015", "minify": True, "port": 3000}
        result = self.generator._dict_to_ts(data)
        self.assertIn('target: "es2015"', result)
        self.assertIn('minify: true', result)
        self.assertIn('port: 3000', result)


class TestVitePlugins(unittest.TestCase):
    """测试VitePlugins类"""
    
    def test_get_plugin_react(self):
        """测试获取React插件"""
        plugin = VitePlugins.get_plugin("react")
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.name, "react")
        self.assertEqual(plugin.package, "@vitejs/plugin-react")
    
    def test_get_plugin_invalid(self):
        """测试获取无效插件"""
        plugin = VitePlugins.get_plugin("nonexistent")
        self.assertIsNone(plugin)
    
    def test_list_plugins(self):
        """测试列出插件"""
        plugins = VitePlugins.list_plugins()
        self.assertIn("react", plugins)
        self.assertIn("vue", plugins)
        self.assertIn("legacy", plugins)
    
    def test_get_plugins_for_framework(self):
        """测试获取框架推荐插件"""
        react_plugins = VitePlugins.get_plugins_for_framework("react")
        self.assertIn("react", react_plugins)
        
        vue_plugins = VitePlugins.get_plugins_for_framework("vue")
        self.assertIn("vue", vue_plugins)


class TestVitePlugin(unittest.TestCase):
    """测试VitePlugin数据类"""
    
    def test_plugin_creation(self):
        """测试插件创建"""
        plugin = VitePlugin(
            name="test",
            import_name="testPlugin",
            package="vite-plugin-test",
            config={"option": "value"},
            description="Test plugin"
        )
        self.assertEqual(plugin.name, "test")
        self.assertEqual(plugin.import_name, "testPlugin")
        self.assertEqual(plugin.config["option"], "value")


class TestOfficialTemplates(unittest.TestCase):
    """测试官方模板列表"""
    
    def test_templates_exist(self):
        """测试模板列表存在"""
        generator = ViteGenerator()
        self.assertIn("vanilla", generator.OFFICIAL_TEMPLATES)
        self.assertIn("react", generator.OFFICIAL_TEMPLATES)
        self.assertIn("react-ts", generator.OFFICIAL_TEMPLATES)
        self.assertIn("vue", generator.OFFICIAL_TEMPLATES)
        self.assertIn("vue-ts", generator.OFFICIAL_TEMPLATES)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestViteGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestVitePlugins))
    suite.addTests(loader.loadTestsFromTestCase(TestVitePlugin))
    suite.addTests(loader.loadTestsFromTestCase(TestOfficialTemplates))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
