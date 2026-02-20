# ElevenLabs Skill

Text-to-Speech (TTS) synthesis tool using ElevenLabs API. Supports voice generation, voice cloning, and multi-language synthesis.

## Features

- 🔊 **High-Quality TTS** - State-of-the-art neural speech synthesis
- 🎭 **Voice Cloning** - Clone voices from audio samples
- 🌍 **Multi-language** - Support for 29+ languages
- 🎚️ **Voice Settings** - Control stability, clarity, and style
- 📁 **Multiple Formats** - MP3, WAV, and more output formats
- 🔊 **Streaming** - Stream audio for real-time playback
- ⏱️ **Timestamps** - Generate word-level timestamps
- 📊 **Usage Tracking** - Monitor your API usage

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Set API Key

```bash
export ELEVENLABS_API_KEY="your_api_key_here"
```

Or create a `.env` file:
```env
ELEVENLABS_API_KEY=your_api_key_here
```

### List Available Voices

```bash
python main.py voices
```

### Text to Speech

```bash
python main.py tts "Hello, world!" --voice Rachel -o output.mp3
```

### Convert File to Speech

```bash
python main.py file story.txt --voice Adam -o story.mp3
```

### Check User Info

```bash
python main.py user
```

## Programmatic Usage

```python
from main import ElevenLabsManager

# Initialize manager
manager = ElevenLabsManager(api_key="your_api_key")

# List available voices
voices = manager.get_voices()
for voice in voices:
    print(f"{voice.voice_id}: {voice.name}")

# Text to speech
result = manager.text_to_speech(
    text="Hello, this is a test.",
    voice_id="Rachel",
    model="eleven_multilingual_v2",
    stability=0.5,
    similarity_boost=0.75,
    style=0.0
)

# Save to file
result.save("output.mp3")

# Long text (auto-split)
results = manager.text_to_speech_long(
    text="Very long text..." * 100,
    voice_id="Rachel"
)

# Stream audio
stream = manager.stream_text_to_speech(
    text="Streaming test",
    voice_id="Adam"
)

# Clone voice
new_voice_id = manager.clone_voice(
    name="My Voice",
    description="Cloned from samples",
    audio_files=["sample1.mp3", "sample2.mp3"]
)

# Generate with timestamps
timestamp_data = manager.generate_with_timestamps(
    text="Hello world",
    voice_id="Rachel"
)

# Get user info
info = manager.get_user_info()
print(f"Usage: {info['character_count']}/{info['character_limit']}")
```

## Voice Settings

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| stability | 0.0-1.0 | 0.5 | Voice consistency |
| similarity_boost | 0.0-1.0 | 0.75 | Similarity to original |
| style | 0.0-1.0 | 0.0 | Speaking style intensity |
| use_speaker_boost | bool | True | Enhance speaker clarity |

## Available Models

| Model | Description | Languages |
|-------|-------------|-----------|
| eleven_multilingual_v2 | Latest multilingual model | 29+ languages |
| eleven_multilingual_v1 | First generation multilingual | 9 languages |
| eleven_monolingual_v1 | English optimized | English only |
| eleven_turbo_v2 | Fast generation | 29+ languages |

## Voice Cloning

### Requirements

- Clear audio samples
- Minimum 1 minute total audio
- Consistent speaking style
- Minimal background noise

### Best Practices

1. Use high-quality recordings
2. Include varied speech patterns
3. Avoid overlapping voices
4. Match recording environment to target use

```python
# Clone from files
voice_id = manager.clone_voice(
    name="Custom Voice",
    description="Professional narrator",
    audio_files=["sample1.wav", "sample2.wav"],
    labels={"gender": "male", "age": "adult"}
)

# Use cloned voice
result = manager.text_to_speech(
    text="Using my cloned voice!",
    voice_id=voice_id
)
```

## Configuration

Create a `.env` file:

```env
# Required
ELEVENLABS_API_KEY=your_api_key_here

# Optional defaults
DEFAULT_VOICE_ID=Rachel
DEFAULT_MODEL=eleven_multilingual_v2
OUTPUT_FORMAT=mp3_44100_128
OUTPUT_DIR=./audio_output

# Voice settings
VOICE_STABILITY=0.5
VOICE_CLARITY=0.75
VOICE_STYLE=0.0
```

## Output Formats

| Format | Quality | Use Case |
|--------|---------|----------|
| mp3_44100_128 | 128kbps MP3 | Standard quality |
| mp3_44100_64 | 64kbps MP3 | Smaller files |
| mp3_44100_32 | 32kbps MP3 | Minimum size |
| pcm_16000 | 16kHz WAV | Processing |
| pcm_22050 | 22kHz WAV | Better quality |
| pcm_24000 | 24kHz WAV | Best quality |
| ulaw_8000 | 8kHz μ-law | Telephony |

## Command Line Reference

### voices
List all available voices
```bash
python main.py voices
```

### models
List available models
```bash
python main.py models
```

### user
Show user subscription info
```bash
python main.py user
```

### tts
Convert text to speech
```bash
python main.py tts "Text to speak" \
  --voice Rachel \
  --model eleven_multilingual_v2 \
  --stability 0.5 \
  --similarity 0.75 \
  --style 0.0 \
  -o output.mp3
```

### file
Convert file to speech
```bash
python main.py file input.txt \
  --voice Adam \
  --model eleven_multilingual_v2 \
  -o output.mp3
```

### clone
Clone a voice from audio files
```bash
python main.py clone "Voice Name" \
  sample1.mp3 sample2.mp3 sample3.mp3 \
  --desc "Description of the voice"
```

## Testing

```bash
python test_main.py
```

## Pricing Notes

- Characters are counted per request
- Free tier: 10,000 characters/month
- Paid tiers available for higher volumes
- Voice cloning requires paid plan

## License

MIT

## Links

- [ElevenLabs Website](https://elevenlabs.io)
- [API Documentation](https://elevenlabs.io/docs)
- [Voice Library](https://elevenlabs.io/voice-library)
