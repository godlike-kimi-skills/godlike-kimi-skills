#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Transcript Skill 测试文件
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import YouTubeTranscriptExtractor, TranscriptSegment, TranscriptResult


class TestYouTubeTranscriptExtractor(unittest.TestCase):
    """YouTube字幕提取器测试类"""
    
    @patch('main.YouTubeTranscriptApi')
    def setUp(self, mock_api):
        """测试前准备"""
        self.mock_api = mock_api
        self.extractor = YouTubeTranscriptExtractor()
    
    def test_extract_video_id_standard_url(self):
        """测试标准URL提取视频ID"""
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),  # 直接ID
        ]
        
        for url, expected_id in test_cases:
            result = self.extractor.extract_video_id(url)
            self.assertEqual(result, expected_id, f"Failed for URL: {url}")
    
    def test_extract_video_id_invalid(self):
        """测试无效URL"""
        invalid_urls = [
            "https://www.google.com",
            "not a url",
            "https://youtube.com/watch",  # 没有v参数
        ]
        
        for url in invalid_urls:
            result = self.extractor.extract_video_id(url)
            self.assertIsNone(result, f"Should be None for: {url}")
    
    @patch('main.YouTubeTranscriptApi')
    def test_get_available_languages(self, mock_api_class):
        """测试获取可用语言"""
        # 设置mock
        mock_transcript = Mock()
        mock_transcript.language_code = "en"
        mock_transcript.language = "English"
        mock_transcript.is_generated = False
        mock_transcript.is_translatable = True
        
        mock_list = Mock()
        mock_list.__iter__ = Mock(return_value=iter([mock_transcript]))
        mock_api_class.list_transcripts.return_value = mock_list
        
        extractor = YouTubeTranscriptExtractor()
        languages = extractor.get_available_languages("test_video_id")
        
        self.assertEqual(len(languages), 1)
        self.assertEqual(languages[0]["language_code"], "en")
        self.assertEqual(languages[0]["language_name"], "English")
    
    def test_format_srt_time(self):
        """测试SRT时间格式化"""
        test_cases = [
            (0, "00:00:00,000"),
            (3661.123, "01:01:01,123"),
            (59.999, "00:00:59,999"),
        ]
        
        for seconds, expected in test_cases:
            result = self.extractor._format_srt_time(seconds)
            self.assertEqual(result, expected)
    
    def test_format_vtt_time(self):
        """测试VTT时间格式化"""
        test_cases = [
            (0, "00:00:00.000"),
            (3661.123, "01:01:01.123"),
        ]
        
        for seconds, expected in test_cases:
            result = self.extractor._format_vtt_time(seconds)
            self.assertEqual(result, expected)
    
    def test_format_transcript_text(self):
        """测试文本格式输出"""
        segments = [
            TranscriptSegment(text="Hello world", start=0, duration=1),
            TranscriptSegment(text="Second sentence", start=1, duration=1),
        ]
        result = TranscriptResult(
            video_id="test",
            language="en",
            language_name="English",
            is_generated=False,
            segments=segments
        )
        
        output = self.extractor.format_transcript(result, "text")
        self.assertIn("Hello world", output)
        self.assertIn("Second sentence", output)
    
    def test_format_transcript_json(self):
        """测试JSON格式输出"""
        segments = [
            TranscriptSegment(text="Test", start=0, duration=1),
        ]
        result = TranscriptResult(
            video_id="test",
            language="en",
            language_name="English",
            is_generated=False,
            segments=segments
        )
        
        output = self.extractor.format_transcript(result, "json")
        data = __import__('json').loads(output)
        self.assertEqual(data["video_id"], "test")
        self.assertEqual(data["language"], "en")
    
    def test_format_transcript_srt(self):
        """测试SRT格式输出"""
        segments = [
            TranscriptSegment(text="First line", start=0, duration=2),
            TranscriptSegment(text="Second line", start=2, duration=2),
        ]
        result = TranscriptResult(
            video_id="test",
            language="en",
            language_name="English",
            is_generated=False,
            segments=segments
        )
        
        output = self.extractor.format_transcript(result, "srt")
        self.assertIn("1", output)
        self.assertIn("00:00:00,000 --> 00:00:02,000", output)
        self.assertIn("First line", output)
        self.assertIn("Second line", output)
    
    def test_format_transcript_vtt(self):
        """测试VTT格式输出"""
        segments = [
            TranscriptSegment(text="Test", start=0, duration=1),
        ]
        result = TranscriptResult(
            video_id="test",
            language="en",
            language_name="English",
            is_generated=False,
            segments=segments
        )
        
        output = self.extractor.format_transcript(result, "vtt")
        self.assertIn("WEBVTT", output)
        self.assertIn("00:00:00.000 --> 00:00:01.000", output)
    
    def test_generate_summary(self):
        """测试摘要生成"""
        segments = [
            TranscriptSegment(text="This is the first sentence.", start=0, duration=1),
            TranscriptSegment(text="This is the second sentence.", start=1, duration=1),
            TranscriptSegment(text="This is the third sentence.", start=2, duration=1),
        ]
        result = TranscriptResult(
            video_id="test",
            language="en",
            language_name="English",
            is_generated=False,
            segments=segments
        )
        
        summary = self.extractor.generate_summary(result, max_sentences=2)
        self.assertIn("first", summary)
        self.assertIn("second", summary)
        # 第三句不应该在摘要中
        self.assertNotIn("third", summary)
    
    def test_search_in_transcript(self):
        """测试字幕搜索"""
        segments = [
            TranscriptSegment(text="Hello world today", start=0, duration=2),
            TranscriptSegment(text="The weather is nice", start=2, duration=2),
            TranscriptSegment(text="Hello again tomorrow", start=4, duration=2),
        ]
        result = TranscriptResult(
            video_id="test",
            language="en",
            language_name="English",
            is_generated=False,
            segments=segments
        )
        
        matches = self.extractor.search_in_transcript(result, "Hello", context_seconds=1)
        
        self.assertEqual(len(matches), 2)  # 应该找到2个匹配
        self.assertEqual(matches[0]["timestamp"], 0)
        self.assertEqual(matches[1]["timestamp"], 4)
    
    def test_search_not_found(self):
        """测试搜索未找到"""
        segments = [
            TranscriptSegment(text="Hello world", start=0, duration=1),
        ]
        result = TranscriptResult(
            video_id="test",
            language="en",
            language_name="English",
            is_generated=False,
            segments=segments
        )
        
        matches = self.extractor.search_in_transcript(result, "xyz")
        self.assertEqual(len(matches), 0)


