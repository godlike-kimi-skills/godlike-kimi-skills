"""
PyTorch Skill - 测试模块
"""

import unittest
import os
import tempfile
import numpy as np
from unittest.mock import patch, MagicMock

# 导入被测试模块
import sys
sys.path.insert(0, os.path.dirname(__file__))

# 检查torch是否可用
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from main import PyTorchSkill, create_skill


@unittest.skipUnless(TORCH_AVAILABLE, "PyTorch not available")
class TestPyTorchSkill(unittest.TestCase):
    """PyTorchSkill测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "device": "cpu",
            "default_epochs": 2,
            "default_batch_size": 16,
            "default_lr": 0.01,
            "model_checkpoint": {"checkpoint_dir": self.temp_dir}
        }
        import json
        self.config_path = os.path.join(self.temp_dir, "config.json")
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """测试初始化"""
        skill = PyTorchSkill(self.config_path)
        self.assertEqual(str(skill.device), "cpu")
        self.assertEqual(skill.default_epochs, 2)
        self.assertEqual(skill.default_batch_size, 16)
    
    def test_default_initialization(self):
        """测试默认初始化"""
        skill = PyTorchSkill()
        self.assertIsNotNone(skill.device)
        self.assertIsNotNone(skill.default_epochs)
    
    def test_load_config(self):
        """测试配置加载"""
        skill = PyTorchSkill(self.config_path)
        self.assertEqual(skill.config["default_epochs"], 2)
        self.assertEqual(skill.config["default_lr"], 0.01)
    
    def test_create_mlp_model(self):
        """测试创建MLP模型"""
        skill = PyTorchSkill(self.config_path)
        model = skill.create_model(
            model_type="mlp",
            input_size=784,
            hidden_sizes=[128, 64],
            output_size=10
        )
        self.assertIsInstance(model, nn.Module)
        self.assertTrue(hasattr(model, 'forward'))
    
    def test_create_cnn_model(self):
        """测试创建CNN模型"""
        skill = PyTorchSkill(self.config_path)
        model = skill.create_model(
            model_type="cnn",
            output_size=10,
            in_channels=3
        )
        self.assertIsInstance(model, nn.Module)
    
    def test_create_rnn_model(self):
        """测试创建RNN模型"""
        skill = PyTorchSkill(self.config_path)
        model = skill.create_model(
            model_type="rnn",
            input_size=50,
            hidden_sizes=[128],
            output_size=5
        )
        self.assertIsInstance(model, nn.Module)
    
    def test_create_lstm_model(self):
        """测试创建LSTM模型"""
        skill = PyTorchSkill(self.config_path)
        model = skill.create_model(
            model_type="lstm",
            input_size=50,
            hidden_sizes=[128],
            output_size=5
        )
        self.assertIsInstance(model, nn.Module)
    
    def test_unknown_model_type(self):
        """测试未知模型类型"""
        skill = PyTorchSkill(self.config_path)
        with self.assertRaises(ValueError):
            skill.create_model(model_type="unknown")
    
    def test_count_parameters(self):
        """测试参数计数"""
        skill = PyTorchSkill(self.config_path)
        model = skill.create_model(
            model_type="mlp",
            input_size=10,
            hidden_sizes=[5],
            output_size=2
        )
        param_count = skill._count_parameters(model)
        self.assertGreater(param_count, 0)
    
    def test_get_optimizer(self):
        """测试获取优化器"""
        skill = PyTorchSkill(self.config_path)
        model = skill.create_model(
            model_type="mlp",
            input_size=10,
            hidden_sizes=[5],
            output_size=2
        )
        
        optimizer = skill.get_optimizer(model, "adam", lr=0.001)
        self.assertIsNotNone(optimizer)
        
        optimizer = skill.get_optimizer(model, "sgd", lr=0.01)
        self.assertIsNotNone(optimizer)
    
    def test_get_loss_function(self):
        """测试获取损失函数"""
        skill = PyTorchSkill(self.config_path)
        
        loss_fn = skill.get_loss_function("cross_entropy")
        self.assertIsNotNone(loss_fn)
        
        loss_fn = skill.get_loss_function("mse")
        self.assertIsNotNone(loss_fn)
    
    def test_create_data_loader(self):
        """测试创建数据加载器"""
        skill = PyTorchSkill(self.config_path)
        
        X = np.random.randn(100, 10).astype(np.float32)
        y = np.random.randint(0, 3, 100)
        
        loader = skill.create_data_loader(X, y, batch_size=16)
        self.assertIsNotNone(loader)
        self.assertEqual(len(loader), 7)  # 100/16 = 6.25 -> 7 batches
    
    def test_predict(self):
        """测试预测"""
        skill = PyTorchSkill(self.config_path)
        model = skill.create_model(
            model_type="mlp",
            input_size=10,
            hidden_sizes=[5],
            output_size=3
        )
        
        data = torch.randn(5, 10)
        predictions = skill.predict(model, data)
        
        self.assertEqual(predictions.shape[0], 5)
        self.assertTrue(torch.all(predictions >= 0))
        self.assertTrue(torch.all(predictions < 3))
    
    def test_save_load_model(self):
        """测试模型保存和加载"""
        skill = PyTorchSkill(self.config_path)
        model = skill.create_model(
            model_type="mlp",
            input_size=10,
            hidden_sizes=[5],
            output_size=3
        )
        
        # 保存
        filepath = skill.save_model(model, "test_model.pth")
        self.assertTrue(os.path.exists(filepath))
        
        # 加载
        new_model = skill.create_model(
            model_type="mlp",
            input_size=10,
            hidden_sizes=[5],
            output_size=3
        )
        loaded_model, _, epoch = skill.load_model("test_model.pth", new_model)
        self.assertIsNotNone(loaded_model)
    
    def test_create_skill(self):
        """测试创建skill"""
        skill = create_skill(self.config_path)
        self.assertIsInstance(skill, PyTorchSkill)


@unittest.skipUnless(TORCH_AVAILABLE, "PyTorch not available")
class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_training_workflow(self):
        """测试完整训练流程"""
        with tempfile.TemporaryDirectory() as temp_dir:
            import json
            config = {
                "device": "cpu",
                "default_epochs": 2,
                "default_batch_size": 32,
                "model_checkpoint": {"checkpoint_dir": temp_dir}
            }
            config_path = os.path.join(temp_dir, "config.json")
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            skill = PyTorchSkill(config_path)
            
            # 创建数据
            np.random.seed(42)
            X = np.random.randn(200, 10).astype(np.float32)
            y = np.random.randint(0, 3, 200)
            
            # 分割数据
            X_train, X_val = X[:160], X[160:]
            y_train, y_val = y[:160], y[160:]
            
            # 创建数据加载器
            train_loader = skill.create_data_loader(X_train, y_train, batch_size=32)
            val_loader = skill.create_data_loader(X_val, y_val, batch_size=32, shuffle=False)
            
            # 创建模型
            model = skill.create_model(
                model_type="mlp",
                input_size=10,
                hidden_sizes=[20, 10],
                output_size=3
            )
            
            # 训练
            history = skill.train(
                model, train_loader, val_loader,
                epochs=2, verbose=False
            )
            
            self.assertIn("train_loss", history)
            self.assertIn("train_acc", history)
            self.assertEqual(len(history["train_loss"]), 2)


def run_tests():
    """运行所有测试"""
    if not TORCH_AVAILABLE:
        print("PyTorch not available, skipping all tests")
        return True
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestPyTorchSkill))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
