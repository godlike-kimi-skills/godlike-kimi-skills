#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for OpenAPI Generator Skill
"""

import unittest
import json
import os
import tempfile
from pathlib import Path
from main import (
    OpenAPISpecBuilder, OpenAPIInfo, OpenAPIServer,
    APIOperation, APIParameter, APIResponse,
    ClientGenerator, validate_spec, export_spec
)


class TestOpenAPIInfo(unittest.TestCase):
    """测试OpenAPIInfo数据类"""
    
    def test_default_values(self):
        info = OpenAPIInfo()
        self.assertEqual(info.title, "API")
        self.assertEqual(info.version, "1.0.0")
        self.assertEqual(info.description, "")
        
    def test_custom_values(self):
        info = OpenAPIInfo(
            title="Test API",
            version="2.0.0",
            description="A test API",
            contact={"name": "John", "email": "john@test.com"},
            license={"name": "MIT"}
        )
        self.assertEqual(info.title, "Test API")
        self.assertEqual(info.version, "2.0.0")
        self.assertEqual(info.contact["name"], "John")


class TestOpenAPISpecBuilder(unittest.TestCase):
    """测试OpenAPISpecBuilder"""
    
    def setUp(self):
        self.builder = OpenAPISpecBuilder(openapi_version="3.0.3")
        
    def test_basic_build(self):
        """测试基本构建"""
        self.builder.set_info(OpenAPIInfo(title="Test API", version="1.0.0"))
        spec = self.builder.build()
        
        self.assertEqual(spec["openapi"], "3.0.3")
        self.assertEqual(spec["info"]["title"], "Test API")
        self.assertEqual(spec["info"]["version"], "1.0.0")
        
    def test_add_server(self):
        """测试添加服务器"""
        self.builder.set_info(OpenAPIInfo())
        self.builder.add_server(OpenAPIServer(url="https://api.example.com", description="Production"))
        spec = self.builder.build()
        
        self.assertEqual(len(spec["servers"]), 1)
        self.assertEqual(spec["servers"][0]["url"], "https://api.example.com")
        
    def test_add_schema(self):
        """测试添加Schema"""
        self.builder.set_info(OpenAPIInfo())
        self.builder.add_schema("Pet", {
            "type": "object",
            "properties": {"name": {"type": "string"}}
        })
        spec = self.builder.build()
        
        self.assertIn("Pet", spec["components"]["schemas"])
        self.assertEqual(spec["components"]["schemas"]["Pet"]["type"], "object")
        
    def test_add_security_scheme(self):
        """测试添加安全方案"""
        self.builder.set_info(OpenAPIInfo())
        self.builder.add_security_scheme(
            name="bearerAuth",
            type_="http",
            scheme="bearer"
        )
        spec = self.builder.build()
        
        self.assertIn("bearerAuth", spec["components"]["securitySchemes"])
        self.assertEqual(spec["components"]["securitySchemes"]["bearerAuth"]["type"], "http")
        
    def test_add_operation(self):
        """测试添加操作"""
        self.builder.set_info(OpenAPIInfo())
        operation = APIOperation(
            method="GET",
            path="/pets",
            summary="List pets",
            operation_id="listPets",
            responses=[APIResponse(code="200", description="Success")]
        )
        self.builder.add_operation(operation)
        spec = self.builder.build()
        
        self.assertIn("/pets", spec["paths"])
        self.assertIn("get", spec["paths"]["/pets"])
        self.assertEqual(spec["paths"]["/pets"]["get"]["summary"], "List pets")
        
    def test_add_operation_with_parameters(self):
        """测试带参数的操作"""
        self.builder.set_info(OpenAPIInfo())
        operation = APIOperation(
            method="GET",
            path="/pets/{id}",
            summary="Get pet",
            parameters=[
                APIParameter(name="id", in_="path", required=True, type_="integer")
            ],
            responses=[APIResponse(code="200", description="Success")]
        )
        self.builder.add_operation(operation)
        spec = self.builder.build()
        
        params = spec["paths"]["/pets/{id}"]["get"]["parameters"]
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0]["name"], "id")
        self.assertTrue(params[0]["required"])


class TestValidateSpec(unittest.TestCase):
    """测试规范验证"""
    
    def test_valid_spec(self):
        """测试有效规范"""
        spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {
                "/test": {
                    "get": {
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }
        errors = validate_spec(spec)
        self.assertEqual(len(errors), 0)
        
    def test_missing_openapi_field(self):
        """测试缺少openapi字段"""
        spec = {
            "info": {"title": "Test", "version": "1.0"},
            "paths": {}
        }
        errors = validate_spec(spec)
        self.assertIn("Missing 'openapi' field", errors)
        
    def test_missing_info_title(self):
        """测试缺少info.title"""
        spec = {
            "openapi": "3.0.3",
            "info": {"version": "1.0"},
            "paths": {}
        }
        errors = validate_spec(spec)
        self.assertIn("Missing 'info.title' field", errors)
        
    def test_missing_responses(self):
        """测试缺少responses"""
        spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {
                "/test": {
                    "get": {}
                }
            }
        }
        errors = validate_spec(spec)
        self.assertTrue(any("Missing responses" in e for e in errors))


class TestExportSpec(unittest.TestCase):
    """测试导出功能"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {}
        }
        
    def test_export_json(self):
        """测试JSON导出"""
        filepath = os.path.join(self.temp_dir, "test.json")
        result = export_spec(self.spec, filepath, "json")
        
        self.assertTrue(os.path.exists(result))
        with open(result) as f:
            loaded = json.load(f)
        self.assertEqual(loaded["info"]["title"], "Test")
        
    def test_export_yaml(self):
        """测试YAML导出"""
        filepath = os.path.join(self.temp_dir, "test.yaml")
        result = export_spec(self.spec, filepath, "yaml")
        
        self.assertTrue(os.path.exists(result))
        with open(result) as f:
            content = f.read()
        self.assertIn("openapi:", content)
        
    def test_export_invalid_format(self):
        """测试无效格式"""
        with self.assertRaises(ValueError):
            export_spec(self.spec, "test.xml", "xml")


