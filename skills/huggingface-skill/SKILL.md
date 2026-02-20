# Hugging Face Skill

Hugging Face模型管理工具，支持模型下载、Pipeline使用和数据集加载。

## Use When

- 需要下载和使用Hugging Face上的预训练模型
- 需要使用Transformers Pipeline进行快速推理
- 需要加载和处理Hugging Face数据集
- 需要进行文本分类、NER、问答等NLP任务
- 需要使用Tokenizers进行文本编码/解码

## Out of Scope

- 模型微调训练（使用pytorch-skill或sklearn-skill）
- 自定义模型架构设计
- 非Hugging Face生态的模型管理
- 模型部署到生产环境

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

编辑 `config.json` 配置默认参数：

```json
{
  "cache_dir": "./hf_cache",
  "default_model": "bert-base-chinese",
  "device": "auto"
}
```

## Usage

### 基本用法

```python
from skills.huggingface_skill.main import HuggingFaceSkill

skill = HuggingFaceSkill()

# 下载模型
skill.download_model("bert-base-chinese")

# 使用Pipeline进行推理
result = skill.pipeline_infer(
    task="sentiment-analysis",
    inputs="这是一个很好的产品！"
)
```

### 高级用法

查看 `examples/example.py` 获取完整示例。

## API Reference

### HuggingFaceSkill

- `download_model(model_name, cache_dir=None)` - 下载模型
- `pipeline_infer(task, inputs, model=None)` - Pipeline推理
- `load_dataset(dataset_name, split="train")` - 加载数据集
- `encode_text(tokenizer_name, text)` - 文本编码
- `decode_tokens(tokenizer_name, tokens)` - Token解码

## Testing

```bash
python test_skill.py
```

## License

MIT
