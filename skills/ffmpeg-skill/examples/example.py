#!/usr/bin/env python3
"""
FFmpeg Skill Usage Examples
"""

import sys
import os
import glob

sys.path.insert(0, '..')

from scripts.main import (
    FFmpegManager, VideoConfig, AudioConfig,
    VideoCodec, AudioCodec, ContainerFormat
)

def example_media_info():
    """Demonstrate getting media information"""
    ffmpeg = FFmpegManager()
    
    # Replace with actual video file path
    video_path = "sample.mp4"
    
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        return
    
    info = ffmpeg.get_media_info(video_path)
    
    if info:
        print("=" * 50)
        print("Media Information")
        print("=" * 50)
        ffmpeg.print_media_info(info)
    else:
        print("Failed to get media info")

def example_video_conversion():
    """Demonstrate video conversion with different settings"""
    ffmpeg = FFmpegManager()
    
    input_file = "input.mp4"
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return
    
    # 1. Basic conversion with H.264
    print("\n1. Converting to H.264...")
    video_config = VideoConfig(
        codec=VideoCodec.H264,
        preset="medium",
        crf=23
    )
    ffmpeg.convert_video(input_file, "output_h264.mp4", video_config=video_config)
    
    # 2. Convert to H.265 for smaller file
    print("\n2. Converting to H.265 (HEVC)...")
    video_config = VideoConfig(
        codec=VideoCodec.H265,
        preset="slow",
        crf=28
    )
    ffmpeg.convert_video(input_file, "output_h265.mp4", video_config=video_config)
    
    # 3. Convert to VP9 for web
    print("\n3. Converting to VP9 (WebM)...")
    video_config = VideoConfig(
        codec=VideoCodec.VP9,
        crf=31
    )
    ffmpeg.convert_video(input_file, "output_vp9.webm", video_config=video_config)

def example_resize_video():
    """Demonstrate video resizing"""
    ffmpeg = FFmpegManager()
    
    input_file = "input.mp4"
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return
    
    # Resize to 720p maintaining aspect ratio
    print("\nResizing to 1280x720...")
    ffmpeg.resize_video(input_file, "output_720p.mp4", 1280, 720, maintain_aspect=True)
    
    # Resize to 480p
    print("Resizing to 854x480...")
    ffmpeg.resize_video(input_file, "output_480p.mp4", 854, 480, maintain_aspect=True)
    
    # Force exact resolution
    print("Forcing 640x480...")
    ffmpeg.resize_video(input_file, "output_forced.mp4", 640, 480, maintain_aspect=False)

def example_audio_operations():
    """Demonstrate audio extraction and conversion"""
    ffmpeg = FFmpegManager()
    
    input_file = "input.mp4"
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return
    
    # 1. Extract audio as MP3
    print("\n1. Extracting audio as MP3...")
    audio_config = AudioConfig(codec=AudioCodec.MP3, bitrate="192k")
    ffmpeg.extract_audio(input_file, "output.mp3", audio_config)
    
    # 2. Extract audio as AAC
    print("\n2. Extracting audio as AAC...")
    audio_config = AudioConfig(codec=AudioCodec.AAC, bitrate="128k")
    ffmpeg.extract_audio(input_file, "output.aac", audio_config)
    
    # 3. Extract audio as FLAC (lossless)
    print("\n3. Extracting audio as FLAC...")
    audio_config = AudioConfig(codec=AudioCodec.FLAC)
    ffmpeg.extract_audio(input_file, "output.flac", audio_config)
    
    # 4. Convert audio file format
    print("\n4. Converting WAV to MP3...")
    ffmpeg.convert_audio("input.wav", "output_mp3.mp3", codec=AudioCodec.MP3, bitrate="320k")

def example_trim_and_split():
    """Demonstrate video trimming"""
    ffmpeg = FFmpegManager()
    
    input_file = "input.mp4"
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return
    
    # Get duration first
    info = ffmpeg.get_media_info(input_file)
    if not info:
        return
    
    # Trim first 30 seconds
    print("\nTrimming first 30 seconds...")
    ffmpeg.trim_media(input_file, "output_first_30s.mp4", 0, 30)
    
    # Extract middle segment
    middle_start = info.duration / 2 - 15
    middle_end = info.duration / 2 + 15
    print(f"\nExtracting middle 30s ({middle_start:.1f}s to {middle_end:.1f}s)...")
    ffmpeg.trim_media(input_file, "output_middle.mp4", middle_start, middle_end)
    
    # Extract last minute
    if info.duration > 60:
        print("\nExtracting last minute...")
        ffmpeg.trim_media(input_file, "output_last_min.mp4", info.duration - 60, info.duration)

