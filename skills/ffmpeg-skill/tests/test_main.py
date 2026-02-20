#!/usr/bin/env python3
"""
Tests for FFmpeg Skill
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.main import (
    FFmpegManager, VideoConfig, AudioConfig, MediaInfo,
    VideoCodec, AudioCodec, ContainerFormat
)

class TestVideoConfig(unittest.TestCase):
    
    def test_default_values(self):
        """Test default video configuration"""
        config = VideoConfig()
        self.assertEqual(config.codec, VideoCodec.H264)
        self.assertEqual(config.preset, "medium")
        self.assertEqual(config.crf, 23)
        self.assertIsNone(config.bitrate)
        self.assertIsNone(config.resolution)
        self.assertIsNone(config.fps)
    
    def test_to_ffmpeg_args(self):
        """Test conversion to FFmpeg arguments"""
        config = VideoConfig(
            codec=VideoCodec.H265,
            preset="slow",
            crf=28,
            resolution=(1920, 1080),
            fps=30
        )
        
        args = config.to_ffmpeg_args()
        
        self.assertIn("-c:v", args)
        self.assertIn("libx265", args)
        self.assertIn("-preset", args)
        self.assertIn("slow", args)
        self.assertIn("-crf", args)
        self.assertIn("28", args)
        self.assertIn("-s", args)
        self.assertIn("1920x1080", args)
        self.assertIn("-r", args)
        self.assertIn("30", args)
    
    def test_bitrate_overrides_crf(self):
        """Test that bitrate overrides CRF when set"""
        config = VideoConfig(bitrate="5M")
        args = config.to_ffmpeg_args()
        
        self.assertIn("-b:v", args)
        self.assertIn("5M", args)
        self.assertNotIn("-crf", args)

class TestAudioConfig(unittest.TestCase):
    
    def test_default_values(self):
        """Test default audio configuration"""
        config = AudioConfig()
        self.assertEqual(config.codec, AudioCodec.AAC)
        self.assertIsNone(config.bitrate)
        self.assertIsNone(config.sample_rate)
        self.assertIsNone(config.channels)
        self.assertIsNone(config.volume)
    
    def test_to_ffmpeg_args(self):
        """Test conversion to FFmpeg arguments"""
        config = AudioConfig(
            codec=AudioCodec.MP3,
            bitrate="192k",
            sample_rate=44100,
            channels=2
        )
        
        args = config.to_ffmpeg_args()
        
        self.assertIn("-c:a", args)
        self.assertIn("libmp3lame", args)
        self.assertIn("-b:a", args)
        self.assertIn("192k", args)
        self.assertIn("-ar", args)
        self.assertIn("44100", args)
        self.assertIn("-ac", args)
        self.assertIn("2", args)

class TestMediaInfo(unittest.TestCase):
    
    def test_initialization(self):
        """Test MediaInfo initialization"""
        info = MediaInfo(
            filename="test.mp4",
            duration=120.5,
            bitrate=5000000,
            width=1920,
            height=1080,
            fps=24.0
        )
        
        self.assertEqual(info.filename, "test.mp4")
        self.assertEqual(info.duration, 120.5)
        self.assertEqual(info.width, 1920)
        self.assertEqual(info.height, 1080)
        self.assertEqual(info.fps, 24.0)

class TestFFmpegManager(unittest.TestCase):
    
    def setUp(self):
        self.ffmpeg = FFmpegManager()
    
    @patch('scripts.main.subprocess.run')
    def test_check_ffmpeg_success(self, mock_run):
        """Test FFmpeg detection - success"""
        mock_run.return_value = Mock(returncode=0)
        self.assertTrue(self.ffmpeg.check_ffmpeg())
    
    @patch('scripts.main.subprocess.run')
    def test_check_ffmpeg_failure(self, mock_run):
        """Test FFmpeg detection - failure"""
        mock_run.side_effect = FileNotFoundError
        self.assertFalse(self.ffmpeg.check_ffmpeg())
    
    @patch('scripts.main.subprocess.run')
    def test_get_media_info(self, mock_run):
        """Test getting media information"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps({
                "format": {
                    "filename": "test.mp4",
                    "duration": "120.5",
                    "bit_rate": "5000000",
                    "format_name": "mov,mp4,m4a",
                    "size": "1000000"
                },
                "streams": [
                    {
                        "codec_type": "video",
                        "codec_name": "h264",
                        "width": 1920,
                        "height": 1080,
                        "r_frame_rate": "24/1"
                    },
                    {
                        "codec_type": "audio",
                        "codec_name": "aac",
                        "channels": 2,
                        "sample_rate": "44100"
                    }
                ]
            }),
            stderr=""
        )
        
        info = self.ffmpeg.get_media_info("test.mp4")
        
        self.assertIsNotNone(info)
        self.assertEqual(info.filename, "test.mp4")
        self.assertEqual(info.duration, 120.5)
        self.assertEqual(info.width, 1920)
        self.assertEqual(info.height, 1080)
        self.assertEqual(info.fps, 24.0)
    
    @patch('scripts.main.subprocess.run')
    def test_get_media_info_failure(self, mock_run):
        """Test getting media information - failure"""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="error")
        
        info = self.ffmpeg.get_media_info("nonexistent.mp4")
        self.assertIsNone(info)
    
    @patch('scripts.main.subprocess.run')
    def test_convert_video(self, mock_run):
        """Test video conversion"""
        mock_run.return_value = Mock(returncode=0, stderr="")
        
        video_config = VideoConfig(codec=VideoCodec.H264)
        result = self.ffmpeg.convert_video(
            "input.mp4",
            "output.mp4",
            video_config=video_config
        )
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('scripts.main.subprocess.run')
    def test_extract_audio(self, mock_run):
        """Test audio extraction"""
        mock_run.return_value = Mock(returncode=0, stderr="")
        
        audio_config = AudioConfig(codec=AudioCodec.MP3, bitrate="192k")
        result = self.ffmpeg.extract_audio(
            "input.mp4",
            "output.mp3",
            audio_config
        )
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('scripts.main.subprocess.run')
    def test_resize_video(self, mock_run):
        """Test video resizing"""
        mock_run.return_value = Mock(returncode=0, stderr="")
        
        result = self.ffmpeg.resize_video(
            "input.mp4",
            "output.mp4",
            1280,
            720,
            maintain_aspect=True
        )
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('scripts.main.subprocess.run')
    def test_trim_media(self, mock_run):
        """Test video trimming"""
        mock_run.return_value = Mock(returncode=0, stderr="")
        
        result = self.ffmpeg.trim_media(
            "input.mp4",
            "output.mp4",
            10.0,
            30.0
        )
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('scripts.main.subprocess.run')
    def test_create_thumbnail(self, mock_run):
        """Test thumbnail creation"""
        mock_run.return_value = Mock(returncode=0, stderr="")
        
        result = self.ffmpeg.create_thumbnail(
            "input.mp4",
            "thumb.jpg",
            time_position=5.0,
            width=320
        )
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('scripts.main.subprocess.run')
    def test_adjust_volume(self, mock_run):
        """Test volume adjustment"""
        mock_run.return_value = Mock(returncode=0, stderr="")
        
        result = self.ffmpeg.adjust_volume("input.mp4", "output.mp4", 10.0)
        
        self.assertTrue(result)
        mock_run.assert_called_once()

import json

if __name__ == "__main__":
    unittest.main()
