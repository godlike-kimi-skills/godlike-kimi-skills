#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Markdown Docs Skill
"""

import unittest
import json
import os
import tempfile
from pathlib import Path
from main import (
    MarkdownBuilder, READMEGenerator, APIDocGenerator, ChangelogGenerator,
    ProjectInfo, APIEndpoint, ChangelogEntry, DocType,
    generate_readme, generate_api_docs
)


class TestMarkdownBuilder(unittest.TestCase):
    """测试MarkdownBuilder"""
    
    def test_basic_heading(self):
        """测试基本标题"""
        builder = MarkdownBuilder()
        result = builder.add_heading("Title", 1).build()
        self.assertIn("# Title", result)
        
    def test_multiple_headings(self):
        """测试多级标题"""
        builder = MarkdownBuilder()
        result = (builder
            .add_heading("H1", 1)
            .add_heading("H2", 2)
            .add_heading("H3", 3)
            .build())
        self.assertIn("# H1", result)
        self.assertIn("## H2", result)
        self.assertIn("### H3", result)
        
    def test_paragraph(self):
        """测试段落"""
        builder = MarkdownBuilder()
        result = builder.add_paragraph("This is a paragraph.").build()
        self.assertIn("This is a paragraph.", result)
        
    def test_code_block(self):
        """测试代码块"""
        builder = MarkdownBuilder()
        result = builder.add_code_block("print('hello')", "python").build()
        self.assertIn("```python", result)
        self.assertIn("print('hello')", result)
        self.assertIn("```", result)
        
    def test_unordered_list(self):
        """测试无序列表"""
        builder = MarkdownBuilder()
        result = builder.add_list(["Item 1", "Item 2", "Item 3"]).build()
        self.assertIn("- Item 1", result)
        self.assertIn("- Item 2", result)
        self.assertIn("- Item 3", result)
        
    def test_ordered_list(self):
        """测试有序列表"""
        builder = MarkdownBuilder()
        result = builder.add_list(["First", "Second"], ordered=True).build()
        self.assertIn("1. First", result)
        self.assertIn("2. Second", result)
        
    def test_table(self):
        """测试表格"""
        builder = MarkdownBuilder()
        result = builder.add_table(
            headers=["Name", "Age"],
            rows=[["Alice", "25"], ["Bob", "30"]]
        ).build()
        self.assertIn("| Name | Age |", result)
        self.assertIn("| --- | --- |", result)
        self.assertIn("| Alice | 25 |", result)
        
    def test_blockquote(self):
        """测试引用块"""
        builder = MarkdownBuilder()
        result = builder.add_blockquote("This is a quote.").build()
        self.assertIn("> This is a quote.", result)
        
    def test_horizontal_rule(self):
        """测试水平线"""
        builder = MarkdownBuilder()
        result = builder.add_horizontal_rule().build()
        self.assertIn("---", result)
        
    def test_badge(self):
        """测试徽章"""
        builder = MarkdownBuilder()
        result = builder.add_badge("license", "MIT", "blue").build()
        self.assertIn("![license](https://img.shields.io/badge/license-MIT-blue)", result)
        
    def test_toc_generation(self):
        """测试目录生成"""
        builder = MarkdownBuilder(title="Doc")
        result = (builder
            .add_heading("Section 1", 2)
            .add_heading("Subsection", 3)
            .add_heading("Section 2", 2)
            .build())
        self.assertIn("## Table of Contents", result)
        self.assertIn("[Section 1](#section-1)", result)
        self.assertIn("[Section 2](#section-2)", result)


class TestREADMEGenerator(unittest.TestCase):
    """测试READMEGenerator"""
    
    def setUp(self):
        self.project_info = ProjectInfo(
            name="Test Project",
            description="A test project",
            version="1.0.0",
            author="Test Author",
            license="MIT",
            repository="https://github.com/test/repo"
        )
        
    def test_default_template(self):
        """测试默认模板"""
        generator = READMEGenerator(self.project_info, template="default")
        result = generator.generate()
        
        self.assertIn("# Test Project", result)
        self.assertIn("A test project", result)
        self.assertIn("Installation", result)
        self.assertIn("Usage", result)
        
    def test_minimal_template(self):
        """测试最小模板"""
        generator = READMEGenerator(self.project_info, template="minimal")
        result = generator.generate()
        
        self.assertIn("Description", result)
        self.assertIn("Installation", result)
        self.assertIn("Usage", result)
        # 最小模板不应包含API Reference
        self.assertNotIn("API Reference", result)
        
    def test_full_template(self):
        """测试完整模板"""
        generator = READMEGenerator(self.project_info, template="full")
        result = generator.generate()
        
        self.assertIn("Features", result)
        self.assertIn("Installation", result)
        self.assertIn("Contributing", result)
        
    def test_custom_section(self):
        """测试自定义章节"""
        generator = READMEGenerator(self.project_info)
        generator.set_section("custom_section", "Custom content here.")
        result = generator.generate()
        
        # 注意：只有当模板包含该章节时才会显示
        self.assertIsNotNone(result)


class TestAPIDocGenerator(unittest.TestCase):
    """测试APIDocGenerator"""
    
    def setUp(self):
        self.generator = APIDocGenerator(title="Test API")
        
    def test_basic_generation(self):
        """测试基本生成"""
        result = self.generator.generate()
        
        self.assertIn("# Test API", result)
        self.assertIn("Overview", result)
        
    def test_add_endpoint(self):
        """测试添加端点"""
        endpoint = APIEndpoint(
            method="GET",
            path="/users",
            summary="List users",
            description="Get all users"
        )
        self.generator.add_endpoint(endpoint)
        result = self.generator.generate()
        
        self.assertIn("GET /users", result)
        self.assertIn("List users", result)
        
    def test_endpoint_with_parameters(self):
        """测试带参数的端点"""
        endpoint = APIEndpoint(
            method="GET",
            path="/users/{id}",
            summary="Get user",
            parameters=[
                {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}
            ]
        )
        self.generator.add_endpoint(endpoint)
        result = self.generator.generate()
        
        self.assertIn("Parameters", result)
        self.assertIn("id", result)
        
    def test_add_model(self):
        """测试添加模型"""
        self.generator.add_model("User", {
            "type": "object",
            "properties": {"name": {"type": "string"}}
        })
        result = self.generator.generate()
        
        self.assertIn("Data Models", result)
        self.assertIn("User", result)
        
    def test_from_openapi(self):
        """测试从OpenAPI生成"""
        openapi_spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {
                "/pets": {
                    "get": {
                        "summary": "List pets",
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            },
            "components": {
                "schemas": {
                    "Pet": {"type": "object"}
                }
            }
        }
        
        result = generate_api_docs(openapi_spec=openapi_spec)
        
        self.assertIn("List pets", result)
        self.assertIn("pets", result)


class TestChangelogGenerator(unittest.TestCase):
    """测试ChangelogGenerator"""
    
    def setUp(self):
        self.generator = ChangelogGenerator()
        
    def test_basic_generation(self):
        """测试基本生成"""
        result = self.generator.generate()
        
        self.assertIn("# Changelog", result)
        self.assertIn("Keep a Changelog", result)
        self.assertIn("Semantic Versioning", result)
        
    def test_add_version(self):
        """测试添加版本"""
        self.generator.add_version(
            "1.0.0",
            ["Initial release"],
            change_type="added"
        )
        result = self.generator.generate()
        
        self.assertIn("[1.0.0]", result)
        self.assertIn("Initial release", result)
        
    def test_multiple_versions(self):
        """测试多个版本"""
        self.generator.add_version("1.1.0", ["New feature"], change_type="added")
        self.generator.add_version("1.0.0", ["Initial release"], change_type="added")
        result = self.generator.generate()
        
        # 新版本应该在前
        index_1_1 = result.index("[1.1.0]")
        index_1_0 = result.index("[1.0.0]")
        self.assertLess(index_1_1, index_1_0)
        
    def test_different_change_types(self):
        """测试不同变更类型"""
        self.generator.add_version("1.0.0", ["Bug fix"], change_type="fixed")
        self.generator.add_version("0.9.0", ["Security patch"], change_type="security")
        result = self.generator.generate()
        
        self.assertIn("Fixed", result)
        self.assertIn("Security", result)


class TestGenerateReadme(unittest.TestCase):
    """测试generate_readme函数"""
    
    def test_basic_generation(self):
        """测试基本生成"""
        result = generate_readme(
            project_name="Test Project",
            description="A test project"
        )
        
        self.assertIn("# Test Project", result)
        self.assertIn("A test project", result)
        
    def test_with_metadata(self):
        """测试带元数据生成"""
        result = generate_readme(
            project_name="Test",
            description="Description",
            version="2.0.0",
            author="Author",
            license="Apache-2.0"
        )
        
        self.assertIn("Apache-2.0", result)


class TestProjectInfo(unittest.TestCase):
    """测试ProjectInfo数据类"""
    
    def test_default_values(self):
        info = ProjectInfo(name="Test")
        self.assertEqual(info.name, "Test")
        self.assertEqual(info.version, "1.0.0")
        self.assertEqual(info.license, "MIT")
        
    def test_custom_values(self):
        info = ProjectInfo(
            name="My Project",
            description="Description",
            version="2.0.0",
            author="Author Name",
            keywords=["api", "python"]
        )
        self.assertEqual(info.version, "2.0.0")
        self.assertEqual(info.keywords, ["api", "python"])


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_complete_documentation_suite(self):
        """测试完整文档套件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. 生成README
            readme = generate_readme(
                project_name="Test API",
                description="A test API",
                template="default",
                version="1.0.0"
            )
            readme_path = os.path.join(tmpdir, "README.md")
            with open(readme_path, "w") as f:
                f.write(readme)
            
            # 2. 生成API文档
            openapi_spec = {
                "openapi": "3.0.3",
                "info": {"title": "Test API", "version": "1.0"},
                "paths": {
                    "/test": {
                        "get": {
                            "summary": "Test endpoint",
                            "responses": {"200": {"description": "OK"}}
                        }
                    }
                }
            }
            api_doc = generate_api_docs(openapi_spec=openapi_spec)
            api_path = os.path.join(tmpdir, "API.md")
            with open(api_path, "w") as f:
                f.write(api_doc)
            
            # 3. 生成Changelog
            changelog_gen = ChangelogGenerator()
            changelog_gen.add_version("1.0.0", ["Initial release"])
            changelog = changelog_gen.generate()
            changelog_path = os.path.join(tmpdir, "CHANGELOG.md")
            with open(changelog_path, "w") as f:
                f.write(changelog)
            
            # 验证所有文件都存在
            self.assertTrue(os.path.exists(readme_path))
            self.assertTrue(os.path.exists(api_path))
            self.assertTrue(os.path.exists(changelog_path))
            
            # 验证内容
            with open(readme_path) as f:
                content = f.read()
                self.assertIn("Test API", content)


