"""Tests for pytest-skill main module"""
import ast
import json
import tempfile
from pathlib import Path

import pytest

from main import PytestSkill, FunctionInfo, ClassInfo, FixtureInfo, CoverageData


class TestPytestSkillInit:
    """Test PytestSkill initialization"""
    
    def test_default_init(self):
        skill = PytestSkill()
        assert skill.coverage_target == 80
        assert skill.parallel_workers == 4
        assert skill.testpaths == ["tests"]
    
    def test_custom_init(self):
        config = {
            "coverage_target": 90,
            "parallel_workers": 8,
            "testpaths": ["unit_tests", "integration_tests"]
        }
        skill = PytestSkill(config)
        assert skill.coverage_target == 90
        assert skill.parallel_workers == 8
        assert skill.testpaths == ["unit_tests", "integration_tests"]


class TestGenerateTests:
    """Test test generation functionality"""
    
    @pytest.fixture
    def skill(self):
        return PytestSkill()
    
    @pytest.fixture
    def sample_module(self, tmp_path):
        """Create a sample Python module"""
        module = tmp_path / "sample_module.py"
        module.write_text('''
def add(a, b):
    """Add two numbers"""
    return a + b

class Calculator:
    """Simple calculator"""
    
    def __init__(self):
        self.value = 0
    
    def add(self, x):
        self.value += x
        return self.value
    
    def reset(self):
        self.value = 0
''')
        return module
    
    def test_generate_tests_for_file(self, skill, sample_module):
        test_code = skill._generate_test_for_file(sample_module)
        assert "def test_add():" in test_code
        assert "class TestCalculator:" in test_code
        assert "def test_init(self):" in test_code
        assert "pytest" in test_code
    
    def test_generate_tests_output_file(self, skill, sample_module, tmp_path):
        output = tmp_path / "test_output.py"
        skill.generate_tests(str(sample_module), str(output))
        assert output.exists()
        content = output.read_text()
        assert "test_add" in content


class TestParseModule:
    """Test AST parsing functionality"""
    
    @pytest.fixture
    def skill(self):
        return PytestSkill()
    
    def test_parse_function(self, skill):
        code = '''
def my_func(a, b, c=10):
    """Docstring"""
    return a + b + c
'''
        tree = ast.parse(code)
        classes, functions = skill._parse_module(tree)
        
        assert len(classes) == 0
        assert len(functions) == 1
        assert functions[0].name == "my_func"
        assert "a" in functions[0].args
        assert functions[0].has_return is True
    
    def test_parse_class(self, skill):
        code = '''
class MyClass:
    """Class docstring"""
    
    def method1(self):
        pass
    
    def method2(self, x):
        return x * 2
'''
        tree = ast.parse(code)
        classes, functions = skill._parse_module(tree)
        
        assert len(classes) == 1
        assert classes[0].name == "MyClass"
        assert len(classes[0].methods) == 2
    
    def test_parse_async_function(self, skill):
        code = '''
async def async_func():
    return await something()
'''
        tree = ast.parse(code)
        classes, functions = skill._parse_module(tree)
        
        assert len(functions) == 1
        assert functions[0].is_async is True


class TestGenerateFunctionTest:
    """Test function test generation"""
    
    @pytest.fixture
    def skill(self):
        return PytestSkill()
    
    def test_simple_function(self, skill):
        func = FunctionInfo(name="simple", args=[], has_return=False)
        lines = skill._generate_function_test(func, "module")
        
        assert "def test_simple():" in lines
        assert "simple()" in " ".join(lines)
    
    def test_function_with_args(self, skill):
        func = FunctionInfo(name="calc", args=["a", "b"], has_return=True)
        lines = skill._generate_function_test(func, "module")
        
        assert "def test_calc():" in lines
        assert "calc(a, b)" in " ".join(lines)
        assert "assert result is not None" in lines
    
    def test_async_function(self, skill):
        func = FunctionInfo(name="fetch", args=[], has_return=True, is_async=True)
        lines = skill._generate_function_test(func, "module")
        
        assert "await fetch" in " ".join(lines)


class TestGenerateClassTest:
    """Test class test generation"""
    
    @pytest.fixture
    def skill(self):
        return PytestSkill()
    
    def test_class_with_init(self, skill):
        cls = ClassInfo(
            name="DataStore",
            methods=[
                FunctionInfo(name="__init__", is_method=True),
                FunctionInfo(name="get", is_method=True, has_return=True),
            ]
        )
        lines = skill._generate_class_test(cls)
        
        assert "class TestDataStore:" in lines
        assert "def setup_method(self):" in lines
        assert "self.instance = DataStore()" in lines
        assert "def test_get(self):" in lines


