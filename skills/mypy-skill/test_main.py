"""Tests for mypy-skill main module"""
import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import MypySkill, TypeError, TypeCheckResult, AnnotationInfo


class TestMypySkillInit:
    """Test MypySkill initialization"""
    
    def test_default_init(self):
        skill = MypySkill()
        assert skill.strict_mode is False
        assert skill.ignore_missing_imports is True
        assert skill.python_version == "3.10"
    
    def test_custom_init(self):
        config = {
            "strict_mode": True,
            "ignore_missing_imports": False,
            "python_version": "3.11"
        }
        skill = MypySkill(config)
        assert skill.strict_mode is True
        assert skill.ignore_missing_imports is False
        assert skill.python_version == "3.11"


class TestParseMypyOutput:
    """Test mypy output parsing"""
    
    @pytest.fixture
    def skill(self):
        return MypySkill()
    
    def test_parse_simple_error(self, skill):
        output = "module.py:10:5: error: Incompatible return value type [return-value]"
        errors = skill._parse_mypy_output(output)
        
        assert len(errors) == 1
        assert errors[0].file_path == "module.py"
        assert errors[0].line == 10
        assert errors[0].column == 5
        assert errors[0].severity == "error"
        assert errors[0].code == "return-value"
    
    def test_parse_warning(self, skill):
        output = "module.py:5:1: warning: Function is missing a return type annotation [return]"
        errors = skill._parse_mypy_output(output)
        
        assert len(errors) == 1
        assert errors[0].severity == "warning"
    
    def test_parse_multiple_errors(self, skill):
        output = '''module.py:1:1: error: First error [error-code]
module.py:2:1: error: Second error [error-code]
module.py:3:1: note: Some note'''
        
        errors = skill._parse_mypy_output(output)
        assert len(errors) == 3


class TestCheckFile:
    """Test file checking"""
    
    @pytest.fixture
    def skill(self):
        return MypySkill()
    
    def test_check_nonexistent_file(self, skill):
        result = skill.check_file("/nonexistent/file.py")
        assert result.success is False
        assert result.error_count == 1
        assert "不存在" in result.errors[0].message
    
    def test_check_valid_python_file(self, skill, tmp_path):
        py_file = tmp_path / "valid.py"
        py_file.write_text("x: int = 1\n")
        
        result = skill.check_file(py_file)
        # 即使没有类型错误，也应该成功
        assert isinstance(result, TypeCheckResult)


class TestFixErrors:
    """Test error fixing"""
    
    @pytest.fixture
    def skill(self):
        return MypySkill()
    
    def test_fix_var_annotated(self, skill, tmp_path):
        py_file = tmp_path / "test_fix.py"
        py_file.write_text("x = 1\n")
        
        result = skill.fix_errors(py_file, dry_run=True)
        assert isinstance(result, dict)
        assert "fixed_count" in result
    
    def test_fix_no_errors(self, skill, tmp_path):
        py_file = tmp_path / "clean.py"
        py_file.write_text("x: int = 1\n")
        
        result = skill.fix_errors(py_file)
        assert result["fixed_count"] == 0


class TestInferType:
    """Test type inference"""
    
    @pytest.fixture
    def skill(self):
        return MypySkill()
    
    def test_infer_string(self, skill):
        assert skill._infer_type('"hello"') == "str"
        assert skill._infer_type("'world'") == "str"
    
    def test_infer_int(self, skill):
        assert skill._infer_type("42") == "int"
        assert skill._infer_type("-10") == "int"
    
    def test_infer_float(self, skill):
        assert skill._infer_type("3.14") == "float"
        assert skill._infer_type("-0.5") == "float"
    
    def test_infer_bool(self, skill):
        assert skill._infer_type("True") == "bool"
        assert skill._infer_type("False") == "bool"
    
    def test_infer_none(self, skill):
        assert skill._infer_type("None") == "Optional[Any]"
    
    def test_infer_list(self, skill):
        assert skill._infer_type("[1, 2, 3]") == "list"
    
    def test_infer_dict(self, skill):
        assert skill._infer_type("{'a': 1}") == "dict"


