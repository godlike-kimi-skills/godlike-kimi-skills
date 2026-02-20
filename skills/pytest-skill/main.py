"""
pytest-skill: PyTest测试框架Skill
提供测试生成、覆盖率分析、Fixtures管理功能
"""

import ast
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from collections import defaultdict
import json


@dataclass
class FunctionInfo:
    """函数信息数据类"""
    name: str
    args: List[str] = field(default_factory=list)
    has_return: bool = False
    is_method: bool = False
    is_async: bool = False
    decorators: List[str] = field(default_factory=list)
    docstring: str = ""
    line_number: int = 0


@dataclass
class ClassInfo:
    """类信息数据类"""
    name: str
    methods: List[FunctionInfo] = field(default_factory=list)
    docstring: str = ""
    line_number: int = 0


@dataclass
class FixtureInfo:
    """Fixture信息数据类"""
    name: str
    scope: str = "function"
    params: Optional[List[Any]] = None
    autouse: bool = False
    dependencies: List[str] = field(default_factory=list)
    line_number: int = 0


@dataclass
class CoverageData:
    """覆盖率数据类"""
    total_lines: int = 0
    covered_lines: int = 0
    missed_lines: List[int] = field(default_factory=list)
    branches: Dict[int, int] = field(default_factory=dict)
    files: Dict[str, Dict] = field(default_factory=dict)
    
    @property
    def coverage_percent(self) -> float:
        if self.total_lines == 0:
            return 100.0
        return round(self.covered_lines / self.total_lines * 100, 2)


