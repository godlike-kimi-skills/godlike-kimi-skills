#!/usr/bin/env python3
"""
基础使用示例

展示如何使用 Skill Creator Enhanced 创建一个新 Skill
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import SkillCreator


def example_create_basic_skill():
    """示例1：创建基础 Skill"""
    print("=" * 60)
    print("示例1：创建基础 Skill")
    print("=" * 60)
    
    creator = SkillCreator(output_dir="./output")
    
    project_dir = creator.create_skill(
        skill_name="my-first-skill",
        skill_title="我的第一个技能",
        description="这是一个示例技能，展示基础功能",
        category="development",
        template="basic",
        with_tests=True,
        with_ci=True,
        with_examples=True
    )
    
    print(f"\n✅ Skill 创建成功！")
    print(f"   项目路径: {project_dir}")
    print(f"\n文件结构:")
    for file in sorted(project_dir.rglob("*")):
        if file.is_file():
            rel_path = file.relative_to(project_dir)
            print(f"   📄 {rel_path}")


def example_create_cli_tool():
    """示例2：创建 CLI 工具 Skill"""
    print("\n" + "=" * 60)
    print("示例2：创建 CLI 工具 Skill")
    print("=" * 60)
    
    creator = SkillCreator(output_dir="./output")
    
    project_dir = creator.create_skill(
        skill_name="file-converter",
        skill_title="文件转换器",
        description="支持多种格式的文件转换工具",
        category="automation",
        template="cli-tool",
        with_tests=True,
        with_ci=False,
        with_examples=True
    )
    
    print(f"\n✅ CLI 工具 Skill 创建成功！")
    print(f"   项目路径: {project_dir}")
    print(f"\n使用方式:")
    print(f"   python {project_dir}/main.py process --input data.txt --output result.json")


def example_create_data_processor():
    """示例3：创建数据处理器 Skill"""
    print("\n" + "=" * 60)
    print("示例3：创建数据处理器 Skill")
    print("=" * 60)
    
    creator = SkillCreator(output_dir="./output")
    
    project_dir = creator.create_skill(
        skill_name="csv-analyzer",
        skill_title="CSV分析器",
        description="读取、清洗、分析 CSV 文件",
        category="data",
        template="data-processor",
        with_tests=True,
        with_ci=True,
        with_examples=False
    )
    
    print(f"\n✅ 数据处理器 Skill 创建成功！")
    print(f"   项目路径: {project_dir}")
    print(f"\n功能特性:")
    print(f"   - 支持大数据集分块处理")
    print(f"   - 内置数据清洗功能")
    print(f"   - 错误处理和数据验证")


def example_validate_skill():
    """示例4：验证 Skill 项目"""
    print("\n" + "=" * 60)
    print("示例4：验证 Skill 项目")
    print("=" * 60)
    
    # 先创建一个 skill
    creator = SkillCreator(output_dir="./output")
    
    project_dir = creator.create_skill(
        skill_name="validate-test",
        skill_title="验证测试",
        description="用于验证的测试技能",
        with_tests=True,
        with_ci=True,
        with_examples=True
    )
    
    # 验证
    results = creator.validate_skill(str(project_dir))
    
    print(f"\n✅ 验证结果: {'通过' if results['valid'] else '失败'}")
    print(f"\n检查项:")
    for check, status in results["checks"].items():
        symbol = "✅" if status else "❌"
        print(f"   {symbol} {check}")
    
    if results["errors"]:
        print(f"\n❌ 错误:")
        for error in results["errors"]:
            print(f"   - {error}")
    
    if results["warnings"]:
        print(f"\n⚠️ 警告:")
        for warning in results["warnings"]:
            print(f"   - {warning}")


def example_list_templates():
    """示例5：列出可用模板"""
    print("\n" + "=" * 60)
    print("示例5：列出可用模板")
    print("=" * 60)
    
    creator = SkillCreator()
    templates = creator.list_templates()
    
    print(f"\n可用模板 ({len(templates)} 个):\n")
    for template in templates:
        print(f"  📋 {template['id']}")
        print(f"     名称: {template['name']}")
        print(f"     描述: {template['description']}")
        print()


if __name__ == "__main__":
    import tempfile
    import shutil
    
    # 使用临时目录
    temp_dir = tempfile.mkdtemp()
    original_dir = Path.cwd()
    
    try:
        # 切换到临时目录
        import os
        os.chdir(temp_dir)
        
        print("\n" + "🚀" * 30)
        print("Skill Creator Enhanced - 基础使用示例")
        print("🚀" * 30)
        
        # 运行示例
        example_create_basic_skill()
        example_create_cli_tool()
        example_create_data_processor()
        example_validate_skill()
        example_list_templates()
        
        print("\n" + "=" * 60)
        print("所有示例执行完成！")
        print("=" * 60)
        
    finally:
        # 清理
        os.chdir(original_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n🧹 清理临时文件: {temp_dir}")
