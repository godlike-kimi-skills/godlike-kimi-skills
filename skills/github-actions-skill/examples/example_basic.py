#!/usr/bin/env python3
"""
GitHub Actions Skill - 基础使用示例

展示如何：
1. 初始化Skill
2. 创建和管理工作流
3. 配置触发器
4. 管理Secrets
5. 监控工作流运行
"""

import os
from main import GitHubActionsSkill


def example_1_basic_init():
    """示例1: 基础初始化"""
    print("=" * 60)
    print("示例1: 基础初始化")
    print("=" * 60)
    
    # 方式1: 直接传入参数
    skill = GitHubActionsSkill(
        token="your-github-token",
        repo="owner/repository"
    )
    print("✓ 使用参数初始化成功")
    
    # 方式2: 使用环境变量
    # 设置环境变量: export GITHUB_TOKEN=xxx
    #              export GITHUB_REPO=owner/repo
    # skill = GitHubActionsSkill()
    # print("✓ 使用环境变量初始化成功")


def example_2_create_workflow():
    """示例2: 创建工作流"""
    print("\n" + "=" * 60)
    print("示例2: 创建工作流")
    print("=" * 60)
    
    skill = GitHubActionsSkill(
        token=os.getenv("GITHUB_TOKEN", "your-token"),
        repo=os.getenv("GITHUB_REPO", "owner/repo")
    )
    
    # 创建简单CI工作流
    result = skill.create_workflow(
        name="simple-ci",
        triggers=["push", "pull_request"],
        jobs=[{
            "name": "build",
            "runs_on": "ubuntu-latest",
            "steps": [
                {"uses": "actions/checkout@v4"},
                {"run": "echo 'Hello World'"}
            ]
        }]
    )
    
    if result["success"]:
        print(f"✓ 工作流创建成功")
        print(f"  路径: {result['data']['path']}")
        print(f"  Commit: {result['data']['commit_sha']}")
    else:
        print(f"✗ 创建失败: {result['error']}")


def example_3_create_from_template():
    """示例3: 使用模板创建工作流"""
    print("\n" + "=" * 60)
    print("示例3: 使用模板创建工作流")
    print("=" * 60)
    
    skill = GitHubActionsSkill(token="your-token", repo="owner/repo")
    
    # 生成Python CI模板
    template = skill.generate_template("ci", "python")
    if template["success"]:
        print("✓ Python CI模板生成成功")
        print("-" * 40)
        print(template["data"]["content"][:500])
        print("-" * 40)


def example_4_manage_secrets():
    """示例4: 管理Secrets"""
    print("\n" + "=" * 60)
    print("示例4: 管理Secrets")
    print("=" * 60)
    
    skill = GitHubActionsSkill(
        token=os.getenv("GITHUB_TOKEN", "your-token"),
        repo=os.getenv("GITHUB_REPO", "owner/repo")
    )
    
    # 设置Secret
    result = skill.set_secret("DEPLOY_TOKEN", "super-secret-value")
    if result["success"]:
        print("✓ Secret设置成功")
    
    # 列出所有Secrets
    result = skill.list_secrets()
    if result["success"]:
        print(f"✓ 当前共有 {len(result['data'])} 个Secrets")
        for secret in result["data"]:
            print(f"  - {secret['name']}")


def example_5_monitor_runs():
    """示例5: 监控工作流运行"""
    print("\n" + "=" * 60)
    print("示例5: 监控工作流运行")
    print("=" * 60)
    
    skill = GitHubActionsSkill(
        token=os.getenv("GITHUB_TOKEN", "your-token"),
        repo=os.getenv("GITHUB_REPO", "owner/repo")
    )
    
    # 获取最近的工作流运行
    result = skill.get_workflow_runs(limit=5)
    if result["success"]:
        print(f"✓ 获取到 {len(result['data'])} 条运行记录")
        for run in result["data"]:
            status_icon = "✓" if run["conclusion"] == "success" else "○"
            print(f"  {status_icon} #{run['run_number']} {run['name']}: {run['status']}")


def example_6_list_workflows():
    """示例6: 列出所有工作流"""
    print("\n" + "=" * 60)
    print("示例6: 列出所有工作流")
    print("=" * 60)
    
    skill = GitHubActionsSkill(
        token=os.getenv("GITHUB_TOKEN", "your-token"),
        repo=os.getenv("GITHUB_REPO", "owner/repo")
    )
    
    result = skill.list_workflows()
    if result["success"]:
        print(f"✓ 共有 {len(result['data'])} 个工作流")
        for wf in result["data"]:
            print(f"  - {wf['name']} ({wf['state']})")
            print(f"    路径: {wf['path']}")


def example_7_configure_triggers():
    """示例7: 配置触发器"""
    print("\n" + "=" * 60)
    print("示例7: 配置触发器")
    print("=" * 60)
    
    skill = GitHubActionsSkill(token="your-token", repo="owner/repo")
    
    # 配置复杂触发器
    triggers = {
        "push": {"branches": ["main", "develop"]},
        "pull_request": {"branches": ["main"]},
        "schedule": [{"cron": "0 2 * * *"}],  # 每天凌晨2点
        "workflow_dispatch": {
            "inputs": {
                "environment": {
                    "description": "部署环境",
                    "required": True,
                    "default": "staging"
                }
            }
        }
    }
    
    result = skill.configure_triggers("my-workflow", triggers)
    if result["success"]:
        print("✓ 触发器配置成功")
        print(f"  工作流: {result['data']['workflow']}")


def example_8_runner_management():
    """示例8: Runner管理"""
    print("\n" + "=" * 60)
    print("示例8: Runner管理")
    print("=" * 60)
    
    skill = GitHubActionsSkill(
        token=os.getenv("GITHUB_TOKEN", "your-token"),
        repo=os.getenv("GITHUB_REPO", "owner/repo")
    )
    
    # 列出Self-hosted runners
    result = skill.list_runners()
    if result["success"]:
        print(f"✓ 共有 {len(result['data'])} 个Self-hosted Runner")
        for runner in result["data"]:
            status = "忙碌" if runner["busy"] else "空闲"
            print(f"  - {runner['name']} ({runner['os']}) - {status}")


def main():
    """主函数 - 运行所有示例"""
    print("\n" + "=" * 60)
    print("GitHub Actions Skill - 基础示例")
    print("=" * 60)
    print("\n注意: 部分示例需要有效的GitHub Token才能运行")
    print("      请设置 GITHUB_TOKEN 环境变量")
    print("=" * 60)
    
    # 运行示例
    try:
        example_1_basic_init()
        example_2_create_workflow()
        example_3_create_from_template()
        example_4_manage_secrets()
        example_5_monitor_runs()
        example_6_list_workflows()
        example_7_configure_triggers()
        example_8_runner_management()
    except Exception as e:
        print(f"\n错误: {e}")
    
    print("\n" + "=" * 60)
    print("示例运行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