class TestAddTypeAnnotation:
    """Test type annotation addition"""
    
    @pytest.fixture
    def skill(self):
        return MypySkill()
    
    def test_add_annotation_simple(self, skill):
        line = "x = 1"
        error = TypeError("", 1, 0, "error", "var-annotated", "")
        fixed = skill._add_type_annotation(line, error)
        assert "x: int = 1" in fixed
    
    def test_add_annotation_with_indent(self, skill):
        line = "    name = 'test'"
        error = TypeError("", 1, 4, "error", "var-annotated", "")
        fixed = skill._add_type_annotation(line, error)
        assert "    name: str = 'test'" in fixed


class TestAddReturnAnnotation:
    """Test return annotation addition"""
    
    @pytest.fixture
    def skill(self):
        return MypySkill()
    
    def test_add_return_annotation_simple(self, skill):
        line = "def foo():"
        error = TypeError("", 1, 0, "error", "return-value", "")
        fixed = skill._add_return_annotation(line, error)
        assert "def foo() -> None:" in fixed
    
    def test_add_return_annotation_with_params(self, skill):
        line = "def bar(x, y):"
        error = TypeError("", 1, 0, "error", "return-value", "")
        fixed = skill._add_return_annotation(line, error)
        assert "def bar(x, y) -> None:" in fixed


class TestAddTypeIgnore:
    """Test type: ignore addition"""
    
    @pytest.fixture
    def skill(self):
        return MypySkill()
    
    def test_add_type_ignore(self, skill):
        line = "x = some_undefined_var"
        error = TypeError("", 1, 0, "error", "name-defined", "")
        fixed = skill._add_type_ignore(line, error)
        assert "# type: ignore[name-defined]" in fixed
    
    def test_add_type_ignore_strips_existing(self, skill):
        line = "x = y  # old comment"
        error = TypeError("", 1, 0, "error", "attr-defined", "")
        fixed = skill._add_type_ignore(line, error)
        assert "# type: ignore[attr-defined]" in fixed
        assert "old comment" not in fixed


class TestAnalyzeErrors:
    """Test error analysis"""
    
    @pytest.fixture
    def skill(self):
        return MypySkill()
    
    def test_analyze_empty_errors(self, skill):
        result = skill.analyze_errors([])
        assert result["most_common"] is None
        assert result["recommendations"] == []
    
    def test_analyze_single_error(self, skill):
        errors = [
            TypeError("file.py", 1, 0, "error", "var-annotated", "")
        ]
        result = skill.analyze_errors(errors)
        
        assert result["most_common"]["code"] == "var-annotated"
        assert result["most_common"]["count"] == 1
        assert len(result["recommendations"]) > 0


class TestGroupByCode:
    """Test error grouping"""
    
    @pytest.fixture
    def skill(self):
        return MypySkill()
    
    def test_group_by_code(self, skill):
        errors = [
            TypeError("f1.py", 1, 0, "error", "code-a", ""),
            TypeError("f2.py", 2, 0, "error", "code-a", ""),
            TypeError("f3.py", 3, 0, "error", "code-b", ""),
        ]
        
        result = skill._group_by_code(errors)
        assert result["code-a"] == 2
        assert result["code-b"] == 1


class TestConfigureProject:
    """Test project configuration"""
    
    @pytest.fixture
    def skill(self):
        return MypySkill()
    
    def test_write_mypy_ini(self, skill, tmp_path):
        config_file = tmp_path / "mypy.ini"
        settings = {
            "python_version": "3.10",
            "warn_return_any": True,
            "ignore_missing_imports": True
        }
        
        skill._write_mypy_ini(config_file, settings)
        
        assert config_file.exists()
        content = config_file.read_text()
        assert "[mypy]" in content
        assert "python_version = 3.10" in content
        assert "warn_return_any = true" in content
    
    def test_write_pyproject_toml(self, skill, tmp_path):
        config_file = tmp_path / "pyproject.toml"
        settings = {
            "python_version": "3.11",
            "strict": False,
            "ignore_missing_imports": True
        }
        
        skill._write_pyproject_toml(config_file, settings)
        
        assert config_file.exists()
        content = config_file.read_text()
        assert "[tool.mypy]" in content
        assert 'python_version = "3.11"' in content


