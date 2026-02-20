#!/usr/bin/env python3
"""
FFmpeg Media Processing Skill
Supports: video conversion, audio extraction, format conversion, batch processing
"""

import os
import sys
import json
import argparse
import subprocess
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import tempfile
import shutil

# ============================================================================
# Enums and Data Classes
# ============================================================================

class VideoCodec(Enum):
    """Supported video codecs"""
    H264 = "libx264"
    H265 = "libx265"
    VP9 = "libvpx-vp9"
    AV1 = "libaom-av1"
    MPEG4 = "mpeg4"
    COPY = "copy"

class AudioCodec(Enum):
    """Supported audio codecs"""
    AAC = "aac"
    MP3 = "libmp3lame"
    OPUS = "libopus"
    FLAC = "flac"
    VORBIS = "libvorbis"
    COPY = "copy"

class ContainerFormat(Enum):
    """Supported container formats"""
    MP4 = "mp4"
    MKV = "matroska"
    AVI = "avi"
    MOV = "mov"
    WEBM = "webm"
    FLV = "flv"
    TS = "mpegts"

@dataclass
class VideoConfig:
    """Video encoding configuration"""
    codec: VideoCodec = VideoCodec.H264
    preset: str = "medium"  # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
    crf: int = 23  # 0-51, lower is better quality
    bitrate: Optional[str] = None  # e.g., "5M" for 5 Mbps
    resolution: Optional[Tuple[int, int]] = None  # (width, height)
    fps: Optional[int] = None
    pix_fmt: str = "yuv420p"
    
    def to_ffmpeg_args(self) -> List[str]:
        """Convert to FFmpeg command arguments"""
        args = ["-c:v", self.codec.value, "-preset", self.preset, "-pix_fmt", self.pix_fmt]
        
        if self.bitrate:
            args.extend(["-b:v", self.bitrate])
        else:
            args.extend(["-crf", str(self.crf)])
        
        if self.resolution:
            args.extend(["-s", f"{self.resolution[0]}x{self.resolution[1]}"])
        
        if self.fps:
            args.extend(["-r", str(self.fps)])
        
        return args

@dataclass
class AudioConfig:
    """Audio encoding configuration"""
    codec: AudioCodec = AudioCodec.AAC
    bitrate: Optional[str] = None  # e.g., "128k"
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    volume: Optional[float] = None
    
    def to_ffmpeg_args(self) -> List[str]:
        """Convert to FFmpeg command arguments"""
        args = ["-c:a", self.codec.value]
        
        if self.bitrate:
            args.extend(["-b:a", self.bitrate])
        
        if self.sample_rate:
            args.extend(["-ar", str(self.sample_rate)])
        
        if self.channels:
            args.extend(["-ac", str(self.channels)])
        
        if self.volume is not None:
            args.extend(["-filter:a", f"volume={self.volume}"])
        
        return args

@dataclass
class MediaInfo:
    """Media file information"""
    filename: str
    duration: float = 0.0
    bitrate: int = 0
    width: int = 0
    height: int = 0
    fps: float = 0.0
    video_codec: str = ""
    audio_codec: str = ""
    audio_channels: int = 0
    audio_sample_rate: int = 0
    format_name: str = ""
    size_bytes: int = 0

# ============================================================================
# FFmpeg Manager
# ============================================================================

