#!/usr/bin/env python3
"""
高级测试

测试 Skill Creator Enhanced 的边界情况和高级功能
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import SkillCreator


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.creator = SkillCreator(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_skill_name_with_numbers(self):
        """测试带数字的 skill_name"""
        project_dir = self.creator.create_skill(
            skill_name="test-123-skill",
            skill_title="测试123",
            description="测试",
            with_tests=False,
            with_ci=False,
            with_examples=False
        )
        
        with open(project_dir / "skill.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        self.assertEqual(config["name"], "test-123-skill")
    
    def test_long_skill_name(self):
        """测试长 skill_name"""
        long_name = "very-long-skill-name-for-testing-purpose"
        project_dir = self.creator.create_skill(
            skill_name=long_name,
            skill_title="长名称测试",
            description="测试",
            with_tests=False,
            with_ci=False,
            with_examples=False
        )
        
        self.assertTrue(project_dir.exists())
    
    def test_unicode_content(self):
        """测试 Unicode 内容"""
        project_dir = self.creator.create_skill(
            skill_name="unicode-test",
            skill_title="🚀 Unicode测试",
            description="测试中文、日本語、한국어、Emoji 🎉",
            with_tests=False,
            with_ci=False,
            with_examples=False
        )
        
        with open(project_dir / "skill.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        self.assertEqual(config["title"], "🚀 Unicode测试")
    
    def test_special_characters_in_description(self):
        """测试描述中的特殊字符"""
        description = "Test with <tags> & special chars: \"quoted\" and 'single'"
        project_dir = self.creator.create_skill(
            skill_name="special-chars",
            skill_title="特殊字符测试",
            description=description,
            with_tests=False,
            with_ci=False,
            with_examples=False
        )
        
        with open(project_dir / "skill.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        self.assertEqual(config["description"], description)


class TestDifferentTemplates(unittest.TestCase):
    """测试不同模板"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.creator = SkillCreator(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cli_tool_template(self):
        """测试 CLI 工具模板"""
        project_dir = self.creator.create_skill(
            skill_name="cli-tool-test",
            skill_title="CLI工具",
            description="命令行工具",
            template="cli-tool",
            with_tests=False,
            with_ci=False,
            with_examples=False
        )
        
        main_py = project_dir / "main.py"
        with open(main_py, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 验证 CLI 特有代码
        self.assertIn("subparsers", content)
        self.assertIn("add_subparsers", content)
    
    def test_data_processor_template(self):
        """测试数据处理模板"""
        project_dir = self.creator.create_skill(
            skill_name="data-processor-test",
            skill_title="数据处理器",
            description="数据处理",
            template="data-processor",
            with_tests=False,
            with_ci=False,
            with_examples=False
        )
        
        main_py = project_dir / "main.py"
        with open(main_py, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 验证数据处理特有代码
        self.assertIn("load_data", content)
        self.assertIn("DataProcessor", content)
    
    def test_automation_template(self):
        """测试自动化模板"""
        project_dir = self.creator.create_skill(
            skill_name="automation-test",
            skill_title="自动化工具",
            description="自动化",
            template="automation",
            with_tests=False,
            with_ci=False,
            with_examples=False
        )
        
        main_py = project_dir / "main.py"
        with open(main_py, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 验证自动化特有代码
        self.assertIn("Workflow", content)
        self.assertIn("add_step", content)
        self.assertIn("execute", content)


class TestValidationEdgeCases(unittest.TestCase):
    """验证边界情况测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.creator = SkillCreator(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_invalid_json(self):
        """测试验证无效的 JSON"""
        skill_dir = Path(self.temp_dir) / "invalid-json"
        skill_dir.mkdir()
        
        # 创建无效的 skill.json
        with open(skill_dir / "skill.json", "w", encoding="utf-8") as f:
            f.write("{ invalid json }")
        
        results = self.creator.validate_skill(str(skill_dir))
        
        self.assertFalse(results["valid"])
        self.assertTrue(any("Invalid skill.json" in e for e in results["errors"]))
    
    def test_validate_missing_required_fields(self):
        """测试验证缺少必填字段"""
        skill_dir = Path(self.temp_dir) / "missing-fields"
        skill_dir.mkdir()
        
        # 创建缺少字段的 skill.json
        with open(skill_dir / "skill.json", "w", encoding="utf-8") as f:
            json.dump({"name": "test"}, f)
        
        results = self.creator.validate_skill(str(skill_dir))
        
        self.assertFalse(results["valid"])
        # 应该有关于缺少字段的错误
        self.assertGreater(len(results["errors"]), 0)
    
    def test_validate_invalid_name_format(self):
        """测试验证无效的 name 格式"""
        skill_dir = Path(self.temp_dir) / "invalid-name"
        skill_dir.mkdir()
        
        # 创建 name 格式错误的 skill.json
        with open(skill_dir / "skill.json", "w", encoding="utf-8") as f:
            json.dump({
                "name": "InvalidName",
                "version": "1.0.0",
                "title": "Test",
                "description": "Test",
                "main": "main.py"
            }, f)
        
        results = self.creator.validate_skill(str(skill_dir))
        
        self.assertFalse(results["valid"])
        self.assertTrue(any("Invalid skill name" in e for e in results["errors"]))


class TestFilePermissions(unittest.TestCase):
    """文件权限测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.creator = SkillCreator(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generated_files_readable(self):
        """测试生成的文件可读"""
        project_dir = self.creator.create_skill(
            skill_name="readable-test",
            skill_title="可读性测试",
            description="测试",
            with_tests=True,
            with_ci=True,
            with_examples=True
        )
        
        # 检查所有文件可读
        for file_path in project_dir.rglob("*"):
            if file_path.is_file():
                self.assertTrue(os.access(file_path, os.R_OK))
    
    def test_main_py_executable(self):
        """测试 main.py 可执行"""
        project_dir = self.creator.create_skill(
            skill_name="executable-test",
            skill_title="可执行测试",
            description="测试",
            with_tests=False,
            with_ci=False,
            with_examples=False
        )
        
        main_py = project_dir / "main.py"
        
        # 尝试读取并执行
        with open(main_py, "r", encoding="utf-8") as f:
            code = f.read()
        
        # 验证是有效的 Python 代码
        compile(code, str(main_py), "exec")


class TestPerformance(unittest.TestCase):
    """性能测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.creator = SkillCreator(output_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_skill_performance(self):
        """测试创建 skill 的性能"""
        import time
        
        start = time.time()
        
        self.creator.create_skill(
            skill_name="perf-test",
            skill_title="性能测试",
            description="测试性能",
            with_tests=True,
            with_ci=True,
            with_examples=True
        )
        
        elapsed = time.time() - start
        
        # 应该在 1 秒内完成
        self.assertLess(elapsed, 1.0)
    
    def test_multiple_skills_creation(self):
        """测试批量创建多个 skills"""
        for i in range(5):
            self.creator.create_skill(
                skill_name=f"batch-test-{i}",
                skill_title=f"批量测试{i}",
                description=f"测试{i}",
                with_tests=False,
                with_ci=False,
                with_examples=False
            )
        
        # 验证所有都创建了
        for i in range(5):
            skill_dir = Path(self.temp_dir) / f"batch-test-{i}"
            self.assertTrue(skill_dir.exists())


if __name__ == "__main__":
    unittest.main()
