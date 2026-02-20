#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Postman Collection Skill

功能：Postman集合管理工具
- 集合导入导出
- 环境管理
- 测试脚本生成
- OpenAPI转Postman集合

Use when documenting APIs, generating documentation, or when user mentions 'OpenAPI', 'Swagger', 'API docs'.
"""

import json
import os
import re
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid


@dataclass
class PostmanVariable:
    """Postman变量定义"""
    key: str
    value: Any = ""
    type_: str = "string"
    name: str = ""
    description: str = ""
    enabled: bool = True


@dataclass
class PostmanHeader:
    """Postman请求头"""
    key: str
    value: str
    type_: str = "text"
    description: str = ""
    disabled: bool = False


@dataclass
class PostmanUrl:
    """Postman URL定义"""
    raw: str
    protocol: str = "https"
    host: List[str] = field(default_factory=list)
    port: str = ""
    path: List[str] = field(default_factory=list)
    query: List[Dict[str, Any]] = field(default_factory=list)
    variable: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PostmanRequest:
    """Postman请求定义"""
    method: str = "GET"
    url: Union[str, PostmanUrl, Dict] = ""
    header: List[PostmanHeader] = field(default_factory=list)
    body: Optional[Dict[str, Any]] = None
    description: str = ""


@dataclass
class PostmanResponse:
    """Postman响应定义"""
    name: str = ""
    originalRequest: Optional[Dict] = None
    status: str = ""
    code: int = 200
    header: List[Dict] = field(default_factory=list)
    body: str = ""


@dataclass
class PostmanItem:
    """Postman集合项（请求或文件夹）"""
    name: str
    item: Optional[List["PostmanItem"]] = None
    request: Optional[PostmanRequest] = None
    response: List[PostmanResponse] = field(default_factory=list)
    event: List[Dict] = field(default_factory=list)
    description: str = ""


@dataclass
class PostmanAuth:
    """Postman认证配置"""
    type_: str = "noauth"
    bearer: List[Dict] = field(default_factory=list)
    basic: List[Dict] = field(default_factory=list)
    apikey: List[Dict] = field(default_factory=list)


class PostmanCollectionBuilder:
    """Postman集合构建器"""
    
    SCHEMA = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    
    def __init__(self, name: str = "New Collection", description: str = ""):
        self.info = {
            "_postman_id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "schema": self.SCHEMA
        }
        self.item: List[PostmanItem] = []
        self.variable: List[PostmanVariable] = []
        self.auth: Optional[PostmanAuth] = None
        self.event: List[Dict] = []
        
    def add_folder(
        self, 
        name: str, 
        description: str = "",
        items: Optional[List[PostmanItem]] = None
    ) -> "PostmanCollectionBuilder":
        """添加文件夹"""
        folder = PostmanItem(
            name=name,
            description=description,
            item=items or []
        )
        self.item.append(folder)
        return self
        
    def add_request(
        self,
        name: str,
        method: str = "GET",
        url: str = "",
        headers: Optional[List[PostmanHeader]] = None,
        body: Optional[Dict] = None,
        description: str = "",
        responses: Optional[List[PostmanResponse]] = None,
        tests: Optional[str] = None,
        folder: Optional[str] = None
    ) -> "PostmanCollectionBuilder":
        """添加请求"""
        # 解析URL
        url_obj = self._parse_url(url)
        
        request = PostmanRequest(
            method=method.upper(),
            url=url_obj,
            header=headers or [],
            body=body,
            description=description
        )
        
        item = PostmanItem(
            name=name,
            request=request,
            response=responses or []
        )
        
        # 添加测试脚本
        if tests:
            item.event.append({
                "listen": "test",
                "script": {
                    "exec": tests.split('\n') if isinstance(tests, str) else tests,
                    "type": "text/javascript"
                }
            })
            
        # 添加到文件夹或根级
        if folder:
            folder_item = self._find_or_create_folder(folder)
            folder_item.item.append(item)
        else:
            self.item.append(item)
            
        return self
        
    def add_variable(
        self,
        key: str,
        value: Any,
        var_type: str = "string",
        description: str = ""
    ) -> "PostmanCollectionBuilder":
        """添加集合变量"""
        self.variable.append(PostmanVariable(
            key=key,
            value=value,
            type_=var_type,
            name=key,
            description=description
        ))
        return self
        
    def set_auth(
        self,
        auth_type: str,
        **kwargs
    ) -> "PostmanCollectionBuilder":
        """设置认证方式"""
        auth = PostmanAuth(type_=auth_type)
        
        if auth_type == "bearer":
            auth.bearer = [{"key": "token", "value": kwargs.get("token", ""), "type": "string"}]
        elif auth_type == "basic":
            auth.basic = [
                {"key": "username", "value": kwargs.get("username", ""), "type": "string"},
                {"key": "password", "value": kwargs.get("password", ""), "type": "string"}
            ]
        elif auth_type == "apikey":
            auth.apikey = [
                {"key": "key", "value": kwargs.get("key", ""), "type": "string"},
                {"key": "value", "value": kwargs.get("value", ""), "type": "string"},
                {"key": "in", "value": kwargs.get("in_", "header"), "type": "string"}
            ]
            
        self.auth = auth
        return self
        
    def add_prerequest_script(self, script: str) -> "PostmanCollectionBuilder":
        """添加前置脚本"""
        self.event.append({
            "listen": "prerequest",
            "script": {
                "exec": script.split('\n') if isinstance(script, str) else script,
                "type": "text/javascript"
            }
        })
        return self
        
    def _parse_url(self, url: str) -> PostmanUrl:
        """解析URL字符串"""
        # 处理变量占位符
        url = url.replace("{{", "").replace("}}", "")
        
        # 解析协议
        protocol = "https"
        if "://" in url:
            protocol, url = url.split("://", 1)
            
        # 解析主机和路径
        parts = url.split("/", 1)
        host = parts[0].split(".")
        path = parts[1].split("/") if len(parts) > 1 else []
        
        # 处理路径变量
        url_variables = []
        for segment in path:
            if segment.startswith(":"):
                var_name = segment[1:]
                url_variables.append({"key": var_name, "value": ""})
                
        return PostmanUrl(
            raw=f"{{{{{protocol}}}}://{{{host[0]}}}}/{'/'.join(path)}",
            protocol=protocol,
            host=[f"{{{{{h}}}}}" for h in host],
            path=path,
            variable=url_variables
        )
        
    def _find_or_create_folder(self, name: str) -> PostmanItem:
        """查找或创建文件夹"""
        for item in self.item:
            if item.name == name and item.item is not None:
                return item
                
        # 创建新文件夹
        folder = PostmanItem(name=name, item=[])
        self.item.append(folder)
        return folder
        
    def build(self) -> Dict[str, Any]:
        """构建Postman集合"""
        collection = {"info": self.info, "item": []}
        
        # 处理item
        for item in self.item:
            collection["item"].append(self._serialize_item(item))
            
        # 添加变量
        if self.variable:
            collection["variable"] = [
                {
                    "key": v.key,
                    "value": v.value,
                    "type": v.type_,
                    "name": v.name or v.key,
                    "description": v.description
                }
                for v in self.variable
            ]
            
        # 添加认证
        if self.auth:
            collection["auth"] = self._serialize_auth(self.auth)
            
        # 添加事件
        if self.event:
            collection["event"] = self.event
            
        return collection
        
    def _serialize_item(self, item: PostmanItem) -> Dict[str, Any]:
        """序列化集合项"""
        result = {"name": item.name}
        
        if item.description:
            result["description"] = item.description
            
        if item.item is not None:
            # 这是一个文件夹
            result["item"] = [self._serialize_item(i) for i in item.item]
        else:
            # 这是一个请求
            if item.request:
                result["request"] = self._serialize_request(item.request)
            if item.response:
                result["response"] = [self._serialize_response(r) for r in item.response]
            if item.event:
                result["event"] = item.event
                
        return result
        
    def _serialize_request(self, request: PostmanRequest) -> Dict[str, Any]:
        """序列化请求"""
        result = {
            "method": request.method,
            "header": [
                {"key": h.key, "value": h.value, "type": h.type_}
                for h in request.header
            ]
        }
        
        if isinstance(request.url, PostmanUrl):
            result["url"] = {
                "raw": request.url.raw,
                "protocol": request.url.protocol,
                "host": request.url.host,
                "path": request.url.path
            }
            if request.url.variable:
                result["url"]["variable"] = request.url.variable
        else:
            result["url"] = request.url
            
        if request.body:
            result["body"] = request.body
            
        if request.description:
            result["description"] = request.description
            
        return result
        
    def _serialize_response(self, response: PostmanResponse) -> Dict[str, Any]:
        """序列化响应"""
        result = {
            "name": response.name,
            "originalRequest": response.originalRequest or {},
            "status": response.status,
            "code": response.code,
            "header": response.header,
            "body": response.body
        }
        return result
        
    def _serialize_auth(self, auth: PostmanAuth) -> Dict[str, Any]:
        """序列化认证配置"""
        result = {"type": auth.type_}
        
        if auth.type_ == "bearer":
            result["bearer"] = auth.bearer
        elif auth.type_ == "basic":
            result["basic"] = auth.basic
        elif auth.type_ == "apikey":
            result["apikey"] = auth.apikey
            
        return result


class PostmanEnvironmentBuilder:
    """Postman环境构建器"""
    
    SCHEMA = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    
    def __init__(self, name: str = "New Environment", environment_type: str = "default"):
        self.id = str(uuid.uuid4())
        self.name = name
        self._postman_variable_scope = environment_type
        self._postman_exported_at = datetime.utcnow().isoformat()
        self._postman_exported_using = "Postman/10.0"
        self.values: List[PostmanVariable] = []
        
    def add_variable(
        self,
        key: str,
        value: Any,
        var_type: str = "string",
        enabled: bool = True
    ) -> "PostmanEnvironmentBuilder":
        """添加环境变量"""
        self.values.append(PostmanVariable(
            key=key,
            value=value,
            type_=var_type,
            enabled=enabled
        ))
        return self
        
    def build(self) -> Dict[str, Any]:
        """构建环境配置"""
        return {
            "id": self.id,
            "name": self.name,
            "_postman_variable_scope": self._postman_variable_scope,
            "_postman_exported_at": self._postman_exported_at,
            "_postman_exported_using": self._postman_exported_using,
            "values": [
                {
                    "key": v.key,
                    "value": v.value,
                    "type": v.type_,
                    "enabled": v.enabled
                }
                for v in self.values
            ]
        }


class OpenAPIToPostmanConverter:
    """OpenAPI到Postman集合转换器"""
    
    def __init__(self, openapi_spec: Dict[str, Any]):
        self.spec = openapi_spec
        
    def convert(self, base_url: Optional[str] = None) -> Dict[str, Any]:
        """转换为Postman集合"""
        info = self.spec.get("info", {})
        title = info.get("title", "API")
        description = info.get("description", "")
        
        builder = PostmanCollectionBuilder(name=title, description=description)
        
        # 设置基础URL
        servers = self.spec.get("servers", [])
        if servers:
            base_url = base_url or servers[0].get("url", "http://localhost")
            # 解析base_url中的变量
            matches = re.findall(r'\{([^}]+)\}', base_url)
            for match in matches:
                builder.add_variable(match, "", "string")
                
        # 添加安全方案作为认证
        security_schemes = self.spec.get("components", {}).get("securitySchemes", {})
        for scheme_name, scheme in security_schemes.items():
            if scheme.get("type") == "http" and scheme.get("scheme") == "bearer":
                builder.set_auth("bearer", token=f"{{{{{scheme_name}}}}")
                builder.add_variable(scheme_name, "your_token_here")
            elif scheme.get("type") == "apiKey":
                builder.add_variable(scheme_name, "your_api_key")
                
        # 转换路径
        paths = self.spec.get("paths", {})
        schemas = self.spec.get("components", {}).get("schemas", {})
        
        for path, path_item in paths.items():
            # 按tag分组
            folder_name = "Default"
            
            for method, operation in path_item.items():
                if method not in ["get", "post", "put", "delete", "patch", "head", "options"]:
                    continue
                    
                summary = operation.get("summary", f"{method.upper()} {path}")
                operation_id = operation.get("operationId", "")
                tags = operation.get("tags", [])
                
                if tags:
                    folder_name = tags[0]
                    
                # 构建URL
                url = f"{base_url}{path}"
                
                # 处理参数
                headers = []
                parameters = operation.get("parameters", [])
                
                for param in parameters:
                    param_in = param.get("in")
                    if param_in == "header":
                        headers.append(PostmanHeader(
                            key=param.get("name"),
                            value=f"{{{{{param.get('name')}}}}}"
                        ))
                    elif param_in == "query":
                        # 添加到URL
                        url += f"?{param.get('name')}={{{{param.get('name')}}}"
                        
                # 处理请求体
                body = None
                request_body = operation.get("requestBody", {})
                if request_body:
                    content = request_body.get("content", {})
                    if "application/json" in content:
                        schema_ref = content["application/json"].get("schema", {})
                        body = self._generate_body_from_schema(schema_ref, schemas)
                        
                # 生成测试脚本
                tests = self._generate_test_script(operation.get("responses", {}))
                
                builder.add_request(
                    name=summary,
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    body=body,
                    description=operation.get("description", ""),
                    tests=tests,
                    folder=folder_name
                )
                
        return builder.build()
        
    def _generate_body_from_schema(
        self, 
        schema_ref: Dict[str, Any], 
        schemas: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """从Schema生成示例请求体"""
        if "$ref" in schema_ref:
            ref = schema_ref["$ref"].split("/")[-1]
            schema = schemas.get(ref, {})
        else:
            schema = schema_ref
            
        if schema.get("type") == "object":
            properties = schema.get("properties", {})
            example = {}
            
            for prop_name, prop_schema in properties.items():
                prop_type = prop_schema.get("type", "string")
                
                if prop_type == "string":
                    example[prop_name] = prop_schema.get("example", f"{prop_name}_value")
                elif prop_type == "integer":
                    example[prop_name] = prop_schema.get("example", 0)
                elif prop_type == "boolean":
                    example[prop_name] = prop_schema.get("example", True)
                elif prop_type == "array":
                    example[prop_name] = []
                elif prop_type == "object":
                    example[prop_name] = {}
                    
            return {
                "mode": "raw",
                "raw": json.dumps(example, indent=2),
                "options": {"raw": {"language": "json"}}
            }
            
        return None
        
    def _generate_test_script(self, responses: Dict[str, Any]) -> str:
        """生成测试脚本"""
        tests = ["// Test script generated automatically", ""]
        
        # 检查状态码
        for code in responses.keys():
            if code.isdigit():
                tests.append(f"// Test for status code {code}")
                tests.append(f"pm.test('Status code is {code}', function () {{")
                tests.append(f"    pm.response.to.have.status({code});")
                tests.append("});")
                tests.append("")
                
        # JSON Schema验证
        tests.append("// Validate JSON response")
        tests.append("pm.test('Response has valid JSON', function () {")
        tests.append("    pm.response.to.be.json;")
        tests.append("});")
        
        return "\n".join(tests)


def export_collection(collection: Dict[str, Any], filepath: str) -> str:
    """导出集合到文件"""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(collection, f, indent=2, ensure_ascii=False)
        
    return str(path)


def import_collection(filepath: str) -> Dict[str, Any]:
    """从文件导入集合"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_test_script(
    assertions: List[str],
    variables: Optional[List[str]] = None
) -> str:
    """生成Postman测试脚本"""
    lines = ["// Auto-generated test script", ""]
    
    # 状态码断言
    if "status_ok" in assertions:
        lines.extend([
            "pm.test('Status code is 200', function () {",
            "    pm.response.to.have.status(200);",
            "});",
            ""
        ])
        
    # JSON验证
    if "is_json" in assertions:
        lines.extend([
            "pm.test('Response is JSON', function () {",
            "    pm.response.to.be.json;",
            "});",
            ""
        ])
        
    # 响应时间
    if "response_time" in assertions:
        lines.extend([
            "pm.test('Response time is acceptable', function () {",
            "    pm.expect(pm.response.responseTime).to.be.below(500);",
            "});",
            ""
        ])
        
    # 设置环境变量
    if variables:
        for var in variables:
            lines.extend([
                f"// Set environment variable: {var}",
                f"pm.environment.set('{var}', pm.response.json().{var});",
                ""
            ])
            
    return "\n".join(lines)


