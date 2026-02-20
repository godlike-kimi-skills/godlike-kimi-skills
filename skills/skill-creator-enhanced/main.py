#!/usr/bin/env python3
"""
Skill Creator Enhanced - 增强版技能创建器

一键创建符合开源标准的 Kimi Skill 项目

Usage:
    python main.py create --skill-name web-scraper --skill-title "Web Scraper" --description "Extract data"
    python main.py validate --skill-path ./my-skill
    python main.py list-templates
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# 模板定义
TEMPLATES = {
    "basic": {
        "name": "基础模板",
        "description": "最小化 Skill 模板，适合简单工具",
        "files": ["main.py", "skill.json", "SKILL.md", "README.md", "requirements.txt"]
    },
    "cli-tool": {
        "name": "CLI工具模板", 
        "description": "命令行工具模板，带参数解析",
        "files": ["main.py", "skill.json", "SKILL.md", "README.md", "requirements.txt", "cli.py"]
    },
    "data-processor": {
        "name": "数据处理模板",
        "description": "数据处理 Skill 模板，带 pandas 示例",
        "files": ["main.py", "skill.json", "SKILL.md", "README.md", "requirements.txt", "processor.py"]
    },
    "automation": {
        "name": "自动化模板",
        "description": "自动化任务模板，适合工作流自动化",
        "files": ["main.py", "skill.json", "SKILL.md", "README.md", "requirements.txt", "workflow.py"]
    }
}


class SkillCreator:
    """Skill 项目创建器"""
    
    def __init__(self, output_dir: str = "./"):
        self.output_dir = Path(output_dir).resolve()
        self.templates_dir = Path(__file__).parent / "templates"
        
    def create_skill(
        self,
        skill_name: str,
        skill_title: str,
        description: str,
        category: str = "other",
        template: str = "basic",
        with_tests: bool = True,
        with_ci: bool = True,
        with_examples: bool = True
    ) -> Path:
        """
        创建新的 Skill 项目
        
        Args:
            skill_name: Skill 名称（小写，连字符分隔）
            skill_title: Skill 中文标题
            description: Skill 描述
            category: 分类
            template: 模板类型
            with_tests: 是否生成测试
            with_ci: 是否生成 CI/CD
            with_examples: 是否生成示例
            
        Returns:
            创建的项目路径
        """
        # 验证 skill_name
        if not self._validate_skill_name(skill_name):
            raise ValueError(f"Invalid skill name: {skill_name}. Use lowercase with hyphens.")
        
        # 创建项目目录
        project_dir = self.output_dir / skill_name
        if project_dir.exists():
            raise FileExistsError(f"Directory already exists: {project_dir}")
        
        project_dir.mkdir(parents=True)
        
        # 生成文件
        self._generate_skill_json(project_dir, skill_name, skill_title, description, category)
        self._generate_skill_md(project_dir, skill_name, skill_title, description)
        self._generate_readme(project_dir, skill_name, skill_title, description)
        self._generate_license(project_dir)
        self._generate_main_py(project_dir, skill_name, template)
        self._generate_requirements(project_dir, template)
        self._generate_gitignore(project_dir)
        
        if with_tests:
            self._generate_tests(project_dir, skill_name)
        
        if with_examples:
            self._generate_examples(project_dir, skill_name)
        
        if with_ci:
            self._generate_github_workflows(project_dir)
        
        print(f"✅ Skill project created: {project_dir}")
        print(f"   Template: {template}")
        print(f"   Tests: {'Yes' if with_tests else 'No'}")
        print(f"   CI/CD: {'Yes' if with_ci else 'No'}")
        print(f"   Examples: {'Yes' if with_examples else 'No'}")
        
        return project_dir
    
    def _validate_skill_name(self, name: str) -> bool:
        """验证 skill_name 格式"""
        pattern = r'^[a-z][a-z0-9-]*$'
        return bool(re.match(pattern, name))
    
    def _generate_skill_json(
        self,
        project_dir: Path,
        skill_name: str,
        skill_title: str,
        description: str,
        category: str
    ) -> None:
        """生成 skill.json"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        skill_json = {
            "schema_version": "v1",
            "name": skill_name,
            "version": "1.0.0",
            "title": skill_title,
            "description": description,
            "author": "Your Name",
            "license": "MIT",
            "repository": f"https://github.com/your-username/{skill_name}",
            "keywords": ["kimi", category, skill_name.split("-")[0]],
            "language": "python",
            "main": "main.py",
            "entry_point": "main:main",
            "requirements": ["requirements.txt"],
            "min_cli_version": "0.5.0",
            "compatible_platforms": ["windows", "macos", "linux"],
            "mcp_compatible": True,
            "category": category,
            "priority": "p1",
            "parameters": [
                {
                    "name": "input",
                    "type": "string",
                    "required": True,
                    "description": "输入参数"
                }
            ]
        }
        
        with open(project_dir / "skill.json", "w", encoding="utf-8") as f:
            json.dump(skill_json, f, indent=2, ensure_ascii=False)
    
    def _generate_skill_md(self, project_dir: Path, skill_name: str, skill_title: str, description: str) -> None:
        """生成 SKILL.md"""
        content = f"""# {skill_title}

> {description}

---

## 功能概述

简要描述本 Skill 的核心功能和适用场景。

### 核心能力

1. **功能一** - 功能描述
2. **功能二** - 功能描述
3. **功能三** - 功能描述

---

## 使用方法

### 基础用法

```bash
kimi skill run {skill_name} --params "input=example"
```

### 进阶用法

```bash
# 添加更多参数示例
kimi skill run {skill_name} --params "input=example&option=true"
```

---

## 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|-------|------|------|-------|------|
| `input` | string | 是 | - | 输入参数说明 |
| `option` | boolean | 否 | false | 可选参数说明 |

---

## 示例

### 示例1：基础使用

```bash
kimi skill run {skill_name} --params "input=test"
```

预期输出：
```
处理结果: test
```

### 示例2：进阶使用

```bash
kimi skill run {skill_name} --params "input=test&option=true"
```

---

## 技术细节

### 依赖要求
- Python 3.10+
- 主要依赖包（见 requirements.txt）

### 实现原理
简要说明核心算法或实现思路。

---

## 更新日志

### v1.0.0 ({datetime.now().strftime("%Y-%m-%d")})
- 初始版本发布
- 核心功能实现

---

**Made with ❤️ by Godlike Kimi Skills**
"""
        
        with open(project_dir / "SKILL.md", "w", encoding="utf-8") as f:
            f.write(content)
    
    def _generate_readme(self, project_dir: Path, skill_name: str, skill_title: str, description: str) -> None:
        """生成 README.md"""
        content = f"""# {skill_title}

> {description}

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## 简介

{description}

## 安装

```bash
kimi skill install https://github.com/your-username/{skill_name}
```

## 使用

```bash
kimi skill run {skill_name} --params "input=example"
```

## 功能特性

- 特性一
- 特性二
- 特性三

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| input | string | 是 | 输入参数 |

## 示例

```bash
# 基础示例
kimi skill run {skill_name} --params "input=test"

# 进阶示例
kimi skill run {skill_name} --params "input=test&option=true"
```

## 开发

```bash
git clone https://github.com/your-username/{skill_name}.git
cd {skill_name}
pip install -r requirements.txt
python -m pytest tests/
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
"""
        
        with open(project_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(content)
    
    def _generate_license(self, project_dir: Path) -> None:
        """生成 LICENSE"""
        license_text = """MIT License

Copyright (c) 2026 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        
        with open(project_dir / "LICENSE", "w", encoding="utf-8") as f:
            f.write(license_text)
    
    def _generate_main_py(self, project_dir: Path, skill_name: str, template: str) -> None:
        """生成 main.py"""
        if template == "cli-tool":
            content = self._get_cli_tool_template(skill_name)
        elif template == "data-processor":
            content = self._get_data_processor_template(skill_name)
        elif template == "automation":
            content = self._get_automation_template(skill_name)
        else:
            content = self._get_basic_template(skill_name)
        
        with open(project_dir / "main.py", "w", encoding="utf-8") as f:
            f.write(content)
    
    def _get_basic_template(self, skill_name: str) -> str:
        """基础模板"""
        class_name = "".join(word.capitalize() for word in skill_name.split("-"))
        
        return f'''#!/usr/bin/env python3
"""
{skill_name} - Skill 主入口

Generated by Skill Creator Enhanced
"""

import argparse
import sys
from pathlib import Path


class {class_name}:
    """主类"""
    
    def __init__(self):
        self.version = "1.0.0"
    
    def process(self, input_data: str, **kwargs) -> str:
        """
        核心处理函数
        
        Args:
            input_data: 输入数据
            **kwargs: 其他参数
            
        Returns:
            处理结果
        """
        # TODO: 实现核心逻辑
        result = f"Processed: {{input_data}}"
        return result


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description="{skill_name}")
    parser.add_argument("--input", "-i", required=True, help="输入参数")
    parser.add_argument("--option", "-o", action="store_true", help="可选参数")
    parser.add_argument("--version", "-v", action="version", version="%(prog)s 1.0.0")
    
    args = parser.parse_args()
    
    try:
        processor = {class_name}()
        result = processor.process(args.input, option=args.option)
        print(result)
        return 0
    except Exception as e:
        print(f"Error: {{e}}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
'''
    
    def _get_cli_tool_template(self, skill_name: str) -> str:
        """CLI工具模板"""
        class_name = "".join(word.capitalize() for word in skill_name.split("-"))
        
        return f'''#!/usr/bin/env python3
"""
{skill_name} - CLI工具

Generated by Skill Creator Enhanced
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional


class {class_name}CLI:
    """CLI 工具类"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.config = {{}}
    
    def load_config(self, config_path: Optional[str] = None) -> dict:
        """加载配置"""
        if config_path and Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {{}}
    
    def execute(self, command: str, args: dict) -> dict:
        """
        执行命令
        
        Args:
            command: 命令名称
            args: 参数字典
            
        Returns:
            执行结果
        """
        if command == "process":
            return self._cmd_process(args)
        elif command == "status":
            return self._cmd_status()
        else:
            raise ValueError(f"Unknown command: {{command}}")
    
    def _cmd_process(self, args: dict) -> dict:
        """处理命令"""
        input_data = args.get("input", "")
        # TODO: 实现处理逻辑
        return {{
            "success": True,
            "input": input_data,
            "output": f"Processed: {{input_data}}"
        }}
    
    def _cmd_status(self) -> dict:
        """状态命令"""
        return {{
            "version": self.version,
            "status": "ready"
        }}


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description="{skill_name} CLI")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # process 命令
    process_parser = subparsers.add_parser("process", help="处理数据")
    process_parser.add_argument("--input", "-i", required=True, help="输入数据")
    process_parser.add_argument("--output", "-o", help="输出文件")
    
    # status 命令
    subparsers.add_parser("status", help="查看状态")
    
    parser.add_argument("--config", "-c", help="配置文件路径")
    parser.add_argument("--version", "-v", action="version", version="%(prog)s 1.0.0")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        cli = {class_name}CLI()
        
        if args.config:
            cli.load_config(args.config)
        
        # 转换参数
        arg_dict = vars(args)
        arg_dict.pop("command")
        arg_dict.pop("config", None)
        
        result = cli.execute(args.command, arg_dict)
        
        if "output" in arg_dict and arg_dict["output"]:
            with open(arg_dict["output"], "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return 0 if result.get("success", True) else 1
        
    except Exception as e:
        print(f"Error: {{e}}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
'''
    
    def _get_data_processor_template(self, skill_name: str) -> str:
        """数据处理模板"""
        class_name = "".join(word.capitalize() for word in skill_name.split("-"))
        
        return f'''#!/usr/bin/env python3
"""
{skill_name} - 数据处理器

Generated by Skill Creator Enhanced
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class {class_name}Processor:
    """数据处理器"""
    
    def __init__(self, config: Optional[dict] = None):
        self.version = "1.0.0"
        self.config = config or {{}}
        self.stats = {{
            "processed": 0,
            "errors": 0,
            "skipped": 0
        }}
    
    def load_data(self, source: str) -> List[Dict[str, Any]]:
        """
        加载数据
        
        Args:
            source: 数据源路径或字符串
            
        Returns:
            数据列表
        """
        source_path = Path(source)
        
        if source_path.exists():
            suffix = source_path.suffix.lower()
            if suffix == ".json":
                with open(source, "r", encoding="utf-8") as f:
                    return json.load(f)
            elif suffix in [".csv", ".txt"]:
                # TODO: 实现 CSV/TXT 读取
                return []
        
        # 尝试解析为 JSON 字符串
        try:
            return json.loads(source)
        except json.JSONDecodeError:
            return [{{"raw": source}}]
    
    def process(self, data: List[Dict[str, Any]], **options) -> List[Dict[str, Any]]:
        """
        处理数据
        
        Args:
            data: 输入数据
            **options: 处理选项
            
        Returns:
            处理后的数据
        """
        results = []
        
        for item in data:
            try:
                processed = self._process_item(item, **options)
                if processed:
                    results.append(processed)
                    self.stats["processed"] += 1
                else:
                    self.stats["skipped"] += 1
            except Exception as e:
                self.stats["errors"] += 1
                if not options.get("skip_errors", True):
                    raise
        
        return results
    
    def _process_item(self, item: Dict[str, Any], **options) -> Optional[Dict[str, Any]]:
        """处理单个数据项"""
        # TODO: 实现具体处理逻辑
        return item
    
    def save_results(self, results: List[Dict[str, Any]], output: str) -> None:
        """保存结果"""
        output_path = Path(output)
        suffix = output_path.suffix.lower()
        
        if suffix == ".json":
            with open(output, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        else:
            # 默认输出为 JSON
            with open(output, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return self.stats.copy()


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description="{skill_name}")
    parser.add_argument("--input", "-i", required=True, help="输入数据路径")
    parser.add_argument("--output", "-o", required=True, help="输出路径")
    parser.add_argument("--config", "-c", help="配置文件路径")
    parser.add_argument("--skip-errors", action="store_true", help="跳过错误")
    parser.add_argument("--version", "-v", action="version", version="%(prog)s 1.0.0")
    
    args = parser.parse_args()
    
    try:
        # 加载配置
        config = {{}}
        if args.config:
            with open(args.config, "r", encoding="utf-8") as f:
                config = json.load(f)
        
        # 创建处理器
        processor = {class_name}Processor(config)
        
        # 加载数据
        data = processor.load_data(args.input)
        
        # 处理数据
        results = processor.process(data, skip_errors=args.skip_errors)
        
        # 保存结果
        processor.save_results(results, args.output)
        
        # 输出统计
        stats = processor.get_stats()
        print(f"处理完成: {{stats}}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {{e}}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
'''
    
    def _get_automation_template(self, skill_name: str) -> str:
        """自动化模板"""
        class_name = "".join(word.capitalize() for word in skill_name.split("-"))
        
        return f'''#!/usr/bin/env python3
"""
{skill_name} - 自动化工作流

Generated by Skill Creator Enhanced
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class {class_name}Workflow:
    """自动化工作流"""
    
    def __init__(self, config: Optional[dict] = None):
        self.version = "1.0.0"
        self.config = config or {{}}
        self.logs = []
        self.steps = []
    
    def log(self, message: str, level: str = "info"):
        """记录日志"""
        entry = {{
            "time": datetime.now().isoformat(),
            "level": level,
            "message": message
        }}
        self.logs.append(entry)
        print(f"[{{level.upper()}}] {{message}}")
    
    def add_step(self, name: str, func, **kwargs):
        """添加工作流步骤"""
        self.steps.append({{
            "name": name,
            "function": func,
            "params": kwargs
        }})
    
    def execute(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        执行工作流
        
        Args:
            dry_run: 是否仅预览不执行
            
        Returns:
            执行结果
        """
        results = {{
            "success": True,
            "steps_executed": 0,
            "steps_failed": 0,
            "dry_run": dry_run
        }}
        
        self.log(f"开始执行工作流 (dry_run={{dry_run}})")
        
        for step in self.steps:
            try:
                self.log(f"执行步骤: {{step['name']}}")
                
                if not dry_run:
                    step["function"](**step["params"])
                
                results["steps_executed"] += 1
                self.log(f"步骤完成: {{step['name']}}")
                
            except Exception as e:
                results["steps_failed"] += 1
                self.log(f"步骤失败: {{step['name']}} - {{e}}", "error")
                
                if not self.config.get("continue_on_error", False):
                    results["success"] = False
                    break
        
        self.log(f"工作流执行完成: {{results}}")
        return results
    
    def save_logs(self, output_path: str):
        """保存日志"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.logs, f, indent=2, ensure_ascii=False)


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description="{skill_name}")
    parser.add_argument("--config", "-c", help="配置文件路径")
    parser.add_argument("--dry-run", action="store_true", help="预览模式")
    parser.add_argument("--log", "-l", help="日志输出路径")
    parser.add_argument("--version", "-v", action="version", version="%(prog)s 1.0.0")
    
    args = parser.parse_args()
    
    try:
        # 加载配置
        config = {{}}
        if args.config:
            with open(args.config, "r", encoding="utf-8") as f:
                config = json.load(f)
        
        # 创建工作流
        workflow = {class_name}Workflow(config)
        
        # TODO: 在这里添加工作流步骤
        # workflow.add_step("step1", lambda: print("Step 1"))
        # workflow.add_step("step2", lambda: print("Step 2"))
        
        # 执行工作流
        results = workflow.execute(dry_run=args.dry_run)
        
        # 保存日志
        if args.log:
            workflow.save_logs(args.log)
        
        return 0 if results["success"] else 1
        
    except Exception as e:
        print(f"Error: {{e}}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
'''
    
    def _generate_requirements(self, project_dir: Path, template: str) -> None:
        """生成 requirements.txt"""
        if template == "data-processor":
            content = "# Core dependencies\n# pandas>=2.0.0\n# numpy>=1.24.0\n\n# Development dependencies\n# pytest>=7.0.0\n# pytest-cov>=4.0.0\n"
        elif template == "automation":
            content = "# Core dependencies\n# requests>=2.31.0\n# schedule>=1.2.0\n\n# Development dependencies\n# pytest>=7.0.0\n# pytest-cov>=4.0.0\n"
        else:
            content = "# Add your dependencies here\n# Example:\n# requests>=2.31.0\n\n# Development dependencies\n# pytest>=7.0.0\n# pytest-cov>=4.0.0\n"
        
        with open(project_dir / "requirements.txt", "w", encoding="utf-8") as f:
            f.write(content)
    
    def _generate_gitignore(self, project_dir: Path) -> None:
        """生成 .gitignore"""
        content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db

# Project specific
*.log
output/
temp/
"""
        
        with open(project_dir / ".gitignore", "w", encoding="utf-8") as f:
            f.write(content)
    
    def _generate_tests(self, project_dir: Path, skill_name: str) -> None:
        """生成测试文件"""
        # tests/__init__.py
        with open(project_dir / "tests" / "__init__.py", "w", encoding="utf-8") as f:
            f.write("# Test package\n")
        
        # tests/test_basic.py
        class_name = "".join(word.capitalize() for word in skill_name.split("-"))
        
        test_content = f'''#!/usr/bin/env python3
"""
基础测试

Generated by Skill Creator Enhanced
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import {class_name}


class Test{class_name}(unittest.TestCase):
    """测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.processor = {class_name}()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.processor.version, "1.0.0")
    
    def test_process(self):
        """测试核心功能"""
        result = self.processor.process("test")
        self.assertIsNotNone(result)
        # TODO: 添加更多断言
    
    def test_process_empty(self):
        """测试空输入处理"""
        result = self.processor.process("")
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
'''
        
        with open(project_dir / "tests" / "test_basic.py", "w", encoding="utf-8") as f:
            f.write(test_content)
        
        # tests/test_advanced.py
        advanced_test = f'''#!/usr/bin/env python3
"""
高级测试

Generated by Skill Creator Enhanced
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import {class_name}


class Test{class_name}Advanced(unittest.TestCase):
    """高级测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.processor = {class_name}()
    
    def test_edge_cases(self):
        """测试边界情况"""
        # TODO: 添加边界测试
        pass
    
    def test_error_handling(self):
        """测试错误处理"""
        # TODO: 添加错误处理测试
        pass
    
    def test_performance(self):
        """测试性能"""
        # TODO: 添加性能测试
        pass


if __name__ == "__main__":
    unittest.main()
'''
        
        with open(project_dir / "tests" / "test_advanced.py", "w", encoding="utf-8") as f:
            f.write(advanced_test)
    
    def _generate_examples(self, project_dir: Path, skill_name: str) -> None:
        """生成示例文件"""
        # examples/basic_usage.py
        basic_example = f'''#!/usr/bin/env python3
"""
基础使用示例

Generated by Skill Creator Enhanced
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import main

if __name__ == "__main__":
    # 基础用法示例
    sys.argv = [
        "main.py",
        "--input", "example_data",
    ]
    
    exit_code = main()
    print(f"Exit code: {{exit_code}}")
'''
        
        with open(project_dir / "examples" / "basic_usage.py", "w", encoding="utf-8") as f:
            f.write(basic_example)
        
        # examples/advanced_usage.py
        advanced_example = f'''#!/usr/bin/env python3
"""
高级使用示例

Generated by Skill Creator Enhanced
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import main

if __name__ == "__main__":
    # 高级用法示例
    sys.argv = [
        "main.py",
        "--input", "example_data",
        # "--option",  # 启用可选功能
    ]
    
    exit_code = main()
    print(f"Exit code: {{exit_code}}")
'''
        
        with open(project_dir / "examples" / "advanced_usage.py", "w", encoding="utf-8") as f:
            f.write(advanced_example)
    
    def _generate_github_workflows(self, project_dir: Path) -> None:
        """生成 GitHub Actions 工作流"""
        # .github/workflows/ci.yml
        ci_content = '''name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Test with pytest
      run: |
        pytest tests/ --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false
'''
        
        github_dir = project_dir / ".github" / "workflows"
        github_dir.mkdir(parents=True, exist_ok=True)
        
        with open(github_dir / "ci.yml", "w", encoding="utf-8") as f:
            f.write(ci_content)
        
        # .github/workflows/release.yml
        release_content = '''name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest
    
    - name: Run tests
      run: pytest tests/
    
    - name: Create Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        draft: false
        prerelease: false
'''
        
        with open(github_dir / "release.yml", "w", encoding="utf-8") as f:
            f.write(release_content)
    
    def validate_skill(self, skill_path: str) -> Dict[str, any]:
        """
        验证 Skill 项目是否符合标准
        
        Args:
            skill_path: Skill 项目路径
            
        Returns:
            验证结果字典
        """
        skill_dir = Path(skill_path)
        
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "checks": {}
        }
        
        # 检查必需文件
        required_files = ["skill.json", "SKILL.md", "README.md", "LICENSE", "main.py"]
        for file in required_files:
            file_path = skill_dir / file
            exists = file_path.exists()
            results["checks"][file] = exists
            if not exists:
                results["errors"].append(f"Missing required file: {file}")
                results["valid"] = False
        
        # 验证 skill.json
        skill_json_path = skill_dir / "skill.json"
        if skill_json_path.exists():
            try:
                with open(skill_json_path, "r", encoding="utf-8") as f:
                    skill_config = json.load(f)
                
                required_fields = ["name", "version", "title", "description", "main"]
                for field in required_fields:
                    if field not in skill_config:
                        results["errors"].append(f"Missing field in skill.json: {field}")
                        results["valid"] = False
                
                # 检查 name 格式
                name = skill_config.get("name", "")
                if not self._validate_skill_name(name):
                    results["errors"].append(f"Invalid skill name format: {name}")
                    results["valid"] = False
                    
            except json.JSONDecodeError as e:
                results["errors"].append(f"Invalid skill.json: {e}")
                results["valid"] = False
        
        # 检查 tests 目录
        tests_dir = skill_dir / "tests"
        if tests_dir.exists():
            test_files = list(tests_dir.glob("test_*.py"))
            results["checks"]["test_files"] = len(test_files)
            if len(test_files) < 1:
                results["warnings"].append("No test files found")
        else:
            results["warnings"].append("No tests directory found")
        
        return results
    
    def list_templates(self) -> List[Dict[str, str]]:
        """列出可用模板"""
        return [
            {"id": key, "name": value["name"], "description": value["description"]}
            for key, value in TEMPLATES.items()
        ]


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="Skill Creator Enhanced - 增强版技能创建器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 创建新 Skill
  python main.py create --skill-name web-scraper --skill-title "Web Scraper" --description "Extract data"
  
  # 验证 Skill
  python main.py validate --skill-path ./my-skill
  
  # 列出模板
  python main.py list-templates
        """
    )
    
    subparsers = parser.add_subparsers(dest="action", help="可用操作")
    
    # create 命令
    create_parser = subparsers.add_parser("create", help="创建新 Skill")
    create_parser.add_argument("--skill-name", required=True, help="Skill 名称（小写，连字符分隔）")
    create_parser.add_argument("--skill-title", required=True, help="Skill 中文标题")
    create_parser.add_argument("--description", required=True, help="Skill 描述")
    create_parser.add_argument("--category", default="other", 
                              choices=["development", "data", "automation", "security", "media", "other"],
                              help="Skill 分类")
    create_parser.add_argument("--template", default="basic", choices=list(TEMPLATES.keys()),
                              help="项目模板")
    create_parser.add_argument("--output-dir", default="./", help="输出目录")
    create_parser.add_argument("--no-tests", action="store_true", help="不生成测试")
    create_parser.add_argument("--no-ci", action="store_true", help="不生成 CI/CD")
    create_parser.add_argument("--no-examples", action="store_true", help="不生成示例")
    
    # validate 命令
    validate_parser = subparsers.add_parser("validate", help="验证 Skill 项目")
    validate_parser.add_argument("--skill-path", required=True, help="Skill 项目路径")
    
    # list-templates 命令
    subparsers.add_parser("list-templates", help="列出可用模板")
    
    # upgrade 命令（TODO）
    upgrade_parser = subparsers.add_parser("upgrade", help="升级现有 Skill")
    upgrade_parser.add_argument("--skill-path", required=True, help="Skill 项目路径")
    
    parser.add_argument("--version", "-v", action="version", version="%(prog)s 1.0.0")
    
    args = parser.parse_args()
    
    if not args.action:
        parser.print_help()
        return 1
    
    creator = SkillCreator()
    
    try:
        if args.action == "create":
            project_dir = creator.create_skill(
                skill_name=args.skill_name,
                skill_title=args.skill_title,
                description=args.description,
                category=args.category,
                template=args.template,
                output_dir=args.output_dir,
                with_tests=not args.no_tests,
                with_ci=not args.no_ci,
                with_examples=not args.no_examples
            )
            print(f"\\n🎉 Skill 项目创建成功!")
            print(f"   路径: {project_dir}")
            print(f"\\n下一步:")
            print(f"   1. cd {project_dir}")
            print(f"   2. 编辑 main.py 实现核心功能")
            print(f"   3. 运行测试: python -m pytest tests/")
            
        elif args.action == "validate":
            results = creator.validate_skill(args.skill_path)
            
            print(f"\\n验证结果: {'✅ 通过' if results['valid'] else '❌ 失败'}")
            print(f"\\n检查项:")
            for check, status in results["checks"].items():
                symbol = "✅" if status else "❌"
                print(f"   {symbol} {check}")
            
            if results["errors"]:
                print(f"\\n❌ 错误:")
                for error in results["errors"]:
                    print(f"   - {error}")
            
            if results["warnings"]:
                print(f"\\n⚠️ 警告:")
                for warning in results["warnings"]:
                    print(f"   - {warning}")
            
            return 0 if results["valid"] else 1
            
        elif args.action == "list-templates":
            templates = creator.list_templates()
            print("\\n可用模板:\\n")
            for template in templates:
                print(f"  {template['id']:<15} - {template['name']}")
                print(f"                   {template['description']}\\n")
        
        elif args.action == "upgrade":
            print("⚠️ 升级功能暂未实现")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"\\n❌ 错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
