#!/usr/bin/env python3
"""
Jest Testing Framework Skill

Jest测试框架智能助手。Use when writing tests, automating testing, 
or when user mentions 'Jest', 'unit testing', 'test coverage', 'mock testing', 'snapshot testing'.

Capabilities:
- 测试生成: 自动生成Jest单元测试代码
- Mock创建: 创建mock函数和模块模拟
- 覆盖率分析: 分析测试覆盖率并生成报告
- Snapshot测试: 创建和管理快照测试
- 测试优化: 优化现有测试代码
"""

import json
import re
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class TestConfig:
    """Jest测试配置"""
    test_environment: str = "jsdom"
    coverage_threshold: float = 80.0
    test_match: List[str] = None
    collect_coverage_from: List[str] = None
    setup_files: List[str] = None
    
    def __post_init__(self):
        if self.test_match is None:
            self.test_match = ["**/__tests__/**/*.js", "**/?(*.)+(spec|test).js"]
        if self.collect_coverage_from is None:
            self.collect_coverage_from = ["src/**/*.js", "!src/**/*.test.js"]
        if self.setup_files is None:
            self.setup_files = []


@dataclass
class MockConfig:
    """Mock配置"""
    module_name: str
    methods: List[str]
    return_values: Dict[str, Any] = None
    implementation: Dict[str, str] = None
    
    def __post_init__(self):
        if self.return_values is None:
            self.return_values = {}
        if self.implementation is None:
            self.implementation = {}


@dataclass
class CoverageReport:
    """覆盖率报告"""
    total_statements: int = 0
    covered_statements: int = 0
    total_branches: int = 0
    covered_branches: int = 0
    total_functions: int = 0
    covered_functions: int = 0
    total_lines: int = 0
    covered_lines: int = 0
    
    @property
    def statement_coverage(self) -> float:
        if self.total_statements == 0:
            return 100.0
        return (self.covered_statements / self.total_statements) * 100
    
    @property
    def branch_coverage(self) -> float:
        if self.total_branches == 0:
            return 100.0
        return (self.covered_branches / self.total_branches) * 100
    
    @property
    def function_coverage(self) -> float:
        if self.total_functions == 0:
            return 100.0
        return (self.covered_functions / self.total_functions) * 100
    
    @property
    def line_coverage(self) -> float:
        if self.total_lines == 0:
            return 100.0
        return (self.covered_lines / self.total_lines) * 100