def example_thumbnails():
    """Demonstrate thumbnail creation"""
    ffmpeg = FFmpegManager()
    
    input_file = "input.mp4"
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return
    
    info = ffmpeg.get_media_info(input_file)
    if not info:
        return
    
    # Create thumbnail at start
    print("\nCreating thumbnail at 0s...")
    ffmpeg.create_thumbnail(input_file, "thumb_start.jpg", 0, width=320)
    
    # Create thumbnail at 25% of duration
    time_25 = info.duration * 0.25
    print(f"Creating thumbnail at {time_25:.1f}s (25%)...")
    ffmpeg.create_thumbnail(input_file, "thumb_25.jpg", time_25, width=320)
    
    # Create thumbnail at middle
    time_50 = info.duration * 0.5
    print(f"Creating thumbnail at {time_50:.1f}s (50%)...")
    ffmpeg.create_thumbnail(input_file, "thumb_50.jpg", time_50, width=640)
    
    # Create thumbnail at 75%
    time_75 = info.duration * 0.75
    print(f"Creating thumbnail at {time_75:.1f}s (75%)...")
    ffmpeg.create_thumbnail(input_file, "thumb_75.jpg", time_75, width=320)

def example_batch_processing():
    """Demonstrate batch processing"""
    ffmpeg = FFmpegManager()
    
    # Find all AVI files
    input_files = glob.glob("*.avi")
    
    if not input_files:
        print("No AVI files found for conversion")
        return
    
    print(f"\nFound {len(input_files)} AVI files")
    
    # Batch convert to MP4
    output_dir = "converted"
    os.makedirs(output_dir, exist_ok=True)
    
    video_config = VideoConfig(codec=VideoCodec.H264, crf=23)
    converted = ffmpeg.batch_convert(input_files, output_dir, "mp4", video_config)
    
    print(f"Successfully converted {len(converted)} files")

def example_concatenate():
    """Demonstrate video concatenation"""
    ffmpeg = FFmpegManager()
    
    # List of videos to concatenate
    input_files = ["part1.mp4", "part2.mp4", "part3.mp4"]
    
    # Check all files exist
    missing = [f for f in input_files if not os.path.exists(f)]
    if missing:
        print(f"Missing files: {missing}")
        return
    
    print("\nConcatenating videos...")
    ffmpeg.concatenate_videos(input_files, "combined.mp4")
    print("Concatenation complete")

def example_adjust_volume():
    """Demonstrate audio volume adjustment"""
    ffmpeg = FFmpegManager()
    
    input_file = "input.mp4"
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return
    
    # Increase volume by 10dB
    print("\nIncreasing volume by 10dB...")
    ffmpeg.adjust_volume(input_file, "output_louder.mp4", 10)
    
    # Decrease volume by 5dB
    print("Decreasing volume by 5dB...")
    ffmpeg.adjust_volume(input_file, "output_quieter.mp4", -5)

def example_framerate_change():
    """Demonstrate framerate conversion"""
    ffmpeg = FFmpegManager()
    
    input_file = "input.mp4"
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return
    
    # Convert to 24fps (cinematic)
    print("\nConverting to 24fps...")
    ffmpeg.change_framerate(input_file, "output_24fps.mp4", 24)
    
    # Convert to 30fps
    print("Converting to 30fps...")
    ffmpeg.change_framerate(input_file, "output_30fps.mp4", 30)
    
    # Convert to 60fps
    print("Converting to 60fps...")
    ffmpeg.change_framerate(input_file, "output_60fps.mp4", 60)

if __name__ == "__main__":
    print("=" * 60)
    print("FFmpeg Skill Examples")
    print("=" * 60)
    
    print("\nNote: These examples require video files in the current directory")
    print("-" * 60)
    
    # Run examples (uncomment as needed)
    # example_media_info()
    # example_video_conversion()
    # example_resize_video()
    # example_audio_operations()
    # example_trim_and_split()
    # example_thumbnails()
    # example_batch_processing()
    # example_concatenate()
    # example_adjust_volume()
    # example_framerate_change()
