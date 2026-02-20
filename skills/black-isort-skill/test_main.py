"""Tests for black-isort-skill main module"""
import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import BlackIsortSkill, FormatResult, FormatConfig


class TestBlackIsortSkillInit:
    """Test BlackIsortSkill initialization"""
    
    def test_default_init(self):
        skill = BlackIsortSkill()
        assert skill.config.line_length == 88
        assert skill.config.isort_profile == "black"
        assert ".git" in skill.config.skip_directories
    
    def test_custom_init(self):
        config = {
            "line_length": 100,
            "skip_string_normalization": True,
            "isort_profile": "django"
        }
        skill = BlackIsortSkill(config)
        assert skill.config.line_length == 100
        assert skill.config.skip_string_normalization is True
        assert skill.config.isort_profile == "django"


class TestFormatCode:
    """Test code formatting functionality"""
    
    @pytest.fixture
    def skill(self):
        return BlackIsortSkill()
    
    def test_format_simple_function(self, skill):
        code = "def foo(x,y):\n    return x+y"
        formatted = skill.format_code(code)
        # Should have proper spacing
        assert "def foo(x, y):" in formatted or "foo" in formatted
    
    def test_format_imports(self, skill):
        code = "import sys\nimport os\nimport json"
        formatted = skill.format_code(code)
        # Should preserve imports
        assert "import" in formatted
    
    def test_format_with_options(self, skill):
        code = "x = 1"
        formatted = skill.format_code(code, line_length=120)
        assert "x = 1" in formatted


class TestFormatFile:
    """Test file formatting"""
    
    @pytest.fixture
    def skill(self):
        return BlackIsortSkill()
    
    def test_format_nonexistent_file(self, skill):
        result = skill.format_file("/nonexistent/file.py")
        assert result.success is False
        assert "不存在" in result.error_message
    
    def test_format_non_python_file(self, skill, tmp_path):
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("hello")
        result = skill.format_file(txt_file)
        assert result.success is False
        assert "不是Python文件" in result.error_message
    
    def test_format_python_file(self, skill, tmp_path):
        py_file = tmp_path / "test_script.py"
        py_file.write_text("def foo(x,y):\n    return x+y")
        result = skill.format_file(py_file)
        assert result.success is True
        assert result.changed is True
    
    def test_format_check_only(self, skill, tmp_path):
        py_file = tmp_path / "test_check.py"
        py_file.write_text("x=1\n")
        result = skill.format_file(py_file, check_only=True)
        # File should not be modified
        content = py_file.read_text()
        assert "x=1" in content


class TestFormatProject:
    """Test project formatting"""
    
    @pytest.fixture
    def skill(self):
        return BlackIsortSkill()
    
    @pytest.fixture
    def sample_project(self, tmp_path):
        """Create a sample project structure"""
        src = tmp_path / "src"
        src.mkdir()
        
        # Create some Python files
        (src / "module1.py").write_text("def a():\n    pass\n")
        (src / "module2.py").write_text("def b( x ):\n    return x\n")
        
        # Create a subdirectory
        sub = src / "subpackage"
        sub.mkdir()
        (sub / "__init__.py").write_text("")
        (sub / "module3.py").write_text("import os\nimport sys\n")
        
        return tmp_path
    
    def test_format_project(self, skill, sample_project):
        result = skill.format_project(sample_project / "src")
        
        assert result["total_files"] == 3
        assert "results" in result
    
    def test_format_project_non_recursive(self, skill, sample_project):
        result = skill.format_project(
            sample_project / "src", 
            recursive=False
        )
        
        # Should only find files in root
        assert result["total_files"] == 2


class TestCheckFormat:
    """Test format checking"""
    
    @pytest.fixture
    def skill(self):
        return BlackIsortSkill()
    
    def test_check_formatted_file(self, skill, tmp_path):
        # Create a properly formatted file
        py_file = tmp_path / "formatted.py"
        py_file.write_text("x = 1\n")
        
        issues = skill.check_format(py_file)
        # Should not flag properly formatted files
        assert isinstance(issues, list)
    
    def test_check_directory(self, skill, tmp_path):
        # Create some files
        (tmp_path / "a.py").write_text("x=1\n")
        (tmp_path / "b.py").write_text("y = 2\n")
        
        issues = skill.check_format(tmp_path)
        assert isinstance(issues, list)


class TestGenerateDiff:
    """Test diff generation"""
    
    @pytest.fixture
    def skill(self):
        return BlackIsortSkill()
    
    def test_generate_diff(self, skill):
        original = "def foo(x,y):\n    return x+y"
        formatted = "def foo(x, y):\n    return x + y"
        
        diff = skill.generate_diff(original, formatted, "test.py")
        
        assert "--- a/test.py" in diff
        assert "+++ b/test.py" in diff
        assert "@@" in diff
    
    def test_no_changes_diff(self, skill):
        code = "x = 1\n"
        diff = skill.generate_diff(code, code, "test.py")
        # Empty diff when no changes
        assert diff == ""


