# ElevenLabs Skill - TTS语音合成工具

使用ElevenLabs API的文本转语音工具，支持语音生成、声音克隆和多语言合成。

## 功能特性

- 🔊 **高质量TTS** - 最先进的神经语音合成
- 🎭 **声音克隆** - 从音频样本克隆声音
- 🌍 **多语言支持** - 支持29+种语言
- 🎚️ **声音设置** - 控制稳定性、清晰度和风格
- 📁 **多格式输出** - MP3、WAV等多种格式
- 🔊 **流式播放** - 实时流式音频生成
- ⏱️ **时间戳** - 生成词级时间戳
- 📊 **用量追踪** - 监控API使用情况

## 安装依赖

```bash
pip install -r requirements.txt
```

依赖列表：
- elevenlabs >= 1.0.0
- requests >= 2.31.0
- python-dotenv >= 1.0.0
- pydub >= 0.25.1

## 快速开始

### 1. 设置API密钥

```bash
export ELEVENLABS_API_KEY="your_api_key_here"
```

或创建 `.env` 文件：
```env
ELEVENLABS_API_KEY=your_api_key_here
```

获取API密钥：[ElevenLabs设置页面](https://elevenlabs.io/app/settings/api-keys)

### 2. 列出可用声音

```bash
python main.py voices
```

### 3. 文本转语音

```bash
python main.py tts "你好，世界！" --voice Rachel -o output.mp3
```

### 4. 文件转语音

```bash
python main.py file story.txt --voice Adam -o story.mp3
```

### 5. 查看用户信息

```bash
python main.py user
```

## 编程使用

```python
from main import ElevenLabsManager

# 初始化管理器
manager = ElevenLabsManager(api_key="your_api_key")

# 列出可用声音
voices = manager.get_voices()
for voice in voices:
    print(f"{voice.voice_id}: {voice.name}")

# 文本转语音
result = manager.text_to_speech(
    text="这是一个测试。",
    voice_id="Rachel",
    model="eleven_multilingual_v2",
    stability=0.5,
    similarity_boost=0.75,
    style=0.0,
    save=True,
    filename="output.mp3"
)

print(f"已保存到: {result.file_path}")
print(f"估计时长: {result.duration_estimate}秒")

# 长文本（自动分割处理）
long_text = "很长的文本..." * 100
results = manager.text_to_speech_long(
    text=long_text,
    voice_id="Rachel"
)

# 流式生成
stream = manager.stream_text_to_speech(
    text="流式测试",
    voice_id="Adam"
)

# 克隆声音
new_voice_id = manager.clone_voice(
    name="我的声音",
    description="克隆的声音样本",
    audio_files=["sample1.mp3", "sample2.mp3"]
)

# 使用克隆的声音
result = manager.text_to_speech(
    text="使用克隆的声音说话！",
    voice_id=new_voice_id
)

# 生成带时间戳的音频
timestamp_data = manager.generate_with_timestamps(
    text="你好世界",
    voice_id="Rachel"
)
print(timestamp_data["alignment"])

# 获取用户信息
info = manager.get_user_info()
print(f"订阅级别: {info['subscription_tier']}")
print(f"字符用量: {info['character_count']}/{info['character_limit']}")
print(f"使用比例: {info['character_usage_percentage']:.1f}%")
```

## 声音设置参数

| 参数 | 范围 | 默认值 | 描述 |
|------|------|--------|------|
| stability | 0.0-1.0 | 0.5 | 声音一致性 |
| similarity_boost | 0.0-1.0 | 0.75 | 与原声相似度 |
| style | 0.0-1.0 | 0.0 | 说话风格强度 |
| use_speaker_boost | bool | True | 增强说话者清晰度 |

## 可用模型

| 模型 | 描述 | 语言 |
|------|------|------|
| eleven_multilingual_v2 | 最新多语言模型 | 29+种语言 |
| eleven_multilingual_v1 | 第一代多语言模型 | 9种语言 |
| eleven_monolingual_v1 | 英语优化模型 | 仅英语 |
| eleven_turbo_v2 | 快速生成模型 | 29+种语言 |

## 声音克隆

### 要求

- 清晰的音频样本
- 最少1分钟总音频时长
- 一致的说话风格
- 最小化背景噪音

### 最佳实践

1. 使用高质量录音
2. 包含不同的语音模式
3. 避免重叠的声音
4. 录音环境与目标使用场景匹配

```python
# 从文件克隆
voice_id = manager.clone_voice(
    name="自定义声音",
    description="专业旁白",
    audio_files=["sample1.wav", "sample2.wav", "sample3.wav"],
    labels={"gender": "male", "age": "adult"}
)

# 使用字节数据克隆
with open("voice.mp3", "rb") as f:
    audio_data = f.read()

voice_id = manager.clone_voice(
    name="克隆声音",
    description="克隆描述",
    audio_files=[audio_data]
)
```

## 配置

创建 `.env` 文件：

```env
# 必需
ELEVENLABS_API_KEY=your_api_key_here

# 可选默认值
DEFAULT_VOICE_ID=Rachel
DEFAULT_MODEL=eleven_multilingual_v2
OUTPUT_FORMAT=mp3_44100_128
OUTPUT_DIR=./audio_output

# 声音设置
VOICE_STABILITY=0.5
VOICE_CLARITY=0.75
VOICE_STYLE=0.0
```

## 输出格式

| 格式 | 质量 | 适用场景 |
|------|------|----------|
| mp3_44100_128 | 128kbps MP3 | 标准质量 |
| mp3_44100_64 | 64kbps MP3 | 较小文件 |
| mp3_44100_32 | 32kbps MP3 | 最小体积 |
| pcm_16000 | 16kHz WAV | 音频处理 |
| pcm_22050 | 22kHz WAV | 更好质量 |
| pcm_24000 | 24kHz WAV | 最佳质量 |
| ulaw_8000 | 8kHz μ-law | 电话语音 |

## 命令行参考

### voices - 列出声音
```bash
python main.py voices
```

### models - 列出模型
```bash
python main.py models
```

### user - 用户信息
```bash
python main.py user
```

### tts - 文本转语音
```bash
python main.py tts "要转换的文本" \
  --voice Rachel \
  --model eleven_multilingual_v2 \
  --stability 0.5 \
  --similarity 0.75 \
  --style 0.0 \
  -o output.mp3
```

### file - 文件转语音
```bash
python main.py file input.txt \
  --voice Adam \
  --model eleven_multilingual_v2 \
  -o output.mp3
```

### clone - 克隆声音
```bash
python main.py clone "声音名称" \
  sample1.mp3 sample2.mp3 sample3.mp3 \
  --desc "声音描述"
```

## API参考

### ElevenLabsManager

#### 构造函数
```python
manager = ElevenLabsManager(api_key=None)
```

#### 方法

| 方法 | 描述 |
|------|------|
| `get_voices(show_all=False)` | 获取可用声音 |
| `text_to_speech(text, ...)` | 文本转语音 |
| `stream_text_to_speech(text, ...)` | 流式TTS |
| `clone_voice(name, description, audio_files)` | 克隆声音 |
| `edit_voice(voice_id, ...)` | 编辑声音 |
| `delete_voice(voice_id)` | 删除声音 |
| `generate_with_timestamps(text, ...)` | 生成带时间戳 |
| `get_models()` | 获取模型列表 |
| `get_user_info()` | 获取用户信息 |
| `split_long_text(text, max_length)` | 分割长文本 |
| `text_to_speech_long(text, ...)` | 长文本TTS |

## 价格说明

- 按请求的字符数计费
- 免费版：每月10,000字符
- 付费版提供更高额度
- 声音克隆需要付费计划

### 字符计算规则

- 包括所有文本字符
- 空格也算作字符
- 中文字符与英文字母同样计费

## 使用场景

1. **有声读物** - 将电子书转换为有声书
2. **播客制作** - 快速生成播客音频
3. **视频配音** - 为视频生成旁白
4. **游戏开发** - 为角色生成语音
5. **辅助功能** - 为视障人士提供语音服务
6. **语言学习** - 生成不同语言的发音

## 测试

```bash
python test_main.py
```

测试覆盖率：
- API密钥验证
- 声音列表获取
- TTS生成
- 长文本分割
- 声音克隆
- 用户信息获取

## 相关链接

- [ElevenLabs官网](https://elevenlabs.io)
- [API文档](https://elevenlabs.io/docs)
- [声音库](https://elevenlabs.io/voice-library)
- [定价信息](https://elevenlabs.io/pricing)

## 许可证

MIT License
