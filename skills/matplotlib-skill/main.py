#!/usr/bin/env python3
"""
Matplotlib Skill - Main Implementation
Matplotlib数据可视化技能主实现文件

功能：Matplotlib数据可视化。支持图表生成、样式定制、导出保存。
Use when analyzing data, creating visualizations, or when user mentions 'matplotlib', 'plot', 'chart', 'visualization', 'graph'.

Author: Kimi Skills
Version: 1.0.0
"""

import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.patches import Rectangle, Circle, Polygon
import numpy as np
from typing import Union, List, Tuple, Optional, Dict, Any
from pathlib import Path
import json
import warnings

warnings.filterwarnings('ignore')


class MatplotlibSkill:
    """
    Matplotlib数据可视化技能类
    
    提供完整的数据可视化功能，包括：
    - 基本图表：折线图、柱状图、散点图、饼图、直方图
    - 统计图表：箱线图、小提琴图、热力图
    - 高级图表：3D图、子图、双Y轴
    - 样式定制：颜色、主题、标注
    - 导出保存：PNG、PDF、SVG、JPG
    """
    
    def __init__(self, figsize: Optional[Tuple[int, int]] = None, 
                 dpi: Optional[int] = None, config_path: Optional[str] = None):
        """
        初始化MatplotlibSkill
        
        Args:
            figsize: 图表尺寸 (宽, 高)
            dpi: 分辨率
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.figsize = figsize or tuple(self.config.get('default_figsize', [10, 6]))
        self.dpi = dpi or self.config.get('default_dpi', 100)
        
        self.fig = None
        self.ax = None
        self.axes = None  # 用于子图
        self.current_subplot_idx = None
        
        self._setup_matplotlib()
    
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
            "default_figsize": [10, 6],
            "default_dpi": 100,
            "default_style": "default"
        }
    
    def _setup_matplotlib(self):
        """设置matplotlib参数"""
        plt.rcParams['font.family'] = self.config.get('font_family', 'sans-serif')
        plt.rcParams['font.size'] = self.config.get('font_size', 12)
        plt.rcParams['axes.titlesize'] = self.config.get('axes_titlesize', 14)
        plt.rcParams['axes.labelsize'] = self.config.get('axes_labelsize', 12)
    
    def _create_figure(self):
        """创建图表"""
        if self.fig is None:
            self.fig, self.ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
    
    # ==================== 样式设置 ====================
    
    def set_style(self, style: str):
        """
        设置图表样式
        
        Args:
            style: 样式名称 ('default', 'seaborn', 'ggplot', 'bmh', etc.)
        """
        try:
            plt.style.use(style)
        except:
            plt.style.use('default')
    
    def set_color_palette(self, palette: str):
        """
        设置颜色方案
        
        Args:
            palette: 颜色方案名称 ('viridis', 'plasma', 'coolwarm', etc.)
        """
        try:
            plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.get_cmap(palette).colors)
        except:
            pass
    
    def set_title(self, title: str, fontsize: Optional[int] = None, **kwargs):
        """设置标题"""
        self._create_figure()
        if fontsize:
            self.ax.set_title(title, fontsize=fontsize, **kwargs)
        else:
            self.ax.set_title(title, **kwargs)
    
    def set_xlabel(self, label: str, fontsize: Optional[int] = None, **kwargs):
        """设置X轴标签"""
        self._create_figure()
        if fontsize:
            self.ax.set_xlabel(label, fontsize=fontsize, **kwargs)
        else:
            self.ax.set_xlabel(label, **kwargs)
    
    def set_ylabel(self, label: str, fontsize: Optional[int] = None, **kwargs):
        """设置Y轴标签"""
        self._create_figure()
        if fontsize:
            self.ax.set_ylabel(label, fontsize=fontsize, **kwargs)
        else:
            self.ax.set_ylabel(label, **kwargs)
    
    def set_xlim(self, xmin: float, xmax: float):
        """设置X轴范围"""
        self._create_figure()
        self.ax.set_xlim(xmin, xmax)
    
    def set_ylim(self, ymin: float, ymax: float):
        """设置Y轴范围"""
        self._create_figure()
        self.ax.set_ylim(ymin, ymax)
    
    def add_legend(self, loc: str = 'best', **kwargs):
        """添加图例"""
        self._create_figure()
        self.ax.legend(loc=loc, **kwargs)
    
    def add_grid(self, visible: bool = True, **kwargs):
        """添加网格"""
        self._create_figure()
        self.ax.grid(visible, **kwargs)
    
    def add_annotation(self, x: float, y: float, text: str, 
                       xytext: Optional[Tuple[float, float]] = None,
                       arrowprops: Optional[Dict] = None, **kwargs):
        """
        添加标注
        
        Args:
            x: 标注点X坐标
            y: 标注点Y坐标
            text: 标注文本
            xytext: 文本位置
            arrowprops: 箭头属性
        """
        self._create_figure()
        self.ax.annotate(text, xy=(x, y), xytext=xytext, 
                        arrowprops=arrowprops, **kwargs)
    
    def add_colorbar(self, mappable=None, label: Optional[str] = None, **kwargs):
        """添加颜色条"""
        self._create_figure()
        cbar = plt.colorbar(mappable, ax=self.ax, **kwargs)
        if label:
            cbar.set_label(label)
        return cbar
    
    def add_text(self, x: float, y: float, text: str, **kwargs):
        """添加文本"""
        self._create_figure()
        self.ax.text(x, y, text, **kwargs)
    
    # ==================== 基本图表 ====================
    
    def line_plot(self, x: Union[List, np.ndarray], y: Union[List, np.ndarray],
                  label: Optional[str] = None, **kwargs):
        """
        绘制折线图
        
        Args:
            x: X轴数据
            y: Y轴数据
            label: 图例标签
            **kwargs: 其他matplotlib参数
        """
        self._create_figure()
        line = self.ax.plot(x, y, label=label, **kwargs)
        return line
    
    def add_line(self, x: Union[List, np.ndarray], y: Union[List, np.ndarray],
                 label: Optional[str] = None, **kwargs):
        """在同一图表上添加另一条线"""
        return self.line_plot(x, y, label=label, **kwargs)
    
    def bar_chart(self, categories: Union[List, np.ndarray], 
                  values: Union[List, np.ndarray],
                  **kwargs):
        """
        绘制柱状图
        
        Args:
            categories: 类别标签
            values: 数值
            **kwargs: 其他matplotlib参数
        """
        self._create_figure()
        bars = self.ax.bar(categories, values, **kwargs)
        return bars
    
    def horizontal_bar_chart(self, categories: Union[List, np.ndarray],
                            values: Union[List, np.ndarray],
                            **kwargs):
        """绘制水平柱状图"""
        self._create_figure()
        bars = self.ax.barh(categories, values, **kwargs)
        return bars
    
    def grouped_bar_chart(self, categories: Union[List, np.ndarray],
                          values_list: List[Union[List, np.ndarray]],
                          labels: Optional[List[str]] = None,
                          width: float = 0.8,
                          title: Optional[str] = None,
                          xlabel: Optional[str] = None,
                          ylabel: Optional[str] = None,
                          **kwargs):
        """
        绘制分组柱状图
        
        Args:
            categories: 类别标签
            values_list: 多组数值
            labels: 组标签
            width: 柱宽
        """
        self._create_figure()
        x = np.arange(len(categories))
        n_groups = len(values_list)
        width = width / n_groups
        
        for i, values in enumerate(values_list):
            offset = (i - n_groups/2 + 0.5) * width
            label = labels[i] if labels else None
            self.ax.bar(x + offset, values, width, label=label, **kwargs)
        
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(categories)
        if title:
            self.set_title(title)
        if xlabel:
            self.set_xlabel(xlabel)
        if ylabel:
            self.set_ylabel(ylabel)
        if labels:
            self.add_legend()
    
    def scatter_plot(self, x: Union[List, np.ndarray], y: Union[List, np.ndarray],
                     colors: Optional[Union[List, np.ndarray]] = None,
                     sizes: Optional[Union[List, np.ndarray]] = None,
                     cmap: str = 'viridis',
                     colorbar: bool = False,
                     title: Optional[str] = None,
                     xlabel: Optional[str] = None,
                     ylabel: Optional[str] = None,
                     **kwargs):
        """
        绘制散点图
        
        Args:
            x: X轴数据
            y: Y轴数据
            colors: 颜色数据
            sizes: 点大小
            cmap: 颜色映射
            colorbar: 是否显示颜色条
        """
        self._create_figure()
        scatter = self.ax.scatter(x, y, c=colors, s=sizes, cmap=cmap, **kwargs)
        
        if title:
            self.set_title(title)
        if xlabel:
            self.set_xlabel(xlabel)
        if ylabel:
            self.set_ylabel(ylabel)
        if colorbar and colors is not None:
            self.add_colorbar(scatter)
        
        return scatter
    
    def pie_chart(self, sizes: Union[List, np.ndarray],
                  labels: Optional[Union[List, np.ndarray]] = None,
                  colors: Optional[Union[List, np.ndarray]] = None,
                  explode: Optional[Union[List, np.ndarray]] = None,
                  autopct: Optional[str] = None,
                  title: Optional[str] = None,
                  **kwargs):
        """
        绘制饼图
        
        Args:
            sizes: 各部分大小
            labels: 标签
            colors: 颜色
            explode: 突出显示
            autopct: 百分比格式
        """
        self._create_figure()
        wedges, texts, autotexts = self.ax.pie(
            sizes, labels=labels, colors=colors, explode=explode,
            autopct=autopct, **kwargs
        )
        
        if title:
            self.set_title(title)
        
        return wedges, texts, autotexts
    
    def histogram(self, data: Union[Union[List, np.ndarray], List[Union[List, np.ndarray]]],
                  bins: int = 10,
                  labels: Optional[List[str]] = None,
                  colors: Optional[List[str]] = None,
                  alpha: float = 0.7,
                  title: Optional[str] = None,
                  xlabel: Optional[str] = None,
                  ylabel: Optional[str] = None,
                  kde: bool = False,
                  **kwargs):
        """
        绘制直方图
        
        Args:
            data: 数据或数据列表
            bins: 箱数
            labels: 标签
            colors: 颜色
            kde: 是否显示核密度估计
        """
        self._create_figure()
        
        if not isinstance(data, list) or not isinstance(data[0], (list, np.ndarray)):
            data = [data]
        
        for i, d in enumerate(data):
            label = labels[i] if labels else None
            color = colors[i] if colors else None
            self.ax.hist(d, bins=bins, label=label, color=color, 
                        alpha=alpha, **kwargs)
        
        if title:
            self.set_title(title)
        if xlabel:
            self.set_xlabel(xlabel)
        if ylabel:
            self.set_ylabel(ylabel)
        if labels:
            self.add_legend()
    
    def area_chart(self, x: Union[List, np.ndarray], 
                   y: Union[List, np.ndarray],
                   **kwargs):
        """绘制面积图"""
        self._create_figure()
        self.ax.fill_between(x, y, **kwargs)
    
    def stacked_area_chart(self, x: Union[List, np.ndarray],
                           y_list: List[Union[List, np.ndarray]],
                           labels: Optional[List[str]] = None,
                           **kwargs):
        """绘制堆叠面积图"""
        self._create_figure()
        self.ax.stackplot(x, *y_list, labels=labels, **kwargs)
        if labels:
            self.add_legend()
    
    # ==================== 统计图表 ====================
    
    def boxplot(self, data: Union[Union[List, np.ndarray], List[Union[List, np.ndarray]]],
                labels: Optional[List[str]] = None,
                title: Optional[str] = None,
                xlabel: Optional[str] = None,
                ylabel: Optional[str] = None,
                showfliers: bool = True,
                patch_artist: bool = False,
                colors: Optional[List[str]] = None,
                **kwargs):
        """
        绘制箱线图
        
        Args:
            data: 数据或数据列表
            labels: 标签
            showfliers: 是否显示异常值
            patch_artist: 是否填充颜色
            colors: 颜色列表
        """
        self._create_figure()
        
        bp = self.ax.boxplot(data, labels=labels, showfliers=showfliers,
                            patch_artist=patch_artist, **kwargs)
        
        if colors and patch_artist:
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
        
        if title:
            self.set_title(title)
        if xlabel:
            self.set_xlabel(xlabel)
        if ylabel:
            self.set_ylabel(ylabel)
        
        return bp
    
    def violin_plot(self, data: Union[Union[List, np.ndarray], List[Union[List, np.ndarray]]],
                    labels: Optional[List[str]] = None,
                    title: Optional[str] = None,
                    **kwargs):
        """
        绘制小提琴图
        
        Args:
            data: 数据或数据列表
            labels: 标签
        """
        self._create_figure()
        
        vp = self.ax.violinplot(data, **kwargs)
        
        if labels:
            self.ax.set_xticks(np.arange(1, len(labels) + 1))
            self.ax.set_xticklabels(labels)
        
        if title:
            self.set_title(title)
        
        return vp
    
    def errorbar_plot(self, x: Union[List, np.ndarray], y: Union[List, np.ndarray],
                      yerr: Optional[Union[List, np.ndarray]] = None,
                      xerr: Optional[Union[List, np.ndarray]] = None,
                      **kwargs):
        """绘制带误差条的图"""
        self._create_figure()
        return self.ax.errorbar(x, y, yerr=yerr, xerr=xerr, **kwargs)
    
    def heatmap(self, data: Union[List, np.ndarray],
                xticklabels: Optional[Union[List, np.ndarray]] = None,
                yticklabels: Optional[Union[List, np.ndarray]] = None,
                cmap: str = 'viridis',
                annot: bool = False,
                fmt: str = '.2f',
                title: Optional[str] = None,
                vmin: Optional[float] = None,
                vmax: Optional[float] = None,
                colorbar: bool = True,
                **kwargs):
        """
        绘制热力图
        
        Args:
            data: 数据矩阵
            xticklabels: X轴标签
            yticklabels: Y轴标签
            cmap: 颜色映射
            annot: 是否显示数值
            fmt: 数值格式
            vmin: 最小值
            vmax: 最大值
        """
        self._create_figure()
        
        im = self.ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax, **kwargs)
        
        if xticklabels is not None:
            self.ax.set_xticks(np.arange(len(xticklabels)))
            self.ax.set_xticklabels(xticklabels)
        if yticklabels is not None:
            self.ax.set_yticks(np.arange(len(yticklabels)))
            self.ax.set_yticklabels(yticklabels)
        
        if annot:
            for i in range(len(data)):
                for j in range(len(data[0])):
                    text = self.ax.text(j, i, format(data[i, j], fmt),
                                       ha="center", va="center", color="w")
        
        if colorbar:
            self.add_colorbar(im)
        
        if title:
            self.set_title(title)
        
        return im
    
    # ==================== 子图管理 ====================
    
    def create_subplots(self, nrows: int = 1, ncols: int = 1, 
                        figsize: Optional[Tuple[int, int]] = None,
                        **kwargs):
        """
        创建子图
        
        Args:
            nrows: 行数
            ncols: 列数
            figsize: 图表尺寸
        """
        if figsize is None:
            figsize = self.figsize
        
        self.fig, self.axes = plt.subplots(nrows, ncols, figsize=figsize, dpi=self.dpi, **kwargs)
        
        if nrows == 1 and ncols == 1:
            self.axes = np.array([[self.axes]])
        elif nrows == 1 or ncols == 1:
            self.axes = self.axes.reshape(nrows, ncols)
        
        self.current_subplot_idx = (0, 0)
        self.ax = self.axes[0, 0]
    
    def set_subplot(self, row: int, col: int):
        """设置当前子图"""
        if self.axes is not None:
            self.current_subplot_idx = (row, col)
            self.ax = self.axes[row, col]
    
    def tight_layout(self, **kwargs):
        """自动调整子图布局"""
        if self.fig:
            self.fig.tight_layout(**kwargs)
    
    # ==================== 导出保存 ====================
    
    def save_figure(self, filepath: str, format: Optional[str] = None,
                    dpi: Optional[int] = None, **kwargs):
        """
        保存图表
        
        Args:
            filepath: 文件路径
            format: 格式 (png, pdf, svg, jpg)
            dpi: 分辨率
        """
        if self.fig is None:
            raise ValueError("没有可保存的图表")
        
        dpi = dpi or self.config.get('savefig_dpi', 300)
        bbox = self.config.get('savefig_bbox', 'tight')
        
        self.fig.savefig(filepath, format=format, dpi=dpi, 
                        bbox_inches=bbox, **kwargs)
    
    def show(self):
        """显示图表（在非交互式模式下不执行）"""
        if self.config.get('interactive', False):
            plt.show()
    
    def close(self):
        """关闭图表"""
        if self.fig:
            plt.close(self.fig)
            self.fig = None
            self.ax = None
            self.axes = None
    
    def clear(self):
        """清空当前图表"""
        if self.ax:
            self.ax.clear()
    
    def get_figure(self):
        """获取当前Figure对象"""
        return self.fig
    
    def get_axes(self):
        """获取当前Axes对象"""
        return self.ax
    
    # ==================== 高级功能 ====================
    
    def create_twin_axis(self, ylabel: Optional[str] = None, side: str = 'right'):
        """
        创建双Y轴
        
        Args:
            ylabel: Y轴标签
            side: 位置 ('left' 或 'right')
            
        Returns:
            Axes: 新的Y轴对象
        """
        self._create_figure()
        ax2 = self.ax.twinx() if side == 'right' else self.ax.twiny()
        if ylabel:
            ax2.set_ylabel(ylabel)
        return ax2
    
    def set_log_scale(self, axis: str = 'y'):
        """设置对数坐标"""
        self._create_figure()
        if axis == 'x':
            self.ax.set_xscale('log')
        elif axis == 'y':
            self.ax.set_yscale('log')
        elif axis == 'both':
            self.ax.set_xscale('log')
            self.ax.set_yscale('log')
    
    def rotate_xticks(self, angle: float = 45):
        """旋转X轴标签"""
        self._create_figure()
        plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=angle)
    
    def rotate_yticks(self, angle: float = 45):
        """旋转Y轴标签"""
        self._create_figure()
        plt.setp(self.ax.yaxis.get_majorticklabels(), rotation=angle)


# ==================== 便捷函数 ====================

def quick_line_plot(x, y, title: Optional[str] = None, save_path: Optional[str] = None):
    """快速绘制折线图"""
    skill = MatplotlibSkill()
    skill.line_plot(x, y)
    if title:
        skill.set_title(title)
    if save_path:
        skill.save_figure(save_path)
    skill.close()


def quick_bar_chart(categories, values, title: Optional[str] = None, 
                    save_path: Optional[str] = None):
    """快速绘制柱状图"""
    skill = MatplotlibSkill()
    skill.bar_chart(categories, values)
    if title:
        skill.set_title(title)
    if save_path:
        skill.save_figure(save_path)
    skill.close()


def quick_scatter(x, y, title: Optional[str] = None, save_path: Optional[str] = None):
    """快速绘制散点图"""
    skill = MatplotlibSkill()
    skill.scatter_plot(x, y)
    if title:
        skill.set_title(title)
    if save_path:
        skill.save_figure(save_path)
    skill.close()


if __name__ == "__main__":
    # 简单的自我测试
    print("Matplotlib Skill 测试")
    print("=" * 40)
    
    skill = MatplotlibSkill()
    
    # 测试折线图
    x = np.linspace(0, 10, 50)
    y = np.sin(x)
    skill.line_plot(x, y, label='sin(x)', color='blue')
    skill.set_title('Test Plot')
    skill.set_xlabel('X')
    skill.set_ylabel('Y')
    skill.add_legend()
    
    # 测试保存
    test_path = 'test_plot.png'
    skill.save_figure(test_path)
    print(f"测试图表已保存到 {test_path}")
    skill.close()
    
    print("\nMatplotlib Skill 测试完成!")
