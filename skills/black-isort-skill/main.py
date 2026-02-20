"""
black-isort-skill: Python代码格式化Skill
集成Black和isort提供统一的代码格式化解决方案
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import difflib
import tempfile


@dataclass
class FormatResult:
    """格式化结果数据类"""
    file_path: str
    success: bool
    changed: bool = False
    original_content: str = ""
    formatted_content: str = ""
    error_message: str = ""
    line_count_change: int = 0


@dataclass
class FormatConfig:
    """格式化配置数据类"""
    line_length: int = 88
    target_version: List[str] = field(default_factory=lambda: ["py38", "py39", "py310"])
    skip_string_normalization: bool = False
    isort_profile: str = "black"
    skip_files: List[str] = field(default_factory=list)
    skip_directories: List[str] = field(default_factory=lambda: [
        ".git", ".venv", "venv", "__pycache__", ".mypy_cache"
    ])


class BlackIsortSkill:
    """
    Python代码格式化Skill主类
    
    提供功能:
    - Black代码格式化
    - isort导入排序
    - 项目配置管理
    - 批量格式化
    - 差异报告
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = FormatConfig()
        if config:
            self._update_config(config)
        
        # 验证依赖
        self._check_dependencies()
    
    def _update_config(self, config: Dict):
        """更新配置"""
        if "line_length" in config:
            self.config.line_length = config["line_length"]
        if "target_version" in config:
            self.config.target_version = config["target_version"]
        if "skip_string_normalization" in config:
            self.config.skip_string_normalization = config["skip_string_normalization"]
        if "isort_profile" in config:
            self.config.isort_profile = config["isort_profile"]
        if "skip_files" in config:
            self.config.skip_files = config["skip_files"]
    
    def _check_dependencies(self):
        """检查Black和isort是否已安装"""
        try:
            import black
            self.black_available = True
        except ImportError:
            self.black_available = False
        
        try:
            import isort
            self.isort_available = True
        except ImportError:
            self.isort_available = False
    
    def format_code(self, code: str, **options) -> str:
        """
        格式化代码字符串
        
        Args:
            code: 原始代码字符串
            **options: 格式化选项
                - line_length: 行长度
                - skip_string_normalization: 跳过字符串规范化
                - isort: 是否运行isort (默认True)
                
        Returns:
            格式化后的代码
        """
        isort_enabled = options.get("isort", True)
        
        # 先运行isort (如果启用)
        if isort_enabled and self.isort_available:
            code = self._run_isort_on_code(code, **options)
        
        # 然后运行black
        if self.black_available:
            code = self._run_black_on_code(code, **options)
        
        return code
    
    def _run_isort_on_code(self, code: str, **options) -> str:
        """使用isort格式化代码"""
        try:
            import isort
            
            profile = options.get("isort_profile", self.config.isort_profile)
            line_length = options.get("line_length", self.config.line_length)
            
            result = isort.code(
                code,
                profile=profile,
                line_length=line_length,
                multi_line_output=3,
                include_trailing_comma=True,
                force_grid_wrap=0,
                use_parentheses=True,
                ensure_newline_before_comments=True,
            )
            return result
        except Exception as e:
            # isort失败时返回原代码
            return code
    
    def _run_black_on_code(self, code: str, **options) -> str:
        """使用black格式化代码"""
        try:
            import black
            
            line_length = options.get("line_length", self.config.line_length)
            skip_string_norm = options.get(
                "skip_string_normalization", 
                self.config.skip_string_normalization
            )
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False, encoding='utf-8'
            ) as f:
                f.write(code)
                temp_path = f.name
            
            try:
                # 构建black命令
                cmd = [
                    sys.executable, "-m", "black",
                    "--line-length", str(line_length),
                    "--quiet",
                ]
                
                if skip_string_norm:
                    cmd.append("--skip-string-normalization")
                
                cmd.append(temp_path)
                
                # 运行black
                result = subprocess.run(
                    cmd, capture_output=True, text=True
                )
                
                # 读取格式化后的代码
                with open(temp_path, 'r', encoding='utf-8') as f:
                    formatted = f.read()
                
                return formatted
            finally:
                os.unlink(temp_path)
                
        except Exception as e:
            return code
    
    def format_file(self, file_path: Union[str, Path], **options) -> FormatResult:
        """
        格式化单个文件
        
        Args:
            file_path: 文件路径
            **options: 格式化选项
                - check_only: 只检查不修改
                - backup: 创建备份
                
        Returns:
            FormatResult对象
        """
        path = Path(file_path)
        
        if not path.exists():
            return FormatResult(
                file_path=str(path),
                success=False,
                error_message="文件不存在"
            )
        
        if not path.suffix == ".py":
            return FormatResult(
                file_path=str(path),
                success=False,
                error_message="不是Python文件"
            )
        
        # 检查是否应该跳过
        if self._should_skip(path):
            return FormatResult(
                file_path=str(path),
                success=True,
                changed=False,
                error_message="文件在跳过列表中"
            )
        
        try:
            original = path.read_text(encoding='utf-8')
            formatted = self.format_code(original, **options)
            
            result = FormatResult(
                file_path=str(path),
                success=True,
                original_content=original,
                formatted_content=formatted,
                changed=original != formatted,
                line_count_change=formatted.count('\n') - original.count('\n')
            )
            
            # 如果不是仅检查，写入文件
            if not options.get("check_only", False) and result.changed:
                if options.get("backup", False):
                    backup_path = path.with_suffix(path.suffix + ".bak")
                    backup_path.write_text(original, encoding='utf-8')
                
                path.write_text(formatted, encoding='utf-8')
            
            return result
            
        except Exception as e:
            return FormatResult(
                file_path=str(path),
                success=False,
                error_message=str(e)
            )
    
    def _should_skip(self, path: Path) -> bool:
        """检查是否应该跳过该文件"""
        # 检查文件名
        if path.name in self.config.skip_files:
            return True
        
        # 检查目录
        for part in path.parts:
            if part in self.config.skip_directories:
                return True
        
        return False
    
    def format_project(
        self, 
        project_path: Union[str, Path], 
        **options
    ) -> Dict[str, Any]:
        """
        批量格式化项目
        
        Args:
            project_path: 项目路径
            **options: 格式化选项
                - pattern: 文件匹配模式 (默认 "*.py")
                - recursive: 是否递归 (默认 True)
                - check_only: 只检查不修改
                - parallel: 并行处理
                
        Returns:
            格式化结果统计
        """
        path = Path(project_path)
        pattern = options.get("pattern", "*.py")
        recursive = options.get("recursive", True)
        
        # 收集文件
        if recursive:
            files = list(path.rglob(pattern))
        else:
            files = list(path.glob(pattern))
        
        # 过滤跳过的文件
        files = [f for f in files if not self._should_skip(f)]
        
        results = []
        changed_count = 0
        error_count = 0
        
        for file_path in files:
            result = self.format_file(file_path, **options)
            results.append(result)
            
            if result.changed:
                changed_count += 1
            if not result.success:
                error_count += 1
        
        return {
            "total_files": len(files),
            "formatted": changed_count,
            "unchanged": len(files) - changed_count - error_count,
            "errors": error_count,
            "needs_formatting": changed_count > 0,
            "results": results,
            "unformatted": [
                r.file_path for r in results 
                if r.changed or not r.success
            ]
        }
    
    def check_format(self, path: Union[str, Path], **options) -> List[Dict]:
        """
        检查格式，不修改文件
        
        Args:
            path: 文件或目录路径
            **options: 检查选项
            
        Returns:
            需要格式化的文件列表
        """
        options = {**options, "check_only": True}
        
        path = Path(path)
        issues = []
        
        if path.is_file():
            result = self.format_file(path, **options)
            if result.changed or not result.success:
                issues.append({
                    "file": str(path),
                    "changed": result.changed,
                    "error": result.error_message if not result.success else None
                })
        elif path.is_dir():
            result = self.format_project(path, **options)
            for r in result["results"]:
                if r.changed or not r.success:
                    issues.append({
                        "file": r.file_path,
                        "changed": r.changed,
                        "error": r.error_message if not r.success else None
                    })
        
        return issues
    
    def generate_diff(self, original: str, formatted: str, 
                      file_path: str = "<string>") -> str:
        """
        生成代码差异
        
        Args:
            original: 原始代码
            formatted: 格式化后代码
            file_path: 文件路径（用于显示）
            
        Returns:
            统一差异格式字符串
        """
        original_lines = original.splitlines(keepends=True)
        formatted_lines = formatted.splitlines(keepends=True)
        
        # 确保每行都有换行符
        if original_lines and not original_lines[-1].endswith('\n'):
            original_lines[-1] += '\n'
        if formatted_lines and not formatted_lines[-1].endswith('\n'):
            formatted_lines[-1] += '\n'
        
        diff = difflib.unified_diff(
            original_lines,
            formatted_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
        )
        
        return "".join(diff)
    
    def is_formatted(self, file_path: Union[str, Path]) -> bool:
        """
        检查文件是否已格式化
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否已格式化
        """
        result = self.format_file(file_path, check_only=True)
        return result.success and not result.changed
    
    def configure_project(self, config_path: Union[str, Path], 
                          settings: Dict[str, Any]) -> bool:
        """
        配置项目格式化规则
        
        Args:
            config_path: 配置文件路径 (pyproject.toml)
            settings: 配置设置
            
        Returns:
            是否成功
        """
        path = Path(config_path)
        
        if path.name == "pyproject.toml":
            return self._write_pyproject_toml(path, settings)
        elif path.name == ".black":
            return self._write_black_config(path, settings)
        elif path.name == ".isort.cfg":
            return self._write_isort_config(path, settings)
        else:
            raise ValueError("不支持的配置文件类型")
    
    def _write_pyproject_toml(self, path: Path, settings: Dict) -> bool:
        """写入pyproject.toml配置"""
        black_settings = settings.get("black", {})
        isort_settings = settings.get("isort", {})
        
        lines = []
        
        # 读取现有内容
        if path.exists():
            existing = path.read_text(encoding='utf-8')
            lines = existing.split('\n')
            # 移除旧的black/isort配置
            lines = self._remove_tool_config(lines, "tool.black")
            lines = self._remove_tool_config(lines, "tool.isort")
        
        content = '\n'.join(lines)
        
        # 添加Black配置
        if black_settings:
            content += "\n\n[tool.black]\n"
            for key, value in black_settings.items():
                if isinstance(value, list):
                    content += f'{key} = ["' + '", "'.join(value) + '"]\n'
                elif isinstance(value, bool):
                    content += f'{key} = {str(value).lower()}\n'
                elif isinstance(value, str):
                    content += f'{key} = "{value}"\n'
                else:
                    content += f'{key} = {value}\n'
        
        # 添加isort配置
        if isort_settings:
            content += "\n[tool.isort]\n"
            for key, value in isort_settings.items():
                if isinstance(value, list):
                    content += f'{key} = ["' + '", "'.join(value) + '"]\n'
                elif isinstance(value, bool):
                    content += f'{key} = {str(value).lower()}\n'
                elif isinstance(value, str):
                    content += f'{key} = "{value}"\n'
                else:
                    content += f'{key} = {value}\n'
        
        path.write_text(content.strip() + '\n', encoding='utf-8')
        return True
    
    def _remove_tool_config(self, lines: List[str], section: str) -> List[str]:
        """从TOML行中移除特定工具配置"""
        result = []
        in_section = False
        
        for line in lines:
            if line.strip().startswith(f"[{section}]"):
                in_section = True
                continue
            elif in_section:
                if line.strip().startswith('[') and not line.strip().startswith('[['):
                    in_section = False
                else:
                    continue
            result.append(line)
        
        return result
    
    def _write_black_config(self, path: Path, settings: Dict) -> bool:
        """写入.black配置文件"""
        lines = ["[tool.black]"]
        for key, value in settings.items():
            if isinstance(value, list):
                lines.append(f'{key} = "' + '", "'.join(value) + '"')
            else:
                lines.append(f'{key} = {value}')
        
        path.write_text('\n'.join(lines), encoding='utf-8')
        return True
    
    def _write_isort_config(self, path: Path, settings: Dict) -> bool:
        """写入.isort.cfg配置文件"""
        lines = ["[settings]"]
        for key, value in settings.items():
            if isinstance(value, list):
                lines.append(f'{key} = "' + '", "'.join(value) + '"')
            else:
                lines.append(f'{key} = {value}')
        
        path.write_text('\n'.join(lines), encoding='utf-8')
        return True
    
    def get_git_changed_files(self, repo_path: str = ".") -> List[str]:
        """
        获取Git变更的文件列表
        
        Args:
            repo_path: 仓库路径
            
        Returns:
            变更文件路径列表
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=ACM", "HEAD"],
                capture_output=True,
                text=True,
                cwd=repo_path
            )
            
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                return [f for f in files if f.endswith('.py')]
            
            return []
        except Exception:
            return []
    
    def format_git_changed(self, repo_path: str = ".", **options) -> Dict[str, Any]:
        """
        只格式化Git变更的文件
        
        Args:
            repo_path: 仓库路径
            **options: 格式化选项
            
        Returns:
            格式化结果
        """
        changed_files = self.get_git_changed_files(repo_path)
        
        results = []
        for file_path in changed_files:
            full_path = Path(repo_path) / file_path
            if full_path.exists():
                result = self.format_file(full_path, **options)
                results.append(result)
        
        changed_count = sum(1 for r in results if r.changed)
        
        return {
            "total_files": len(results),
            "formatted": changed_count,
            "unchanged": len(results) - changed_count,
            "results": results
        }


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Black-Isort Formatting Skill")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # format 命令
    fmt_parser = subparsers.add_parser("format", help="格式化代码")
    fmt_parser.add_argument("path", help="文件或目录路径")
    fmt_parser.add_argument("-c", "--check", action="store_true", help="只检查")
    fmt_parser.add_argument("-l", "--line-length", type=int, default=88, help="行长度")
    fmt_parser.add_argument("--no-isort", action="store_true", help="跳过isort")
    
    # check 命令
    check_parser = subparsers.add_parser("check", help="检查格式")
    check_parser.add_argument("path", help="文件或目录路径")
    
    # diff 命令
    diff_parser = subparsers.add_parser("diff", help="显示差异")
    diff_parser.add_argument("path", help="文件路径")
    
    # config 命令
    config_parser = subparsers.add_parser("config", help="配置项目")
    config_parser.add_argument("path", default="pyproject.toml", help="配置文件路径")
    
    args = parser.parse_args()
    
    skill = BlackIsortSkill()
    
    if args.command == "format":
        options = {
            "check_only": args.check,
            "line_length": args.line_length,
            "isort": not args.no_isort
        }
        
        path = Path(args.path)
        if path.is_file():
            result = skill.format_file(path, **options)
            print(f"文件: {result.file_path}")
            print(f"已更改: {result.changed}")
            if result.error_message:
                print(f"错误: {result.error_message}")
        else:
            result = skill.format_project(path, **options)
            print(f"总文件数: {result['total_files']}")
            print(f"已格式化: {result['formatted']}")
            print(f"未更改: {result['unchanged']}")
            print(f"错误: {result['errors']}")
    
    elif args.command == "check":
        issues = skill.check_format(args.path)
        if issues:
            print(f"发现 {len(issues)} 个文件需要格式化:")
            for issue in issues:
                print(f"  - {issue['file']}")
            sys.exit(1)
        else:
            print("所有文件格式正确!")
    
    elif args.command == "diff":
        path = Path(args.path)
        result = skill.format_file(path, check_only=True)
        if result.changed:
            diff = skill.generate_diff(
                result.original_content,
                result.formatted_content,
                str(path)
            )
            print(diff)
    
    elif args.command == "config":
        settings = {
            "black": {
                "line-length": 88,
                "target-version": ["py38", "py39", "py310"]
            },
            "isort": {
                "profile": "black"
            }
        }
        skill.configure_project(args.path, settings)
        print(f"配置已写入: {args.path}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
