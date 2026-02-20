"""
poetry-skill: Poetry依赖管理Skill
提供项目初始化、依赖管理、发布打包功能
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
import json


@dataclass
class ProjectInfo:
    """项目信息数据类"""
    name: str
    version: str
    description: str = ""
    authors: List[str] = field(default_factory=list)
    dependencies: Dict[str, str] = field(default_factory=dict)
    dev_dependencies: Dict[str, str] = field(default_factory=dict)
    python_version: str = "^3.8"
    readme: str = "README.md"
    license: str = ""
    homepage: str = ""
    repository: str = ""


@dataclass
class DependencyInfo:
    """依赖信息数据类"""
    name: str
    version: str
    category: str = "main"  # main, dev, or custom group
    optional: bool = False
    extras: List[str] = field(default_factory=list)


@dataclass
class BuildInfo:
    """构建信息数据类"""
    success: bool
    artifacts: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class PoetrySkill:
    """
    Poetry依赖管理Skill主类
    
    提供功能:
    - 项目初始化
    - 依赖管理
    - 虚拟环境管理
    - 构建发布
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.virtualenvs_create = self.config.get("virtualenvs_create", True)
        self.virtualenvs_in_project = self.config.get("virtualenvs_in_project", True)
        self.max_workers = self.config.get("installer_max_workers", 4)
        
        self._check_poetry_installation()
    
    def _check_poetry_installation(self):
        """检查Poetry是否已安装"""
        try:
            result = subprocess.run(
                ["poetry", "--version"],
                capture_output=True,
                text=True
            )
            self.poetry_available = result.returncode == 0
            if self.poetry_available:
                self.poetry_version = result.stdout.strip()
        except FileNotFoundError:
            self.poetry_available = False
            self.poetry_version = None
    
    def init_project(self, name: str, **options) -> Dict[str, Any]:
        """
        初始化新项目
        
        Args:
            name: 项目名称
            **options: 初始化选项
                - description: 项目描述
                - author: 作者信息
                - python: Python版本要求
                - path: 项目路径（默认为当前目录）
                - template: 项目模板
                
        Returns:
            初始化结果
        """
        project_path = Path(options.get("path", ".")) / name
        
        # 创建项目目录
        project_path.mkdir(parents=True, exist_ok=True)
        
        # 创建基本目录结构
        pkg_name = self._normalize_package_name(name)
        (project_path / pkg_name).mkdir(exist_ok=True)
        (project_path / "tests").mkdir(exist_ok=True)
        
        # 生成pyproject.toml
        self._generate_pyproject_toml(project_path, name, options)
        
        # 生成README.md
        self._generate_readme(project_path, name, options)
        
        # 生成基础文件
        self._generate_init_file(project_path / pkg_name, pkg_name)
        self._generate_test_init(project_path / "tests")
        self._generate_gitignore(project_path)
        
        return {
            "success": True,
            "project_path": str(project_path),
            "package_name": pkg_name,
            "files_created": [
                "pyproject.toml",
                "README.md",
                f"{pkg_name}/__init__.py",
                "tests/__init__.py",
                ".gitignore"
            ]
        }
    
    def _normalize_package_name(self, name: str) -> str:
        """规范化包名"""
        # 替换连字符和空格为下划线
        return re.sub(r'[-\s]+', '_', name.lower())
    
    def _generate_pyproject_toml(self, path: Path, name: str, 
                                  options: Dict) -> None:
        """生成pyproject.toml文件"""
        pkg_name = self._normalize_package_name(name)
        description = options.get("description", f"{name} project")
        author = options.get("author", "Your Name <you@example.com>")
        python = options.get("python", "^3.8")
        license_str = options.get("license", "MIT")
        
        content = f'''[tool.poetry]
name = "{name}"
version = "0.1.0"
description = "{description}"
authors = ["{author}"]
readme = "README.md"
license = "{license_str}"
packages = [{{include = "{pkg_name}"}}]

[tool.poetry.dependencies]
python = "{python}"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
'''
        
        (path / "pyproject.toml").write_text(content, encoding='utf-8')
    
    def _generate_readme(self, path: Path, name: str, 
                         options: Dict) -> None:
        """生成README.md文件"""
        description = options.get("description", f"{name} project")
        
        content = f'''# {name}

{description}

## Installation

```bash
pip install {name}
```

## Usage

```python
from {self._normalize_package_name(name)} import *

# TODO: Add usage example
```

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest
```

## License

{options.get("license", "MIT")}
'''
        
        (path / "README.md").write_text(content, encoding='utf-8')
    
    def _generate_init_file(self, path: Path, pkg_name: str) -> None:
        """生成__init__.py文件"""
        content = f'''"""{pkg_name} package"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "you@example.com"
'''
        (path / "__init__.py").write_text(content, encoding='utf-8')
    
    def _generate_test_init(self, path: Path) -> None:
        """生成tests/__init__.py文件"""
        content = '"""Tests package"""\n'
        (path / "__init__.py").write_text(content, encoding='utf-8')
    
    def _generate_gitignore(self, path: Path) -> None:
        """生成.gitignore文件"""
        content = '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
