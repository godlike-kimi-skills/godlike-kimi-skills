#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown Docs Skill

功能：Markdown文档生成工具
- README生成
- API文档生成
- Changelog维护
- 文档模板管理

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


class DocType(Enum):
    """文档类型枚举"""
    README = "readme"
    API = "api"
    CHANGELOG = "changelog"
    CONTRIBUTING = "contributing"
    LICENSE = "license"
    CUSTOM = "custom"


@dataclass
class ProjectInfo:
    """项目信息"""
    name: str
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    license: str = "MIT"
    homepage: str = ""
    repository: str = ""
    keywords: List[str] = field(default_factory=list)


@dataclass
class APIEndpoint:
    """API端点信息"""
    method: str
    path: str
    summary: str = ""
    description: str = ""
    parameters: List[Dict] = field(default_factory=list)
    request_body: Optional[Dict] = None
    responses: List[Dict] = field(default_factory=list)


@dataclass
class ChangelogEntry:
    """Changelog条目"""
    version: str
    date: str
    changes: List[str]
    type_: str = "added"  # added, changed, deprecated, removed, fixed, security


class MarkdownBuilder:
    """Markdown文档构建器"""
    
    def __init__(self, title: str = ""):
        self.title = title
        self.sections: List[Dict[str, Any]] = []
        self.toc_enabled = True
        
    def add_heading(self, text: str, level: int = 1) -> "MarkdownBuilder":
        """添加标题"""
        self.sections.append({
            "type": "heading",
            "level": level,
            "text": text
        })
        return self
        
    def add_paragraph(self, text: str) -> "MarkdownBuilder":
        """添加段落"""
        self.sections.append({
            "type": "paragraph",
            "text": text
        })
        return self
        
    def add_code_block(self, code: str, language: str = "") -> "MarkdownBuilder":
        """添加代码块"""
        self.sections.append({
            "type": "code",
            "language": language,
            "code": code
        })
        return self
        
    def add_list(self, items: List[str], ordered: bool = False) -> "MarkdownBuilder":
        """添加列表"""
        self.sections.append({
            "type": "list",
            "ordered": ordered,
            "items": items
        })
        return self
        
    def add_table(self, headers: List[str], rows: List[List[str]]) -> "MarkdownBuilder":
        """添加表格"""
        self.sections.append({
            "type": "table",
            "headers": headers,
            "rows": rows
        })
        return self
        
    def add_blockquote(self, text: str) -> "MarkdownBuilder":
        """添加引用块"""
        self.sections.append({
            "type": "blockquote",
            "text": text
        })
        return self
        
    def add_horizontal_rule(self) -> "MarkdownBuilder":
        """添加水平分隔线"""
        self.sections.append({"type": "hr"})
        return self
        
    def add_toc(self, max_depth: int = 3) -> "MarkdownBuilder":
        """添加目录"""
        self.sections.append({
            "type": "toc",
            "max_depth": max_depth
        })
        return self
        
    def add_badge(self, label: str, message: str, color: str = "blue") -> "MarkdownBuilder":
        """添加徽章"""
        self.sections.append({
            "type": "badge",
            "label": label,
            "message": message,
            "color": color
        })
        return self
        
    def build(self) -> str:
        """构建Markdown文档"""
        lines = []
        
        # 添加标题
        if self.title:
            lines.append(f"# {self.title}")
            lines.append("")
            
        # 处理目录
        if self.toc_enabled:
            toc_sections = [s for s in self.sections if s.get("type") == "toc"]
            if toc_sections:
                lines.append("## Table of Contents")
                lines.append("")
                headings = [s for s in self.sections if s.get("type") == "heading"]
                for heading in headings:
                    level = heading["level"]
                    text = heading["text"]
                    anchor = self._generate_anchor(text)
                    indent = "  " * (level - 1)
                    lines.append(f"{indent}- [{text}](#{anchor})")
                lines.append("")
                
        # 处理其他部分
        for section in self.sections:
            section_type = section.get("type")
            
            if section_type == "heading":
                prefix = "#" * section["level"]
                lines.append(f"{prefix} {section['text']}")
                lines.append("")
                
            elif section_type == "paragraph":
                lines.append(section["text"])
                lines.append("")
                
            elif section_type == "code":
                lang = section.get("language", "")
                lines.append(f"```{lang}")
                lines.append(section["code"])
                lines.append("```")
                lines.append("")
                
            elif section_type == "list":
                for i, item in enumerate(section["items"]):
                    if section.get("ordered"):
                        lines.append(f"{i + 1}. {item}")
                    else:
                        lines.append(f"- {item}")
                lines.append("")
                
            elif section_type == "table":
                headers = section["headers"]
                rows = section["rows"]
                
                # 表头
                lines.append("| " + " | ".join(headers) + " |")
                lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                
                # 行
                for row in rows:
                    lines.append("| " + " | ".join(row) + " |")
                lines.append("")
                
            elif section_type == "blockquote":
                lines.append(f"> {section['text']}")
                lines.append("")
                
            elif section_type == "hr":
                lines.append("---")
                lines.append("")
                
            elif section_type == "badge":
                #  shields.io 格式
                label = section["label"]
                message = section["message"]
                color = section.get("color", "blue")
                badge = f"![{label}](https://img.shields.io/badge/{label}-{message}-{color})"
                lines.append(badge)
                lines.append("")
                
        return "\n".join(lines)
        
    def _generate_anchor(self, text: str) -> str:
        """生成锚点链接"""
        anchor = text.lower()
        anchor = re.sub(r'[^\w\s-]', '', anchor)
        anchor = re.sub(r'[\s]+', '-', anchor)
        return anchor


