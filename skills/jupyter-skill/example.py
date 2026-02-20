#!/usr/bin/env python3
"""
Jupyter Skill Usage Examples
展示Jupyter Skill的各种使用场景
"""

from main import JupyterSkill
import os


def example_create_notebook():
    """示例：创建Notebook"""
    print("=" * 60)
    print("示例1: 创建Notebook")
    print("=" * 60)
    
    skill = JupyterSkill()
    
    # 创建新的Notebook
    notebook = skill.create_notebook()
    print("创建新的Notebook")
    
    # 添加Markdown单元格
    skill.add_markdown_cell(
        notebook,
        "# 数据分析示例\n\n这是一个使用Jupyter Skill创建的Notebook示例。"
    )
    print("添加Markdown单元格")
    
    # 添加代码单元格
    skill.add_code_cell(
        notebook,
        """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 创建示例数据
data = {
    'A': np.random.randn(100),
    'B': np.random.randn(100) + 2
}
df = pd.DataFrame(data)
print(df.head())"""
    )
    print("添加代码单元格")
    
    # 添加更多代码单元格
    skill.add_code_cell(
        notebook,
        """# 数据统计
df.describe()"""
    )
    
    skill.add_code_cell(
        notebook,
        """# 绘制直方图
plt.figure(figsize=(10, 6))
plt.hist(df['A'], bins=20, alpha=0.5, label='A')
plt.hist(df['B'], bins=20, alpha=0.5, label='B')
plt.legend()
plt.title('Distribution Comparison')
plt.show()"""
    )
    
    # 保存Notebook
    output_path = "example_notebook.ipynb"
    skill.save_notebook(notebook, output_path)
    print(f"Notebook已保存到 {output_path}")
    
    return notebook


def example_load_and_modify():
    """示例：加载和修改Notebook"""
    print("\n" + "=" * 60)
    print("示例2: 加载和修改Notebook")
    print("=" * 60)
    
    skill = JupyterSkill()
    
    # 先创建一个示例Notebook
    notebook = skill.create_notebook()
    skill.add_code_cell(notebook, "x = 10")
    skill.add_code_cell(notebook, "y = 20")
    skill.save_notebook(notebook, "temp_notebook.ipynb")
    
    # 加载Notebook
    loaded = skill.load_notebook("temp_notebook.ipynb")
    print(f"加载Notebook，包含 {skill.count_cells(loaded)} 个单元格")
    
    # 添加新单元格
    skill.add_code_cell(loaded, "print(f'x + y = {x + y}')")
    print(f"添加单元格后，共 {skill.count_cells(loaded)} 个单元格")
    
    # 列出所有单元格
    cells = skill.list_cells(loaded)
    print(f"\n单元格列表:")
    for i, cell in enumerate(cells):
        print(f"  [{i}] {cell['cell_type']}: {cell['source'][:50]}...")
    
    # 获取特定单元格
    cell = skill.get_cell(loaded, 0)
    print(f"\n第一个单元格类型: {cell['cell_type']}")
    
    # 修改单元格
    skill.update_cell(loaded, 0, "x = 100  # 修改后的代码")
    print("修改第一个单元格的内容")
    
    # 保存修改后的Notebook
    skill.save_notebook(loaded, "modified_notebook.ipynb")
    print("修改后的Notebook已保存到 modified_notebook.ipynb")
    
    # 清理
    os.remove("temp_notebook.ipynb")
    
    return loaded


def example_notebook_execution():
    """示例：执行Notebook"""
    print("\n" + "=" * 60)
    print("示例3: 执行Notebook")
    print("=" * 60)
    
    skill = JupyterSkill()
    
    # 创建一个可执行的Notebook
    notebook = skill.create_notebook()
    skill.add_code_cell(notebook, "print('Hello from Jupyter!')")
    skill.add_code_cell(notebook, "x = 5 + 3\nprint(f'x = {x}')")
    skill.add_code_cell(notebook, "[i**2 for i in range(5)]")
    skill.save_notebook(notebook, "to_execute.ipynb")
    
    print("创建待执行的Notebook")
    
    # 执行Notebook
    try:
        result = skill.execute_notebook(
            "to_execute.ipynb",
            output_path="executed_notebook.ipynb"
        )
        print("Notebook执行完成")
        print(f"输出已保存到 executed_notebook.ipynb")
        
        # 检查结果
        executed = skill.load_notebook("executed_notebook.ipynb")
        cells_with_output = sum(1 for cell in executed.cells if cell.get('outputs'))
        print(f"有输出的单元格数量: {cells_with_output}")
        
    except Exception as e:
        print(f"执行Notebook时出错: {e}")
    
    # 清理
    os.remove("to_execute.ipynb")


