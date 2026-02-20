#!/usr/bin/env python3
"""
Helm Skill 测试文件

运行测试: python test.py
"""

import unittest
import subprocess
import json
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from datetime import datetime

# 导入被测试的模块
sys.path.insert(0, os.path.dirname(__file__))
from main import HelmClient, ReleaseInfo, RepoInfo, ChartInfo


class TestHelmClient(unittest.TestCase):
    """HelmClient类测试"""
    
    def setUp(self):
        """测试准备"""
        self.helm = HelmClient(
            kubeconfig="/path/to/config",
            namespace="test-ns",
            helm_path="helm"
        )
    
    def test_build_cmd(self):
        """测试命令构建"""
        cmd = self.helm._build_cmd(["list"])
        
        self.assertIn("helm", cmd)
        self.assertIn("--kubeconfig", cmd)
        self.assertIn("/path/to/config", cmd)
        self.assertIn("list", cmd)
    
    @patch('main.subprocess.run')
    def test_run_command_success(self, mock_run):
        """测试命令执行成功"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='test output',
            stderr=''
        )
        
        returncode, stdout, stderr = self.helm._run_command(["list"])
        
        self.assertEqual(returncode, 0)
        self.assertEqual(stdout, 'test output')
        self.assertEqual(stderr, '')
    
    @patch('main.subprocess.run')
    def test_run_command_failure(self, mock_run):
        """测试命令执行失败"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='',
            stderr='error message'
        )
        
        returncode, stdout, stderr = self.helm._run_command(["invalid"])
        
        self.assertEqual(returncode, 1)
        self.assertEqual(stderr, 'error message')
    
    @patch('main.subprocess.run')
    def test_list_repos(self, mock_run):
        """测试列出仓库"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps([
                {"name": "bitnami", "url": "https://charts.bitnami.com/bitnami"},
                {"name": "stable", "url": "https://charts.helm.sh/stable"}
            ]),
            stderr=''
        )
        
        repos = self.helm.list_repos()
        
        self.assertEqual(len(repos), 2)
        self.assertEqual(repos[0].name, "bitnami")
        self.assertEqual(repos[1].name, "stable")
    
    @patch('main.subprocess.run')
    def test_list_repos_empty(self, mock_run):
        """测试列出空仓库"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='',
            stderr='Error: no repositories configured'
        )
        
        repos = self.helm.list_repos()
        
        self.assertEqual(len(repos), 0)
    
    @patch('main.subprocess.run')
    def test_add_repo(self, mock_run):
        """测试添加仓库"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='"bitnami" has been added',
            stderr=''
        )
        
        result = self.helm.add_repo("bitnami", "https://charts.bitnami.com/bitnami")
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_remove_repo(self, mock_run):
        """测试删除仓库"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='"bitnami" has been removed',
            stderr=''
        )
        
        result = self.helm.remove_repo("bitnami")
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_update_repos(self, mock_run):
        """测试更新仓库"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='Successfully got an update from the "bitnami" chart repository',
            stderr=''
        )
        
        result = self.helm.update_repos()
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_search_repo(self, mock_run):
        """测试搜索仓库"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps([
                {
                    "name": "bitnami/nginx",
                    "version": "13.2.0",
                    "app_version": "1.21.6",
                    "description": "NGINX Open Source"
                }
            ]),
            stderr=''
        )
        
        charts = self.helm.search_repo("nginx")
        
        self.assertEqual(len(charts), 1)
        self.assertEqual(charts[0].name, "bitnami/nginx")
    
    @patch('main.subprocess.run')
    def test_list_releases(self, mock_run):
        """测试列出Release"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps([
                {
                    "name": "my-nginx",
                    "namespace": "default",
                    "revision": "1",
                    "updated": "2024-01-01 10:00:00",
                    "status": "deployed",
                    "chart": "nginx-13.2.0",
                    "app_version": "1.21.6"
                }
            ]),
            stderr=''
        )
        
        releases = self.helm.list_releases()
        
        self.assertEqual(len(releases), 1)
        self.assertEqual(releases[0].name, "my-nginx")
        self.assertEqual(releases[0].status, "deployed")
    
    @patch('main.subprocess.run')
    def test_install(self, mock_run):
        """测试安装Chart"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='NAME: my-nginx\nSTATUS: deployed',
            stderr=''
        )
        
        result = self.helm.install("my-nginx", "bitnami/nginx")
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_upgrade(self, mock_run):
        """测试升级Release"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='Release "my-nginx" has been upgraded',
            stderr=''
        )
        
        result = self.helm.upgrade("my-nginx", "bitnami/nginx", install=True)
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_rollback(self, mock_run):
        """测试回滚"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='Rollback was a success!',
            stderr=''
        )
        
        result = self.helm.rollback("my-nginx", 1)
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_uninstall(self, mock_run):
        """测试卸载"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='release "my-nginx" uninstalled',
            stderr=''
        )
        
        result = self.helm.uninstall(["my-nginx"])
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_create_chart(self, mock_run):
        """测试创建Chart"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='Creating my-chart',
            stderr=''
        )
        
        result = self.helm.create_chart("my-chart")
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_package_chart(self, mock_run):
        """测试打包Chart"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='Successfully packaged chart',
            stderr=''
        )
        
        result = self.helm.package_chart("./my-chart", "./dist")
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_lint_chart(self, mock_run):
        """测试验证Chart"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='1 chart(s) linted, 0 chart(s) failed',
            stderr=''
        )
        
        result = self.helm.lint_chart("./my-chart")
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_template_chart(self, mock_run):
        """测试模板渲染"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='---\napiVersion: v1\nkind: Service',
            stderr=''
        )
        
        output = self.helm.template_chart("test", "./my-chart")
        
        self.assertIn("apiVersion", output)
    
    @patch('main.subprocess.run')
    def test_show_chart_info(self, mock_run):
        """测试显示Chart信息"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='apiVersion: v2\nname: my-chart',
            stderr=''
        )
        
        output = self.helm.show_chart_info("./my-chart", "chart")
        
        self.assertIn("apiVersion", output)
    
    @patch('main.subprocess.run')
    def test_dependency_update(self, mock_run):
        """测试更新依赖"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='Saving 1 charts',
            stderr=''
        )
        
        result = self.helm.dependency_update("./my-chart")
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_release_status(self, mock_run):
        """测试Release状态"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='NAME: my-release\nSTATUS: deployed',
            stderr=''
        )
        
        output = self.helm.release_status("my-release")
        
        self.assertIn("STATUS", output)
    
    @patch('main.subprocess.run')
    def test_release_history(self, mock_run):
        """测试Release历史"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='REVISION\tUPDATED\tSTATUS\n1\tJan 1\tdeployed',
            stderr=''
        )
        
        output = self.helm.release_history("my-release")
        
        self.assertIn("REVISION", output)


class TestDataClasses(unittest.TestCase):
    """数据类测试"""
    
    def test_release_info(self):
        """测试ReleaseInfo数据类"""
        release = ReleaseInfo(
            name="my-release",
            namespace="default",
            revision="1",
            updated="2024-01-01 10:00:00",
            status="deployed",
            chart="nginx-13.2.0",
            app_version="1.21.6"
        )
        
        self.assertEqual(release.name, "my-release")
        self.assertEqual(release.status, "deployed")
        self.assertEqual(release.revision, "1")
    
    def test_repo_info(self):
        """测试RepoInfo数据类"""
        repo = RepoInfo(
            name="bitnami",
            url="https://charts.bitnami.com/bitnami"
        )
        
        self.assertEqual(repo.name, "bitnami")
        self.assertEqual(repo.url, "https://charts.bitnami.com/bitnami")
    
    def test_chart_info(self):
        """测试ChartInfo数据类"""
        chart = ChartInfo(
            name="bitnami/nginx",
            version="13.2.0",
            app_version="1.21.6",
            description="NGINX Open Source"
        )
        
        self.assertEqual(chart.name, "bitnami/nginx")
        self.assertEqual(chart.version, "13.2.0")


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = HelmClient()
        self.assertEqual(client.namespace, "default")
        self.assertIsNone(client.kubeconfig)
        self.assertEqual(client.helm_path, "helm")
    
    def test_client_with_custom_config(self):
        """测试自定义配置的客户端"""
        client = HelmClient(
            kubeconfig="/custom/config",
            namespace="production",
            helm_path="/usr/local/bin/helm"
        )
        self.assertEqual(client.kubeconfig, "/custom/config")
        self.assertEqual(client.namespace, "production")
        self.assertEqual(client.helm_path, "/usr/local/bin/helm")
    
    def test_build_cmd_with_namespace(self):
        """测试带命名空间的命令构建"""
        client = HelmClient(namespace="test")
        cmd = client._build_cmd(["install", "my-app", "./chart"])
        
        self.assertIn("helm", cmd)
        self.assertIn("install", cmd)
        self.assertIn("my-app", cmd)


def run_command_test():
    """运行命令行测试"""
    print("=" * 60)
    print("Helm Skill 命令行测试")
    print("=" * 60)
    
    test_commands = [
        ("显示帮助", ["python", "main.py", "--help"]),
        ("Repo命令帮助", ["python", "main.py", "repo", "--help"]),
        ("Release命令帮助", ["python", "main.py", "release", "--help"]),
        ("Install命令帮助", ["python", "main.py", "install", "--help"]),
    ]
    
    for desc, cmd in test_commands:
        print(f"\n测试: {desc}")
        print("-" * 40)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8'
            )
            if result.returncode == 0:
                print(f"✓ 通过")
                print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
            else:
                print(f"✗ 失败")
                print(result.stderr[:500])
        except Exception as e:
            print(f"✗ 错误: {e}")


def main():
    """主测试函数"""
    print("Helm Skill 测试套件")
    print("=" * 60)
    
    # 运行单元测试
    print("\n[1/2] 运行单元测试...")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestHelmClient))
    suite.addTests(loader.loadTestsFromTestCase(TestDataClasses))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 运行命令行测试
    print("\n[2/2] 运行命令行测试...")
    run_command_test()
    
    # 输出总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"单元测试: 运行={result.testsRun}, 失败={len(result.failures)}, 错误={len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ 所有测试通过!")
        return 0
    else:
        print("\n✗ 部分测试失败")
        return 1


if __name__ == '__main__':
    exit(main())