class READMEGenerator:
    """README生成器"""
    
    TEMPLATES = {
        "default": {
            "sections": ["badges", "description", "installation", "usage", "api", "contributing", "license"]
        },
        "minimal": {
            "sections": ["description", "installation", "usage"]
        },
        "full": {
            "sections": ["badges", "logo", "description", "features", "demo", "installation", "usage", "api", "examples", "roadmap", "contributing", "license", "acknowledgments"]
        }
    }
    
    def __init__(self, project_info: ProjectInfo, template: str = "default"):
        self.info = project_info
        self.template = template
        self.custom_sections: Dict[str, str] = {}
        
    def set_section(self, name: str, content: str) -> "READMEGenerator":
        """设置自定义章节内容"""
        self.custom_sections[name] = content
        return self
        
    def generate(self) -> str:
        """生成README内容"""
        builder = MarkdownBuilder(title=self.info.name)
        
        template_config = self.TEMPLATES.get(self.template, self.TEMPLATES["default"])
        
        for section in template_config["sections"]:
            if section == "badges":
                self._add_badges(builder)
            elif section == "description":
                self._add_description(builder)
            elif section == "installation":
                self._add_installation(builder)
            elif section == "usage":
                self._add_usage(builder)
            elif section == "api":
                self._add_api(builder)
            elif section == "contributing":
                self._add_contributing(builder)
            elif section == "license":
                self._add_license(builder)
            elif section == "features":
                self._add_features(builder)
            elif section == "examples":
                self._add_examples(builder)
            elif section in self.custom_sections:
                builder.add_heading(section.replace("_", " ").title(), 2)
                builder.add_paragraph(self.custom_sections[section])
                
        return builder.build()
        
    def _add_badges(self, builder: MarkdownBuilder):
        """添加徽章"""
        if self.info.license:
            builder.add_badge("license", self.info.license, "blue")
        if self.info.version:
            builder.add_badge("version", self.info.version, "green")
        builder.add_paragraph("")
        
    def _add_description(self, builder: MarkdownBuilder):
        """添加描述"""
        if self.info.description:
            builder.add_heading("Description", 2)
            builder.add_paragraph(self.info.description)
            
    def _add_installation(self, builder: MarkdownBuilder):
        """添加安装说明"""
        builder.add_heading("Installation", 2)
        
        if self.info.repository:
            builder.add_code_block(f"pip install {self.info.name.lower()}", "bash")
        else:
            builder.add_paragraph("Add installation instructions here.")
            
    def _add_usage(self, builder: MarkdownBuilder):
        """添加使用说明"""
        builder.add_heading("Usage", 2)
        builder.add_code_block(f"""import {self.info.name.lower().replace('-', '_')}

# Initialize
client = {self.info.name.lower().replace('-', '_')}.Client()

# Use the API
result = client.get_data()
print(result)""", "python")
        
    def _add_api(self, builder: MarkdownBuilder):
        """添加API文档"""
        builder.add_heading("API Reference", 2)
        builder.add_paragraph("See [API.md](API.md) for detailed API documentation.")
        
    def _add_contributing(self, builder: MarkdownBuilder):
        """添加贡献指南"""
        builder.add_heading("Contributing", 2)
        builder.add_paragraph("Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.")
        
    def _add_license(self, builder: MarkdownBuilder):
        """添加许可证信息"""
        builder.add_heading("License", 2)
        builder.add_paragraph(f"This project is licensed under the {self.info.license} License.")
        
    def _add_features(self, builder: MarkdownBuilder):
        """添加功能特性"""
        builder.add_heading("Features", 2)
        builder.add_list([
            "Feature 1: Description of feature 1",
            "Feature 2: Description of feature 2",
            "Feature 3: Description of feature 3"
        ])
        
    def _add_examples(self, builder: MarkdownBuilder):
        """添加示例"""
        builder.add_heading("Examples", 2)
        builder.add_paragraph("More examples can be found in the [examples](examples/) directory.")