class FFmpegManager:
    """Main class for managing FFmpeg operations"""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg", ffprobe_path: str = "ffprobe"):
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path
    
    def _run_command(self, args: List[str], capture_output: bool = True) -> Tuple[bool, str]:
        """Run FFmpeg/FFprobe command"""
        cmd = [self.ffmpeg_path] + args
        
        try:
            if capture_output:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                result = subprocess.run(cmd)
            
            return result.returncode == 0, result.stderr
        except FileNotFoundError:
            return False, f"Command not found: {cmd[0]}"
        except Exception as e:
            return False, str(e)
    
    def check_ffmpeg(self) -> bool:
        """Check if FFmpeg is installed"""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    # ========================================================================
    # Media Information
    # ========================================================================
    
    def get_media_info(self, input_file: str) -> Optional[MediaInfo]:
        """Get media file information using ffprobe"""
        cmd = [
            self.ffprobe_path,
            "-v", "error",
            "-show_format",
            "-show_streams",
            "-of", "json",
            input_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return None
            
            data = json.loads(result.stdout)
            format_info = data.get("format", {})
            streams = data.get("streams", [])
            
            # Find video and audio streams
            video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
            audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})
            
            # Calculate FPS
            fps = 0.0
            r_frame_rate = video_stream.get("r_frame_rate", "0/1")
            if "/" in r_frame_rate:
                num, den = r_frame_rate.split("/")
                fps = float(num) / float(den) if float(den) != 0 else 0
            
            return MediaInfo(
                filename=input_file,
                duration=float(format_info.get("duration", 0)),
                bitrate=int(format_info.get("bit_rate", 0)),
                width=video_stream.get("width", 0),
                height=video_stream.get("height", 0),
                fps=fps,
                video_codec=video_stream.get("codec_name", ""),
                audio_codec=audio_stream.get("codec_name", ""),
                audio_channels=audio_stream.get("channels", 0),
                audio_sample_rate=int(audio_stream.get("sample_rate", 0)),
                format_name=format_info.get("format_name", ""),
                size_bytes=int(format_info.get("size", 0))
            )
        except Exception:
            return None
    
    def print_media_info(self, info: MediaInfo) -> None:
        """Print media information in readable format"""
        print(f"File: {info.filename}")
        print(f"Format: {info.format_name}")
        print(f"Duration: {info.duration:.2f} seconds")
        print(f"Size: {info.size_bytes / 1024 / 1024:.2f} MB")
        print(f"Bitrate: {info.bitrate / 1000:.0f} kbps")
        print(f"Video: {info.width}x{info.height} @ {info.fps:.2f} fps ({info.video_codec})")
        print(f"Audio: {info.audio_codec}, {info.audio_channels} channels @ {info.audio_sample_rate} Hz")
    
    # ========================================================================
    # Video Conversion
    # ========================================================================
    
    def convert_video(self, input_file: str, output_file: str,
                      video_config: VideoConfig = None,
                      audio_config: AudioConfig = None,
                      start_time: Optional[float] = None,
                      duration: Optional[float] = None,
                      overwrite: bool = False) -> bool:
        """Convert video file with specified configuration"""
        args = ["-i", input_file]
        
        # Time options
        if start_time is not None:
            args.extend(["-ss", str(start_time)])
        if duration is not None:
            args.extend(["-t", str(duration)])
        
        # Video options
        if video_config:
            args.extend(video_config.to_ffmpeg_args())
        else:
            args.extend(["-c:v", "copy"])
        
        # Audio options
        if audio_config:
            args.extend(audio_config.to_ffmpeg_args())
        else:
            args.extend(["-c:a", "copy"])
        
        # Output
        if overwrite:
            args.append("-y")
        args.append(output_file)
        
        success, error = self._run_command(args)
        if not success:
            print(f"Conversion failed: {error}")
        return success
    
    def convert_format(self, input_file: str, output_file: str,
                       container: ContainerFormat = None,
                       video_codec: VideoCodec = VideoCodec.COPY,
                       audio_codec: AudioCodec = AudioCodec.COPY) -> bool:
        """Convert video to different format"""
        args = ["-i", input_file]
        
        args.extend(["-c:v", video_codec.value])
        args.extend(["-c:a", audio_codec.value])
        
        if container:
            args.extend(["-f", container.value])
        
        args.append(output_file)
        
        success, error = self._run_command(args)
        return success
    
    def resize_video(self, input_file: str, output_file: str,
                     width: int, height: int, maintain_aspect: bool = True) -> bool:
        """Resize video to specified dimensions"""
        if maintain_aspect:
            scale_filter = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
        else:
            scale_filter = f"scale={width}:{height}"
        
        args = [
            "-i", input_file,
            "-vf", scale_filter,
            "-c:a", "copy",
            output_file
        ]
        
        success, error = self._run_command(args)
        return success
    
    def change_framerate(self, input_file: str, output_file: str, fps: int) -> bool:
        """Change video framerate"""
        args = [
            "-i", input_file,
            "-r", str(fps),
            "-c:a", "copy",
            output_file
        ]
        
        success, error = self._run_command(args)
        return success
    
    # ========================================================================
    # Audio Operations
    # ========================================================================
    
    def extract_audio(self, input_file: str, output_file: str,
                      audio_config: AudioConfig = None) -> bool:
        """Extract audio from video file"""
        args = ["-i", input_file, "-vn"]  # No video
        
        if audio_config:
            args.extend(audio_config.to_ffmpeg_args())
        else:
            args.extend(["-c:a", "libmp3lame", "-q:a", "2"])
        
        args.append(output_file)
        
        success, error = self._run_command(args)
        return success
    
    def convert_audio(self, input_file: str, output_file: str,
                      codec: AudioCodec = AudioCodec.MP3,
                      bitrate: str = "192k") -> bool:
        """Convert audio file to different format"""
        config = AudioConfig(codec=codec, bitrate=bitrate)
        args = ["-i", input_file]
        args.extend(config.to_ffmpeg_args())
        args.append(output_file)
        
        success, error = self._run_command(args)
        return success
    
    def adjust_volume(self, input_file: str, output_file: str,
                      volume_db: float) -> bool:
        """Adjust audio volume (in dB, negative to decrease)"""
        args = [
            "-i", input_file,
            "-af", f"volume={volume_db}dB",
            "-c:v", "copy",
            output_file
        ]
        
        success, error = self._run_command(args)
        return success
    
    def trim_media(self, input_file: str, output_file: str,
                   start_time: float, end_time: float) -> bool:
        """Trim media file to specified time range"""
        duration = end_time - start_time
        args = [
            "-i", input_file,
            "-ss", str(start_time),
            "-t", str(duration),
            "-c", "copy",  # Stream copy (no re-encode)
            output_file
        ]
        
        success, error = self._run_command(args)
        return success
    
    # ========================================================================
    # Batch Processing
    # ========================================================================
    
    def batch_convert(self, input_files: List[str], output_dir: str,
                      output_ext: str, video_config: VideoConfig = None) -> List[str]:
        """Batch convert multiple files"""
        output_files = []
        
        for input_file in input_files:
            base_name = Path(input_file).stem
            output_file = os.path.join(output_dir, f"{base_name}.{output_ext}")
            
            if self.convert_video(input_file, output_file, video_config):
                output_files.append(output_file)
                print(f"Converted: {input_file} -> {output_file}")
            else:
                print(f"Failed: {input_file}")
        
        return output_files
    
    def create_thumbnail(self, input_file: str, output_file: str,
                         time_position: float = 0, width: int = 320) -> bool:
        """Create video thumbnail at specified time position"""
        args = [
            "-i", input_file,
            "-ss", str(time_position),
            "-vframes", "1",
            "-vf", f"scale={width}:-1",
            "-q:v", "2",
            output_file
        ]
        
        success, error = self._run_command(args)
        return success
    
    def concatenate_videos(self, input_files: List[str], output_file: str) -> bool:
        """Concatenate multiple video files"""
        # Create concat demuxer input file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for video in input_files:
                f.write(f"file '{os.path.abspath(video)}'\n")
            concat_file = f.name
        
        try:
            args = [
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",
                output_file
            ]
            
            success, error = self._run_command(args)
        finally:
            os.unlink(concat_file)
        
        return success

