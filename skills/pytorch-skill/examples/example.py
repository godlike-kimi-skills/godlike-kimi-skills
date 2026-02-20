"""
PyTorch Skill - 使用示例
"""

import sys
import os
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import PyTorchSkill


def example_1_basic_mlp():
    """示例1: 基本MLP分类"""
    print("=" * 60)
    print("示例1: 多层感知机分类")
    print("=" * 60)
    
    skill = PyTorchSkill()
    
    # 生成分类数据
    np.random.seed(42)
    X = np.random.randn(1000, 20).astype(np.float32)
    y = np.random.randint(0, 5, 1000)
    
    # 分割数据
    X_train, X_val = X[:800], X[800:]
    y_train, y_val = y[:800], y[800:]
    
    print(f"训练集: {len(X_train)}, 验证集: {len(X_val)}")
    print(f"特征维度: {X.shape[1]}, 类别数: {len(np.unique(y))}")
    
    # 创建数据加载器
    train_loader = skill.create_data_loader(X_train, y_train, batch_size=64)
    val_loader = skill.create_data_loader(X_val, y_val, batch_size=64, shuffle=False)
    
    # 创建模型
    model = skill.create_model(
        model_type="mlp",
        input_size=20,
        hidden_sizes=[64, 32],
        output_size=5,
        dropout=0.2
    )
    
    # 训练
    history = skill.train(
        model, train_loader, val_loader,
        epochs=5, lr=0.001, verbose=False
    )
    
    print(f"\n训练完成!")
    print(f"最终训练准确率: {history['train_acc'][-1]:.2f}%")
    print(f"最终验证准确率: {history['val_acc'][-1]:.2f}%")


