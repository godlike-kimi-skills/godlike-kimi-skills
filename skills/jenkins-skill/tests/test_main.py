"""
Jenkins Skill 测试套件
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from main import JenkinsSkill, BuildStatus


class TestJenkinsSkill(unittest.TestCase):
    """测试JenkinsSkill类"""
    
    @patch('main.jenkins.Jenkins')
    def setUp(self, mock_jenkins):
        """测试前准备"""
        mock_server = MagicMock()
        mock_jenkins.return_value = mock_server
        mock_server.get_whoami.return_value = {"fullName": "Test User"}
        
        self.skill = JenkinsSkill(
            url="http://jenkins.test.com",
            username="admin",
            token="test-token"
        )
        self.mock_server = mock_server
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.skill.url, "http://jenkins.test.com")
        self.assertEqual(self.skill.username, "admin")
        self.assertEqual(self.skill.token, "test-token")
    
    def test_init_missing_params(self):
        """测试缺少参数初始化"""
        with self.assertRaises(ValueError):
            JenkinsSkill()
    
    @patch.dict('os.environ', {
        'JENKINS_URL': 'http://env.jenkins.com',
        'JENKINS_USER': 'envuser',
        'JENKINS_TOKEN': 'envtoken'
    })
    @patch('main.jenkins.Jenkins')
    def test_init_from_env(self, mock_jenkins):
        """测试从环境变量初始化"""
        mock_server = MagicMock()
        mock_jenkins.return_value = mock_server
        mock_server.get_whoami.return_value = {"fullName": "Test"}
        
        skill = JenkinsSkill()
        self.assertEqual(skill.url, "http://env.jenkins.com")
        self.assertEqual(skill.username, "envuser")
    
    def test_create_response(self):
        """测试响应创建"""
        response = self.skill._create_response(True, data="test")
        self.assertTrue(response["success"])
        self.assertEqual(response["data"], "test")
        self.assertIsNone(response["error"])
        self.assertIn("timestamp", response)
    
    def test_get_version(self):
        """测试获取版本"""
        self.mock_server.get_version.return_value = "2.401.1"
        result = self.skill.get_version()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["version"], "2.401.1")
    
    def test_create_job(self):
        """测试创建Job"""
        self.mock_server.create_job.return_value = None
        result = self.skill.create_job("test-job", "pipeline")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["name"], "test-job")
        self.mock_server.create_job.assert_called_once()
    
    def test_create_job_exists(self):
        """测试创建已存在的Job"""
        import jenkins
        self.mock_server.create_job.side_effect = jenkins.JenkinsException("Job already exists")
        result = self.skill.create_job("existing-job")
        
        self.assertFalse(result["success"])
        self.assertIn("already exists", result["error"])
    
    def test_delete_job(self):
        """测试删除Job"""
        self.mock_server.delete_job.return_value = None
        result = self.skill.delete_job("test-job")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["deleted"], "test-job")
    
    def test_get_job_info(self):
        """测试获取Job信息"""
        self.mock_server.get_job_info.return_value = {
            "name": "test-job",
            "url": "http://jenkins/job/test-job",
            "buildable": True,
            "inQueue": False,
            "lastBuild": {"number": 42}
        }
        result = self.skill.get_job_info("test-job")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["name"], "test-job")
        self.assertTrue(result["data"]["buildable"])
    
    def test_list_jobs(self):
        """测试列出Jobs"""
        self.mock_server.get_jobs.return_value = [
            {"name": "job1", "url": "http://jenkins/job1", "color": "blue"},
            {"name": "job2", "url": "http://jenkins/job2", "color": "red"}
        ]
        result = self.skill.list_jobs()
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["name"], "job1")
    
    def test_trigger_build(self):
        """测试触发Build"""
        self.mock_server.build_job.return_value = 12345
        result = self.skill.trigger_build("test-job")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["queue_item"], 12345)
    
    def test_trigger_build_with_params(self):
        """测试带参数触发Build"""
        self.mock_server.build_job.return_value = 12345
        params = {"BRANCH": "main", "ENV": "prod"}
        result = self.skill.trigger_build("test-job", parameters=params)
        
        self.assertTrue(result["success"])
        self.mock_server.build_job.assert_called_with("test-job", params)
    
    def test_get_build_info(self):
        """测试获取Build信息"""
        self.mock_server.get_build_info.return_value = {
            "number": 42,
            "result": "SUCCESS",
            "building": False,
            "timestamp": 1234567890,
            "duration": 120000
        }
        result = self.skill.get_build_info("test-job", 42)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["number"], 42)
        self.assertEqual(result["data"]["result"], "SUCCESS")
    
    def test_get_build_logs(self):
        """测试获取Build日志"""
        self.mock_server.get_build_console_output.return_value = "Build started...\nBuild complete"
        result = self.skill.get_build_logs("test-job", 42)
        
        self.assertTrue(result["success"])
        self.assertIn("Build started", result["data"]["logs"])
    
    def test_stop_build(self):
        """测试停止Build"""
        self.mock_server.stop_build.return_value = None
        result = self.skill.stop_build("test-job", 42)
        
        self.assertTrue(result["success"])
        self.assertTrue(result["data"]["stopped"])
    
    def test_list_builds(self):
        """测试列出Builds"""
        self.mock_server.get_job_info.return_value = {
            "builds": [{"number": 3}, {"number": 2}, {"number": 1}]
        }
        self.mock_server.get_build_info.side_effect = [
            {"number": 3, "result": "SUCCESS", "timestamp": 1000, "duration": 60000, "building": False},
            {"number": 2, "result": "FAILURE", "timestamp": 900, "duration": 50000, "building": False}
        ]
        result = self.skill.list_builds("test-job", limit=2)
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 2)
    
    def test_list_nodes(self):
        """测试列出节点"""
        self.mock_server.get_nodes.return_value = [
            {"name": "master"},
            {"name": "agent-1"}
        ]
        self.mock_server.get_node_info.return_value = {
            "offline": False,
            "numExecutors": 2,
            "executors": [{"idle": True}, {"idle": False}],
            "assignedLabels": [{"name": "linux"}, {"name": "docker"}]
        }
        result = self.skill.list_nodes()
        
        self.assertTrue(result["success"])
        self.assertGreaterEqual(len(result["data"]), 1)
    
    def test_get_queue(self):
        """测试获取队列"""
        self.mock_server.get_queue_info.return_value = [
            {"id": 1, "inQueueSince": 1234567890, "why": "Waiting for executor", "task": {"name": "test-job"}}
        ]
        result = self.skill.get_queue()
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 1)
    
    def test_generate_pipeline_template(self):
        """测试生成Pipeline模板"""
        result = self.skill.generate_pipeline_template("ci", "python")
        
        self.assertTrue(result["success"])
        self.assertIn("script", result["data"])
        self.assertIn("pipeline", result["data"]["script"])
    
    def test_generate_templates_for_languages(self):
        """测试不同语言的模板"""
        for lang in ["python", "nodejs", "java"]:
            result = self.skill.generate_pipeline_template("ci", lang)
            self.assertTrue(result["success"], f"Failed for {lang}")


class TestJobXMLGeneration(unittest.TestCase):
    """测试Job XML生成"""
    
    @patch('main.jenkins.Jenkins')
    def setUp(self, mock_jenkins):
        mock_server = MagicMock()
        mock_jenkins.return_value = mock_server
        mock_server.get_whoami.return_value = {"fullName": "Test"}
        
        self.skill = JenkinsSkill(
            url="http://jenkins.test.com",
            username="admin",
            token="test-token"
        )
    
    def test_generate_pipeline_xml(self):
        """测试生成Pipeline XML"""
        xml = self.skill._generate_job_xml("pipeline", {
            "description": "Test pipeline",
            "script": "pipeline { agent any }"
        })
        
        self.assertIn("flow-definition", xml)
        self.assertIn("Test pipeline", xml)
        self.assertIn("pipeline { agent any }", xml)
    
    def test_generate_freestyle_xml(self):
        """测试生成Freestyle XML"""
        xml = self.skill._generate_job_xml("freestyle", {
            "description": "Test freestyle job"
        })
        
        self.assertIn("<project>", xml)
        self.assertIn("Test freestyle job", xml)


if __name__ == "__main__":
    unittest.main(verbosity=2)
