"""
OpenAI API Skill - 测试模块
"""

import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open

# 导入被测试模块
import sys
sys.path.insert(0, os.path.dirname(__file__))

# 检查openai是否可用
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from main import OpenAISkill, create_skill, quick_chat


class TestOpenAISkill(unittest.TestCase):
    """OpenAISkill测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "api_key": "test-api-key",
            "base_url": "https://api.openai.com/v1",
            "default_model": "gpt-3.5-turbo",
            "default_temperature": 0.7,
            "default_max_tokens": 2048,
            "embedding_model": "text-embedding-ada-002"
        }
        import json
        self.config_path = os.path.join(self.temp_dir, "config.json")
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "env-api-key"})
    def test_initialization_with_env(self):
        """测试使用环境变量初始化"""
        with patch('main.OPENAI_AVAILABLE', True):
            with patch('main.OpenAI'):
                skill = OpenAISkill()
                self.assertEqual(skill.api_key, "env-api-key")
    
    def test_initialization_with_config(self):
        """测试使用配置文件初始化"""
        with patch('main.OPENAI_AVAILABLE', True):
            with patch('main.OpenAI'):
                skill = OpenAISkill(self.config_path)
                self.assertEqual(skill.api_key, "test-api-key")
                self.assertEqual(skill.default_model, "gpt-3.5-turbo")
    
    def test_initialization_with_api_key(self):
        """测试直接传入API密钥"""
        with patch('main.OPENAI_AVAILABLE', True):
            with patch('main.OpenAI'):
                skill = OpenAISkill(api_key="direct-api-key")
                self.assertEqual(skill.api_key, "direct-api-key")
    
    def test_load_config(self):
        """测试配置加载"""
        with patch('main.OPENAI_AVAILABLE', True):
            with patch('main.OpenAI'):
                skill = OpenAISkill(self.config_path)
                self.assertEqual(skill.config["default_temperature"], 0.7)
                self.assertEqual(skill.config["default_max_tokens"], 2048)
    
    @patch('main.OpenAI')
    def test_chat_mock(self, mock_openai_class):
        """测试对话接口（模拟）"""
        # 设置模拟对象
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello!"
        mock_response.choices[0].message.role = "assistant"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        mock_response.model = "gpt-3.5-turbo"
        mock_response.id = "test-id"
        
        mock_client.chat.completions.create.return_value = mock_response
        
        skill = OpenAISkill(self.config_path)
        skill.client = mock_client
        
        messages = [{"role": "user", "content": "Hi"}]
        result = skill.chat(messages)
        
        self.assertEqual(result["content"], "Hello!")
        self.assertEqual(result["role"], "assistant")
        self.assertEqual(result["usage"]["total_tokens"], 15)
    
    @patch('main.OpenAI')
    def test_simple_chat_mock(self, mock_openai_class):
        """测试简单对话接口（模拟）"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Simple response"
        mock_response.choices[0].message.role = "assistant"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.prompt_tokens = 5
        mock_response.usage.completion_tokens = 3
        mock_response.usage.total_tokens = 8
        mock_response.model = "gpt-3.5-turbo"
        mock_response.id = "test-id"
        
        mock_client.chat.completions.create.return_value = mock_response
        
        skill = OpenAISkill(self.config_path)
        skill.client = mock_client
        
        result = skill.simple_chat("Hello")
        
        self.assertEqual(result, "Simple response")
    
    @patch('main.OpenAI')
    def test_create_embedding_mock(self, mock_openai_class):
        """测试嵌入生成（模拟）"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.data = [MagicMock()]
        mock_response.data[0].embedding = [0.1, 0.2, 0.3]
        mock_response.model = "text-embedding-ada-002"
        mock_response.usage.prompt_tokens = 3
        mock_response.usage.total_tokens = 3
        
        mock_client.embeddings.create.return_value = mock_response
        
        skill = OpenAISkill(self.config_path)
        skill.client = mock_client
        
        result = skill.create_embedding("Hello")
        
        self.assertEqual(result["embeddings"], [0.1, 0.2, 0.3])
        self.assertEqual(result["model"], "text-embedding-ada-002")
    
    @patch('main.OpenAI')
    def test_generate_image_mock(self, mock_openai_class):
        """测试图像生成（模拟）"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.data = [MagicMock()]
        mock_response.data[0].url = "https://example.com/image.png"
        mock_response.data[0].revised_prompt = "Revised prompt"
        mock_response.created = 1234567890
        
        mock_client.images.generate.return_value = mock_response
        
        skill = OpenAISkill(self.config_path)
        skill.client = mock_client
        
        result = skill.generate_image("A cat")
        
        self.assertEqual(result["images"]["url"], "https://example.com/image.png")
        self.assertEqual(result["created"], 1234567890)
    
    @patch('main.OpenAI')
    def test_transcribe_audio_mock(self, mock_openai_class):
        """测试语音转文字（模拟）"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.text = "Hello world"
        
        mock_client.audio.transcriptions.create.return_value = mock_response
        
        skill = OpenAISkill(self.config_path)
        skill.client = mock_client
        
        # 使用模拟文件
        mock_file = MagicMock()
        with patch('builtins.open', mock_open(read_data=b'audio data')) as mock_file_open:
            result = skill.transcribe_audio("test.mp3")
        
        self.assertEqual(result["text"], "Hello world")
    
    def test_count_tokens(self):
        """测试token计数"""
        with patch('main.OPENAI_AVAILABLE', True):
            with patch('main.OpenAI'):
                skill = OpenAISkill(self.config_path)
                
                # 简单估算测试
                text = "Hello world"
                count = skill.count_tokens(text)
                self.assertGreater(count, 0)
    
    def test_estimate_cost(self):
        """测试成本估算"""
        with patch('main.OPENAI_AVAILABLE', True):
            with patch('main.OpenAI'):
                skill = OpenAISkill(self.config_path)
                
                cost = skill.estimate_cost(1000, 500, "gpt-3.5-turbo")
                self.assertGreater(cost, 0)
    
    def test_create_skill(self):
        """测试创建skill"""
        with patch('main.OPENAI_AVAILABLE', True):
            with patch('main.OpenAI'):
                skill = create_skill(self.config_path)
                self.assertIsInstance(skill, OpenAISkill)
    
    def test_no_api_key_warning(self):
        """测试无API密钥警告"""
        with patch('main.OPENAI_AVAILABLE', True):
            with patch('main.OpenAI'):
                # 清除环境变量
                with patch.dict(os.environ, {}, clear=True):
                    with self.assertLogs(level='WARNING') as log_context:
                        skill = OpenAISkill()
                        self.assertIn("API key not found", str(log_context.output))


class TestIntegration(unittest.TestCase):
    """集成测试（需要真实API密钥）"""
    
    @unittest.skip("需要真实API密钥")
    def test_real_chat(self):
        """测试真实对话API"""
        skill = OpenAISkill()
        messages = [{"role": "user", "content": "Say 'Hello' and nothing else"}]
        result = skill.chat(messages, max_tokens=10)
        
        self.assertIn("content", result)
        self.assertIn("usage", result)
        self.assertIn("Hello", result["content"])
    
    @unittest.skip("需要真实API密钥")
    def test_real_embedding(self):
        """测试真实嵌入API"""
        skill = OpenAISkill()
        result = skill.create_embedding("Hello world")
        
        self.assertIn("embeddings", result)
        self.assertIsInstance(result["embeddings"], list)
        self.assertGreater(len(result["embeddings"]), 0)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestOpenAISkill))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