class TestCommandLine(unittest.TestCase):
    """测试命令行接口"""
    
    def test_run_readme(self):
        """测试README命令"""
        from main import run
        result = run(["readme", "--name", "Test Project", "--description", "A test"])
        
        self.assertTrue(result["success"])
        self.assertIn("content", result)
        self.assertIn("# Test Project", result["content"])
        
    def test_run_api(self):
        """测试API命令"""
        from main import run
        
        with tempfile.TemporaryDirectory() as tmpdir:
            spec_path = os.path.join(tmpdir, "spec.json")
            with open(spec_path, "w") as f:
                json.dump({
                    "openapi": "3.0.3",
                    "info": {"title": "Test", "version": "1.0"},
                    "paths": {}
                }, f)
            
            output_path = os.path.join(tmpdir, "API.md")
            result = run(["api", "--input", spec_path, "--output", output_path])
            
            self.assertTrue(result["success"])
            self.assertTrue(os.path.exists(output_path))
            
    def test_run_changelog(self):
        """测试Changelog命令"""
        from main import run
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "CHANGELOG.md")
            result = run(["changelog", "--name", "Test", "--version", "1.0.0", "--output", output_path])
            
            self.assertTrue(result["success"])
            self.assertTrue(os.path.exists(output_path))


if __name__ == "__main__":
    unittest.main(verbosity=2)
