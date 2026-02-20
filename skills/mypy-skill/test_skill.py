"""Skill-specific tests for mypy-skill"""
import json
import sys
from pathlib import Path

import pytest

# Import the skill module
sys.path.insert(0, str(Path(__file__).parent))

from main import MypySkill, main


class TestSkillInterface:
    """Test that the skill adheres to the skill interface requirements"""
    
    def test_skill_has_required_methods(self):
        skill = MypySkill()
        required_methods = [
            "check_file",
            "check_project",
            "fix_errors",
            "generate_annotations",
            "configure_project",
            "analyze_errors",
            "get_error_stats"
        ]
        
        for method in required_methods:
            assert hasattr(skill, method), f"Missing method: {method}"
            assert callable(getattr(skill, method)), f"{method} is not callable"
    
    def test_skill_initialization_with_config(self):
        config = {
            "strict_mode": True,
            "ignore_missing_imports": False,
            "disallow_untyped_defs": True
        }
        skill = MypySkill(config)
        
        assert skill.strict_mode is True
        assert skill.ignore_missing_imports is False


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
        assert skill_json.get("name") == "mypy-skill"


class TestSkillEntryPoint:
    """Test the skill entry point (main function)"""
    
    def test_main_function_exists(self):
        assert callable(main)


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
    
    def test_skill_md_has_mypy_content(self):
        skill_md = Path(__file__).parent / "SKILL.md"
        content = skill_md.read_text()
        assert "mypy" in content.lower()


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
            from main import MypySkill, main
        except ImportError as e:
            pytest.fail(f"Cannot import from main: {e}")


class TestSkillFunctionality:
    """Test core functionality of the skill"""
    
    @pytest.fixture
    def skill(self):
        return MypySkill()
    
    def test_check_file_returns_result(self, skill, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text("x = 1\n")
        
        result = skill.check_file(py_file)
        assert hasattr(result, 'success')
        assert hasattr(result, 'errors')
    
    def test_check_project_returns_dict(self, skill, tmp_path):
        result = skill.check_project(tmp_path)
        assert isinstance(result, dict)
        assert "success" in result
    
    def test_fix_errors_returns_dict(self, skill, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text("x = 1\n")
        
        result = skill.fix_errors(py_file)
        assert isinstance(result, dict)
        assert "fixed_count" in result
    
    def test_generate_annotations_returns_string(self, skill, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text("def foo(): pass\n")
        
        result = skill.generate_annotations(py_file)
        assert isinstance(result, str)


class TestSkillErrorHandling:
    """Test error handling"""
    
    @pytest.fixture
    def skill(self):
        return MypySkill()
    
    def test_nonexistent_file_returns_error(self, skill):
        result = skill.check_file("/nonexistent/path.py")
        assert result.success is False
        assert result.error_count > 0
    
    def test_invalid_config_raises_error(self, skill, tmp_path):
        with pytest.raises(ValueError):
            skill.configure_project(str(tmp_path / "invalid.txt"), {})


class TestSkillConfiguration:
    """Test skill configuration options"""
    
    def test_default_strict_mode(self):
        skill = MypySkill()
        assert skill.strict_mode is False
    
    def test_custom_strict_mode(self):
        skill = MypySkill({"strict_mode": True})
        assert skill.strict_mode is True
    
    def test_default_ignore_missing(self):
        skill = MypySkill()
        assert skill.ignore_missing_imports is True


class TestSkillMypyAvailability:
    """Test mypy availability checking"""
    
    def test_mypy_availability_attribute(self):
        skill = MypySkill()
        assert hasattr(skill, 'mypy_available')
        assert isinstance(skill.mypy_available, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
