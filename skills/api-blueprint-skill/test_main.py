#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for API Blueprint Skill
"""

import unittest
import json
import os
import tempfile
from pathlib import Path
from main import (
    APIBlueprintBuilder, ResourceGroup, Resource, Action,
    HttpMethod, Parameter, ParameterType, Request, Response,
    MockServerGenerator, OpenAPIToBlueprintConverter,
    validate_blueprint, export_blueprint
)


class TestAPIBlueprintBuilder(unittest.TestCase):
    """测试APIBlueprintBuilder"""
    
    def setUp(self):
        self.builder = APIBlueprintBuilder(
            name="Test API",
            description="A test API",
            host="https://api.test.com"
        )
        
    def test_basic_build(self):
        """测试基本构建"""
        result = self.builder.build()
        
        self.assertIn("FORMAT: 1A", result)
        self.assertIn("# Test API", result)
        self.assertIn("HOST: https://api.test.com", result)
        
    def test_add_metadata(self):
        """测试添加元数据"""
        self.builder.add_metadata("VERSION", "1.0.0")
        result = self.builder.build()
        
        self.assertIn("VERSION: 1.0.0", result)
        
    def test_add_resource_group(self):
        """测试添加资源组"""
        group = self.builder.add_resource_group("Users", "User operations")
        
        self.assertEqual(group.name, "Users")
        self.assertEqual(len(self.builder.resource_groups), 1)
        
    def test_add_resource(self):
        """测试添加资源"""
        resource = self.builder.add_resource("User", "/users/{id}")
        
        self.assertEqual(resource.name, "User")
        self.assertEqual(resource.uri_template, "/users/{id}")
        self.assertEqual(len(self.builder.resources), 1)
        
    def test_add_resource_to_group(self):
        """测试添加资源到组"""
        group = self.builder.add_resource_group("Users")
        resource = self.builder.add_resource("User", "/users", group=group)
        
        self.assertEqual(len(group.resources), 1)
        self.assertEqual(group.resources[0].name, "User")
        
    def test_add_action(self):
        """测试添加操作"""
        resource = self.builder.add_resource("User", "/users/{id}")
        action = self.builder.add_action(
            resource=resource,
            name="Get User",
            method=HttpMethod.GET
        )
        
        self.assertEqual(action.name, "Get User")
        self.assertEqual(action.method, HttpMethod.GET)
        self.assertEqual(len(resource.actions), 1)
        
    def test_add_request(self):
        """测试添加请求"""
        resource = self.builder.add_resource("User", "/users/{id}")
        action = self.builder.add_action(resource, "Get User", HttpMethod.GET)
        
        request = self.builder.add_request(
            action=action,
            parameters=[Parameter(name="id", type_=ParameterType.STRING, required=True)]
        )
        
        self.assertIsNotNone(action.request)
        self.assertEqual(len(action.request.parameters), 1)
        
    def test_add_response(self):
        """测试添加响应"""
        resource = self.builder.add_resource("User", "/users/{id}")
        action = self.builder.add_action(resource, "Get User", HttpMethod.GET)
        
        response = self.builder.add_response(
            action=action,
            status_code=200,
            description="Success"
        )
        
        self.assertEqual(len(action.responses), 1)
        self.assertEqual(action.responses[0].status_code, 200)
        
    def test_complete_blueprint(self):
        """测试完整Blueprint"""
        group = self.builder.add_resource_group("Users")
        resource = self.builder.add_resource("User", "/users/{id}", group=group)
        action = self.builder.add_action(resource, "Get User", HttpMethod.GET)
        self.builder.add_request(action, parameters=[Parameter(name="id", required=True)])
        self.builder.add_response(action, 200, example='{"id": "1"}')
        
        result = self.builder.build()
        
        self.assertIn("# Group Users", result)
        self.assertIn("## User [/users/{id}]", result)
        self.assertIn("### Get User [GET /users/{id}]", result)
        self.assertIn("+ Parameters", result)
        self.assertIn("+ Response 200", result)


class TestMockServerGenerator(unittest.TestCase):
    """测试MockServerGenerator"""
    
    def setUp(self):
        self.blueprint = '''FORMAT: 1A
# Test API

## Users [/users]

### List Users [GET /users]

+ Response 200

### Create User [POST /users]

+ Response 201
'''
        self.generator = MockServerGenerator(self.blueprint)
        
    def test_generate_flask_app(self):
        """测试生成Flask应用"""
        code = self.generator.generate_flask_app()
        
        self.assertIn("from flask import Flask", code)
        self.assertIn("@app.route('/users', methods=['GET'])", code)
        self.assertIn("@app.route('/users', methods=['POST'])", code)
        self.assertIn("def get_users():", code)
        
    def test_generate_express_app(self):
        """测试生成Express应用"""
        code = self.generator.generate_express_app()
        
        self.assertIn("const express = require", code)
        self.assertIn("app.get('/users'", code)
        self.assertIn("app.post('/users'", code)
        self.assertIn("const PORT = process.env.PORT", code)


class TestOpenAPIToBlueprintConverter(unittest.TestCase):
    """测试OpenAPIToBlueprintConverter"""
    
    def setUp(self):
        self.openapi_spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "description": "A test API"
            },
            "servers": [{"url": "https://api.test.com"}],
            "paths": {
                "/users": {
                    "get": {
                        "summary": "List users",
                        "tags": ["users"],
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }
        
    def test_basic_conversion(self):
        """测试基本转换"""
        converter = OpenAPIToBlueprintConverter(self.openapi_spec)
        result = converter.convert()
        
        self.assertIn("# Test API", result)
        self.assertIn("HOST: https://api.test.com", result)
        
    def test_group_conversion(self):
        """测试分组转换"""
        converter = OpenAPIToBlueprintConverter(self.openapi_spec)
        result = converter.convert()
        
        self.assertIn("# Group users", result)
        
    def test_resource_conversion(self):
        """测试资源转换"""
        converter = OpenAPIToBlueprintConverter(self.openapi_spec)
        result = converter.convert()
        
        self.assertIn("## Users [/users]", result)
        
    def test_action_conversion(self):
        """测试操作转换"""
        converter = OpenAPIToBlueprintConverter(self.openapi_spec)
        result = converter.convert()
        
        self.assertIn("### List users [GET /users]", result)
        
    def test_with_parameters(self):
        """测试带参数的转换"""
        self.openapi_spec["paths"]["/users"]["get"]["parameters"] = [
            {"name": "limit", "in": "query", "schema": {"type": "integer"}}
        ]
        
        converter = OpenAPIToBlueprintConverter(self.openapi_spec)
        result = converter.convert()
        
        self.assertIn("+ Parameters", result)
        self.assertIn("limit", result)


class TestValidateBlueprint(unittest.TestCase):
    """测试验证功能"""
    
    def test_valid_blueprint(self):
        """测试有效文档"""
        blueprint = '''FORMAT: 1A
# Test API

## Resource [/test]

### Action [GET /test]

+ Response 200
'''
        errors = validate_blueprint(blueprint)
        
        self.assertEqual(len(errors), 0)
        
    def test_missing_format(self):
        """测试缺少格式声明"""
        blueprint = '''# Test API
'''
        errors = validate_blueprint(blueprint)
        
        self.assertIn("Missing FORMAT declaration", errors)
        
    def test_missing_api_name(self):
        """测试缺少API名称"""
        blueprint = '''FORMAT: 1A
'''
        errors = validate_blueprint(blueprint)
        
        self.assertIn("Missing API name", errors)
        
    def test_no_resources(self):
        """测试无资源"""
        blueprint = '''FORMAT: 1A
# Test API
'''
        errors = validate_blueprint(blueprint)
        
        self.assertIn("No resources defined", errors)


class TestExportBlueprint(unittest.TestCase):
    """测试导出功能"""
    
    def test_export_to_file(self):
        """测试导出到文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.apib")
            result = export_blueprint("FORMAT: 1A", filepath)
            
            self.assertTrue(os.path.exists(result))
            with open(result) as f:
                content = f.read()
            self.assertEqual(content, "FORMAT: 1A")


