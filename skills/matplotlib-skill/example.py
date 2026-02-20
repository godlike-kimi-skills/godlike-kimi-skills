#!/usr/bin/env python3
"""
Matplotlib Skill Usage Examples
展示Matplotlib Skill的各种使用场景
"""

from main import MatplotlibSkill
import numpy as np


def example_line_plots():
    """示例：折线图"""
    print("=" * 60)
    print("示例1: 折线图")
    print("=" * 60)
    
    skill = MatplotlibSkill()
    
    # 生成数据
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    # 创建折线图
    skill.line_plot(x, y1, label='sin(x)', color='blue', linewidth=2)
    skill.add_line(x, y2, label='cos(x)', color='red', linestyle='--', linewidth=2)
    
    # 设置标题和标签
    skill.set_title('Trigonometric Functions')
    skill.set_xlabel('x (radians)')
    skill.set_ylabel('y')
    skill.add_legend()
    skill.add_grid(True)
    
    # 保存
    skill.save_figure('example_line_plot.png')
    print("折线图已保存到 example_line_plot.png")
    skill.close()


def example_bar_charts():
    """示例：柱状图"""
    print("\n" + "=" * 60)
    print("示例2: 柱状图")
    print("=" * 60)
    
    skill = MatplotlibSkill()
    
    # 数据
    categories = ['Product A', 'Product B', 'Product C', 'Product D']
    sales_2023 = [450, 520, 380, 600]
    sales_2024 = [480, 580, 420, 650]
    
    # 创建分组柱状图
    skill.grouped_bar_chart(
        categories=categories,
        values_list=[sales_2023, sales_2024],
        labels=['2023', '2024'],
        title='Sales Comparison',
        xlabel='Products',
        ylabel='Sales (units)'
    )
    
    skill.save_figure('example_bar_chart.png')
    print("柱状图已保存到 example_bar_chart.png")
    skill.close()


def example_scatter_plots():
    """示例：散点图"""
    print("\n" + "=" * 60)
    print("示例3: 散点图")
    print("=" * 60)
    
    skill = MatplotlibSkill()
    
    # 生成随机数据
    np.random.seed(42)
    n = 100
    x = np.random.randn(n)
    y = 2 * x + np.random.randn(n) * 0.5
    colors = np.random.rand(n)
    sizes = 100 + 500 * np.random.rand(n)
    
    # 创建散点图
    skill.scatter_plot(
        x, y,
        colors=colors,
        sizes=sizes,
        cmap='viridis',
        alpha=0.6,
        title='Scatter Plot with Color Mapping',
        xlabel='X Variable',
        ylabel='Y Variable'
    )
    skill.add_colorbar(label='Color Scale')
    
    skill.save_figure('example_scatter.png')
    print("散点图已保存到 example_scatter.png")
    skill.close()


def example_pie_charts():
    """示例：饼图"""
    print("\n" + "=" * 60)
    print("示例4: 饼图")
    print("=" * 60)
    
    skill = MatplotlibSkill()
    
    # 数据
    labels = ['Desktop', 'Mobile', 'Tablet', 'Other']
    sizes = [55, 30, 10, 5]
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
    explode = (0.05, 0, 0, 0)  # 突出显示第一个扇形
    
    skill.pie_chart(
        sizes=sizes,
        labels=labels,
        colors=colors,
        explode=explode,
        autopct='%1.1f%%',
        title='Device Usage Distribution',
        shadow=True,
        startangle=90
    )
    
    skill.save_figure('example_pie_chart.png')
    print("饼图已保存到 example_pie_chart.png")
    skill.close()


def example_histograms():
    """示例：直方图"""
    print("\n" + "=" * 60)
    print("示例5: 直方图")
    print("=" * 60)
    
    skill = MatplotlibSkill()
    
    # 生成数据
    np.random.seed(42)
    data1 = np.random.normal(100, 15, 1000)
    data2 = np.random.normal(120, 20, 1000)
    
    skill.histogram(
        [data1, data2],
        bins=30,
        labels=['Group A', 'Group B'],
        colors=['skyblue', 'lightcoral'],
        alpha=0.7,
        title='Distribution Comparison',
        xlabel='Value',
        ylabel='Frequency',
        kde=True
    )
    
    skill.save_figure('example_histogram.png')
    print("直方图已保存到 example_histogram.png")
    skill.close()