.venv/
venv/
ENV/

# Distribution / packaging
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

# PyCharm
.idea/

# VS Code
.vscode/

# Jupyter Notebook
.ipynb_checkpoints

# pytest
.pytest_cache/

# mypy
.mypy_cache/
.dmypy.json
'''
        (path / ".gitignore").write_text(content, encoding='utf-8')
    
    def add_dependency(self, package: str, version: Optional[str] = None,
                       **options) -> Dict[str, Any]:
        """
        添加依赖
        
        Args:
            package: 包名
            version: 版本约束（可选）
            **options: 选项
                - dev: 是否为开发依赖
                - group: 依赖组名
                - optional: 是否为可选依赖
                - extras: 额外依赖列表
                
        Returns:
            操作结果
        """
        cmd = ["poetry", "add"]
        
        # 处理版本
        if version:
            package_spec = f"{package}@{version}"
        else:
            package_spec = package
        
        # 处理选项
        if options.get("dev", False):
            cmd.append("--group=dev")
        elif options.get("group"):
            cmd.append(f"--group={options['group']}")
        
        if options.get("optional", False):
            cmd.append("--optional")
        
        if options.get("extras"):
            for extra in options["extras"]:
                cmd.extend(["--extras", extra])
        
        cmd.append(package_spec)
        
        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=options.get("cwd")
        )
        
        return {
            "success": result.returncode == 0,
            "package": package,
            "version": version or "latest",
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def remove_dependency(self, package: str, **options) -> Dict[str, Any]:
        """
        删除依赖
        
        Args:
            package: 包名
            **options: 选项
                - dev: 是否为开发依赖
                - group: 依赖组名
                
        Returns:
            操作结果
        """
        cmd = ["poetry", "remove"]
        
        if options.get("dev", False):
            cmd.append("--group=dev")
        elif options.get("group"):
            cmd.append(f"--group={options['group']}")
        
        cmd.append(package)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=options.get("cwd")
        )
        
        return {
            "success": result.returncode == 0,
            "package": package,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def install(self, **options) -> Dict[str, Any]:
        """
        安装依赖
        
        Args:
            **options: 选项
                - without: 排除的组列表
                - with: 包含的组列表
                - no_dev: 不安装开发依赖
                - no_root: 不安装根包
                
        Returns:
            安装结果
        """
        cmd = ["poetry", "install"]
        
        if options.get("no_dev", False):
            cmd.append("--no-dev")
        
        if options.get("no_root", False):
            cmd.append("--no-root")
        
        if options.get("without"):
            for group in options["without"]:
                cmd.extend(["--without", group])
        
        if options.get("with_groups"):
            for group in options["with_groups"]:
                cmd.extend(["--with", group])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=options.get("cwd")
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def update(self, package: Optional[str] = None, 
               **options) -> Dict[str, Any]:
        """
        更新依赖
        
        Args:
            package: 包名（None表示更新所有）
            **options: 选项
                - lock_only: 只更新锁文件
                - dry_run: 试运行
                
        Returns:
            更新结果
        """
        cmd = ["poetry", "update"]
        
        if options.get("lock_only", False):
            cmd.append("--lock")
        
        if options.get("dry_run", False):
            cmd.append("--dry-run")
        
        if package:
            cmd.append(package)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=options.get("cwd")
        )
        
        return {
            "success": result.returncode == 0,
            "package": package or "all",
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def lock(self, **options) -> Dict[str, Any]:
        """
        锁定依赖版本
        
        Args:
            **options: 选项
                - no_update: 不更新已锁定的版本
                
        Returns:
            锁定结果
        """
        cmd = ["poetry", "lock"]
        
        if options.get("no_update", False):
            cmd.append("--no-update")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=options.get("cwd")
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def build(self, **options) -> BuildInfo:
        """
        构建包
        
        Args:
            **options: 选项
                - format: 构建格式 (wheel, sdist)
                - clean: 构建前清理
                
        Returns:
            构建信息
        """
        cmd = ["poetry", "build"]
        
        if options.get("format"):
            cmd.extend(["--format", options["format"]])
        
        if options.get("clean", False):
            cmd.append("--clean")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=options.get("cwd")
        )
        
        artifacts = []
        if result.returncode == 0:
            # 解析构建输出查找产物
            for line in result.stdout.split('\n'):
                if '- ' in line and ('.whl' in line or '.tar.gz' in line):
                    artifact = line.split('- ')[-1].strip()
                    artifacts.append(artifact)
        
        return BuildInfo(
            success=result.returncode == 0,
            artifacts=artifacts,
            errors=[result.stderr] if result.stderr else []
        )
    
    def publish(self, **options) -> Dict[str, Any]:
        """
        发布到PyPI
        
        Args:
            **options: 选项
                - username: PyPI用户名
                - password: PyPI密码
                - token: PyPI API token
                - repository: 目标仓库 (pypi/testpypi)
                - dry_run: 试运行
                
        Returns:
            发布结果
        """
        cmd = ["poetry", "publish"]
        
        if options.get("dry_run", False):
            cmd.append("--dry-run")
        
        if options.get("repository"):
            cmd.extend(["--repository", options["repository"]])
        
        # 认证信息
        env = os.environ.copy()
        if options.get("token"):
            env["POETRY_PYPI_TOKEN_PYPI"] = options["token"]
        elif options.get("username") and options.get("password"):
            env["POETRY_HTTP_BASIC_PYPI_USERNAME"] = options["username"]
            env["POETRY_HTTP_BASIC_PYPI_PASSWORD"] = options["password"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=options.get("cwd"),
            env=env
        )
        
        return {
            "success": result.returncode == 0,
            "repository": options.get("repository", "pypi"),
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def get_project_info(self, **options) -> ProjectInfo:
        """
        获取项目信息
        
        Args:
            **options: 选项
                
        Returns:
            项目信息
        """
        # 使用poetry show获取信息
        result = subprocess.run(
            ["poetry", "show", "--tree"],
            capture_output=True,
            text=True,
            cwd=options.get("cwd")
        )
        
        # 解析pyproject.toml获取基本信息
        pyproject_path = Path(options.get("cwd", ".")) / "pyproject.toml"
        
        if pyproject_path.exists():
            content = pyproject_path.read_text(encoding='utf-8')
            info = self._parse_pyproject_toml(content)
        else:
            info = ProjectInfo(name="unknown", version="0.0.0")
        
        return info
    
    def _parse_pyproject_toml(self, content: str) -> ProjectInfo:
        """解析pyproject.toml内容"""
        # 简化的TOML解析
        info = ProjectInfo(name="unknown", version="0.0.0")
        
        # 解析工具.poetry部分
        in_poetry = False
        in_deps = False
        in_dev_deps = False
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line == '[tool.poetry]':
                in_poetry = True
                in_deps = False
                in_dev_deps = False
                continue
            
            if line == '[tool.poetry.dependencies]':
                in_poetry = False
                in_deps = True
                in_dev_deps = False
                continue
            
            if line.startswith('[tool.poetry.group.dev.dependencies]'):
                in_poetry = False
                in_deps = False
                in_dev_deps = True
                continue
            
            if line.startswith('['):
                in_poetry = False
                in_deps = False
                in_dev_deps = False
                continue
            
            if in_poetry and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                
                if key == 'name':
                    info.name = value
                elif key == 'version':
                    info.version = value
                elif key == 'description':
                    info.description = value
                elif key == 'readme':
                    info.readme = value
                elif key == 'license':
                    info.license = value
                elif key == 'homepage':
                    info.homepage = value
                elif key == 'repository':
                    info.repository = value
            
            if (in_deps or in_dev_deps) and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                
                if key != 'python':
                    if in_deps:
                        info.dependencies[key] = value
                    else:
                        info.dev_dependencies[key] = value
                else:
                    info.python_version = value
        
        return info
    
    def manage_venv(self, action: str, **options) -> Dict[str, Any]:
        """
        管理虚拟环境
        
        Args:
            action: 操作 (create, remove, list, info)
            **options: 选项
                - python: Python版本
                
        Returns:
            操作结果
        """
        if action == "create":
            cmd = ["poetry", "env", "use", options.get("python", "python3")]
        elif action == "remove":
            cmd = ["poetry", "env", "remove", "python"]
        elif action == "list":
            cmd = ["poetry", "env", "list"]
        elif action == "info":
            cmd = ["poetry", "env", "info"]
        else:
            return {"success": False, "error": f"未知操作: {action}"}
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=options.get("cwd")
        )
        
        return {
            "success": result.returncode == 0,
            "action": action,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def export_requirements(self, output_path: Union[str, Path],
                            **options) -> Dict[str, Any]:
        """
        导出requirements.txt
        
        Args:
            output_path: 输出路径
            **options: 选项
                - dev: 包含开发依赖
                - without_hashes: 不包含哈希
                
        Returns:
            导出结果
        """
        cmd = ["poetry", "export", "-f", "requirements.txt", 
               "-o", str(output_path)]
        
        if options.get("dev", False):
            cmd.append("--with=dev")
        
        if options.get("without_hashes", True):
            cmd.append("--without-hashes")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=options.get("cwd")
        )
        
        return {
            "success": result.returncode == 0,
            "output_path": str(output_path),
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def validate_build(self, **options) -> bool:
        """
        验证构建
        
        Args:
            **options: 选项
                
        Returns:
            是否有效
        """
        # 检查pyproject.toml
        pyproject_path = Path(options.get("cwd", ".")) / "pyproject.toml"
        if not pyproject_path.exists():
            return False
        
        # 检查必要的字段
        content = pyproject_path.read_text(encoding='utf-8')
        required = ['[tool.poetry]', 'name', 'version', '[build-system]']
        
        for field in required:
            if field not in content:
                return False
        
        return True


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Poetry Package Management Skill")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # init 命令
    init_parser = subparsers.add_parser("init", help="初始化项目")
    init_parser.add_argument("name", help="项目名称")
    init_parser.add_argument("--description", default="", help="项目描述")
    init_parser.add_argument("--author", default="", help="作者")
    init_parser.add_argument("--python", default="^3.8", help="Python版本")
    
    # add 命令
    add_parser = subparsers.add_parser("add", help="添加依赖")
    add_parser.add_argument("package", help="包名")
    add_parser.add_argument("--version", help="版本")
    add_parser.add_argument("--dev", action="store_true", help="开发依赖")
    add_parser.add_argument("--group", help="依赖组")
    
    # remove 命令
    remove_parser = subparsers.add_parser("remove", help="删除依赖")
    remove_parser.add_argument("package", help="包名")
    remove_parser.add_argument("--dev", action="store_true", help="开发依赖")
    
    # install 命令
    install_parser = subparsers.add_parser("install", help="安装依赖")
    install_parser.add_argument("--no-dev", action="store_true", help="不安装开发依赖")
    
    # update 命令
    update_parser = subparsers.add_parser("update", help="更新依赖")
    update_parser.add_argument("package", nargs="?", help="包名")
    
    # build 命令
    build_parser = subparsers.add_parser("build", help="构建包")
    build_parser.add_argument("--format", choices=["wheel", "sdist"], help="格式")
    
    # publish 命令
    publish_parser = subparsers.add_parser("publish", help="发布包")
    publish_parser.add_argument("--token", help="API Token")
    publish_parser.add_argument("--username", help="用户名")
    publish_parser.add_argument("--password", help="密码")
    
    # info 命令
    info_parser = subparsers.add_parser("info", help="项目信息")
    
    # export 命令
    export_parser = subparsers.add_parser("export", help="导出requirements")
    export_parser.add_argument("output", help="输出路径")
    export_parser.add_argument("--dev", action="store_true", help="包含开发依赖")
    
    args = parser.parse_args()
    
    skill = PoetrySkill()
    
    if args.command == "init":
        result = skill.init_project(
            args.name,
            description=args.description,
            author=args.author,
            python=args.python
        )
        print(f"项目已创建: {result['project_path']}")
    
    elif args.command == "add":
        result = skill.add_dependency(
            args.package,
            args.version,
            dev=args.dev,
            group=args.group
        )
        print(f"添加依赖: {result['success']}")
    
    elif args.command == "remove":
        result = skill.remove_dependency(args.package, dev=args.dev)
        print(f"删除依赖: {result['success']}")
    
    elif args.command == "install":
        result = skill.install(no_dev=args.no_dev)
        print(f"安装: {result['success']}")
    
    elif args.command == "update":
        result = skill.update(args.package)
        print(f"更新: {result['success']}")
    
    elif args.command == "build":
        result = skill.build(format=args.format)
        print(f"构建: {result.success}")
        if result.artifacts:
            print("产物:")
            for artifact in result.artifacts:
                print(f"  - {artifact}")
    
    elif args.command == "publish":
        result = skill.publish(
            token=args.token,
            username=args.username,
            password=args.password
        )
        print(f"发布: {result['success']}")
    
    elif args.command == "info":
        info = skill.get_project_info()
        print(f"名称: {info.name}")
        print(f"版本: {info.version}")
        print(f"描述: {info.description}")
        print(f"依赖数: {len(info.dependencies)}")
    
    elif args.command == "export":
        result = skill.export_requirements(args.output, dev=args.dev)
        print(f"导出: {result['success']}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
