#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Postman Collection Skill
"""

import unittest
import json
import os
import tempfile
from pathlib import Path
from main import (
    PostmanCollectionBuilder, PostmanEnvironmentBuilder,
    PostmanVariable, PostmanHeader, PostmanItem,
    OpenAPIToPostmanConverter, export_collection, import_collection,
    generate_test_script
)


class TestPostmanVariable(unittest.TestCase):
    """测试PostmanVariable数据类"""
    
    def test_default_values(self):
        var = PostmanVariable(key="test")
        self.assertEqual(var.key, "test")
        self.assertEqual(var.value, "")
        self.assertEqual(var.type_, "string")
        
    def test_custom_values(self):
        var = PostmanVariable(
            key="apiKey",
            value="secret123",
            type_="string",
            description="API Key"
        )
        self.assertEqual(var.value, "secret123")
        self.assertEqual(var.description, "API Key")


class TestPostmanCollectionBuilder(unittest.TestCase):
    """测试PostmanCollectionBuilder"""
    
    def setUp(self):
        self.builder = PostmanCollectionBuilder(name="Test Collection")
        
    def test_basic_build(self):
        """测试基本构建"""
        collection = self.builder.build()
        
        self.assertEqual(collection["info"]["name"], "Test Collection")
        self.assertEqual(collection["info"]["schema"], self.builder.SCHEMA)
        self.assertIn("_postman_id", collection["info"])
        
    def test_add_folder(self):
        """测试添加文件夹"""
        self.builder.add_folder("Users", "User management")
        collection = self.builder.build()
        
        self.assertEqual(len(collection["item"]), 1)
        self.assertEqual(collection["item"][0]["name"], "Users")
        
    def test_add_request(self):
        """测试添加请求"""
        self.builder.add_request(
            name="Get Users",
            method="GET",
            url="https://api.example.com/users"
        )
        collection = self.builder.build()
        
        self.assertEqual(len(collection["item"]), 1)
        self.assertEqual(collection["item"][0]["name"], "Get Users")
        self.assertEqual(collection["item"][0]["request"]["method"], "GET")
        
    def test_add_request_to_folder(self):
        """测试添加请求到文件夹"""
        self.builder.add_request(
            name="Get Users",
            method="GET",
            url="https://api.example.com/users",
            folder="Users"
        )
        collection = self.builder.build()
        
        self.assertEqual(len(collection["item"]), 1)
        self.assertEqual(collection["item"][0]["name"], "Users")
        self.assertEqual(len(collection["item"][0]["item"]), 1)
        
    def test_add_variable(self):
        """测试添加变量"""
        self.builder.add_variable("baseUrl", "https://api.example.com")
        collection = self.builder.build()
        
        self.assertEqual(len(collection["variable"]), 1)
        self.assertEqual(collection["variable"][0]["key"], "baseUrl")
        self.assertEqual(collection["variable"][0]["value"], "https://api.example.com")
        
    def test_set_auth_bearer(self):
        """测试Bearer认证"""
        self.builder.set_auth("bearer", token="test-token")
        collection = self.builder.build()
        
        self.assertEqual(collection["auth"]["type"], "bearer")
        self.assertEqual(collection["auth"]["bearer"][0]["value"], "test-token")
        
    def test_set_auth_basic(self):
        """测试Basic认证"""
        self.builder.set_auth("basic", username="admin", password="secret")
        collection = self.builder.build()
        
        self.assertEqual(collection["auth"]["type"], "basic")
        self.assertEqual(collection["auth"]["basic"][0]["value"], "admin")
        
    def test_add_prerequest_script(self):
        """测试前置脚本"""
        self.builder.add_prerequest_script("console.log('test');")
        collection = self.builder.build()
        
        self.assertEqual(len(collection["event"]), 1)
        self.assertEqual(collection["event"][0]["listen"], "prerequest")


class TestPostmanEnvironmentBuilder(unittest.TestCase):
    """测试PostmanEnvironmentBuilder"""
    
    def test_basic_build(self):
        builder = PostmanEnvironmentBuilder(name="Test Environment")
        env = builder.build()
        
        self.assertEqual(env["name"], "Test Environment")
        self.assertEqual(env["_postman_variable_scope"], "default")
        
    def test_add_variable(self):
        builder = PostmanEnvironmentBuilder(name="Test")
        builder.add_variable("apiKey", "secret123", "string")
        builder.add_variable("timeout", 5000, "number")
        env = builder.build()
        
        self.assertEqual(len(env["values"]), 2)
        self.assertEqual(env["values"][0]["key"], "apiKey")
        self.assertEqual(env["values"][0]["value"], "secret123")


class TestOpenAPIToPostmanConverter(unittest.TestCase):
    """测试OpenAPI转换器"""
    
    def setUp(self):
        self.openapi_spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "servers": [{"url": "https://api.example.com"}],
            "paths": {
                "/users": {
                    "get": {
                        "summary": "List users",
                        "operationId": "listUsers",
                        "tags": ["users"],
                        "parameters": [
                            {"name": "page", "in": "query", "schema": {"type": "integer"}}
                        ],
                        "responses": {"200": {"description": "Success"}}
                    },
                    "post": {
                        "summary": "Create user",
                        "tags": ["users"],
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/User"}
                                }
                            }
                        },
                        "responses": {"201": {"description": "Created"}}
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"}
                        }
                    }
                }
            }
        }
        
    def test_basic_conversion(self):
        """测试基本转换"""
        converter = OpenAPIToPostmanConverter(self.openapi_spec)
        collection = converter.convert()
        
        self.assertEqual(collection["info"]["name"], "Test API")
        self.assertIn("item", collection)
        
    def test_folder_creation_from_tags(self):
        """测试从tags创建文件夹"""
        converter = OpenAPIToPostmanConverter(self.openapi_spec)
        collection = converter.convert()
        
        # 应该创建users文件夹
        folder_names = [item["name"] for item in collection["item"]]
        self.assertIn("users", folder_names)
        
    def test_request_generation(self):
        """测试请求生成"""
        converter = OpenAPIToPostmanConverter(self.openapi_spec)
        collection = converter.convert()
        
        # 查找users文件夹
        users_folder = None
        for item in collection["item"]:
            if item["name"] == "users":
                users_folder = item
                break
                
        self.assertIsNotNone(users_folder)
        self.assertEqual(len(users_folder["item"]), 2)  # GET和POST
        
    def test_parameter_conversion(self):
        """测试参数转换"""
        converter = OpenAPIToPostmanConverter(self.openapi_spec)
        collection = converter.convert()
        
        # 检查变量是否添加
        var_keys = [v["key"] for v in collection.get("variable", [])]
        self.assertIn("baseUrl", var_keys)
        
    def test_test_script_generation(self):
        """测试脚本生成"""
        converter = OpenAPIToPostmanConverter(self.openapi_spec)
        collection = converter.convert()
        
        # 检查请求是否包含测试事件
        users_folder = next(item for item in collection["item"] if item["name"] == "users")
        for request in users_folder["item"]:
            self.assertIn("event", request)
            test_events = [e for e in request["event"] if e["listen"] == "test"]
            self.assertGreater(len(test_events), 0)


class TestExportImport(unittest.TestCase):
    """测试导入导出功能"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.collection = {
            "info": {"name": "Test", "schema": "test"},
            "item": []
        }
        
    def test_export_collection(self):
        """测试导出集合"""
        filepath = os.path.join(self.temp_dir, "test.json")
        result = export_collection(self.collection, filepath)
        
        self.assertTrue(os.path.exists(result))
        with open(result) as f:
            loaded = json.load(f)
        self.assertEqual(loaded["info"]["name"], "Test")
        
    def test_import_collection(self):
        """测试导入集合"""
        filepath = os.path.join(self.temp_dir, "test.json")
        export_collection(self.collection, filepath)
        
        loaded = import_collection(filepath)
        self.assertEqual(loaded["info"]["name"], "Test")


