#!/usr/bin/env python3
"""
Pandas Skill - Main Implementation
Pandas数据分析技能主实现文件

功能：Pandas数据分析。支持数据清洗、转换、统计分析。
Use when analyzing data, creating visualizations, or when user mentions 'pandas', 'data analysis', 'data cleaning', 'dataframe'.

Author: Kimi Skills
Version: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Callable, Any
from pathlib import Path
import json
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')


class PandasSkill:
    """
    Pandas数据分析技能类
    
    提供完整的数据分析功能，包括：
    - 数据加载与保存
    - 数据清洗
    - 数据转换
    - 统计分析
    - 数据导出
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化PandasSkill
        
        Args:
            config_path: 配置文件路径，默认使用config.json
        """
        self.config = self._load_config(config_path)
        self._setup_display()
        self.history = []
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        if config_path is None:
            config_path = Path(__file__).parent / "config.json"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            "default_encoding": "utf-8",
            "max_rows_display": 100,
            "max_columns_display": 50,
            "float_format": "%.4f"
        }
    
    def _setup_display(self):
        """设置pandas显示选项"""
        pd.set_option('display.max_rows', self.config.get('max_rows_display', 100))
        pd.set_option('display.max_columns', self.config.get('max_columns_display', 50))
        pd.set_option('display.float_format', lambda x: self.config.get('float_format', '%.4f') % x)
        pd.set_option('display.width', self.config.get('display_width', 120))
    
    def _log_operation(self, operation: str, details: Dict):
        """记录操作历史"""
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'details': details
        })
    
    # ==================== 数据加载 ====================
    
    def load_csv(self, filepath: str, **kwargs) -> pd.DataFrame:
        """
        从CSV文件加载数据
        
        Args:
            filepath: CSV文件路径
            **kwargs: 传递给pd.read_csv的额外参数
            
        Returns:
            pd.DataFrame: 加载的数据框
        """
        encoding = kwargs.pop('encoding', self.config.get('default_encoding', 'utf-8'))
        try:
            df = pd.read_csv(filepath, encoding=encoding, **kwargs)
            self._log_operation('load_csv', {'filepath': filepath, 'rows': len(df)})
            return df
        except Exception as e:
            raise ValueError(f"无法加载CSV文件 {filepath}: {e}")
    
    def load_excel(self, filepath: str, sheet_name: Union[str, int] = 0, **kwargs) -> pd.DataFrame:
        """
        从Excel文件加载数据
        
        Args:
            filepath: Excel文件路径
            sheet_name: 工作表名称或索引
            **kwargs: 传递给pd.read_excel的额外参数
            
        Returns:
            pd.DataFrame: 加载的数据框
        """
        try:
            df = pd.read_excel(filepath, sheet_name=sheet_name, **kwargs)
            self._log_operation('load_excel', {'filepath': filepath, 'sheet': sheet_name, 'rows': len(df)})
            return df
        except Exception as e:
            raise ValueError(f"无法加载Excel文件 {filepath}: {e}")
    
    def load_json(self, filepath: str, **kwargs) -> pd.DataFrame:
        """
        从JSON文件加载数据
        
        Args:
            filepath: JSON文件路径
            **kwargs: 传递给pd.read_json的额外参数
            
        Returns:
            pd.DataFrame: 加载的数据框
        """
        try:
            df = pd.read_json(filepath, **kwargs)
            self._log_operation('load_json', {'filepath': filepath, 'rows': len(df)})
            return df
        except Exception as e:
            raise ValueError(f"无法加载JSON文件 {filepath}: {e}")
    
    def load_sql(self, query: str, connection, **kwargs) -> pd.DataFrame:
        """
        从SQL数据库加载数据
        
        Args:
            query: SQL查询语句
            connection: 数据库连接对象
            **kwargs: 传递给pd.read_sql的额外参数
            
        Returns:
            pd.DataFrame: 加载的数据框
        """
        try:
            df = pd.read_sql(query, connection, **kwargs)
            self._log_operation('load_sql', {'query': query[:100], 'rows': len(df)})
            return df
        except Exception as e:
            raise ValueError(f"无法执行SQL查询: {e}")
    
    # ==================== 数据保存 ====================
    
    def save_csv(self, df: pd.DataFrame, filepath: str, **kwargs) -> None:
        """
        保存数据到CSV文件
        
        Args:
            df: 要保存的数据框
            filepath: 目标文件路径
            **kwargs: 传递给to_csv的额外参数
        """
        index = kwargs.pop('index', False)
        encoding = kwargs.pop('encoding', self.config.get('default_encoding', 'utf-8'))
        df.to_csv(filepath, index=index, encoding=encoding, **kwargs)
        self._log_operation('save_csv', {'filepath': filepath, 'rows': len(df)})
    
    def save_excel(self, df: pd.DataFrame, filepath: str, sheet_name: str = 'Sheet1', **kwargs) -> None:
        """
        保存数据到Excel文件
        
        Args:
            df: 要保存的数据框
            filepath: 目标文件路径
            sheet_name: 工作表名称
            **kwargs: 传递给to_excel的额外参数
        """
        index = kwargs.pop('index', False)
        df.to_excel(filepath, sheet_name=sheet_name, index=index, **kwargs)
        self._log_operation('save_excel', {'filepath': filepath, 'sheet': sheet_name, 'rows': len(df)})
    
    def save_json(self, df: pd.DataFrame, filepath: str, **kwargs) -> None:
        """
        保存数据到JSON文件
        
        Args:
            df: 要保存的数据框
            filepath: 目标文件路径
            **kwargs: 传递给to_json的额外参数
        """
        orient = kwargs.pop('orient', 'records')
        df.to_json(filepath, orient=orient, **kwargs)
        self._log_operation('save_json', {'filepath': filepath, 'rows': len(df)})
    
    # ==================== 数据清洗 ====================
    
    def remove_duplicates(self, df: pd.DataFrame, subset: Optional[List[str]] = None, 
                          keep: str = 'first') -> pd.DataFrame:
        """
        删除重复行
        
        Args:
            df: 输入数据框
            subset: 用于判断重复的列名列表
            keep: 保留哪个重复项 ('first', 'last', False)
            
        Returns:
            pd.DataFrame: 去重后的数据框
        """
        before_count = len(df)
        df_clean = df.drop_duplicates(subset=subset, keep=keep)
        after_count = len(df_clean)
        self._log_operation('remove_duplicates', {'before': before_count, 'after': after_count})
        return df_clean
    
    def fill_missing(self, df: pd.DataFrame, strategy: str = 'mean', 
                     fill_value: Optional[Any] = None, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        填充缺失值
        
        Args:
            df: 输入数据框
            strategy: 填充策略 ('mean', 'median', 'mode', 'constant', 'ffill', 'bfill')
            fill_value: 当strategy='constant'时的填充值
            columns: 要填充的列，None表示所有列
            
        Returns:
            pd.DataFrame: 填充后的数据框
        """
        df_filled = df.copy()
        target_cols = columns if columns else df.columns
        
        for col in target_cols:
            if df[col].isnull().sum() == 0:
                continue
                
            if strategy == 'mean' and df[col].dtype in ['int64', 'float64']:
                df_filled[col] = df[col].fillna(df[col].mean())
            elif strategy == 'median' and df[col].dtype in ['int64', 'float64']:
                df_filled[col] = df[col].fillna(df[col].median())
            elif strategy == 'mode':
                df_filled[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else None)
            elif strategy == 'constant':
                df_filled[col] = df[col].fillna(fill_value)
            elif strategy == 'ffill':
                df_filled[col] = df[col].fillna(method='ffill')
            elif strategy == 'bfill':
                df_filled[col] = df[col].fillna(method='bfill')
        
        self._log_operation('fill_missing', {'strategy': strategy, 'columns': len(target_cols)})
        return df_filled
    
    def drop_missing(self, df: pd.DataFrame, axis: int = 0, 
                     how: str = 'any', thresh: Optional[int] = None) -> pd.DataFrame:
        """
        删除包含缺失值的行或列
        
        Args:
            df: 输入数据框
            axis: 0删除行，1删除列
            how: 'any'表示有缺失就删除，'all'表示全部缺失才删除
            thresh: 非缺失值最小数量
            
        Returns:
            pd.DataFrame: 处理后的数据框
        """
        before_shape = df.shape
        df_clean = df.dropna(axis=axis, how=how, thresh=thresh)
        after_shape = df_clean.shape
        self._log_operation('drop_missing', {'before': before_shape, 'after': after_shape})
        return df_clean
    
    def remove_outliers(self, df: pd.DataFrame, columns: List[str], 
                        method: str = 'iqr', threshold: float = 1.5) -> pd.DataFrame:
        """
        移除异常值
        
        Args:
            df: 输入数据框
            columns: 要处理的数值列
            method: 检测方法 ('iqr', 'zscore')
            threshold: 阈值
            
        Returns:
            pd.DataFrame: 移除异常值后的数据框
        """
        df_clean = df.copy()
        mask = pd.Series([True] * len(df), index=df.index)
        
        for col in columns:
            if df[col].dtype not in ['int64', 'float64']:
                continue
                
            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - threshold * IQR
                upper = Q3 + threshold * IQR
                mask &= (df[col] >= lower) & (df[col] <= upper)
            elif method == 'zscore':
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                mask &= (z_scores < threshold)
        
        df_clean = df_clean[mask]
        self._log_operation('remove_outliers', {'before': len(df), 'after': len(df_clean)})
        return df_clean
    
    # ==================== 数据转换 ====================
    
    def filter_rows(self, df: pd.DataFrame, condition: str) -> pd.DataFrame:
        """
        根据条件过滤行
        
        Args:
            df: 输入数据框
            condition: 查询条件字符串
            
        Returns:
            pd.DataFrame: 过滤后的数据框
        """
        try:
            result = df.query(condition)
            self._log_operation('filter_rows', {'condition': condition, 'result_rows': len(result)})
            return result
        except Exception as e:
            raise ValueError(f"过滤条件无效: {e}")
    
    def sort_by(self, df: pd.DataFrame, by: Union[str, List[str]], 
                ascending: Union[bool, List[bool]] = True) -> pd.DataFrame:
        """
        排序数据
        
        Args:
            df: 输入数据框
            by: 排序列名
            ascending: 是否升序
            
        Returns:
            pd.DataFrame: 排序后的数据框
        """
        result = df.sort_values(by=by, ascending=ascending)
        self._log_operation('sort_by', {'by': by, 'ascending': ascending})
        return result
    
    def group_and_aggregate(self, df: pd.DataFrame, by: Union[str, List[str]], 
                           agg: Dict[str, Union[str, List[str]]]) -> pd.DataFrame:
        """
        分组聚合
        
        Args:
            df: 输入数据框
            by: 分组列
            agg: 聚合规则字典，如 {'col': 'mean', 'col2': ['min', 'max']}
            
        Returns:
            pd.DataFrame: 聚合结果
        """
        result = df.groupby(by).agg(agg)
        self._log_operation('group_and_aggregate', {'by': by, 'agg': agg})
        return result
    
    def pivot_table(self, df: pd.DataFrame, values: Optional[Union[str, List[str]]] = None,
                    index: Optional[Union[str, List[str]]] = None,
                    columns: Optional[Union[str, List[str]]] = None,
                    aggfunc: Union[str, Callable] = 'mean') -> pd.DataFrame:
        """
        创建透视表
        
        Args:
            df: 输入数据框
            values: 值列
            index: 行索引列
            columns: 列索引列
            aggfunc: 聚合函数
            
        Returns:
            pd.DataFrame: 透视表
        """
        result = pd.pivot_table(df, values=values, index=index, columns=columns, aggfunc=aggfunc)
        self._log_operation('pivot_table', {'values': values, 'index': index, 'columns': columns})
        return result
    
    def merge_dataframes(self, left: pd.DataFrame, right: pd.DataFrame, 
                         on: Optional[Union[str, List[str]]] = None,
                         how: str = 'inner', left_on: Optional[str] = None,
                         right_on: Optional[str] = None) -> pd.DataFrame:
        """
        合并数据框
        
        Args:
            left: 左数据框
            right: 右数据框
            on: 连接键
            how: 连接方式 ('inner', 'outer', 'left', 'right')
            left_on: 左表连接键
            right_on: 右表连接键
            
        Returns:
            pd.DataFrame: 合并后的数据框
        """
        result = pd.merge(left, right, on=on, how=how, left_on=left_on, right_on=right_on)
        self._log_operation('merge_dataframes', {'how': how, 'on': on, 'result_rows': len(result)})
        return result
    
    # ==================== 统计分析 ====================
    
    def describe(self, df: pd.DataFrame, include: Optional[str] = None) -> pd.DataFrame:
        """
        描述性统计
        
        Args:
            df: 输入数据框
            include: 包含的数据类型 ('all', 'number', 'object')
            
        Returns:
            pd.DataFrame: 统计摘要
        """
        result = df.describe(include=include)
        self._log_operation('describe', {'columns': len(df.columns)})
        return result
    
    def correlation(self, df: pd.DataFrame, method: str = 'pearson',
                    columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        计算相关性矩阵
        
        Args:
            df: 输入数据框
            method: 计算方法 ('pearson', 'spearman', 'kendall')
            columns: 要计算的数值列
            
        Returns:
            pd.DataFrame: 相关性矩阵
        """
        if columns:
            df = df[columns]
        numeric_df = df.select_dtypes(include=[np.number])
        result = numeric_df.corr(method=method)
        self._log_operation('correlation', {'method': method})
        return result
    
    def group_stats(self, df: pd.DataFrame, by: Union[str, List[str]]) -> pd.DataFrame:
        """
        分组统计
        
        Args:
            df: 输入数据框
            by: 分组列
            
        Returns:
            pd.DataFrame: 分组统计结果
        """
        result = df.groupby(by).describe()
        self._log_operation('group_stats', {'by': by})
        return result
    
    def value_counts(self, df: pd.DataFrame, column: str, 
                     normalize: bool = False) -> pd.Series:
        """
        统计唯一值出现次数
        
        Args:
            df: 输入数据框
            column: 列名
            normalize: 是否返回比例
            
        Returns:
            pd.Series: 计数结果
        """
        result = df[column].value_counts(normalize=normalize)
        self._log_operation('value_counts', {'column': column})
        return result
    
    # ==================== 工具方法 ====================
    
    def get_info(self, df: pd.DataFrame) -> Dict:
        """
        获取数据框信息
        
        Args:
            df: 输入数据框
            
        Returns:
            Dict: 数据框信息字典
        """
        info = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'missing_values': df.isnull().sum().to_dict(),
            'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict()
        }
        return info
    
    def get_history(self) -> List[Dict]:
        """获取操作历史"""
        return self.history
    
    def clear_history(self):
        """清空操作历史"""
        self.history = []


# ==================== 便捷函数 ====================

def quick_load(filepath: str) -> pd.DataFrame:
    """快速加载数据文件"""
    skill = PandasSkill()
    ext = Path(filepath).suffix.lower()
    
    if ext == '.csv':
        return skill.load_csv(filepath)
    elif ext in ['.xls', '.xlsx']:
        return skill.load_excel(filepath)
    elif ext == '.json':
        return skill.load_json(filepath)
    else:
        raise ValueError(f"不支持的文件格式: {ext}")


def quick_save(df: pd.DataFrame, filepath: str):
    """快速保存数据文件"""
    skill = PandasSkill()
    ext = Path(filepath).suffix.lower()
    
    if ext == '.csv':
        skill.save_csv(df, filepath)
    elif ext in ['.xls', '.xlsx']:
        skill.save_excel(df, filepath)
    elif ext == '.json':
        skill.save_json(df, filepath)
    else:
        raise ValueError(f"不支持的文件格式: {ext}")


if __name__ == "__main__":
    # 简单的自我测试
    print("Pandas Skill 测试")
    print("=" * 40)
    
    skill = PandasSkill()
    
    # 创建测试数据
    data = {
        'A': [1, 2, 3, 4, 5],
        'B': ['a', 'b', 'c', 'd', 'e'],
        'C': [1.1, 2.2, 3.3, 4.4, 5.5]
    }
    df = pd.DataFrame(data)
    
    print("原始数据:")
    print(df)
    print(f"\n数据信息: {skill.get_info(df)}")
    print(f"\n描述统计:\n{skill.describe(df)}")
    
    print("\nPandas Skill 测试完成!")