class APIDocGenerator:
    """API文档生成器"""
    
    def __init__(self, title: str = "API Documentation"):
        self.title = title
        self.endpoints: List[APIEndpoint] = []
        self.models: Dict[str, Dict] = {}
        
    def add_endpoint(self, endpoint: APIEndpoint) -> "APIDocGenerator":
        """添加API端点"""
        self.endpoints.append(endpoint)
        return self
        
    def add_model(self, name: str, schema: Dict) -> "APIDocGenerator":
        """添加数据模型"""
        self.models[name] = schema
        return self
        
    def generate(self) -> str:
        """生成API文档"""
        builder = MarkdownBuilder(title=self.title)
        
        # 目录
        builder.add_toc()
        
        # 概述
        builder.add_heading("Overview", 2)
        builder.add_paragraph("This document describes the API endpoints and data models.")
        
        # 端点分组
        grouped = self._group_endpoints_by_tag()
        
        for group, endpoints in grouped.items():
            builder.add_heading(group.capitalize(), 2)
            
            for endpoint in endpoints:
                builder.add_heading(f"{endpoint.method.upper()} {endpoint.path}", 3)
                
                if endpoint.summary:
                    builder.add_paragraph(f"**{endpoint.summary}**")
                    
                if endpoint.description:
                    builder.add_paragraph(endpoint.description)
                    
                # 参数
                if endpoint.parameters:
                    builder.add_heading("Parameters", 4)
                    headers = ["Name", "Type", "In", "Required", "Description"]
                    rows = []
                    for param in endpoint.parameters:
                        rows.append([
                            param.get("name", ""),
                            param.get("schema", {}).get("type", "string"),
                            param.get("in", "query"),
                            str(param.get("required", False)),
                            param.get("description", "")
                        ])
                    builder.add_table(headers, rows)
                    
                # 请求体
                if endpoint.request_body:
                    builder.add_heading("Request Body", 4)
                    builder.add_code_block(
                        json.dumps(endpoint.request_body, indent=2),
                        "json"
                    )
                    
                # 响应
                if endpoint.responses:
                    builder.add_heading("Responses", 4)
                    for resp in endpoint.responses:
                        builder.add_paragraph(f"**{resp.get('code', '200')}** - {resp.get('description', '')}")
                        if "schema" in resp:
                            builder.add_code_block(
                                json.dumps(resp["schema"], indent=2),
                                "json"
                            )
                            
        # 数据模型
        if self.models:
            builder.add_heading("Data Models", 2)
            
            for name, schema in self.models.items():
                builder.add_heading(name, 3)
                builder.add_code_block(
                    json.dumps(schema, indent=2),
                    "json"
                )
                
        return builder.build()
        
    def _group_endpoints_by_tag(self) -> Dict[str, List[APIEndpoint]]:
        """按标签分组端点"""
        grouped: Dict[str, List[APIEndpoint]] = {}
        
        for endpoint in self.endpoints:
            # 从路径提取分组
            parts = endpoint.path.strip("/").split("/")
            group = parts[0] if parts else "default"
            
            if group not in grouped:
                grouped[group] = []
            grouped[group].append(endpoint)
            
        return grouped