# ============================================================================
# CLI Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="FFmpeg Media Processor")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="FFmpeg binary path")
    parser.add_argument("--ffprobe", default="ffprobe", help="FFprobe binary path")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Info
    info_parser = subparsers.add_parser("info", help="Get media info")
    info_parser.add_argument("input", help="Input file")
    
    # Convert
    convert_parser = subparsers.add_parser("convert", help="Convert video")
    convert_parser.add_argument("input", help="Input file")
    convert_parser.add_argument("output", help="Output file")
    convert_parser.add_argument("--codec", default="libx264", help="Video codec")
    convert_parser.add_argument("--preset", default="medium", help="Encoding preset")
    convert_parser.add_argument("--crf", type=int, default=23, help="CRF quality")
    convert_parser.add_argument("--resolution", help="Resolution (e.g., 1920x1080)")
    
    # Extract audio
    extract_parser = subparsers.add_parser("extract-audio", help="Extract audio")
    extract_parser.add_argument("input", help="Input video file")
    extract_parser.add_argument("output", help="Output audio file")
    extract_parser.add_argument("--codec", default="libmp3lame", help="Audio codec")
    extract_parser.add_argument("--bitrate", default="192k", help="Audio bitrate")
    
    # Resize
    resize_parser = subparsers.add_parser("resize", help="Resize video")
    resize_parser.add_argument("input", help="Input file")
    resize_parser.add_argument("output", help="Output file")
    resize_parser.add_argument("--width", type=int, required=True, help="Width")
    resize_parser.add_argument("--height", type=int, required=True, help="Height")
    
    # Trim
    trim_parser = subparsers.add_parser("trim", help="Trim video")
    trim_parser.add_argument("input", help="Input file")
    trim_parser.add_argument("output", help="Output file")
    trim_parser.add_argument("--start", type=float, required=True, help="Start time")
    trim_parser.add_argument("--end", type=float, required=True, help="End time")
    
    # Thumbnail
    thumb_parser = subparsers.add_parser("thumbnail", help="Create thumbnail")
    thumb_parser.add_argument("input", help="Input file")
    thumb_parser.add_argument("output", help="Output file")
    thumb_parser.add_argument("--time", type=float, default=0, help="Time position")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = FFmpegManager(args.ffmpeg, args.ffprobe)
    
    if not manager.check_ffmpeg():
        print("FFmpeg not found. Please install FFmpeg.")
        return
    
    if args.command == "info":
        info = manager.get_media_info(args.input)
        if info:
            manager.print_media_info(info)
        else:
            print("Failed to get media info")
    
    elif args.command == "convert":
        video_config = VideoConfig(
            codec=VideoCodec(args.codec),
            preset=args.preset,
            crf=args.crf
        )
        if args.resolution:
            w, h = map(int, args.resolution.split("x"))
            video_config.resolution = (w, h)
        
        if manager.convert_video(args.input, args.output, video_config):
            print(f"Converted: {args.output}")
    
    elif args.command == "extract-audio":
        audio_config = AudioConfig(
            codec=AudioCodec(args.codec),
            bitrate=args.bitrate
        )
        if manager.extract_audio(args.input, args.output, audio_config):
            print(f"Extracted: {args.output}")
    
    elif args.command == "resize":
        if manager.resize_video(args.input, args.output, args.width, args.height):
            print(f"Resized: {args.output}")
    
    elif args.command == "trim":
        if manager.trim_media(args.input, args.output, args.start, args.end):
            print(f"Trimmed: {args.output}")
    
    elif args.command == "thumbnail":
        if manager.create_thumbnail(args.input, args.output, args.time):
            print(f"Created thumbnail: {args.output}")

if __name__ == "__main__":
    main()
