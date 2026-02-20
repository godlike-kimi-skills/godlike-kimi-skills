#!/usr/bin/env python3
"""
Docker Skill 测试文件

运行测试: python test.py
"""

import unittest
import subprocess
import json
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# 导入被测试的模块
import sys
sys.path.insert(0, os.path.dirname(__file__))
from main import DockerClient, ComposeManager, ContainerInfo, ImageInfo


class TestDockerClient(unittest.TestCase):
    """DockerClient类测试"""
    
    def setUp(self):
        """测试准备"""
        self.docker = DockerClient()
    
    @patch('main.subprocess.run')
    def test_run_command_success(self, mock_run):
        """测试命令执行成功"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='test output',
            stderr=''
        )
        
        returncode, stdout, stderr = self.docker._run_command(['ps'])
        
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
        
        returncode, stdout, stderr = self.docker._run_command(['invalid'])
        
        self.assertEqual(returncode, 1)
        self.assertEqual(stderr, 'error message')
    
    @patch('main.subprocess.run')
    def test_list_containers(self, mock_run):
        """测试列出容器"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                'ID': 'abc123def456',
                'Names': 'test-container',
                'Image': 'nginx',
                'Status': 'Up 2 hours',
                'Ports': '80/tcp',
                'CreatedAt': '2024-01-01',
                'Command': '"nginx"'
            }),
            stderr=''
        )
        
        containers = self.docker.list_containers()
        
        self.assertEqual(len(containers), 1)
        self.assertEqual(containers[0].name, 'test-container')
        self.assertEqual(containers[0].image, 'nginx')
    
    @patch('main.subprocess.run')
    def test_start_container(self, mock_run):
        """测试启动容器"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='test-container',
            stderr=''
        )
        
        result = self.docker.start_container('test-container')
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('main.subprocess.run')
    def test_stop_container(self, mock_run):
        """测试停止容器"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='test-container',
            stderr=''
        )
        
        result = self.docker.stop_container('test-container')
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_get_container_logs(self, mock_run):
        """测试获取容器日志"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='log line 1\nlog line 2',
            stderr=''
        )
        
        logs = self.docker.get_container_logs('test-container', tail=10)
        
        self.assertIn('log line 1', logs)
        self.assertIn('log line 2', logs)
    
    @patch('main.subprocess.run')
    def test_list_images(self, mock_run):
        """测试列出镜像"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                'ID': 'img123',
                'Repository': 'nginx',
                'Tag': 'latest',
                'Size': '150MB',
                'CreatedAt': '2024-01-01'
            }),
            stderr=''
        )
        
        images = self.docker.list_images()
        
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0].repository, 'nginx')
    
    @patch('main.subprocess.run')
    def test_pull_image(self, mock_run):
        """测试拉取镜像"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='',
            stderr=''
        )
        
        result = self.docker.pull_image('nginx:latest')
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_build_image(self, mock_run):
        """测试构建镜像"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='',
            stderr=''
        )
        
        result = self.docker.build_image('.', tag='myapp:1.0')
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_remove_image(self, mock_run):
        """测试删除镜像"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='',
            stderr=''
        )
        
        result = self.docker.remove_image('nginx:latest')
        
        self.assertTrue(result)


class TestComposeManager(unittest.TestCase):
    """ComposeManager类测试"""
    
    def setUp(self):
        """测试准备"""
        self.compose = ComposeManager(
            compose_file='docker-compose.yml',
            project_name='test-project'
        )
    
    def test_build_cmd(self):
        """测试命令构建"""
        cmd = self.compose._build_cmd('up', '-d')
        
        self.assertIn('docker', cmd)
        self.assertIn('compose', cmd)
        self.assertIn('-f', cmd)
        self.assertIn('docker-compose.yml', cmd)
        self.assertIn('-p', cmd)
        self.assertIn('test-project', cmd)
        self.assertIn('up', cmd)
        self.assertIn('-d', cmd)
    
    @patch('main.subprocess.run')
    def test_up(self, mock_run):
        """测试启动服务"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='',
            stderr=''
        )
        
        result = self.compose.up(detach=True)
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_down(self, mock_run):
        """测试停止服务"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='',
            stderr=''
        )
        
        result = self.compose.down(volumes=True)
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_restart(self, mock_run):
        """测试重启服务"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='',
            stderr=''
        )
        
        result = self.compose.restart(['web', 'db'])
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_logs(self, mock_run):
        """测试查看日志"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='log output',
            stderr=''
        )
        
        logs = self.compose.logs(tail=50)
        
        self.assertEqual(logs, 'log output')
    
    @patch('main.subprocess.run')
    def test_ps(self, mock_run):
        """测试查看服务状态"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[{"Name": "web", "State": "running"}]',
            stderr=''
        )
        
        services = self.compose.ps()
        
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0]['Name'], 'web')


class TestDataClasses(unittest.TestCase):
    """数据类测试"""
    
    def test_container_info(self):
        """测试ContainerInfo数据类"""
        info = ContainerInfo(
            id='abc123',
            name='test-container',
            image='nginx',
            status='Up 2 hours',
            ports='80/tcp',
            created='2024-01-01',
            command='nginx'
        )
        
        self.assertEqual(info.id, 'abc123')
        self.assertEqual(info.name, 'test-container')
        self.assertEqual(info.image, 'nginx')
    
    def test_image_info(self):
        """测试ImageInfo数据类"""
        info = ImageInfo(
            id='img123',
            repository='nginx',
            tag='latest',
            size='150MB',
            created='2024-01-01'
        )
        
        self.assertEqual(info.id, 'img123')
        self.assertEqual(info.repository, 'nginx')
        self.assertEqual(info.tag, 'latest')


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试准备"""
        self.test_dir = tempfile.mkdtemp()
        self.compose_file = os.path.join(self.test_dir, 'docker-compose.yml')
        
        # 创建测试用的docker-compose.yml
        compose_content = """
version: '3.8'
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
  
  db:
    image: redis:alpine
"""
        with open(self.compose_file, 'w') as f:
            f.write(compose_content)
    
    def tearDown(self):
        """测试清理"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_compose_file_parsing(self):
        """测试Compose文件解析"""
        with open(self.compose_file, 'r') as f:
            content = f.read()
        
        self.assertIn('version:', content)
        self.assertIn('services:', content)
        self.assertIn('web:', content)
        self.assertIn('db:', content)


def run_command_test():
    """运行命令行测试"""
    print("=" * 60)
    print("Docker Skill 命令行测试")
    print("=" * 60)
    
    test_commands = [
        ("显示帮助", ["python", "main.py", "--help"]),
        ("容器命令帮助", ["python", "main.py", "container", "--help"]),
        ("镜像命令帮助", ["python", "main.py", "image", "--help"]),
        ("Compose命令帮助", ["python", "main.py", "compose", "--help"]),
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
                print(result.stderr)
        except Exception as e:
            print(f"✗ 错误: {e}")


def main():
    """主测试函数"""
    print("Docker Skill 测试套件")
    print("=" * 60)
    
    # 运行单元测试
    print("\n[1/2] 运行单元测试...")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestDockerClient))
    suite.addTests(loader.loadTestsFromTestCase(TestComposeManager))
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
