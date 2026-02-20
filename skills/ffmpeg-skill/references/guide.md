# FFmpeg Media Processing Guide

## Table of Contents
1. [Video Codecs](#video-codecs)
2. [Audio Codecs](#audio-codecs)
3. [Container Formats](#containers)
4. [Encoding Settings](#encoding)
5. [Common Operations](#operations)

## Video Codecs <a name="video-codecs"></a>

### H.264 (AVC)
Most compatible codec, good balance of quality and size.
```bash
-c:v libx264 -preset medium -crf 23
```
- **Best for**: General purpose, web streaming
- **Compatibility**: Universal
- **Hardware**: Widely supported

### H.265 (HEVC)
Better compression than H.264, smaller files at same quality.
```bash
-c:v libx265 -preset slow -crf 28
```
- **Best for**: Archiving, limited bandwidth
- **Compatibility**: Modern devices
- **Hardware**: Requires newer hardware

### VP9
Open codec, excellent for web streaming.
```bash
-c:v libvpx-vp9 -crf 31 -b:v 0
```
- **Best for**: YouTube, web video
- **Compatibility**: Modern browsers
- **Hardware**: Limited support

### AV1
Next-generation codec, best compression.
```bash
-c:v libaom-av1 -crf 30 -b:v 0
```
- **Best for**: Future-proofing
- **Compatibility**: Limited
- **Hardware**: Emerging support

## Audio Codecs <a name="audio-codecs"></a>

### AAC
Standard for MP4, good quality at low bitrates.
```bash
-c:a aac -b:a 128k
```

### MP3
Universal compatibility.
```bash
-c:a libmp3lame -q:a 2
```

### Opus
Best quality for low bitrates, excellent for streaming.
```bash
-c:a libopus -b:a 96k
```

### FLAC
Lossless compression.
```bash
-c:a flac
```

## Container Formats <a name="containers"></a>

| Format | Video Codecs | Audio Codecs | Best For |
|--------|--------------|--------------|----------|
| MP4 | H.264, H.265 | AAC, MP3 | General purpose |
| MKV | All | All | Archiving |
| WEBM | VP9, VP8 | Vorbis, Opus | Web streaming |
| MOV | H.264, ProRes | AAC, PCM | Apple ecosystem |
| AVI | MPEG4, XviD | MP3, AC3 | Legacy support |

## Encoding Settings <a name="encoding"></a>

### CRF (Constant Rate Factor)
Quality-based encoding (0-51):
- **17-18**: Visually lossless
- **20-23**: Good quality (default)
- **28**: Acceptable quality
- **51**: Worst quality

### Presets
Speed vs compression tradeoff:
- **ultrafast**: Fastest, largest files
- **superfast, veryfast**: Fast encoding
- **faster, fast**: Good for batch
- **medium**: Balanced (default)
- **slow, slower, veryslow**: Best compression

### Bitrate Control
```bash
# Constant Bitrate (CBR)
-b:v 5M -minrate 5M -maxrate 5M -bufsize 10M

# Variable Bitrate (VBR)
-b:v 5M

# Constrained Quality
-crf 23 -maxrate 10M -bufsize 20M
```

## Common Operations <a name="operations"></a>

### Extract Audio
```bash
ffmpeg -i video.mp4 -vn -c:a libmp3lame -q:a 2 output.mp3
```

### Resize Video
```bash
# Maintain aspect ratio
ffmpeg -i input.mp4 -vf "scale=1280:-1" output.mp4

# Force resolution
ffmpeg -i input.mp4 -vf "scale=1280:720" output.mp4

# With padding
ffmpeg -i input.mp4 -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" output.mp4
```

### Trim Video
```bash
# Extract 30 seconds starting at 1 minute
ffmpeg -i input.mp4 -ss 00:01:00 -t 30 -c copy output.mp4

# Extract to end
ffmpeg -i input.mp4 -ss 00:01:00 -c copy output.mp4
```

### Concatenate Videos
```bash
# Create list file
echo "file 'video1.mp4'" > list.txt
echo "file 'video2.mp4'" >> list.txt

# Concatenate
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4
```

### Create Thumbnail
```bash
# At specific time
ffmpeg -i input.mp4 -ss 00:00:05 -vframes 1 output.jpg

# With scaling
ffmpeg -i input.mp4 -ss 00:00:05 -vframes 1 -vf "scale=320:-1" output.jpg
```

### Change Framerate
```bash
ffmpeg -i input.mp4 -r 30 output.mp4
```

### Adjust Volume
```bash
# Increase by 10dB
ffmpeg -i input.mp4 -af "volume=10dB" output.mp4

# Decrease by half
ffmpeg -i input.mp4 -af "volume=0.5" output.mp4
```

## Quality Guidelines

### Web Streaming
```bash
-c:v libx264 -preset medium -crf 23 -c:a aac -b:a 128k
```

### Mobile Devices
```bash
-c:v libx264 -preset medium -crf 26 -vf "scale=720:-2" -c:a aac -b:a 96k
```

### Archiving
```bash
-c:v libx265 -preset slow -crf 20 -c:a copy
```

### Fast Preview
```bash
-c:v libx264 -preset ultrafast -crf 28 -vf "scale=480:-2" -c:a aac -b:a 64k
```