class TestDataClasses(unittest.TestCase):
    """测试数据类"""
    
    def test_parameter(self):
        """测试Parameter"""
        param = Parameter(
            name="id",
            type_=ParameterType.STRING,
            required=True,
            description="User ID"
        )
        
        self.assertEqual(param.name, "id")
        self.assertTrue(param.required)
        
    def test_request(self):
        """测试Request"""
        request = Request(
            method=HttpMethod.GET,
            description="Test request"
        )
        
        self.assertEqual(request.method, HttpMethod.GET)
        
    def test_response(self):
        """测试Response"""
        response = Response(
            status_code=200,
            description="OK",
            body='{"id": 1}'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, '{"id": 1}')


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_complete_workflow(self):
        """测试完整工作流"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. 创建Blueprint
            builder = APIBlueprintBuilder(
                name="Integration Test API",
                host="https://api.test.com"
            )
            
            group = builder.add_resource_group("Test")
            resource = builder.add_resource("Item", "/items", group=group)
            action = builder.add_action(resource, "Get Item", HttpMethod.GET)
            self.builder_response = self.builder.add_response(action, 200, example='{"id": 1}')
            
            blueprint = builder.build()
            
            # 2. 导出
            filepath = os.path.join(tmpdir, "test.apib")
            export_blueprint(blueprint, filepath)
            
            # 3. 验证
            errors = validate_blueprint(blueprint)
            self.assertEqual(len(errors), 0)
            
            # 4. 生成Mock服务器
            generator = MockServerGenerator(blueprint)
            flask_code = generator.generate_flask_app()
            
            mock_path = os.path.join(tmpdir, "mock.py")
            with open(mock_path, "w") as f:
                f.write(flask_code)
                
            self.assertTrue(os.path.exists(mock_path))
            self.assertIn("from flask import Flask", flask_code)


class TestCommandLine(unittest.TestCase):
    """测试命令行接口"""
    
    def test_run_create(self):
        """测试创建命令"""
        from main import run
        result = run(["create", "--name", "Test API", "--host", "https://api.test.com"])
        
        self.assertTrue(result["success"])
        self.assertIn("blueprint", result)
        self.assertIn("# Test API", result["blueprint"])
        
    def test_run_convert(self):
        """测试转换命令"""
        from main import run
        
        with tempfile.TemporaryDirectory() as tmpdir:
            spec_path = os.path.join(tmpdir, "spec.json")
            with open(spec_path, "w") as f:
                json.dump({
                    "openapi": "3.0.3",
                    "info": {"title": "Test", "version": "1.0"},
                    "paths": {}
                }, f)
            
            output_path = os.path.join(tmpdir, "api.apib")
            result = run(["convert", "--input", spec_path, "--output", output_path])
            
            self.assertTrue(result["success"])
            self.assertTrue(os.path.exists(output_path))
            
    def test_run_validate(self):
        """测试验证命令"""
        from main import run
        
        with tempfile.TemporaryDirectory() as tmpdir:
            blueprint_path = os.path.join(tmpdir, "test.apib")
            with open(blueprint_path, "w") as f:
                f.write('''FORMAT: 1A
# Test
## Resource [/test]
### Action [GET /test]
+ Response 200
''')
            
            result = run(["validate", "--input", blueprint_path])
            
            self.assertTrue(result["success"])
            self.assertTrue(result["valid"])
            
    def test_run_mock(self):
        """测试Mock命令"""
        from main import run
        
        with tempfile.TemporaryDirectory() as tmpdir:
            blueprint_path = os.path.join(tmpdir, "test.apib")
            with open(blueprint_path, "w") as f:
                f.write('''FORMAT: 1A
# Test
## Resource [/test]
### Action [GET /test]
+ Response 200
''')
            
            output_path = os.path.join(tmpdir, "mock.py")
            result = run(["mock", "--input", blueprint_path, "--output", output_path, "--framework", "flask"])
            
            self.assertTrue(result["success"])
            self.assertTrue(os.path.exists(output_path))


if __name__ == "__main__":
    unittest.main(verbosity=2)