class TestGenerateTestScript(unittest.TestCase):
    """测试测试脚本生成"""
    
    def test_basic_assertions(self):
        """测试基本断言"""
        script = generate_test_script(["status_ok", "is_json"])
        
        self.assertIn("Status code is 200", script)
        self.assertIn("Response is JSON", script)
        
    def test_response_time_assertion(self):
        """测试响应时间断言"""
        script = generate_test_script(["response_time"])
        
        self.assertIn("Response time is acceptable", script)
        
    def test_variable_extraction(self):
        """测试变量提取"""
        script = generate_test_script([], variables=["token", "userId"])
        
        self.assertIn("pm.environment.set('token'", script)
        self.assertIn("pm.environment.set('userId'", script)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_complete_workflow(self):
        """测试完整工作流"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. 创建集合
            builder = PostmanCollectionBuilder(name="Integration Test")
            builder.add_variable("baseUrl", "https://api.test.com")
            builder.add_request(
                name="Test Request",
                method="GET",
                url="{{baseUrl}}/test",
                tests="pm.test('OK', function () { pm.response.to.have.status(200); });"
            )
            collection = builder.build()
            
            # 2. 导出
            col_path = os.path.join(tmpdir, "test.postman_collection.json")
            export_collection(collection, col_path)
            
            # 3. 导入
            loaded = import_collection(col_path)
            
            # 4. 验证
            self.assertEqual(loaded["info"]["name"], "Integration Test")
            self.assertEqual(len(loaded["variable"]), 1)
            
            # 5. 创建环境
            env_builder = PostmanEnvironmentBuilder(name="Test Env")
            env_builder.add_variable("apiKey", "test-key")
            environment = env_builder.build()
            
            # 6. 导出环境
            env_path = os.path.join(tmpdir, "test.postman_environment.json")
            export_collection(environment, env_path)
            
            self.assertTrue(os.path.exists(env_path))


class TestCommandLine(unittest.TestCase):
    """测试命令行接口"""
    
    def test_run_create(self):
        """测试创建命令"""
        from main import run
        result = run(["create", "--name", "Test API", "--url", "https://api.test.com"])
        
        self.assertTrue(result["success"])
        self.assertEqual(result["action"], "create")
        self.assertIn("collection", result)
        
    def test_run_export(self):
        """测试导出命令"""
        from main import run
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "env.json")
            result = run(["export", "--name", "Test Env", "--output", output_path])
            
            self.assertTrue(result["success"])
            self.assertEqual(result["output_file"], output_path)
            self.assertTrue(os.path.exists(output_path))
            
    def test_run_test(self):
        """测试生成命令"""
        from main import run
        result = run(["test"])
        
        self.assertTrue(result["success"])
        self.assertIn("test_script", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