# Kimi CLI 入口点
def run(args: Optional[List[str]] = None) -> Dict[str, Any]:
    """Kimi CLI 入口函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Postman Collection Skill")
    parser.add_argument("action", choices=["create", "convert", "export", "test"],
                       help="Action to perform")
    parser.add_argument("--name", "-n", default="New Collection", help="Collection name")
    parser.add_argument("--input", "-i", help="Input file path")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--url", "-u", help="Base URL")
    parser.add_argument("--format", "-f", default="json", help="Output format")
    
    parsed = parser.parse_args(args)
    
    result = {"success": True, "action": parsed.action}
    
    try:
        if parsed.action == "create":
            # 创建新集合
            builder = PostmanCollectionBuilder(name=parsed.name)
            
            if parsed.url:
                builder.add_variable("baseUrl", parsed.url)
                
            collection = builder.build()
            
            if parsed.output:
                export_collection(collection, parsed.output)
                result["output_file"] = parsed.output
            else:
                result["collection"] = collection
                
        elif parsed.action == "convert":
            # 从OpenAPI转换
            if not parsed.input:
                raise ValueError("--input is required for convert")
                
            with open(parsed.input, 'r', encoding='utf-8') as f:
                if parsed.input.endswith('.yaml') or parsed.input.endswith('.yml'):
                    import yaml
                    openapi_spec = yaml.safe_load(f)
                else:
                    openapi_spec = json.load(f)
                    
            converter = OpenAPIToPostmanConverter(openapi_spec)
            collection = converter.convert(base_url=parsed.url)
            
            output_path = parsed.output or f"{parsed.name}.postman_collection.json"
            export_collection(collection, output_path)
            result["output_file"] = output_path
            
        elif parsed.action == "export":
            # 导出环境配置
            builder = PostmanEnvironmentBuilder(name=parsed.name)
            
            if parsed.url:
                builder.add_variable("baseUrl", parsed.url)
                
            env = builder.build()
            output_path = parsed.output or f"{parsed.name}.postman_environment.json"
            export_collection(env, output_path)
            result["output_file"] = output_path
            
        elif parsed.action == "test":
            # 生成测试脚本
            tests = generate_test_script(["status_ok", "is_json", "response_time"])
            
            if parsed.output:
                with open(parsed.output, 'w', encoding='utf-8') as f:
                    f.write(tests)
                result["output_file"] = parsed.output
            else:
                result["test_script"] = tests
                
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
