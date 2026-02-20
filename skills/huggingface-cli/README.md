# HuggingFace CLI Skill

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Hub-yellow.svg)

**[中文](#中文) | [English](#english)**

简化 HuggingFace 模型和数据集的管理，让 AI 资源触手可及。

</div>

---

<a name="中文"></a>
## 中文

### 🚀 功能特性

- 🔍 **智能搜索** - 快速搜索模型和数据集，显示下载量、点赞数等统计
- ⬇️ **高速下载** - 支持断点续传、选择性下载、文件过滤
- 📋 **信息查询** - 查看详细的模型/数据集元数据
- 🔐 **Token 管理** - 安全的登录/登出，支持私有资源访问
- 💾 **缓存管理** - 查看缓存使用情况，清理过期文件
- 📚 **本地管理** - 列出和管理已下载的本地模型

### 📦 快速安装

```bash
# 克隆仓库
git clone https://github.com/your-repo/huggingface-cli-skill.git
cd huggingface-cli-skill

# 安装依赖
pip install -r requirements.txt
```

### 📝 快速开始

```bash
# 1. 搜索模型
python main.py search --query bert-base-chinese --limit 5

# 2. 下载模型
python main.py download --model bert-base-chinese --local-dir ./models

# 3. 查看模型信息
python main.py info --model bert-base-chinese
```

### 📖 详细文档

查看 [SKILL.md](./SKILL.md) 获取完整的命令参考和使用示例。

### 🎯 使用场景

- **NLP 开发者**: 快速下载 BERT、GPT、T5 等预训练模型
- **数据科学家**: 获取 GLUE、SQuAD 等标准数据集
- **AI 研究者**: 管理和分享实验模型
- **Kimi 用户**: 无缝集成到 Kimi Code CLI 工作流

### 🔧 支持的命令

| 命令 | 说明 |
|------|------|
| `search` | 搜索模型 |
| `download` | 下载模型 |
| `info` | 模型信息 |
| `login` | 登录 HuggingFace |
| `logout` | 登出 HuggingFace |
| `cache` | 缓存信息 |
| `list` | 列出本地模型 |
| `dataset-search` | 搜索数据集 |
| `dataset-download` | 下载数据集 |
| `dataset-info` | 数据集信息 |

---

<a name="english"></a>
## English

### 🚀 Features

- 🔍 **Smart Search** - Quickly search models and datasets with download/likes statistics
- ⬇️ **Fast Download** - Resume interrupted downloads, selective file filtering
- 📋 **Info Query** - View detailed model/dataset metadata
- 🔐 **Token Management** - Secure login/logout with private resource access
- 💾 **Cache Management** - Monitor cache usage, clean up old files
- 📚 **Local Management** - List and manage downloaded local models

### 📦 Quick Install

```bash
# Clone the repository
git clone https://github.com/your-repo/huggingface-cli-skill.git
cd huggingface-cli-skill

# Install dependencies
pip install -r requirements.txt
```

### 📝 Quick Start

```bash
# 1. Search for models
python main.py search --query bert-base-uncased --limit 5

# 2. Download a model
python main.py download --model bert-base-uncased --local-dir ./models

# 3. View model info
python main.py info --model bert-base-uncased
```

### 📖 Full Documentation

See [SKILL.md](./SKILL.md) for complete command reference and usage examples.

### 🎯 Use Cases

- **NLP Developers**: Quickly download BERT, GPT, T5 pretrained models
- **Data Scientists**: Access GLUE, SQuAD standard datasets
- **AI Researchers**: Manage and share experimental models
- **Kimi Users**: Seamlessly integrate into Kimi Code CLI workflow

### 🔧 Supported Commands

| Command | Description |
|---------|-------------|
| `search` | Search for models |
| `download` | Download models |
| `info` | Model information |
| `login` | Login to HuggingFace |
| `logout` | Logout from HuggingFace |
| `cache` | Cache information |
| `list` | List local models |
| `dataset-search` | Search for datasets |
| `dataset-download` | Download datasets |
| `dataset-info` | Dataset information |

---

## 📊 Project Structure

```
huggingface-cli/
├── main.py              # Main CLI implementation (~400 lines)
├── skill.json           # Skill configuration
├── requirements.txt     # Python dependencies
├── SKILL.md            # Detailed documentation (Chinese)
├── README.md           # This file (Bilingual)
├── LICENSE             # MIT License
└── tests/
    └── test_basic.py   # Basic test suite
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/test_basic.py -v

# Or run directly
python tests/test_basic.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [HuggingFace](https://huggingface.co/) - For the amazing model hub
- [huggingface_hub](https://github.com/huggingface/huggingface_hub) - Python library
- [Kimi Code CLI](https://kimi.com) - For the skill framework

## 📞 Support

If you encounter any issues or have questions:

- 🐛 [Open an Issue](https://github.com/your-repo/huggingface-cli-skill/issues)
- 📧 Email: support@example.com
- 💬 [Discussions](https://github.com/your-repo/huggingface-cli-skill/discussions)

---

<div align="center">

**Made with ❤️ for the AI Community**

[⬆ Back to Top](#huggingface-cli-skill)

</div>
