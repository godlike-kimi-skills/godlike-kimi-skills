---
name: ffmpeg-skill
description: FFmpeg media processing for video conversion, audio extraction, format conversion, batch processing, and thumbnail generation. Use when converting media formats, resizing videos, extracting audio tracks, trimming content, or creating video thumbnails. Supports H.264/H.265/VP9 codecs and various container formats.
---

# FFmpeg Media Processing Skill

## Use When
- Converting video formats (MP4, MKV, AVI, etc.)
- Extracting audio from video files
- Resizing or changing video resolution
- Trimming video segments
- Creating video thumbnails
- Batch processing multiple files
- Adjusting video framerate
- Changing audio volume

## Out of Scope
- Real-time streaming setup
- Complex video editing (non-linear)
- Hardware acceleration configuration (CPU only)
- DRM/protected content handling
- Professional color grading
- Motion tracking or effects
- Live encoding pipelines

## Quick Start

```python
from scripts.main import FFmpegManager, VideoConfig, AudioConfig
from scripts.main import VideoCodec, AudioCodec, ContainerFormat

# Initialize
ffmpeg = FFmpegManager()

# Check installation
if not ffmpeg.check_ffmpeg():
    print("FFmpeg not installed")

# Get media info
info = ffmpeg.get_media_info("input.mp4")
print(f"Duration: {info.duration}s, Resolution: {info.width}x{info.height}")

# Convert video
video_config = VideoConfig(
    codec=VideoCodec.H264,
    preset="medium",
    crf=23
)
ffmpeg.convert_video("input.mp4", "output.mp4", video_config=video_config)

# Extract audio
ffmpeg.extract_audio("input.mp4", "output.mp3")
```

## Core Features

### Video Conversion
- Multiple codec support (H.264, H.265, VP9, AV1)
- Resolution scaling with aspect ratio control
- Framerate conversion
- Quality control via CRF or bitrate

### Audio Operations
- Extract audio tracks
- Convert audio formats (MP3, AAC, Opus, FLAC)
- Adjust volume levels
- Change sample rate and channels

### Format Support
- **Video**: MP4, MKV, AVI, MOV, WEBM, FLV
- **Audio**: MP3, AAC, FLAC, Opus, Vorbis
- **Codecs**: H.264, H.265, VP9, AV1, MPEG4

### Batch Processing
- Convert multiple files
- Generate thumbnails in batch
- Concatenate videos
- Parallel processing support

## CLI Usage

```bash
# Get media info
python scripts/main.py info input.mp4

# Convert video
python scripts/main.py convert input.mp4 output.mp4 --codec libx264 --preset medium --crf 23

# Extract audio
python scripts/main.py extract-audio input.mp4 output.mp3 --codec libmp3lame --bitrate 192k

# Resize video
python scripts/main.py resize input.mp4 output.mp4 --width 1280 --height 720

# Trim video
python scripts/main.py trim input.mp4 output.mp4 --start 10.5 --end 60.0

# Create thumbnail
python scripts/main.py thumbnail input.mp4 thumb.jpg --time 5.0
```

## Configuration Options

### VideoConfig Options
| Option | Default | Description |
|--------|---------|-------------|
| codec | H264 | Video codec (H264, H265, VP9, AV1) |
| preset | medium | Encoding speed/quality tradeoff |
| crf | 23 | Constant rate factor (0-51, lower=better) |
| bitrate | None | Target bitrate (e.g., "5M") |
| resolution | None | Output resolution (width, height) |
| fps | None | Output framerate |

### Preset Options
- **ultrafast**: Fastest encoding, largest file
- **superfast, veryfast, faster, fast**: Progressive speed/quality
- **medium**: Balanced (default)
- **slow, slower, veryslow**: Better quality, slower encoding

## Code Examples

### Batch Convert Directory
```python
import glob
from pathlib import Path

ffmpeg = FFmpegManager()
input_files = glob.glob("/path/to/videos/*.avi")
output_dir = "/path/to/output"

video_config = VideoConfig(codec=VideoCodec.H264, crf=23)
ffmpeg.batch_convert(input_files, output_dir, "mp4", video_config)
```

### Create Thumbnails
```python
ffmpeg = FFmpegManager()
info = ffmpeg.get_media_info("video.mp4")

# Create thumbnail at 10% of duration
thumb_time = info.duration * 0.1
ffmpeg.create_thumbnail("video.mp4", "thumb.jpg", thumb_time, width=320)
```
