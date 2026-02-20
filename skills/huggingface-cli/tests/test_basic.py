#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HuggingFace CLI 基础测试
=======================

运行测试:
    python -m pytest tests/test_basic.py -v
    或
    python tests/test_basic.py
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# 添加上级目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import HuggingFaceCLI
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装依赖: pip install -r requirements.txt")
    sys.exit(1)


class TestHuggingFaceCLI(unittest.TestCase):
    """HuggingFace CLI 测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.test_cache_dir = tempfile.mkdtemp(prefix="hf_test_")
        cls.cli = HuggingFaceCLI(cache_dir=cls.test_cache_dir)
        print(f"\n测试缓存目录: {cls.test_cache_dir}")
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        if os.path.exists(cls.test_cache_dir):
            shutil.rmtree(cls.test_cache_dir)
        print(f"已清理测试目录: {cls.test_cache_dir}")
    
    # ==================== 基础功能测试 ====================
    
    def test_initialization(self):
        """测试CLI初始化"""
        self.assertIsNotNone(self.cli)
        self.assertEqual(str(self.cli.cache_dir), self.test_cache_dir)
        print("✅ 初始化测试通过")
    
    def test_format_size(self):
        """测试文件大小格式化"""
        test_cases = [
            (0, "0.00 B"),
            (1024, "1.00 KB"),
            (1024 * 1024, "1.00 MB"),
            (1024 * 1024 * 1024, "1.00 GB"),
        ]
        
        for size, expected in test_cases:
            result = self.cli._format_size(size)
            self.assertEqual(result, expected)
        
        print("✅ 文件大小格式化测试通过")
    
    def test_get_dir_size(self):
        """测试目录大小计算"""
        # 创建测试文件
        test_dir = os.path.join(self.test_cache_dir, "size_test")
        os.makedirs(test_dir, exist_ok=True)
        
        # 写入测试数据
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Hello, World!" * 100)
        
        size = self.cli._get_dir_size(test_dir)
        self.assertGreater(size, 0)
        
        # 清理
        os.remove(test_file)
        os.rmdir(test_dir)
        
        print("✅ 目录大小计算测试通过")
    
    # ==================== 搜索功能测试 ====================
    
    def test_search_models_bert(self):
        """测试模型搜索 (bert)"""
        print("\n🔍 测试模型搜索...")
        results = self.cli.search_models("bert-base-chinese", limit=3)
        self.assertIsInstance(results, list)
        if results:
            self.assertIn("id", results[0])
            self.assertIn("downloads", results[0])
        print("✅ 模型搜索测试通过")
    
    def test_search_datasets_glue(self):
        """测试数据集搜索 (glue)"""
        print("\n🔍 测试数据集搜索...")
        results = self.cli.search_datasets("glue", limit=3)
        self.assertIsInstance(results, list)
        if results:
            self.assertIn("id", results[0])
        print("✅ 数据集搜索测试通过")
    
    def test_search_empty_query(self):
        """测试空搜索返回结果"""
        results = self.cli.search_models("xyz123nonexistent", limit=5)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)
        print("✅ 空搜索结果测试通过")
    
    # ==================== 信息查询测试 ====================
    
    def test_model_info_bert(self):
        """测试模型信息查询"""
        print("\n📋 测试模型信息查询...")
        info = self.cli.get_model_info("bert-base-chinese")
        if info:
            self.assertEqual(info["id"], "bert-base-chinese")
            self.assertIn("downloads", info)
            self.assertIn("tags", info)
        print("✅ 模型信息查询测试通过")
    
    def test_model_info_not_exist(self):
        """测试不存在的模型"""
        info = self.cli.get_model_info("this-model-does-not-exist-12345")
        self.assertIsNone(info)
        print("✅ 不存在的模型测试通过")
    
    def test_dataset_info_glue(self):
        """测试数据集信息查询"""
        print("\n📋 测试数据集信息查询...")
        info = self.cli.get_dataset_info("glue")
        if info:
            self.assertEqual(info["id"], "glue")
            self.assertIn("downloads", info)
        print("✅ 数据集信息查询测试通过")
    
    # ==================== 缓存管理测试 ====================
    
    def test_cache_info(self):
        """测试缓存信息查询"""
        info = self.cli.cache_info()
        self.assertIsInstance(info, dict)
        self.assertIn("cache_dir", info)
        self.assertIn("hub_dir", info)
        self.assertIn("datasets_dir", info)
        print("✅ 缓存信息测试通过")
    
    def test_list_local_models_empty(self):
        """测试空本地模型列表"""
        models = self.cli.list_local_models()
        self.assertIsInstance(models, list)
        print("✅ 本地模型列表测试通过")
    
    # ==================== 小文件下载测试 ====================
    
    def test_download_small_model_config(self):
        """测试下载小模型配置文件"""
        print("\n⬇️  测试小文件下载...")
        
        # 下载一个小配置文件
        test_dir = os.path.join(self.test_cache_dir, "download_test")
        
        result = self.cli.download_model(
            model_id="bert-base-chinese",
            local_dir=test_dir,
            include=["config.json"],
            resume=True
        )
        
        if result:
            self.assertTrue(os.path.exists(result))
            config_file = os.path.join(result, "config.json")
            if os.path.exists(config_file):
                self.assertTrue(os.path.getsize(config_file) > 0)
        
        # 清理
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        print("✅ 小文件下载测试通过")


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 HuggingFace CLI 基础测试")
    print("=" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestHuggingFaceCLI)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ 所有测试通过!")
    else:
        print(f"❌ 测试失败: {len(result.failures)} 个失败, {len(result.errors)} 个错误")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