class PytestSkill:
    """
    PyTest测试框架Skill主类
    
    提供功能:
    - 测试代码自动生成
    - 覆盖率分析
    - Fixtures管理
    - 项目配置
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.coverage_target = self.config.get("coverage_target", 80)
        self.parallel_workers = self.config.get("parallel_workers", 4)
        self.testpaths = self.config.get("testpaths", ["tests"])
        
    def generate_tests(self, source_path: str, output_path: Optional[str] = None) -> str:
        """
        为指定源代码生成测试代码
        
        Args:
            source_path: 源代码文件或目录路径
            output_path: 测试文件输出路径（可选）
            
        Returns:
            生成的测试代码字符串
        """
        source = Path(source_path)
        
        if source.is_file():
            test_code = self._generate_test_for_file(source)
        elif source.is_dir():
            test_code = self._generate_tests_for_package(source)
        else:
            raise FileNotFoundError(f"路径不存在: {source_path}")
        
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            Path(output_path).write_text(test_code, encoding="utf-8")
        
        return test_code
    
    def _generate_test_for_file(self, file_path: Path) -> str:
        """为单个文件生成测试"""
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
        except SyntaxError as e:
            return f"# 解析错误: {e}\n"
        
        classes, functions = self._parse_module(tree)
        module_name = file_path.stem
        
        lines = [
            f'"""Tests for {module_name} module"""',
            "import pytest",
            f"from {module_name} import *",
            "",
            "",
        ]
        
        # 生成函数测试
        for func in functions:
            lines.extend(self._generate_function_test(func, module_name))
            lines.append("")
        
        # 生成类测试
        for cls in classes:
            lines.extend(self._generate_class_test(cls))
            lines.append("")
        
        return "\n".join(lines)
    
    def _parse_module(self, tree: ast.AST) -> tuple:
        """解析AST模块，提取类和函数信息"""
        classes = []
        functions = []
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                cls_info = self._parse_class(node)
                classes.append(cls_info)
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                func_info = self._parse_function(node)
                functions.append(func_info)
        
        return classes, functions
    
    def _parse_class(self, node: ast.ClassDef) -> ClassInfo:
        """解析类定义"""
        cls = ClassInfo(
            name=node.name,
            docstring=ast.get_docstring(node) or "",
            line_number=node.lineno
        )
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not item.name.startswith("_") or item.name == "__init__":
                    method = self._parse_function(item, is_method=True)
                    cls.methods.append(method)
        
        return cls
    
    def _parse_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], 
                        is_method: bool = False) -> FunctionInfo:
        """解析函数定义"""
        args = []
        for arg in node.args.args:
            if arg.arg != "self" and arg.arg != "cls":
                args.append(arg.arg)
        
        has_return = any(
            isinstance(n, ast.Return) and n.value is not None 
            for n in ast.walk(node)
        )
        
        return FunctionInfo(
            name=node.name,
            args=args,
            has_return=has_return,
            is_method=is_method,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            docstring=ast.get_docstring(node) or "",
            line_number=node.lineno
        )
    
    def _generate_function_test(self, func: FunctionInfo, module: str) -> List[str]:
        """为函数生成测试代码"""
        lines = [f"def test_{func.name}():"]
        
        # 生成参数
        args_str = ", ".join([f'"arg_{i}"' for i in range(len(func.args))])
        if func.args:
            args_str = ", ".join(func.args)
        
        # 生成调用
        if func.is_async:
            lines.append(f"    result = await {func.name}({args_str})")
        else:
            lines.append(f"    result = {func.name}({args_str})")
        
        # 生成断言
        if func.has_return:
            lines.append("    assert result is not None")
        else:
            lines.append("    # 添加适当的断言")
        
        # 添加参数化建议
        if len(func.args) >= 2:
            lines.insert(0, f"# TODO: Consider using @pytest.mark.parametrize for {func.name}")
        
        return lines
    
    def _generate_class_test(self, cls: ClassInfo) -> List[str]:
        """为类生成测试代码"""
        lines = [f"class Test{cls.name}:", ""]
        
        # 添加setup方法
        lines.extend([
            "    def setup_method(self):",
            f"        self.instance = {cls.name}()",
            "",
        ])
        
        # 为每个方法生成测试
        for method in cls.methods:
            if method.name == "__init__":
                lines.extend([
                    "    def test_init(self):",
                    f"        assert isinstance(self.instance, {cls.name})",
                    "",
                ])
            else:
                lines.extend([
                    f"    def test_{method.name}(self):",
                    f"        result = self.instance.{method.name}()",
                ])
                if method.has_return:
                    lines.append("        assert result is not None")
                else:
                    lines.append("        # 添加适当的断言")
                lines.append("")
        
        return lines
    
    def _generate_tests_for_package(self, pkg_path: Path) -> str:
        """为包生成测试"""
        lines = ['"""Package tests"""', "import pytest", ""]
        
        for py_file in pkg_path.rglob("*.py"):
            if py_file.name.startswith("test_") or py_file.name == "__init__.py":
                continue
            
            test_code = self._generate_test_for_file(py_file)
            lines.append(f"# Tests for {py_file.relative_to(pkg_path)}")
            lines.append(test_code)
            lines.append("")
        
        return "\n".join(lines)
    
    def run_tests(self, test_path: str, **options) -> Dict[str, Any]:
        """
        运行测试并返回结果
        
        Args:
            test_path: 测试文件或目录路径
            **options: 额外选项
                - coverage: 是否启用覆盖率 (bool)
                - parallel: 是否并行运行 (bool)
                - verbose: 详细输出 (bool)
                - markers: 测试标记筛选 (str)
                - junit: JUnit XML输出路径 (str)
                
        Returns:
            测试结果字典
        """
        cmd = ["python", "-m", "pytest", test_path]
        
        # 添加选项
        if options.get("coverage", False):
            cmd.extend(["--cov", options.get("cov_source", "."), "--cov-report=term-missing"])
        
        if options.get("parallel", False):
            cmd.extend(["-n", str(self.parallel_workers)])
        
        if options.get("verbose", True):
            cmd.append("-v")
        
        if "markers" in options:
            cmd.extend(["-m", options["markers"]])
        
        if "junit" in options:
            cmd.extend([f"--junitxml={options['junit']}"])
        
        # 运行测试
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=options.get("cwd")
        )
        
        # 解析结果
        return self._parse_test_output(result.stdout, result.stderr, result.returncode)
    
    def _parse_test_output(self, stdout: str, stderr: str, returncode: int) -> Dict:
        """解析pytest输出"""
        result = {
            "success": returncode == 0,
            "returncode": returncode,
            "stdout": stdout,
            "stderr": stderr,
            "summary": {},
        }
        
        # 解析摘要
        summary_match = re.search(
            r"(\d+) passed.*?((\d+) failed)?.*?((\d+) error)?.*?((\d+) skipped)?.*?in ([\d.]+)s",
            stdout,
            re.DOTALL
        )
        
        if summary_match:
            result["summary"] = {
                "passed": int(summary_match.group(1) or 0),
                "failed": int(summary_match.group(3) or 0),
                "errors": int(summary_match.group(5) or 0),
                "skipped": int(summary_match.group(7) or 0),
                "duration": float(summary_match.group(8)),
            }
            total = sum(result["summary"].values()) - result["summary"]["duration"]
            if total > 0:
                result["pass_rate"] = round(result["summary"]["passed"] / total * 100, 2)
        
        # 解析覆盖率
        cov_match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", stdout)
        if cov_match:
            result["coverage"] = float(cov_match.group(1))
        
        return result
    
    def analyze_coverage(self, source_path: str, test_path: Optional[str] = None) -> CoverageData:
        """
        分析代码覆盖率
        
        Args:
            source_path: 源代码路径
            test_path: 测试路径（可选）
            
        Returns:
            覆盖率数据对象
        """
        cmd = ["python", "-m", "coverage", "run", "--source", source_path, "-m", "pytest"]
        
        if test_path:
            cmd.append(test_path)
        else:
            cmd.append("tests/")
        
        subprocess.run(cmd, capture_output=True)
        
        # 获取覆盖率报告
        result = subprocess.run(
            ["python", "-m", "coverage", "json", "-o", "-"],
            capture_output=True,
            text=True
        )
        
        return self._parse_coverage_json(result.stdout)
    
    def _parse_coverage_json(self, json_str: str) -> CoverageData:
        """解析覆盖率JSON输出"""
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            return CoverageData()
        
        cov_data = CoverageData()
        
        for file_path, file_info in data.get("files", {}).items():
            cov_data.files[file_path] = {
                "summary": file_info.get("summary", {}),
                "missing_lines": file_info.get("missing_lines", []),
                "excluded_lines": file_info.get("excluded_lines", []),
            }
            
            summary = file_info.get("summary", {})
            cov_data.total_lines += summary.get("num_statements", 0)
            cov_data.covered_lines += summary.get("covered_lines", 0)
        
        return cov_data
    
    def generate_coverage_report(self, coverage_data: CoverageData, 
                                  format: str = "html", output_dir: str = "htmlcov") -> str:
        """
        生成覆盖率报告
        
        Args:
            coverage_data: 覆盖率数据
            format: 报告格式 (html, xml, json)
            output_dir: 输出目录
            
        Returns:
            报告文件路径
        """
        if format == "html":
            subprocess.run(["python", "-m", "coverage", "html", "-d", output_dir])
            return f"{output_dir}/index.html"
        elif format == "xml":
            output_file = f"{output_dir}/coverage.xml"
            subprocess.run(["python", "-m", "coverage", "xml", "-o", output_file])
            return output_file
        elif format == "json":
            output_file = f"{output_dir}/coverage.json"
            subprocess.run(["python", "-m", "coverage", "json", "-o", output_file])
            return output_file
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def analyze_fixtures(self, test_path: str) -> List[FixtureInfo]:
        """
        分析测试文件中的Fixtures
        
        Args:
            test_path: 测试文件或目录路径
            
        Returns:
            Fixtures信息列表
        """
        fixtures = []
        path = Path(test_path)
        
        if path.is_file():
            fixtures.extend(self._extract_fixtures(path))
        elif path.is_dir():
            for test_file in path.rglob("test_*.py"):
                fixtures.extend(self._extract_fixtures(test_file))
        
        return fixtures
    
    def _extract_fixtures(self, file_path: Path) -> List[FixtureInfo]:
        """从文件中提取Fixture定义"""
        fixtures = []
        
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
        except SyntaxError:
            return fixtures
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fixture = self._parse_fixture(node)
                if fixture:
                    fixtures.append(fixture)
        
        return fixtures
    
    def _parse_fixture(self, node: ast.FunctionDef) -> Optional[FixtureInfo]:
        """解析Fixture装饰器"""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name) and decorator.func.id == "pytest.fixture":
                    return self._extract_fixture_info(node, decorator)
            elif isinstance(decorator, ast.Name) and decorator.id == "fixture":
                return FixtureInfo(name=node.name, line_number=node.lineno)
        
        return None
    
    def _extract_fixture_info(self, node: ast.FunctionDef, 
                               decorator: ast.Call) -> FixtureInfo:
        """提取Fixture详细信息"""
        info = FixtureInfo(name=node.name, line_number=node.lineno)
        
        for keyword in decorator.keywords:
            if keyword.arg == "scope":
                if isinstance(keyword.value, ast.Constant):
                    info.scope = keyword.value.value
            elif keyword.arg == "params":
                info.params = []  # 简化处理
            elif keyword.arg == "autouse":
                if isinstance(keyword.value, ast.Constant):
                    info.autouse = keyword.value.value
        
        # 提取依赖
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and child.id != node.name:
                info.dependencies.append(child.id)
        
        return info
    
    def optimize_fixtures(self, fixtures: List[FixtureInfo]) -> Dict[str, Any]:
        """
        优化Fixtures配置建议
        
        Args:
            fixtures: Fixtures列表
            
        Returns:
            优化建议字典
        """
        suggestions = {
            "scope_optimizations": [],
            "duplicate_fixtures": [],
            "circular_dependencies": [],
            "unused_fixtures": [],
        }
        
        # 检查作用域优化
        scope_counts = defaultdict(list)
        for f in fixtures:
            scope_counts[f.scope].append(f.name)
        
        # 检测可能的重复
        names = [f.name for f in fixtures]
        for name in set(names):
            if names.count(name) > 1:
                suggestions["duplicate_fixtures"].append(name)
        
        # 检测循环依赖
        for fixture in fixtures:
            deps = set(fixture.dependencies)
            for other in fixtures:
                if other.name in deps and fixture.name in other.dependencies:
                    suggestions["circular_dependencies"].append(
                        (fixture.name, other.name)
                    )
        
        return suggestions
    
    def configure_project(self, config_path: str, settings: Dict[str, Any]) -> bool:
        """
        配置PyTest项目
        
        Args:
            config_path: 配置文件路径 (pytest.ini 或 pyproject.toml)
            settings: 配置设置
            
        Returns:
            是否成功
        """
        path = Path(config_path)
        
        if path.name == "pytest.ini":
            return self._write_pytest_ini(path, settings)
        elif path.name == "pyproject.toml":
            return self._write_pyproject_toml(path, settings)
        else:
            raise ValueError("配置文件必须是 pytest.ini 或 pyproject.toml")
    
    def _write_pytest_ini(self, path: Path, settings: Dict) -> bool:
        """写入pytest.ini配置"""
        lines = ["[pytest]", ""]
        
        for key, value in settings.items():
            if isinstance(value, list):
                lines.append(f"{key} =")
                for item in value:
                    lines.append(f"    {item}")
            elif isinstance(value, dict) and key == "markers":
                lines.append("markers =")
                for marker, desc in value.items():
                    lines.append(f"    {marker}: {desc}")
            else:
                lines.append(f"{key} = {value}")
        
        path.write_text("\n".join(lines), encoding="utf-8")
        return True
    
    def _write_pyproject_toml(self, path: Path, settings: Dict) -> bool:
        """写入pyproject.toml配置"""
        # 简化实现，实际应使用toml库
        content = '[tool.pytest.ini_options]\n'
        
        for key, value in settings.items():
            if isinstance(value, list):
                content += f'{key} = [\n'
                for item in value:
                    content += f'    "{item}",\n'
                content += ']\n'
            elif isinstance(value, str):
                content += f'{key} = "{value}"\n'
            else:
                content += f'{key} = {value}\n'
        
        if path.exists():
            existing = path.read_text(encoding="utf-8")
            content = existing + "\n" + content
        
        path.write_text(content, encoding="utf-8")
        return True


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PyTest Skill")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # generate 命令
    gen_parser = subparsers.add_parser("generate", help="生成测试代码")
    gen_parser.add_argument("source", help="源代码路径")
    gen_parser.add_argument("-o", "--output", help="输出路径")
    
    # run 命令
    run_parser = subparsers.add_parser("run", help="运行测试")
    run_parser.add_argument("path", help="测试路径")
    run_parser.add_argument("-c", "--coverage", action="store_true", help="启用覆盖率")
    run_parser.add_argument("-p", "--parallel", action="store_true", help="并行运行")
    
    # coverage 命令
    cov_parser = subparsers.add_parser("coverage", help="分析覆盖率")
    cov_parser.add_argument("source", help="源代码路径")
    cov_parser.add_argument("-f", "--format", default="html", help="报告格式")
    
    # fixtures 命令
    fix_parser = subparsers.add_parser("fixtures", help="分析Fixtures")
    fix_parser.add_argument("path", help="测试路径")
    
    args = parser.parse_args()
    
    skill = PytestSkill()
    
    if args.command == "generate":
        code = skill.generate_tests(args.source, args.output)
        if not args.output:
            print(code)
    elif args.command == "run":
        result = skill.run_tests(args.path, coverage=args.coverage, parallel=args.parallel)
        print(json.dumps(result, indent=2))
    elif args.command == "coverage":
        cov = skill.analyze_coverage(args.source)
        print(f"覆盖率: {cov.coverage_percent}%")
    elif args.command == "fixtures":
        fixtures = skill.analyze_fixtures(args.path)
        for f in fixtures:
            print(f"{f.name}: scope={f.scope}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
