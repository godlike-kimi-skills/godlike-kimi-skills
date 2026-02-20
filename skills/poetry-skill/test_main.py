"""Tests for poetry-skill main module"""
import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import PoetrySkill, ProjectInfo, DependencyInfo, BuildInfo


class TestPoetrySkillInit:
    """Test PoetrySkill initialization"""
    
    def test_default_init(self):
        skill = PoetrySkill()
        assert skill.virtualenvs_create is True
        assert skill.virtualenvs_in_project is True
        assert skill.max_workers == 4
    
    def test_custom_init(self):
        config = {
            "virtualenvs_create": False,
            "virtualenvs_in_project": False,
            "installer_max_workers": 8
        }
        skill = PoetrySkill(config)
        assert skill.virtualenvs_create is False
        assert skill.virtualenvs_in_project is False
        assert skill.max_workers == 8


class TestNormalizePackageName:
    """Test package name normalization"""
    
    @pytest.fixture
    def skill(self):
        return PoetrySkill()
    
    def test_normalize_simple(self, skill):
        assert skill._normalize_package_name("my-package") == "my_package"
    
    def test_normalize_with_spaces(self, skill):
        assert skill._normalize_package_name("my package") == "my_package"
    
    def test_normalize_mixed(self, skill):
        assert skill._normalize_package_name("My-Package Name") == "my_package_name"
    
    def test_normalize_already_normalized(self, skill):
        assert skill._normalize_package_name("my_package") == "my_package"


class TestInitProject:
    """Test project initialization"""
    
    @pytest.fixture
    def skill(self):
        return PoetrySkill()
    
    def test_init_creates_directory(self, skill, tmp_path):
        result = skill.init_project("test-project", path=tmp_path)
        
        project_path = Path(result["project_path"])
        assert project_path.exists()
        assert (project_path / "test_project").exists()
        assert (project_path / "tests").exists()
    
    def test_init_creates_pyproject_toml(self, skill, tmp_path):
        result = skill.init_project("my-project", 
                                     description="Test desc",
                                     author="Test Author",
                                     path=tmp_path)
        
        project_path = Path(result["project_path"])
        pyproject = project_path / "pyproject.toml"
        assert pyproject.exists()
        
        content = pyproject.read_text()
        assert "name = \"my-project\"" in content
        assert "Test desc" in content
        assert "Test Author" in content
    
    def test_init_creates_readme(self, skill, tmp_path):
        result = skill.init_project("test-project", path=tmp_path)
        
        readme = Path(result["project_path"]) / "README.md"
        assert readme.exists()
        assert "# test-project" in readme.read_text()


class TestGeneratePyprojectToml:
    """Test pyproject.toml generation"""
    
    @pytest.fixture
    def skill(self):
        return PoetrySkill()
    
    def test_generates_valid_toml(self, skill, tmp_path):
        skill._generate_pyproject_toml(tmp_path, "test-project", {
            "description": "A test project",
            "author": "Test <test@test.com>",
            "python": "^3.10",
            "license": "Apache-2.0"
        })
        
        toml_file = tmp_path / "pyproject.toml"
        assert toml_file.exists()
        
        content = toml_file.read_text()
        assert '[tool.poetry]' in content
        assert 'name = "test-project"' in content
        assert 'python = "^3.10"' in content
        assert "Apache-2.0" in content


class TestParsePyprojectToml:
    """Test pyproject.toml parsing"""
    
    @pytest.fixture
    def skill(self):
        return PoetrySkill()
    
    def test_parse_basic_info(self, skill):
        content = '''[tool.poetry]
name = "my-project"
version = "1.0.0"
description = "My project"
readme = "README.md"
license = "MIT"

[tool.poetry.dependencies]
python = "^3.9"
requests = "^2.28.0"
'''
        info = skill._parse_pyproject_toml(content)
        
        assert info.name == "my-project"
        assert info.version == "1.0.0"
        assert info.description == "My project"
        assert info.license == "MIT"
        assert info.python_version == "^3.9"
        assert info.dependencies["requests"] == "^2.28.0"


