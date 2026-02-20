#!/usr/bin/env python3
"""
K8s Troubleshoot Skill 测试文件

运行测试: python test.py
"""

import unittest
import subprocess
import json
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime

# 导入被测试的模块
sys.path.insert(0, os.path.dirname(__file__))
from main import TroubleshootClient, PodDiagnostic, ResourceUsage


class TestTroubleshootClient(unittest.TestCase):
    """TroubleshootClient类测试"""
    
    def setUp(self):
        """测试准备"""
        self.client = TroubleshootClient(
            kubeconfig="/path/to/config",
            context="test-context",
            namespace="test-ns"
        )
    
    def test_build_cmd(self):
        """测试命令构建"""
        cmd = self.client._build_cmd(["get", "pods"])
        
        self.assertIn("kubectl", cmd)
        self.assertIn("--kubeconfig", cmd)
        self.assertIn("/path/to/config", cmd)
        self.assertIn("--context", cmd)
        self.assertIn("test-context", cmd)
        self.assertIn("get", cmd)
        self.assertIn("pods", cmd)
    
    @patch('main.subprocess.run')
    def test_run_command_success(self, mock_run):
        """测试命令执行成功"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='test output',
            stderr=''
        )
        
        returncode, stdout, stderr = self.client._run_command(["get", "pods"])
        
        self.assertEqual(returncode, 0)
        self.assertEqual(stdout, 'test output')
    
    @patch('main.subprocess.run')
    def test_run_command_failure(self, mock_run):
        """测试命令执行失败"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='',
            stderr='error message'
        )
        
        returncode, stdout, stderr = self.client._run_command(["invalid"])
        
        self.assertEqual(returncode, 1)
        self.assertEqual(stderr, 'error message')
    
    @patch('main.subprocess.run')
    def test_diagnose_pod_running(self, mock_run):
        """测试诊断运行中的Pod"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "metadata": {"name": "test-pod", "namespace": "default"},
                "status": {
                    "phase": "Running",
                    "conditions": [{"status": "True"}],
                    "containerStatuses": [{"ready": True, "restartCount": 0}]
                },
                "spec": {"containers": [{"name": "app", "resources": {}}]}
            }),
            stderr=''
        )
        
        diagnostic = self.client.diagnose_pod("test-pod")
        
        self.assertEqual(diagnostic.name, "test-pod")
        self.assertEqual(diagnostic.phase, "Running")
        self.assertEqual(diagnostic.restarts, 0)
    
    @patch('main.subprocess.run')
    def test_diagnose_pod_pending(self, mock_run):
        """测试诊断Pending状态的Pod"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "metadata": {"name": "pending-pod", "namespace": "default"},
                "status": {
                    "phase": "Pending",
                    "conditions": [],
                    "containerStatuses": []
                },
                "spec": {"containers": []}
            }),
            stderr=''
        )
        
        diagnostic = self.client.diagnose_pod("pending-pod")
        
        self.assertEqual(diagnostic.phase, "Pending")
        self.assertTrue(any("Pending" in issue for issue in diagnostic.issues))
    
    @patch('main.subprocess.run')
    def test_diagnose_pod_crashloop(self, mock_run):
        """测试诊断CrashLoopBackOff的Pod"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "metadata": {"name": "crash-pod", "namespace": "default"},
                "status": {
                    "phase": "Failed",
                    "conditions": [],
                    "containerStatuses": [{
                        "name": "app",
                        "ready": False,
                        "restartCount": 10,
                        "state": {
                            "waiting": {
                                "reason": "CrashLoopBackOff",
                                "message": "back-off 5m0s restarting failed container"
                            }
                        }
                    }]
                },
                "spec": {"containers": [{"name": "app"}]}
            }),
            stderr=''
        )
        
        diagnostic = self.client.diagnose_pod("crash-pod")
        
        self.assertEqual(diagnostic.restarts, 10)
        self.assertTrue(any("CrashLoopBackOff" in issue for issue in diagnostic.issues))
    
    @patch('main.subprocess.run')
    def test_get_pod_events(self, mock_run):
        """测试获取Pod事件"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "items": [
                    {
                        "lastTimestamp": "2024-01-01T10:00:00Z",
                        "type": "Warning",
                        "reason": "FailedScheduling",
                        "message": "0/3 nodes are available"
                    },
                    {
                        "lastTimestamp": "2024-01-01T10:05:00Z",
                        "type": "Normal",
                        "reason": "Scheduled",
                        "message": "Successfully assigned"
                    }
                ]
            }),
            stderr=''
        )
        
        events = self.client.get_pod_events("test-pod")
        
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]['type'], 'Warning')
        self.assertEqual(events[1]['type'], 'Normal')
    
    @patch('main.subprocess.run')
    def test_check_node_resources(self, mock_run):
        """测试检查节点资源"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "items": [
                    {
                        "metadata": {"name": "node1"},
                        "status": {
                            "capacity": {"cpu": "4", "memory": "16Gi"},
                            "allocatable": {"cpu": "3800m", "memory": "15Gi"},
                            "conditions": [{"type": "Ready", "status": "True"}]
                        }
                    }
                ]
            }),
            stderr=''
        )
        
        nodes = self.client.check_node_resources()
        
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0]['name'], 'node1')
        self.assertEqual(nodes[0]['capacity']['cpu'], '4')
    
    @patch('main.subprocess.run')
    def test_check_resource_pressure(self, mock_run):
        """测试检查资源压力"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "items": [
                    {
                        "metadata": {"name": "node1"},
                        "status": {
                            "conditions": [
                                {"type": "Ready", "status": "True"},
                                {"type": "MemoryPressure", "status": "True", "message": "memory pressure"},
                                {"type": "DiskPressure", "status": "False"}
                            ]
                        }
                    }
                ]
            }),
            stderr=''
        )
        
        pressures = self.client.check_resource_pressure()
        
        self.assertEqual(len(pressures), 1)
        self.assertEqual(pressures[0]['node'], 'node1')
        self.assertEqual(pressures[0]['type'], 'MemoryPressure')
    
    @patch('main.subprocess.run')
    def test_check_services(self, mock_run):
        """测试检查Service"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "items": [
                    {
                        "metadata": {"name": "my-service"},
                        "spec": {
                            "type": "ClusterIP",
                            "clusterIP": "10.96.0.1",
                            "ports": [{"port": 80, "protocol": "TCP"}],
                            "selector": {"app": "myapp"}
                        }
                    }
                ]
            }),
            stderr=''
        )
        
        services = self.client.check_services()
        
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0]['name'], 'my-service')
        self.assertEqual(services[0]['type'], 'ClusterIP')
    
    @patch('main.subprocess.run')
    def test_check_storage(self, mock_run):
        """测试检查存储"""
        # Mock for PV
        mock_run.side_effect = [
            MagicMock(
                returncode=0,
                stdout=json.dumps({
                    "items": [
                        {
                            "metadata": {"name": "pv1"},
                            "spec": {"capacity": {"storage": "10Gi"}, "storageClassName": "standard"},
                            "status": {"phase": "Bound"}
                        }
                    ]
                }),
                stderr=''
            ),
            MagicMock(
                returncode=0,
                stdout=json.dumps({
                    "items": [
                        {
                            "metadata": {"name": "pvc1", "namespace": "default"},
                            "spec": {"storageClassName": "standard"},
                            "status": {"phase": "Bound", "capacity": {"storage": "10Gi"}}
                        }
                    ]
                }),
                stderr=''
            )
        ]
        
        pvs, pvcs = self.client.check_storage()
        
        self.assertEqual(len(pvs), 1)
        self.assertEqual(len(pvcs), 1)
        self.assertEqual(pvs[0]['name'], 'pv1')
        self.assertEqual(pvcs[0]['name'], 'pvc1')
    
    @patch('main.subprocess.run')
    def test_analyze_logs(self, mock_run):
        """测试日志分析"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='''