class TestTranscriptSegment(unittest.TestCase):
    """字幕片段测试类"""
    
    def test_segment_calculation(self):
        """测试片段计算"""
        segment = TranscriptSegment(
            text="Test",
            start=10.5,
            duration=2.5
        )
        
        self.assertEqual(segment.start, 10.5)
        self.assertEqual(segment.duration, 2.5)
        self.assertEqual(segment.end, 13.0)  # start + duration


class TestTranscriptResult(unittest.TestCase):
    """转录结果测试类"""
    
    def test_full_text_generation(self):
        """测试全文生成"""
        segments = [
            TranscriptSegment(text="First", start=0, duration=1),
            TranscriptSegment(text="Second", start=1, duration=1),
        ]
        result = TranscriptResult(
            video_id="test",
            language="en",
            language_name="English",
            is_generated=False,
            segments=segments
        )
        
        self.assertEqual(result.full_text, "First Second")
    
    def test_empty_segments(self):
        """测试空片段"""
        result = TranscriptResult(
            video_id="test",
            language="en",
            language_name="English",
            is_generated=False,
            segments=[]
        )
        
        self.assertEqual(result.full_text, "")


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestYouTubeTranscriptExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestTranscriptSegment))
    suite.addTests(loader.loadTestsFromTestCase(TestTranscriptResult))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