class TestParseTestOutput:
    """Test test output parsing"""
    
    @pytest.fixture
    def skill(self):
        return PytestSkill()
    
    def test_successful_run(self, skill):
        stdout = '''
============================= test session starts ==============================
collected 5 items
test_sample.py::test_one PASSED
test_sample.py::test_two PASSED

============================== 5 passed in 0.50s ===============================
'''
        result = skill._parse_test_output(stdout, "", 0)
        
        assert result["success"] is True
        assert result["summary"]["passed"] == 5
        assert result["summary"]["failed"] == 0
    
    def test_failed_run(self, skill):
        stdout = '''
collected 10 items
test_sample.py::test_one PASSED
test_sample.py::test_two FAILED

============================== 8 passed, 2 failed in 1.20s =====================
'''
        result = skill._parse_test_output(stdout, "", 1)
        
        assert result["success"] is False
        assert result["summary"]["passed"] == 8
        assert result["summary"]["failed"] == 2
    
    def test_with_coverage(self, skill):
        stdout = '''
Name              Stmts   Miss  Cover   Missing
-----------------------------------------------
module.py            20      4    80%
-----------------------------------------------
TOTAL                20      4    80%

============================== 5 passed in 0.50s ===============================
'''
        result = skill._parse_test_output(stdout, "", 0)
        
        assert result["coverage"] == 80.0


class TestFixtureAnalysis:
    """Test fixture analysis"""
    
    @pytest.fixture
    def skill(self):
        return PytestSkill()
    
    @pytest.fixture
    def sample_test_file(self, tmp_path):
        test_file = tmp_path / "test_sample.py"
        test_file.write_text('''
import pytest

@pytest.fixture
def simple_fixture():
    return {"key": "value"}

@pytest.fixture(scope="module")
def module_fixture():
    return [1, 2, 3]

@pytest.fixture(autouse=True)
def auto_fixture():
    yield
    cleanup()
''')
        return test_file
    
    def test_extract_fixtures(self, skill, sample_test_file):
        fixtures = skill._extract_fixtures(sample_test_file)
        
        assert len(fixtures) == 3
        names = [f.name for f in fixtures]
        assert "simple_fixture" in names
        assert "module_fixture" in names
    
    def test_parse_fixture_scope(self, skill, sample_test_file):
        fixtures = skill._extract_fixtures(sample_test_file)
        
        module_fix = next(f for f in fixtures if f.name == "module_fixture")
        assert module_fix.scope == "module"
        
        simple_fix = next(f for f in fixtures if f.name == "simple_fixture")
        assert simple_fix.scope == "function"


class TestOptimizeFixtures:
    """Test fixture optimization"""
    
    @pytest.fixture
    def skill(self):
        return PytestSkill()
    
    def test_detect_duplicate_names(self, skill):
        fixtures = [
            FixtureInfo(name="db", scope="function"),
            FixtureInfo(name="db", scope="module"),
            FixtureInfo(name="client", scope="function"),
        ]
        
        suggestions = skill.optimize_fixtures(fixtures)
        assert "db" in suggestions["duplicate_fixtures"]
    
    def test_no_duplicates(self, skill):
        fixtures = [
            FixtureInfo(name="db1", scope="function"),
            FixtureInfo(name="db2", scope="module"),
        ]
        
        suggestions = skill.optimize_fixtures(fixtures)
        assert len(suggestions["duplicate_fixtures"]) == 0


class TestCoverageData:
    """Test CoverageData class"""
    
    def test_empty_coverage(self):
        cov = CoverageData()
        assert cov.coverage_percent == 100.0
    
    def test_partial_coverage(self):
        cov = CoverageData(total_lines=100, covered_lines=75)
        assert cov.coverage_percent == 75.0
    
    def test_zero_coverage(self):
        cov = CoverageData(total_lines=100, covered_lines=0)
        assert cov.coverage_percent == 0.0


class TestConfigureProject:
    """Test project configuration"""
    
    @pytest.fixture
    def skill(self):
        return PytestSkill()
    
    def test_write_pytest_ini(self, skill, tmp_path):
        config_file = tmp_path / "pytest.ini"
        settings = {
            "testpaths": ["tests", "integration_tests"],
            "python_files": ["test_*.py"],
            "addopts": "-v --tb=short"
        }
        
        skill._write_pytest_ini(config_file, settings)
        
        content = config_file.read_text()
        assert "[pytest]" in content
        assert "testpaths =" in content
        assert "tests" in content
    
    def test_write_pyproject_toml(self, skill, tmp_path):
        config_file = tmp_path / "pyproject.toml"
        settings = {
            "testpaths": ["tests"],
            "addopts": "-v"
        }
        
        skill._write_pyproject_toml(config_file, settings)
        
        content = config_file.read_text()
        assert "[tool.pytest.ini_options]" in content


class TestIntegration:
    """Integration tests"""
    
    @pytest.fixture
    def skill(self):
        return PytestSkill()
    
    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure"""
        src = tmp_path / "src"
        src.mkdir()
        
        module = src / "calculator.py"
        module.write_text('''
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
''')
        
        tests = tmp_path / "tests"
        tests.mkdir()
        
        test_file = tests / "test_calculator.py"
        test_file.write_text('''
def test_add():
    from src.calculator import add
    assert add(1, 2) == 3
''')
        
        return tmp_path
    
    def test_full_workflow(self, skill, temp_project):
        # Generate tests
        test_code = skill.generate_tests(str(temp_project / "src" / "calculator.py"))
        assert "test_add" in test_code
        assert "test_subtract" in test_code
        
        # Analyze fixtures
        fixtures = skill.analyze_fixtures(str(temp_project / "tests"))
        assert isinstance(fixtures, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
