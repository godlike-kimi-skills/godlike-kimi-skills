#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Blueprint Skill

功能：API Blueprint文档工具
- API文档编写
- Mock服务器生成
- 文档验证
- OpenAPI转API Blueprint

Use when documenting APIs, generating documentation, or when user mentions 'OpenAPI', 'Swagger', 'API docs'.
"""

import json
import os
import re
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ParameterType(Enum):
    """参数类型"""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


class HttpMethod(Enum):
    """HTTP方法"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass
class Parameter:
    """API参数"""
    name: str
    type_: ParameterType = ParameterType.STRING
    required: bool = False
    default: Any = None
    description: str = ""
    example: Any = None
    members: Optional[List[str]] = None  # 枚举值


@dataclass
class Request:
    """API请求"""
    method: HttpMethod
    description: str = ""
    parameters: List[Parameter] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    schema: Optional[Dict] = None
    example: Optional[str] = None


@dataclass
class Response:
    """API响应"""
    status_code: int
    description: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    schema: Optional[Dict] = None
    example: Optional[str] = None


@dataclass
class Action:
    """API操作"""
    name: str
    method: HttpMethod
    description: str = ""
    request: Optional[Request] = None
    responses: List[Response] = field(default_factory=list)
    uri_template: str = ""


@dataclass
class Resource:
    """API资源"""
    name: str
    uri_template: str
    description: str = ""
    actions: List[Action] = field(default_factory=list)
    model: Optional[Dict] = None


@dataclass
class ResourceGroup:
    """资源组"""
    name: str
    description: str = ""
    resources: List[Resource] = field(default_factory=list)