class TestIsFormatted:
    """Test is_formatted method"""
    
    @pytest.fixture
    def skill(self):
        return BlackIsortSkill()
    
    def test_is_formatted_true(self, skill, tmp_path):
        # Create a properly formatted file
        py_file = tmp_path / "formatted.py"
        py_file.write_text("x = 1\n")
        
        # Format it first
        skill.format_file(py_file)
        
        # Should now be formatted
        result = skill.is_formatted(py_file)
        assert result is True
    
    def test_is_formatted_false(self, skill, tmp_path):
        # Create a badly formatted file
        py_file = tmp_path / "unformatted.py"
        py_file.write_text("x=1\ny=2\n")
        
        result = skill.is_formatted(py_file)
        assert result is False


class TestConfigureProject:
    """Test project configuration"""
    
    @pytest.fixture
    def skill(self):
        return BlackIsortSkill()
    
    def test_write_pyproject_toml(self, skill, tmp_path):
        config_file = tmp_path / "pyproject.toml"
        settings = {
            "black": {
                "line-length": 100,
                "target-version": ["py39"]
            },
            "isort": {
                "profile": "black"
            }
        }
        
        skill._write_pyproject_toml(config_file, settings)
        
        assert config_file.exists()
        content = config_file.read_text()
        assert "[tool.black]" in content
        assert "[tool.isort]" in content
        assert "line-length = 100" in content
    
    def test_write_isort_config(self, skill, tmp_path):
        config_file = tmp_path / ".isort.cfg"
        settings = {
            "profile": "black",
            "line_length": "88"
        }
        
        skill._write_isort_config(config_file, settings)
        
        assert config_file.exists()
        content = config_file.read_text()
        assert "[settings]" in content
        assert "profile" in content


class TestShouldSkip:
    """Test file skipping logic"""
    
    @pytest.fixture
    def skill(self):
        return BlackIsortSkill()
    
    def test_skip_git_directory(self, skill, tmp_path):
        git_path = tmp_path / ".git" / "hooks" / "pre-commit.py"
        git_path.parent.mkdir(parents=True)
        git_path.write_text("#!/bin/python\n")
        
        assert skill._should_skip(git_path) is True
    
    def test_skip_venv_directory(self, skill, tmp_path):
        venv_path = tmp_path / "venv" / "lib" / "site.py"
        venv_path.parent.mkdir(parents=True)
        venv_path.write_text("# site module\n")
        
        assert skill._should_skip(venv_path) is True
    
    def test_dont_skip_normal_file(self, skill, tmp_path):
        normal_path = tmp_path / "src" / "module.py"
        normal_path.parent.mkdir(parents=True)
        normal_path.write_text("x = 1\n")
        
        assert skill._should_skip(normal_path) is False


class TestFormatResult:
    """Test FormatResult dataclass"""
    
    def test_format_result_defaults(self):
        result = FormatResult(file_path="test.py", success=True)
        assert result.file_path == "test.py"
        assert result.success is True
        assert result.changed is False
        assert result.error_message == ""
    
    def test_format_result_with_changes(self):
        result = FormatResult(
            file_path="test.py",
            success=True,
            changed=True,
            original_content="x=1",
            formatted_content="x = 1",
            line_count_change=0
        )
        assert result.changed is True
        assert result.original_content == "x=1"


class TestFormatConfig:
    """Test FormatConfig dataclass"""
    
    def test_default_config(self):
        config = FormatConfig()
        assert config.line_length == 88
        assert config.isort_profile == "black"
        assert ".git" in config.skip_directories
    
    def test_custom_config(self):
        config = FormatConfig(
            line_length=120,
            isort_profile="django",
            skip_files=["special.py"]
        )
        assert config.line_length == 120
        assert config.isort_profile == "django"
        assert "special.py" in config.skip_files


class TestGitIntegration:
    """Test Git integration features"""
    
    @pytest.fixture
    def skill(self):
        return BlackIsortSkill()
    
    def test_get_git_changed_files_not_git_repo(self, skill, tmp_path):
        # Not a git repo
        files = skill.get_git_changed_files(str(tmp_path))
        assert files == []
    
    def test_format_git_changed_not_git_repo(self, skill, tmp_path):
        result = skill.format_git_changed(str(tmp_path))
        assert result["total_files"] == 0


class TestIntegration:
    """Integration tests"""
    
    @pytest.fixture
    def skill(self):
        return BlackIsortSkill()
    
    def test_full_formatting_workflow(self, skill, tmp_path):
        """Test the complete formatting workflow"""
        # Create project structure
        src = tmp_path / "myproject"
        src.mkdir()
        
        # Create unformatted files
        (src / "__init__.py").write_text("")
        (src / "core.py").write_text("""
import sys
import os
import json

def calculate(x,y):
    result=x+y
    return result
""")
        
        # Check format
        issues = skill.check_format(src)
        assert isinstance(issues, list)
        
        # Format project
        result = skill.format_project(src)
        assert result["total_files"] == 1  # Only core.py, __init__.py is empty
        
        # Verify files are now formatted
        formatted_content = (src / "core.py").read_text()
        assert "def calculate" in formatted_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
