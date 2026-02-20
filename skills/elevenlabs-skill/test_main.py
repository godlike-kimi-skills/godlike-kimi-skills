#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ElevenLabs Skill 测试文件
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import ElevenLabsManager, VoiceInfo, TTSResult


class TestElevenLabsManager(unittest.TestCase):
    """ElevenLabs管理器测试类"""
    
    @patch.dict(os.environ, {'ELEVENLABS_API_KEY': 'test_api_key'})
    @patch('main.ElevenLabs')
    def setUp(self, mock_elevenlabs_class):
        """测试前准备"""
        self.mock_elevenlabs_class = mock_elevenlabs_class
        self.mock_client = Mock()
        mock_elevenlabs_class.return_value = self.mock_client
        self.manager = ElevenLabsManager(api_key="test_api_key")
    
    def test_init_without_api_key(self):
        """测试没有API密钥时的初始化"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                ElevenLabsManager()
            self.assertIn("API密钥", str(context.exception))
    
    @patch('main.ElevenLabs')
    def test_get_voices(self, mock_elevenlabs_class):
        """测试获取声音列表"""
        mock_client = Mock()
        mock_elevenlabs_class.return_value = mock_client
        
        # 设置mock声音
        mock_voice = Mock()
        mock_voice.voice_id = "voice123"
        mock_voice.name = "Test Voice"
        mock_voice.category = "premade"
        mock_voice.description = "A test voice"
        mock_voice.labels = {"accent": "american"}
        mock_voice.preview_url = "http://preview.url"
        
        mock_response = Mock()
        mock_response.voices = [mock_voice]
        mock_client.voices.get_all.return_value = mock_response
        
        manager = ElevenLabsManager(api_key="test")
        voices = manager.get_voices()
        
        self.assertEqual(len(voices), 1)
        self.assertEqual(voices[0].voice_id, "voice123")
        self.assertEqual(voices[0].name, "Test Voice")
    
    @patch('main.ElevenLabs')
    @patch('main.VoiceSettings')
    def test_text_to_speech(self, mock_voice_settings_class, mock_elevenlabs_class):
        """测试文本转语音"""
        mock_client = Mock()
        mock_elevenlabs_class.return_value = mock_client
        
        # 设置mock音频数据
        mock_client.text_to_speech.convert.return_value = [b"audio", b"data"]
        
        # 设置mock声音列表
        mock_voice = Mock()
        mock_voice.voice_id = "Rachel"
        mock_voice.name = "Rachel"
        mock_voice.category = "premade"
        
        mock_response = Mock()
        mock_response.voices = [mock_voice]
        mock_client.voices.get_all.return_value = mock_response
        
        manager = ElevenLabsManager(api_key="test")
        result = manager.text_to_speech(
            text="Hello world",
            voice_id="Rachel",
            save=False
        )
        
        self.assertEqual(result.text, "Hello world")
        self.assertEqual(result.voice_id, "Rachel")
        self.assertEqual(result.audio_data, b"audiodata")
    
    def test_split_long_text(self):
        """测试长文本分割"""
        # 短文本不应分割
        short_text = "Hello world."
        chunks = self.manager.split_long_text(short_text, max_length=100)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], short_text)
        
        # 长文本应分割
        long_text = "Hello world. " * 1000  # 很长的文本
        chunks = self.manager.split_long_text(long_text, max_length=100)
        self.assertGreater(len(chunks), 1)
    
    def test_split_long_text_sentence_boundary(self):
        """测试按句子边界分割"""
        text = "First sentence. Second sentence. Third sentence."
        chunks = self.manager.split_long_text(text, max_length=50)
        
        # 应该保持句子完整性
        for chunk in chunks:
            self.assertTrue(chunk.strip().endswith("."))
    
    @patch('main.ElevenLabs')
    def test_clone_voice(self, mock_elevenlabs_class):
        """测试声音克隆"""
        mock_client = Mock()
        mock_elevenlabs_class.return_value = mock_client
        
        mock_voice = Mock()
        mock_voice.voice_id = "cloned_voice_123"
        mock_client.voices.add.return_value = mock_voice
        
        manager = ElevenLabsManager(api_key="test")
        
        # 使用BytesIO模拟文件
        fake_file = BytesIO(b"fake audio data")
        voice_id = manager.clone_voice(
            name="My Voice",
            description="A cloned voice",
            audio_files=[fake_file]
        )
        
        self.assertEqual(voice_id, "cloned_voice_123")
        mock_client.voices.add.assert_called_once()
    
    @patch('main.ElevenLabs')
    def test_delete_voice(self, mock_elevenlabs_class):
        """测试删除声音"""
        mock_client = Mock()
        mock_elevenlabs_class.return_value = mock_client
        
        manager = ElevenLabsManager(api_key="test")
        result = manager.delete_voice("voice123")
        
        self.assertTrue(result)
        mock_client.voices.delete.assert_called_with(voice_id="voice123")
    
    @patch('main.ElevenLabs')
    def test_delete_voice_failure(self, mock_elevenlabs_class):
        """测试删除声音失败"""
        mock_client = Mock()
        mock_client.voices.delete.side_effect = Exception("API Error")
        mock_elevenlabs_class.return_value = mock_client
        
        manager = ElevenLabsManager(api_key="test")
        result = manager.delete_voice("voice123")
        
        self.assertFalse(result)
    
    @patch('main.ElevenLabs')
    def test_get_user_info(self, mock_elevenlabs_class):
        """测试获取用户信息"""
        mock_client = Mock()
        mock_elevenlabs_class.return_value = mock_client
        
        # 设置mock用户
        mock_user = Mock()
        mock_user.user_id = "user123"
        mock_client.user.get.return_value = mock_user
        
        # 设置mock订阅
        mock_sub = Mock()
        mock_sub.tier = "starter"
        mock_sub.character_count = 5000
        mock_sub.character_limit = 10000
        mock_sub.voice_slots = 10
        mock_sub.voice_slots_used = 3
        mock_sub.professional_voice_slots = 5
        mock_sub.professional_voice_slots_used = 1
        mock_client.user.get_subscription.return_value = mock_sub
        
        manager = ElevenLabsManager(api_key="test")
        info = manager.get_user_info()
        
        self.assertEqual(info["subscription_tier"], "starter")
        self.assertEqual(info["character_count"], 5000)
        self.assertEqual(info["character_limit"], 10000)
        self.assertEqual(info["character_usage_percentage"], 50.0)
    
    @patch('main.ElevenLabs')
    def test_get_models(self, mock_elevenlabs_class):
        """测试获取模型列表"""
        mock_client = Mock()
        mock_elevenlabs_class.return_value = mock_client
        
        # 设置mock模型
        mock_model = Mock()
        mock_model.model_id = "eleven_multilingual_v2"
        mock_model.name = "Eleven Multilingual v2"
        mock_model.description = "Latest multilingual model"
        mock_model.can_do_text_to_speech = True
        mock_model.can_do_voice_conversion = True
        mock_model.token_cost_factor = 1.0
        
        mock_client.models.get_all.return_value = [mock_model]
        
        manager = ElevenLabsManager(api_key="test")
        models = manager.get_models()
        
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0]["model_id"], "eleven_multilingual_v2")
        self.assertTrue(models[0]["can_do_text_to_speech"])


class TestVoiceInfo(unittest.TestCase):
    """声音信息测试类"""
    
    def test_voice_info_defaults(self):
        """测试默认值"""
        voice = VoiceInfo(voice_id="v1", name="Test")
        
        self.assertEqual(voice.voice_id, "v1")
        self.assertEqual(voice.name, "Test")
        self.assertEqual(voice.category, "premade")
        self.assertEqual(voice.description, "")
        self.assertEqual(voice.labels, {})
    
    def test_voice_info_with_data(self):
        """测试带数据的初始化"""
        voice = VoiceInfo(
            voice_id="v2",
            name="Custom Voice",
            category="cloned",
            description="A custom voice",
            labels={"gender": "female", "age": "young"},
            preview_url="http://example.com/preview.mp3"
        )
        
        self.assertEqual(voice.category, "cloned")
        self.assertEqual(voice.labels["gender"], "female")


class TestTTSResult(unittest.TestCase):
    """TTS结果测试类"""
    
    def test_tts_result_save(self):
        """测试保存音频"""
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp_path = tmp.name
        
        try:
            result = TTSResult(
                text="Hello",
                voice_id="Rachel",
                voice_name="Rachel",
                model="eleven_multilingual_v2",
                audio_data=b"test audio data"
            )
            
            saved_path = result.save(tmp_path)
            self.assertEqual(saved_path, tmp_path)
            self.assertEqual(result.file_path, tmp_path)
            
            # 验证文件内容
            with open(tmp_path, 'rb') as f:
                self.assertEqual(f.read(), b"test audio data")
        finally:
            os.unlink(tmp_path)
    
    def test_tts_result_save_no_data(self):
        """测试没有音频数据时保存"""
        result = TTSResult(
            text="Hello",
            voice_id="Rachel",
            voice_name="Rachel",
            model="eleven_multilingual_v2",
            audio_data=None
        )
        
        saved_path = result.save("/tmp/test.mp3")
        self.assertEqual(saved_path, "")


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestElevenLabsManager))
    suite.addTests(loader.loadTestsFromTestCase(TestVoiceInfo))
    suite.addTests(loader.loadTestsFromTestCase(TestTTSResult))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
