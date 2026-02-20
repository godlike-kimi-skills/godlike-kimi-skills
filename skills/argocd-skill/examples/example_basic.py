#!/usr/bin/env python3
"""
ArgoCD Skill - 基础使用示例

展示如何：
1. 初始化Skill
2. 创建和管理Applications
3. 执行Sync操作
4. 管理仓库
5. 查看资源和历史
"""

import os
from main import ArgoCDSkill


def example_1_basic_init():
    """示例1: 基础初始化"""
    print("=" * 60)
    print("示例1: 基础初始化")
    print("=" * 60)
    
    # 方式1: 使用用户名密码
    skill = ArgoCDSkill(
        server="https://argocd.example.com",
        username="admin",
        password="password",
        insecure=True  # 测试环境跳过TLS验证
    )
    print("✓ 使用用户名密码初始化成功")
    
    # 方式2: 使用Token
    # skill = ArgoCDSkill(
    #     server="https://argocd.example.com",
    #     token="your-api-token"
    # )
    # print("✓ 使用Token初始化成功")
    
    # 方式3: 使用环境变量
    # export ARGOCD_SERVER=https://argocd.example.com
    # export ARGOCD_TOKEN=your-api-token
    # skill = ArgoCDSkill()
    # print("✓ 使用环境变量初始化成功")


def example_2_server_info():
    """示例2: 获取服务器信息"""
    print("\n" + "=" * 60)
    print("示例2: 获取服务器信息")
    print("=" * 60)
    
    skill = ArgoCDSkill(
        server=os.getenv("ARGOCD_SERVER", "https://argocd.example.com"),
        token=os.getenv("ARGOCD_TOKEN", "token"),
        insecure=True
    )
    
    result = skill.get_server_info()
    if result["success"]:
        print(f"✓ ArgoCD服务器信息:")
        print(f"  URL: {result['data']['url']}")
        print(f"  DEX启用: {result['data']['dexEnabled']}")


def example_3_create_app():
    """示例3: 创建Application"""
    print("\n" + "=" * 60)
    print("示例3: 创建Application")
    print("=" * 60)
    
    skill = ArgoCDSkill(
        server=os.getenv("ARGOCD_SERVER", "https://argocd.example.com"),
        token=os.getenv("ARGOCD_TOKEN", "token"),
        insecure=True
    )
    
    # 创建Git应用
    result = skill.create_app(
        name="example-app",
        repo_url="https://github.com/example-org/example-repo.git",
        path="kubernetes/manifests",
        dest_namespace="example",
        sync_policy={
            "automated": {
                "prune": True,
                "selfHeal": True
            },
            "syncOptions": ["CreateNamespace=true"]
        }
    )
    
    if result["success"]:
        print(f"✓ Application创建成功")
        print(f"  名称: {result['data']['name']}")
        print(f"  仓库: {result['data']['repoURL']}")
        print(f"  目标: {result['data']['destination']}")
    else:
        print(f"✗ 创建失败: {result['error']}")


def example_4_list_apps():
    """示例4: 列出Applications"""
    print("\n" + "=" * 60)
    print("示例4: 列出Applications")
    print("=" * 60)
    
    skill = ArgoCDSkill(
        server=os.getenv("ARGOCD_SERVER", "https://argocd.example.com"),
        token=os.getenv("ARGOCD_TOKEN", "token"),
        insecure=True
    )
    
    result = skill.list_apps()
    if result["success"]:
        print(f"✓ 共有 {len(result['data'])} 个Application")
        for app in result["data"]:
            sync_icon = "✓" if app["syncStatus"] == "Synced" else "○"
            health_icon = "✓" if app["healthStatus"] == "Healthy" else "✗"
            print(f"  {sync_icon} {app['name']} ({app['project']})")
            print(f"    同步: {app['syncStatus']}, 健康: {app['healthStatus']}")


def example_5_get_app_details():
    """示例5: 获取Application详情"""
    print("\n" + "=" * 60)
    print("示例5: 获取Application详情")
    print("=" * 60)
    
    skill = ArgoCDSkill(
        server=os.getenv("ARGOCD_SERVER", "https://argocd.example.com"),
        token=os.getenv("ARGOCD_TOKEN", "token"),
        insecure=True
    )
    
    result = skill.get_app("example-app")
    if result["success"]:
        print(f"✓ Application详情:")
        print(f"  名称: {result['data']['name']}")
        print(f"  命名空间: {result['data']['namespace']}")
        print(f"  项目: {result['data']['project']}")
        print(f"  同步状态: {result['data']['syncStatus']}")
        print(f"  健康状态: {result['data']['healthStatus']}")
        print(f"  资源数量: {len(result['data']['resources'])}")


def example_6_sync_app():
    """示例6: 同步Application"""
    print("\n" + "=" * 60)
    print("示例6: 同步Application")
    print("=" * 60)
    
    skill = ArgoCDSkill(
        server=os.getenv("ARGOCD_SERVER", "https://argocd.example.com"),
        token=os.getenv("ARGOCD_TOKEN", "token"),
        insecure=True
    )
    
    # 普通同步
    result = skill.sync_app("example-app")
    if result["success"]:
        print("✓ 同步请求已发送")
    
    # 强制同步（带prune）
    result = skill.sync_app("example-app", prune=True, force=True)
    if result["success"]:
        print("✓ 强制同步请求已发送")


