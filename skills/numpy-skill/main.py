#!/usr/bin/env python3
"""
NumPy Skill - Main Implementation
NumPy数值计算技能主实现文件

功能：NumPy数值计算。支持数组操作、数学运算、随机数生成。
Use when analyzing data, creating visualizations, or when user mentions 'numpy', 'array operations', 'numerical computing', 'linear algebra'.

Author: Kimi Skills
Version: 1.0.0
"""

import numpy as np
from typing import Union, List, Tuple, Optional, Callable, Any
from pathlib import Path
import json
import warnings

warnings.filterwarnings('ignore')


class NumpySkill:
    """
    NumPy数值计算技能类
    
    提供完整的数值计算功能，包括：
    - 数组创建和操作
    - 数学运算
    - 线性代数
    - 随机数生成
    - 聚合统计
    """
    
    def __init__(self, seed: Optional[int] = None, config_path: Optional[str] = None):
        """
        初始化NumpySkill
        
        Args:
            seed: 随机数种子
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self._setup_print_options()
        
        if seed is not None or self.config.get('default_seed') is not None:
            self.set_seed(seed or self.config.get('default_seed'))
    
    def _load_config(self, config_path: Optional[str]) -> dict:
        """加载配置文件"""
        if config_path is None:
            config_path = Path(__file__).parent / "config.json"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._default_config()
    
    def _default_config(self) -> dict:
        """默认配置"""
        return {
            "default_dtype": "float64",
            "default_seed": None,
            "print_options": {"precision": 4, "suppress": True}
        }
    
    def _setup_print_options(self):
        """设置打印选项"""
        options = self.config.get('print_options', {})
        np.set_printoptions(
            precision=options.get('precision', 4),
            suppress=options.get('suppress', True),
            linewidth=options.get('linewidth', 120)
        )
    
    def set_seed(self, seed: int):
        """设置随机数种子"""
        np.random.seed(seed)
    
    # ==================== 数组创建 ====================
    
    def create_array(self, data: Union[List, Tuple], dtype: Optional[str] = None) -> np.ndarray:
        """
        从列表或元组创建数组
        
        Args:
            data: 输入数据
            dtype: 数据类型
            
        Returns:
            np.ndarray: 创建的数组
        """
        dtype = dtype or self.config.get('default_dtype', 'float64')
        return np.array(data, dtype=dtype)
    
    def arange(self, start: int, stop: Optional[int] = None, step: int = 1) -> np.ndarray:
        """
        创建等差数列
        
        Args:
            start: 起始值
            stop: 终止值（不包含）
            step: 步长
            
        Returns:
            np.ndarray: 等差数列数组
        """
        return np.arange(start, stop, step)
    
    def linspace(self, start: float, stop: float, num: int = 50) -> np.ndarray:
        """
        创建等间隔数列
        
        Args:
            start: 起始值
            stop: 终止值
            num: 样本数
            
        Returns:
            np.ndarray: 等间隔数列数组
        """
        return np.linspace(start, stop, num)
    
    def logspace(self, start: float, stop: float, num: int = 50, base: float = 10.0) -> np.ndarray:
        """
        创建对数间隔数列
        
        Args:
            start: 起始指数
            stop: 终止指数
            num: 样本数
            base: 对数底数
            
        Returns:
            np.ndarray: 对数间隔数列数组
        """
        return np.logspace(start, stop, num, base=base)
    
    def zeros(self, shape: Union[int, Tuple[int, ...]], dtype: Optional[str] = None) -> np.ndarray:
        """
        创建全零数组
        
        Args:
            shape: 数组形状
            dtype: 数据类型
            
        Returns:
            np.ndarray: 全零数组
        """
        dtype = dtype or self.config.get('default_dtype', 'float64')
        return np.zeros(shape, dtype=dtype)
    
    def ones(self, shape: Union[int, Tuple[int, ...]], dtype: Optional[str] = None) -> np.ndarray:
        """
        创建全一数组
        
        Args:
            shape: 数组形状
            dtype: 数据类型
            
        Returns:
            np.ndarray: 全一数组
        """
        dtype = dtype or self.config.get('default_dtype', 'float64')
        return np.ones(shape, dtype=dtype)
    
    def eye(self, n: int, m: Optional[int] = None, dtype: Optional[str] = None) -> np.ndarray:
        """
        创建单位矩阵
        
        Args:
            n: 行数
            m: 列数，默认为n
            dtype: 数据类型
            
        Returns:
            np.ndarray: 单位矩阵
        """
        dtype = dtype or self.config.get('default_dtype', 'float64')
        return np.eye(n, m, dtype=dtype)
    
    def full(self, shape: Union[int, Tuple[int, ...]], fill_value: Any, 
             dtype: Optional[str] = None) -> np.ndarray:
        """
        创建填充指定值的数组
        
        Args:
            shape: 数组形状
            fill_value: 填充值
            dtype: 数据类型
            
        Returns:
            np.ndarray: 填充数组
        """
        dtype = dtype or self.config.get('default_dtype', 'float64')
        return np.full(shape, fill_value, dtype=dtype)
    
    def empty(self, shape: Union[int, Tuple[int, ...]], dtype: Optional[str] = None) -> np.ndarray:
        """
        创建未初始化数组
        
        Args:
            shape: 数组形状
            dtype: 数据类型
            
        Returns:
            np.ndarray: 未初始化数组
        """
        dtype = dtype or self.config.get('default_dtype', 'float64')
        return np.empty(shape, dtype=dtype)
    
    # ==================== 数组操作 ====================
    
    def reshape(self, arr: np.ndarray, shape: Union[int, Tuple[int, ...]]) -> np.ndarray:
        """
        重塑数组形状
        
        Args:
            arr: 输入数组
            shape: 新形状
            
        Returns:
            np.ndarray: 重塑后的数组
        """
        return arr.reshape(shape)
    
    def transpose(self, arr: np.ndarray, axes: Optional[Tuple[int, ...]] = None) -> np.ndarray:
        """
        转置数组
        
        Args:
            arr: 输入数组
            axes: 轴顺序
            
        Returns:
            np.ndarray: 转置后的数组
        """
        return arr.transpose(axes)
    
    def flatten(self, arr: np.ndarray) -> np.ndarray:
        """
        展平数组
        
        Args:
            arr: 输入数组
            
        Returns:
            np.ndarray: 一维数组
        """
        return arr.flatten()
    
    def ravel(self, arr: np.ndarray) -> np.ndarray:
        """
        展平数组（可能返回视图）
        
        Args:
            arr: 输入数组
            
        Returns:
            np.ndarray: 一维数组
        """
        return arr.ravel()
    
    def slice_array(self, arr: np.ndarray, start: Optional[int] = None, 
                    stop: Optional[int] = None, step: Optional[int] = None) -> np.ndarray:
        """
        切片数组
        
        Args:
            arr: 输入数组
            start: 起始索引
            stop: 终止索引
            step: 步长
            
        Returns:
            np.ndarray: 切片后的数组
        """
        return arr[start:stop:step]
    
    def index_array(self, arr: np.ndarray, indices: Union[List[int], np.ndarray]) -> np.ndarray:
        """
        索引数组
        
        Args:
            arr: 输入数组
            indices: 索引列表
            
        Returns:
            np.ndarray: 索引后的数组
        """
        return arr[indices]
    
    def concatenate(self, arrays: List[np.ndarray], axis: int = 0) -> np.ndarray:
        """
        连接数组
        
        Args:
            arrays: 要连接的数组列表
            axis: 连接轴
            
        Returns:
            np.ndarray: 连接后的数组
        """
        return np.concatenate(arrays, axis=axis)
    
    def stack(self, arrays: List[np.ndarray], axis: int = 0) -> np.ndarray:
        """
        堆叠数组
        
        Args:
            arrays: 要堆叠的数组列表
            axis: 堆叠轴
            
        Returns:
            np.ndarray: 堆叠后的数组
        """
        return np.stack(arrays, axis=axis)
    
    def split(self, arr: np.ndarray, indices_or_sections: Union[int, List[int]], 
              axis: int = 0) -> List[np.ndarray]:
        """
        分割数组
        
        Args:
            arr: 输入数组
            indices_or_sections: 分割点或段数
            axis: 分割轴
            
        Returns:
            List[np.ndarray]: 分割后的数组列表
        """
        return np.split(arr, indices_or_sections, axis=axis)
    
    def tile(self, arr: np.ndarray, reps: Union[int, Tuple[int, ...]]) -> np.ndarray:
        """
        重复数组
        
        Args:
            arr: 输入数组
            reps: 重复次数
            
        Returns:
            np.ndarray: 重复后的数组
        """
        return np.tile(arr, reps)
    
    def repeat(self, arr: np.ndarray, repeats: Union[int, List[int]], axis: Optional[int] = None) -> np.ndarray:
        """
        重复数组元素
        
        Args:
            arr: 输入数组
            repeats: 重复次数
            axis: 重复轴
            
        Returns:
            np.ndarray: 重复后的数组
        """
        return np.repeat(arr, repeats, axis=axis)
    
    # ==================== 数学运算 ====================
    
    def add(self, arr1: np.ndarray, arr2: Union[np.ndarray, float]) -> np.ndarray:
        """加法运算"""
        return np.add(arr1, arr2)
    
    def subtract(self, arr1: np.ndarray, arr2: Union[np.ndarray, float]) -> np.ndarray:
        """减法运算"""
        return np.subtract(arr1, arr2)
    
    def multiply(self, arr1: np.ndarray, arr2: Union[np.ndarray, float]) -> np.ndarray:
        """乘法运算"""
        return np.multiply(arr1, arr2)
    
    def divide(self, arr1: np.ndarray, arr2: Union[np.ndarray, float]) -> np.ndarray:
        """除法运算"""
        return np.divide(arr1, arr2)
    
    def power(self, arr: np.ndarray, exponent: Union[np.ndarray, float]) -> np.ndarray:
        """幂运算"""
        return np.power(arr, exponent)
    
    def sqrt(self, arr: np.ndarray) -> np.ndarray:
        """平方根"""
        return np.sqrt(arr)
    
    def exp(self, arr: np.ndarray) -> np.ndarray:
        """指数函数 e^x"""
        return np.exp(arr)
    
    def log(self, arr: np.ndarray) -> np.ndarray:
        """自然对数"""
        return np.log(arr)
    
    def log2(self, arr: np.ndarray) -> np.ndarray:
        """以2为底的对数"""
        return np.log2(arr)
    
    def log10(self, arr: np.ndarray) -> np.ndarray:
        """以10为底的对数"""
        return np.log10(arr)
    
    def sin(self, arr: np.ndarray) -> np.ndarray:
        """正弦函数"""
        return np.sin(arr)
    
    def cos(self, arr: np.ndarray) -> np.ndarray:
        """余弦函数"""
        return np.cos(arr)
    
    def tan(self, arr: np.ndarray) -> np.ndarray:
        """正切函数"""
        return np.tan(arr)
    
    def arcsin(self, arr: np.ndarray) -> np.ndarray:
        """反正弦函数"""
        return np.arcsin(arr)
    
    def arccos(self, arr: np.ndarray) -> np.ndarray:
        """反余弦函数"""
        return np.arccos(arr)
    
    def arctan(self, arr: np.ndarray) -> np.ndarray:
        """反正切函数"""
        return np.arctan(arr)
    
    def abs(self, arr: np.ndarray) -> np.ndarray:
        """绝对值"""
        return np.abs(arr)
    
    def clip(self, arr: np.ndarray, min_val: Optional[float] = None, 
             max_val: Optional[float] = None) -> np.ndarray:
        """裁剪数组值到指定范围"""
        return np.clip(arr, min_val, max_val)
    
    def round(self, arr: np.ndarray, decimals: int = 0) -> np.ndarray:
        """四舍五入"""
        return np.round(arr, decimals)
    
    def floor(self, arr: np.ndarray) -> np.ndarray:
        """向下取整"""
        return np.floor(arr)
    
    def ceil(self, arr: np.ndarray) -> np.ndarray:
        """向上取整"""
        return np.ceil(arr)
    
    # ==================== 线性代数 ====================
    
    def matrix_multiply(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        矩阵乘法
        
        Args:
            a: 第一个矩阵
            b: 第二个矩阵
            
        Returns:
            np.ndarray: 矩阵乘积
        """
        return np.matmul(a, b)
    
    def dot(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        点积运算
        
        Args:
            a: 第一个数组
            b: 第二个数组
            
        Returns:
            np.ndarray: 点积结果
        """
        return np.dot(a, b)
    
    def inner(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        内积运算
        
        Args:
            a: 第一个数组
            b: 第二个数组
            
        Returns:
            np.ndarray: 内积结果
        """
        return np.inner(a, b)
    
    def outer(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        外积运算
        
        Args:
            a: 第一个数组
            b: 第二个数组
            
        Returns:
            np.ndarray: 外积结果
        """
        return np.outer(a, b)
    
    def determinant(self, arr: np.ndarray) -> float:
        """
        计算行列式
        
        Args:
            arr: 方阵
            
        Returns:
            float: 行列式值
        """
        return np.linalg.det(arr)
    
    def inverse(self, arr: np.ndarray) -> np.ndarray:
        """
        计算逆矩阵
        
        Args:
            arr: 方阵
            
        Returns:
            np.ndarray: 逆矩阵
        """
        return np.linalg.inv(arr)
    
    def pseudo_inverse(self, arr: np.ndarray) -> np.ndarray:
        """
        计算伪逆矩阵
        
        Args:
            arr: 输入矩阵
            
        Returns:
            np.ndarray: 伪逆矩阵
        """
        return np.linalg.pinv(arr)
    
    def eigenvalues(self, arr: np.ndarray) -> np.ndarray:
        """
        计算特征值
        
        Args:
            arr: 方阵
            
        Returns:
            np.ndarray: 特征值
        """
        return np.linalg.eigvals(arr)
    
    def eigen_decomposition(self, arr: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        特征值分解
        
        Args:
            arr: 方阵
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (特征值, 特征向量)
        """
        return np.linalg.eig(arr)
    
    def svd(self, arr: np.ndarray, full_matrices: bool = True) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        奇异值分解
        
        Args:
            arr: 输入矩阵
            full_matrices: 是否返回完整矩阵
            
        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: (U, S, Vh)
        """
        return np.linalg.svd(arr, full_matrices=full_matrices)
    
    def qr_decomposition(self, arr: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        QR分解
        
        Args:
            arr: 输入矩阵
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (Q, R)
        """
        return np.linalg.qr(arr)
    
    def cholesky(self, arr: np.ndarray) -> np.ndarray:
        """
        Cholesky分解
        
        Args:
            arr: 正定矩阵
            
        Returns:
            np.ndarray: 下三角矩阵
        """
        return np.linalg.cholesky(arr)
    
    def solve_linear(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        求解线性方程组 ax = b
        
        Args:
            a: 系数矩阵
            b: 常数向量或矩阵
            
        Returns:
            np.ndarray: 解向量
        """
        return np.linalg.solve(a, b)
    
    def least_squares(self, a: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, ...]:
        """
        最小二乘解
        
        Args:
            a: 系数矩阵
            b: 目标向量
            
        Returns:
            Tuple: (解, 残差, 秩, 奇异值)
        """
        return np.linalg.lstsq(a, b, rcond=None)
    
    def norm(self, arr: np.ndarray, ord: Optional[Union[int, str]] = None) -> float:
        """
        计算范数
        
        Args:
            arr: 输入数组
            ord: 范数类型
            
        Returns:
            float: 范数值
        """
        return np.linalg.norm(arr, ord=ord)
    
    def rank(self, arr: np.ndarray) -> int:
        """
        计算矩阵秩
        
        Args:
            arr: 输入矩阵
            
        Returns:
            int: 矩阵秩
        """
        return np.linalg.matrix_rank(arr)
    
    def trace(self, arr: np.ndarray) -> float:
        """
        计算矩阵迹
        
        Args:
            arr: 方阵
            
        Returns:
            float: 迹
        """
        return np.trace(arr)
    
    def diagonal(self, arr: np.ndarray, offset: int = 0) -> np.ndarray:
        """
        获取对角线元素
        
        Args:
            arr: 输入数组
            offset: 对角线偏移
            
        Returns:
            np.ndarray: 对角线元素
        """
        return np.diagonal(arr, offset=offset)
    
    # ==================== 随机数生成 ====================
    
    def random_uniform(self, low: float = 0.0, high: float = 1.0, 
                       size: Optional[Union[int, Tuple[int, ...]]] = None) -> np.ndarray:
        """
        生成均匀分布随机数
        
        Args:
            low: 下限
            high: 上限
            size: 数组形状
            
        Returns:
            np.ndarray: 均匀分布随机数
        """
        return np.random.uniform(low, high, size)
    
    def random_normal(self, loc: float = 0.0, scale: float = 1.0, 
                      size: Optional[Union[int, Tuple[int, ...]]] = None) -> np.ndarray:
        """
        生成正态分布随机数
        
        Args:
            loc: 均值
            scale: 标准差
            size: 数组形状
            
        Returns:
            np.ndarray: 正态分布随机数
        """
        return np.random.normal(loc, scale, size)
    
    def random_integers(self, low: int, high: Optional[int] = None, 
                        size: Optional[Union[int, Tuple[int, ...]]] = None) -> np.ndarray:
        """
        生成随机整数
        
        Args:
            low: 下限（包含）
            high: 上限（不包含）
            size: 数组形状
            
        Returns:
            np.ndarray: 随机整数
        """
        return np.random.randint(low, high, size)
    
    def random_choice(self, a: Union[int, List[Any]], size: Optional[Union[int, Tuple[int, ...]]] = None,
                      replace: bool = True, p: Optional[np.ndarray] = None) -> np.ndarray:
        """
        随机选择
        
        Args:
            a: 数据源或范围
            size: 输出形状
            replace: 是否允许重复
            p: 概率分布
            
        Returns:
            np.ndarray: 随机选择结果
        """
        return np.random.choice(a, size=size, replace=replace, p=p)
    
    def random_shuffle(self, arr: np.ndarray) -> np.ndarray:
        """
        随机打乱数组
        
        Args:
            arr: 输入数组
            
        Returns:
            np.ndarray: 打乱后的数组
        """
        result = arr.copy()
        np.random.shuffle(result)
        return result
    
    def random_permutation(self, n: Union[int, np.ndarray]) -> np.ndarray:
        """
        生成随机排列
        
        Args:
            n: 整数或数组
            
        Returns:
            np.ndarray: 随机排列
        """
        return np.random.permutation(n)
    
    def random_binomial(self, n: int, p: float, size: Optional[Union[int, Tuple[int, ...]]] = None) -> np.ndarray:
        """生成二项分布随机数"""
        return np.random.binomial(n, p, size)
    
    def random_poisson(self, lam: float, size: Optional[Union[int, Tuple[int, ...]]] = None) -> np.ndarray:
        """生成泊松分布随机数"""
        return np.random.poisson(lam, size)
    
    def random_exponential(self, scale: float = 1.0, 
                         size: Optional[Union[int, Tuple[int, ...]]] = None) -> np.ndarray:
        """生成指数分布随机数"""
        return np.random.exponential(scale, size)
    
    def random_beta(self, a: float, b: float, 
                    size: Optional[Union[int, Tuple[int, ...]]] = None) -> np.ndarray:
        """生成Beta分布随机数"""
        return np.random.beta(a, b, size)
    
    def random_gamma(self, shape: float, scale: float = 1.0, 
                     size: Optional[Union[int, Tuple[int, ...]]] = None) -> np.ndarray:
        """生成Gamma分布随机数"""
        return np.random.gamma(shape, scale, size)
    
    # ==================== 聚合统计 ====================
    
    def sum(self, arr: np.ndarray, axis: Optional[int] = None) -> Union[float, np.ndarray]:
        """求和"""
        return np.sum(arr, axis=axis)
    
    def mean(self, arr: np.ndarray, axis: Optional[int] = None) -> Union[float, np.ndarray]:
        """均值"""
        return np.mean(arr, axis=axis)
    
    def std(self, arr: np.ndarray, axis: Optional[int] = None, ddof: int = 0) -> Union[float, np.ndarray]:
        """标准差"""
        return np.std(arr, axis=axis, ddof=ddof)
    
    def var(self, arr: np.ndarray, axis: Optional[int] = None, ddof: int = 0) -> Union[float, np.ndarray]:
        """方差"""
        return np.var(arr, axis=axis, ddof=ddof)
    
    def min(self, arr: np.ndarray, axis: Optional[int] = None) -> Union[float, np.ndarray]:
        """最小值"""
        return np.min(arr, axis=axis)
    
    def max(self, arr: np.ndarray, axis: Optional[int] = None) -> Union[float, np.ndarray]:
        """最大值"""
        return np.max(arr, axis=axis)
    
    def argmin(self, arr: np.ndarray, axis: Optional[int] = None) -> Union[int, np.ndarray]:
        """最小值索引"""
        return np.argmin(arr, axis=axis)
    
    def argmax(self, arr: np.ndarray, axis: Optional[int] = None) -> Union[int, np.ndarray]:
        """最大值索引"""
        return np.argmax(arr, axis=axis)
    
    def median(self, arr: np.ndarray, axis: Optional[int] = None) -> Union[float, np.ndarray]:
        """中位数"""
        return np.median(arr, axis=axis)
    
    def percentile(self, arr: np.ndarray, q: Union[float, List[float]], 
                   axis: Optional[int] = None) -> Union[float, np.ndarray]:
        """百分位数"""
        return np.percentile(arr, q, axis=axis)
    
    def cumsum(self, arr: np.ndarray, axis: Optional[int] = None) -> np.ndarray:
        """累积和"""
        return np.cumsum(arr, axis=axis)
    
    def cumprod(self, arr: np.ndarray, axis: Optional[int] = None) -> np.ndarray:
        """累积积"""
        return np.cumprod(arr, axis=axis)
    
    def diff(self, arr: np.ndarray, n: int = 1, axis: int = -1) -> np.ndarray:
        """差分"""
        return np.diff(arr, n=n, axis=axis)
    
    def gradient(self, arr: np.ndarray, *varargs) -> Union[np.ndarray, List[np.ndarray]]:
        """梯度"""
        return np.gradient(arr, *varargs)
    
    def histogram(self, arr: np.ndarray, bins: Union[int, str] = 10, 
                  range: Optional[Tuple[float, float]] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        计算直方图
        
        Args:
            arr: 输入数组
            bins: 箱数或策略
            range: 值范围
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (频数, 箱边界)
        """
        return np.histogram(arr, bins=bins, range=range)
    
    def bincount(self, arr: np.ndarray, minlength: int = 0) -> np.ndarray:
        """
        计算非负整数数组的频数
        
        Args:
            arr: 非负整数数组
            minlength: 最小输出长度
            
        Returns:
            np.ndarray: 频数数组
        """
        return np.bincount(arr, minlength=minlength)
    
    def unique(self, arr: np.ndarray, return_counts: bool = False) -> Union[np.ndarray, Tuple]:
        """
        获取唯一值
        
        Args:
            arr: 输入数组
            return_counts: 是否返回频数
            
        Returns:
            np.ndarray或Tuple: 唯一值或(唯一值, 频数)
        """
        return np.unique(arr, return_counts=return_counts)
    
    def count_nonzero(self, arr: np.ndarray, axis: Optional[int] = None) -> Union[int, np.ndarray]:
        """计算非零元素个数"""
        return np.count_nonzero(arr, axis=axis)
    
    def allclose(self, a: np.ndarray, b: np.ndarray, rtol: float = 1e-05, 
                 atol: float = 1e-08) -> bool:
        """判断两个数组是否近似相等"""
        return np.allclose(a, b, rtol=rtol, atol=atol)
    
    def isclose(self, a: np.ndarray, b: np.ndarray, rtol: float = 1e-05, 
                atol: float = 1e-08) -> np.ndarray:
        """元素级判断是否近似相等"""
        return np.isclose(a, b, rtol=rtol, atol=atol)
    
    def save_array(self, arr: np.ndarray, filepath: str):
        """保存数组到.npy文件"""
        np.save(filepath, arr)
    
    def load_array(self, filepath: str) -> np.ndarray:
        """从.npy文件加载数组"""
        return np.load(filepath)


# ==================== 便捷函数 ====================

def array(data: Union[List, Tuple], dtype: Optional[str] = None) -> np.ndarray:
    """快速创建数组"""
    return np.array(data, dtype=dtype)


def zeros(shape: Union[int, Tuple[int, ...]], dtype: Optional[str] = None) -> np.ndarray:
    """快速创建全零数组"""
    return np.zeros(shape, dtype=dtype)


def ones(shape: Union[int, Tuple[int, ...]], dtype: Optional[str] = None) -> np.ndarray:
    """快速创建全一阵列"""
    return np.ones(shape, dtype=dtype)


def arange(start: int, stop: Optional[int] = None, step: int = 1) -> np.ndarray:
    """快速创建等差数列"""
    return np.arange(start, stop, step)


def linspace(start: float, stop: float, num: int = 50) -> np.ndarray:
    """快速创建等间隔数列"""
    return np.linspace(start, stop, num)


if __name__ == "__main__":
    # 简单的自我测试
    print("NumPy Skill 测试")
    print("=" * 40)
    
    skill = NumpySkill(seed=42)
    
    # 测试数组创建
    arr = skill.create_array([[1, 2, 3], [4, 5, 6]])
    print(f"数组:\n{arr}")
    print(f"形状: {arr.shape}")
    
    # 测试数学运算
    print(f"\n转置:\n{skill.transpose(arr)}")
    print(f"求和: {skill.sum(arr)}")
    print(f"均值: {skill.mean(arr)}")
    
    # 测试随机数
    random_arr = skill.random_normal(0, 1, (2, 3))
    print(f"\n随机数组:\n{random_arr}")
    
    print("\nNumPy Skill 测试完成!")
