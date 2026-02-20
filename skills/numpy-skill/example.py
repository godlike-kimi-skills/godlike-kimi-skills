#!/usr/bin/env python3
"""
NumPy Skill Usage Examples
展示NumPy Skill的各种使用场景
"""

from main import NumpySkill
import numpy as np


def example_array_creation():
    """示例：数组创建"""
    print("=" * 60)
    print("示例1: 数组创建")
    print("=" * 60)
    
    skill = NumpySkill()
    
    # 从列表创建
    arr1 = skill.create_array([1, 2, 3, 4, 5])
    print(f"从列表创建: {arr1}")
    
    # 创建等差数列
    arr2 = skill.arange(0, 10, 2)
    print(f"等差数列: {arr2}")
    
    # 创建等间隔数列
    arr3 = skill.linspace(0, 1, 5)
    print(f"等间隔数列: {arr3}")
    
    # 创建全零/全一阵列
    zeros = skill.zeros((2, 3))
    ones = skill.ones((3, 2))
    print(f"\n全零数组 (2x3):\n{zeros}")
    print(f"\n全一数组 (3x2):\n{ones}")
    
    # 创建单位矩阵
    eye = skill.eye(4)
    print(f"\n4x4单位矩阵:\n{eye}")
    
    return arr1


def example_array_operations():
    """示例：数组操作"""
    print("\n" + "=" * 60)
    print("示例2: 数组操作")
    print("=" * 60)
    
    skill = NumpySkill()
    
    # 创建测试数组
    arr = skill.arange(0, 12)
    print(f"原始数组: {arr}")
    print(f"数组形状: {arr.shape}")
    
    # 重塑
    arr_2d = skill.reshape(arr, (3, 4))
    print(f"\n重塑为 3x4:\n{arr_2d}")
    
    # 转置
    arr_t = skill.transpose(arr_2d)
    print(f"\n转置后:\n{arr_t}")
    
    # 切片
    sliced = skill.slice_array(arr, start=2, stop=8, step=2)
    print(f"\n切片 [2:8:2]: {sliced}")
    
    # 索引
    indexed = skill.index_array(arr, [0, 3, 5, 7])
    print(f"\n索引 [0,3,5,7]: {indexed}")
    
    return arr_2d


def example_mathematical_operations():
    """示例：数学运算"""
    print("\n" + "=" * 60)
    print("示例3: 数学运算")
    print("=" * 60)
    
    skill = NumpySkill()
    
    # 创建测试数组
    arr = skill.create_array([1, 2, 3, 4, 5])
    print(f"原始数组: {arr}")
    
    # 基本运算
    print(f"\n加 10: {skill.add(arr, 10)}")
    print(f"减 2: {skill.subtract(arr, 2)}")
    print(f"乘 3: {skill.multiply(arr, 3)}")
    print(f"除 2: {skill.divide(arr, 2)}")
    
    # 幂运算
    print(f"\n平方: {skill.power(arr, 2)}")
    print(f"开方: {skill.sqrt(arr)}")
    
    # 三角函数
    angles = skill.linspace(0, np.pi, 5)
    print(f"\n角度: {angles}")
    print(f"正弦: {skill.sin(angles)}")
    print(f"余弦: {skill.cos(angles)}")
    
    # 指数和对数
    print(f"\n指数 e^x: {skill.exp(arr)}")
    print(f"自然对数: {skill.log(arr)}")
    print(f"log2: {skill.log2(arr)}")
    
    return arr


def example_linear_algebra():
    """示例：线性代数"""
    print("\n" + "=" * 60)
    print("示例4: 线性代数")
    print("=" * 60)
    
    skill = NumpySkill()
    
    # 创建矩阵
    A = skill.create_array([[1, 2], [3, 4], [5, 6]])
    B = skill.create_array([[7, 8, 9], [10, 11, 12]])
    
    print(f"矩阵 A (3x2):\n{A}")
    print(f"\n矩阵 B (2x3):\n{B}")
    
    # 矩阵乘法
    C = skill.matrix_multiply(A, B)
    print(f"\n矩阵乘法 A @ B (3x3):\n{C}")
    
    # 方阵操作
    square = skill.create_array([[4, 7], [2, 6]])
    print(f"\n方阵:\n{square}")
    
    # 行列式
    det = skill.determinant(square)
    print(f"行列式: {det}")
    
    # 逆矩阵
    inv = skill.inverse(square)
    print(f"\n逆矩阵:\n{inv}")
    
    # 特征值
    eigenvalues, eigenvectors = skill.eigen_decomposition(square)
    print(f"\n特征值: {eigenvalues}")
    print(f"特征向量:\n{eigenvectors}")
    
    return C


def example_random_generation():
    """示例：随机数生成"""
    print("\n" + "=" * 60)
    print("示例5: 随机数生成")
    print("=" * 60)
    
    skill = NumpySkill(seed=42)
    
    # 均匀分布
    uniform = skill.random_uniform(0, 1, (2, 3))
    print(f"均匀分布 [0,1]:\n{uniform}")
    
    # 正态分布
    normal = skill.random_normal(0, 1, (2, 3))
    print(f"\n标准正态分布:\n{normal}")
    
    # 整数随机数
    integers = skill.random_integers(1, 10, (2, 5))
    print(f"\n随机整数 [1,10]:\n{integers}")
    
    # 随机选择
    choice = skill.random_choice(['a', 'b', 'c', 'd'], size=5)
    print(f"\n随机选择: {choice}")
    
    # 随机打乱
    arr = skill.arange(10)
    shuffled = skill.random_shuffle(arr.copy())
    print(f"\n原始数组: {arr}")
    print(f"打乱后: {shuffled}")
    
    return normal


def example_aggregation():
    """示例：聚合统计"""
    print("\n" + "=" * 60)
    print("示例6: 聚合统计")
    print("=" * 60)
    
    skill = NumpySkill()
    
    # 创建测试数组
    arr = skill.create_array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    print(f"测试数组:\n{arr}")
    
    # 基本统计
    print(f"\n总和: {skill.sum(arr)}")
    print(f"均值: {skill.mean(arr)}")
    print(f"标准差: {skill.std(arr):.4f}")
    print(f"方差: {skill.var(arr):.4f}")
    print(f"最小值: {skill.min(arr)}")
    print(f"最大值: {skill.max(arr)}")
    
    # 按轴统计
    print(f"\n按行求和: {skill.sum(arr, axis=1)}")
    print(f"按列求和: {skill.sum(arr, axis=0)}")
    
    # 累积和
    print(f"\n累积和: {skill.cumsum(arr)}")
    
    return arr


def main():
    """主函数：运行所有示例"""
    try:
        example_array_creation()
        example_array_operations()
        example_mathematical_operations()
        example_linear_algebra()
        example_random_generation()
        example_aggregation()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"运行示例时出错: {e}")
        raise


if __name__ == "__main__":
    main()
