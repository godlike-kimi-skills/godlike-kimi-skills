"""
ArgoCD Skill 测试套件
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import yaml
from main import ArgoCDSkill


class TestArgoCDSkill(unittest.TestCase):
    """测试ArgoCDSkill类"""
    
    @patch('main.requests.Session')
    def setUp(self, mock_session_class):
        """测试前准备"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"token": "test-auth-token"}
        mock_response.content = b'{"token": "test-auth-token"}'
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        mock_session.request.return_value = mock_response
        
        self.skill = ArgoCDSkill(
            server="https://argocd.example.com",
            username="admin",
            password="password",
            insecure=True
        )
        self.mock_session = mock_session
    
    def test_init_with_credentials(self):
        """测试使用用户名密码初始化"""
        self.assertEqual(self.skill.server, "https://argocd.example.com")
        self.assertEqual(self.skill.username, "admin")
        self.assertEqual(self.skill.password, "password")
        self.assertEqual(self.skill.token, "test-auth-token")
    
    def test_init_missing_server(self):
        """测试无服务器地址初始化"""
        with self.assertRaises(ValueError):
            ArgoCDSkill(username="admin", password="password")
    
    @patch.dict('os.environ', {
        'ARGOCD_SERVER': 'https://env.argocd.com',
        'ARGOCD_TOKEN': 'env-token'
    })
    @patch('main.requests.Session')
    def test_init_from_env(self, mock_session_class):
        """测试从环境变量初始化"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.request.return_value = MagicMock(json=lambda: {}, content=b'{}')
        
        skill = ArgoCDSkill()
        self.assertEqual(skill.server, "https://env.argocd.com")
        self.assertEqual(skill.token, "env-token")
    
    def test_create_response(self):
        """测试响应创建"""
        response = self.skill._create_response(True, data="test")
        self.assertTrue(response["success"])
        self.assertEqual(response["data"], "test")
        self.assertIsNone(response["error"])
        self.assertIn("timestamp", response)
    
    def test_get_server_info(self):
        """测试获取服务器信息"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "dexEnabled": True,
            "disablePassword": False,
            "help": {"chatText": "Chat"}
        }
        mock_response.content = json.dumps(mock_response.json.return_value).encode()
        mock_response.raise_for_status.return_value = None
        self.mock_session.request.return_value = mock_response
        
        result = self.skill.get_server_info()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["url"], "https://argocd.example.com")
        self.assertTrue(result["data"]["dexEnabled"])
    
    def test_create_app(self):
        """测试创建Application"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "metadata": {"name": "test-app"},
            "status": {"sync": {"status": "OutOfSync"}}
        }
        mock_response.content = json.dumps(mock_response.json.return_value).encode()
        mock_response.raise_for_status.return_value = None
        self.mock_session.request.return_value = mock_response
        
        result = self.skill.create_app(
            name="test-app",
            repo_url="https://github.com/org/repo.git",
            path="manifests"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["name"], "test-app")
    
    def test_delete_app(self):
        """测试删除Application"""
        mock_response = MagicMock()
        mock_response.content = b'{}'
        mock_response.raise_for_status.return_value = None
        self.mock_session.request.return_value = mock_response
        
        result = self.skill.delete_app("test-app")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["deleted"], "test-app")
    
    def test_get_app(self):
        """测试获取Application"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "metadata": {"name": "test-app", "namespace": "argocd"},
            "spec": {
                "project": "default",
                "source": {"repoURL": "https://github.com/org/repo.git", "path": "manifests"},
                "destination": {"server": "https://kubernetes.default.svc", "namespace": "default"}
            },
            "status": {
                "sync": {"status": "Synced"},
                "health": {"status": "Healthy"}
            }
        }
        mock_response.content = json.dumps(mock_response.json.return_value).encode()
        mock_response.raise_for_status.return_value = None
        self.mock_session.request.return_value = mock_response
        
        result = self.skill.get_app("test-app")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["name"], "test-app")
        self.assertEqual(result["data"]["syncStatus"], "Synced")
        self.assertEqual(result["data"]["healthStatus"], "Healthy")
    
    def test_list_apps(self):
        """测试列出Applications"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "metadata": {"name": "app1"},
                    "spec": {
                        "project": "default",
                        "source": {"repoURL": "https://github.com/org/repo1.git", "path": "app1"}
                    },
                    "status": {
                        "sync": {"status": "Synced"},
                        "health": {"status": "Healthy"}
                    }
                }
            ]
        }
        mock_response.content = json.dumps(mock_response.json.return_value).encode()
        mock_response.raise_for_status.return_value = None
        self.mock_session.request.return_value = mock_response
        
        result = self.skill.list_apps()
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["name"], "app1")
    
    def test_sync_app(self):
        """测试同步Application"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"synced": True}
        mock_response.content = json.dumps(mock_response.json.return_value).encode()
        mock_response.raise_for_status.return_value = None
        self.mock_session.request.return_value = mock_response
        
        result = self.skill.sync_app("test-app", prune=True, force=True)
        
        self.assertTrue(result["success"])
        self.assertTrue(result["data"]["synced"])
    
    def test_rollback_app(self):
        """测试回滚Application"""
        mock_response = MagicMock()
        mock_response.content = b'{}'
        mock_response.raise_for_status.return_value = None
        self.mock_session.request.return_value = mock_response
        
        result = self.skill.rollback_app("test-app", 5)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["history_id"], 5)
    
    def test_get_app_resources(self):
        """测试获取资源树"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "nodes": [
                {
                    "group": "apps",
                    "kind": "Deployment",
                    "namespace": "default",
                    "name": "my-app",
                    "status": "Synced",
                    "health": {"status": "Healthy"}
                }
            ]
        }
        mock_response.content = json.dumps(mock_response.json.return_value).encode()
        mock_response.raise_for_status.return_value = None
        self.mock_session.request.return_value = mock_response
        
        result = self.skill.get_app_resources("test-app")
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["kind"], "Deployment")
    
    def test_get_app_history(self):
        """测试获取同步历史"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": {
                "history": [
                    {"id": 1, "revision": "abc123", "deployedAt": "2024-01-01T00:00:00Z"},
                    {"id": 2, "revision": "def456", "deployedAt": "2024-01-02T00:00:00Z"}
                ]
            }
        }
        mock_response.content = json.dumps(mock_response.json.return_value).encode()
        mock_response.raise_for_status.return_value = None
        self.mock_session.request.return_value = mock_response
        
        result = self.skill.get_app_history("test-app", limit=2)
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 2)
    
    def test_add_repo(self):
        """测试添加仓库"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "repo": "https://github.com/org/repo.git",
            "connectionState": {"status": "Successful"}
        }
        mock_response.content = json.dumps(mock_response.json.return_value).encode()
        mock_response.raise_for_status.return_value = None
        self.mock_session.request.return_value = mock_response
        
        result = self.skill.add_repo(
            "https://github.com/org/repo.git",
            username="user",
            password="token"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["repo"], "https://github.com/org/repo.git")
    
    def test_list_repos(self):
        """测试列出仓库"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "repo": "https://github.com/org/repo1.git",
                    "connectionState": {"status": "Successful"},
                    "type": "git"
                }
            ]
        }
        mock_response.content = json.dumps(mock_response.json.return_value).encode()
        mock_response.raise_for_status.return_value = None
        self.mock_session.request.return_value = mock_response
        
        result = self.skill.list_repos()
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 1)
    
    def test_list_projects(self):
        """测试列出项目"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "metadata": {"name": "default"},
                    "spec": {
                        "description": "Default project",
                        "sourceRepos": ["*"],
                        "destinations": [{"server": "*", "namespace": "*"}]
                    }
                }
            ]
        }
        mock_response.content = json.dumps(mock_response.json.return_value).encode()
        mock_response.raise_for_status.return_value = None
        self.mock_session.request.return_value = mock_response
        
        result = self.skill.list_projects()
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["name"], "default")


class TestTemplateGeneration(unittest.TestCase):
    """测试模板生成"""
    
    @patch('main.requests.Session')
    def setUp(self, mock_session_class):
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.request.return_value = MagicMock(json=lambda: {}, content=b'{}')
        
        self.skill = ArgoCDSkill(
            server="https://argocd.example.com",
            token="test-token"
        )
    
    def test_generate_git_template(self):
        """测试生成Git模板"""
        template = self.skill._generate_git_template(
            name="my-app",
            repo_url="https://github.com/org/repo.git",
            path="manifests"
        )
        
        parsed = yaml.safe_load(template)
        self.assertEqual(parsed["metadata"]["name"], "my-app")
        self.assertEqual(parsed["spec"]["source"]["path"], "manifests")
        self.assertIn("syncPolicy", parsed["spec"])
    
    def test_generate_helm_template(self):
        """测试生成Helm模板"""
        template = self.skill._generate_helm_template(
            name="my-helm-app",
            repo_url="https://charts.helm.sh/stable",
            chart="nginx"
        )
        
        parsed = yaml.safe_load(template)
        self.assertEqual(parsed["metadata"]["name"], "my-helm-app")
        self.assertEqual(parsed["spec"]["source"]["chart"], "nginx")
    
    def test_generate_kustomize_template(self):
        """测试生成Kustomize模板"""
        template = self.skill._generate_kustomize_template(
            name="my-kustomize-app",
            path="overlays/production",
            name_prefix="prod-"
        )
        
        parsed = yaml.safe_load(template)
        self.assertEqual(parsed["metadata"]["name"], "my-kustomize-app")
        self.assertEqual(parsed["spec"]["source"]["kustomize"]["namePrefix"], "prod-")


if __name__ == "__main__":
    unittest.main(verbosity=2)