class ChangelogGenerator:
    """Changelog生成器"""
    
    def __init__(self, title: str = "Changelog"):
        self.title = title
        self.entries: List[ChangelogEntry] = []
        self.format_type = "keepachangelog"  # keepachangelog, semantic
        
    def add_entry(self, entry: ChangelogEntry) -> "ChangelogGenerator":
        """添加Changelog条目"""
        self.entries.append(entry)
        # 按版本排序
        self.entries.sort(key=lambda e: e.version, reverse=True)
        return self
        
    def generate(self) -> str:
        """生成Changelog"""
        builder = MarkdownBuilder(title=self.title)
        
        builder.add_paragraph(
            "All notable changes to this project will be documented in this file."
        )
        builder.add_paragraph(
            "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), "
            "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)."
        )
        
        # 未发布版本
        builder.add_heading("[Unreleased]", 2)
        builder.add_list([
            "Features and changes planned for next release"
        ])
        
        # 已发布版本
        for entry in self.entries:
            builder.add_heading(f"[{entry.version}] - {entry.date}", 2)
            
            # 按类型分组
            type_labels = {
                "added": "Added",
                "changed": "Changed",
                "deprecated": "Deprecated",
                "removed": "Removed",
                "fixed": "Fixed",
                "security": "Security"
            }
            
            builder.add_heading(type_labels.get(entry.type_, "Changed"), 3)
            builder.add_list(entry.changes)
            
        return builder.build()
        
    def add_version(
        self,
        version: str,
        changes: List[str],
        date: Optional[str] = None,
        change_type: str = "added"
    ) -> "ChangelogGenerator":
        """添加版本记录"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
            
        entry = ChangelogEntry(
            version=version,
            date=date,
            changes=changes,
            type_=change_type
        )
        return self.add_entry(entry)


def generate_readme(
    project_name: str,
    description: str = "",
    template: str = "default",
    **kwargs
) -> str:
    """生成README文档"""
    info = ProjectInfo(
        name=project_name,
        description=description,
        version=kwargs.get("version", "1.0.0"),
        author=kwargs.get("author", ""),
        license=kwargs.get("license", "MIT"),
        repository=kwargs.get("repository", "")
    )
    
    generator = READMEGenerator(info, template)
    
    # 设置自定义章节
    for key, value in kwargs.items():
        if key not in ["version", "author", "license", "repository"]:
            generator.set_section(key, value)
            
    return generator.generate()


def generate_api_docs(
    openapi_spec: Optional[Dict] = None,
    title: str = "API Documentation",
    endpoints: Optional[List[APIEndpoint]] = None
) -> str:
    """生成API文档"""
    generator = APIDocGenerator(title)
    
    if openapi_spec:
        # 从OpenAPI规范转换
        paths = openapi_spec.get("paths", {})
        schemas = openapi_spec.get("components", {}).get("schemas", {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method not in ["get", "post", "put", "delete", "patch"]:
                    continue
                    
                endpoint = APIEndpoint(
                    method=method.upper(),
                    path=path,
                    summary=operation.get("summary", ""),
                    description=operation.get("description", ""),
                    parameters=operation.get("parameters", []),
                    request_body=operation.get("requestBody"),
                    responses=[
                        {"code": code, **resp}
                        for code, resp in operation.get("responses", {}).items()
                    ]
                )
                generator.add_endpoint(endpoint)
                
        for name, schema in schemas.items():
            generator.add_model(name, schema)
            
    elif endpoints:
        for endpoint in endpoints:
            generator.add_endpoint(endpoint)
            
    return generator.generate()


def update_changelog(
    changelog_path: str,
    version: str,
    changes: List[str],
    change_type: str = "added"
) -> str:
    """更新Changelog文件"""
    generator = ChangelogGenerator()
    generator.add_version(version, changes, change_type=change_type)
    
    new_content = generator.generate()
    
    # 如果文件存在，合并内容
    if os.path.exists(changelog_path):
        with open(changelog_path, 'r', encoding='utf-8') as f:
            existing = f.read()
            
        # 简单合并（实际应用需要更复杂的逻辑）
        new_content = existing + "\n\n" + new_content
        
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    return changelog_path


# Kimi CLI 入口点
def run(args: Optional[List[str]] = None) -> Dict[str, Any]:
    """Kimi CLI 入口函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Markdown Docs Skill")
    parser.add_argument("action", choices=["readme", "api", "changelog"],
                       help="Action to perform")
    parser.add_argument("--name", "-n", help="Project name")
    parser.add_argument("--description", "-d", help="Project description")
    parser.add_argument("--template", "-t", default="default",
                       choices=["default", "minimal", "full"],
                       help="Template to use")
    parser.add_argument("--input", "-i", help="Input file path")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--version", "-v", default="1.0.0", help="Version")
    
    parsed = parser.parse_args(args)
    
    result = {"success": True, "action": parsed.action}
    
    try:
        if parsed.action == "readme":
            if not parsed.name:
                raise ValueError("--name is required for readme generation")
                
            content = generate_readme(
                project_name=parsed.name,
                description=parsed.description or "",
                template=parsed.template,
                version=parsed.version
            )
            
            if parsed.output:
                with open(parsed.output, 'w', encoding='utf-8') as f:
                    f.write(content)
                result["output_file"] = parsed.output
            else:
                result["content"] = content
                
        elif parsed.action == "api":
            if not parsed.input:
                raise ValueError("--input is required for api doc generation")
                
            with open(parsed.input, 'r', encoding='utf-8') as f:
                if parsed.input.endswith('.yaml') or parsed.input.endswith('.yml'):
                    import yaml
                    spec = yaml.safe_load(f)
                else:
                    spec = json.load(f)
                    
            content = generate_api_docs(openapi_spec=spec)
            
            output_path = parsed.output or "API.md"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            result["output_file"] = output_path
            
        elif parsed.action == "changelog":
            if not parsed.name:
                raise ValueError("--name is required for changelog")
                
            generator = ChangelogGenerator()
            generator.add_version(parsed.version, ["Initial release"])
            content = generator.generate()
            
            output_path = parsed.output or "CHANGELOG.md"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            result["output_file"] = output_path
            
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