def example_2_cnn_mnist():
    """示例2: CNN图像分类"""
    print("\n" + "=" * 60)
    print("示例2: CNN图像分类")
    print("=" * 60)
    
    skill = PyTorchSkill()
    
    # 模拟图像数据 (MNIST格式)
    np.random.seed(42)
    X = np.random.randn(500, 1, 28, 28).astype(np.float32)
    y = np.random.randint(0, 10, 500)
    
    print(f"数据形状: {X.shape}")
    print(f"类别数: {len(np.unique(y))}")
    
    # 创建CNN模型
    import torch.nn as nn
    
    class SimpleCNN(nn.Module):
        def __init__(self):
            super(SimpleCNN, self).__init__()
            self.features = nn.Sequential(
                nn.Conv2d(1, 32, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Conv2d(32, 64, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(2),
            )
            self.classifier = nn.Sequential(
                nn.Flatten(),
                nn.Linear(64 * 7 * 7, 128),
                nn.ReLU(),
                nn.Dropout(0.5),
                nn.Linear(128, 10)
            )
        
        def forward(self, x):
            x = self.features(x)
            x = self.classifier(x)
            return x
    
    model = SimpleCNN().to(skill.device)
    
    # 创建数据加载器
    import torch
    from torch.utils.data import DataLoader, TensorDataset
    
    X_train, X_val = X[:400], X[400:]
    y_train, y_val = y[:400], y[400:]
    
    train_dataset = TensorDataset(torch.FloatTensor(X_train), torch.LongTensor(y_train))
    val_dataset = TensorDataset(torch.FloatTensor(X_val), torch.LongTensor(y_val))
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32)
    
    # 训练
    history = skill.train(model, train_loader, val_loader, epochs=3, verbose=False)
    
    print(f"\nCNN训练完成!")
    print(f"最终验证准确率: {history['val_acc'][-1]:.2f}%")


def example_3_rnn_sequence():
    """示例3: RNN序列分类"""
    print("\n" + "=" * 60)
    print("示例3: RNN序列分类")
    print("=" * 60)
    
    skill = PyTorchSkill()
    
    # 生成序列数据
    np.random.seed(42)
    n_samples = 500
    seq_length = 20
    n_features = 10
    n_classes = 3
    
    X = np.random.randn(n_samples, seq_length, n_features).astype(np.float32)
    y = np.random.randint(0, n_classes, n_samples)
    
    print(f"数据形状: {X.shape}")
    print(f"序列长度: {seq_length}, 特征维度: {n_features}")
    print(f"类别数: {n_classes}")
    
    # 创建LSTM模型
    model = skill.create_model(
        model_type="lstm",
        input_size=n_features,
        hidden_sizes=[64],
        output_size=n_classes,
        num_layers=1
    )
    
    # 创建数据加载器
    X_train, X_val = X[:400], X[400:]
    y_train, y_val = y[:400], y[400:]
    
    train_loader = skill.create_data_loader(
        X_train.reshape(-1, seq_length * n_features),
        y_train, batch_size=32
    )
    val_loader = skill.create_data_loader(
        X_val.reshape(-1, seq_length * n_features),
        y_val, batch_size=32, shuffle=False
    )
    
    print(f"\nLSTM模型创建完成")
    print(f"模型类型: LSTM")
    print(f"隐藏层大小: 64")


def example_4_model_comparison():
    """示例4: 不同优化器对比"""
    print("\n" + "=" * 60)
    print("示例4: 优化器对比")
    print("=" * 60)
    
    # 生成数据
    np.random.seed(42)
    X = np.random.randn(500, 10).astype(np.float32)
    y = np.random.randint(0, 3, 500)
    
    X_train, X_val = X[:400], X[400:]
    y_train, y_val = y[:400], y[400:]
    
    optimizers = ["adam", "sgd", "rmsprop"]
    results = {}
    
    for opt_name in optimizers:
        skill = PyTorchSkill()
        
        train_loader = skill.create_data_loader(X_train, y_train, batch_size=32)
        val_loader = skill.create_data_loader(X_val, y_val, batch_size=32, shuffle=False)
        
        model = skill.create_model(
            model_type="mlp",
            input_size=10,
            hidden_sizes=[32, 16],
            output_size=3
        )
        
        history = skill.train(
            model, train_loader, val_loader,
            epochs=3, optimizer_name=opt_name, verbose=False
        )
        
        results[opt_name] = history['val_acc'][-1]
    
    print("\n优化器性能对比:")
    for opt, acc in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(f"  {opt:10s}: {acc:.2f}%")


def example_5_save_load_checkpoint():
    """示例5: 模型保存和加载"""
    print("\n" + "=" * 60)
    print("示例5: 模型保存和加载")
    print("=" * 60)
    
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        import json
        config = {"device": "cpu", "model_checkpoint": {"checkpoint_dir": temp_dir}}
        config_path = os.path.join(temp_dir, "config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f)
        
        skill = PyTorchSkill(config_path)
        
        # 创建并保存模型
        model = skill.create_model(
            model_type="mlp",
            input_size=10,
            hidden_sizes=[20],
            output_size=3
        )
        
        # 保存
        filepath = skill.save_model(model, "my_model.pth", epoch=0)
        print(f"模型已保存: {filepath}")
        
        # 加载
        new_model = skill.create_model(
            model_type="mlp",
            input_size=10,
            hidden_sizes=[20],
            output_size=3
        )
        loaded_model, _, epoch = skill.load_model("my_model.pth", new_model)
        
        print(f"模型加载成功!")
        print(f"恢复轮数: {epoch}")
        
        # 验证预测一致
        import torch
        test_input = torch.randn(1, 10)
        model.eval()
        loaded_model.eval()
        
        with torch.no_grad():
            out1 = model(test_input.to(skill.device))
            out2 = loaded_model(test_input.to(skill.device))
        
        diff = torch.abs(out1 - out2).max().item()
        print(f"预测差异: {diff:.6f}")
        print(f"✓ 模型保存和加载成功")


def example_6_custom_training_loop():
    """示例6: 自定义训练循环"""
    print("\n" + "=" * 60)
    print("示例6: 自定义训练循环")
    print("=" * 60)
    
    skill = PyTorchSkill()
    
    # 数据
    np.random.seed(42)
    X = np.random.randn(300, 5).astype(np.float32)
    y = np.random.randint(0, 2, 300)
    
    X_train, X_val = X[:240], X[240:]
    y_train, y_val = y[:240], y[240:]
    
    train_loader = skill.create_data_loader(X_train, y_train, batch_size=24)
    val_loader = skill.create_data_loader(X_val, y_val, batch_size=24, shuffle=False)
    
    # 模型
    model = skill.create_model(
        model_type="mlp",
        input_size=5,
        hidden_sizes=[16, 8],
        output_size=2
    )
    
    # 使用内置训练
    history = skill.train(model, train_loader, val_loader, epochs=3, verbose=False)
    
    print("训练历史:")
    print(f"  Epoch 1 - Loss: {history['train_loss'][0]:.4f}, Acc: {history['train_acc'][0]:.2f}%")
    print(f"  Epoch 2 - Loss: {history['train_loss'][1]:.4f}, Acc: {history['train_acc'][1]:.2f}%")
    print(f"  Epoch 3 - Loss: {history['train_loss'][2]:.4f}, Acc: {history['train_acc'][2]:.2f}%")
    print(f"\n最终验证准确率: {history['val_acc'][-1]:.2f}%")


def example_7_different_architectures():
    """示例7: 不同架构对比"""
    print("\n" + "=" * 60)
    print("示例7: 不同神经网络架构对比")
    print("=" * 60)
    
    skill = PyTorchSkill()
    
    architectures = [
        ("Small MLP", {"model_type": "mlp", "input_size": 10, "hidden_sizes": [16], "output_size": 3}),
        ("Medium MLP", {"model_type": "mlp", "input_size": 10, "hidden_sizes": [32, 16], "output_size": 3}),
        ("Large MLP", {"model_type": "mlp", "input_size": 10, "hidden_sizes": [64, 32, 16], "output_size": 3}),
        ("CNN", {"model_type": "cnn", "output_size": 3, "in_channels": 1}),
    ]
    
    print("\n架构参数对比:")
    for name, params in architectures:
        model = skill.create_model(**params)
        param_count = skill._count_parameters(model)
        print(f"  {name:15s}: {param_count:,} 参数")


def example_8_device_info():
    """示例8: 设备信息"""
    print("\n" + "=" * 60)
    print("示例8: 设备信息")
    print("=" * 60)
    
    skill = PyTorchSkill()
    
    print(f"当前设备: {skill.device}")
    
    import torch
    if torch.cuda.is_available():
        print(f"CUDA可用: 是")
        print(f"GPU数量: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
        print(f"当前GPU显存: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    else:
        print(f"CUDA可用: 否")
    
    if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        print(f"MPS (Apple Silicon) 可用: 是")
    else:
        print(f"MPS (Apple Silicon) 可用: 否")


def example_9_batch_prediction():
    """示例9: 批量预测"""
    print("\n" + "=" * 60)
    print("示例9: 批量预测")
    print("=" * 60)
    
    skill = PyTorchSkill()
    
    # 创建模型
    model = skill.create_model(
        model_type="mlp",
        input_size=5,
        hidden_sizes=[10],
        output_size=3
    )
    
    # 批量数据
    import torch
    batch_data = torch.randn(100, 5)
    
    # 预测
    predictions = skill.predict(model, batch_data)
    
    print(f"输入批次: {batch_data.shape}")
    print(f"预测输出: {predictions.shape}")
    print(f"预测类别分布:")
    unique, counts = torch.unique(predictions, return_counts=True)
    for cls, cnt in zip(unique.tolist(), counts.tolist()):
        print(f"  类别 {cls}: {cnt} 个 ({cnt/len(predictions)*100:.1f}%)")


def example_10_training_visualization():
    """示例10: 训练可视化"""
    print("\n" + "=" * 60)
    print("示例10: 训练历史记录")
    print("=" * 60)
    
    skill = PyTorchSkill()
    
    # 数据
    np.random.seed(42)
    X = np.random.randn(400, 8).astype(np.float32)
    y = np.random.randint(0, 4, 400)
    
    X_train, X_val = X[:320], X[320:]
    y_train, y_val = y[:320], y[320:]
    
    train_loader = skill.create_data_loader(X_train, y_train, batch_size=32)
    val_loader = skill.create_data_loader(X_val, y_val, batch_size=32, shuffle=False)
    
    # 模型
    model = skill.create_model(
        model_type="mlp",
        input_size=8,
        hidden_sizes=[32, 16],
        output_size=4
    )
    
    # 训练
    history = skill.train(model, train_loader, val_loader, epochs=5, verbose=False)
    
    print("训练进度:")
    print(f"{'Epoch':<8} {'Train Loss':<12} {'Train Acc':<12} {'Val Loss':<12} {'Val Acc':<12}")
    print("-" * 60)
    for i in range(len(history['train_loss'])):
        print(f"{i+1:<8} {history['train_loss'][i]:<12.4f} "
              f"{history['train_acc'][i]:<12.2f} {history['val_loss'][i]:<12.4f} "
              f"{history['val_acc'][i]:<12.2f}")
    
    # 保存训练历史
    import tempfile
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(history, f, indent=2)
        print(f"\n训练历史已保存")


def main():
    """运行所有示例"""
    examples = [
        example_1_basic_mlp,
        example_2_cnn_mnist,
        example_3_rnn_sequence,
        example_4_model_comparison,
        example_5_save_load_checkpoint,
        example_6_custom_training_loop,
        example_7_different_architectures,
        example_8_device_info,
        example_9_batch_prediction,
        example_10_training_visualization,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n[!] {example.__name__} 执行失败: {e}")
    
    print("\n" + "=" * 60)
    print("所有示例执行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