class TestBuildMypyCommand:
    """Test mypy command building"""
    
    @pytest.fixture
    def skill(self):
        return MypySkill()
    
    def test_basic_command(self, skill):
        cmd = skill._build_mypy_command("test.py")
        assert "mypy" in cmd
        assert "test.py" in cmd
    
    def test_strict_flag(self, skill):
        cmd = skill._build_mypy_command("test.py", strict=True)
        assert "--strict" in cmd
    
    def test_ignore_missing(self, skill):
        cmd = skill._build_mypy_command("test.py", ignore_missing=True)
        assert "--ignore-missing-imports" in cmd
    
    def test_python_version(self, skill):
        cmd = skill._build_mypy_command("test.py", python_version="3.9")
        assert "--python-version" in cmd
        assert "3.9" in cmd


class TestGenerateSuggestion:
    """Test suggestion generation"""
    
    @pytest.fixture
    def skill(self):
        return MypySkill()
    
    def test_suggestion_var_annotated(self, skill):
        error = TypeError("", 1, 0, "error", "var-annotated", "")
        suggestion = skill._generate_suggestion(error)
        assert "类型注解" in suggestion
    
    def test_suggestion_return_value(self, skill):
        error = TypeError("", 1, 0, "error", "return-value", "")
        suggestion = skill._generate_suggestion(error)
        assert "返回类型" in suggestion
    
    def test_suggestion_unknown(self, skill):
        error = TypeError("", 1, 0, "error", "unknown-code", "")
        suggestion = skill._generate_suggestion(error)
        assert "mypy文档" in suggestion


class TestTypeErrorDataClass:
    """Test TypeError dataclass"""
    
    def test_error_creation(self):
        error = TypeError(
            file_path="test.py",
            line=10,
            column=5,
            severity="error",
            code="test-code",
            message="Test message",
            error_type="测试类型",
            suggestion="修复建议"
        )
        
        assert error.file_path == "test.py"
        assert error.line == 10
        assert error.severity == "error"


class TestTypeCheckResultDataClass:
    """Test TypeCheckResult dataclass"""
    
    def test_result_creation(self):
        result = TypeCheckResult(
            success=True,
            file_path="test.py",
            errors=[],
            warnings=[]
        )
        
        assert result.success is True
        assert result.error_count == 0
        assert result.warning_count == 0
    
    def test_result_with_errors(self):
        errors = [
            TypeError("f.py", 1, 0, "error", "c1", ""),
            TypeError("f.py", 2, 0, "error", "c2", "")
        ]
        result = TypeCheckResult(
            success=False,
            file_path="test.py",
            errors=errors,
            warnings=[]
        )
        
        assert result.error_count == 2
        assert result.warning_count == 0


class TestShouldSkip:
    """Test file skipping logic"""
    
    @pytest.fixture
    def skill(self):
        return MypySkill()
    
    def test_skip_venv(self, skill, tmp_path):
        venv_path = tmp_path / "venv" / "lib" / "test.py"
        venv_path.parent.mkdir(parents=True)
        venv_path.write_text("x = 1\n")
        
        assert skill._should_skip(venv_path) is True
    
    def test_skip_mypy_cache(self, skill, tmp_path):
        cache_path = tmp_path / ".mypy_cache" / "test.py"
        cache_path.parent.mkdir(parents=True)
        cache_path.write_text("x = 1\n")
        
        assert skill._should_skip(cache_path) is True
    
    def test_dont_skip_normal(self, skill, tmp_path):
        normal_path = tmp_path / "src" / "module.py"
        normal_path.parent.mkdir(parents=True)
        normal_path.write_text("x = 1\n")
        
        assert skill._should_skip(normal_path) is False


class TestErrorCategories:
    """Test error categories"""
    
    def test_error_categories_exist(self):
        skill = MypySkill()
        assert "arg-type" in skill.ERROR_CATEGORIES
        assert "return-value" in skill.ERROR_CATEGORIES
        assert "var-annotated" in skill.ERROR_CATEGORIES


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
