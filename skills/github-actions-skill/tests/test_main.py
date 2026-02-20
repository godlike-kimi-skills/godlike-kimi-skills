"""
GitHub Actions Skill 测试套件
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import yaml
from main import GitHubActionsSkill


class TestGitHubActionsSkill(unittest.TestCase):
    """测试GitHubActionsSkill类"""
    
    def setUp(self):
        """测试前准备"""
        self.skill = GitHubActionsSkill(token="test-token", repo="owner/repo")
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.skill.token, "test-token")
        self.assertEqual(self.skill.repo_name, "owner/repo")
    
    def test_init_without_token(self):
        """测试无token初始化"""
        with self.assertRaises(ValueError):
            GitHubActionsSkill()
    
    @patch.dict('os.environ', {'GITHUB_TOKEN': 'env-token', 'GITHUB_REPO': 'env/repo'})
    def test_init_from_env(self):
        """测试从环境变量初始化"""
        skill = GitHubActionsSkill()
        self.assertEqual(skill.token, "env-token")
        self.assertEqual(skill.repo_name, "env/repo")
    
    def test_create_response(self):
        """测试响应创建"""
        response = self.skill._create_response(True, data="test")
        self.assertTrue(response["success"])
        self.assertEqual(response["data"], "test")
        self.assertIsNone(response["error"])
        self.assertIn("timestamp", response)
    
    def test_build_workflow(self):
        """测试工作流构建"""
        triggers = ["push", "pull_request"]
        jobs = [{"name": "build", "runs_on": "ubuntu-latest", "steps": []}]
        
        workflow = self.skill._build_workflow("Test Workflow", triggers, jobs)
        
        self.assertEqual(workflow["name"], "Test Workflow")
        self.assertIn("push", workflow["on"])
        self.assertIn("pull_request", workflow["on"])
        self.assertIn("build", workflow["jobs"])
    
    def test_build_workflow_default(self):
        """测试默认工作流构建"""
        workflow = self.skill._build_workflow("Test", None, None)
        
        self.assertEqual(workflow["name"], "Test")
        self.assertIn("push", workflow["on"])
        self.assertIn("build", workflow["jobs"])
    
    @patch('main.Github')
    def test_create_workflow_no_repo(self, mock_github):
        """测试无仓库创建工作流"""
        skill = GitHubActionsSkill(token="test-token")
        result = skill.create_workflow("test")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Repository not set")
    
    @patch('main.Github')
    def test_create_workflow_success(self, mock_github):
        """测试创建工作流成功"""
        mock_repo = MagicMock()
        mock_repo.get_contents.side_effect = Exception("Not found")
        mock_repo.create_file.return_value = {"commit": Mock(sha="abc123")}
        
        self.skill.repo = mock_repo
        result = self.skill.create_workflow("ci", triggers=["push"])
        
        self.assertTrue(result["success"])
        self.assertIn("commit_sha", result["data"])
    
    @patch('main.Github')
    def test_list_workflows(self, mock_github):
        """测试列出工作流"""
        mock_repo = MagicMock()
        mock_workflow = MagicMock()
        mock_workflow.id = 123
        mock_workflow.name = "CI"
        mock_workflow.path = ".github/workflows/ci.yml"
        mock_workflow.state = "active"
        mock_workflow.created_at = None
        mock_workflow.updated_at = None
        mock_repo.get_workflows.return_value = [mock_workflow]
        
        self.skill.repo = mock_repo
        result = self.skill.list_workflows()
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["name"], "CI")
    
    @patch('main.Github')
    def test_set_secret(self, mock_github):
        """测试设置secret"""
        mock_repo = MagicMock()
        self.skill.repo = mock_repo
        
        result = self.skill.set_secret("API_KEY", "secret-value")
        
        self.assertTrue(result["success"])
        mock_repo.create_secret.assert_called_once_with("API_KEY", "secret-value")
    
    @patch('main.Github')
    def test_list_secrets(self, mock_github):
        """测试列出secrets"""
        mock_repo = MagicMock()
        mock_secret = Mock()
        mock_secret.name = "API_KEY"
        mock_secret.created_at = "2024-01-01"
        mock_repo.get_secrets.return_value = [mock_secret]
        
        self.skill.repo = mock_repo
        result = self.skill.list_secrets()
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 1)
    
    @patch('main.Github')
    def test_get_workflow_runs(self, mock_github):
        """测试获取工作流运行"""
        mock_repo = MagicMock()
        mock_run = MagicMock()
        mock_run.id = 123
        mock_run.name = "CI"
        mock_run.head_branch = "main"
        mock_run.head_sha = "abcdef1234567890"
        mock_run.status = "completed"
        mock_run.conclusion = "success"
        mock_run.created_at = None
        mock_run.run_number = 1
        mock_run.html_url = "https://github.com/run/123"
        
        mock_repo.get_workflow_runs.return_value = [mock_run]
        self.skill.repo = mock_repo
        
        result = self.skill.get_workflow_runs()
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["status"], "completed")
    
    @patch('main.Github')
    def test_cancel_workflow(self, mock_github):
        """测试取消工作流"""
        mock_repo = MagicMock()
        mock_run = MagicMock()
        mock_repo.get_workflow_run.return_value = mock_run
        
        self.skill.repo = mock_repo
        result = self.skill.cancel_workflow(123)
        
        self.assertTrue(result["success"])
        mock_run.cancel.assert_called_once()
    
    def test_generate_ci_template(self):
        """测试生成CI模板"""
        result = self.skill.generate_template("ci", "python")
        
        self.assertTrue(result["success"])
        self.assertIn("template_type", result["data"])
        self.assertIn("content", result["data"])
        
        content = yaml.safe_load(result["data"]["content"])
        self.assertEqual(content["name"], "CI")
    
    def test_generate_cd_template(self):
        """测试生成CD模板"""
        result = self.skill.generate_template("cd")
        
        self.assertTrue(result["success"])
        content = yaml.safe_load(result["data"]["content"])
        self.assertEqual(content["name"], "CD")
    
    def test_generate_templates_for_languages(self):
        """测试不同语言的模板"""
        for lang in ["python", "nodejs", "go"]:
            result = self.skill.generate_template("ci", lang)
            self.assertTrue(result["success"], f"Failed for {lang}")


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_workflow_lifecycle(self):
        """测试完整工作流生命周期"""
        with patch('main.Github') as mock_github:
            skill = GitHubActionsSkill(token="test", repo="owner/repo")
            mock_repo = MagicMock()
            skill.repo = mock_repo
            
            # 创建工作流
            mock_repo.create_file.return_value = {"commit": Mock(sha="abc")}
            result = skill.create_workflow("test-wf", triggers=["push"])
            self.assertTrue(result["success"])
            
            # 列出工作流
            mock_workflow = MagicMock()
            mock_workflow.id = 1
            mock_workflow.name = "Test"
            mock_workflow.path = ".github/workflows/test-wf.yml"
            mock_workflow.state = "active"
            mock_workflow.created_at = None
            mock_workflow.updated_at = None
            mock_repo.get_workflows.return_value = [mock_workflow]
            
            result = skill.list_workflows()
            self.assertTrue(result["success"])
            self.assertEqual(len(result["data"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
