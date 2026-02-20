# OpenAI API Skill

OpenAI API调用工具，支持Chat/Completion API、Embedding和图像生成。

## Use When

- 需要调用OpenAI GPT模型进行对话
- 需要使用文本补全功能
- 需要生成文本嵌入向量
- 需要使用DALL-E生成图像
- 需要使用Whisper进行语音识别

## Out of Scope

- 本地模型部署（使用pytorch-skill）
- 非OpenAI的API调用
- 流式响应处理的高级定制
- 自定义模型微调

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

编辑 `config.json` 配置API密钥和默认参数：

```json
{
  "api_key": "your-api-key-here",
  "base_url": "https://api.openai.com/v1",
  "default_model": "gpt-3.5-turbo",
  "default_temperature": 0.7,
  "default_max_tokens": 150
}
```

或使用环境变量：
```bash
export OPENAI_API_KEY="your-api-key"
```

## Usage

### 基本用法

```python
from skills.openai_api_skill.main import OpenAISkill

skill = OpenAISkill()

# 对话
response = skill.chat(
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

# 生成嵌入
embeddings = skill.create_embedding("Hello world")
```

### 高级用法

查看 `examples/example.py` 获取完整示例。

## API Reference

### OpenAISkill

- `chat(messages, model, temperature, max_tokens)` - 对话接口
- `complete(prompt, model, temperature)` - 文本补全
- `create_embedding(text, model)` - 生成嵌入
- `generate_image(prompt, size, quality)` - 生成图像
- `transcribe_audio(audio_file, model)` - 语音转文字

## Testing

```bash
python test_skill.py
```

## License

MIT