class JestSkill:
    """Jest测试框架Skill主类"""
    
    def __init__(self, config: Optional[TestConfig] = None):
        self.config = config or TestConfig()
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """加载测试模板"""
        return {
            "basic_test": '''/**
 * {description}
 */

describe('{suite_name}', () => {{
  {before_each}
  
  {test_cases}
}});
''',
            "test_case": '''
  test('{test_name}', () => {{
    {arrange}
    {act}
    {assert}
  }});
''',
            "async_test": '''
  test('{test_name}', async () => {{
    {arrange}
    const result = await {async_call};
    {assert}
  }});
''',
            "mock_function": '''jest.fn(){return_value}''',
            "mock_module": '''jest.mock('{module_name}', () => ({ mock_methods }));''',
            "snapshot_test": '''
  test('{test_name}', () => {{
    const result = {function_call};
    expect(result).toMatchSnapshot();
  }});
'''
        }
    
    def generate_test(
        self,
        source_code: str,
        function_name: Optional[str] = None,
        test_type: str = "unit",
        framework: str = "jest"
    ) -> str:
        """
        根据源代码生成Jest测试代码
        
        Args:
            source_code: 源代码
            function_name: 函数名（可选，自动检测）
            test_type: 测试类型 (unit, integration, snapshot)
            framework: 测试框架
            
        Returns:
            生成的测试代码
        """
        # 解析函数信息
        func_info = self._parse_function(source_code, function_name)
        
        if test_type == "snapshot":
            return self._generate_snapshot_test(func_info)
        elif test_type == "integration":
            return self._generate_integration_test(func_info)
        else:
            return self._generate_unit_test(func_info)
    
    def _parse_function(self, source_code: str, function_name: Optional[str] = None) -> Dict:
        """解析函数信息"""
        # 检测函数类型和参数
        func_patterns = [
            r'function\s+(\w+)\s*\(([^)]*)\)',
            r'const\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>',
            r'export\s+(?:default\s+)?function\s+(\w+)\s*\(([^)]*)\)',
            r'(?:async\s+)?(\w+)\s*\(([^)]*)\)\s*\{',
        ]
        
        func_info = {
            "name": function_name or "unknown",
            "params": [],
            "is_async": "async" in source_code,
            "return_type": None,
            "description": ""
        }
        
        for pattern in func_patterns:
            match = re.search(pattern, source_code)
            if match:
                if not function_name:
                    func_info["name"] = match.group(1)
                func_info["params"] = [p.strip() for p in match.group(2).split(",") if p.strip()]
                break
        
        # 提取JSDoc注释
        jsdoc_pattern = r'/\*\*\s*\n([^*]|\*(?!/))*\*/'
        jsdoc_match = re.search(jsdoc_pattern, source_code)
        if jsdoc_match:
            func_info["description"] = jsdoc_match.group(0)
        
        return func_info
    
    def _generate_unit_test(self, func_info: Dict) -> str:
        """生成单元测试"""
        test_cases = []
        
        # 基础测试用例
        params_str = ", ".join([f"'{p}'" if i == 0 else str(i+1) for i, p in enumerate(func_info["params"])])
        if not params_str:
            params_str = ""
        
        test_case = self.templates["test_case"].format(
            test_name=f"should handle basic case for {func_info['name']}",
            arrange="// Arrange",
            act=f"const result = {func_info['name']}({params_str});",
            assert="// Assert\n    expect(result).toBeDefined();"
        )
        test_cases.append(test_case)
        
        # 边界条件测试
        if func_info["params"]:
            edge_case = self.templates["test_case"].format(
                test_name=f"should handle edge cases for {func_info['name']}",
                arrange="// Arrange - edge case setup",
                act=f"const result = {func_info['name']}();",
                assert="// Assert edge case\n    expect(result).toBeDefined();"
            )
            test_cases.append(edge_case)
        
        # 异步测试
        if func_info["is_async"]:
            async_test = self.templates["async_test"].format(
                test_name=f"should handle async operation",
                arrange="// Arrange",
                async_call=f"{func_info['name']}({params_str})",
                assert="expect(result).toBeDefined();"
            )
            test_cases.append(async_test)
        
        return self.templates["basic_test"].format(
            description=f"Tests for {func_info['name']}",
            suite_name=func_info['name'],
            before_each="beforeEach(() => {\n    // Setup before each test\n  });",
            test_cases="".join(test_cases)
        )
    
    def _generate_integration_test(self, func_info: Dict) -> str:
        """生成集成测试"""
        return f'''/**
 * Integration tests for {func_info['name']}
 */

describe('{func_info['name']} Integration', () => {{
  beforeAll(async () => {{
    // Global setup
  }});

  afterAll(async () => {{
    // Cleanup
  }});

  test('should integrate with dependencies', async () => {{
    // Integration test
    const result = await {func_info['name']}();
    expect(result).toBeDefined();
  }});
}});
'''
    
    def _generate_snapshot_test(self, func_info: Dict) -> str:
        """生成Snapshot测试"""
        params_str = ", ".join(["'test'" for _ in func_info["params"]]) if func_info["params"] else ""
        
        return f'''/**
 * Snapshot tests for {func_info['name']}
 */

describe('{func_info['name']} Snapshots', () => {{
  test('should match snapshot for standard input', () => {{
    const result = {func_info['name']}({params_str});
    expect(result).toMatchSnapshot();
  }});

  test('should match snapshot for empty input', () => {{
    const result = {func_info['name']}();
    expect(result).toMatchSnapshot();
  }});
}});
'''
    
    def generate_mock(
        self,
        module_name: str,
        methods: List[str],
        config: Optional[MockConfig] = None
    ) -> str:
        """
        生成Mock代码
        
        Args:
            module_name: 模块名称
            methods: 需要mock的方法列表
            config: Mock配置
            
        Returns:
            生成的mock代码
        """
        if config is None:
            config = MockConfig(module_name, methods)
        
        mock_methods = []
        for method in methods:
            return_val = config.return_values.get(method, "undefined")
            impl = config.implementation.get(method)
            
            if impl:
                mock_methods.append(f"{method}: jest.fn({impl})")
            else:
                mock_methods.append(f"{method}: jest.fn().mockReturnValue({return_val})")
        
        return self.templates["mock_module"].format(
            module_name=module_name,
            mock_methods=",\n    ".join(mock_methods)
        )
    
    def generate_spy(self, object_name: str, method_name: str) -> str:
        """生成Spy代码"""
        return f'''const spy = jest.spyOn({object_name}, '{method_name}');
spy.mockReturnValue('mocked value');

// After test
spy.mockRestore();'''
    
    def analyze_coverage(
        self,
        coverage_json_path: Optional[str] = None,
        test_files: Optional[List[str]] = None
    ) -> CoverageReport:
        """
        分析测试覆盖率
        
        Args:
            coverage_json_path: coverage-final.json路径
            test_files: 测试文件列表
            
        Returns:
            覆盖率报告
        """
        report = CoverageReport()
        
        if coverage_json_path and os.path.exists(coverage_json_path):
            with open(coverage_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for file_path, file_data in data.items():
                statement_map = file_data.get("statementMap", {})
                s = file_data.get("s", {})
                branch_map = file_data.get("branchMap", {})
                b = file_data.get("b", {})
                fn_map = file_data.get("fnMap", {})
                f = file_data.get("f", {})
                
                report.total_statements += len(statement_map)
                report.covered_statements += sum(1 for v in s.values() if v > 0)
                
                report.total_branches += sum(len(branches) for branches in branch_map.values())
                for branch_id, branches in b.items():
                    report.covered_branches += sum(1 for v in branches if v > 0)
                
                report.total_functions += len(fn_map)
                report.covered_functions += sum(1 for v in f.values() if v > 0)
        
        return report
    
    def generate_coverage_config(self) -> str:
        """生成Jest覆盖率配置"""
        return f'''module.exports = {{
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  coverageThreshold: {{
    global: {{
      branches: {self.config.coverage_threshold},
      functions: {self.config.coverage_threshold},
      lines: {self.config.coverage_threshold},
      statements: {self.config.coverage_threshold}
    }}
  }},
  collectCoverageFrom: {json.dumps(self.config.collect_coverage_from)}
}};'''
    
    def optimize_tests(self, test_code: str) -> str:
        """
        优化测试代码
        
        Args:
            test_code: 原始测试代码
            
        Returns:
            优化后的测试代码
        """
        optimizations = []
        
        # 检测重复代码
        if test_code.count("beforeEach") > 1:
            optimizations.append("- 合并多个beforeEach块")
        
        # 检测缺少的断言
        test_count = len(re.findall(r'\btest\(|\bit\(', test_code))
        expect_count = len(re.findall(r'\bexpect\(', test_code))
        if test_count > expect_count:
            optimizations.append(f"- 发现{test_count - expect_count}个测试缺少expect断言")
        
        # 检测过长的测试
        tests = re.findall(r'test\([\s\S]*?\}\);', test_code)
        for test in tests:
            if test.count('\n') > 20:
                optimizations.append("- 存在过长的测试函数，建议拆分")
                break
        
        if optimizations:
            return f'''// 优化建议:\n// {'\n// '.join(optimizations)}\n\n{test_code}'''
        
        return test_code
    
    def setup_test_environment(self, project_path: str) -> Dict[str, str]:
        """
        设置测试环境
        
        Args:
            project_path: 项目路径
            
        Returns:
            生成的文件内容字典
        """
        files = {}
        
        # jest.config.js
        files["jest.config.js"] = f'''module.exports = {{
  testEnvironment: '{self.config.test_environment}',
  testMatch: {json.dumps(self.config.test_match)},
  collectCoverageFrom: {json.dumps(self.config.collect_coverage_from)},
  setupFilesAfterEnv: {json.dumps(self.config.setup_files)},
  moduleNameMapper: {{
    '^@/(.*)$': '<rootDir>/src/$1'
  }},
  transform: {{
    '^.+\\.jsx?$': 'babel-jest'
  }}
}};'''
        
        # setupTests.js
        files["setupTests.js"] = '''import '@testing-library/jest-dom';

// Global mocks
global.mockFetch = (data) => {
  global.fetch = jest.fn().mockResolvedValue({
    json: jest.fn().mockResolvedValue(data),
    ok: true
  });
};'''
        
        # testUtils.js
        files["testUtils.js"] = '''import {{ render }} from '@testing-library/react';

export const renderWithProviders = (ui, options = {{}}) => {
  return render(ui, {{ wrapper: Providers, ...options }});
};

export * from '@testing-library/react';'''
        
        return files
    
    def create_test_suite(
        self,
        module_name: str,
        functions: List[Dict],
        options: Optional[Dict] = None
    ) -> str:
        """
        创建完整的测试套件
        
        Args:
            module_name: 模块名
            functions: 函数列表
            options: 选项
            
        Returns:
            完整测试套件代码
        """
        options = options or {}
        include_mocks = options.get("include_mocks", True)
        include_setup = options.get("include_setup", True)
        
        lines = []
        
        # Imports
        lines.append(f"import {{ {', '.join([f['name'] for f in functions])} }} from './{module_name}';\n")
        
        # Mocks
        if include_mocks:
            lines.append("// Mocks")
            lines.append("jest.mock('./api', () => ({")
            lines.append("  fetchData: jest.fn().mockResolvedValue({ data: [] })")
            lines.append("}));\n")
        
        # Setup
        if include_setup:
            lines.append("// Setup")
            lines.append("beforeEach(() => {")
            lines.append("  jest.clearAllMocks();")
            lines.append("});\n")
        
        # Test suites
        for func in functions:
            test_code = self.generate_unit_test_for_function(func)
            lines.append(test_code)
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_unit_test_for_function(self, func: Dict) -> str:
        """为单个函数生成单元测试"""
        name = func.get("name", "unknown")
        params = func.get("params", [])
        
        params_str = ", ".join([f"arg{i}" for i in range(len(params))]) if params else ""
        
        return f'''describe('{name}', () => {{
  test('should return expected result', () => {{
    // Arrange
    {chr(10).join([f'const arg{i} = mockData;' for i in range(len(params))])}
    
    // Act
    const result = {name}({params_str});
    
    // Assert
    expect(result).toBeDefined();
  }});
  
  test('should handle errors', () => {{
    // Arrange
    
    // Act & Assert
    expect(() => {name}()).toThrow();
  }});
}});'''


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Jest Testing Skill')
    parser.add_argument('action', choices=['generate', 'mock', 'coverage', 'setup'])
    parser.add_argument('--source', '-s', help='Source code or file path')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--function', '-f', help='Function name')
    parser.add_argument('--type', '-t', default='unit', help='Test type')
    parser.add_argument('--module', '-m', help='Module name for mock')
    
    args = parser.parse_args()
    
    skill = JestSkill()
    
    if args.action == 'generate':
        source = args.source
        if os.path.isfile(source):
            with open(source, 'r', encoding='utf-8') as f:
                source = f.read()
        test_code = skill.generate_test(source, args.function, args.type)
        print(test_code)
        
    elif args.action == 'mock':
        methods = ['get', 'post', 'put', 'delete']
        mock_code = skill.generate_mock(args.module or 'axios', methods)
        print(mock_code)
        
    elif args.action == 'coverage':
        report = skill.analyze_coverage(args.source)
        print(f"Statements: {report.statement_coverage:.2f}%")
        print(f"Branches: {report.branch_coverage:.2f}%")
        print(f"Functions: {report.function_coverage:.2f}%")
        print(f"Lines: {report.line_coverage:.2f}%")
        
    elif args.action == 'setup':
        files = skill.setup_test_environment('.')
        for filename, content in files.items():
            print(f"\n=== {filename} ===")
            print(content)


if __name__ == '__main__':
    main()
