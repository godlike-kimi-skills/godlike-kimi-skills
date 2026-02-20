"""Skill-specific tests for black-isort-skill"""
import json
import sys
from pathlib import Path

import pytest

# Import the skill module
sys.path.insert(0, str(Path(__file__).parent))

from main import BlackIsortSkill, main


class TestSkillInterface:
    """Test that the skill adheres to the skill interface requirements"""
    
    def test_skill_has_required_methods(self):
        skill = BlackIsortSkill()
        required_methods = [
            "format_code",
            "format_file",
            "format_project",
            "check_format",
            "configure_project",
            "generate_diff",
            "is_formatted"
        ]
        
        for method in required_methods:
            assert hasattr(skill, method), f"Missing method: {method}"
            assert callable(getattr(skill, method)), f"{method} is not callable"
    
    def test_skill_initialization_with_config(self):
        config = {
            "line_length": 100,
            "skip_string_normalization": True
        }
        skill = BlackIsortSkill(config)
        
        assert skill.config.line_length == 100
        assert skill.config.skip_string_normalization is True


class TestSkillMetadata:
    """Test skill.json metadata"""
    
    @pytest.fixture
    def skill_json(self):
        skill_path = Path(__file__).parent / "skill.json"
        if skill_path.exists():
            return json.loads(skill_path.read_text())
        return {}
    
    def test_skill_json_exists(self, skill_json):
        assert skill_json, "skill.json should exist"
    
    def test_required_fields(self, skill_json):
        required = ["name", "version", "description", "category", "entry"]
        for field in required:
            assert field in skill_json, f"Missing required field: {field}"
    
    def test_category_is_python(self, skill_json):
        assert skill_json.get("category") == "python"
    
    def test_name_matches_directory(self, skill_json):
        assert skill_json.get("name") == "black-isort-skill"


class TestSkillEntryPoint:
    """Test the skill entry point (main function)"""
    
    def test_main_function_exists(self):
        assert callable(main)
    
    def test_main_with_help(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            import argparse
            parser = argparse.ArgumentParser()
            parser.print_help()
        # Help should exit with 0


class TestSkillDocumentation:
    """Test that documentation exists and is valid"""
    
    def test_skill_md_exists(self):
        skill_md = Path(__file__).parent / "SKILL.md"
        assert skill_md.exists(), "SKILL.md should exist"
    
    def test_skill_md_has_use_when(self):
        skill_md = Path(__file__).parent / "SKILL.md"
        content = skill_md.read_text()
        assert "## Use When" in content
    
    def test_skill_md_has_out_of_scope(self):
        skill_md = Path(__file__).parent / "SKILL.md"
        content = skill_md.read_text()
        assert "## Out of Scope" in content
    
    def test_skill_md_has_black_content(self):
        skill_md = Path(__file__).parent / "SKILL.md"
        content = skill_md.read_text()
        assert "Black" in content
    
    def test_skill_md_has_isort_content(self):
        skill_md = Path(__file__).parent / "SKILL.md"
        content = skill_md.read_text()
        assert "isort" in content


class TestSkillCodeQuality:
    """Test code quality aspects"""
    
    def test_no_syntax_errors(self):
        main_file = Path(__file__).parent / "main.py"
        try:
            compile(main_file.read_text(), str(main_file), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in main.py: {e}")
    
    def test_importable(self):
        try:
            from main import BlackIsortSkill, main
        except ImportError as e:
            pytest.fail(f"Cannot import from main: {e}")


class TestSkillFunctionality:
    """Test core functionality of the skill"""
    
    @pytest.fixture
    def skill(self):
        return BlackIsortSkill()
    
    def test_format_code_returns_string(self, skill):
        code = "x = 1"
        result = skill.format_code(code)
        assert isinstance(result, str)
    
    def test_format_file_returns_result(self, skill, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text("x=1\n")
        
        result = skill.format_file(py_file)
        assert hasattr(result, 'success')
        assert hasattr(result, 'changed')
    
    def check_format_returns_list(self, skill, tmp_path):
        result = skill.check_format(str(tmp_path))
        assert isinstance(result, list)
    
    def test_is_formatted_returns_bool(self, skill, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text("x = 1\n")
        
        result = skill.is_formatted(py_file)
        assert isinstance(result, bool)


class TestSkillErrorHandling:
    """Test error handling"""
    
    @pytest.fixture
    def skill(self):
        return BlackIsortSkill()
    
    def test_nonexistent_file_returns_error(self, skill):
        result = skill.format_file("/nonexistent/path.py")
        assert result.success is False
        assert result.error_message != ""
    
    def test_invalid_config_raises_error(self, skill, tmp_path):
        with pytest.raises(ValueError):
            skill.configure_project(str(tmp_path / "invalid.txt"), {})


class TestSkillConfiguration:
    """Test skill configuration options"""
    
    def test_default_line_length(self):
        skill = BlackIsortSkill()
        assert skill.config.line_length == 88
    
    def test_custom_line_length(self):
        skill = BlackIsortSkill({"line_length": 120})
        assert skill.config.line_length == 120
    
    def test_default_skip_directories(self):
        skill = BlackIsortSkill()
        assert ".git" in skill.config.skip_directories
        assert "__pycache__" in skill.config.skip_directories


class TestSkillDependencies:
    """Test dependency checking"""
    
    def test_check_dependencies(self):
        skill = BlackIsortSkill()
        # Should check for black and isort availability
        assert hasattr(skill, 'black_available')
        assert hasattr(skill, 'isort_available')
        assert isinstance(skill.black_available, bool)
        assert isinstance(skill.isort_available, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
