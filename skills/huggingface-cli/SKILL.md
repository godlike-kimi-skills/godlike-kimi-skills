# HuggingFace CLI Skill

一个强大的 HuggingFace Hub 命令行工具，让 Kimi 用户能够轻松搜索、下载和管理 AI 模型与数据集。

---

## 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [命令详解](#命令详解)
- [使用示例](#使用示例)
- [配置说明](#配置说明)
- [常见问题](#常见问题)

---

## 功能特性

### 🔍 智能搜索
- 支持模型搜索（按关键词、标签、任务类型）
- 支持数据集搜索
- 显示下载量、点赞数等统计信息

### ⬇️ 高速下载
- 支持断点续传
- 支持选择性下载（按文件类型过滤）
- 支持自定义缓存目录
- 显示下载进度和速度

### 📋 信息查询
- 查看模型/数据集详细信息
- 显示文件列表和元数据
- 查看标签和任务类型

### 🔐 Token 管理
- 安全登录/登出
- Token 本地加密存储
- 支持私有资源访问

### 💾 缓存管理
- 查看缓存使用情况
- 清理过期缓存
- 列出本地模型

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 Token（可选）

访问私有模型或下载 gated 模型需要 Token：

```bash
# 从 https://huggingface.co/settings/tokens 获取 Token
python main.py login --token your_token_here
```

### 3. 开始使用

```bash
# 搜索模型
python main.py search --query bert-base-chinese --limit 5

# 下载模型
python main.py download --model bert-base-chinese --local-dir ./models

# 查看模型信息
python main.py info --model bert-base-chinese
```

---

## 命令详解

### 🔍 search - 搜索模型

搜索 HuggingFace Hub 上的公开模型。

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--query, -q` | string | ✅ | 搜索关键词 |
| `--limit, -l` | int | ❌ | 结果数量限制，默认 10 |

**示例：**

```bash
# 搜索中文 BERT 模型
python main.py search --query bert-base-chinese

# 搜索 GPT 相关模型，限制 5 个结果
python main.py search --query gpt --limit 5

# 搜索特定任务模型
python main.py search --query "text-classification" --limit 10
```

**输出示例：**

```
============================================================
  🔍 搜索模型: 'bert-base-chinese'
============================================================

找到 3 个模型:

  1. bert-base-chinese
     📥 下载: 1,234,567 | ❤️ 点赞: 890
     🏷️ 标签: transformers, bert, chinese, pytorch
     🔧 任务: fill-mask

  2. hfl/chinese-bert-wwm-ext
     📥 下载: 567,890 | ❤️ 点赞: 456
     🏷️ 标签: transformers, bert, chinese, wwm
     🔧 任务: fill-mask
```

---

### 📥 download - 下载模型

下载指定模型到本地目录。

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--model, -m` | string | ✅ | 模型 ID |
| `--local-dir` | string | ❌ | 本地下载目录 |
| `--include` | array | ❌ | 包含的文件模式（如 `*.bin *.json`） |
| `--exclude` | array | ❌ | 排除的文件模式 |
| `--resume` | bool | ❌ | 断点续传，默认开启 |
| `--force` | bool | ❌ | 强制重新下载 |

**示例：**

```bash
# 下载完整模型
python main.py download --model bert-base-chinese --local-dir ./models/bert

# 只下载配置文件（用于快速预览）
python main.py download --model gpt2 \
    --local-dir ./models/gpt2 \
    --include "config.json" "tokenizer.json"

# 排除大文件（如 .bin 或 .safetensors）
python main.py download --model bert-base-chinese \
    --local-dir ./models/bert-lite \
    --exclude "*.bin" "*.safetensors"

# 指定缓存目录
python main.py download --model bert-base-chinese --cache-dir /path/to/cache
```

**输出示例：**

```
============================================================
  ⬇️  下载模型: bert-base-chinese
============================================================

ℹ️  目标目录: ./models/bert
✅ 模型下载完成!
ℹ️  保存位置: ./models/bert
ℹ️  总大小: 412.35 MB
```

---

### 📋 info - 模型信息

查看模型的详细信息和元数据。

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--model, -m` | string | ✅ | 模型 ID |

**示例：**

```bash
python main.py info --model bert-base-chinese
```

**输出示例：**

```
============================================================
  📋 模型信息: bert-base-chinese
============================================================

  🆔 ID: bert-base-chinese
  🔢 SHA: a1b2c3d4e5f6...
  📥 下载量: 1,234,567
  ❤️ 点赞数: 890
  🔧 任务类型: fill-mask
  📅 创建时间: 2020-01-15
  📝 最后修改: 2023-06-20

  🏷️ 标签:
     - transformers
     - bert
     - chinese
     - pytorch

  📁 文件列表 (6 个文件):
     - config.json
     - pytorch_model.bin
     - tokenizer.json
     - tokenizer_config.json
     - vocab.txt
     - README.md
```

---

### 🔐 login - 登录

使用 HuggingFace Token 登录，用于访问私有资源。

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--token, -t` | string | ✅ | HuggingFace 访问令牌 |

**示例：**

```bash
python main.py login --token hf_xxxxxxxxxxxxxxxxxxxx
```

> 💡 **获取 Token：** 访问 https://huggingface.co/settings/tokens

---

### 🚪 logout - 登出

登出 HuggingFace，删除本地存储的 Token。

```bash
python main.py logout
```

---

### 💾 cache - 缓存信息

查看本地缓存的使用情况。

```bash
python main.py cache
```

**输出示例：**

```
============================================================
  💾 缓存信息
============================================================

  📁 缓存根目录: /home/user/.cache/huggingface
  🤖 模型缓存: /home/user/.cache/huggingface/hub
  📊 数据集缓存: /home/user/.cache/huggingface/datasets
  🔑 Token文件: 存在

  💽 空间使用:
     模型缓存: 2.34 GB
     数据集缓存: 567.89 MB
     总计: 2.89 GB
```

---

### 📚 list - 列出本地模型

显示所有已下载到本地的模型。

```bash
python main.py list
```

**输出示例：**

```
============================================================
  📚 本地模型
============================================================

共 3 个本地模型:

  1. bert-base-chinese (412.35 MB)
  2. gpt2 (523.89 MB)
  3. t5-small (234.12 MB)
```

---

## 数据集命令

### dataset-search - 搜索数据集

```bash
python main.py dataset-search --query glue --limit 5
```

### dataset-download - 下载数据集

```bash
python main.py dataset-download --dataset glue --local-dir ./datasets/glue
```

### dataset-info - 数据集信息

```bash
python main.py dataset-info --dataset glue
```

---

## 使用示例

### 场景 1：快速下载 BERT 进行文本分类

```bash
# 1. 搜索中文 BERT 模型
python main.py search --query "chinese bert classification" --limit 3

# 2. 下载选中的模型
python main.py download --model bert-base-chinese --local-dir ./my-models/bert

# 3. 查看下载的模型
python main.py list
```

### 场景 2：下载特定任务的数据集

```bash
# 下载 GLUE 基准测试数据集
python main.py dataset-download --dataset glue --local-dir ./datasets/glue

# 只下载特定子集
python main.py dataset-download --dataset glue \
    --local-dir ./datasets/glue-sst2 \
    --include "*sst2*"
```

### 场景 3：管理缓存空间

```bash
# 查看缓存使用情况
python main.py cache

# 清理缓存（危险操作，请谨慎）
# python main.py cache --force
```

### 场景 4：访问私有模型

```bash
# 1. 登录
python main.py login --token hf_your_private_token

# 2. 下载私有模型
python main.py download --model your-username/private-model --local-dir ./private

# 3. 完成后登出（可选）
python main.py logout
```

---

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `HF_HOME` | HuggingFace 主目录 | `~/.cache/huggingface` |
| `HF_HUB_CACHE` | 模型缓存目录 | `~/.cache/huggingface/hub` |
| `HF_DATASETS_CACHE` | 数据集缓存目录 | `~/.cache/huggingface/datasets` |
| `HF_TOKEN` | 访问令牌（优先于本地存储） | - |

### 配置文件

Token 默认存储在：

- **Linux/macOS**: `~/.huggingface/token`
- **Windows**: `%USERPROFILE%\.huggingface\token`

---

## 常见问题

### Q: 下载速度慢怎么办？

**A:** 可以尝试以下方法：

1. 使用镜像源（如 hf-mirror.com）
2. 设置代理：`export HTTPS_PROXY=http://proxy:port`
3. 只下载需要的文件，使用 `--include` 参数

### Q: 如何下载特定版本的模型？

**A:** 使用模型 ID 时添加版本号：

```bash
python main.py info --model bert-base-chinese@main  # 主分支
python main.py info --model bert-base-chinese@v1.0.0  # 特定标签
```

### Q: 下载中断后如何恢复？

**A:** 默认启用断点续传，重新运行相同命令即可：

```bash
python main.py download --model bert-base-chinese --local-dir ./models
```

### Q: Token 保存在哪里？安全吗？

**A:** Token 保存在本地 `~/.huggingface/token`，文件权限设置为仅当前用户可读。

### Q: 如何批量下载多个模型？

**A:** 可以编写简单的 shell 脚本：

```bash
#!/bin/bash
models=("bert-base-chinese" "gpt2" "t5-small")

for model in "${models[@]}"; do
    echo "Downloading $model..."
    python main.py download --model "$model" --local-dir "./models/$model"
done
```

---

## 参考链接

- [HuggingFace Hub 文档](https://huggingface.co/docs/hub)
- [huggingface_hub Python 库](https://huggingface.co/docs/huggingface_hub)
- [模型搜索](https://huggingface.co/models)
- [数据集搜索](https://huggingface.co/datasets)

---

**版本**: 1.0.0  
**许可证**: MIT  
**作者**: Kimi Code CLI
