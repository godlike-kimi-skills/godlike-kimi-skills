"""
GitLab CI Skill 测试套件
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import yaml
from main import GitLabCISkill


class TestGitLabCISkill(unittest.TestCase):
    """测试GitLabCISkill类"""
    
    @patch('main.gitlab.Gitlab')
    def setUp(self, mock_gitlab):
        """测试前准备"""
        mock_gl = MagicMock()
        mock_gitlab.return_value = mock_gl
        
        mock_project = MagicMock()
        mock_gl.projects.get.return_value = mock_project
        
        self.skill = GitLabCISkill(
            token="test-token",
            project="group/project",
            url="https://gitlab.com"
        )
        self.mock_gl = mock_gl
        self.mock_project = mock_project
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.skill.token, "test-token")
        self.assertEqual(self.skill.project_id, "group/project")
        self.assertEqual(self.skill.url, "https://gitlab.com")
    
    def test_init_missing_token(self):
        """测试无token初始化"""
        with self.assertRaises(ValueError):
            GitLabCISkill(project="group/project")
    
    @patch.dict('os.environ', {
        'GITLAB_TOKEN': 'env-token',
        'GITLAB_PROJECT': 'env/project'
    })
    @patch('main.gitlab.Gitlab')
    def test_init_from_env(self, mock_gitlab):
        """测试从环境变量初始化"""
        mock_gl = MagicMock()
        mock_gitlab.return_value = mock_gl
        
        skill = GitLabCISkill()
        self.assertEqual(skill.token, "env-token")
        self.assertEqual(skill.project_id, "env/project")
    
    def test_create_response(self):
        """测试响应创建"""
        response = self.skill._create_response(True, data="test")
        self.assertTrue(response["success"])
        self.assertEqual(response["data"], "test")
        self.assertIsNone(response["error"])
        self.assertIn("timestamp", response)
    
    @patch('main.base64.b64decode')
    def test_get_ci_config(self, mock_b64decode):
        """测试获取CI配置"""
        mock_file = MagicMock()
        mock_file.content = "ZW5jb2RlZCBjb250ZW50"
        mock_file.sha = "abc123"
        mock_b64decode.return_value = b"stages:\n  - test"
        
        self.mock_project.files.get.return_value = mock_file
        
        result = self.skill.get_ci_config("main")
        
        self.assertTrue(result["success"])
        self.assertIn("content", result["data"])
        self.assertIn("parsed", result["data"])
    
    def test_get_ci_config_not_found(self):
        """测试获取不存在的CI配置"""
        from gitlab.exceptions import GitlabError
        mock_response = MagicMock()
        mock_response.status_code = 404
        self.mock_project.files.get.side_effect = GitlabError("Not found", response_code=404)
        
        result = self.skill.get_ci_config("main")
        
        self.assertFalse(result["success"])
        self.assertIn("not found", result["error"])
    
    def test_create_ci_config(self):
        """测试创建CI配置"""
        self.mock_project.files.get.side_effect = Exception("Not found")
        
        mock_new_file = MagicMock()
        mock_new_file.commit_id = "def456"
        self.mock_project.files.create.return_value = mock_new_file
        
        result = self.skill.create_ci_config(
            stages=["test", "build"],
            jobs={"test": {"stage": "test", "script": ["pytest"]}}
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["action"], "created")
    
    def test_validate_ci_config_valid(self):
        """测试验证有效CI配置"""
        content = """
stages:
  - test
  - build

test:
  stage: test
  script:
    - pytest
