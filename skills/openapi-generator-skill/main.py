#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAPI Generator Skill

功能：OpenAPI/Swagger文档生成工具
- 从代码生成OpenAPI文档
- 支持文档渲染和预览
- 客户端SDK代码生成
- API规范验证

Use when documenting APIs, generating documentation, or when user mentions 'OpenAPI', 'Swagger', 'API docs'.
"""

import json
import yaml
import os
import re
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, field, asdict
from datetime import datetime
import inspect
import textwrap


@dataclass
class OpenAPIInfo:
    """OpenAPI基本信息"""
    title: str = "API"
    version: str = "1.0.0"
    description: str = ""
    terms_of_service: Optional[str] = None
    contact: Dict[str, str] = field(default_factory=dict)
    license: Dict[str, str] = field(default_factory=dict)


@dataclass
class OpenAPIServer:
    """OpenAPI服务器配置"""
    url: str
    description: str = ""
    variables: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIParameter:
    """API参数定义"""
    name: str
    in_: str  # query, path, header, cookie
    required: bool = False
    type_: str = "string"
    description: str = ""
    default: Any = None


@dataclass
class APIResponse:
    """API响应定义"""
    code: str
    description: str
    schema: Optional[Dict[str, Any]] = None
    examples: Optional[Dict[str, Any]] = None


@dataclass
class APIOperation:
    """API操作定义"""
    method: str
    path: str
    summary: str = ""
    description: str = ""
    operation_id: str = ""
    tags: List[str] = field(default_factory=list)
    parameters: List[APIParameter] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: List[APIResponse] = field(default_factory=list)
    security: List[Dict[str, List[str]]] = field(default_factory=list)


class OpenAPISpecBuilder:
    """OpenAPI规范构建器"""
    
    def __init__(self, openapi_version: str = "3.0.3"):
        self.openapi_version = openapi_version
        self.info: Optional[OpenAPIInfo] = None
        self.servers: List[OpenAPIServer] = []
        self.paths: Dict[str, Dict[str, Any]] = {}
        self.components: Dict[str, Any] = {
            "schemas": {},
            "responses": {},
            "parameters": {},
            "securitySchemes": {}
        }
        self.tags: List[Dict[str, str]] = []
        self.security: List[Dict[str, List[str]]] = []
        
    def set_info(self, info: OpenAPIInfo) -> "OpenAPISpecBuilder":
        """设置API基本信息"""
        self.info = info
        return self
        
    def add_server(self, server: OpenAPIServer) -> "OpenAPISpecBuilder":
        """添加服务器配置"""
        self.servers.append(server)
        return self
        
    def add_tag(self, name: str, description: str = "") -> "OpenAPISpecBuilder":
        """添加API标签"""
        self.tags.append({"name": name, "description": description})
        return self
        
    def add_schema(self, name: str, schema: Dict[str, Any]) -> "OpenAPISpecBuilder":
        """添加组件schema"""
        self.components["schemas"][name] = schema
        return self
        
    def add_security_scheme(
        self, 
        name: str, 
        type_: str,
        scheme: Optional[str] = None,
        bearer_format: Optional[str] = None,
        flows: Optional[Dict] = None,
        api_key_location: Optional[str] = None,
        api_key_name: Optional[str] = None
    ) -> "OpenAPISpecBuilder":
        """添加安全方案"""
        security_scheme = {"type": type_}
        
        if scheme:
            security_scheme["scheme"] = scheme
        if bearer_format:
            security_scheme["bearerFormat"] = bearer_format
        if flows:
            security_scheme["flows"] = flows
        if api_key_location and api_key_name:
            security_scheme["in"] = api_key_location
            security_scheme["name"] = api_key_name
            
        self.components["securitySchemes"][name] = security_scheme
        return self
        
    def add_operation(self, operation: APIOperation) -> "OpenAPISpecBuilder":
        """添加API操作"""
        if operation.path not in self.paths:
            self.paths[operation.path] = {}
            
        path_item = {
            "summary": operation.summary,
            "description": operation.description,
            "operationId": operation.operation_id or self._generate_operation_id(operation),
            "tags": operation.tags,
        }
        
        # 添加参数
        if operation.parameters:
            path_item["parameters"] = [
                {
                    "name": p.name,
                    "in": p.in_,
                    "required": p.required,
                    "schema": {"type": p.type_},
                    "description": p.description
                }
                for p in operation.parameters
            ]
            
        # 添加请求体
        if operation.request_body:
            path_item["requestBody"] = operation.request_body
            
        # 添加响应
        path_item["responses"] = {
            resp.code: {
                "description": resp.description,
                **({"content": {"application/json": {"schema": resp.schema}}} if resp.schema else {})
            }
            for resp in operation.responses
        }
        
        # 添加安全
        if operation.security:
            path_item["security"] = operation.security
            
        self.paths[operation.path][operation.method.lower()] = path_item
        return self
        
    def _generate_operation_id(self, operation: APIOperation) -> str:
        """生成操作ID"""
        path_clean = re.sub(r'[{}]', '', operation.path).replace('/', '_').strip('_')
        return f"{operation.method.lower()}_{path_clean}"
        
    def build(self) -> Dict[str, Any]:
        """构建完整的OpenAPI规范"""
        spec = {
            "openapi": self.openapi_version,
            "info": {
                "title": self.info.title if self.info else "API",
                "version": self.info.version if self.info else "1.0.0",
            }
        }
        
        if self.info:
            if self.info.description:
                spec["info"]["description"] = self.info.description
            if self.info.terms_of_service:
                spec["info"]["termsOfService"] = self.info.terms_of_service
            if self.info.contact:
                spec["info"]["contact"] = self.info.contact
            if self.info.license:
                spec["info"]["license"] = self.info.license
                
        if self.servers:
            spec["servers"] = [
                {"url": s.url, **({"description": s.description} if s.description else {})}
                for s in self.servers
            ]
            
        if self.tags:
            spec["tags"] = self.tags
            
        spec["paths"] = self.paths
        spec["components"] = self.components
        
        if self.security:
            spec["security"] = self.security
            
        return spec


class CodeAnalyzer:
    """代码分析器 - 从Python代码提取API信息"""
    
    @staticmethod
    def analyze_function(func) -> Dict[str, Any]:
        """分析函数签名提取参数信息"""
        sig = inspect.signature(func)
        parameters = []
        
        for name, param in sig.parameters.items():
            if name == 'self':
                continue
                
            param_info = {
                "name": name,
                "in": "query",
                "required": param.default is inspect.Parameter.empty,
                "schema": {"type": CodeAnalyzer._get_type_hint(param.annotation)}
            }
            
            if param.default is not inspect.Parameter.empty and param.default is not None:
                param_info["schema"]["default"] = param.default
                
            parameters.append(param_info)
            
        # 解析返回类型
        return_type = CodeAnalyzer._get_type_hint(sig.return_annotation)
        
        return {
            "parameters": parameters,
            "return_type": return_type
        }
        
    @staticmethod
    def _get_type_hint(annotation) -> str:
        """获取类型提示字符串"""
        if annotation is inspect.Parameter.empty:
            return "string"
            
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object"
        }
        
        return type_map.get(annotation, "string")


class ClientGenerator:
    """客户端代码生成器"""
    
    TEMPLATES = {
        "python": '''
import requests
from typing import Optional, Dict, Any

class {{client_name}}:
    """{{description}}"""
    
    def __init__(self, base_url: str = "{{base_url}}", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"
    
    {% for method in methods %}
    def {{method.name}}(self{% for param in method.params %}, {{param.name}}: {{param.type}}{% if not param.required %} = None{% endif %}{% endfor %}) -> Dict[str, Any]:
        """
        {{method.summary}}
        
        {% if method.params %}Args:{% endif %}
        {% for param in method.params %}
            {{param.name}}: {{param.description}}
        {% endfor %}
        """
        url = f"{self.base_url}{{method.path}}"
        {% if method.has_query_params %}
        params = { {% for param in method.query_params %}"{{param.name}}": {{param.name}}{% if not loop.last %}, {% endif %}{% endfor %} }
        {% endif %}
        response = self.session.{{method.http_method}}(url{% if method.has_query_params %}, params=params{% endif %})
        response.raise_for_status()
        return response.json()
    
    {% endfor %}
''',
        "javascript": '''
class {{client_name}} {
    constructor(baseUrl = "{{base_url}}", apiKey = null) {
        this.baseUrl = baseUrl.replace(/\\/$/, '');
        this.apiKey = apiKey;
        this.headers = {
            'Content-Type': 'application/json'
        };
        if (apiKey) {
            this.headers['Authorization'] = `Bearer ${apiKey}`;
        }
    }
    
    {% for method in methods %}
    async {{method.name}}({% for param in method.params %}{{param.name}}{% if not loop.last %}, {% endif %}{% endfor %}) {
        const url = `${this.baseUrl}{{method.path}}`;
        {% if method.has_query_params %}
        const params = new URLSearchParams();
        {% for param in method.query_params %}
        if ({{param.name}}) params.append('{{param.name}}', {{param.name}});
        {% endfor %}
        {% endif %}
        const response = await fetch(url, {
            method: '{{method.http_method.upper()}}',
            headers: this.headers,
            {% if method.has_query_params %}
            params: params
            {% endif %}
        });
        return response.json();
    }
    {% endfor %}
}

module.exports = {{client_name}};
'''
    }
    
    def __init__(self, spec: Dict[str, Any]):
        self.spec = spec
        
    def generate(self, language: str, client_name: Optional[str] = None) -> str:
        """生成客户端代码"""
        if language not in self.TEMPLATES:
            raise ValueError(f"Unsupported language: {language}")
            
        template = self.TEMPLATES[language]
        
        # 提取方法信息
        methods = []
        for path, path_item in self.spec.get("paths", {}).items():
            for http_method, operation in path_item.items():
                if http_method in ["get", "post", "put", "delete", "patch"]:
                    method_info = self._extract_method_info(path, http_method, operation)
                    methods.append(method_info)
                    
        # 渲染模板
        from jinja2 import Template
        jinja_template = Template(template)
        
        return jinja_template.render(
            client_name=client_name or "APIClient",
            base_url=self.spec.get("servers", [{}])[0].get("url", "http://localhost"),
            description=self.spec.get("info", {}).get("description", ""),
            methods=methods
        )
        
    def _extract_method_info(self, path: str, http_method: str, operation: Dict) -> Dict:
        """提取方法信息"""
        params = []
        query_params = []
        
        for param in operation.get("parameters", []):
            param_info = {
                "name": param["name"],
                "type": self._map_type(param.get("schema", {}).get("type", "string")),
                "required": param.get("required", False),
                "description": param.get("description", "")
            }
            params.append(param_info)
            
            if param.get("in") == "query":
                query_params.append(param_info)
                
        return {
            "name": operation.get("operationId", f"{http_method}_{path.replace('/', '_')}"),
            "http_method": http_method,
            "path": path,
            "summary": operation.get("summary", ""),
            "params": params,
            "query_params": query_params,
            "has_query_params": len(query_params) > 0
        }
        
    def _map_type(self, openapi_type: str, language: str = "python") -> str:
        """映射OpenAPI类型到目标语言类型"""
        type_maps = {
            "python": {
                "string": "str",
                "integer": "int",
                "number": "float",
                "boolean": "bool",
                "array": "list",
                "object": "dict"
            },
            "javascript": {
                "string": "string",
                "integer": "number",
                "number": "number",
                "boolean": "boolean",
                "array": "Array",
                "object": "Object"
            }
        }
        
        return type_maps.get(language, type_maps["python"]).get(openapi_type, "Any")


def generate_from_code(
    module,
    title: str,
    version: str = "1.0.0",
    base_url: str = "http://localhost:8000"
) -> Dict[str, Any]:
    """从Python模块生成OpenAPI规范"""
    builder = OpenAPISpecBuilder()
    builder.set_info(OpenAPIInfo(title=title, version=version))
    builder.add_server(OpenAPIServer(url=base_url))
    
    # 分析模块中的类和方法
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            # 为每个类创建一个tag
            builder.add_tag(name=name, description=f"{name} operations")
            
            # 分析类中的方法
            for method_name, method in inspect.getmembers(obj):
                if inspect.isfunction(method) and not method_name.startswith('_'):
                    analysis = CodeAnalyzer.analyze_function(method)
                    
                    operation = APIOperation(
                        method="GET",
                        path=f"/{name.lower()}/{method_name}",
                        summary=f"{method_name} operation",
                        operation_id=f"{name.lower()}_{method_name}",
                        tags=[name],
                        parameters=[APIParameter(
                            name=p["name"],
                            in_=p["in"],
                            required=p["required"],
                            type_=p["schema"]["type"]
                        ) for p in analysis["parameters"]],
                        responses=[APIResponse(
                            code="200",
                            description="Success",
                            schema={"type": analysis["return_type"]}
                        )]
                    )
                    builder.add_operation(operation)
                    
    return builder.build()


def export_spec(spec: Dict[str, Any], filepath: str, format_: str = "json") -> str:
    """导出OpenAPI规范到文件"""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if format_.lower() == "json":
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
    elif format_.lower() in ["yaml", "yml"]:
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(spec, f, default_flow_style=False, allow_unicode=True)
    else:
        raise ValueError(f"Unsupported format: {format_}")
        
    return str(path)


def validate_spec(spec: Dict[str, Any]) -> List[str]:
    """验证OpenAPI规范"""
    errors = []
    
    # 检查必需字段
    if "openapi" not in spec:
        errors.append("Missing 'openapi' field")
    if "info" not in spec:
        errors.append("Missing 'info' field")
    else:
        if "title" not in spec["info"]:
            errors.append("Missing 'info.title' field")
        if "version" not in spec["info"]:
            errors.append("Missing 'info.version' field")
            
    # 检查路径
    if "paths" not in spec or not spec["paths"]:
        errors.append("No paths defined")
        
    # 验证路径项
    for path, path_item in spec.get("paths", {}).items():
        if not path.startswith('/'):
            errors.append(f"Path must start with '/': {path}")
            
        for method, operation in path_item.items():
            if method not in ["get", "post", "put", "delete", "patch", "head", "options", "trace"]:
                continue
                
            if "responses" not in operation:
                errors.append(f"Missing responses for {method.upper()} {path}")
                
    return errors


# Kimi CLI 入口点
def run(args: Optional[List[str]] = None) -> Dict[str, Any]:
    """Kimi CLI 入口函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenAPI Generator Skill")
    parser.add_argument("action", choices=["generate", "validate", "export", "client"],
                       help="Action to perform")
    parser.add_argument("--input", "-i", help="Input file or module")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--format", "-f", default="json", choices=["json", "yaml"],
                       help="Output format")
    parser.add_argument("--language", "-l", default="python",
                       choices=["python", "javascript"],
                       help="Client language")
    parser.add_argument("--title", "-t", default="API", help="API title")
    parser.add_argument("--version", "-v", default="1.0.0", help="API version")
    
    parsed = parser.parse_args(args)
    
    result = {"success": True, "action": parsed.action}
    
    try:
        if parsed.action == "generate":
            # 从代码生成
            if parsed.input:
                # 动态导入模块
                import importlib.util
                spec = importlib.util.spec_from_file_location("module", parsed.input)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                openapi_spec = generate_from_code(
                    module,
                    title=parsed.title,
                    version=parsed.version
                )
            else:
                # 创建基础模板
                builder = OpenAPISpecBuilder()
                builder.set_info(OpenAPIInfo(title=parsed.title, version=parsed.version))
                builder.add_server(OpenAPIServer(url="http://localhost:8000"))
                openapi_spec = builder.build()
                
            result["spec"] = openapi_spec
            
            if parsed.output:
                export_spec(openapi_spec, parsed.output, parsed.format)
                result["output_file"] = parsed.output
                
        elif parsed.action == "validate":
            if not parsed.input:
                raise ValueError("--input is required for validation")
                
            with open(parsed.input, 'r', encoding='utf-8') as f:
                if parsed.input.endswith('.yaml') or parsed.input.endswith('.yml'):
                    spec = yaml.safe_load(f)
                else:
                    spec = json.load(f)
                    
            errors = validate_spec(spec)
            result["valid"] = len(errors) == 0
            result["errors"] = errors
            
        elif parsed.action == "export":
            if not parsed.input:
                raise ValueError("--input is required for export")
                
            with open(parsed.input, 'r', encoding='utf-8') as f:
                if parsed.input.endswith('.yaml') or parsed.input.endswith('.yml'):
                    spec = yaml.safe_load(f)
                else:
                    spec = json.load(f)
                    
            output_path = parsed.output or f"openapi.{parsed.format}"
            export_spec(spec, output_path, parsed.format)
            result["output_file"] = output_path
            
        elif parsed.action == "client":
            if not parsed.input:
                raise ValueError("--input is required for client generation")
                
            with open(parsed.input, 'r', encoding='utf-8') as f:
                if parsed.input.endswith('.yaml') or parsed.input.endswith('.yml'):
                    spec = yaml.safe_load(f)
                else:
                    spec = json.load(f)
                    
            generator = ClientGenerator(spec)
            code = generator.generate(parsed.language)
            
            if parsed.output:
                with open(parsed.output, 'w', encoding='utf-8') as f:
                    f.write(code)
                result["output_file"] = parsed.output
            else:
                result["code"] = code
                
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
