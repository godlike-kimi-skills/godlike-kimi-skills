#!/usr/bin/env python3
"""
基础测试

测试 Skill Creator Enhanced 的核心功能
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import SkillCreator, TEMPLATES


class TestSkillCreator(unittest.TestCase):
    """测试 SkillCreator 类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.creator = SkillCreator(output_dir=self.temp_dir)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_skill_name_valid(self):
        """测试有效的 skill_name"""
        valid_names = [
            "web-scraper",
            "pdf-converter",
            "data-processor",
            "test123",
            "a-b-c"
        ]
        for name in valid_names:
            with self.subTest(name=name):
                self.assertTrue(self.creator._validate_skill_name(name))
    
    def test_validate_skill_name_invalid(self):
        """测试无效的 skill_name"""
        invalid_names = [
            "WebScraper",  # 大写
            "web_scraper",  # 下划线
            "web scraper",  # 空格
            "123web",  # 数字开头
            "web@scraper",  # 特殊字符
            "",  # 空字符串
        ]
        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(self.creator._validate_skill_name(name))
    
    def test_create_skill_basic(self):
        """测试基础 Skill 创建"""
        project_dir = self.creator.create_skill(
            skill_name="test-skill",
            skill_title="测试技能",
            description="这是一个测试技能",
            category="development",
            template="basic",
            with_tests=False,
            with_ci=False,
            with_examples=False
        )
        
        # 验证目录存在
        self.assertTrue(project_dir.exists())
        
        # 验证必需文件
        required_files = ["skill.json", "SKILL.md", "README.md", "LICENSE", "main.py", ".gitignore"]
        for file in required_files:
            self.assertTrue((project_dir / file).exists(), f"Missing file: {file}")
        
        # 验证 skill.json 内容
        with open(project_dir / "skill.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        self.assertEqual(config["name"], "test-skill")
        self.assertEqual(config["title"], "测试技能")
        self.assertEqual(config["description"], "这是一个测试技能")
        self.assertEqual(config["category"], "development")
    
    def test_create_skill_with_tests(self):
        """测试带测试的 Skill 创建"""
        project_dir = self.creator.create_skill(
            skill_name="test-with-tests",
            skill_title="带测试的技能",
            description="测试技能",
            with_tests=True,
            with_ci=False,
            with_examples=False
        )
        
        tests_dir = project_dir / "tests"
        self.assertTrue(tests_dir.exists())
        self.assertTrue((tests_dir / "__init__.py").exists())
        self.assertTrue((tests_dir / "test_basic.py").exists())
        self.assertTrue((tests_dir / "test_advanced.py").exists())
    
    def test_create_skill_with_ci(self):
        """测试带 CI/CD 的 Skill 创建"""
        project_dir = self.creator.create_skill(
            skill_name="test-with-ci",
            skill_title="带CI的技能",
            description="测试技能",
            with_tests=False,
            with_ci=True,
            with_examples=False
        )
        
        github_dir = project_dir / ".github" / "workflows"
        self.assertTrue(github_dir.exists())
        self.assertTrue((github_dir / "ci.yml").exists())
        self.assertTrue((github_dir / "release.yml").exists())
    
    def test_create_skill_with_examples(self):
        """测试带示例的 Skill 创建"""
        project_dir = self.creator.create_skill(
            skill_name="test-with-examples",
            skill_title="带示例的技能",
            description="测试技能",
            with_tests=False,
            with_ci=False,
            with_examples=True
        )
        
        examples_dir = project_dir / "examples"
        self.assertTrue(examples_dir.exists())
        self.assertTrue((examples_dir / "basic_usage.py").exists())
        self.assertTrue((examples_dir / "advanced_usage.py").exists())
    
    def test_create_skill_duplicate_name(self):
        """测试重复名称抛出异常"""
        self.creator.create_skill(
            skill_name="duplicate-test",
            skill_title="重复测试",
            description="测试技能",
            with_tests=False,
            with_ci=False,
            with_examples=False
        )
        
        with self.assertRaises(FileExistsError):
            self.creator.create_skill(
                skill_name="duplicate-test",
                skill_title="重复测试2",
                description="测试技能2",
                with_tests=False,
                with_ci=False,
                with_examples=False
            )
    
    def test_validate_skill_valid(self):
        """测试验证有效的 Skill"""
        # 先创建一个 skill
        project_dir = self.creator.create_skill(
            skill_name="valid-skill",
            skill_title="有效技能",
            description="测试技能",
            with_tests=True,
            with_ci=True,
            with_examples=False
        )
        
        results = self.creator.validate_skill(str(project_dir))
        
        self.assertTrue(results["valid"])
        self.assertEqual(len(results["errors"]), 0)
        self.assertTrue(results["checks"]["skill.json"])
        self.assertTrue(results["checks"]["SKILL.md"])
    
    def test_validate_skill_missing_files(self):
        """测试验证缺少文件的 Skill"""
        # 创建空目录
        empty_skill_dir = Path(self.temp_dir) / "empty-skill"
        empty_skill_dir.mkdir()
        
        results = self.creator.validate_skill(str(empty_skill_dir))
        
        self.assertFalse(results["valid"])
        self.assertGreater(len(results["errors"]), 0)
    
    def test_list_templates(self):
        """测试列出模板"""
        templates = self.creator.list_templates()
        
        self.assertGreater(len(templates), 0)
        
        # 验证模板包含必要字段
        for template in templates:
            self.assertIn("id", template)
            self.assertIn("name", template)
            self.assertIn("description", template)


class TestTemplates(unittest.TestCase):
    """测试模板定义"""
    
    def test_templates_not_empty(self):
        """测试模板不为空"""
        self.assertGreater(len(TEMPLATES), 0)
    
    def test_template_structure(self):
        """测试模板结构正确"""
        for key, template in TEMPLATES.items():
            with self.subTest(template=key):
                self.assertIn("name", template)
                self.assertIn("description", template)
                self.assertIn("files", template)
                self.assertIsInstance(template["files"], list)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_workflow(self):
        """测试完整工作流程"""
        with tempfile.TemporaryDirectory() as temp_dir:
            creator = SkillCreator(output_dir=temp_dir)
            
            # 1. 创建 skill
            project_dir = creator.create_skill(
                skill_name="integration-test",
                skill_title="集成测试",
                description="集成测试技能",
                category="development",
                template="basic",
                with_tests=True,
                with_ci=True,
                with_examples=True
            )
            
            # 2. 验证创建成功
            self.assertTrue(project_dir.exists())
            
            # 3. 验证 skill.json 可解析
            skill_json_path = project_dir / "skill.json"
            with open(skill_json_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            self.assertEqual(config["name"], "integration-test")
            
            # 4. 验证生成的 main.py 语法正确
            main_py_path = project_dir / "main.py"
            with open(main_py_path, "r", encoding="utf-8") as f:
                code = f.read()
            
            # 尝试编译验证语法
            compile(code, str(main_py_path), "exec")
            
            # 5. 验证项目
            results = creator.validate_skill(str(project_dir))
            self.assertTrue(results["valid"])


if __name__ == "__main__":
    unittest.main()