INFO: Starting application
ERROR: Failed to connect to database
Exception: Connection timeout
ERROR: Retrying connection
INFO: Application started
OutOfMemory: Java heap space
            ''',
            stderr=''
        )
        
        analysis = self.client.analyze_logs("test-pod")
        
        self.assertEqual(analysis['total_lines'], 7)
        self.assertEqual(analysis['error_counts']['error'], 2)
        self.assertEqual(analysis['error_counts']['exception'], 1)
        self.assertEqual(analysis['error_counts']['oom'], 1)
    
    @patch('main.subprocess.run')
    def test_get_exit_code_info(self, mock_run):
        """测试获取退出码信息"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "status": {
                    "containerStatuses": [
                        {
                            "name": "app",
                            "lastState": {
                                "terminated": {
                                    "exitCode": 1,
                                    "reason": "Error",
                                    "message": "Application crashed"
                                }
                            }
                        }
                    ]
                }
            }),
            stderr=''
        )
        
        exit_info = self.client.get_exit_code_info("test-pod")
        
        self.assertEqual(len(exit_info['containers']), 1)
        self.assertEqual(exit_info['containers'][0]['exit_code'], 1)
        self.assertEqual(exit_info['containers'][0]['reason'], 'Error')


class TestPodDiagnostic(unittest.TestCase):
    """PodDiagnostic数据类测试"""
    
    def test_diagnostic_creation(self):
        """测试创建诊断结果"""
        diagnostic = PodDiagnostic(
            name="test-pod",
            namespace="default",
            status="Running",
            phase="Running",
            ready="1/1",
            restarts=0,
            issues=[],
            recommendations=[]
        )
        
        self.assertEqual(diagnostic.name, "test-pod")
        self.assertEqual(diagnostic.phase, "Running")
        self.assertEqual(diagnostic.restarts, 0)
    
    def test_diagnostic_with_issues(self):
        """测试带问题的诊断结果"""
        diagnostic = PodDiagnostic(
            name="crash-pod",
            namespace="default",
            status="CrashLoopBackOff",
            phase="Failed",
            ready="0/1",
            restarts=15,
            issues=["容器频繁重启", "退出码1"],
            recommendations=["检查日志", "检查资源限制"]
        )
        
        self.assertEqual(len(diagnostic.issues), 2)
        self.assertEqual(len(diagnostic.recommendations), 2)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = TroubleshootClient()
        self.assertEqual(client.namespace, "default")
        self.assertIsNone(client.kubeconfig)
        self.assertIsNone(client.context)
    
    def test_client_with_custom_config(self):
        """测试自定义配置的客户端"""
        client = TroubleshootClient(
            kubeconfig="/custom/config",
            context="prod",
            namespace="production"
        )
        self.assertEqual(client.kubeconfig, "/custom/config")
        self.assertEqual(client.context, "prod")
        self.assertEqual(client.namespace, "production")


def run_command_test():
    """运行命令行测试"""
    print("=" * 60)
    print("K8s Troubleshoot Skill 命令行测试")
    print("=" * 60)
    
    test_commands = [
        ("显示帮助", ["python", "main.py", "--help"]),
        ("Pod命令帮助", ["python", "main.py", "pod", "--help"]),
        ("Network命令帮助", ["python", "main.py", "network", "--help"]),
        ("Resource命令帮助", ["python", "main.py", "resource", "--help"]),
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
    print("K8s Troubleshoot Skill 测试套件")
    print("=" * 60)
    
    # 运行单元测试
    print("\n[1/2] 运行单元测试...")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestTroubleshootClient))
    suite.addTests(loader.loadTestsFromTestCase(TestPodDiagnostic))
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