"""
        result = self.skill.validate_ci_config(content)
        
        self.assertTrue(result["success"])
        self.assertTrue(result["data"]["valid"])
        self.assertEqual(len(result["data"]["errors"]), 0)
    
    def test_validate_ci_config_invalid_yaml(self):
        """测试验证无效YAML"""
        content = "invalid: yaml: [unclosed"
        result = self.skill.validate_ci_config(content)
        
        self.assertFalse(result["success"])
        self.assertIn("YAML", result["error"])
    
    def test_validate_ci_config_empty(self):
        """测试验证空配置"""
        result = self.skill.validate_ci_config("")
        
        self.assertTrue(result["success"])
        self.assertFalse(result["data"]["valid"])
        self.assertIn("Empty configuration", result["data"]["errors"])
    
    def test_list_runners(self):
        """测试列出Runners"""
        mock_runner = MagicMock()
        mock_runner.id = 1
        mock_runner.description = "test-runner"
        mock_runner.active = True
        mock_runner.online = True
        mock_runner.status = "online"
        mock_runner.tag_list = ["docker"]
        
        self.mock_project.runners.list.return_value = [mock_runner]
        
        result = self.skill.list_runners()
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["description"], "test-runner")
    
    def test_list_pipelines(self):
        """测试列出Pipelines"""
        mock_pipeline = MagicMock()
        mock_pipeline.id = 123
        mock_pipeline.sha = "abc123"
        mock_pipeline.ref = "main"
        mock_pipeline.status = "success"
        mock_pipeline.created_at = "2024-01-01T00:00:00Z"
        mock_pipeline.updated_at = "2024-01-01T00:05:00Z"
        mock_pipeline.web_url = "https://gitlab.com/project/-/pipelines/123"
        
        self.mock_project.pipelines.list.return_value = [mock_pipeline]
        
        result = self.skill.list_pipelines(status="success")
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["status"], "success")
    
    def test_trigger_pipeline(self):
        """测试触发Pipeline"""
        mock_pipeline = MagicMock()
        mock_pipeline.id = 456
        mock_pipeline.sha = "def789"
        mock_pipeline.ref = "main"
        mock_pipeline.status = "pending"
        mock_pipeline.web_url = "https://gitlab.com/project/-/pipelines/456"
        
        self.mock_project.pipelines.create.return_value = mock_pipeline
        
        result = self.skill.trigger_pipeline("main", {"VAR": "value"})
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["id"], 456)
        self.mock_project.pipelines.create.assert_called_once()
    
    def test_list_variables(self):
        """测试列出变量"""
        mock_var = MagicMock()
        mock_var.key = "API_KEY"
        mock_var.protected = True
        mock_var.masked = True
        mock_var.environment_scope = "*"
        
        self.mock_project.variables.list.return_value = [mock_var]
        
        result = self.skill.list_variables()
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["key"], "API_KEY")
    
    def test_set_variable_create(self):
        """测试创建变量"""
        from gitlab.exceptions import GitlabError
        self.mock_project.variables.get.side_effect = GitlabError("Not found")
        
        mock_var = MagicMock()
        mock_var.key = "NEW_VAR"
        self.mock_project.variables.create.return_value = mock_var
        
        result = self.skill.set_variable("NEW_VAR", "value", protected=True)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["action"], "created")
    
    def test_delete_variable(self):
        """测试删除变量"""
        mock_var = MagicMock()
        self.mock_project.variables.get.return_value = mock_var
        
        result = self.skill.delete_variable("OLD_VAR")
        
        self.assertTrue(result["success"])
        mock_var.delete.assert_called_once()
    
    def test_generate_python_template(self):
        """测试生成Python模板"""
        result = self.skill.generate_ci_template("python")
        
        self.assertTrue(result["success"])
        self.assertIn("content", result["data"])
        
        parsed = yaml.safe_load(result["data"]["content"])
        self.assertIn("stages", parsed)
        self.assertIn("test", parsed)
    
    def test_generate_nodejs_template(self):
        """测试生成Node.js模板"""
        result = self.skill.generate_ci_template("nodejs")
        
        self.assertTrue(result["success"])
        parsed = yaml.safe_load(result["data"]["content"])
        self.assertIn("NODE_VERSION", parsed.get("variables", {}))
    
    def test_generate_docker_template(self):
        """测试生成Docker模板"""
        result = self.skill.generate_ci_template("docker")
        
        self.assertTrue(result["success"])
        parsed = yaml.safe_load(result["data"]["content"])
        self.assertIn("build", parsed)
        self.assertIn("push", parsed)


class TestTemplateGeneration(unittest.TestCase):
    """测试模板生成"""
    
    @patch('main.gitlab.Gitlab')
    def setUp(self, mock_gitlab):
        mock_gl = MagicMock()
        mock_gitlab.return_value = mock_gl
        
        self.skill = GitLabCISkill(
            token="test-token",
            project="group/project"
        )
    
    def test_python_template_structure(self):
        """测试Python模板结构"""
        template = self.skill._generate_python_template(["test", "build"])
        parsed = yaml.safe_load(template)
        
        self.assertEqual(parsed["stages"], ["test", "build"])
        self.assertIn("cache", parsed)
        self.assertIn("test", parsed)
        self.assertIn("build", parsed)
    
    def test_java_template_structure(self):
        """测试Java模板结构"""
        template = self.skill._generate_java_template(None)
        parsed = yaml.safe_load(template)
        
        self.assertIn("MAVEN_OPTS", parsed.get("variables", {}))
        self.assertIn("build", parsed)
        self.assertIn("test", parsed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
