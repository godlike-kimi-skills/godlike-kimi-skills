#!/usr/bin/env python3
"""
高级使用示例

展示 Skill Creator Enhanced 的高级功能和最佳实践
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import SkillCreator


def example_custom_configuration():
    """示例1：自定义配置生成 Skill"""
    print("=" * 60)
    print("示例1：自定义配置生成")
    print("=" * 60)
    
    creator = SkillCreator(output_dir="./custom-output")
    
    # 只生成核心文件，不包含测试和 CI/CD
    project_dir = creator.create_skill(
        skill_name="minimal-skill",
        skill_title="最小化技能",
        description="不包含测试和 CI/CD 的最小化版本",
        category="other",
        template="basic",
        with_tests=False,  # 不生成测试
        with_ci=False,     # 不生成 CI/CD
        with_examples=False # 不生成示例
    )
    
    print(f"\n✅ 最小化 Skill 创建成功！")
    print(f"   项目路径: {project_dir}")
    print(f"\n生成的文件:")
    for file in sorted(project_dir.glob("*")):
        if file.is_file():
            print(f"   📄 {file.name}")


def example_batch_creation():
    """示例2：批量创建多个 Skills"""
    print("\n" + "=" * 60)
    print("示例2：批量创建 Skills")
    print("=" * 60)
    
    creator = SkillCreator(output_dir="./batch-output")
    
    skills_to_create = [
        {
            "name": "web-scraper",
            "title": "网页抓取器",
            "description": "从网页提取结构化数据",
            "category": "automation"
        },
        {
            "name": "pdf-converter",
            "title": "PDF转换器",
            "description": "PDF与其他格式互转",
            "category": "automation"
        },
        {
            "name": "data-cleaner",
            "title": "数据清洗器",
            "description": "清洗和标准化数据",
            "category": "data"
        }
    ]
    
    print(f"\n批量创建 {len(skills_to_create)} 个 Skills...\n")
    
    for i, skill_config in enumerate(skills_to_create, 1):
        print(f"  [{i}/{len(skills_to_create)}] 创建 {skill_config['name']}...")
        
        project_dir = creator.create_skill(
            skill_name=skill_config["name"],
            skill_title=skill_config["title"],
            description=skill_config["description"],
            category=skill_config["category"],
            template="basic",
            with_tests=True,
            with_ci=False,
            with_examples=False
        )
        
        print(f"       ✅ 完成: {project_dir}")
    
    print(f"\n✅ 批量创建完成！")


def example_skill_json_customization():
    """示例3：自定义 skill.json 后修改"""
    print("\n" + "=" * 60)
    print("示例3：自定义 skill.json")
    print("=" * 60)
    
    creator = SkillCreator(output_dir="./custom-json-output")
    
    # 创建基础 skill
    project_dir = creator.create_skill(
        skill_name="custom-config-skill",
        skill_title="自定义配置技能",
        description="展示如何自定义配置",
        with_tests=False,
        with_ci=False,
        with_examples=False
    )
    
    # 读取并修改 skill.json
    skill_json_path = project_dir / "skill.json"
    with open(skill_json_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # 添加自定义配置
    config["custom_field"] = "custom_value"
    config["parameters"] = [
        {
            "name": "url",
            "type": "string",
            "required": True,
            "description": "目标URL"
        },
        {
            "name": "timeout",
            "type": "number",
            "required": False,
            "default": 30,
            "description": "超时时间（秒）"
        }
    ]
    
    # 保存修改后的配置
    with open(skill_json_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Skill 创建并自定义配置完成！")
    print(f"   项目路径: {project_dir}")
    print(f"\n修改后的 skill.json:")
    print(json.dumps(config, indent=2, ensure_ascii=False))


def example_validation_workflow():
    """示例4：验证工作流集成"""
    print("\n" + "=" * 60)
    print("示例4：验证工作流集成")
    print("=" * 60)
    
    creator = SkillCreator(output_dir="./validation-workflow")
    
    # 创建一个有效的 skill
    valid_project = creator.create_skill(
        skill_name="valid-skill",
        skill_title="有效技能",
        description="用于验证测试",
        with_tests=True,
        with_ci=True,
        with_examples=True
    )
    
    # 验证
    results = creator.validate_skill(str(valid_project))
    
    print(f"\n✅ 有效 Skill 验证:")
    print(f"   结果: {'通过' if results['valid'] else '失败'}")
    print(f"   检查项数: {len(results['checks'])}")
    print(f"   错误数: {len(results['errors'])}")
    print(f"   警告数: {len(results['warnings'])}")
    
    # 创建一个无效的 skill（模拟）
    import tempfile
    import shutil
    
    invalid_dir = Path(tempfile.mkdtemp()) / "invalid-skill"
    invalid_dir.mkdir(parents=True)
    
    # 只创建部分文件
    (invalid_dir / "skill.json").write_text('{"invalid": json}')
    (invalid_dir / "main.py").write_text("# empty")
    
    results = creator.validate_skill(str(invalid_dir))
    
    print(f"\n❌ 无效 Skill 验证:")
    print(f"   结果: {'通过' if results['valid'] else '失败'}")
    print(f"   错误:")
    for error in results["errors"][:3]:  # 只显示前3个
        print(f"      - {error}")
    
    # 清理
    shutil.rmtree(invalid_dir.parent, ignore_errors=True)


def example_template_comparison():
    """示例5：模板对比"""
    print("\n" + "=" * 60)
    print("示例5：不同模板对比")
    print("=" * 60)
    
    creator = SkillCreator(output_dir="./template-comparison")
    
    templates = ["basic", "cli-tool", "data-processor", "automation"]
    
    print(f"\n使用不同模板创建相同功能的 Skill:\n")
    
    for template in templates:
        skill_name = f"comparison-{template}"
        
        project_dir = creator.create_skill(
            skill_name=skill_name,
            skill_title=f"模板对比 - {template}",
            description="用于对比不同模板的示例",
            template=template,
            with_tests=False,
            with_ci=False,
            with_examples=False
        )
        
        # 统计文件数量
        file_count = len(list(project_dir.rglob("*")))
        
        print(f"  📋 {template:<15} - {file_count} 个文件/目录")
        
        # 显示 main.py 的第一行
        main_py = project_dir / "main.py"
        with open(main_py, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
        
        print(f"      入口文件: {first_line}")


def example_best_practices():
    """示例6：最佳实践"""
    print("\n" + "=" * 60)
    print("示例6：最佳实践")
    print("=" * 60)
    
    print("""