class APIBlueprintBuilder:
    """API Blueprint文档构建器"""
    
    def __init__(
        self,
        name: str = "API",
        description: str = "",
        host: str = "https://api.example.com",
        format_version: str = "1A"
    ):
        self.name = name
        self.description = description
        self.host = host
        self.format_version = format_version
        self.metadata: Dict[str, str] = {}
        self.resource_groups: List[ResourceGroup] = []
        self.resources: List[Resource] = []  # 未分组的资源
        
    def add_metadata(self, key: str, value: str) -> "APIBlueprintBuilder":
        """添加元数据"""
        self.metadata[key] = value
        return self
        
    def add_resource_group(
        self,
        name: str,
        description: str = ""
    ) -> ResourceGroup:
        """添加资源组"""
        group = ResourceGroup(name=name, description=description)
        self.resource_groups.append(group)
        return group
        
    def add_resource(
        self,
        name: str,
        uri_template: str,
        description: str = "",
        group: Optional[ResourceGroup] = None
    ) -> Resource:
        """添加资源"""
        resource = Resource(
            name=name,
            uri_template=uri_template,
            description=description
        )
        
        if group:
            group.resources.append(resource)
        else:
            self.resources.append(resource)
            
        return resource
        
    def add_action(
        self,
        resource: Resource,
        name: str,
        method: HttpMethod,
        description: str = "",
        uri_template: str = ""
    ) -> Action:
        """添加操作"""
        action = Action(
            name=name,
            method=method,
            description=description,
            uri_template=uri_template
        )
        resource.actions.append(action)
        return action
        
    def add_request(
        self,
        action: Action,
        description: str = "",
        parameters: Optional[List[Parameter]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        schema: Optional[Dict] = None,
        example: Optional[str] = None
    ) -> Request:
        """添加请求"""
        request = Request(
            method=action.method,
            description=description,
            parameters=parameters or [],
            headers=headers or {},
            body=body,
            schema=schema,
            example=example
        )
        action.request = request
        return request
        
    def add_response(
        self,
        action: Action,
        status_code: int,
        description: str = "",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        schema: Optional[Dict] = None,
        example: Optional[str] = None
    ) -> Response:
        """添加响应"""
        response = Response(
            status_code=status_code,
            description=description,
            headers=headers or {},
            body=body,
            schema=schema,
            example=example
        )
        action.responses.append(response)
        return response
        
    def build(self) -> str:
        """构建API Blueprint文档"""
        lines = []
        
        # 格式声明
        lines.append(f"FORMAT: {self.format_version}")
        lines.append("")
        
        # 元数据
        for key, value in self.metadata.items():
            lines.append(f"{key}: {value}")
        if self.metadata:
            lines.append("")
            
        # API名称和描述
        lines.append(f"# {self.name}")
        lines.append("")
        
        if self.description:
            lines.append(self.description)
            lines.append("")
            
        # Host
        if self.host:
            lines.append(f"HOST: {self.host}")
            lines.append("")
            
        # 资源组
        for group in self.resource_groups:
            lines.append(f"# Group {group.name}")
            lines.append("")
            
            if group.description:
                lines.append(group.description)
                lines.append("")
                
            for resource in group.resources:
                lines.extend(self._build_resource(resource))
                
        # 未分组的资源
        for resource in self.resources:
            lines.extend(self._build_resource(resource))
            
        return "\n".join(lines)
        
    def _build_resource(self, resource: Resource) -> List[str]:
        """构建资源定义"""
        lines = []
        
        lines.append(f"## {resource.name} [{resource.uri_template}]")
        lines.append("")
        
        if resource.description:
            lines.append(resource.description)
            lines.append("")
            
        # 模型定义
        if resource.model:
            lines.append("### Model")
            lines.append("")
            lines.append("```")
            lines.append(json.dumps(resource.model, indent=2))
            lines.append("```")
            lines.append("")
            
        # 操作
        for action in resource.actions:
            lines.extend(self._build_action(action, resource.uri_template))
            
        return lines
        
    def _build_action(self, action: Action, resource_uri: str) -> List[str]:
        """构建操作定义"""
        lines = []
        
        uri = action.uri_template or resource_uri
        lines.append(f"### {action.name} [{action.method.value} {uri}]")
        lines.append("")
        
        if action.description:
            lines.append(action.description)
            lines.append("")
            
        # 请求
        if action.request:
            lines.extend(self._build_request(action.request))
            
        # 响应
        for response in action.responses:
            lines.extend(self._build_response(response))
            
        return lines
        
    def _build_request(self, request: Request) -> List[str]:
        """构建请求定义"""
        lines = []
        
        if request.description:
            lines.append(request.description)
            lines.append("")
            
        # 参数
        if request.parameters:
            lines.append("+ Parameters")
            for param in request.parameters:
                param_line = f"    + {param.name}"
                
                if param.type_ != ParameterType.STRING:
                    param_line += f" ({param.type_.value})"
                if param.required:
                    param_line += " - required"
                if param.description:
                    param_line += f" - {param.description}"
                if param.example is not None:
                    param_line += f" (e.g., `{param.example}`)"
                    
                lines.append(param_line)
            lines.append("")
            
        # 请求头
        if request.headers:
            lines.append("+ Request")
            for key, value in request.headers.items():
                lines.append(f"    + Headers")
                lines.append(f"")
                lines.append(f"            {key}: {value}")
            lines.append("")
            
        # 请求体
        if request.body or request.example:
            body = request.example or request.body or ""
            lines.append("+ Request (application/json)")
            lines.append("")
            lines.append("    + Body")
            lines.append("")
            lines.append("            " + body.replace("\n", "\n            "))
            lines.append("")
            
        return lines
        
    def _build_response(self, response: Response) -> List[str]:
        """构建响应定义"""
        lines = []
        
        content_type = "application/json"
        if response.headers and "Content-Type" in response.headers:
            content_type = response.headers["Content-Type"]
            
        lines.append(f"+ Response {response.status_code} ({content_type})")
        lines.append("")
        
        if response.description:
            lines.append(f"    {response.description}")
            lines.append("")
            
        # 响应头
        if response.headers:
            lines.append("    + Headers")
            lines.append("")
            for key, value in response.headers.items():
                if key != "Content-Type":
                    lines.append(f"            {key}: {value}")
            lines.append("")
            
        # 响应体
        if response.body or response.example:
            body = response.example or response.body or ""
            lines.append("    + Body")
            lines.append("")
            lines.append("            " + body.replace("\n", "\n            "))
            lines.append("")
            
        return lines


class MockServerGenerator:
    """Mock服务器生成器"""
    
    def __init__(self, blueprint: str):
        self.blueprint = blueprint
        
    def generate_flask_app(self) -> str:
        """生成Flask应用代码"""
        code_lines = [
            "#!/usr/bin/env python3",
            "# -*- coding: utf-8 -*-",
            "\"\"\"Auto-generated Flask Mock Server\"\"\"",
            "",
            "from flask import Flask, jsonify, request",
            "from flask_cors import CORS",
            "",
            "app = Flask(__name__)",
            "CORS(app)",
            "",
            "# Mock data storage",
            "mock_data = {}",
            "",
        ]
        
        # 解析blueprint并生成路由
        routes = self._parse_blueprint()
        
        for route in routes:
            method = route["method"].lower()
            path = route["path"]
            response = route.get("response", {})
            
            code_lines.extend([
                f"@app.route('{path}', methods=['{method.upper()}'])",
                f"def {method}_{path.replace('/', '_').replace('{', '').replace('}', '')}():",
                f"    \"\"\"{route.get('description', '')}\"\"\"",
                f"    response = {json.dumps(response, indent=4)}",
                f"    return jsonify(response), {route.get('status', 200)}",
                "",
            ])
            
        code_lines.extend([
            "",
            "if __name__ == '__main__':",
            "    app.run(debug=True, port=5000)",
        ])
        
        return "\n".join(code_lines)
        
    def generate_express_app(self) -> str:
        """生成Express应用代码"""
        code_lines = [
            "// Auto-generated Express Mock Server",
            "",
            "const express = require('express');",
            "const cors = require('cors');",
            "",
            "const app = express();",
            "app.use(cors());",
            "app.use(express.json());",
            "",
            "// Mock data storage",
            "const mockData = {};",
            "",
        ]
        
        routes = self._parse_blueprint()
        
        for route in routes:
            method = route["method"].lower()
            path = route["path"]
            response = route.get("response", {})
            
            code_lines.extend([
                f"app.{method}('{path}', (req, res) => {{",
                f"    // {route.get('description', '')}",
                f"    res.status({route.get('status', 200)}).json({json.dumps(response)});",
                "});",
                "",
            ])
            
        code_lines.extend([
            "",
            "const PORT = process.env.PORT || 3000;",
            "app.listen(PORT, () => {",
            "    console.log(`Mock server running on port ${PORT}`);",
            "});",
        ])
        
        return "\n".join(code_lines)
        
    def _parse_blueprint(self) -> List[Dict]:
        """解析API Blueprint提取路由信息"""
        routes = []
        
        # 简单的正则解析
        action_pattern = r'###\s+(\w+)\s*\[(\w+)\s+(\S+)\]'
        response_pattern = r'\+\s*Response\s+(\d+)'
        
        actions = re.findall(action_pattern, self.blueprint)
        responses = re.findall(response_pattern, self.blueprint)
        
        for i, (name, method, path) in enumerate(actions):
            route = {
                "name": name,
                "method": method,
                "path": path,
                "status": int(responses[i]) if i < len(responses) else 200,
                "response": {"message": f"Mock response for {name}"}
            }
            routes.append(route)
            
        return routes


class OpenAPIToBlueprintConverter:
    """OpenAPI到API Blueprint转换器"""
    
    def __init__(self, openapi_spec: Dict[str, Any]):
        self.spec = openapi_spec
        
    def convert(self) -> str:
        """转换为API Blueprint格式"""
        info = self.spec.get("info", {})
        title = info.get("title", "API")
        description = info.get("description", "")
        version = info.get("version", "1.0.0")
        
        servers = self.spec.get("servers", [{}])
        host = servers[0].get("url", "https://api.example.com") if servers else "https://api.example.com"
        
        builder = APIBlueprintBuilder(
            name=title,
            description=description,
            host=host
        )
        
        # 添加元数据
        builder.add_metadata("VERSION", version)
        
        # 转换路径
        paths = self.spec.get("paths", {})
        schemas = self.spec.get("components", {}).get("schemas", {})
        
        # 按标签分组
        groups: Dict[str, List] = {}
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method not in ["get", "post", "put", "delete", "patch"]:
                    continue
                    
                tags = operation.get("tags", ["Default"])
                group_name = tags[0]
                
                if group_name not in groups:
                    groups[group_name] = []
                    
                groups[group_name].append({
                    "path": path,
                    "method": method,
                    "operation": operation
                })
                
        # 构建资源组
        for group_name, operations in groups.items():
            group = builder.add_resource_group(
                name=group_name,
                description=f"{group_name} operations"
            )
            
            # 按路径分组
            path_groups: Dict[str, List] = {}
            for op in operations:
                path = op["path"]
                if path not in path_groups:
                    path_groups[path] = []
                path_groups[path].append(op)
                
            for path, path_ops in path_groups.items():
                resource_name = path.strip("/").split("/")[0].capitalize()
                resource = builder.add_resource(
                    name=resource_name,
                    uri_template=path,
                    group=group
                )
                
                for op in path_ops:
                    operation = op["operation"]
                    action = builder.add_action(
                        resource=resource,
                        name=operation.get("summary", op["method"].upper()),
                        method=HttpMethod(op["method"].upper()),
                        description=operation.get("description", "")
                    )
                    
                    # 处理参数
                    parameters = []
                    for param in operation.get("parameters", []):
                        parameters.append(Parameter(
                            name=param.get("name", ""),
                            type_=ParameterType(param.get("schema", {}).get("type", "string")),
                            required=param.get("required", False),
                            description=param.get("description", "")
                        ))
                        
                    # 处理请求体
                    request_body = operation.get("requestBody", {})
                    body_example = None
                    if request_body:
                        content = request_body.get("content", {})
                        if "application/json" in content:
                            schema_ref = content["application/json"].get("schema", {})
                            body_example = self._generate_example_from_schema(schema_ref, schemas)
                            
                    if parameters or body_example:
                        builder.add_request(
                            action=action,
                            parameters=parameters,
                            example=json.dumps(body_example, indent=2) if body_example else None
                        )
                        
                    # 处理响应
                    for code, resp in operation.get("responses", {}).items():
                        resp_example = None
                        if "content" in resp and "application/json" in resp["content"]:
                            schema_ref = resp["content"]["application/json"].get("schema", {})
                            resp_example = self._generate_example_from_schema(schema_ref, schemas)
                            
                        builder.add_response(
                            action=action,
                            status_code=int(code) if code.isdigit() else 200,
                            description=resp.get("description", ""),
                            example=json.dumps(resp_example, indent=2) if resp_example else None
                        )
                        
        return builder.build()
        
    def _generate_example_from_schema(
        self,
        schema_ref: Dict,
        schemas: Dict[str, Any]
    ) -> Any:
        """从Schema生成示例数据"""
        if "$ref" in schema_ref:
            ref_name = schema_ref["$ref"].split("/")[-1]
            schema = schemas.get(ref_name, {})
        else:
            schema = schema_ref
            
        if schema.get("type") == "object":
            example = {}
            for prop_name, prop_schema in schema.get("properties", {}).items():
                prop_type = prop_schema.get("type", "string")
                if prop_type == "string":
                    example[prop_name] = prop_schema.get("example", f"{prop_name}_value")
                elif prop_type == "integer":
                    example[prop_name] = prop_schema.get("example", 1)
                elif prop_type == "boolean":
                    example[prop_name] = prop_schema.get("example", True)
                elif prop_type == "array":
                    example[prop_name] = []
            return example
        elif schema.get("type") == "array":
            return []
            
        return {}


def validate_blueprint(blueprint: str) -> List[str]:
    """验证API Blueprint语法"""
    errors = []
    
    # 检查格式声明
    if not blueprint.startswith("FORMAT:"):
        errors.append("Missing FORMAT declaration")
        
    # 检查API名称
    if not re.search(r'^#\s+\w+', blueprint, re.MULTILINE):
        errors.append("Missing API name")
        
    # 检查资源定义
    resource_pattern = r'##\s+\w+\s*\[\S+\]'
    if not re.search(resource_pattern, blueprint):
        errors.append("No resources defined")
        
    # 检查操作定义
    action_pattern = r'###\s+\w+\s*\[\w+\s+\S+\]'
    if not re.search(action_pattern, blueprint):
        errors.append("No actions defined")
        
    return errors


def export_blueprint(blueprint: str, filepath: str) -> str:
    """导出API Blueprint到文件"""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(blueprint)
        
    return str(path)


def generate_mock_response(
    blueprint: str,
    method: str,
    path: str,
    status_code: Optional[int] = None
) -> Optional[Dict]:
    """从Blueprint生成Mock响应"""
    # 查找匹配的action
    action_pattern = rf'###\s+\w+\s*\[{method.upper()}\s+{re.escape(path)}\]'
    
    if not re.search(action_pattern, blueprint, re.IGNORECASE):
        return None
        
    # 查找响应
    if status_code:
        response_pattern = rf'\+\s*Response\s+{status_code}'
    else:
        response_pattern = r'\+\s*Response\s+(\d+)'
        
    match = re.search(response_pattern, blueprint)
    if match:
        return {
            "status": int(match.group(1)),
            "body": {"message": "Mock response generated from blueprint"}
        }
        
    return {"status": 200, "body": {"message": "Default mock response"}}


# Kimi CLI 入口点
def run(args: Optional[List[str]] = None) -> Dict[str, Any]:
    """Kimi CLI 入口函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="API Blueprint Skill")
    parser.add_argument("action", choices=["create", "convert", "mock", "validate"],
                       help="Action to perform")
    parser.add_argument("--name", "-n", default="API", help="API name")
    parser.add_argument("--input", "-i", help="Input file path")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--host", default="https://api.example.com", help="API host")
    parser.add_argument("--framework", default="flask", choices=["flask", "express"],
                       help="Mock server framework")
    
    parsed = parser.parse_args(args)
    
    result = {"success": True, "action": parsed.action}
    
    try:
        if parsed.action == "create":
            # 创建基本Blueprint
            builder = APIBlueprintBuilder(
                name=parsed.name,
                description=f"{parsed.name} API Documentation",
                host=parsed.host
            )
            
            # 添加示例资源
            group = builder.add_resource_group("Users", "User management")
            resource = builder.add_resource(
                name="User",
                uri_template="/users/{id}",
                description="A single user resource",
                group=group
            )
            
            action = builder.add_action(
                resource=resource,
                name="Get User",
                method=HttpMethod.GET,
                description="Retrieve a single user"
            )
            
            builder.add_request(
                action=action,
                parameters=[Parameter(name="id", type_=ParameterType.STRING, required=True)]
            )
            
            builder.add_response(
                action=action,
                status_code=200,
                description="User found",
                example=json.dumps({"id": "1", "name": "John"}, indent=2)
            )
            
            blueprint = builder.build()
            
            if parsed.output:
                export_blueprint(blueprint, parsed.output)
                result["output_file"] = parsed.output
            else:
                result["blueprint"] = blueprint
                
        elif parsed.action == "convert":
            if not parsed.input:
                raise ValueError("--input is required for convert")
                
            with open(parsed.input, 'r', encoding='utf-8') as f:
                if parsed.input.endswith('.yaml') or parsed.input.endswith('.yml'):
                    import yaml
                    spec = yaml.safe_load(f)
                else:
                    spec = json.load(f)
                    
            converter = OpenAPIToBlueprintConverter(spec)
            blueprint = converter.convert()
            
            output_path = parsed.output or f"{parsed.name}.apib"
            export_blueprint(blueprint, output_path)
            result["output_file"] = output_path
            
        elif parsed.action == "mock":
            if not parsed.input:
                raise ValueError("--input is required for mock generation")
                
            with open(parsed.input, 'r', encoding='utf-8') as f:
                blueprint = f.read()
                
            generator = MockServerGenerator(blueprint)
            
            if parsed.framework == "flask":
                code = generator.generate_flask_app()
                ext = "py"
            else:
                code = generator.generate_express_app()
                ext = "js"
                
            output_path = parsed.output or f"mock_server.{ext}"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(code)
                
            result["output_file"] = output_path
            
        elif parsed.action == "validate":
            if not parsed.input:
                raise ValueError("--input is required for validation")
                
            with open(parsed.input, 'r', encoding='utf-8') as f:
                blueprint = f.read()
                
            errors = validate_blueprint(blueprint)
            result["valid"] = len(errors) == 0
            result["errors"] = errors
            
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
