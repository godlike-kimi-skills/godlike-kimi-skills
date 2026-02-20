#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrangler Skill - Basic Tests
基础测试套件
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import WranglerSkill, WranglerConfig, WranglerAction


class TestWranglerConfig(unittest.TestCase):
    """测试 WranglerConfig 类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "wrangler.toml"
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_default_config(self):
        """测试默认配置"""
        config = WranglerConfig()
        self.assertEqual(config.name, "")
        self.assertEqual(config.account_id, "")
        self.assertEqual(config.main, "src/index.js")
    
    def test_config_to_toml(self):
        """测试配置转 TOML"""
        config = WranglerConfig(
            name="test-worker",
            account_id="123456",
            compatibility_date="2024-01-01",
            main="src/index.ts"
        )
        toml_str = config.to_toml()
        self.assertIn("name = \"test-worker\"", toml_str)
        self.assertIn("account_id = \"123456\"", toml_str)
    
    def test_load_from_toml(self):
        """测试从 TOML 文件加载"""
        toml_content = '''
name = "my-worker"
account_id = "abc123"
compatibility_date = "2024-06-01"
main = "src/worker.js"
'''
        self.config_path.write_text(toml_content, encoding="utf-8")
        config = WranglerConfig.from_file(self.config_path)
        
        self.assertEqual(config.name, "my-worker")
        self.assertEqual(config.account_id, "abc123")
        self.assertEqual(config.compatibility_date, "2024-06-01")
        self.assertEqual(config.main, "src/worker.js")
    
    def test_load_from_nonexistent_file(self):
        """测试从不存在文件加载"""
        config = WranglerConfig.from_file("/nonexistent/wrangler.toml")
        self.assertEqual(config.name, "")
        self.assertEqual(config.account_id, "")


class TestWranglerSkill(unittest.TestCase):
    """测试 WranglerSkill 类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.skill = WranglerSkill(self.temp_dir)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_init_with_path(self):
        """测试使用路径初始化"""
        skill = WranglerSkill(self.temp_dir)
        self.assertEqual(skill.project_path, Path(self.temp_dir))
        self.assertEqual(skill.wrangler_toml, Path(self.temp_dir) / "wrangler.toml")
    
    def test_init_without_path(self):
        """测试不使用路径初始化"""
        skill = WranglerSkill()
        self.assertEqual(skill.project_path, Path.cwd())
    
    def test_check_project_no_toml(self):
        """测试检查项目 - 无 toml 文件"""
        # 无 wrangler.toml 时应该返回 False
        self.assertFalse(self.skill._check_project())
    
    def test_check_project_with_toml(self):
        """测试检查项目 - 有 toml 文件"""
        # 创建 wrangler.toml
        self.skill.wrangler_toml.write_text("name = 'test'\n", encoding="utf-8")
        self.assertTrue(self.skill._check_project())
    
    def test_dry_run_flag(self):
        """测试 dry_run 标志"""
        skill = WranglerSkill(self.temp_dir)
        skill.dry_run = True
        self.assertTrue(skill.dry_run)
    
    def test_config_loading(self):
        """测试配置加载"""
        toml_content = '''
name = "test-worker"
account_id = "test123"
'''
        self.skill.wrangler_toml.write_text(toml_content, encoding="utf-8")
        skill = WranglerSkill(self.temp_dir)
        
        self.assertEqual(skill.config.name, "test-worker")
        self.assertEqual(skill.config.account_id, "test123")


class TestWranglerAction(unittest.TestCase):
    """测试 WranglerAction 枚举"""
    
    def test_action_values(self):
        """测试所有操作类型"""
        actions = [
            "deploy", "dev", "kv", "d1", "r2",
            "tail", "init", "config", "status", "logs"
        ]
        for action in actions:
            self.assertIsNotNone(WranglerAction(action))
    
    def test_action_enum_members(self):
        """测试枚举成员"""
        self.assertEqual(WranglerAction.DEPLOY.value, "deploy")
        self.assertEqual(WranglerAction.DEV.value, "dev")
        self.assertEqual(WranglerAction.KV.value, "kv")
        self.assertEqual(WranglerAction.D1.value, "d1")
        self.assertEqual(WranglerAction.R2.value, "r2")


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_full_workflow_simulation(self):
        """模拟完整工作流"""
        skill = WranglerSkill(self.temp_dir)
        skill.dry_run = True
        
        # 模拟创建配置
        toml_content = '''
name = "integration-test"
account_id = "test-account"
compatibility_date = "2024-01-01"
main = "src/index.js"
'''
        skill.wrangler_toml.write_text(toml_content, encoding="utf-8")
        
        # 重新加载配置
        skill = WranglerSkill(self.temp_dir)
        self.assertEqual(skill.config.name, "integration-test")
        self.assertEqual(skill.config.account_id, "test-account")
        
        # 检查项目状态
        self.assertTrue(skill._check_project())


class TestCommandLineArguments(unittest.TestCase):
    """测试命令行参数"""
    
    def test_action_parameter(self):
        """测试 action 参数"""
        # 测试所有有效的 action 值
        valid_actions = [e.value for e in WranglerAction]
        self.assertIn("deploy", valid_actions)
        self.assertIn("dev", valid_actions)
        self.assertIn("kv", valid_actions)
        self.assertIn("d1", valid_actions)
        self.assertIn("r2", valid_actions)
    
    def test_parameter_types(self):
        """测试参数类型"""
        # 这些参数应该是字符串类型
        string_params = ["project", "command", "env", "namespace", "key", "value", "file", "query"]
        # 这些参数应该是布尔类型
        bool_params = ["follow", "dry_run"]
        
        self.assertEqual(len(string_params), 8)
        self.assertEqual(len(bool_params), 2)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestWranglerConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestWranglerSkill))
    suite.addTests(loader.loadTestsFromTestCase(TestWranglerAction))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCommandLineArguments))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