def example_notebook_conversion():
    """示例：Notebook格式转换"""
    print("\n" + "=" * 60)
    print("示例4: Notebook格式转换")
    print("=" * 60)
    
    skill = JupyterSkill()
    
    # 创建示例Notebook
    notebook = skill.create_notebook()
    skill.add_markdown_cell(notebook, "# 测试文档")
    skill.add_code_cell(notebook, "print('Hello World')")
    skill.save_notebook(notebook, "convert_example.ipynb")
    
    print("创建示例Notebook")
    
    # 转换为Python脚本
    try:
        skill.convert_notebook("convert_example.ipynb", "python", "output_script.py")
        print("转换为Python脚本: output_script.py")
        
        # 显示转换后的内容
        if os.path.exists("output_script.py"):
            with open("output_script.py", 'r', encoding='utf-8') as f:
                content = f.read()[:500]
            print(f"\nPython脚本预览:\n{content}...")
    except Exception as e:
        print(f"转换失败: {e}")
    
    # 转换为HTML
    try:
        skill.convert_notebook("convert_example.ipynb", "html", "output_notebook.html")
        print("\n转换为HTML: output_notebook.html")
    except Exception as e:
        print(f"HTML转换失败: {e}")
    
    # 转换为Markdown
    try:
        skill.convert_notebook("convert_example.ipynb", "markdown", "output_notebook.md")
        print("转换为Markdown: output_notebook.md")
    except Exception as e:
        print(f"Markdown转换失败: {e}")
    
    # 清理
    os.remove("convert_example.ipynb")


def example_notebook_analysis():
    """示例：Notebook分析"""
    print("\n" + "=" * 60)
    print("示例5: Notebook分析")
    print("=" * 60)
    
    skill = JupyterSkill()
    
    # 创建包含不同类型单元格的Notebook
    notebook = skill.create_notebook()
    skill.add_markdown_cell(notebook, "# 标题\n\n一些说明文字")
    skill.add_code_cell(notebook, "import numpy as np")
    skill.add_code_cell(notebook, "x = np.array([1, 2, 3])")
    skill.add_markdown_cell(notebook, "## 小节标题")
    skill.add_code_cell(notebook, "print(x)")
    skill.save_notebook(notebook, "analysis_example.ipynb")
    
    print("创建分析用Notebook")
    
    # 获取Notebook信息
    info = skill.get_notebook_info("analysis_example.ipynb")
    print(f"\nNotebook信息:")
    print(f"  格式版本: {info.get('nbformat', 'unknown')}")
    print(f"  单元格数量: {info.get('num_cells', 0)}")
    print(f"  代码单元格: {info.get('num_code_cells', 0)}")
    print(f"  Markdown单元格: {info.get('num_markdown_cells', 0)}")
    print(f"  内核: {info.get('kernel', 'unknown')}")
    
    # 提取代码
    code = skill.extract_code("analysis_example.ipynb")
    print(f"\n提取的代码:\n{code}")
    
    # 提取Markdown
    markdown = skill.extract_markdown("analysis_example.ipynb")
    print(f"\n提取的Markdown:\n{markdown}")
    
    # 清理
    os.remove("analysis_example.ipynb")


def example_cell_operations():
    """示例：单元格操作"""
    print("\n" + "=" * 60)
    print("示例6: 单元格操作")
    print("=" * 60)
    
    skill = JupyterSkill()
    
    # 创建Notebook
    notebook = skill.create_notebook()
    
    # 在特定位置插入单元格
    skill.insert_cell(notebook, 0, "markdown", "# 第一个标题")
    skill.insert_cell(notebook, 1, "code", "a = 1")
    skill.insert_cell(notebook, 2, "code", "b = 2")
    skill.insert_cell(notebook, 3, "code", "c = 3")
    
    print(f"创建Notebook，共 {skill.count_cells(notebook)} 个单元格")
    
    # 列出所有单元格
    print("\n原始单元格:")
    for i, cell in enumerate(skill.list_cells(notebook)):
        source = cell['source'][:30].replace('\n', ' ')
        print(f"  [{i}] {cell['cell_type']}: {source}...")
    
    # 删除单元格
    skill.delete_cell(notebook, 2)
    print(f"\n删除索引2的单元格后，共 {skill.count_cells(notebook)} 个单元格")
    
    # 移动单元格
    skill.move_cell(notebook, 2, 0)
    print("将索引2的单元格移动到索引0")
    
    print("\n最终单元格顺序:")
    for i, cell in enumerate(skill.list_cells(notebook)):
        source = cell['source'][:30].replace('\n', ' ')
        print(f"  [{i}] {cell['cell_type']}: {source}...")


def example_batch_operations():
    """示例：批量操作"""
    print("\n" + "=" * 60)
    print("示例7: 批量操作")
    print("=" * 60)
    
    skill = JupyterSkill()
    
    # 创建多个Notebook
    notebook_files = []
    for i in range(3):
        notebook = skill.create_notebook()
        skill.add_markdown_cell(notebook, f"# Notebook {i+1}")
        skill.add_code_cell(notebook, f"print('This is notebook {i+1}')")
        filename = f"batch_notebook_{i+1}.ipynb"
        skill.save_notebook(notebook, filename)
        notebook_files.append(filename)
    
    print(f"创建 {len(notebook_files)} 个Notebook")
    
    # 批量验证
    print("\n验证Notebook格式:")
    for filename in notebook_files:
        is_valid = skill.validate_notebook(filename)
        print(f"  {filename}: {'有效' if is_valid else '无效'}")
    
    # 批量获取信息
    print("\n批量获取信息:")
    for filename in notebook_files:
        info = skill.get_notebook_info(filename)
        print(f"  {filename}: {info['num_cells']} 个单元格")
    
    # 清理
    for filename in notebook_files:
        os.remove(filename)
    print("\n批量清理完成")


def main():
    """主函数：运行所有示例"""
    try:
        example_create_notebook()
        example_load_and_modify()
        example_notebook_execution()
        example_notebook_conversion()
        example_notebook_analysis()
        example_cell_operations()
        example_batch_operations()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
