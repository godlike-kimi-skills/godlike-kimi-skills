#!/usr/bin/env python3
"""
Pandas Skill Usage Examples
展示Pandas Skill的各种使用场景
"""

from main import PandasSkill
import pandas as pd
import numpy as np


def example_basic_loading():
    """示例：基本数据加载"""
    print("=" * 60)
    print("示例1: 基本数据加载")
    print("=" * 60)
    
    skill = PandasSkill()
    
    # 创建示例数据
    data = {
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
        'age': [25, 30, 35, 28, 32],
        'salary': [50000, 60000, 75000, 55000, 65000],
        'department': ['IT', 'HR', 'IT', 'Finance', 'HR']
    }
    
    df = pd.DataFrame(data)
    print("原始数据:")
    print(df)
    
    # 保存为CSV
    df.to_csv('sample_data.csv', index=False)
    print("\n数据已保存到 sample_data.csv")
    
    # 重新加载
    df_loaded = skill.load_csv('sample_data.csv')
    print("\n重新加载的数据:")
    print(df_loaded)
    
    return df


def example_data_cleaning():
    """示例：数据清洗"""
    print("\n" + "=" * 60)
    print("示例2: 数据清洗")
    print("=" * 60)
    
    skill = PandasSkill()
    
    # 创建包含脏数据的数据集
    data = {
        'A': [1, 2, np.nan, 4, 5, 2, np.nan],
        'B': ['a', 'b', 'c', 'a', 'b', 'b', 'c'],
        'C': [10, 20, 30, np.nan, 50, 20, 30]
    }
    df = pd.DataFrame(data)
    
    print("原始脏数据:")
    print(df)
    print(f"\n数据形状: {df.shape}")
    print(f"缺失值统计:\n{df.isnull().sum()}")
    
    # 处理缺失值
    df_filled = skill.fill_missing(df, strategy='mean')
    print("\n填充缺失值后:")
    print(df_filled)
    
    # 删除重复值
    df_clean = skill.remove_duplicates(df_filled, subset=['B', 'C'])
    print("\n删除重复值后:")
    print(df_clean)
    
    return df_clean


def example_data_transformation():
    """示例：数据转换"""
    print("\n" + "=" * 60)
    print("示例3: 数据转换")
    print("=" * 60)
    
    skill = PandasSkill()
    
    # 创建示例数据
    data = {
        'product': ['A', 'B', 'A', 'C', 'B', 'A', 'C'],
        'region': ['East', 'West', 'East', 'North', 'West', 'South', 'East'],
        'sales': [100, 150, 200, 120, 180, 90, 160],
        'quantity': [10, 15, 20, 12, 18, 9, 16]
    }
    df = pd.DataFrame(data)
    
    print("原始销售数据:")
    print(df)
    
    # 分组聚合
    grouped = skill.group_and_aggregate(df, by='product', agg={'sales': 'sum', 'quantity': 'mean'})
    print("\n按产品分组聚合:")
    print(grouped)
    
    # 透视表
    pivot = skill.pivot_table(df, values='sales', index='product', columns='region', aggfunc='sum')
    print("\n销售透视表:")
    print(pivot)
    
    # 添加计算列
    df['revenue'] = df['sales'] * df['quantity']
    print("\n添加收入列后:")
    print(df)
    
    return df


def example_statistical_analysis():
    """示例：统计分析"""
    print("\n" + "=" * 60)
    print("示例4: 统计分析")
    print("=" * 60)
    
    skill = PandasSkill()
    
    # 创建数值数据
    np.random.seed(42)
    data = {
        'feature1': np.random.normal(100, 15, 100),
        'feature2': np.random.normal(50, 10, 100),
        'feature3': np.random.normal(200, 30, 100),
        'category': np.random.choice(['A', 'B', 'C'], 100)
    }
    df = pd.DataFrame(data)
    
    print("数据统计摘要:")
    stats = skill.describe(df)
    print(stats)
    
    # 相关性分析
    print("\n特征相关性:")
    corr = skill.correlation(df, method='pearson')
    print(corr)
    
    # 分组统计
    print("\n按类别分组统计:")
    group_stats = skill.group_stats(df, by='category')
    print(group_stats)
    
    return df


def example_advanced_operations():
    """示例：高级操作"""
    print("\n" + "=" * 60)
    print("示例5: 高级操作")
    print("=" * 60)
    
    skill = PandasSkill()
    
    # 创建两个数据集
    df1 = pd.DataFrame({
        'id': [1, 2, 3, 4],
        'name': ['Alice', 'Bob', 'Charlie', 'David'],
        'score': [85, 90, 78, 92]
    })
    
    df2 = pd.DataFrame({
        'id': [2, 3, 4, 5],
        'department': ['IT', 'HR', 'Finance', 'Marketing'],
        'salary': [5000, 4500, 6000, 4800]
    })
    
    print("数据集1:")
    print(df1)
    print("\n数据集2:")
    print(df2)
    
    # 合并数据
    merged = skill.merge_dataframes(df1, df2, on='id', how='inner')
    print("\n内连接结果:")
    print(merged)
    
    # 过滤数据
    filtered = skill.filter_rows(df1, condition="score > 80")
    print("\n分数大于80的记录:")
    print(filtered)
    
    # 排序
    sorted_df = skill.sort_by(df1, by='score', ascending=False)
    print("\n按分数降序排序:")
    print(sorted_df)
    
    return merged


def main():
    """主函数：运行所有示例"""
    try:
        example_basic_loading()
        example_data_cleaning()
        example_data_transformation()
        example_statistical_analysis()
        example_advanced_operations()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"运行示例时出错: {e}")
        raise


if __name__ == "__main__":
    main()