class TestClientGenerator(unittest.TestCase):
    """测试客户端生成器"""
    
    def setUp(self):
        self.spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0"},
            "servers": [{"url": "https://api.example.com"}],
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "listUsers",
                        "summary": "List users",
                        "parameters": [
                            {"name": "limit", "in": "query", "schema": {"type": "integer"}}
                        ],
                        "responses": {"200": {"description": "Success"}}
                    },
                    "post": {
                        "operationId": "createUser",
                        "summary": "Create user",
                        "responses": {"201": {"description": "Created"}}
                    }
                }
            }
        }
        self.generator = ClientGenerator(self.spec)
        
    def test_generate_python(self):
        """测试生成Python客户端"""
        code = self.generator.generate("python", "TestClient")
        
        self.assertIn("class TestClient", code)
        self.assertIn("def list_users", code)
        self.assertIn("def create_user", code)
        self.assertIn("import requests", code)
        
    def test_generate_javascript(self):
        """测试生成JavaScript客户端"""
        code = self.generator.generate("javascript", "TestClient")
        
        self.assertIn("class TestClient", code)
        self.assertIn("async listUsers", code)
        self.assertIn("module.exports", code)
        
    def test_generate_invalid_language(self):
        """测试无效语言"""
        with self.assertRaises(ValueError):
            self.generator.generate("java", "TestClient")


class TestCommandLine(unittest.TestCase):
    """测试命令行接口"""
    
    def test_run_generate_basic(self):
        """测试基本生成命令"""
        from main import run
        result = run(["generate", "--title", "Test API", "--version", "1.0.0"])
        
        self.assertTrue(result["success"])
        self.assertEqual(result["action"], "generate")
        self.assertIn("spec", result)
        self.assertEqual(result["spec"]["info"]["title"], "Test API")
        
    def test_run_validate(self):
        """测试验证命令"""
        from main import run
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "openapi": "3.0.3",
                "info": {"title": "Test", "version": "1.0"},
                "paths": {"/test": {"get": {"responses": {"200": {"description": "OK"}}}}}
            }, f)
            temp_path = f.name
            
        try:
            result = run(["validate", "--input", temp_path])
            self.assertTrue(result["success"])
            self.assertTrue(result["valid"])
        finally:
            os.unlink(temp_path)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_workflow(self):
        """测试完整工作流"""
        # 1. 构建规范
        builder = OpenAPISpecBuilder()
        builder.set_info(OpenAPIInfo(
            title="Pet Store",
            version="1.0.0",
            description="Pet management API"
        ))
        builder.add_server(OpenAPIServer(url="https://api.petstore.com"))
        builder.add_schema("Pet", {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"}
            }
        })
        builder.add_operation(APIOperation(
            method="GET",
            path="/pets",
            summary="List pets",
            operation_id="listPets",
            responses=[APIResponse(code="200", description="Success")]
        ))
        
        spec = builder.build()
        
        # 2. 验证规范
        errors = validate_spec(spec)
        self.assertEqual(len(errors), 0)
        
        # 3. 导出规范
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "spec.json")
            export_spec(spec, filepath, "json")
            self.assertTrue(os.path.exists(filepath))
            
            # 4. 生成客户端
            with open(filepath) as f:
                loaded_spec = json.load(f)
            generator = ClientGenerator(loaded_spec)
            code = generator.generate("python", "PetStoreClient")
            
            self.assertIn("class PetStoreClient", code)
            self.assertIn("def list_pets", code)


if __name__ == "__main__":
    unittest.main(verbosity=2)
