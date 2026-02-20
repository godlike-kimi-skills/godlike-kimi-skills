# YouTube Transcript Skill - YouTube字幕提取工具

提取YouTube视频字幕、翻译并生成摘要。支持多种输出格式：文本、JSON、SRT、VTT。

## 功能特性

- 🎯 **提取字幕** - 从任何YouTube视频获取字幕
- 🌍 **多语言支持** - 自动查找可用语言
- 🔄 **翻译功能** - 将字幕翻译为目标语言
- 📝 **多种格式** - 输出为文本、JSON、SRT、VTT或TSV
- 🔍 **关键词搜索** - 在字幕中搜索关键词
- ⏱️ **时间段提取** - 提取特定时间段的内容
- 📊 **摘要生成** - 自动生成文本摘要

## 安装依赖

```bash
pip install -r requirements.txt
```

依赖列表：
- youtube-transcript-api >= 0.6.0
- requests >= 2.31.0
- urllib3 >= 2.0.0
- textblob >= 0.17.1

## 快速开始

### 1. 提取字幕

```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### 2. 查看可用语言

```bash
python main.py "视频URL" --list-langs
```

### 3. 保存为SRT字幕文件

```bash
python main.py "视频URL" --format srt -o subtitles.srt
```

### 4. 翻译字幕

```bash
python main.py "视频URL" --translate zh
```

### 5. 生成摘要

```bash
python main.py "视频URL" --summary
```

### 6. 搜索关键词

```bash
python main.py "视频URL" --search "关键词"
```

### 7. 提取时间段

```bash
python main.py "视频URL" --start 60 --end 120
```

## 编程使用

```python
from main import YouTubeTranscriptExtractor

# 初始化提取器（可选代理）
extractor = YouTubeTranscriptExtractor(proxy="http://127.0.0.1:7890")

# 从URL提取视频ID
video_id = extractor.extract_video_id("https://youtu.be/dQw4w9WgXcQ")

# 列出可用语言
languages = extractor.get_available_languages(video_id)
for lang in languages:
    print(f"{lang['language_code']}: {lang['language_name']}")

# 提取字幕
result = extractor.extract_transcript(
    video_id=video_id,
    languages=["zh", "en"]  # 按优先级
)

print(f"语言: {result.language_name}")
print(f"文本: {result.full_text[:500]}")
print(f"片段数: {len(result.segments)}")

# 格式化为SRT
srt_content = extractor.format_transcript(result, "srt")
with open("subtitles.srt", "w", encoding="utf-8") as f:
    f.write(srt_content)

# 翻译字幕
translated = extractor.translate_transcript(video_id, target_language="zh")

# 搜索关键词
matches = extractor.search_in_transcript(result, "重要概念")
for match in matches:
    print(f"[{match['formatted_time']}] {match['text']}")
    print(f"上下文: {match['context'][:100]}...")

# 提取时间段
clip = extractor.extract_with_timestamps(video_id, start_time=60, end_time=120)

# 生成摘要
summary = extractor.generate_summary(result, max_sentences=5)
print("摘要:", summary)
```

## 支持的URL格式

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`
- 直接视频ID: `VIDEO_ID`

## 输出格式

| 格式 | 描述 | 适用场景 |
|------|------|----------|
| text | 纯文本 | 阅读、分析 |
| json | 结构化JSON | 数据处理 |
| srt | SubRip字幕 | 视频播放器 |
| vtt | WebVTT字幕 | 网页播放器 |
| tsv | 制表符分隔值 | 电子表格 |

## 命令行参考

### 基本用法
```bash
python main.py "视频URL或ID"
```

### 参数说明

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `url` | YouTube视频URL或ID | 必需 |
| `--proxy` | 代理地址 | 无 |
| `--lang` | 语言优先级列表 | zh,zh-CN,en |
| `--format` | 输出格式 | text |
| `--translate` | 翻译到目标语言 | 无 |
| `--output`, `-o` | 输出文件 | 无 |
| `--summary` | 生成摘要 | False |
| `--search` | 搜索关键词 | 无 |
| `--start` | 开始时间(秒) | 无 |
| `--end` | 结束时间(秒) | 无 |
| `--list-langs` | 列出可用语言 | False |

## 配置

创建 `.env` 文件：

```env
# 代理设置（可选）
PROXY=http://127.0.0.1:7890

# 默认字幕语言（逗号分隔的优先级列表）
DEFAULT_LANGUAGES=zh,zh-CN,zh-TW,en

# 是否自动翻译
AUTO_TRANSLATE=false
TARGET_LANGUAGE=zh

# 输出格式：text, json, srt, vtt
OUTPUT_FORMAT=text

# 摘要最大字数
SUMMARY_MAX_LENGTH=500
```

## API参考

### YouTubeTranscriptExtractor

#### 构造函数
```python
extractor = YouTubeTranscriptExtractor(proxy=None)
```

#### 方法

| 方法 | 描述 |
|------|------|
| `extract_video_id(url)` | 从URL提取视频ID |
| `get_available_languages(video_id)` | 获取可用字幕语言 |
| `extract_transcript(video_id, languages)` | 提取字幕 |
| `translate_transcript(video_id, target_language)` | 翻译字幕 |
| `format_transcript(result, format_type)` | 格式化输出 |
| `generate_summary(result, max_sentences)` | 生成摘要 |
| `search_in_transcript(result, keyword)` | 搜索关键词 |
| `extract_with_timestamps(video_id, start, end)` | 提取时间段 |

## 使用场景

1. **学习笔记** - 提取教育视频字幕做笔记
2. **内容创作** - 获取视频文案进行二次创作
3. **翻译工作** - 翻译国外视频字幕
4. **数据分析** - 分析视频内容关键词
5. **无障碍访问** - 为听障人士提供字幕

## 限制说明

- 仅适用于有字幕/字幕的视频
- 部分视频可能禁用了第三方字幕访问
- 自动生成字幕的质量因视频而异
- 翻译功能依赖YouTube的翻译服务

## 测试

```bash
python test_main.py
```

测试覆盖率：
- URL解析
- 字幕提取（mock测试）
- 格式转换
- 搜索功能
- 摘要生成

## 许可证

MIT License
