#!/usr/bin/env python3
"""
Matplotlib Skill - Test Suite
Matplotlib技能测试套件
"""

import unittest
import numpy as np
import os
import tempfile
import shutil
from pathlib import Path

from main import MatplotlibSkill, quick_line_plot, quick_bar_chart, quick_scatter


class TestMatplotlibSkill(unittest.TestCase):
    """MatplotlibSkill测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.test_dir = tempfile.mkdtemp()
        cls.skill = MatplotlibSkill()
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    def setUp(self):
        """每个测试前执行"""
        self.skill.close()
        self.skill = MatplotlibSkill()
    
    def tearDown(self):
        """每个测试后执行"""
        self.skill.close()
    
    # ==================== 基础功能测试 ====================
    
    def test_initialization(self):
        """测试初始化"""
        skill = MatplotlibSkill(figsize=(8, 6), dpi=150)
        self.assertEqual(skill.figsize, (8, 6))
        self.assertEqual(skill.dpi, 150)
        skill.close()
    
    def test_create_figure(self):
        """测试创建图表"""
        self.skill._create_figure()
        self.assertIsNotNone(self.skill.fig)
        self.assertIsNotNone(self.skill.ax)
    
    def test_set_title(self):
        """测试设置标题"""
        self.skill.set_title('Test Title')
        self.assertEqual(self.skill.ax.get_title(), 'Test Title')
    
    def test_set_labels(self):
        """测试设置轴标签"""
        self.skill.set_xlabel('X Label')
        self.skill.set_ylabel('Y Label')
        self.assertEqual(self.skill.ax.get_xlabel(), 'X Label')
        self.assertEqual(self.skill.ax.get_ylabel(), 'Y Label')
    
    def test_set_limits(self):
        """测试设置轴范围"""
        self.skill.set_xlim(0, 10)
        self.skill.set_ylim(-5, 5)
        self.assertEqual(self.skill.ax.get_xlim(), (0, 10))
    
    def test_add_grid(self):
        """测试添加网格"""
        self.skill.add_grid(True)
        self.assertTrue(self.skill.ax.xaxis._gridOnMajor)
    
    # ==================== 图表类型测试 ====================
    
    def test_line_plot(self):
        """测试折线图"""
        x = np.linspace(0, 10, 50)
        y = np.sin(x)
        lines = self.skill.line_plot(x, y, label='sin')
        self.assertIsNotNone(lines)
    
    def test_add_line(self):
        """测试添加线"""
        x = np.linspace(0, 10, 50)
        self.skill.line_plot(x, np.sin(x))
        lines = self.skill.add_line(x, np.cos(x))
        self.assertIsNotNone(lines)
    
    def test_bar_chart(self):
        """测试柱状图"""
        categories = ['A', 'B', 'C']
        values = [1, 2, 3]
        bars = self.skill.bar_chart(categories, values)
        self.assertIsNotNone(bars)
    
    def test_horizontal_bar_chart(self):
        """测试水平柱状图"""
        categories = ['A', 'B', 'C']
        values = [1, 2, 3]
        bars = self.skill.horizontal_bar_chart(categories, values)
        self.assertIsNotNone(bars)
    
    def test_grouped_bar_chart(self):
        """测试分组柱状图"""
        categories = ['A', 'B', 'C']
        values_list = [[1, 2, 3], [4, 5, 6]]
        labels = ['Group 1', 'Group 2']
        self.skill.grouped_bar_chart(categories, values_list, labels=labels)
        self.assertIsNotNone(self.skill.ax)
    
    def test_scatter_plot(self):
        """测试散点图"""
        x = np.random.rand(50)
        y = np.random.rand(50)
        scatter = self.skill.scatter_plot(x, y)
        self.assertIsNotNone(scatter)
    
    def test_scatter_with_colors(self):
        """测试带颜色的散点图"""
        x = np.random.rand(50)
        y = np.random.rand(50)
        colors = np.random.rand(50)
        scatter = self.skill.scatter_plot(x, y, colors=colors, colorbar=True)
        self.assertIsNotNone(scatter)
    
    def test_pie_chart(self):
        """测试饼图"""
        sizes = [30, 40, 30]
        labels = ['A', 'B', 'C']
        wedges, texts, autotexts = self.skill.pie_chart(sizes, labels=labels)
        self.assertIsNotNone(wedges)
        self.assertEqual(len(wedges), 3)
    
    def test_histogram_single(self):
        """测试单组直方图"""
        data = np.random.randn(100)
        self.skill.histogram(data, bins=10)
        self.assertIsNotNone(self.skill.ax)
    
    def test_histogram_multiple(self):
        """测试多组直方图"""
        data = [np.random.randn(100), np.random.randn(100)]
        labels = ['A', 'B']
        self.skill.histogram(data, labels=labels)
        self.assertIsNotNone(self.skill.ax)
    
    def test_area_chart(self):
        """测试面积图"""
        x = np.linspace(0, 10, 50)
        y = np.sin(x)
        self.skill.area_chart(x, y)
        self.assertIsNotNone(self.skill.ax)
    
    def test_stacked_area_chart(self):
        """测试堆叠面积图"""
        x = np.linspace(0, 10, 50)
        y1 = np.sin(x)
        y2 = np.cos(x)
        self.skill.stacked_area_chart(x, [y1, y2])
        self.assertIsNotNone(self.skill.ax)
    
    # ==================== 统计图表测试 ====================
    
    def test_boxplot(self):
        """测试箱线图"""
        data = [np.random.randn(100), np.random.randn(100)]
        bp = self.skill.boxplot(data, labels=['A', 'B'])
        self.assertIsNotNone(bp)
    
    def test_boxplot_with_colors(self):
        """测试带颜色的箱线图"""
        data = [np.random.randn(100), np.random.randn(100)]
        colors = ['lightblue', 'lightgreen']
        bp = self.skill.boxplot(data, patch_artist=True, colors=colors)
        self.assertIsNotNone(bp)
    
    def test_violin_plot(self):
        """测试小提琴图"""
        data = [np.random.randn(100), np.random.randn(100)]
        vp = self.skill.violin_plot(data, labels=['A', 'B'])
        self.assertIsNotNone(vp)
    
    def test_errorbar_plot(self):
        """测试误差条图"""
        x = np.arange(10)
        y = np.random.rand(10)
        yerr = np.random.rand(10) * 0.1
        eb = self.skill.errorbar_plot(x, y, yerr=yerr)
        self.assertIsNotNone(eb)
    
    def test_heatmap(self):
        """测试热力图"""
        data = np.random.rand(5, 5)
        im = self.skill.heatmap(data)
        self.assertIsNotNone(im)
    
    def test_heatmap_with_labels(self):
        """测试带标签的热力图"""
        data = np.random.rand(3, 3)
        labels = ['A', 'B', 'C']
        im = self.skill.heatmap(data, xticklabels=labels, yticklabels=labels, annot=True)
        self.assertIsNotNone(im)
    
    # ==================== 子图测试 ====================
    
    def test_create_subplots(self):
        """测试创建子图"""
        self.skill.create_subplots(2, 2)
        self.assertIsNotNone(self.skill.axes)
        self.assertEqual(self.skill.axes.shape, (2, 2))
    
    def test_set_subplot(self):
        """测试设置子图"""
        self.skill.create_subplots(2, 2)
        self.skill.set_subplot(0, 1)
        self.assertEqual(self.skill.current_subplot_idx, (0, 1))
    
    def test_subplot_plotting(self):
        """测试子图绘图"""
        self.skill.create_subplots(1, 2)
        
        self.skill.set_subplot(0, 0)
        self.skill.line_plot([1, 2, 3], [1, 4, 9])
        
        self.skill.set_subplot(0, 1)
        self.skill.bar_chart(['A', 'B'], [1, 2])
        
        self.assertIsNotNone(self.skill.fig)
    
    def test_tight_layout(self):
        """测试紧凑布局"""
        self.skill.create_subplots(2, 2)
        self.skill.tight_layout()
        self.assertIsNotNone(self.skill.fig)
    
    # ==================== 保存测试 ====================
    
    def test_save_figure_png(self):
        """测试保存PNG"""
        x = np.linspace(0, 10, 50)
        y = np.sin(x)
        self.skill.line_plot(x, y)
        
        filepath = os.path.join(self.test_dir, 'test.png')
        self.skill.save_figure(filepath)
        self.assertTrue(os.path.exists(filepath))
    
    def test_save_figure_pdf(self):
        """测试保存PDF"""
        x = np.linspace(0, 10, 50)
        y = np.sin(x)
        self.skill.line_plot(x, y)
        
        filepath = os.path.join(self.test_dir, 'test.pdf')
        self.skill.save_figure(filepath, format='pdf')
        self.assertTrue(os.path.exists(filepath))
    
    def test_save_figure_svg(self):
        """测试保存SVG"""
        x = np.linspace(0, 10, 50)
        y = np.sin(x)
        self.skill.line_plot(x, y)
        
        filepath = os.path.join(self.test_dir, 'test.svg')
        self.skill.save_figure(filepath, format='svg')
        self.assertTrue(os.path.exists(filepath))
    
    def test_save_figure_dpi(self):
        """测试保存指定DPI"""
        x = np.linspace(0, 10, 50)
        y = np.sin(x)
        self.skill.line_plot(x, y)
        
        filepath = os.path.join(self.test_dir, 'test_dpi.png')
        self.skill.save_figure(filepath, dpi=200)
        self.assertTrue(os.path.exists(filepath))
    
    def test_save_without_figure(self):
        """测试无图表时保存"""
        skill = MatplotlibSkill()
        skill.fig = None  # 确保没有图表
        with self.assertRaises(ValueError):
            skill.save_figure('test.png')
    
    # ==================== 样式测试 ====================
    
    def test_set_style(self):
        """测试设置样式"""
        self.skill.set_style('default')
        self.assertIsNotNone(self.skill)
    
    def test_add_annotation(self):
        """测试添加标注"""
        self.skill.line_plot([1, 2, 3], [1, 4, 9])
        self.skill.add_annotation(2, 4, 'Point', xytext=(2.5, 6))
        self.assertIsNotNone(self.skill.ax)
    
    def test_add_text(self):
        """测试添加文本"""
        self.skill.line_plot([1, 2, 3], [1, 4, 9])
        self.skill.add_text(2, 5, 'Test Text')
        self.assertIsNotNone(self.skill.ax)
    
    def test_set_log_scale(self):
        """测试对数坐标"""
        self.skill.line_plot([1, 10, 100], [1, 10, 100])
        self.skill.set_log_scale('y')
        self.assertEqual(self.skill.ax.get_yscale(), 'log')
    
    def test_rotate_xticks(self):
        """测试旋转X轴标签"""
        self.skill.bar_chart(['A', 'B', 'C'], [1, 2, 3])
        self.skill.rotate_xticks(45)
        self.assertIsNotNone(self.skill.ax)
    
    # ==================== 高级功能测试 ====================
    
    def test_create_twin_axis(self):
        """测试双Y轴"""
        x = np.linspace(0, 10, 50)
        y1 = np.sin(x)
        y2 = np.cos(x) * 100
        
        self.skill.line_plot(x, y1, label='sin', color='blue')
        ax2 = self.skill.create_twin_axis('Right Y')
        ax2.plot(x, y2, color='red', label='cos*100')
        
        self.assertIsNotNone(ax2)
    
    def test_clear(self):
        """测试清空图表"""
        self.skill.line_plot([1, 2, 3], [1, 4, 9])
        self.skill.clear()
        self.assertEqual(len(self.skill.ax.lines), 0)
    
    def test_close(self):
        """测试关闭图表"""
        self.skill.line_plot([1, 2, 3], [1, 4, 9])
        self.skill.close()
        self.assertIsNone(self.skill.fig)
        self.assertIsNone(self.skill.ax)


class TestConvenienceFunctions(unittest.TestCase):
    """便捷函数测试"""
    
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp()
    
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    def test_quick_line_plot(self):
        """测试快速折线图"""
        x = np.linspace(0, 10, 50)
        y = np.sin(x)
        filepath = os.path.join(self.test_dir, 'quick_line.png')
        quick_line_plot(x, y, title='Quick Line', save_path=filepath)
        self.assertTrue(os.path.exists(filepath))
    
    def test_quick_bar_chart(self):
        """测试快速柱状图"""
        filepath = os.path.join(self.test_dir, 'quick_bar.png')
        quick_bar_chart(['A', 'B', 'C'], [1, 2, 3], title='Quick Bar', save_path=filepath)
        self.assertTrue(os.path.exists(filepath))
    
    def test_quick_scatter(self):
        """测试快速散点图"""
        x = np.random.rand(50)
        y = np.random.rand(50)
        filepath = os.path.join(self.test_dir, 'quick_scatter.png')
        quick_scatter(x, y, title='Quick Scatter', save_path=filepath)
        self.assertTrue(os.path.exists(filepath))


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""
    
    def setUp(self):
        self.skill = MatplotlibSkill()
    
    def tearDown(self):
        self.skill.close()
    
    def test_empty_data(self):
        """测试空数据"""
        self.skill.line_plot([], [])
        self.assertIsNotNone(self.skill.ax)
    
    def test_single_point(self):
        """测试单点"""
        self.skill.scatter_plot([1], [1])
        self.assertIsNotNone(self.skill.ax)
    
    def test_large_dataset(self):
        """测试大数据集"""
        x = np.linspace(0, 1000, 10000)
        y = np.sin(x)
        self.skill.line_plot(x, y)
        self.assertIsNotNone(self.skill.ax)
    
    def test_negative_values(self):
        """测试负值"""
        self.skill.bar_chart(['A', 'B', 'C'], [-1, 0, 1])
        self.assertIsNotNone(self.skill.ax)
    
    def test_nan_values(self):
        """测试NaN值"""
        x = np.array([1, 2, np.nan, 4, 5])
        y = np.array([1, 4, 9, np.nan, 25])
        self.skill.line_plot(x, y)
        self.assertIsNotNone(self.skill.ax)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestMatplotlibSkill))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
