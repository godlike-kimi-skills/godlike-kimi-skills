"""Skill-specific tests for poetry-skill"""
import json
import sys
from pathlib import Path

import pytest

# Import the skill module
sys.path.insert(0, str(Path(__file__).parent))

from main import PoetrySkill, main


class TestSkillInterface:
    """Test that the skill adheres to the skill interface requirements"""
    
    def test_skill_has_required_methods(self):
        skill = PoetrySkill()
        required_methods = [
            "init_project",
            "add_dependency",
            "remove_dependency",
            "install",
            "update",
            "build",
            "publish",
            "get_project_info",
            "manage_venv",
            "export_requirements",
            "validate_build"
        ]
        
        for method in required_methods:
            assert hasattr(skill, method), f"Missing method: {method}"
            assert callable(getattr(skill, method)), f"{method} is not callable"
    
    def test_skill_initialization_with_config(self):
        config = {
            "virtualenvs_create": False,
            "virtualenvs_in_project": False
        }
        skill = PoetrySkill(config)
        
        assert skill.virtualenvs_create is False
        assert skill.virtualenvs_in_project is False


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
        assert skill_json.get("name") == "poetry-skill"


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
    
    def test_skill_md_has_poetry_content(self):
        skill_md = Path(__file__).parent / "SKILL.md"
        content = skill_md.read_text()
        assert "Poetry" in content


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
            from main import PoetrySkill, main
        except ImportError as e:
            pytest.fail(f"Cannot import from main: {e}")


class TestSkillFunctionality:
    """Test core functionality of the skill"""
    
    @pytest.fixture
    def skill(self):
        return PoetrySkill()
    
    def test_init_project_returns_dict(self, skill, tmp_path):
        result = skill.init_project("test", path=tmp_path)
        assert isinstance(result, dict)
        assert "success" in result
        assert "project_path" in result
    
    def test_get_project_info_returns_project_info(self, skill, tmp_path):
        # Create a minimal pyproject.toml
        (tmp_path / "pyproject.toml").write_text('''[tool.poetry]
name = "test-project"
version = "1.0.0"
description = "Test"

[tool.poetry.dependencies]
python = "^3.10"
''')
        
        info = skill.get_project_info(cwd=tmp_path)
        assert info.name == "test-project"
        assert info.version == "1.0.0"
    
    def test_validate_build_returns_bool(self, skill, tmp_path):
        result = skill.validate_build(cwd=tmp_path)
        assert isinstance(result, bool)


class TestSkillErrorHandling:
    """Test error handling"""
    
    @pytest.fixture
    def skill(self):
        return PoetrySkill()
    
    def test_manage_venv_invalid_action(self, skill):
        result = skill.manage_venv("invalid_action")
        assert result["success"] is False
        assert "error" in result


class TestSkillConfiguration:
    """Test skill configuration options"""
    
    def test_default_virtualenvs_create(self):
        skill = PoetrySkill()
        assert skill.virtualenvs_create is True
    
    def test_custom_virtualenvs_create(self):
        skill = PoetrySkill({"virtualenvs_create": False})
        assert skill.virtualenvs_create is False
    
    def test_default_virtualenvs_in_project(self):
        skill = PoetrySkill()
        assert skill.virtualenvs_in_project is True


class TestSkillPoetryAvailability:
    """Test poetry availability checking"""
    
    def test_poetry_availability_attribute(self):
        skill = PoetrySkill()
        assert hasattr(skill, 'poetry_available')
        assert isinstance(skill.poetry_available, bool)
    
    def test_poetry_version_attribute(self):
        skill = PoetrySkill()
        assert hasattr(skill, 'poetry_version')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
