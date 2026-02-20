#!/usr/bin/env python3
"""
GitLab CI Skill - 基础使用示例

展示如何：
1. 初始化Skill
2. 创建和编辑.gitlab-ci.yml
3. 管理Runners
4. 查看和触发Pipelines
5. 管理CI/CD变量
"""

import os
from main import GitLabCISkill


def example_1_basic_init():
    """示例1: 基础初始化"""
    print("=" * 60)
    print("示例1: 基础初始化")
    print("=" * 60)
    
    # 方式1: 直接传入参数
    skill = GitLabCISkill(
        token="your-gitlab-token",
        project="group/project",
        url="https://gitlab.com"
    )
    print("✓ 使用参数初始化成功")
    
    # 方式2: 使用环境变量
    # export GITLAB_TOKEN=your-token
    # export GITLAB_PROJECT=group/project
    # skill = GitLabCISkill()
    # print("✓ 使用环境变量初始化成功")


def example_2_create_ci_config():
    """示例2: 创建CI配置"""
    print("\n" + "=" * 60)
    print("示例2: 创建CI配置")
    print("=" * 60)
    
    skill = GitLabCISkill(
        token=os.getenv("GITLAB_TOKEN", "your-token"),
        project=os.getenv("GITLAB_PROJECT", "group/project")
    )
    
    result = skill.create_ci_config(
        stages=["test", "build", "deploy"],
        jobs={
            "test": {
                "stage": "test",
                "image": "python:3.11",
                "script": [
                    "pip install -r requirements.txt",
                    "pytest"
                ]
            },
            "build": {
                "stage": "build",
                "image": "python:3.11",
                "script": ["python setup.py build"],
                "artifacts": {
                    "paths": ["dist/"]
                }
            },
            "deploy": {
                "stage": "deploy",
                "script": ["echo 'Deploying...'"],
                "only": ["main"]
            }
        },
        variables={
            "PIP_CACHE_DIR": "$CI_PROJECT_DIR/.cache/pip"
        },
        ref="main"
    )
    
    if result["success"]:
        print(f"✓ CI配置创建成功")
        print(f"  动作: {result['data']['action']}")
        print(f"  Commit: {result['data']['commit_id']}")
    else:
        print(f"✗ 创建失败: {result['error']}")


def example_3_update_ci_job():
    """示例3: 更新特定Job"""
    print("\n" + "=" * 60)
    print("示例3: 更新特定Job")
    print("=" * 60)
    
    skill = GitLabCISkill(
        token=os.getenv("GITLAB_TOKEN", "your-token"),
        project=os.getenv("GITLAB_PROJECT", "group/project")
    )
    
    result = skill.update_ci_job("test", {
        "stage": "test",
        "image": "python:3.11",
        "script": [
            "pip install -r requirements.txt",
            "pip install pytest pytest-cov",
            "pytest --cov=. --cov-report=xml"
        ],
        "artifacts": {
            "reports": {
                "coverage_report": {
                    "coverage_format": "cobertura",
                    "path": "coverage.xml"
                }
            }
        }
    })
    
    if result["success"]:
        print("✓ Job更新成功")


def example_4_validate_config():
    """示例4: 验证CI配置"""
    print("\n" + "=" * 60)
    print("示例4: 验证CI配置")
    print("=" * 60)
    
    skill = GitLabCISkill(
        token=os.getenv("GITLAB_TOKEN", "your-token"),
        project=os.getenv("GITLAB_PROJECT", "group/project")
    )
    
    # 验证当前配置
    result = skill.validate_ci_config()
    if result["success"]:
        if result["data"]["valid"]:
            print("✓ CI配置有效")
        else:
            print("✗ CI配置无效")
            for error in result["data"]["errors"]:
                print(f"  - {error}")
        
        if result["data"]["warnings"]:
            print("⚠ 警告:")
            for warning in result["data"]["warnings"]:
                print(f"  - {warning}")


def example_5_list_runners():
    """示例5: 列出Runners"""
    print("\n" + "=" * 60)
    print("示例5: 列出Runners")
    print("=" * 60)
    
    skill = GitLabCISkill(
        token=os.getenv("GITLAB_TOKEN", "your-token"),
        project=os.getenv("GITLAB_PROJECT", "group/project")
    )
    
    result = skill.list_runners()
    if result["success"]:
        print(f"✓ 共有 {len(result['data'])} 个Runner")
        for runner in result["data"]:
            status = "在线" if runner.get("online") else "离线"
            tags = ", ".join(runner.get("tags", []))
            print(f"  - {runner['description']} ({status})")
            print(f"    标签: {tags}")


