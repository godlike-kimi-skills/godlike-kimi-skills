"""
Hugging Face Skill - 测试模块
"""

import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock

# 导入被测试模块
import sys
sys.path.insert(0, os.path.dirname(__file__))
from main import HuggingFaceSkill, create_skill, quick_infer


class TestHuggingFaceSkill(unittest.TestCase):
    """HuggingFaceSkill测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "cache_dir": self.temp_dir,
            "device": "cpu",
            "default_model": "bert-base-uncased"
        }
        # 保存测试配置
        import json
        self.config_path = os.path.join(self.temp_dir, "test_config.json")
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """测试初始化"""
        skill = HuggingFaceSkill(self.config_path)
        self.assertEqual(skill.cache_dir, self.temp_dir)
        self.assertEqual(skill.device, "cpu")
        self.assertTrue(os.path.exists(self.temp_dir))
    
    def test_default_initialization(self):
        """测试默认初始化"""
        skill = HuggingFaceSkill()
        self.assertIsNotNone(skill.cache_dir)
        self.assertIsNotNone(skill.device)
    
    def test_load_config(self):
        """测试配置加载"""
        skill = HuggingFaceSkill(self.config_path)
        self.assertEqual(skill.config["cache_dir"], self.temp_dir)
        self.assertEqual(skill.config["device"], "cpu")
    
    @patch('main.logger')
    def test_logging(self, mock_logger):
        """测试日志功能"""
        skill = HuggingFaceSkill(self.config_path)
        self.assertIsNotNone(skill)
    
    def test_list_cached_models_empty(self):
        """测试空缓存列表"""
        skill = HuggingFaceSkill(self.config_path)
        models = skill.list_cached_models()
        self.assertIsInstance(models, list)
        self.assertEqual(len(models), 0)
    
    def test_encode_text_mock(self):
        """测试文本编码（模拟）"""
        skill = HuggingFaceSkill(self.config_path)
        
        with patch('transformers.AutoTokenizer') as mock_tokenizer:
            mock_instance = MagicMock()
            mock_instance.return_value = {"input_ids": [[1, 2, 3]]}
            mock_tokenizer.from_pretrained.return_value = mock_instance
            
            # 模拟编码
            result = skill.encode_text("test-model", "Hello")
            self.assertIsNotNone(result)
    
    def test_decode_tokens_mock(self):
        """测试Token解码（模拟）"""
        skill = HuggingFaceSkill(self.config_path)
        
        with patch('transformers.AutoTokenizer') as mock_tokenizer:
            mock_instance = MagicMock()
            mock_instance.batch_decode.return_value = ["Hello World"]
            mock_tokenizer.from_pretrained.return_value = mock_instance
            
            result = skill.decode_tokens("test-model", [[1, 2, 3]])
            self.assertEqual(result, "Hello World")
    
    @patch('huggingface_hub.snapshot_download')
    def test_download_model_mock(self, mock_download):
        """测试模型下载（模拟）"""
        mock_download.return_value = "/fake/path"
        
        skill = HuggingFaceSkill(self.config_path)
        result = skill.download_model("bert-base-uncased")
        
        mock_download.assert_called_once()
        self.assertEqual(result, "/fake/path")
    
    def test_get_device_cpu(self):
        """测试CPU设备检测"""
        config = {"device": "cpu"}
        skill = HuggingFaceSkill(self.config_path)
        skill.config = config
        device = skill._get_device()
        self.assertEqual(device, "cpu")
    
    def test_create_skill(self):
        """测试创建skill实例"""
        skill = create_skill(self.config_path)
        self.assertIsInstance(skill, HuggingFaceSkill)
    
    def test_clear_cache(self):
        """测试清理缓存"""
        skill = HuggingFaceSkill(self.config_path)
        
        # 创建一些测试文件
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        skill.clear_cache()
        self.assertFalse(os.path.exists(test_file))
        self.assertTrue(os.path.exists(self.temp_dir))


class TestIntegration(unittest.TestCase):
    """集成测试（需要网络连接）"""
    
    @unittest.skip("需要网络连接")
    def test_real_model_download(self):
        """测试真实模型下载"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"cache_dir": temp_dir, "device": "cpu"}
            import json
            config_path = os.path.join(temp_dir, "config.json")
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            skill = HuggingFaceSkill(config_path)
            # 下载一个小模型进行测试
            result = skill.download_model("distilbert-base-uncased-finetuned-sst-2-english")
            self.assertTrue(os.path.exists(result))


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestHuggingFaceSkill))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
