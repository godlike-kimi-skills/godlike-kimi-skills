#!/usr/bin/env python3
"""
Pandas Skill - Test Suite
Pandas技能测试套件
"""

import unittest
import pandas as pd
import numpy as np
import os
import tempfile
import shutil
from pathlib import Path

from main import PandasSkill, quick_load, quick_save


class TestPandasSkill(unittest.TestCase):
    """PandasSkill测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.skill = PandasSkill()
        cls.test_dir = tempfile.mkdtemp()
        
        # 创建测试数据
        cls.test_data = {
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
            'age': [25, 30, 35, 28, 32],
            'salary': [50000.0, 60000.0, 75000.0, 55000.0, 65000.0],
            'department': ['IT', 'HR', 'IT', 'Finance', 'HR']
        }
        cls.df = pd.DataFrame(cls.test_data)
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    def setUp(self):
        """每个测试前执行"""
        self.skill.clear_history()
    
    # ==================== 数据加载测试 ====================
    
    def test_load_csv(self):
        """测试CSV加载"""
        filepath = os.path.join(self.test_dir, 'test.csv')
        self.df.to_csv(filepath, index=False)
        
        loaded_df = self.skill.load_csv(filepath)
        self.assertEqual(len(loaded_df), len(self.df))
        self.assertListEqual(list(loaded_df.columns), list(self.df.columns))
    
    def test_load_excel(self):
        """测试Excel加载"""
        filepath = os.path.join(self.test_dir, 'test.xlsx')
        self.df.to_excel(filepath, index=False)
        
        loaded_df = self.skill.load_excel(filepath)
        self.assertEqual(len(loaded_df), len(self.df))
    
    def test_load_json(self):
        """测试JSON加载"""
        filepath = os.path.join(self.test_dir, 'test.json')
        self.df.to_json(filepath, orient='records')
        
        loaded_df = self.skill.load_json(filepath)
        self.assertEqual(len(loaded_df), len(self.df))
    
    # ==================== 数据保存测试 ====================
    
    def test_save_csv(self):
        """测试CSV保存"""
        filepath = os.path.join(self.test_dir, 'output.csv')
        self.skill.save_csv(self.df, filepath)
        
        self.assertTrue(os.path.exists(filepath))
        loaded = pd.read_csv(filepath)
        self.assertEqual(len(loaded), len(self.df))
    
    def test_save_excel(self):
        """测试Excel保存"""
        filepath = os.path.join(self.test_dir, 'output.xlsx')
        self.skill.save_excel(self.df, filepath)
        
        self.assertTrue(os.path.exists(filepath))
        loaded = pd.read_excel(filepath)
        self.assertEqual(len(loaded), len(self.df))
    
    def test_save_json(self):
        """测试JSON保存"""
        filepath = os.path.join(self.test_dir, 'output.json')
        self.skill.save_json(self.df, filepath)
        
        self.assertTrue(os.path.exists(filepath))
        loaded = pd.read_json(filepath)
        self.assertEqual(len(loaded), len(self.df))
    
    # ==================== 数据清洗测试 ====================
    
    def test_remove_duplicates(self):
        """测试删除重复值"""
        df_with_dups = pd.concat([self.df, self.df.iloc[:2]], ignore_index=True)
        self.assertEqual(len(df_with_dups), 7)
        
        df_clean = self.skill.remove_duplicates(df_with_dups)
        self.assertEqual(len(df_clean), 5)
    
    def test_fill_missing_mean(self):
        """测试均值填充缺失值"""
        df_with_nan = self.df.copy()
        df_with_nan.loc[0, 'age'] = np.nan
        df_with_nan.loc[1, 'salary'] = np.nan
        
        df_filled = self.skill.fill_missing(df_with_nan, strategy='mean')
        self.assertFalse(df_filled['age'].isnull().any())
        self.assertFalse(df_filled['salary'].isnull().any())
    
    def test_fill_missing_constant(self):
        """测试常数填充缺失值"""
        df_with_nan = self.df.copy()
        df_with_nan.loc[0, 'name'] = np.nan
        
        df_filled = self.skill.fill_missing(df_with_nan, strategy='constant', fill_value='Unknown')
        self.assertEqual(df_filled.loc[0, 'name'], 'Unknown')
    
    def test_drop_missing(self):
        """测试删除缺失值"""
        df_with_nan = self.df.copy()
        df_with_nan.loc[0, 'age'] = np.nan
        df_with_nan.loc[1, 'age'] = np.nan
        
        df_clean = self.skill.drop_missing(df_with_nan)
        self.assertEqual(len(df_clean), 3)
    
    def test_remove_outliers_iqr(self):
        """测试IQR方法移除异常值"""
        df_with_outliers = self.df.copy()
        df_with_outliers = pd.concat([
            df_with_outliers,
            pd.DataFrame({'id': [99], 'name': ['Outlier'], 'age': [999], 'salary': [999999], 'department': ['IT']})
        ], ignore_index=True)
        
        df_clean = self.skill.remove_outliers(df_with_outliers, columns=['age', 'salary'])
        self.assertLess(len(df_clean), len(df_with_outliers))
    
    # ==================== 数据转换测试 ====================
    
    def test_filter_rows(self):
        """测试行过滤"""
        filtered = self.skill.filter_rows(self.df, "age > 28")
        self.assertEqual(len(filtered), 3)
        self.assertTrue(all(filtered['age'] > 28))
    
    def test_sort_by(self):
        """测试排序"""
        sorted_df = self.skill.sort_by(self.df, by='age', ascending=False)
        self.assertEqual(sorted_df.iloc[0]['age'], 35)
        self.assertEqual(sorted_df.iloc[-1]['age'], 25)
    
    def test_group_and_aggregate(self):
        """测试分组聚合"""
        grouped = self.skill.group_and_aggregate(
            self.df, 
            by='department', 
            agg={'salary': 'mean', 'age': 'max'}
        )
        self.assertIn('salary', grouped.columns.get_level_values(0))
        self.assertEqual(len(grouped), 3)  # IT, HR, Finance
    
    def test_pivot_table(self):
        """测试透视表"""
        pivot = self.skill.pivot_table(
            self.df,
            values='salary',
            index='department',
            aggfunc='mean'
        )
        self.assertEqual(len(pivot), 3)
    
    def test_merge_dataframes(self):
        """测试数据框合并"""
        df_left = self.df[['id', 'name']].copy()
        df_right = self.df[['id', 'department']].copy()
        
        merged = self.skill.merge_dataframes(df_left, df_right, on='id')
        self.assertEqual(len(merged), 5)
        self.assertIn('name', merged.columns)
        self.assertIn('department', merged.columns)
    
    # ==================== 统计分析测试 ====================
    
    def test_describe(self):
        """测试描述性统计"""
        stats = self.skill.describe(self.df)
        self.assertIn('mean', stats.index)
        self.assertIn('std', stats.index)
        self.assertIn('age', stats.columns)
        self.assertIn('salary', stats.columns)
    
    def test_correlation(self):
        """测试相关性计算"""
        corr = self.skill.correlation(self.df)
        self.assertIn('age', corr.columns)
        self.assertIn('salary', corr.columns)
        self.assertAlmostEqual(corr.loc['age', 'age'], 1.0)
    
    def test_group_stats(self):
        """测试分组统计"""
        stats = self.skill.group_stats(self.df, by='department')
        self.assertIsInstance(stats, pd.DataFrame)
    
    def test_value_counts(self):
        """测试值计数"""
        counts = self.skill.value_counts(self.df, 'department')
        self.assertEqual(counts['HR'], 2)
        self.assertEqual(counts['IT'], 2)
    
    # ==================== 工具方法测试 ====================
    
    def test_get_info(self):
        """测试获取数据框信息"""
        info = self.skill.get_info(self.df)
        self.assertIn('shape', info)
        self.assertIn('columns', info)
        self.assertIn('dtypes', info)
        self.assertEqual(info['shape'], (5, 5))
    
    def test_get_history(self):
        """测试操作历史"""
        self.skill.describe(self.df)
        history = self.skill.get_history()
        self.assertGreater(len(history), 0)
        self.assertIn('operation', history[0])
    
    # ==================== 便捷函数测试 ====================
    
    def test_quick_load_csv(self):
        """测试快速加载CSV"""
        filepath = os.path.join(self.test_dir, 'quick.csv')
        self.df.to_csv(filepath, index=False)
        
        loaded = quick_load(filepath)
        self.assertEqual(len(loaded), len(self.df))
    
    def test_quick_save_csv(self):
        """测试快速保存CSV"""
        filepath = os.path.join(self.test_dir, 'quick_save.csv')
        quick_save(self.df, filepath)
        
        self.assertTrue(os.path.exists(filepath))


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""
    
    def setUp(self):
        self.skill = PandasSkill()
    
    def test_empty_dataframe(self):
        """测试空数据框"""
        df = pd.DataFrame()
        info = self.skill.get_info(df)
        self.assertEqual(info['shape'], (0, 0))
    
    def test_single_row(self):
        """测试单行数据"""
        df = pd.DataFrame({'a': [1], 'b': [2]})
        stats = self.skill.describe(df)
        self.assertIsInstance(stats, pd.DataFrame)
    
    def test_all_missing_column(self):
        """测试全缺失列"""
        df = pd.DataFrame({'a': [1, 2, 3], 'b': [np.nan, np.nan, np.nan]})
        df_filled = self.skill.fill_missing(df, strategy='mean')
        self.assertTrue(df_filled['b'].isnull().all())
    
    def test_no_numeric_columns(self):
        """测试无数值列"""
        df = pd.DataFrame({'a': ['x', 'y', 'z'], 'b': ['a', 'b', 'c']})
        corr = self.skill.correlation(df)
        self.assertTrue(corr.empty)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestPandasSkill))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