def example_subplots():
    """示例：子图"""
    print("\n" + "=" * 60)
    print("示例6: 子图布局")
    print("=" * 60)
    
    skill = MatplotlibSkill(figsize=(12, 8))
    
    # 创建2x2子图
    skill.create_subplots(2, 2)
    
    # 子图1: 折线图
    x = np.linspace(0, 10, 50)
    skill.set_subplot(0, 0)
    skill.line_plot(x, np.sin(x), color='blue')
    skill.set_title('Sine Wave')
    
    # 子图2: 柱状图
    skill.set_subplot(0, 1)
    skill.bar_chart(['A', 'B', 'C', 'D'], [3, 7, 5, 9], color='green')
    skill.set_title('Bar Chart')
    
    # 子图3: 散点图
    skill.set_subplot(1, 0)
    np.random.seed(42)
    skill.scatter_plot(np.random.rand(50), np.random.rand(50), color='red')
    skill.set_title('Scatter Plot')
    
    # 子图4: 直方图
    skill.set_subplot(1, 1)
    skill.histogram(np.random.randn(1000), bins=20, color='purple')
    skill.set_title('Histogram')
    
    skill.tight_layout()
    skill.save_figure('example_subplots.png')
    print("子图已保存到 example_subplots.png")
    skill.close()


def example_heatmap():
    """示例：热力图"""
    print("\n" + "=" * 60)
    print("示例7: 热力图")
    print("=" * 60)
    
    skill = MatplotlibSkill()
    
    # 生成相关性矩阵
    np.random.seed(42)
    data = np.random.randn(100, 5)
    corr_matrix = np.corrcoef(data.T)
    labels = ['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4', 'Feature 5']
    
    skill.heatmap(
        corr_matrix,
        xticklabels=labels,
        yticklabels=labels,
        cmap='coolwarm',
        annot=True,
        fmt='.2f',
        title='Correlation Matrix',
        vmin=-1,
        vmax=1
    )
    
    skill.save_figure('example_heatmap.png')
    print("热力图已保存到 example_heatmap.png")
    skill.close()


def example_boxplot():
    """示例：箱线图"""
    print("\n" + "=" * 60)
    print("示例8: 箱线图")
    print("=" * 60)
    
    skill = MatplotlibSkill()
    
    # 生成数据
    np.random.seed(42)
    data = [
        np.random.normal(100, 10, 200),
        np.random.normal(120, 15, 200),
        np.random.normal(90, 12, 200),
        np.random.normal(110, 8, 200)
    ]
    
    skill.boxplot(
        data,
        labels=['Group A', 'Group B', 'Group C', 'Group D'],
        title='Box Plot Comparison',
        ylabel='Value',
        showfliers=True,
        patch_artist=True,
        colors=['lightblue', 'lightgreen', 'lightcoral', 'lightyellow']
    )
    
    skill.save_figure('example_boxplot.png')
    print("箱线图已保存到 example_boxplot.png")
    skill.close()


def example_advanced_styling():
    """示例：高级样式"""
    print("\n" + "=" * 60)
    print("示例9: 高级样式定制")
    print("=" * 60)
    
    skill = MatplotlibSkill(figsize=(10, 6))
    
    # 设置样式
    skill.set_style('seaborn-v0_8-darkgrid')
    skill.set_color_palette('Set2')
    
    # 生成数据
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    y3 = np.sin(x) * np.cos(x)
    
    # 绘制多条线
    skill.line_plot(x, y1, label='sin(x)', linewidth=2.5)
    skill.add_line(x, y2, label='cos(x)', linewidth=2.5, linestyle='--')
    skill.add_line(x, y3, label='sin(x)*cos(x)', linewidth=2.5, linestyle='-.')
    
    # 添加标注
    skill.add_annotation(1.57, 1, 'Peak', xytext=(3, 1.3),
                        arrowprops=dict(arrowstyle='->', color='red'))
    skill.add_annotation(4.71, -1, 'Trough', xytext=(6, -1.3),
                        arrowprops=dict(arrowstyle='->', color='blue'))
    
    # 设置标题和标签
    skill.set_title('Advanced Styled Plot', fontsize=16, fontweight='bold')
    skill.set_xlabel('X Axis', fontsize=12)
    skill.set_ylabel('Y Axis', fontsize=12)
    skill.add_legend(loc='upper right', fontsize=10)
    
    # 添加网格和范围
    skill.add_grid(True, linestyle=':', alpha=0.7)
    skill.set_xlim(0, 10)
    skill.set_ylim(-1.5, 1.5)
    
    skill.save_figure('example_advanced_style.png', dpi=150)
    print("高级样式图已保存到 example_advanced_style.png")
    skill.close()


def main():
    """主函数：运行所有示例"""
    try:
        example_line_plots()
        example_bar_charts()
        example_scatter_plots()
        example_pie_charts()
        example_histograms()
        example_subplots()
        example_heatmap()
        example_boxplot()
        example_advanced_styling()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"运行示例时出错: {e}")
        raise


if __name__ == "__main__":
    main()
