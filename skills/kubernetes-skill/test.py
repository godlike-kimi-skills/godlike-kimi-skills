#!/usr/bin/env python3
"""
Kubernetes Skill 测试文件

运行测试: python test.py
"""

import unittest
import subprocess
import json
import os
import sys
from unittest.mock import patch, MagicMock, call
from datetime import datetime

# 导入被测试的模块
sys.path.insert(0, os.path.dirname(__file__))
from main import KubectlClient, PodInfo, DeploymentInfo, ServiceInfo, NodeInfo


class TestKubectlClient(unittest.TestCase):
    """KubectlClient类测试"""
    
    def setUp(self):
        """测试准备"""
        self.kubectl = KubectlClient(
            kubeconfig="/path/to/config",
            context="test-context",
            namespace="test-ns"
        )
    
    def test_build_cmd(self):
        """测试命令构建"""
        cmd = self.kubectl._build_cmd(["get", "pods"])
        
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
        
        returncode, stdout, stderr = self.kubectl._run_command(["get", "pods"])
        
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
        
        returncode, stdout, stderr = self.kubectl._run_command(["invalid"])
        
        self.assertEqual(returncode, 1)
        self.assertEqual(stderr, 'error message')
    
    @patch('main.subprocess.run')
    def test_get_cluster_info(self, mock_run):
        """测试获取集群信息"""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=json.dumps({
                "serverVersion": {"major": "1", "minor": "28"}
            }), stderr=''),
            MagicMock(returncode=0, stdout='Kubernetes control plane', stderr=''),
            MagicMock(returncode=0, stdout='node1 node2', stderr='')
        ]
        
        info = self.kubectl.get_cluster_info()
        
        self.assertIn('version', info)
        self.assertIn('nodes', info)
    
    @patch('main.subprocess.run')
    def test_list_nodes(self, mock_run):
        """测试列出节点"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "items": [{
                    "metadata": {
                        "name": "node1",
                        "creationTimestamp": "2024-01-01T00:00:00Z",
                        "labels": {"kubernetes.io/role": "master"}
                    },
                    "status": {
                        "conditions": [{"type": "Ready", "status": "True"}],
                        "addresses": [
                            {"type": "InternalIP", "address": "10.0.0.1"},
                            {"type": "ExternalIP", "address": "1.2.3.4"}
                        ],
                        "nodeInfo": {"kubeletVersion": "v1.28.0"}
                    }
                }]
            }),
            stderr=''
        )
        
        nodes = self.kubectl.list_nodes()
        
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].name, "node1")
        self.assertEqual(nodes[0].status, "Ready")
    
    @patch('main.subprocess.run')
    def test_list_pods(self, mock_run):
        """测试列出Pod"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "items": [{
                    "metadata": {
                        "name": "pod1",
                        "namespace": "default",
                        "creationTimestamp": "2024-01-01T00:00:00Z"
                    },
                    "status": {
                        "phase": "Running",
                        "podIP": "10.244.0.1",
                        "containerStatuses": [{"ready": True, "restartCount": 0}]
                    },
                    "spec": {"nodeName": "node1"}
                }]
            }),
            stderr=''
        )
        
        pods = self.kubectl.list_pods()
        
        self.assertEqual(len(pods), 1)
        self.assertEqual(pods[0].name, "pod1")
        self.assertEqual(pods[0].status, "Running")
    
    @patch('main.subprocess.run')
    def test_list_deployments(self, mock_run):
        """测试列出Deployment"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "items": [{
                    "metadata": {
                        "name": "deploy1",
                        "namespace": "default",
                        "creationTimestamp": "2024-01-01T00:00:00Z"
                    },
                    "spec": {"replicas": 3},
                    "status": {
                        "readyReplicas": 3,
                        "updatedReplicas": 3,
                        "availableReplicas": 3
                    }
                }]
            }),
            stderr=''
        )
        
        deployments = self.kubectl.list_deployments()
        
        self.assertEqual(len(deployments), 1)
        self.assertEqual(deployments[0].name, "deploy1")
        self.assertEqual(deployments[0].ready, "3/3")
    
    @patch('main.subprocess.run')
    def test_list_services(self, mock_run):
        """测试列出Service"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "items": [{
                    "metadata": {
                        "name": "svc1",
                        "namespace": "default",
                        "creationTimestamp": "2024-01-01T00:00:00Z"
                    },
                    "spec": {
                        "type": "ClusterIP",
                        "clusterIP": "10.96.0.1",
                        "ports": [{"port": 80, "targetPort": 8080, "protocol": "TCP"}]
                    },
                    "status": {"loadBalancer": {}}
                }]
            }),
            stderr=''
        )
        
        services = self.kubectl.list_services()
        
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0].name, "svc1")
        self.assertEqual(services[0].type, "ClusterIP")
    
    @patch('main.subprocess.run')
    def test_get_pod_logs(self, mock_run):
        """测试获取Pod日志"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='log line 1\nlog line 2',
            stderr=''
        )
        
        logs = self.kubectl.get_pod_logs("pod1", tail=50)
        
        self.assertIn('log line 1', logs)
    
    @patch('main.subprocess.run')
    def test_create_deployment(self, mock_run):
        """测试创建Deployment"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='deployment.apps/deploy1 created',
            stderr=''
        )
        
        result = self.kubectl.create_deployment("deploy1", "nginx:latest", replicas=3)
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_scale_deployment(self, mock_run):
        """测试扩缩容"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='deployment.apps/deploy1 scaled',
            stderr=''
        )
        
        result = self.kubectl.scale_deployment("deploy1", 5)
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_rollout_undo(self, mock_run):
        """测试回滚"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='deployment.apps/deploy1 rolled back',
            stderr=''
        )
        
        result = self.kubectl.rollout_undo("deploy1", to_revision=2)
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_apply_manifest(self, mock_run):
        """测试应用配置"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='deployment.apps/deploy1 created',
            stderr=''
        )
        
        result = self.kubectl.apply_manifest("deployment.yaml")
        
        self.assertTrue(result)
    
    @patch('main.subprocess.run')
    def test_apply_manifest_dry_run(self, mock_run):
        """测试dry-run模式"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='deployment.apps/deploy1 created (dry run)',
            stderr=''
        )
        
        result = self.kubectl.apply_manifest("deployment.yaml", dry_run=True)
        
        self.assertTrue(result)
    
    def test_calculate_age(self):
        """测试年龄计算"""
        # 测试几分钟前
        timestamp = datetime.utcnow().isoformat() + 'Z'
        age = self.kubectl._calculate_age(timestamp)
        self.assertIn('m', age)
        
        # 测试几小时前
        from datetime import timedelta
        hours_ago = (datetime.utcnow() - timedelta(hours=2)).isoformat() + 'Z'
        age = self.kubectl._calculate_age(hours_ago)
        self.assertIn('h', age)
        
        # 测试几天前
        days_ago = (datetime.utcnow() - timedelta(days=2)).isoformat() + 'Z'
        age = self.kubectl._calculate_age(days_ago)
        self.assertIn('d', age)


