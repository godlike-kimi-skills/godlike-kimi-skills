#!/usr/bin/env python3
"""
Jupyter Skill - Main Implementation
Jupyter Notebook管理技能主实现文件

功能：Jupyter Notebook管理。支持Notebook创建、执行、转换。
Use when analyzing data, creating visualizations, or when user mentions 'jupyter', 'notebook', 'ipynb', 'jupyter lab'.

Author: Kimi Skills
Version: 1.0.0
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
import warnings

warnings.filterwarnings('ignore')

# Jupyter相关导入
try:
    import nbformat
    from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell, new_raw_cell
    from nbformat.validator import validate
    NBFORMAT_AVAILABLE = True
except ImportError:
    NBFORMAT_AVAILABLE = False
    # 提供基本的Notebook结构
    def new_notebook(): return {"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 4}
    def new_code_cell(source): return {"cell_type": "code", "source": source, "metadata": {}, "outputs": [], "execution_count": None}
    def new_markdown_cell(source): return {"cell_type": "markdown", "source": source, "metadata": {}}
    def new_raw_cell(source): return {"cell_type": "raw", "source": source, "metadata": {}}

try:
    from nbconvert import HTMLExporter, PDFExporter, PythonExporter, MarkdownExporter
    from nbconvert.preprocessors import ExecutePreprocessor
    NBCONVERT_AVAILABLE = True
except ImportError:
    NBCONVERT_AVAILABLE = False


class JupyterSkill:
    """
    Jupyter Notebook管理技能类
    
    提供完整的Notebook管理功能，包括：
    - Notebook创建和加载
    - 单元格管理（添加、编辑、删除、移动）
    - Notebook执行
    - 格式转换（HTML、PDF、Python、Markdown）
    - Notebook分析
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化JupyterSkill
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.execution_timeout = self.config.get('execution_timeout', 300)
        self.default_kernel = self.config.get('default_kernel', 'python3')
    
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
            "default_kernel": "python3",
            "execution_timeout": 300,
            "allow_errors": False
        }
    
    def _ensure_nbformat(self):
        """确保nbformat可用"""
        if not NBFORMAT_AVAILABLE:
            raise ImportError("nbformat模块未安装，请运行: pip install nbformat")
    
    def _ensure_nbconvert(self):
        """确保nbconvert可用"""
        if not NBCONVERT_AVAILABLE:
            raise ImportError("nbconvert模块未安装，请运行: pip install nbconvert")
    
    # ==================== Notebook创建和加载 ====================
    
    def create_notebook(self, metadata: Optional[Dict] = None) -> Any:
        """
        创建新的Notebook
        
        Args:
            metadata: Notebook元数据
            
        Returns:
            新的Notebook对象
        """
        self._ensure_nbformat()
        
        notebook = new_notebook()
        
        if metadata:
            notebook.metadata.update(metadata)
        else:
            default_metadata = self.config.get('default_metadata', {})
            notebook.metadata.update(default_metadata)
        
        return notebook
    
    def load_notebook(self, filepath: str) -> Any:
        """
        加载Notebook文件
        
        Args:
            filepath: Notebook文件路径
            
        Returns:
            Notebook对象
        """
        self._ensure_nbformat()
        
        with open(filepath, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
        
        return notebook
    
    def save_notebook(self, notebook: Any, filepath: str) -> None:
        """
        保存Notebook文件
        
        Args:
            notebook: Notebook对象
            filepath: 目标文件路径
        """
        self._ensure_nbformat()
        
        # 确保目录存在
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            nbformat.write(notebook, f)
    
    def validate_notebook(self, filepath: str) -> Tuple[bool, Optional[str]]:
        """
        验证Notebook格式
        
        Args:
            filepath: Notebook文件路径
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        self._ensure_nbformat()
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                notebook = nbformat.read(f, as_version=4)
            
            # 验证Notebook格式
            validate(notebook)
            return True, None
        except Exception as e:
            return False, str(e)
    
    # ==================== 单元格管理 ====================
    
    def add_code_cell(self, notebook: Any, source: str, 
                      metadata: Optional[Dict] = None) -> Any:
        """
        添加代码单元格
        
        Args:
            notebook: Notebook对象
            source: 代码内容
            metadata: 单元格元数据
            
        Returns:
            创建的单元格
        """
        cell = new_code_cell(source)
        if metadata:
            cell.metadata.update(metadata)
        notebook.cells.append(cell)
        return cell
    
    def add_markdown_cell(self, notebook: Any, source: str,
                          metadata: Optional[Dict] = None) -> Any:
        """
        添加Markdown单元格
        
        Args:
            notebook: Notebook对象
            source: Markdown内容
            metadata: 单元格元数据
            
        Returns:
            创建的单元格
        """
        cell = new_markdown_cell(source)
        if metadata:
            cell.metadata.update(metadata)
        notebook.cells.append(cell)
        return cell
    
    def add_raw_cell(self, notebook: Any, source: str,
                     metadata: Optional[Dict] = None) -> Any:
        """
        添加Raw单元格
        
        Args:
            notebook: Notebook对象
            source: 原始内容
            metadata: 单元格元数据
            
        Returns:
            创建的单元格
        """
        cell = new_raw_cell(source)
        if metadata:
            cell.metadata.update(metadata)
        notebook.cells.append(cell)
        return cell
    
    def insert_cell(self, notebook: Any, index: int, cell_type: str,
                    source: str, metadata: Optional[Dict] = None) -> Any:
        """
        在指定位置插入单元格
        
        Args:
            notebook: Notebook对象
            index: 插入位置
            cell_type: 单元格类型 ('code', 'markdown', 'raw')
            source: 单元格内容
            metadata: 单元格元数据
            
        Returns:
            创建的单元格
        """
        if cell_type == 'code':
            cell = new_code_cell(source)
        elif cell_type == 'markdown':
            cell = new_markdown_cell(source)
        elif cell_type == 'raw':
            cell = new_raw_cell(source)
        else:
            raise ValueError(f"不支持的单元格类型: {cell_type}")
        
        if metadata:
            cell.metadata.update(metadata)
        
        notebook.cells.insert(index, cell)
        return cell
    
    def get_cell(self, notebook: Any, index: int) -> Any:
        """
        获取指定索引的单元格
        
        Args:
            notebook: Notebook对象
            index: 单元格索引
            
        Returns:
            单元格对象
        """
        if index < 0 or index >= len(notebook.cells):
            raise IndexError(f"单元格索引 {index} 超出范围")
        return notebook.cells[index]
    
    def update_cell(self, notebook: Any, index: int, source: str,
                    metadata: Optional[Dict] = None) -> Any:
        """
        更新单元格内容
        
        Args:
            notebook: Notebook对象
            index: 单元格索引
            source: 新的内容
            metadata: 新的元数据（可选）
            
        Returns:
            更新后的单元格
        """
        cell = self.get_cell(notebook, index)
        cell.source = source
        if metadata:
            cell.metadata.update(metadata)
        return cell
    
    def delete_cell(self, notebook: Any, index: int) -> Any:
        """
        删除指定索引的单元格
        
        Args:
            notebook: Notebook对象
            index: 单元格索引
            
        Returns:
            被删除的单元格
        """
        if index < 0 or index >= len(notebook.cells):
            raise IndexError(f"单元格索引 {index} 超出范围")
        return notebook.cells.pop(index)
    
    def move_cell(self, notebook: Any, from_index: int, to_index: int) -> None:
        """
        移动单元格
        
        Args:
            notebook: Notebook对象
            from_index: 原索引
            to_index: 目标索引
        """
        if from_index < 0 or from_index >= len(notebook.cells):
            raise IndexError(f"原索引 {from_index} 超出范围")
        if to_index < 0 or to_index > len(notebook.cells):
            raise IndexError(f"目标索引 {to_index} 超出范围")
        
        cell = notebook.cells.pop(from_index)
        notebook.cells.insert(to_index, cell)
    
    def clear_cell_output(self, notebook: Any, index: int) -> None:
        """
        清除单元格输出
        
        Args:
            notebook: Notebook对象
            index: 单元格索引
        """
        cell = self.get_cell(notebook, index)
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None
    
    def clear_all_outputs(self, notebook: Any) -> None:
        """
        清除所有单元格输出
        
        Args:
            notebook: Notebook对象
        """
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                cell.outputs = []
                cell.execution_count = None
    
    def count_cells(self, notebook: Any, cell_type: Optional[str] = None) -> int:
        """
        统计单元格数量
        
        Args:
            notebook: Notebook对象
            cell_type: 单元格类型过滤 ('code', 'markdown', 'raw')
            
        Returns:
            单元格数量
        """
        if cell_type:
            return sum(1 for cell in notebook.cells if cell.cell_type == cell_type)
        return len(notebook.cells)
    
    def list_cells(self, notebook: Any) -> List[Dict]:
        """
        列出所有单元格信息
        
        Args:
            notebook: Notebook对象
            
        Returns:
            单元格信息列表
        """
        return [
            {
                'index': i,
                'cell_type': cell.cell_type,
                'source': cell.source,
                'execution_count': getattr(cell, 'execution_count', None)
            }
            for i, cell in enumerate(notebook.cells)
        ]
    
    # ==================== Notebook执行 ====================
    
    def execute_notebook(self, input_path: str, output_path: Optional[str] = None,
                        kernel: Optional[str] = None, timeout: Optional[int] = None,
                        allow_errors: bool = False) -> Any:
        """
        执行Notebook
        
        Args:
            input_path: 输入Notebook路径
            output_path: 输出Notebook路径（可选）
            kernel: 内核名称
            timeout: 超时时间（秒）
            allow_errors: 是否允许错误继续执行
            
        Returns:
            执行后的Notebook对象
        """
        self._ensure_nbformat()
        self._ensure_nbconvert()
        
        # 加载Notebook
        with open(input_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
        
        # 设置执行参数
        kernel = kernel or self.default_kernel
        timeout = timeout or self.execution_timeout
        
        # 创建执行预处理器
        ep = ExecutePreprocessor(
            timeout=timeout,
            kernel_name=kernel,
            allow_errors=allow_errors
        )
        
        # 执行Notebook
        ep.preprocess(notebook, {'metadata': {'path': Path(input_path).parent}})
        
        # 保存结果
        if output_path:
            self.save_notebook(notebook, output_path)
        
        return notebook
    
    def execute_cell(self, notebook: Any, index: int, 
                     kernel: Optional[str] = None) -> Any:
        """
        执行单个单元格（需要完整Jupyter环境）
        
        Args:
            notebook: Notebook对象
            index: 单元格索引
            kernel: 内核名称
            
        Returns:
            执行后的单元格
        """
        self._ensure_nbformat()
        self._ensure_nbconvert()
        
        cell = self.get_cell(notebook, index)
        if cell.cell_type != 'code':
            raise ValueError("只有代码单元格可以执行")
        
        # 创建临时Notebook
        temp_notebook = new_notebook()
        temp_notebook.cells.append(cell)
        
        # 执行
        kernel = kernel or self.default_kernel
        ep = ExecutePreprocessor(timeout=self.execution_timeout, kernel_name=kernel)
        ep.preprocess(temp_notebook, {})
        
        # 更新原单元格
        executed_cell = temp_notebook.cells[0]
        notebook.cells[index] = executed_cell
        
        return executed_cell
    
    # ==================== 格式转换 ====================
    
    def convert_notebook(self, input_path: str, to_format: str,
                         output_path: Optional[str] = None, **kwargs) -> str:
        """
        转换Notebook格式
        
        Args:
            input_path: 输入Notebook路径
            to_format: 目标格式 ('html', 'pdf', 'python', 'markdown', 'rst', 'latex')
            output_path: 输出路径（可选）
            **kwargs: 转换器额外参数
            
        Returns:
            转换后的内容（如果output_path为None）或输出路径
        """
        self._ensure_nbformat()
        self._ensure_nbconvert()
        
        # 加载Notebook
        with open(input_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
        
        # 选择转换器
        exporters = {
            'html': HTMLExporter,
            'pdf': PDFExporter,
            'python': PythonExporter,
            'markdown': MarkdownExporter,
            'py': PythonExporter,
            'md': MarkdownExporter
        }
        
        if to_format.lower() not in exporters:
            raise ValueError(f"不支持的格式: {to_format}")
        
        exporter_class = exporters[to_format.lower()]
        exporter = exporter_class(**kwargs)
        
        # 转换
        output, resources = exporter.from_notebook_node(notebook)
        
        # 保存或返回
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
            return output_path
        else:
            return output
    
    def notebook_to_html(self, input_path: str, 
                         output_path: Optional[str] = None, **kwargs) -> str:
        """转换为HTML"""
        return self.convert_notebook(input_path, 'html', output_path, **kwargs)
    
    def notebook_to_python(self, input_path: str,
                           output_path: Optional[str] = None, **kwargs) -> str:
        """转换为Python脚本"""
        return self.convert_notebook(input_path, 'python', output_path, **kwargs)
    
    def notebook_to_markdown(self, input_path: str,
                             output_path: Optional[str] = None, **kwargs) -> str:
        """转换为Markdown"""
        return self.convert_notebook(input_path, 'markdown', output_path, **kwargs)
    
    def notebook_to_pdf(self, input_path: str,
                        output_path: Optional[str] = None, **kwargs) -> str:
        """转换为PDF"""
        return self.convert_notebook(input_path, 'pdf', output_path, **kwargs)
    
    # ==================== Notebook分析 ====================
    
    def get_notebook_info(self, notebook: Union[str, Any]) -> Dict:
        """
        获取Notebook信息
        
        Args:
            notebook: Notebook对象或文件路径
            
        Returns:
            Notebook信息字典
        """
        self._ensure_nbformat()
        
        if isinstance(notebook, str):
            notebook = self.load_notebook(notebook)
        
        info = {
            'nbformat': notebook.nbformat,
            'nbformat_minor': notebook.nbformat_minor,
            'num_cells': len(notebook.cells),
            'num_code_cells': self.count_cells(notebook, 'code'),
            'num_markdown_cells': self.count_cells(notebook, 'markdown'),
            'num_raw_cells': self.count_cells(notebook, 'raw'),
            'metadata_keys': list(notebook.metadata.keys())
        }
        
        # 获取内核信息
        if 'kernelspec' in notebook.metadata:
            info['kernel'] = notebook.metadata.kernelspec.get('name', 'unknown')
            info['language'] = notebook.metadata.kernelspec.get('language', 'unknown')
        else:
            info['kernel'] = 'unknown'
            info['language'] = 'unknown'
        
        return info
    
    def extract_code(self, notebook: Union[str, Any], 
                     join: bool = True) -> Union[str, List[str]]:
        """
        提取所有代码
        
        Args:
            notebook: Notebook对象或文件路径
            join: 是否合并为字符串
            
        Returns:
            代码字符串或代码列表
        """
        self._ensure_nbformat()
        
        if isinstance(notebook, str):
            notebook = self.load_notebook(notebook)
        
        code_cells = [cell.source for cell in notebook.cells if cell.cell_type == 'code']
        
        if join:
            return '\n\n'.join(code_cells)
        return code_cells
    
    def extract_markdown(self, notebook: Union[str, Any],
                         join: bool = True) -> Union[str, List[str]]:
        """
        提取所有Markdown内容
        
        Args:
            notebook: Notebook对象或文件路径
            join: 是否合并为字符串
            
        Returns:
            Markdown字符串或列表
        """
        self._ensure_nbformat()
        
        if isinstance(notebook, str):
            notebook = self.load_notebook(notebook)
        
        markdown_cells = [cell.source for cell in notebook.cells if cell.cell_type == 'markdown']
        
        if join:
            return '\n\n'.join(markdown_cells)
        return markdown_cells
    
    def search_in_notebook(self, notebook: Union[str, Any], 
                          pattern: str, cell_type: Optional[str] = None) -> List[Dict]:
        """
        在Notebook中搜索
        
        Args:
            notebook: Notebook对象或文件路径
            pattern: 搜索模式
            cell_type: 单元格类型过滤
            
        Returns:
            匹配的单元格列表
        """
        self._ensure_nbformat()
        
        if isinstance(notebook, str):
            notebook = self.load_notebook(notebook)
        
        results = []
        for i, cell in enumerate(notebook.cells):
            if cell_type and cell.cell_type != cell_type:
                continue
            if pattern in cell.source:
                results.append({
                    'index': i,
                    'cell_type': cell.cell_type,
                    'source': cell.source
                })
        
        return results
    
    def merge_notebooks(self, notebook_paths: List[str], 
                        output_path: Optional[str] = None) -> Any:
        """
        合并多个Notebook
        
        Args:
            notebook_paths: Notebook文件路径列表
            output_path: 输出路径（可选）
            
        Returns:
            合并后的Notebook对象
        """
        self._ensure_nbformat()
        
        merged = self.create_notebook()
        
        for path in notebook_paths:
            notebook = self.load_notebook(path)
            merged.cells.extend(notebook.cells)
            # 合并元数据
            merged.metadata.update(notebook.metadata)
        
        if output_path:
            self.save_notebook(merged, output_path)
        
        return merged
    
    def split_notebook(self, notebook: Union[str, Any], 
                       indices: List[int], output_dir: str) -> List[str]:
        """
        按索引分割Notebook
        
        Args:
            notebook: Notebook对象或文件路径
            indices: 分割点索引列表
            output_dir: 输出目录
            
        Returns:
            生成的文件路径列表
        """
        self._ensure_nbformat()
        
        if isinstance(notebook, str):
            notebook = self.load_notebook(notebook)
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        output_paths = []
        start_idx = 0
        
        for i, end_idx in enumerate(indices + [len(notebook.cells)]):
            new_notebook = self.create_notebook(metadata=dict(notebook.metadata))
            new_notebook.cells = notebook.cells[start_idx:end_idx]
            
            output_path = os.path.join(output_dir, f'split_{i+1}.ipynb')
            self.save_notebook(new_notebook, output_path)
            output_paths.append(output_path)
            
            start_idx = end_idx
        
        return output_paths


# ==================== 便捷函数 ====================

def create_notebook(cells: Optional[List[Dict]] = None) -> Any:
    """
    快速创建Notebook
    
    Args:
        cells: 单元格列表，每个单元格为{'type': 'code'|'markdown', 'source': str}
        
    Returns:
        Notebook对象
    """
    skill = JupyterSkill()
    notebook = skill.create_notebook()
    
    if cells:
        for cell in cells:
            if cell['type'] == 'code':
                skill.add_code_cell(notebook, cell['source'])
            elif cell['type'] == 'markdown':
                skill.add_markdown_cell(notebook, cell['source'])
    
    return notebook


def execute_notebook_file(input_path: str, output_path: Optional[str] = None) -> Any:
    """快速执行Notebook文件"""
    skill = JupyterSkill()
    return skill.execute_notebook(input_path, output_path)


def convert_notebook_file(input_path: str, to_format: str, 
                          output_path: Optional[str] = None) -> str:
    """快速转换Notebook"""
    skill = JupyterSkill()
    return skill.convert_notebook(input_path, to_format, output_path)


if __name__ == "__main__":
    # 简单的自我测试
    print("Jupyter Skill 测试")
    print("=" * 40)
    
    try:
        skill = JupyterSkill()
        
        # 测试创建
        notebook = skill.create_notebook()
        print("✓ 创建Notebook成功")
        
        # 测试添加单元格
        skill.add_markdown_cell(notebook, "# 测试")
        skill.add_code_cell(notebook, "print('Hello')")
        print(f"✓ 添加单元格成功，共 {skill.count_cells(notebook)} 个单元格")
        
        # 测试保存和加载
        skill.save_notebook(notebook, "test_notebook.ipynb")
        loaded = skill.load_notebook("test_notebook.ipynb")
        print(f"✓ 保存和加载成功，共 {skill.count_cells(loaded)} 个单元格")
        
        # 测试验证
        is_valid, error = skill.validate_notebook("test_notebook.ipynb")
        print(f"✓ 验证Notebook: {'有效' if is_valid else '无效'}")
        
        # 清理
        os.remove("test_notebook.ipynb")
        print("✓ 清理完成")
        
        print("\nJupyter Skill 测试完成!")
        
    except Exception as e:
        print(f"测试出错: {e}")
        print("注意：完整功能需要安装 jupyter, nbformat, nbconvert")