def example_7_app_resources():
    """示例7: 查看资源树"""
    print("\n" + "=" * 60)
    print("示例7: 查看资源树")
    print("=" * 60)
    
    skill = ArgoCDSkill(
        server=os.getenv("ARGOCD_SERVER", "https://argocd.example.com"),
        token=os.getenv("ARGOCD_TOKEN", "token"),
        insecure=True
    )
    
    result = skill.get_app_resources("example-app")
    if result["success"]:
        print(f"✓ 资源列表:")
        for resource in result["data"]:
            status = "✓" if resource["status"] == "Synced" else "○"
            print(f"  {status} {resource['kind']}/{resource['name']} ({resource['namespace']})")


def example_8_app_history():
    """示例8: 查看同步历史"""
    print("\n" + "=" * 60)
    print("示例8: 查看同步历史")
    print("=" * 60)
    
    skill = ArgoCDSkill(
        server=os.getenv("ARGOCD_SERVER", "https://argocd.example.com"),
        token=os.getenv("ARGOCD_TOKEN", "token"),
        insecure=True
    )
    
    result = skill.get_app_history("example-app", limit=5)
    if result["success"]:
        print(f"✓ 同步历史:")
        for item in result["data"]:
            print(f"  #{item['id']} - {item['revision'][:8]}")
            print(f"    部署时间: {item['deployedAt']}")


def example_9_rollback():
    """示例9: 回滚Application"""
    print("\n" + "=" * 60)
    print("示例9: 回滚Application")
    print("=" * 60)
    
    skill = ArgoCDSkill(
        server=os.getenv("ARGOCD_SERVER", "https://argocd.example.com"),
        token=os.getenv("ARGOCD_TOKEN", "token"),
        insecure=True
    )
    
    # 回滚到历史版本#5
    result = skill.rollback_app("example-app", 5)
    if result["success"]:
        print(f"✓ 已回滚到版本 #{result['data']['history_id']}")


def example_10_manage_repos():
    """示例10: 管理仓库"""
    print("\n" + "=" * 60)
    print("示例10: 管理仓库")
    print("=" * 60)
    
    skill = ArgoCDSkill(
        server=os.getenv("ARGOCD_SERVER", "https://argocd.example.com"),
        token=os.getenv("ARGOCD_TOKEN", "token"),
        insecure=True
    )
    
    # 添加Git仓库
    result = skill.add_repo(
        url="https://github.com/example-org/new-repo.git",
        username="git",
        password="github-token"
    )
    if result["success"]:
        print(f"✓ 仓库添加成功")
    
    # 列出仓库
    result = skill.list_repos()
    if result["success"]:
        print(f"✓ 共有 {len(result['data'])} 个仓库")
        for repo in result["data"]:
            status_icon = "✓" if repo["connectionState"] == "Successful" else "✗"
            print(f"  {status_icon} {repo['repo']} ({repo['type']})")


def example_11_generate_templates():
    """示例11: 生成Application模板"""
    print("\n" + "=" * 60)
    print("示例11: 生成Application模板")
    print("=" * 60)
    
    skill = ArgoCDSkill(
        server="https://argocd.example.com",
        token="token"
    )
    
    # 生成Git应用模板
    result = skill.generate_app_template(
        app_type="git",
        name="my-app",
        repo_url="https://github.com/org/repo.git",
        path="manifests"
    )
    if result["success"]:
        print("✓ Git应用模板:")
        print(result["data"]["template"][:500])
        print("...")
    
    # 生成Helm应用模板
    result = skill.generate_app_template(
        app_type="helm",
        name="my-helm-app",
        repo_url="https://charts.helm.sh/stable",
        chart="nginx"
    )
    if result["success"]:
        print("\n✓ Helm应用模板:")
        print(result["data"]["template"][:500])
        print("...")


def example_12_delete_app():
    """示例12: 删除Application"""
    print("\n" + "=" * 60)
    print("示例12: 删除Application")
    print("=" * 60)
    
    skill = ArgoCDSkill(
        server=os.getenv("ARGOCD_SERVER", "https://argocd.example.com"),
        token=os.getenv("ARGOCD_TOKEN", "token"),
        insecure=True
    )
    
    result = skill.delete_app("example-app", cascade=True)
    if result["success"]:
        print(f"✓ Application已删除: {result['data']['deleted']}")
    else:
        print(f"✗ 删除失败: {result['error']}")


def main():
    """主函数 - 运行所有示例"""
    print("\n" + "=" * 60)
    print("ArgoCD Skill - 基础示例")
    print("=" * 60)
    print("\n注意: 部分示例需要有效的ArgoCD服务器才能运行")
    print("      请设置 ARGOCD_SERVER 和 ARGOCD_TOKEN 环境变量")
    print("=" * 60)
    
    examples = [
        example_1_basic_init,
        example_2_server_info,
        example_3_create_app,
        example_4_list_apps,
        example_5_get_app_details,
        example_6_sync_app,
        example_7_app_resources,
        example_8_app_history,
        example_9_rollback,
        example_10_manage_repos,
        example_11_generate_templates,
        example_12_delete_app,
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
