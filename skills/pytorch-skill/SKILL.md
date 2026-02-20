# PyTorch Skill

PyTorch深度学习工具，支持模型定义、训练循环和GPU管理。

## Use When

- 需要构建和训练深度学习模型
- 需要使用GPU进行加速训练
- 需要自定义神经网络架构
- 需要进行迁移学习
- 需要处理大规模数据集

## Out of Scope

- 传统机器学习任务（使用sklearn-skill）
- 预训练模型直接使用（使用huggingface-skill）
- 模型部署到生产环境
- 分布式多机训练

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

编辑 `config.json` 配置默认参数：

```json
{
  "device": "auto",
  "default_epochs": 10,
  "default_batch_size": 32,
  "default_lr": 0.001
}
```

## Usage

### 基本用法

```python
from skills.pytorch_skill.main import PyTorchSkill

skill = PyTorchSkill()

# 定义模型
model = skill.create_model(
    input_size=784,
    hidden_sizes=[256, 128],
    output_size=10,
    model_type="mlp"
)

# 训练模型
history = skill.train(
    model, train_loader, val_loader,
    epochs=10, lr=0.001
)
```

### 高级用法

查看 `examples/example.py` 获取完整示例。

## API Reference

### PyTorchSkill

- `create_model(input_size, hidden_sizes, output_size, model_type)` - 创建模型
- `train(model, train_loader, val_loader, epochs, lr)` - 训练模型
- `evaluate(model, test_loader)` - 评估模型
- `predict(model, data)` - 模型预测
- `save_model(model, path)` - 保存模型
- `load_model(path, model_class)` - 加载模型
- `get_device()` - 获取可用设备

## Testing

```bash
python test_skill.py
```

## License

MIT
