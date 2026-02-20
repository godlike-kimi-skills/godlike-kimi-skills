"""
PyTorch Skill - Deep Learning Tool
支持模型定义、训练循环和GPU管理
"""

import os
import json
import logging
from typing import Optional, Union, List, Dict, Any, Tuple, Callable
from pathlib import Path
import time

import numpy as np

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试导入torch
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available. Some features will be limited.")


class PyTorchSkill:
    """PyTorch深度学习技能"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化PyTorchSkill
        
        Args:
            config_path: 配置文件路径
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required. Install with: pip install torch")
        
        self.config = self._load_config(config_path)
        self.device = self._get_device()
        self.default_epochs = self.config.get("default_epochs", 10)
        self.default_batch_size = self.config.get("default_batch_size", 32)
        self.default_lr = self.config.get("default_lr", 0.001)
        self.checkpoint_dir = self.config.get("model_checkpoint", {}).get("checkpoint_dir", "./checkpoints")
        
        # 确保检查点目录存在
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        self._models = {}
        self._optimizers = {}
        self._schedulers = {}
        
        logger.info(f"PyTorchSkill initialized with device: {self.device}")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
        
        default_config = {
            "device": "auto",
            "default_epochs": 10,
            "default_batch_size": 32,
            "default_lr": 0.001
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return {**default_config, **json.load(f)}
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
    def _get_device(self) -> torch.device:
        """获取计算设备"""
        device_config = self.config.get("device", "auto")
        
        if device_config != "auto":
            return torch.device(device_config)
        
        if torch.cuda.is_available():
            device = torch.device("cuda")
            logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = torch.device("mps")
            logger.info("Using Apple MPS")
        else:
            device = torch.device("cpu")
            logger.info("Using CPU")
        
        return device
    
    def create_model(
        self,
        model_type: str = "mlp",
        input_size: int = 784,
        hidden_sizes: List[int] = [256, 128],
        output_size: int = 10,
        dropout: float = 0.2,
        **kwargs
    ) -> nn.Module:
        """
        创建神经网络模型
        
        Args:
            model_type: 模型类型 (mlp/cnn/rnn/lstm)
            input_size: 输入维度
            hidden_sizes: 隐藏层维度列表
            output_size: 输出维度
            dropout: Dropout率
            **kwargs: 额外参数
            
        Returns:
            PyTorch模型
        """
        if model_type == "mlp":
            model = self._create_mlp(input_size, hidden_sizes, output_size, dropout)
        elif model_type == "cnn":
            model = self._create_cnn(output_size, dropout, **kwargs)
        elif model_type == "rnn":
            model = self._create_rnn(input_size, hidden_sizes[0], output_size, **kwargs)
        elif model_type == "lstm":
            model = self._create_lstm(input_size, hidden_sizes[0], output_size, **kwargs)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        model = model.to(self.device)
        logger.info(f"Created {model_type} model with {self._count_parameters(model)} parameters")
        return model
    
    def _create_mlp(
        self,
        input_size: int,
        hidden_sizes: List[int],
        output_size: int,
        dropout: float
    ) -> nn.Module:
        """创建多层感知机"""
        layers = []
        prev_size = input_size
        
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.ReLU(),
                nn.Dropout(dropout)
            ])
            prev_size = hidden_size
        
        layers.append(nn.Linear(prev_size, output_size))
        
        return nn.Sequential(*layers)
    
    def _create_cnn(
        self,
        num_classes: int,
        dropout: float,
        in_channels: int = 3
    ) -> nn.Module:
        """创建卷积神经网络"""
        class CNN(nn.Module):
            def __init__(self, in_channels, num_classes, dropout):
                super(CNN, self).__init__()
                self.features = nn.Sequential(
                    nn.Conv2d(in_channels, 32, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2),
                    nn.Conv2d(32, 64, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2),
                    nn.Conv2d(64, 128, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2),
                )
                self.classifier = nn.Sequential(
                    nn.AdaptiveAvgPool2d((1, 1)),
                    nn.Flatten(),
                    nn.Dropout(dropout),
                    nn.Linear(128, num_classes)
                )
            
            def forward(self, x):
                x = self.features(x)
                x = self.classifier(x)
                return x
        
        return CNN(in_channels, num_classes, dropout)
    
    def _create_rnn(
        self,
        input_size: int,
        hidden_size: int,
        output_size: int,
        num_layers: int = 1
    ) -> nn.Module:
        """创建RNN模型"""
        class RNNClassifier(nn.Module):
            def __init__(self, input_size, hidden_size, output_size, num_layers):
                super(RNNClassifier, self).__init__()
                self.hidden_size = hidden_size
                self.num_layers = num_layers
                self.rnn = nn.RNN(input_size, hidden_size, num_layers, batch_first=True)
                self.fc = nn.Linear(hidden_size, output_size)
            
            def forward(self, x):
                h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
                out, _ = self.rnn(x, h0)
                out = self.fc(out[:, -1, :])
                return out
        
        return RNNClassifier(input_size, hidden_size, output_size, num_layers)
    
    def _create_lstm(
        self,
        input_size: int,
        hidden_size: int,
        output_size: int,
        num_layers: int = 1
    ) -> nn.Module:
        """创建LSTM模型"""
        class LSTMClassifier(nn.Module):
            def __init__(self, input_size, hidden_size, output_size, num_layers):
                super(LSTMClassifier, self).__init__()
                self.hidden_size = hidden_size
                self.num_layers = num_layers
                self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
                self.fc = nn.Linear(hidden_size, output_size)
            
            def forward(self, x):
                h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
                c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
                out, _ = self.lstm(x, (h0, c0))
                out = self.fc(out[:, -1, :])
                return out
        
        return LSTMClassifier(input_size, hidden_size, output_size, num_layers)
    
    def _count_parameters(self, model: nn.Module) -> int:
        """计算模型参数数量"""
        return sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    def get_optimizer(
        self,
        model: nn.Module,
        optimizer_name: str = "adam",
        lr: Optional[float] = None,
        **kwargs
    ) -> optim.Optimizer:
        """
        获取优化器
        
        Args:
            model: 模型
            optimizer_name: 优化器名称
            lr: 学习率
            **kwargs: 额外参数
            
        Returns:
            优化器实例
        """
        lr = lr or self.default_lr
        
        optimizers = {
            "adam": optim.Adam,
            "sgd": optim.SGD,
            "adamw": optim.AdamW,
            "rmsprop": optim.RMSprop
        }
        
        if optimizer_name not in optimizers:
            raise ValueError(f"Unknown optimizer: {optimizer_name}")
        
        optimizer = optimizers[optimizer_name](model.parameters(), lr=lr, **kwargs)
        return optimizer
    
    def get_loss_function(self, loss_name: str = "cross_entropy") -> nn.Module:
        """
        获取损失函数
        
        Args:
            loss_name: 损失函数名称
            
        Returns:
            损失函数实例
        """
        losses = {
            "cross_entropy": nn.CrossEntropyLoss(),
            "mse": nn.MSELoss(),
            "bce": nn.BCELoss(),
            "bce_with_logits": nn.BCEWithLogitsLoss(),
            "l1": nn.L1Loss()
        }
        
        if loss_name not in losses:
            raise ValueError(f"Unknown loss function: {loss_name}")
        
        return losses[loss_name]
    
    def train(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: Optional[DataLoader] = None,
        epochs: Optional[int] = None,
        lr: Optional[float] = None,
        optimizer_name: Optional[str] = None,
        loss_name: Optional[str] = None,
        verbose: bool = True
    ) -> Dict[str, List]:
        """
        训练模型
        
        Args:
            model: 模型
            train_loader: 训练数据加载器
            val_loader: 验证数据加载器
            epochs: 训练轮数
            lr: 学习率
            optimizer_name: 优化器名称
            loss_name: 损失函数名称
            verbose: 是否显示进度
            
        Returns:
            训练历史记录
        """
        epochs = epochs or self.default_epochs
        optimizer_name = optimizer_name or self.config.get("default_optimizer", "adam")
        loss_name = loss_name or self.config.get("default_loss", "cross_entropy")
        
        optimizer = self.get_optimizer(model, optimizer_name, lr)
        criterion = self.get_loss_function(loss_name)
        
        history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}
        best_val_loss = float('inf')
        patience_counter = 0
        early_stopping = self.config.get("early_stopping", {})
        
        if verbose:
            from tqdm import tqdm
        
        for epoch in range(epochs):
            # 训练阶段
            model.train()
            train_loss = 0.0
            train_correct = 0
            train_total = 0
            
            train_iter = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}") if verbose else train_loader
            
            for batch_idx, (data, target) in enumerate(train_iter):
                data, target = data.to(self.device), target.to(self.device)
                
                optimizer.zero_grad()
                output = model(data)
                loss = criterion(output, target)
                loss.backward()
                
                # 梯度裁剪
                grad_clip = self.config.get("gradient_clipping", {})
                if grad_clip.get("enabled", False):
                    torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip.get("max_norm", 1.0))
                
                optimizer.step()
                
                train_loss += loss.item()
                _, predicted = output.max(1)
                train_total += target.size(0)
                train_correct += predicted.eq(target).sum().item()
            
            train_loss /= len(train_loader)
            train_acc = 100. * train_correct / train_total
            
            history["train_loss"].append(train_loss)
            history["train_acc"].append(train_acc)
            
            # 验证阶段
            if val_loader is not None:
                val_loss, val_acc = self._validate(model, val_loader, criterion)
                history["val_loss"].append(val_loss)
                history["val_acc"].append(val_acc)
                
                if verbose:
                    logger.info(f"Epoch {epoch+1}: Train Loss={train_loss:.4f}, "
                              f"Train Acc={train_acc:.2f}%, Val Loss={val_loss:.4f}, "
                              f"Val Acc={val_acc:.2f}%")
                
                # 早停检查
                if early_stopping.get("enabled", False):
                    if val_loss < best_val_loss - early_stopping.get("min_delta", 0.001):
                        best_val_loss = val_loss
                        patience_counter = 0
                        # 保存最佳模型
                        self.save_model(model, "best_model.pth")
                    else:
                        patience_counter += 1
                        if patience_counter >= early_stopping.get("patience", 5):
                            logger.info(f"Early stopping at epoch {epoch+1}")
                            break
            else:
                if verbose:
                    logger.info(f"Epoch {epoch+1}: Train Loss={train_loss:.4f}, "
                              f"Train Acc={train_acc:.2f}%")
        
        return history
    
    def _validate(
        self,
        model: nn.Module,
        val_loader: DataLoader,
        criterion: nn.Module
    ) -> Tuple[float, float]:
        """验证模型"""
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = model(data)
                val_loss += criterion(output, target).item()
                _, predicted = output.max(1)
                total += target.size(0)
                correct += predicted.eq(target).sum().item()
        
        val_loss /= len(val_loader)
        val_acc = 100. * correct / total
        
        return val_loss, val_acc
    
    def evaluate(
        self,
        model: nn.Module,
        test_loader: DataLoader
    ) -> Dict[str, float]:
        """
        评估模型
        
        Args:
            model: 模型
            test_loader: 测试数据加载器
            
        Returns:
            评估指标字典
        """
        model.eval()
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = model(data)
                _, predicted = output.max(1)
                total += target.size(0)
                correct += predicted.eq(target).sum().item()
        
        accuracy = 100. * correct / total
        logger.info(f"Test Accuracy: {accuracy:.2f}%")
        
        return {"accuracy": accuracy, "correct": correct, "total": total}
    
    def predict(
        self,
        model: nn.Module,
        data: torch.Tensor
    ) -> torch.Tensor:
        """
        模型预测
        
        Args:
            model: 模型
            data: 输入数据
            
        Returns:
            预测结果
        """
        model.eval()
        data = data.to(self.device)
        
        with torch.no_grad():
            output = model(data)
            _, predicted = output.max(1)
        
        return predicted
    
    def save_model(
        self,
        model: nn.Module,
        filename: str,
        optimizer: Optional[optim.Optimizer] = None,
        epoch: Optional[int] = None
    ) -> str:
        """
        保存模型
        
        Args:
            model: 模型
            filename: 文件名
            optimizer: 优化器（可选）
            epoch: 当前轮数（可选）
            
        Returns:
            保存路径
        """
        filepath = os.path.join(self.checkpoint_dir, filename)
        
        checkpoint = {
            "model_state_dict": model.state_dict(),
            "model_architecture": str(model)
        }
        
        if optimizer is not None:
            checkpoint["optimizer_state_dict"] = optimizer.state_dict()
        
        if epoch is not None:
            checkpoint["epoch"] = epoch
        
        torch.save(checkpoint, filepath)
        logger.info(f"Model saved to {filepath}")
        return filepath
    
    def load_model(
        self,
        filename: str,
        model: nn.Module,
        optimizer: Optional[optim.Optimizer] = None
    ) -> Tuple[nn.Module, Optional[optim.Optimizer], int]:
        """
        加载模型
        
        Args:
            filename: 文件名
            model: 模型实例
            optimizer: 优化器实例（可选）
            
        Returns:
            (模型, 优化器, 轮数)
        """
        filepath = os.path.join(self.checkpoint_dir, filename)
        checkpoint = torch.load(filepath, map_location=self.device)
        
        model.load_state_dict(checkpoint["model_state_dict"])
        model.to(self.device)
        
        if optimizer is not None and "optimizer_state_dict" in checkpoint:
            optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        
        epoch = checkpoint.get("epoch", 0)
        
        logger.info(f"Model loaded from {filepath}")
        return model, optimizer, epoch
    
    def create_data_loader(
        self,
        X: np.ndarray,
        y: np.ndarray,
        batch_size: Optional[int] = None,
        shuffle: bool = True
    ) -> DataLoader:
        """
        创建数据加载器
        
        Args:
            X: 特征数据
            y: 标签数据
            batch_size: 批次大小
            shuffle: 是否打乱数据
            
        Returns:
            数据加载器
        """
        batch_size = batch_size or self.default_batch_size
        
        X_tensor = torch.FloatTensor(X)
        y_tensor = torch.LongTensor(y)
        
        dataset = TensorDataset(X_tensor, y_tensor)
        loader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=self.config.get("training", {}).get("num_workers", 0)
        )
        
        return loader
    
    def plot_training_history(
        self,
        history: Dict[str, List],
        save_path: Optional[str] = None
    ) -> None:
        """
        绘制训练历史
        
        Args:
            history: 训练历史记录
            save_path: 保存路径（可选）
        """
        try:
            import matplotlib.pyplot as plt
            
            fig, axes = plt.subplots(1, 2, figsize=(12, 4))
            
            # 损失曲线
            axes[0].plot(history["train_loss"], label="Train Loss")
            if "val_loss" in history and history["val_loss"]:
                axes[0].plot(history["val_loss"], label="Val Loss")
            axes[0].set_xlabel("Epoch")
            axes[0].set_ylabel("Loss")
            axes[0].set_title("Training Loss")
            axes[0].legend()
            axes[0].grid(True)
            
            # 准确率曲线
            axes[1].plot(history["train_acc"], label="Train Acc")
            if "val_acc" in history and history["val_acc"]:
                axes[1].plot(history["val_acc"], label="Val Acc")
            axes[1].set_xlabel("Epoch")
            axes[1].set_ylabel("Accuracy (%)")
            axes[1].set_title("Training Accuracy")
            axes[1].legend()
            axes[1].grid(True)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path)
                logger.info(f"Training history saved to {save_path}")
            else:
                plt.show()
        except ImportError:
            logger.warning("matplotlib not available for plotting")


# 便捷函数接口
def create_skill(config_path: Optional[str] = None) -> PyTorchSkill:
    """创建Skill实例"""
    return PyTorchSkill(config_path)


if __name__ == "__main__":
    skill = PyTorchSkill()
    print(f"Device: {skill.device}")
    print("PyTorchSkill ready to use!")