创建生产级 Skill 的最佳实践：

1. 命名规范
   ✅ 使用小写字母和连字符: web-scraper
   ❌ 避免: WebScraper, web_scraper, web scraper

2. 目录结构
   my-skill/
   ├── skill.json          # 清单文件
   ├── SKILL.md            # 使用说明
   ├── README.md           # 项目文档
   ├── LICENSE             # MIT 许可证
   ├── main.py             # 入口文件
   ├── requirements.txt    # 依赖
   ├── tests/              # 测试
   └── examples/           # 示例

3. 代码规范
   - 使用类型注解
   - 编写文档字符串
   - 处理异常情况
   - 最小化依赖

4. 测试要求
   - 至少 3 个测试用例
   - 覆盖正常和异常情况
   - 测试边界条件

5. 文档要求
   - 清晰的安装说明
   - 可复制的使用示例
   - 完整的参数说明
   - 更新日志

6. 开源合规
   - MIT 许可证
   - 无硬编码敏感信息
   - 符合 Kimi CLI 规范
""")


def example_project_structure_analysis():
    """示例7：项目结构分析"""
    print("\n" + "=" * 60)
    print("示例7：项目结构分析")
    print("=" * 60)
    
    creator = SkillCreator(output_dir="./structure-analysis")
    
    # 创建完整功能的 skill
    project_dir = creator.create_skill(
        skill_name="full-featured-skill",
        skill_title="全功能技能",
        description="展示完整的项目结构",
        template="data-processor",
        with_tests=True,
        with_ci=True,
        with_examples=True
    )
    
    print(f"\n✅ 全功能 Skill 创建成功！")
    print(f"   路径: {project_dir}")
    
    # 分析结构
    print(f"\n📁 项目结构分析:\n")
    
    categories = {
        "配置文件": ["skill.json", ".gitignore"],
        "文档": ["SKILL.md", "README.md", "LICENSE"],
        "源代码": ["main.py"],
        "依赖": ["requirements.txt"],
        "测试": [],
        "示例": [],
        "CI/CD": []
    }
    
    # 统计各类文件
    for file in project_dir.rglob("*"):
        if file.is_file():
            rel_path = str(file.relative_to(project_dir))
            
            if rel_path.startswith("tests/"):
                categories["测试"].append(rel_path)
            elif rel_path.startswith("examples/"):
                categories["示例"].append(rel_path)
            elif rel_path.startswith(".github/"):
                categories["CI/CD"].append(rel_path)
    
    for category, files in categories.items():
        if files:
            print(f"  {category}:")
            for file in files:
                print(f"    📄 {file}")
    
    # 代码统计
    total_lines = 0
    for file in project_dir.rglob("*.py"):
        if file.is_file():
            with open(file, "r", encoding="utf-8") as f:
                total_lines += len(f.readlines())
    
    print(f"\n📊 代码统计:")
    print(f"   Python 文件数: {len(list(project_dir.rglob('*.py')))}")
    print(f"   总代码行数: {total_lines}")


if __name__ == "__main__":
    import os
    import shutil
    
    # 使用临时目录
    temp_dir = tempfile.mkdtemp()
    original_dir = Path.cwd()
    
    try:
        os.chdir(temp_dir)
        
        print("\n" + "🚀" * 30)
        print("Skill Creator Enhanced - 高级使用示例")
        print("🚀" * 30)
        
        # 运行示例
        example_custom_configuration()
        example_batch_creation()
        example_skill_json_customization()
        example_validation_workflow()
        example_template_comparison()
        example_best_practices()
        example_project_structure_analysis()
        
        print("\n" + "=" * 60)
        print("所有高级示例执行完成！")
        print("=" * 60)
        
    finally:
        os.chdir(original_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n🧹 清理临时文件: {temp_dir}")