class TestDataClasses(unittest.TestCase):
    """数据类测试"""
    
    def test_pod_info(self):
        """测试PodInfo数据类"""
        pod = PodInfo(
            name="test-pod",
            namespace="default",
            ready="1/1",
            status="Running",
            restarts="0",
            age="5m",
            ip="10.244.0.1",
            node="node1"
        )
        
        self.assertEqual(pod.name, "test-pod")
        self.assertEqual(pod.status, "Running")
        self.assertEqual(pod.ready, "1/1")
    
    def test_deployment_info(self):
        """测试DeploymentInfo数据类"""
        deploy = DeploymentInfo(
            name="test-deploy",
            namespace="default",
            ready="3/3",
            up_to_date="3",
            available="3",
            age="1h"
        )
        
        self.assertEqual(deploy.name, "test-deploy")
        self.assertEqual(deploy.ready, "3/3")
    
    def test_service_info(self):
        """测试ServiceInfo数据类"""
        svc = ServiceInfo(
            name="test-svc",
            namespace="default",
            type="ClusterIP",
            cluster_ip="10.96.0.1",
            external_ip="<none>",
            ports="80:8080/TCP",
            age="2h"
        )
        
        self.assertEqual(svc.name, "test-svc")
        self.assertEqual(svc.type, "ClusterIP")
    
    def test_node_info(self):
        """测试NodeInfo数据类"""
        node = NodeInfo(
            name="node1",
            status="Ready",
            roles="master,worker",
            age="10d",
            version="v1.28.0",
            internal_ip="10.0.0.1",
            external_ip="1.2.3.4"
        )
        
        self.assertEqual(node.name, "node1")
        self.assertEqual(node.status, "Ready")


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = KubectlClient()
        self.assertEqual(client.namespace, "default")
        self.assertIsNone(client.kubeconfig)
        self.assertIsNone(client.context)
    
    def test_client_with_custom_config(self):
        """测试自定义配置的客户端"""
        client = KubectlClient(
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
    print("Kubernetes Skill 命令行测试")
    print("=" * 60)
    
    test_commands = [
        ("显示帮助", ["python", "main.py", "--help"]),
        ("Pod命令帮助", ["python", "main.py", "pod", "--help"]),
        ("Deployment命令帮助", ["python", "main.py", "deployment", "--help"]),
        ("Service命令帮助", ["python", "main.py", "service", "--help"]),
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
    print("Kubernetes Skill 测试套件")
    print("=" * 60)
    
    # 运行单元测试
    print("\n[1/2] 运行单元测试...")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestKubectlClient))
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
