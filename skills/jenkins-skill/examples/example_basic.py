#!/usr/bin/env python3
"""
Jenkins Skill - 基础使用示例

展示如何：
1. 初始化Skill
2. 创建和管理Job
3. 触发和监控Build
4. 获取Build日志
5. 管理节点
"""

import os
import time
from main import JenkinsSkill


def example_1_basic_init():
    """示例1: 基础初始化"""
    print("=" * 60)
    print("示例1: 基础初始化")
    print("=" * 60)
    
    # 方式1: 直接传入参数
    skill = JenkinsSkill(
        url="http://jenkins.example.com",
        username="admin",
        token="api-token"
    )
    print("✓ 使用参数初始化成功")
    
    # 方式2: 使用环境变量
    # export JENKINS_URL=http://jenkins.example.com
    # export JENKINS_USER=admin
    # export JENKINS_TOKEN=api-token
    # skill = JenkinsSkill()
    # print("✓ 使用环境变量初始化成功")


def example_2_create_job():
    """示例2: 创建Job"""
    print("\n" + "=" * 60)
    print("示例2: 创建Job")
    print("=" * 60)
    
    skill = JenkinsSkill(
        url=os.getenv("JENKINS_URL", "http://jenkins.example.com"),
        username=os.getenv("JENKINS_USER", "admin"),
        token=os.getenv("JENKINS_TOKEN", "token")
    )
    
    # 创建Pipeline Job
    pipeline_script = """
pipeline {
    agent any
    stages {
        stage('Hello') {
            steps {
                echo 'Hello from Jenkins Skill!'
            }
        }
    }
}
"""
    
    result = skill.create_job(
        name="example-pipeline",
        job_type="pipeline",
        config={
            "description": "示例Pipeline Job",
            "script": pipeline_script
        }
    )
    
    if result["success"]:
        print(f"✓ Job创建成功")
        print(f"  名称: {result['data']['name']}")
        print(f"  URL: {result['data']['url']}")
    else:
        print(f"✗ 创建失败: {result['error']}")


def example_3_list_jobs():
    """示例3: 列出所有Jobs"""
    print("\n" + "=" * 60)
    print("示例3: 列出所有Jobs")
    print("=" * 60)
    
    skill = JenkinsSkill(
        url=os.getenv("JENKINS_URL", "http://jenkins.example.com"),
        username=os.getenv("JENKINS_USER", "admin"),
        token=os.getenv("JENKINS_TOKEN", "token")
    )
    
    result = skill.list_jobs()
    if result["success"]:
        print(f"✓ 共有 {len(result['data'])} 个Job")
        for job in result["data"]:
            status_icon = "●" if job["color"] in ["blue", "blue_anime"] else "○"
            print(f"  {status_icon} {job['name']}")


def example_4_trigger_build():
    """示例4: 触发Build"""
    print("\n" + "=" * 60)
    print("示例4: 触发Build")
    print("=" * 60)
    
    skill = JenkinsSkill(
        url=os.getenv("JENKINS_URL", "http://jenkins.example.com"),
        username=os.getenv("JENKINS_USER", "admin"),
        token=os.getenv("JENKINS_TOKEN", "token")
    )
    
    # 触发Build
    result = skill.trigger_build("example-pipeline")
    if result["success"]:
        print(f"✓ Build已触发")
        print(f"  Queue Item ID: {result['data']['queue_item']}")


def example_5_monitor_build():
    """示例5: 监控Build状态"""
    print("\n" + "=" * 60)
    print("示例5: 监控Build状态")
    print("=" * 60)
    
    skill = JenkinsSkill(
        url=os.getenv("JENKINS_URL", "http://jenkins.example.com"),
        username=os.getenv("JENKINS_USER", "admin"),
        token=os.getenv("JENKINS_TOKEN", "token")
    )
    
    # 获取最近的Builds
    result = skill.list_builds("example-pipeline", limit=5)
    if result["success"]:
        print(f"✓ 最近Build记录:")
        for build in result["data"]:
            status = build["result"] or "RUNNING"
            icon = "✓" if status == "SUCCESS" else "✗" if status == "FAILURE" else "○"
            print(f"  {icon} Build #{build['number']}: {status}")


