"""
mypy-skill: Python类型检查Skill
提供类型检查、错误修复、配置优化功能
"""

import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class TypeError:
    """类型错误数据类"""
    file_path: str
    line: int
    column: int
    severity: str  # error, warning, note
    code: str
    message: str
    error_type: str = ""  # 错误分类
    suggestion: str = ""


@dataclass
class TypeCheckResult:
    """类型检查结果数据类"""
    success: bool
    file_path: str
    errors: List[TypeError] = field(default_factory=list)
    warnings: List[TypeError] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def error_count(self) -> int:
        return len(self.errors)
    
    @property
    def warning_count(self) -> int:
        return len(self.warnings)


@dataclass
class AnnotationInfo:
    """类型注解信息"""
    name: str
    line: int
    col_offset: int
    suggested_type: str
    confidence: float
    context: str = ""


class MypySkill:
    """
    Python类型检查Skill主类
    
    提供功能:
    - 类型检查
    - 错误修复
    - 类型注解生成
    - 配置管理
    """
    
    # 错误代码分类
    ERROR_CATEGORIES = {
        "arg-type": "参数类型错误",
        "assignment": "赋值类型错误",
        "return-value": "返回值类型错误",
        "var-annotated": "变量注解缺失",
        "no-redef": "重复定义",
        "misc": "其他错误",
        "union-attr": "Union属性访问",
        "operator": "操作符错误",
        "index": "索引错误",
        "list-item": "列表元素类型",
        "dict-item": "字典元素类型",
        "attr-defined": "属性未定义",
        "name-defined": "名称未定义",
        "call-arg": "调用参数错误",
        "call-overload": "重载调用错误",
    }
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.strict_mode = self.config.get("strict_mode", False)
        self.ignore_missing_imports = self.config.get("ignore_missing_imports", True)
        self.disallow_untyped_defs = self.config.get("disallow_untyped_defs", False)
        self.python_version = self.config.get("python_version", "3.10")
        self.show_error_codes = self.config.get("show_error_codes", True)
        
        self._check_mypy_installation()
    
    def _check_mypy_installation(self):
        """检查mypy是否已安装"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "mypy", "--version"],
                capture_output=True,
                text=True
            )
            self.mypy_available = result.returncode == 0
        except Exception:
            self.mypy_available = False
    
    def check_file(self, file_path: Union[str, Path], **options) -> TypeCheckResult:
        """
        检查单个文件
        
        Args:
            file_path: 文件路径
            **options: 检查选项
                - strict: 严格模式
                - ignore_missing: 忽略缺失导入
                
        Returns:
            类型检查结果
        """
        path = Path(file_path)
        
        if not path.exists():
            return TypeCheckResult(
                success=False,
                file_path=str(path),
                errors=[TypeError(
                    file_path=str(path),
                    line=0,
                    column=0,
                    severity="error",
                    code="file-not-found",
                    message=f"文件不存在: {path}"
                )]
            )
        
        # 构建mypy命令
        cmd = self._build_mypy_command(str(path), **options)
        
        # 运行mypy
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=options.get("cwd")
        )
        
        # 解析输出
        errors = self._parse_mypy_output(result.stdout)
        
        # 分类错误
        categorized_errors = []
        warnings = []
        
        for error in errors:
            error.error_type = self.ERROR_CATEGORIES.get(error.code, "其他")
            if error.severity == "error":
                categorized_errors.append(error)
            else:
                warnings.append(error)
        
        return TypeCheckResult(
            success=len(categorized_errors) == 0,
            file_path=str(path),
            errors=categorized_errors,
            warnings=warnings,
            stats={
                "error_count": len(categorized_errors),
                "warning_count": len(warnings),
                "by_code": self._group_by_code(categorized_errors)
            }
        )
    
    def check_project(self, project_path: Union[str, Path], 
                      **options) -> Dict[str, Any]:
        """
        检查整个项目
        
        Args:
            project_path: 项目路径
            **options: 检查选项
                
        Returns:
            检查结果统计
        """
        path = Path(project_path)
        
        # 查找所有Python文件
        files = list(path.rglob("*.py"))
        files = [f for f in files if not self._should_skip(f)]
        
        all_errors = []
        all_warnings = []
        file_results = []
        
        for py_file in files:
            result = self.check_file(py_file, **options)
            file_results.append(result)
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
        
        # 生成统计
        stats = {
            "total_files": len(files),
            "files_with_errors": sum(1 for r in file_results if r.error_count > 0),
            "files_clean": sum(1 for r in file_results if r.error_count == 0),
            "total_errors": len(all_errors),
            "total_warnings": len(all_warnings),
            "by_category": self._group_by_category(all_errors),
            "by_file": self._group_by_file(all_errors),
        }
        
        return {
            "success": len(all_errors) == 0,
            "error_count": len(all_errors),
            "warning_count": len(all_warnings),
            "stats": stats,
            "errors": [
                {
                    "file": e.file_path,
                    "line": e.line,
                    "column": e.column,
                    "code": e.code,
                    "message": e.message,
                    "type": e.error_type
                }
                for e in all_errors
            ],
            "file_results": file_results
        }
    
    def _build_mypy_command(self, target: str, **options) -> List[str]:
        """构建mypy命令"""
        cmd = [sys.executable, "-m", "mypy"]
        
        # 基本选项
        if options.get("strict", self.strict_mode):
            cmd.append("--strict")
        
        if options.get("ignore_missing", self.ignore_missing_imports):
            cmd.append("--ignore-missing-imports")
        
        if options.get("show_error_codes", self.show_error_codes):
            cmd.append("--show-error-codes")
        
        if options.get("show_column_numbers", True):
            cmd.append("--show-column-numbers")
        
        # Python版本
        python_version = options.get("python_version", self.python_version)
        cmd.extend(["--python-version", python_version])
        
        # 输出格式
        cmd.append("--show-traceback")
        
        # 目标
        cmd.append(target)
        
        return cmd
    
    def _parse_mypy_output(self, output: str) -> List[TypeError]:
        """解析mypy输出"""
        errors = []
        
        # 解析错误行格式: file.py:10:5: error: message [error-code]
        pattern = r'^(.*?):(\d+):(\d+):\s*(error|warning|note):\s*(.*?)(?:\s*\[(\w+)\])?$'
        
        for line in output.split('\n'):
            match = re.match(pattern, line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))
                col_num = int(match.group(3))
                severity = match.group(4)
                message = match.group(5)
                code = match.group(6) or "misc"
                
                error = TypeError(
                    file_path=file_path,
                    line=line_num,
                    column=col_num,
                    severity=severity,
                    code=code,
                    message=message
                )
                
                # 生成修复建议
                error.suggestion = self._generate_suggestion(error)
                
                errors.append(error)
        
        return errors
    
    def _generate_suggestion(self, error: TypeError) -> str:
        """根据错误生成修复建议"""
        suggestions = {
            "arg-type": "检查参数类型是否与函数签名匹配",
            "assignment": "确保赋值右侧类型与左侧变量类型兼容",
            "return-value": "确保返回值类型与函数声明的返回类型一致",
            "var-annotated": "为变量添加类型注解，如 `x: int = 1`",
            "no-redef": "移除重复定义或重命名变量",
            "attr-defined": "检查属性名拼写或确认类定义",
            "name-defined": "检查导入语句或变量名拼写",
            "call-arg": "检查函数调用参数数量和类型",
            "union-attr": "使用 isinstance() 检查具体类型后再访问属性",
            "operator": "检查操作数类型是否支持该操作符",
            "index": "确保索引类型正确，如整数用于列表",
        }
        
        return suggestions.get(error.code, "查看mypy文档了解此错误的修复方法")
    
    def _group_by_code(self, errors: List[TypeError]) -> Dict[str, int]:
        """按错误代码分组统计"""
        counts = defaultdict(int)
        for error in errors:
            counts[error.code] += 1
        return dict(counts)
    
    def _group_by_category(self, errors: List[TypeError]) -> Dict[str, int]:
        """按错误类别分组统计"""
        counts = defaultdict(int)
        for error in errors:
            counts[error.error_type] += 1
        return dict(counts)
    
    def _group_by_file(self, errors: List[TypeError]) -> Dict[str, int]:
        """按文件分组统计"""
        counts = defaultdict(int)
        for error in errors:
            counts[error.file_path] += 1
        return dict(counts)
    
    def _should_skip(self, path: Path) -> bool:
        """检查是否应该跳过该文件"""
        skip_dirs = ['.venv', 'venv', '__pycache__', '.mypy_cache', '.git']
        for part in path.parts:
            if part in skip_dirs:
                return True
        return False
    
    def fix_errors(self, file_path: Union[str, Path], 
                   **options) -> Dict[str, Any]:
        """
        自动修复类型错误
        
        Args:
            file_path: 文件路径
            **options: 修复选项
                - auto_fix: 自动修复类型
                - dry_run: 仅预览不保存
                
        Returns:
            修复结果
        """
        path = Path(file_path)
        
        # 先检查
        check_result = self.check_file(path, **options)
        
        if not check_result.errors:
            return {
                "success": True,
                "fixed_count": 0,
                "message": "没有发现需要修复的错误"
            }
        
        try:
            content = path.read_text(encoding='utf-8')
            original_content = content
            lines = content.split('\n')
            fixed_count = 0
            fixes = []
            
            # 修复可自动修复的错误
            for error in check_result.errors:
                if error.line > 0 and error.line <= len(lines):
                    line_idx = error.line - 1
                    original_line = lines[line_idx]
                    fixed_line = self._fix_single_error(
                        original_line, error, lines, line_idx
                    )
                    
                    if fixed_line != original_line:
                        lines[line_idx] = fixed_line
                        fixed_count += 1
                        fixes.append({
                            "line": error.line,
                            "code": error.code,
                            "original": original_line,
                            "fixed": fixed_line
                        })
            
            # 保存（如果不是dry run）
            if not options.get("dry_run", False) and fixed_count > 0:
                new_content = '\n'.join(lines)
                path.write_text(new_content, encoding='utf-8')
            
            return {
                "success": True,
                "fixed_count": fixed_count,
                "fixes": fixes,
                "dry_run": options.get("dry_run", False)
            }
            
        except Exception as e:
            return {
                "success": False,
                "fixed_count": 0,
                "error": str(e)
            }
    
    def _fix_single_error(self, line: str, error: TypeError, 
                          all_lines: List[str], line_idx: int) -> str:
        """修复单个错误"""
        # 缺失类型注解
        if error.code == "var-annotated":
            return self._add_type_annotation(line, error)
        
        # 缺失返回值注解
        if error.code == "return-value" and "Missing return" in error.message:
            return self._add_return_annotation(line, error)
        
        # 其他错误添加 type: ignore
        if error.code in ["attr-defined", "name-defined", "arg-type"]:
            return self._add_type_ignore(line, error)
        
        return line
    
    def _add_type_annotation(self, line: str, error: TypeError) -> str:
        """添加类型注解"""
        # 简单推断类型
        match = re.match(r'^(\s*)(\w+)\s*=\s*(.+)$', line)
        if match:
            indent = match.group(1)
            var_name = match.group(2)
            value = match.group(3)
            
            # 基于值推断类型
            inferred_type = self._infer_type(value)
            
            return f"{indent}{var_name}: {inferred_type} = {value}"
        
        return line
    
    def _add_return_annotation(self, line: str, error: TypeError) -> str:
        """添加返回值注解"""
        match = re.match(r'^(\s*)def\s+(\w+)\s*\((.*?)\)\s*:', line)
        if match:
            indent = match.group(1)
            func_name = match.group(2)
            params = match.group(3)
            return f"{indent}def {func_name}({params}) -> None:"
        return line
    
    def _add_type_ignore(self, line: str, error: TypeError) -> str:
        """添加type: ignore注释"""
        # 移除行尾已有注释
        line = line.rstrip()
        if '#' in line:
            line = line[:line.index('#')].rstrip()
        
        return f"{line}  # type: ignore[{error.code}]"
    
    def _infer_type(self, value: str) -> str:
        """基于值推断类型"""
        value = value.strip()
        
        # 字符串
        if value.startswith('"') or value.startswith("'"):
            return "str"
        
        # 数字
        if re.match(r'^-?\d+$', value):
            return "int"
        if re.match(r'^-?\d+\.\d+$', value):
            return "float"
        
        # 布尔
        if value in ["True", "False"]:
            return "bool"
        
        # 空值
        if value == "None":
            return "Optional[Any]"
        
        # 列表
        if value.startswith('[') and value.endswith(']'):
            return "list"
        
        # 字典
        if value.startswith('{') and value.endswith('}'):
            return "dict"
        
        # 元组
        if value.startswith('(') and value.endswith(')'):
            return "tuple"
        
        return "Any"
    
    def generate_annotations(self, file_path: Union[str, Path],
                             **options) -> str:
        """
        为文件生成类型注解
        
        Args:
            file_path: 文件路径
            **options: 生成选项
                
        Returns:
            带类型注解的代码
        """
        path = Path(file_path)
        
        if not path.exists():
            return f"# 文件不存在: {path}"
        
        try:
            content = path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            # 收集需要注解的位置
            annotations = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_annotations = self._analyze_function(node)
                    annotations.extend(func_annotations)
            
            # 应用注解
            lines = content.split('\n')
            for ann in sorted(annotations, key=lambda x: x.line, reverse=True):
                if ann.line <= len(lines):
                    line_idx = ann.line - 1
                    line = lines[line_idx]
                    
                    # 在适当位置插入注解
                    if ann.context == "return":
                        lines[line_idx] = self._insert_return_annotation(
                            line, ann.suggested_type
                        )
                    elif ann.context == "param":
                        lines[line_idx] = self._insert_param_annotation(
                            line, ann.name, ann.suggested_type
                        )
            
            return '\n'.join(lines)
            
        except SyntaxError as e:
            return f"# 语法错误: {e}"
        except Exception as e:
            return f"# 错误: {e}"
    
    def _analyze_function(self, node: ast.FunctionDef) -> List[AnnotationInfo]:
        """分析函数，返回注解建议"""
        annotations = []
        
        # 检查返回值
        if node.returns is None and node.body:
            # 推断返回类型
            return_type = self._infer_return_type(node)
            if return_type:
                annotations.append(AnnotationInfo(
                    name=node.name,
                    line=node.lineno,
                    col_offset=node.col_offset,
                    suggested_type=return_type,
                    confidence=0.7,
                    context="return"
                ))
        
        # 检查参数
        for arg in node.args.args:
            if arg.arg not in ['self', 'cls'] and arg.annotation is None:
                param_type = self._infer_param_type(arg.arg, node)
                if param_type:
                    annotations.append(AnnotationInfo(
                        name=arg.arg,
                        line=node.lineno,
                        col_offset=node.col_offset,
                        suggested_type=param_type,
                        confidence=0.5,
                        context="param"
                    ))
        
        return annotations
    
    def _infer_return_type(self, node: ast.FunctionDef) -> str:
        """推断函数返回类型"""
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value:
                return self._infer_type_from_ast(child.value)
        return "None"
    
    def _infer_param_type(self, param_name: str, node: ast.FunctionDef) -> str:
        """推断参数类型"""
        # 简单启发式：基于参数名推断
        type_hints = {
            'name': 'str',
            'text': 'str',
            'value': 'Any',
            'count': 'int',
            'index': 'int',
            'flag': 'bool',
            'items': 'list',
            'data': 'dict',
            'callback': 'Callable',
            'timeout': 'float',
        }
        return type_hints.get(param_name, "")
    
    def _infer_type_from_ast(self, node: ast.AST) -> str:
        """从AST节点推断类型"""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                return "str"
            elif isinstance(node.value, int):
                return "int"
            elif isinstance(node.value, float):
                return "float"
            elif isinstance(node.value, bool):
                return "bool"
            elif node.value is None:
                return "None"
        elif isinstance(node, ast.List):
            return "list"
        elif isinstance(node, ast.Dict):
            return "dict"
        elif isinstance(node, ast.Tuple):
            return "tuple"
        elif isinstance(node, ast.Set):
            return "set"
        
        return "Any"
    
    def _insert_return_annotation(self, line: str, type_str: str) -> str:
        """插入返回值注解"""
        match = re.match(r'^(\s*def\s+\w+\s*\(.*?)\):', line)
        if match:
            return f"{match.group(1)}) -> {type_str}:"
        return line
    
    def _insert_param_annotation(self, line: str, param: str, type_str: str) -> str:
        """插入参数注解"""
        pattern = rf'\b{param}\b(?![=:])'
        replacement = f"{param}: {type_str}"
        return re.sub(pattern, replacement, line)
    
    def analyze_errors(self, errors: List[TypeError]) -> Dict[str, Any]:
        """
        分析错误
        
        Args:
            errors: 错误列表
            
        Returns:
            分析结果
        """
        if not errors:
            return {
                "most_common": None,
                "by_severity": {},
                "recommendations": []
            }
        
        # 最常见错误
        code_counts = self._group_by_code(errors)
        most_common = max(code_counts.items(), key=lambda x: x[1])
        
        # 按严重程度分组
        by_severity = defaultdict(list)
        for error in errors:
            by_severity[error.severity].append(error.code)
        
        # 生成建议
        recommendations = []
        if "var-annotated" in code_counts:
            recommendations.append("考虑启用disallow_untyped_defs强制类型注解")
        if "attr-defined" in code_counts:
            recommendations.append("检查是否有缺失的类定义或导入")
        if "name-defined" in code_counts:
            recommendations.append("检查导入语句和变量拼写")
        
        return {
            "most_common": {
                "code": most_common[0],
                "count": most_common[1],
                "type": self.ERROR_CATEGORIES.get(most_common[0], "其他")
            },
            "by_severity": dict(by_severity),
            "recommendations": recommendations
        }
    
    def get_error_stats(self, project_path: Union[str, Path],
                        **options) -> Dict[str, Any]:
        """
        获取错误统计
        
        Args:
            project_path: 项目路径
            **options: 检查选项
            
        Returns:
            错误统计信息
        """
        result = self.check_project(project_path, **options)
        return result.get("stats", {})
    
    def configure_project(self, config_path: Union[str, Path],
                          settings: Dict[str, Any]) -> bool:
        """
        配置项目类型检查
        
        Args:
            config_path: 配置文件路径
            settings: 配置设置
            
        Returns:
            是否成功
        """
        path = Path(config_path)
        
        if path.name == "mypy.ini":
            return self._write_mypy_ini(path, settings)
        elif path.name == "pyproject.toml":
            return self._write_pyproject_toml(path, settings)
        else:
            raise ValueError("配置文件必须是 mypy.ini 或 pyproject.toml")
    
    def _write_mypy_ini(self, path: Path, settings: Dict) -> bool:
        """写入mypy.ini配置"""
        lines = ["[mypy]"]
        
        for key, value in settings.items():
            if isinstance(value, bool):
                lines.append(f"{key} = {str(value).lower()}")
            elif isinstance(value, list):
                lines.append(f"{key} = {', '.join(value)}")
            else:
                lines.append(f"{key} = {value}")
        
        path.write_text('\n'.join(lines), encoding='utf-8')
        return True
    
    def _write_pyproject_toml(self, path: Path, settings: Dict) -> bool:
        """写入pyproject.toml配置"""
        lines = ["[tool.mypy]"]
        
        for key, value in settings.items():
            if isinstance(value, bool):
                lines.append(f"{key} = {str(value).lower()}")
            elif isinstance(value, list):
                lines.append(f'{key} = ["' + '", "'.join(value) + '"]')
            elif isinstance(value, str):
                lines.append(f'{key} = "{value}"')
            else:
                lines.append(f"{key} = {value}")
        
        if path.exists():
            existing = path.read_text(encoding='utf-8')
            # 移除旧的mypy配置
            lines = [existing] + [''] + lines
        
        path.write_text('\n'.join(lines), encoding='utf-8')
        return True


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mypy Type Checking Skill")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # check 命令
    check_parser = subparsers.add_parser("check", help="检查类型")
    check_parser.add_argument("path", help="文件或目录路径")
    check_parser.add_argument("--strict", action="store_true", help="严格模式")
    check_parser.add_argument("--ignore-missing", action="store_true", help="忽略缺失导入")
    
    # fix 命令
    fix_parser = subparsers.add_parser("fix", help="修复错误")
    fix_parser.add_argument("path", help="文件路径")
    fix_parser.add_argument("--dry-run", action="store_true", help="仅预览")
    
    # annotate 命令
    ann_parser = subparsers.add_parser("annotate", help="生成注解")
    ann_parser.add_argument("path", help="文件路径")
    
    # stats 命令
    stats_parser = subparsers.add_parser("stats", help="错误统计")
    stats_parser.add_argument("path", help="项目路径")
    
    # config 命令
    config_parser = subparsers.add_parser("config", help="配置项目")
    config_parser.add_argument("path", default="mypy.ini", help="配置文件路径")
    
    args = parser.parse_args()
    
    skill = MypySkill()
    
    if args.command == "check":
        path = Path(args.path)
        if path.is_file():
            result = skill.check_file(path, strict=args.strict, 
                                       ignore_missing=args.ignore_missing)
            print(f"文件: {result.file_path}")
            print(f"错误: {result.error_count}")
            print(f"警告: {result.warning_count}")
            for error in result.errors[:10]:
                print(f"  {error.line}:{error.column} [{error.code}] {error.message}")
        else:
            result = skill.check_project(path, strict=args.strict)
            print(f"总错误: {result['error_count']}")
            print(f"文件统计: {result['stats']}")
    
    elif args.command == "fix":
        result = skill.fix_errors(args.path, dry_run=args.dry_run)
        print(f"修复了 {result['fixed_count']} 个错误")
        for fix in result.get('fixes', []):
            print(f"  行 {fix['line']}: {fix['code']}")
    
    elif args.command == "annotate":
        code = skill.generate_annotations(args.path)
        print(code)
    
    elif args.command == "stats":
        stats = skill.get_error_stats(args.path)
        print(json.dumps(stats, indent=2))
    
    elif args.command == "config":
        settings = {
            "python_version": "3.10",
            "warn_return_any": True,
            "warn_unused_configs": True,
            "ignore_missing_imports": True,
            "show_error_codes": True
        }
        skill.configure_project(args.path, settings)
        print(f"配置已写入: {args.path}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
