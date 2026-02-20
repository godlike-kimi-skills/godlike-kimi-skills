#!/usr/bin/env python3
"""
NumPy Skill - Test Suite
NumPy技能测试套件
"""

import unittest
import numpy as np
import os
import tempfile
import shutil

from main import NumpySkill, array, zeros, ones, arange, linspace


class TestNumpySkill(unittest.TestCase):
    """NumpySkill测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.skill = NumpySkill(seed=42)
        cls.test_dir = tempfile.mkdtemp()
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    # ==================== 数组创建测试 ====================
    
    def test_create_array_from_list(self):
        """测试从列表创建数组"""
        arr = self.skill.create_array([1, 2, 3, 4, 5])
        self.assertEqual(arr.shape, (5,))
        self.assertEqual(arr.dtype, np.float64)
    
    def test_create_array_from_nested_list(self):
        """测试从嵌套列表创建数组"""
        arr = self.skill.create_array([[1, 2], [3, 4], [5, 6]])
        self.assertEqual(arr.shape, (3, 2))
    
    def test_arange(self):
        """测试等差数列"""
        arr = self.skill.arange(0, 10, 2)
        expected = np.array([0, 2, 4, 6, 8])
        np.testing.assert_array_equal(arr, expected)
    
    def test_linspace(self):
        """测试等间隔数列"""
        arr = self.skill.linspace(0, 1, 5)
        self.assertEqual(len(arr), 5)
        self.assertAlmostEqual(arr[0], 0)
        self.assertAlmostEqual(arr[-1], 1)
    
    def test_zeros(self):
        """测试全零数组"""
        arr = self.skill.zeros((3, 4))
        self.assertEqual(arr.shape, (3, 4))
        self.assertTrue(np.all(arr == 0))
    
    def test_ones(self):
        """测试全一阵列"""
        arr = self.skill.ones((2, 3))
        self.assertEqual(arr.shape, (2, 3))
        self.assertTrue(np.all(arr == 1))
    
    def test_eye(self):
        """测试单位矩阵"""
        arr = self.skill.eye(3)
        self.assertEqual(arr.shape, (3, 3))
        self.assertTrue(np.all(np.diag(arr) == 1))
        self.assertTrue(np.all(arr[np.logical_not(np.eye(3, dtype=bool))] == 0))
    
    def test_full(self):
        """测试填充数组"""
        arr = self.skill.full((2, 2), 5)
        self.assertTrue(np.all(arr == 5))
    
    # ==================== 数组操作测试 ====================
    
    def test_reshape(self):
        """测试重塑"""
        arr = self.skill.arange(12)
        reshaped = self.skill.reshape(arr, (3, 4))
        self.assertEqual(reshaped.shape, (3, 4))
    
    def test_transpose(self):
        """测试转置"""
        arr = self.skill.create_array([[1, 2, 3], [4, 5, 6]])
        transposed = self.skill.transpose(arr)
        self.assertEqual(transposed.shape, (3, 2))
        self.assertEqual(transposed[0, 1], 4)
    
    def test_flatten(self):
        """测试展平"""
        arr = self.skill.create_array([[1, 2], [3, 4]])
        flat = self.skill.flatten(arr)
        self.assertEqual(flat.shape, (4,))
        np.testing.assert_array_equal(flat, [1, 2, 3, 4])
    
    def test_slice_array(self):
        """测试切片"""
        arr = self.skill.arange(10)
        sliced = self.skill.slice_array(arr, 2, 8, 2)
        np.testing.assert_array_equal(sliced, [2, 4, 6])
    
    def test_index_array(self):
        """测试索引"""
        arr = self.skill.arange(10)
        indexed = self.skill.index_array(arr, [0, 3, 5])
        np.testing.assert_array_equal(indexed, [0, 3, 5])
    
    def test_concatenate(self):
        """测试连接"""
        arr1 = self.skill.create_array([1, 2, 3])
        arr2 = self.skill.create_array([4, 5, 6])
        concatenated = self.skill.concatenate([arr1, arr2])
        np.testing.assert_array_equal(concatenated, [1, 2, 3, 4, 5, 6])
    
    def test_stack(self):
        """测试堆叠"""
        arr1 = self.skill.create_array([1, 2, 3])
        arr2 = self.skill.create_array([4, 5, 6])
        stacked = self.skill.stack([arr1, arr2], axis=0)
        self.assertEqual(stacked.shape, (2, 3))
    
    def test_split(self):
        """测试分割"""
        arr = self.skill.arange(10)
        split_arr = self.skill.split(arr, 2)
        self.assertEqual(len(split_arr), 2)
        self.assertEqual(len(split_arr[0]), 5)
    
    def test_tile(self):
        """测试重复"""
        arr = self.skill.create_array([1, 2])
        tiled = self.skill.tile(arr, 3)
        np.testing.assert_array_equal(tiled, [1, 2, 1, 2, 1, 2])
    
    # ==================== 数学运算测试 ====================
    
    def test_add(self):
        """测试加法"""
        arr = self.skill.create_array([1, 2, 3])
        result = self.skill.add(arr, 10)
        np.testing.assert_array_equal(result, [11, 12, 13])
    
    def test_multiply(self):
        """测试乘法"""
        arr = self.skill.create_array([1, 2, 3])
        result = self.skill.multiply(arr, 2)
        np.testing.assert_array_equal(result, [2, 4, 6])
    
    def test_power(self):
        """测试幂运算"""
        arr = self.skill.create_array([1, 2, 3])
        result = self.skill.power(arr, 2)
        np.testing.assert_array_equal(result, [1, 4, 9])
    
    def test_sqrt(self):
        """测试平方根"""
        arr = self.skill.create_array([1, 4, 9])
        result = self.skill.sqrt(arr)
        np.testing.assert_array_almost_equal(result, [1, 2, 3])
    
    def test_exp(self):
        """测试指数"""
        arr = self.skill.create_array([0, 1, 2])
        result = self.skill.exp(arr)
        self.assertAlmostEqual(result[0], 1)
        self.assertAlmostEqual(result[1], np.e, places=5)
    
    def test_log(self):
        """测试对数"""
        arr = self.skill.create_array([1, np.e, np.e**2])
        result = self.skill.log(arr)
        np.testing.assert_array_almost_equal(result, [0, 1, 2])
    
    def test_sin(self):
        """测试正弦"""
        arr = self.skill.create_array([0, np.pi/2, np.pi])
        result = self.skill.sin(arr)
        np.testing.assert_array_almost_equal(result, [0, 1, 0], decimal=5)
    
    def test_cos(self):
        """测试余弦"""
        arr = self.skill.create_array([0, np.pi/2, np.pi])
        result = self.skill.cos(arr)
        np.testing.assert_array_almost_equal(result, [1, 0, -1], decimal=5)
    
    def test_clip(self):
        """测试裁剪"""
        arr = self.skill.create_array([1, 2, 3, 4, 5])
        result = self.skill.clip(arr, 2, 4)
        np.testing.assert_array_equal(result, [2, 2, 3, 4, 4])
    
    def test_round(self):
        """测试四舍五入"""
        arr = self.skill.create_array([1.234, 2.567, 3.891])
        result = self.skill.round(arr, 1)
        np.testing.assert_array_almost_equal(result, [1.2, 2.6, 3.9], decimal=1)
    
    # ==================== 线性代数测试 ====================
    
    def test_matrix_multiply(self):
        """测试矩阵乘法"""
        a = self.skill.create_array([[1, 2], [3, 4]])
        b = self.skill.create_array([[5, 6], [7, 8]])
        result = self.skill.matrix_multiply(a, b)
        expected = np.array([[19, 22], [43, 50]])
        np.testing.assert_array_equal(result, expected)
    
    def test_determinant(self):
        """测试行列式"""
        arr = self.skill.create_array([[1, 2], [3, 4]])
        det = self.skill.determinant(arr)
        self.assertAlmostEqual(det, -2)
    
    def test_inverse(self):
        """测试逆矩阵"""
        arr = self.skill.create_array([[4, 7], [2, 6]])
        inv = self.skill.inverse(arr)
        identity = self.skill.matrix_multiply(arr, inv)
        np.testing.assert_array_almost_equal(identity, np.eye(2), decimal=10)
    
    def test_eigenvalues(self):
        """测试特征值"""
        arr = self.skill.create_array([[4, 2], [1, 3]])
        eigenvals = self.skill.eigenvalues(arr)
        self.assertEqual(len(eigenvals), 2)
    
    def test_eigen_decomposition(self):
        """测试特征值分解"""
        arr = self.skill.create_array([[4, 2], [1, 3]])
        eigenvals, eigenvecs = self.skill.eigen_decomposition(arr)
        self.assertEqual(len(eigenvals), 2)
        self.assertEqual(eigenvecs.shape, (2, 2))
    
    def test_svd(self):
        """测试SVD"""
        arr = self.skill.create_array([[1, 2], [3, 4], [5, 6]])
        u, s, vh = self.skill.svd(arr)
        self.assertEqual(u.shape, (3, 3))
        self.assertEqual(len(s), 2)
        self.assertEqual(vh.shape, (2, 2))
    
    def test_solve_linear(self):
        """测试求解线性方程组"""
        a = self.skill.create_array([[3, 1], [1, 2]])
        b = self.skill.create_array([9, 8])
        x = self.skill.solve_linear(a, b)
        result = self.skill.matrix_multiply(a, x.reshape(-1, 1)).flatten()
        np.testing.assert_array_almost_equal(result, b)
    
    def test_norm(self):
        """测试范数"""
        arr = self.skill.create_array([3, 4])
        norm = self.skill.norm(arr)
        self.assertAlmostEqual(norm, 5)
    
    def test_rank(self):
        """测试矩阵秩"""
        arr = self.skill.create_array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        rank = self.skill.rank(arr)
        self.assertEqual(rank, 2)
    
    def test_trace(self):
        """测试矩阵迹"""
        arr = self.skill.create_array([[1, 2], [3, 4]])
        trace = self.skill.trace(arr)
        self.assertEqual(trace, 5)
    
    def test_diagonal(self):
        """测试对角线"""
        arr = self.skill.create_array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        diag = self.skill.diagonal(arr)
        np.testing.assert_array_equal(diag, [1, 5, 9])
    
    # ==================== 随机数生成测试 ====================
    
    def test_random_uniform(self):
        """测试均匀分布"""
        arr = self.skill.random_uniform(0, 1, (100,))
        self.assertEqual(arr.shape, (100,))
        self.assertTrue(np.all(arr >= 0) and np.all(arr <= 1))
    
    def test_random_normal(self):
        """测试正态分布"""
        arr = self.skill.random_normal(0, 1, (1000,))
        self.assertEqual(arr.shape, (1000,))
        # 均值应该接近0，标准差接近1
        self.assertAlmostEqual(np.mean(arr), 0, places=1)
        self.assertAlmostEqual(np.std(arr), 1, places=1)
    
    def test_random_integers(self):
        """测试随机整数"""
        arr = self.skill.random_integers(1, 10, (100,))
        self.assertTrue(np.all(arr >= 1) and np.all(arr < 10))
    
    def test_random_choice(self):
        """测试随机选择"""
        choices = ['a', 'b', 'c']
        result = self.skill.random_choice(choices, size=10)
        self.assertEqual(len(result), 10)
        self.assertTrue(all(r in choices for r in result))
    
    def test_random_shuffle(self):
        """测试随机打乱"""
        arr = self.skill.arange(10)
        shuffled = self.skill.random_shuffle(arr.copy())
        self.assertEqual(len(shuffled), 10)
        self.assertEqual(set(shuffled), set(arr))
    
    # ==================== 聚合统计测试 ====================
    
    def test_sum(self):
        """测试求和"""
        arr = self.skill.create_array([1, 2, 3, 4, 5])
        result = self.skill.sum(arr)
        self.assertEqual(result, 15)
    
    def test_mean(self):
        """测试均值"""
        arr = self.skill.create_array([1, 2, 3, 4, 5])
        result = self.skill.mean(arr)
        self.assertEqual(result, 3)
    
    def test_std(self):
        """测试标准差"""
        arr = self.skill.create_array([1, 2, 3, 4, 5])
        result = self.skill.std(arr)
        self.assertAlmostEqual(result, np.std([1, 2, 3, 4, 5]))
    
    def test_min_max(self):
        """测试最值"""
        arr = self.skill.create_array([3, 1, 4, 1, 5, 9, 2, 6])
        self.assertEqual(self.skill.min(arr), 1)
        self.assertEqual(self.skill.max(arr), 9)
    
    def test_argmin_argmax(self):
        """测试最值索引"""
        arr = self.skill.create_array([3, 1, 4, 1, 5])
        self.assertEqual(self.skill.argmin(arr), 1)
        self.assertEqual(self.skill.argmax(arr), 4)
    
    def test_median(self):
        """测试中位数"""
        arr = self.skill.create_array([1, 2, 3, 4, 5])
        result = self.skill.median(arr)
        self.assertEqual(result, 3)
    
    def test_percentile(self):
        """测试百分位数"""
        arr = self.skill.arange(101)
        result = self.skill.percentile(arr, 50)
        self.assertEqual(result, 50)
    
    def test_cumsum(self):
        """测试累积和"""
        arr = self.skill.create_array([1, 2, 3, 4])
        result = self.skill.cumsum(arr)
        np.testing.assert_array_equal(result, [1, 3, 6, 10])
    
    def test_unique(self):
        """测试唯一值"""
        arr = self.skill.create_array([1, 2, 2, 3, 3, 3])
        unique = self.skill.unique(arr)
        np.testing.assert_array_equal(unique, [1, 2, 3])
    
    def test_unique_with_counts(self):
        """测试唯一值和频数"""
        arr = self.skill.create_array([1, 2, 2, 3, 3, 3])
        unique, counts = self.skill.unique(arr, return_counts=True)
        np.testing.assert_array_equal(unique, [1, 2, 3])
        np.testing.assert_array_equal(counts, [1, 2, 3])
    
    def test_histogram(self):
        """测试直方图"""
        arr = self.skill.random_normal(0, 1, (1000,))
        hist, bins = self.skill.histogram(arr, bins=10)
        self.assertEqual(len(hist), 10)
        self.assertEqual(len(bins), 11)
    
    # ==================== 文件I/O测试 ====================
    
    def test_save_and_load_array(self):
        """测试数组保存和加载"""
        arr = self.skill.create_array([[1, 2, 3], [4, 5, 6]])
        filepath = os.path.join(self.test_dir, 'test_array.npy')
        
        self.skill.save_array(arr, filepath)
        self.assertTrue(os.path.exists(filepath))
        
        loaded = self.skill.load_array(filepath)
        np.testing.assert_array_equal(loaded, arr)


class TestConvenienceFunctions(unittest.TestCase):
    """便捷函数测试"""
    
    def test_array(self):
        """测试array函数"""
        arr = array([1, 2, 3])
        np.testing.assert_array_equal(arr, [1, 2, 3])
    
    def test_zeros(self):
        """测试zeros函数"""
        arr = zeros((2, 3))
        self.assertEqual(arr.shape, (2, 3))
        self.assertTrue(np.all(arr == 0))
    
    def test_ones(self):
        """测试ones函数"""
        arr = ones((3, 2))
        self.assertEqual(arr.shape, (3, 2))
        self.assertTrue(np.all(arr == 1))
    
    def test_arange(self):
        """测试arange函数"""
        arr = arange(5)
        np.testing.assert_array_equal(arr, [0, 1, 2, 3, 4])
    
    def test_linspace(self):
        """测试linspace函数"""
        arr = linspace(0, 1, 5)
        self.assertEqual(len(arr), 5)


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""
    
    def setUp(self):
        self.skill = NumpySkill()
    
    def test_empty_array_operations(self):
        """测试空数组操作"""
        arr = np.array([])
        self.assertEqual(self.skill.sum(arr), 0)
    
    def test_single_element_array(self):
        """测试单元素数组"""
        arr = self.skill.create_array([5])
        self.assertEqual(self.skill.sum(arr), 5)
        self.assertEqual(self.skill.mean(arr), 5)
    
    def test_very_large_array(self):
        """测试大数组"""
        arr = self.skill.ones((1000, 1000))
        self.assertEqual(self.skill.sum(arr), 1000000)
    
    def test_singular_matrix_inverse(self):
        """测试奇异矩阵求逆"""
        arr = self.skill.create_array([[1, 2], [2, 4]])  # 奇异矩阵
        with self.assertRaises(np.linalg.LinAlgError):
            self.skill.inverse(arr)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestNumpySkill))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