def example_6_get_build_logs():
    """示例6: 获取Build日志"""
    print("\n" + "=" * 60)
    print("示例6: 获取Build日志")
    print("=" * 60)
    
    skill = JenkinsSkill(
        url=os.getenv("JENKINS_URL", "http://jenkins.example.com"),
        username=os.getenv("JENKINS_USER", "admin"),
        token=os.getenv("JENKINS_TOKEN", "token")
    )
    
    # 获取最新Build的日志
    builds = skill.list_builds("example-pipeline", limit=1)
    if builds["success"] and builds["data"]:
        build_number = builds["data"][0]["number"]
        result = skill.get_build_logs("example-pipeline", build_number)
        if result["success"]:
            print(f"✓ Build #{build_number} 日志:")
            print("-" * 40)
            # 只显示前500字符
            logs = result["data"]["logs"][:500]
            print(logs)
            print("-" * 40)


def example_7_list_nodes():
    """示例7: 列出Jenkins节点"""
    print("\n" + "=" * 60)
    print("示例7: 列出Jenkins节点")
    print("=" * 60)
    
    skill = JenkinsSkill(
        url=os.getenv("JENKINS_URL", "http://jenkins.example.com"),
        username=os.getenv("JENKINS_USER", "admin"),
        token=os.getenv("JENKINS_TOKEN", "token")
    )
    
    result = skill.list_nodes()
    if result["success"]:
        print(f"✓ 共有 {len(result['data'])} 个节点")
        for node in result["data"]:
            status = "离线" if node["offline"] else "在线"
            labels = ", ".join(node.get("labels", [])[:3])
            print(f"  - {node['name']} ({status}) - {labels}")


def example_8_get_queue():
    """示例8: 查看构建队列"""
    print("\n" + "=" * 60)
    print("示例8: 查看构建队列")
    print("=" * 60)
    
    skill = JenkinsSkill(
        url=os.getenv("JENKINS_URL", "http://jenkins.example.com"),
        username=os.getenv("JENKINS_USER", "admin"),
        token=os.getenv("JENKINS_TOKEN", "token")
    )
    
    result = skill.get_queue()
    if result["success"]:
        if result["data"]:
            print(f"✓ 队列中有 {len(result['data'])} 个任务")
            for item in result["data"]:
                print(f"  - {item['task']}: {item['why']}")
        else:
            print("✓ 队列为空")


def example_9_generate_template():
    """示例9: 生成Pipeline模板"""
    print("\n" + "=" * 60)
    print("示例9: 生成Pipeline模板")
    print("=" * 60)
    
    skill = JenkinsSkill(
        url="http://jenkins.example.com",
        username="admin",
        token="token"
    )
    
    # 生成Python CI模板
    result = skill.generate_pipeline_template("ci", "python")
    if result["success"]:
        print("✓ Python CI Pipeline模板:")
        print("-" * 40)
        print(result["data"]["script"][:500])
        print("-" * 40)


def example_10_delete_job():
    """示例10: 删除Job"""
    print("\n" + "=" * 60)
    print("示例10: 删除Job")
    print("=" * 60)
    
    skill = JenkinsSkill(
        url=os.getenv("JENKINS_URL", "http://jenkins.example.com"),
        username=os.getenv("JENKINS_USER", "admin"),
        token=os.getenv("JENKINS_TOKEN", "token")
    )
    
    result = skill.delete_job("example-pipeline")
    if result["success"]:
        print(f"✓ Job已删除: {result['data']['deleted']}")
    else:
        print(f"✗ 删除失败: {result['error']}")


def main():
    """主函数 - 运行所有示例"""
    print("\n" + "=" * 60)
    print("Jenkins Skill - 基础示例")
    print("=" * 60)
    print("\n注意: 部分示例需要有效的Jenkins服务器才能运行")
    print("      请设置 JENKINS_URL, JENKINS_USER, JENKINS_TOKEN 环境变量")
    print("=" * 60)
    
    examples = [
        example_1_basic_init,
        example_2_create_job,
        example_3_list_jobs,
        example_4_trigger_build,
        example_5_monitor_build,
        example_6_get_build_logs,
        example_7_list_nodes,
        example_8_get_queue,
        example_9_generate_template,
        example_10_delete_job,
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