class TestProjectInfo:
    """Test ProjectInfo dataclass"""
    
    def test_project_info_creation(self):
        info = ProjectInfo(
            name="test",
            version="1.0.0",
            description="Test project",
            authors=["Author"],
            dependencies={"requests": "^2.0"},
            python_version="^3.10"
        )
        
        assert info.name == "test"
        assert info.version == "1.0.0"
        assert len(info.dependencies) == 1


class TestDependencyInfo:
    """Test DependencyInfo dataclass"""
    
    def test_dependency_info_creation(self):
        dep = DependencyInfo(
            name="requests",
            version="^2.28.0",
            category="main",
            optional=False
        )
        
        assert dep.name == "requests"
        assert dep.version == "^2.28.0"
        assert dep.category == "main"


class TestBuildInfo:
    """Test BuildInfo dataclass"""
    
    def test_build_info_success(self):
        info = BuildInfo(
            success=True,
            artifacts=["dist/package-1.0.0-py3-none-any.whl"]
        )
        
        assert info.success is True
        assert len(info.artifacts) == 1
    
    def test_build_info_failure(self):
        info = BuildInfo(
            success=False,
            errors=["Build failed"]
        )
        
        assert info.success is False
        assert len(info.errors) == 1


class TestValidateBuild:
    """Test build validation"""
    
    @pytest.fixture
    def skill(self):
        return PoetrySkill()
    
    def test_validate_missing_pyproject(self, skill, tmp_path):
        result = skill.validate_build(cwd=tmp_path)
        assert result is False
    
    def test_validate_valid_pyproject(self, skill, tmp_path):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('''[tool.poetry]
name = "test"
version = "0.1.0"
description = "Test"

[build-system]
requires = ["poetry-core"]
''')
        
        result = skill.validate_build(cwd=tmp_path)
        assert result is True


class TestGenerateInitFile:
    """Test __init__.py generation"""
    
    @pytest.fixture
    def skill(self):
        return PoetrySkill()
    
    def test_generate_init(self, skill, tmp_path):
        skill._generate_init_file(tmp_path, "my_package")
        
        init_file = tmp_path / "__init__.py"
        assert init_file.exists()
        
        content = init_file.read_text()
        assert '"""my_package package"""' in content
        assert '__version__ = "0.1.0"' in content


class TestGenerateGitignore:
    """Test .gitignore generation"""
    
    @pytest.fixture
    def skill(self):
        return PoetrySkill()
    
    def test_generate_gitignore(self, skill, tmp_path):
        skill._generate_gitignore(tmp_path)
        
        gitignore = tmp_path / ".gitignore"
        assert gitignore.exists()
        
        content = gitignore.read_text()
        assert "__pycache__/" in content
        assert ".venv/" in content


class TestGenerateReadme:
    """Test README generation"""
    
    @pytest.fixture
    def skill(self):
        return PoetrySkill()
    
    def test_generate_readme(self, skill, tmp_path):
        skill._generate_readme(tmp_path, "my-project", {
            "description": "A test project",
            "license": "MIT"
        })
        
        readme = tmp_path / "README.md"
        assert readme.exists()
        
        content = readme.read_text()
        assert "# my-project" in content
        assert "A test project" in content
        assert "pip install my-project" in content


class TestProjectStructure:
    """Test complete project structure"""
    
    @pytest.fixture
    def skill(self):
        return PoetrySkill()
    
    def test_full_project_structure(self, skill, tmp_path):
        result = skill.init_project("full-test", path=tmp_path)
        
        project_path = Path(result["project_path"])
        
        # Check all expected files exist
        assert (project_path / "pyproject.toml").exists()
        assert (project_path / "README.md").exists()
        assert (project_path / ".gitignore").exists()
        assert (project_path / "full_test" / "__init__.py").exists()
        assert (project_path / "tests" / "__init__.py").exists()
        
        # Check files created list
        assert "pyproject.toml" in result["files_created"]
        assert "README.md" in result["files_created"]


class TestSkillConfiguration:
    """Test skill configuration handling"""
    
    def test_default_config_values(self):
        skill = PoetrySkill()
        assert skill.config == {}
    
    def test_custom_config_values(self):
        config = {
            "virtualenvs_create": False,
            "installer_max_workers": 2
        }
        skill = PoetrySkill(config)
        assert skill.config == config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
