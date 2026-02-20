"""Skill-specific tests for pytest-skill"""
import json
from pathlib import Path

import pytest

# Import the skill module
import sys
sys.path.insert(0, str(Path(__file__).parent))

from main import PytestSkill, main


class TestSkillInterface:
    """Test that the skill adheres to the skill interface requirements"""
    
    def test_skill_has_required_methods(self):
        skill = PytestSkill()
        required_methods = [
            "generate_tests",
            "run_tests", 
            "analyze_coverage",
            "generate_coverage_report",
            "analyze_fixtures",
            "optimize_fixtures",
            "configure_project"
        ]
        
        for method in required_methods:
            assert hasattr(skill, method), f"Missing method: {method}"
            assert callable(getattr(skill, method)), f"{method} is not callable"
    
    def test_skill_initialization_with_config(self):
        config = {
            "coverage_target": 85,
            "parallel_workers": 2,
            "testpaths": ["tests", "test_integration"]
        }
        skill = PytestSkill(config)
        
        assert skill.config == config
        assert skill.coverage_target == 85
        assert skill.parallel_workers == 2


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
        assert skill_json.get("name") == "pytest-skill"


class TestSkillEntryPoint:
    """Test the skill entry point (main function)"""
    
    def test_main_function_exists(self):
        assert callable(main)
    
    def test_main_with_generate_command(self, capsys):
        # This would need actual files to test properly
        # Just verify it doesn't crash with help
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0 or exc_info.value.code is None


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
            from main import PytestSkill, main
        except ImportError as e:
            pytest.fail(f"Cannot import from main: {e}")


class TestSkillFunctionality:
    """Test core functionality of the skill"""
    
    @pytest.fixture
    def skill(self):
        return PytestSkill()
    
    def test_generate_tests_returns_string(self, skill, tmp_path):
        # Create a simple module
        module = tmp_path / "test_module.py"
        module.write_text("def foo(): pass")
        
        result = skill.generate_tests(str(module))
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_analyze_fixtures_returns_list(self, skill, tmp_path):
        # Create a test file with fixtures
        test_file = tmp_path / "test_fixtures.py"
        test_file.write_text('''
import pytest

@pytest.fixture
def my_fixture():
    return 42
''')
        
        result = skill.analyze_fixtures(str(test_file))
        assert isinstance(result, list)
    
    def test_optimize_fixtures_returns_dict(self, skill):
        fixtures = []
        result = skill.optimize_fixtures(fixtures)
        assert isinstance(result, dict)
        assert "duplicate_fixtures" in result


class TestSkillErrorHandling:
    """Test error handling"""
    
    @pytest.fixture
    def skill(self):
        return PytestSkill()
    
    def test_nonexistent_path_raises_error(self, skill):
        with pytest.raises(FileNotFoundError):
            skill.generate_tests("/nonexistent/path.py")
    
    def test_invalid_config_format(self, skill, tmp_path):
        with pytest.raises(ValueError):
            skill.configure_project(str(tmp_path / "invalid.txt"), {})


class TestSkillConfiguration:
    """Test skill configuration options"""
    
    def test_default_configuration(self):
        skill = PytestSkill()
        assert skill.coverage_target == 80
        assert skill.parallel_workers == 4
    
    def test_custom_configuration(self):
        config = {
            "coverage_target": 95,
            "parallel_workers": 8
        }
        skill = PytestSkill(config)
        assert skill.coverage_target == 95
        assert skill.parallel_workers == 8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
