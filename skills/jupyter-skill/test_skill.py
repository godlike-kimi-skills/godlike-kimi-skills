#!/usr/bin/env python3
"""
Jupyter Skill - Test Suite
Jupyter技能测试套件
"""

import unittest
import os
import tempfile
import shutil
from pathlib import Path

from main import JupyterSkill, create_notebook, execute_notebook_file, convert_notebook_file


class TestJupyterSkill(unittest.TestCase):
    """JupyterSkill测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.test_dir = tempfile.mkdtemp()
        cls.skill = JupyterSkill()
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    def _get_test_path(self, filename: str) -> str:
        """获取测试文件路径"""
        return os.path.join(self.test_dir, filename)
    
    # ==================== Notebook创建和加载测试 ====================
    
    def test_create_notebook(self):
        """测试创建Notebook"""
        notebook = self.skill.create_notebook()
        self.assertIsNotNone(notebook)
        self.assertEqual(len(notebook.cells), 0)
    
    def test_create_notebook_with_metadata(self):
        """测试带元数据创建Notebook"""
        metadata = {'custom': {'author': 'test'}}
        notebook = self.skill.create_notebook(metadata=metadata)
        self.assertIn('custom', notebook.metadata)
    
    def test_save_and_load_notebook(self):
        """测试保存和加载Notebook"""
        notebook = self.skill.create_notebook()
        self.skill.add_code_cell(notebook, "x = 1")
        
        filepath = self._get_test_path('test.ipynb')
        self.skill.save_notebook(notebook, filepath)
        self.assertTrue(os.path.exists(filepath))
        
        loaded = self.skill.load_notebook(filepath)
        self.assertEqual(len(loaded.cells), 1)
        self.assertEqual(loaded.cells[0].source, "x = 1")
    
    def test_validate_valid_notebook(self):
        """测试验证有效的Notebook"""
        notebook = self.skill.create_notebook()
        filepath = self._get_test_path('valid.ipynb')
        self.skill.save_notebook(notebook, filepath)
        
        is_valid, error = self.skill.validate_notebook(filepath)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_invalid_file(self):
        """测试验证无效文件"""
        filepath = self._get_test_path('invalid.txt')
        with open(filepath, 'w') as f:
            f.write("这不是有效的notebook")
        
        is_valid, error = self.skill.validate_notebook(filepath)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    # ==================== 单元格管理测试 ====================
    
    def test_add_code_cell(self):
        """测试添加代码单元格"""
        notebook = self.skill.create_notebook()
        cell = self.skill.add_code_cell(notebook, "print('hello')")
        
        self.assertEqual(len(notebook.cells), 1)
        self.assertEqual(cell.cell_type, 'code')
        self.assertEqual(cell.source, "print('hello')")
    
    def test_add_markdown_cell(self):
        """测试添加Markdown单元格"""
        notebook = self.skill.create_notebook()
        cell = self.skill.add_markdown_cell(notebook, "# 标题")
        
        self.assertEqual(len(notebook.cells), 1)
        self.assertEqual(cell.cell_type, 'markdown')
        self.assertEqual(cell.source, "# 标题")
    
    def test_add_raw_cell(self):
        """测试添加Raw单元格"""
        notebook = self.skill.create_notebook()
        cell = self.skill.add_raw_cell(notebook, "raw content")
        
        self.assertEqual(len(notebook.cells), 1)
        self.assertEqual(cell.cell_type, 'raw')
    
    def test_insert_cell(self):
        """测试插入单元格"""
        notebook = self.skill.create_notebook()
        self.skill.add_code_cell(notebook, "first")
        self.skill.add_code_cell(notebook, "third")
        
        self.skill.insert_cell(notebook, 1, 'code', "second")
        
        self.assertEqual(len(notebook.cells), 3)
        self.assertEqual(notebook.cells[1].source, "second")
    
    def test_get_cell(self):
        """测试获取单元格"""
        notebook = self.skill.create_notebook()
        self.skill.add_code_cell(notebook, "test")
        
        cell = self.skill.get_cell(notebook, 0)
        self.assertEqual(cell.source, "test")
    
    def test_get_cell_out_of_range(self):
        """测试获取超出范围的单元格"""
        notebook = self.skill.create_notebook()
        with self.assertRaises(IndexError):
            self.skill.get_cell(notebook, 0)
    
    def test_update_cell(self):
        """测试更新单元格"""
        notebook = self.skill.create_notebook()
        self.skill.add_code_cell(notebook, "old")
        
        self.skill.update_cell(notebook, 0, "new")
        self.assertEqual(notebook.cells[0].source, "new")
    
    def test_delete_cell(self):
        """测试删除单元格"""
        notebook = self.skill.create_notebook()
        self.skill.add_code_cell(notebook, "first")
        self.skill.add_code_cell(notebook, "second")
        
        deleted = self.skill.delete_cell(notebook, 0)
        self.assertEqual(deleted.source, "first")
        self.assertEqual(len(notebook.cells), 1)
        self.assertEqual(notebook.cells[0].source, "second")
    
    def test_move_cell(self):
        """测试移动单元格"""
        notebook = self.skill.create_notebook()
        self.skill.add_code_cell(notebook, "A")
        self.skill.add_code_cell(notebook, "B")
        self.skill.add_code_cell(notebook, "C")
        
        self.skill.move_cell(notebook, 2, 0)
        self.assertEqual(notebook.cells[0].source, "C")
        self.assertEqual(notebook.cells[1].source, "A")
        self.assertEqual(notebook.cells[2].source, "B")
    
    def test_clear_cell_output(self):
        """测试清除单元格输出"""
        notebook = self.skill.create_notebook()
        cell = self.skill.add_code_cell(notebook, "print('test')")
        # 模拟输出
        cell.outputs = [{'output_type': 'stream', 'text': 'test\n'}]
        cell.execution_count = 1
        
        self.skill.clear_cell_output(notebook, 0)
        self.assertEqual(len(cell.outputs), 0)
        self.assertIsNone(cell.execution_count)
    
    def test_clear_all_outputs(self):
        """测试清除所有输出"""
        notebook = self.skill.create_notebook()
        cell1 = self.skill.add_code_cell(notebook, "print('1')")
        cell2 = self.skill.add_code_cell(notebook, "print('2')")
        cell1.outputs = [{'output_type': 'stream'}]
        cell2.outputs = [{'output_type': 'stream'}]
        
        self.skill.clear_all_outputs(notebook)
        self.assertEqual(len(cell1.outputs), 0)
        self.assertEqual(len(cell2.outputs), 0)
    
    def test_count_cells(self):
        """测试统计单元格"""
        notebook = self.skill.create_notebook()
        self.skill.add_markdown_cell(notebook, "# Title")
        self.skill.add_code_cell(notebook, "x = 1")
        self.skill.add_code_cell(notebook, "y = 2")
        
        self.assertEqual(self.skill.count_cells(notebook), 3)
        self.assertEqual(self.skill.count_cells(notebook, 'code'), 2)
        self.assertEqual(self.skill.count_cells(notebook, 'markdown'), 1)
    
    def test_list_cells(self):
        """测试列出单元格"""
        notebook = self.skill.create_notebook()
        self.skill.add_code_cell(notebook, "x = 1")
        self.skill.add_markdown_cell(notebook, "# Title")
        
        cells = self.skill.list_cells(notebook)
        self.assertEqual(len(cells), 2)
        self.assertEqual(cells[0]['cell_type'], 'code')
        self.assertEqual(cells[1]['cell_type'], 'markdown')
    
    # ==================== Notebook分析测试 ====================
    
    def test_get_notebook_info(self):
        """测试获取Notebook信息"""
        notebook = self.skill.create_notebook()
        self.skill.add_code_cell(notebook, "x = 1")
        self.skill.add_markdown_cell(notebook, "# Title")
        
        info = self.skill.get_notebook_info(notebook)
        self.assertEqual(info['num_cells'], 2)
        self.assertEqual(info['num_code_cells'], 1)
        self.assertEqual(info['num_markdown_cells'], 1)
    
    def test_extract_code(self):
        """测试提取代码"""
        notebook = self.skill.create_notebook()
        self.skill.add_code_cell(notebook, "x = 1")
        self.skill.add_code_cell(notebook, "y = 2")
        self.skill.add_markdown_cell(notebook, "# Title")
        
        code = self.skill.extract_code(notebook, join=True)
        self.assertIn("x = 1", code)
        self.assertIn("y = 2", code)
        
        code_list = self.skill.extract_code(notebook, join=False)
        self.assertEqual(len(code_list), 2)
    
    def test_extract_markdown(self):
        """测试提取Markdown"""
        notebook = self.skill.create_notebook()
        self.skill.add_markdown_cell(notebook, "# Title")
        self.skill.add_markdown_cell(notebook, "Some text")
        self.skill.add_code_cell(notebook, "x = 1")
        
        md = self.skill.extract_markdown(notebook, join=True)
        self.assertIn("# Title", md)
        self.assertIn("Some text", md)
        self.assertNotIn("x = 1", md)
    
    def test_search_in_notebook(self):
        """测试在Notebook中搜索"""
        notebook = self.skill.create_notebook()
        self.skill.add_code_cell(notebook, "import numpy as np")
        self.skill.add_code_cell(notebook, "import pandas as pd")
        self.skill.add_markdown_cell(notebook, "numpy tutorial")
        
        results = self.skill.search_in_notebook(notebook, "numpy")
        self.assertEqual(len(results), 2)
        
        results = self.skill.search_in_notebook(notebook, "numpy", cell_type='code')
        self.assertEqual(len(results), 1)
    
    def test_search_from_file(self):
        """测试从文件搜索"""
        notebook = self.skill.create_notebook()
        self.skill.add_code_cell(notebook, "test_search_content")
        filepath = self._get_test_path('search.ipynb')
        self.skill.save_notebook(notebook, filepath)
        
        results = self.skill.search_in_notebook(filepath, "test_search")
        self.assertEqual(len(results), 1)
    
    # ==================== Notebook合并和分割测试 ====================
    
    def test_merge_notebooks(self):
        """测试合并Notebooks"""
        # 创建两个Notebook
        nb1 = self.skill.create_notebook()
        self.skill.add_code_cell(nb1, "# Notebook 1")
        
        nb2 = self.skill.create_notebook()
        self.skill.add_code_cell(nb2, "# Notebook 2")
        
        # 保存
        path1 = self._get_test_path('merge1.ipynb')
        path2 = self._get_test_path('merge2.ipynb')
        self.skill.save_notebook(nb1, path1)
        self.skill.save_notebook(nb2, path2)
        
        # 合并
        merged = self.skill.merge_notebooks([path1, path2])
        self.assertEqual(len(merged.cells), 2)
    
    def test_merge_notebooks_with_output(self):
        """测试合并Notebooks并保存"""
        nb1 = self.skill.create_notebook()
        self.skill.add_code_cell(nb1, "cell 1")
        
        nb2 = self.skill.create_notebook()
        self.skill.add_code_cell(nb2, "cell 2")
        
        path1 = self._get_test_path('merge_out1.ipynb')
        path2 = self._get_test_path('merge_out2.ipynb')
        output_path = self._get_test_path('merged.ipynb')
        self.skill.save_notebook(nb1, path1)
        self.skill.save_notebook(nb2, path2)
        
        self.skill.merge_notebooks([path1, path2], output_path)
        self.assertTrue(os.path.exists(output_path))
    
    def test_split_notebook(self):
        """测试分割Notebook"""
        notebook = self.skill.create_notebook()
        self.skill.add_code_cell(notebook, "cell 1")
        self.skill.add_code_cell(notebook, "cell 2")
        self.skill.add_code_cell(notebook, "cell 3")
        self.skill.add_code_cell(notebook, "cell 4")
        
        filepath = self._get_test_path('split.ipynb')
        self.skill.save_notebook(notebook, filepath)
        
        output_dir = self._get_test_path('split_output')
        paths = self.skill.split_notebook(filepath, [2], output_dir)
        
        self.assertEqual(len(paths), 2)
        self.assertTrue(os.path.exists(paths[0]))
        self.assertTrue(os.path.exists(paths[1]))


class TestConvenienceFunctions(unittest.TestCase):
    """便捷函数测试"""
    
    def test_create_notebook_basic(self):
        """测试基本创建Notebook"""
        notebook = create_notebook()
        self.assertEqual(len(notebook.cells), 0)
    
    def test_create_notebook_with_cells(self):
        """测试带单元格创建Notebook"""
        cells = [
            {'type': 'markdown', 'source': '# Title'},
            {'type': 'code', 'source': 'x = 1'}
        ]
        notebook = create_notebook(cells)
        self.assertEqual(len(notebook.cells), 2)


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""
    
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp()
        cls.skill = JupyterSkill()
    
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    def _get_test_path(self, filename: str) -> str:
        return os.path.join(self.test_dir, filename)
    
    def test_empty_notebook_operations(self):
        """测试空Notebook操作"""
        notebook = self.skill.create_notebook()
        
        self.assertEqual(self.skill.count_cells(notebook), 0)
        self.assertEqual(self.skill.list_cells(notebook), [])
        self.assertEqual(self.skill.extract_code(notebook), "")
        self.assertEqual(self.skill.extract_markdown(notebook), "")
    
    def test_single_cell_notebook(self):
        """测试单单元格Notebook"""
        notebook = self.skill.create_notebook()
        self.skill.add_code_cell(notebook, "pass")
        
        self.assertEqual(self.skill.count_cells(notebook), 1)
        cell = self.skill.get_cell(notebook, 0)
        self.assertEqual(cell.source, "pass")
    
    def test_move_cell_to_same_position(self):
        """测试移动单元格到相同位置"""
        notebook = self.skill.create_notebook()
        self.skill.add_code_cell(notebook, "A")
        self.skill.add_code_cell(notebook, "B")
        
        self.skill.move_cell(notebook, 0, 0)
        self.assertEqual(notebook.cells[0].source, "A")
        self.assertEqual(notebook.cells[1].source, "B")
    
    def test_move_cell_to_end(self):
        """测试移动单元格到末尾"""
        notebook = self.skill.create_notebook()
        self.skill.add_code_cell(notebook, "A")
        self.skill.add_code_cell(notebook, "B")
        self.skill.add_code_cell(notebook, "C")
        
        self.skill.move_cell(notebook, 0, 3)
        self.assertEqual(notebook.cells[0].source, "B")
        self.assertEqual(notebook.cells[1].source, "C")
        self.assertEqual(notebook.cells[2].source, "A")
    
    def test_delete_only_cell(self):
        """测试删除唯一单元格"""
        notebook = self.skill.create_notebook()
        self.skill.add_code_cell(notebook, "only")
        
        deleted = self.skill.delete_cell(notebook, 0)
        self.assertEqual(deleted.source, "only")
        self.assertEqual(len(notebook.cells), 0)
    
    def test_search_no_results(self):
        """测试搜索无结果"""
        notebook = self.skill.create_notebook()
        self.skill.add_code_cell(notebook, "hello")
        
        results = self.skill.search_in_notebook(notebook, "notfound")
        self.assertEqual(len(results), 0)
    
    def test_merge_single_notebook(self):
        """测试合并单个Notebook"""
        notebook = self.skill.create_notebook()
        self.skill.add_code_cell(notebook, "single")
        
        filepath = self._get_test_path('single.ipynb')
        self.skill.save_notebook(notebook, filepath)
        
        merged = self.skill.merge_notebooks([filepath])
        self.assertEqual(len(merged.cells), 1)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestJupyterSkill))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
