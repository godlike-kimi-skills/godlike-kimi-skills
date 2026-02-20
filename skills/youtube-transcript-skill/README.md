# YouTube Transcript Skill

Extract YouTube video transcripts, translate, and generate summaries. Supports multiple output formats including text, JSON, SRT, and VTT.

## Features

- 🎯 **Extract Transcripts** - Get subtitles from any YouTube video
- 🌍 **Multi-language Support** - Automatically find available languages
- 🔄 **Translation** - Translate transcripts to your preferred language
- 📝 **Multiple Formats** - Output as text, JSON, SRT, VTT, or TSV
- 🔍 **Search** - Search for keywords in transcripts
- ⏱️ **Time Range** - Extract specific time segments
- 📊 **Summarization** - Generate text summaries

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Extract Transcript

```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### List Available Languages

```bash
python main.py "VIDEO_URL" --list-langs
```

### Save as SRT

```bash
python main.py "VIDEO_URL" --format srt -o subtitles.srt
```

### Translate

```bash
python main.py "VIDEO_URL" --translate zh
```

### Generate Summary

```bash
python main.py "VIDEO_URL" --summary
```

### Search in Transcript

```bash
python main.py "VIDEO_URL" --search "keyword"
```

### Extract Time Range

```bash
python main.py "VIDEO_URL" --start 60 --end 120
```

## Programmatic Usage

```python
from main import YouTubeTranscriptExtractor

# Initialize extractor
extractor = YouTubeTranscriptExtractor(proxy="http://127.0.0.1:7890")

# Extract video ID from URL
video_id = extractor.extract_video_id("https://youtu.be/dQw4w9WgXcQ")

# List available languages
languages = extractor.get_available_languages(video_id)
for lang in languages:
    print(f"{lang['language_code']}: {lang['language_name']}")

# Extract transcript
result = extractor.extract_transcript(
    video_id=video_id,
    languages=["zh", "en"]  # Priority order
)

print(f"Language: {result.language_name}")
print(f"Text: {result.full_text[:500]}")

# Format output
srt_content = extractor.format_transcript(result, "srt")
json_content = extractor.format_transcript(result, "json")

# Translate
translated = extractor.translate_transcript(video_id, target_language="zh")

# Search
matches = extractor.search_in_transcript(result, "important keyword")
for match in matches:
    print(f"[{match['formatted_time']}] {match['text']}")

# Extract time range
clip = extractor.extract_with_timestamps(video_id, start_time=60, end_time=120)

# Generate summary
summary = extractor.generate_summary(result, max_sentences=5)
print(summary)
```

## Supported URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`
- Direct video ID: `VIDEO_ID`

## Output Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| text | Plain text | Reading, analysis |
| json | Structured JSON | Data processing |
| srt | SubRip subtitle | Video players |
| vtt | WebVTT subtitle | Web players |
| tsv | Tab-separated values | Spreadsheets |

## Configuration

Create a `.env` file:

```env
# Proxy settings (optional)
PROXY=http://127.0.0.1:7890

# Default language priority
DEFAULT_LANGUAGES=zh,zh-CN,zh-TW,en

# Auto-translate settings
AUTO_TRANSLATE=false
TARGET_LANGUAGE=zh

# Default output format
OUTPUT_FORMAT=text
```

## API Reference

### YouTubeTranscriptExtractor

#### Constructor
```python
extractor = YouTubeTranscriptExtractor(proxy=None)
```

#### Methods

| Method | Description |
|--------|-------------|
| `extract_video_id(url)` | Extract video ID from URL |
| `get_available_languages(video_id)` | List available subtitle languages |
| `extract_transcript(video_id, languages)` | Extract transcript |
| `translate_transcript(video_id, target_language)` | Translate transcript |
| `format_transcript(result, format_type)` | Format output |
| `generate_summary(result, max_sentences)` | Generate summary |
| `search_in_transcript(result, keyword)` | Search for keywords |
| `extract_with_timestamps(video_id, start, end)` | Extract time range |

## Testing

```bash
python test_main.py
```

## Limitations

- Only works with videos that have captions/subtitles
- Some videos may have disabled third-party access to transcripts
- Auto-generated captions quality varies

## License

MIT