def example_6_list_pipelines():
    """示例6: 列出Pipelines"""
    print("\n" + "=" * 60)
    print("示例6: 列出Pipelines")
    print("=" * 60)
    
    skill = GitLabCISkill(
        token=os.getenv("GITLAB_TOKEN", "your-token"),
        project=os.getenv("GITLAB_PROJECT", "group/project")
    )
    
    result = skill.list_pipelines(limit=5)
    if result["success"]:
        print(f"✓ 最近Pipelines:")
        for pipe in result["data"]:
            status_icon = {
                "success": "✓",
                "failed": "✗",
                "running": "▶",
                "pending": "○",
                "canceled": "⊘"
            }.get(pipe["status"], "?")
            print(f"  {status_icon} Pipeline #{pipe['id']} ({pipe['ref']}): {pipe['status']}")


def example_7_trigger_pipeline():
    """示例7: 触发Pipeline"""
    print("\n" + "=" * 60)
    print("示例7: 触发Pipeline")
    print("=" * 60)
    
    skill = GitLabCISkill(
        token=os.getenv("GITLAB_TOKEN", "your-token"),
        project=os.getenv("GITLAB_PROJECT", "group/project")
    )
    
    result = skill.trigger_pipeline(
        ref="main",
        variables={"DEPLOY_ENV": "staging", "DEBUG": "true"}
    )
    
    if result["success"]:
        print(f"✓ Pipeline已触发")
        print(f"  ID: {result['data']['id']}")
        print(f"  状态: {result['data']['status']}")
        print(f"  URL: {result['data']['web_url']}")


def example_8_get_pipeline_details():
    """示例8: 获取Pipeline详情"""
    print("\n" + "=" * 60)
    print("示例8: 获取Pipeline详情")
    print("=" * 60)
    
    skill = GitLabCISkill(
        token=os.getenv("GITLAB_TOKEN", "your-token"),
        project=os.getenv("GITLAB_PROJECT", "group/project")
    )
    
    # 先获取最近的Pipeline
    pipes = skill.list_pipelines(limit=1)
    if pipes["success"] and pipes["data"]:
        pipeline_id = pipes["data"][0]["id"]
        result = skill.get_pipeline(pipeline_id)
        
        if result["success"]:
            print(f"✓ Pipeline #{pipeline_id} 详情:")
            print(f"  状态: {result['data']['status']}")
            print(f"  分支: {result['data']['ref']}")
            print(f"  Jobs:")
            for job in result["data"]["jobs"]:
                print(f"    - {job['name']} ({job['stage']}): {job['status']}")


def example_9_manage_variables():
    """示例9: 管理CI/CD变量"""
    print("\n" + "=" * 60)
    print("示例9: 管理CI/CD变量")
    print("=" * 60)
    
    skill = GitLabCISkill(
        token=os.getenv("GITLAB_TOKEN", "your-token"),
        project=os.getenv("GITLAB_PROJECT", "group/project")
    )
    
    # 设置变量
    result = skill.set_variable(
        key="API_KEY",
        value="secret-api-key",
        protected=True,
        masked=True
    )
    if result["success"]:
        print(f"✓ 变量设置成功: {result['data']['key']}")
    
    # 列出变量
    result = skill.list_variables()
    if result["success"]:
        print(f"✓ 共有 {len(result['data'])} 个变量")
        for var in result["data"]:
            protected = "受保护" if var["protected"] else ""
            masked = "已掩码" if var["masked"] else ""
            flags = ", ".join(filter(None, [protected, masked]))
            print(f"  - {var['key']} ({flags})")


def example_10_generate_template():
    """示例10: 生成CI模板"""
    print("\n" + "=" * 60)
    print("示例10: 生成CI模板")
    print("=" * 60)
    
    skill = GitLabCISkill(token="token", project="project")
    
    for template_type in ["python", "nodejs", "java", "docker"]:
        result = skill.generate_ci_template(template_type)
        if result["success"]:
            print(f"✓ {template_type.upper()} 模板生成成功")
            # 显示前300字符
            content = result["data"]["content"][:300]
            print(content)
            print("-" * 40)


def main():
    """主函数 - 运行所有示例"""
    print("\n" + "=" * 60)
    print("GitLab CI Skill - 基础示例")
    print("=" * 60)
    print("\n注意: 部分示例需要有效的GitLab Token才能运行")
    print("      请设置 GITLAB_TOKEN 和 GITLAB_PROJECT 环境变量")
    print("=" * 60)
    
    examples = [
        example_1_basic_init,
        example_2_create_ci_config,
        example_3_update_ci_job,
        example_4_validate_config,
        example_5_list_runners,
        example_6_list_pipelines,
        example_7_trigger_pipeline,
        example_8_get_pipeline_details,
        example_9_manage_variables,
        example_10_generate_template,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n错误: {e}")
    
    print("\n" + "=" * 60)
    print("示例运行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
