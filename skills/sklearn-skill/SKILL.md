# Scikit-Learn Skill

Scikit-Learn机器学习工具，支持模型训练、评估和预处理。

## Use When

- 需要进行传统的机器学习任务（分类、回归、聚类）
- 需要进行数据预处理和特征工程
- 需要评估模型性能（交叉验证、网格搜索）
- 需要使用经典的ML算法（SVM、随机森林、梯度提升等）
- 需要进行降维和特征选择

## Out of Scope

- 深度学习任务（使用pytorch-skill）
- 大规模分布式训练
- GPU加速训练（sklearn本身不支持）
- 神经网络架构设计

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

编辑 `config.json` 配置默认参数：

```json
{
  "random_state": 42,
  "test_size": 0.2,
  "n_jobs": -1
}
```

## Usage

### 基本用法

```python
from skills.sklearn_skill.main import SklearnSkill

skill = SklearnSkill()

# 训练分类模型
model = skill.train_classifier(
    X_train, y_train,
    algorithm="random_forest"
)

# 评估模型
metrics = skill.evaluate_model(model, X_test, y_test)
```

### 高级用法

查看 `examples/example.py` 获取完整示例。

## API Reference

### SklearnSkill

- `train_classifier(X, y, algorithm, **params)` - 训练分类器
- `train_regressor(X, y, algorithm, **params)` - 训练回归器
- `train_cluster(X, algorithm, **params)` - 训练聚类模型
- `evaluate_model(model, X, y, task_type)` - 评估模型
- `cross_validate(model, X, y, cv)` - 交叉验证
- `grid_search(model, param_grid, X, y)` - 网格搜索
- `preprocess_data(X, method)` - 数据预处理

## Testing

```bash
python test_skill.py
```

## License

MIT
