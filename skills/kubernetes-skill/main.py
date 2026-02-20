#!/usr/bin/env python3
"""
Kubernetes Skill - Kubernetes集群管理工具

功能：Kubernetes集群管理。Use when managing Kubernetes clusters, deploying applications to K8s, 
or when user mentions 'kubernetes', 'k8s', 'kubectl', 'pod', 'deployment'。
"""

import argparse
import json
import sys
import subprocess
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree


console = Console()


@dataclass
class PodInfo:
    """Pod信息数据类"""
    name: str
    namespace: str
    ready: str
    status: str
    restarts: str
    age: str
    ip: str
    node: str


@dataclass
class DeploymentInfo:
    """Deployment信息数据类"""
    name: str
    namespace: str
    ready: str
    up_to_date: str
    available: str
    age: str


@dataclass
class ServiceInfo:
    """Service信息数据类"""
    name: str
    namespace: str
    type: str
    cluster_ip: str
    external_ip: str
    ports: str
    age: str


@dataclass
class NodeInfo:
    """节点信息数据类"""
    name: str
    status: str
    roles: str
    age: str
    version: str
    internal_ip: str
    external_ip: str


class KubectlClient:
    """Kubectl客户端封装"""
    
    def __init__(self, kubeconfig: Optional[str] = None, 
                 context: Optional[str] = None,
                 namespace: str = "default"):
        self.kubeconfig = kubeconfig
        self.context = context
        self.namespace = namespace
        self.base_cmd = ["kubectl"]
    
    def _build_cmd(self, args: List[str]) -> List[str]:
        """构建kubectl命令"""
        cmd = self.base_cmd.copy()
        
        if self.kubeconfig:
            cmd.extend(["--kubeconfig", self.kubeconfig])
        if self.context:
            cmd.extend(["--context", self.context])
        
        # 全局参数
        cmd.extend(args)
        return cmd
    
    def _run_command(self, cmd: List[str], capture_output: bool = True) -> tuple:
        """执行kubectl命令"""
        full_cmd = self._build_cmd(cmd)
        try:
            result = subprocess.run(
                full_cmd,
                capture_output=capture_output,
                text=True,
                timeout=60,
                encoding='utf-8'
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out after 60 seconds"
        except Exception as e:
            return -1, "", str(e)
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """获取集群信息"""
        info = {}
        
        # 集群版本
        returncode, stdout, _ = self._run_command(["version", "-o", "json"])
        if returncode == 0:
            try:
                version_data = json.loads(stdout)
                info['version'] = version_data
            except json.JSONDecodeError:
                pass
        
        # 集群信息
        returncode, stdout, _ = self._run_command(["cluster-info"])
        if returncode == 0:
            info['cluster_info'] = stdout
        
        # 节点数量
        returncode, stdout, _ = self._run_command(
            ["get", "nodes", "-o", "jsonpath={.items[*].metadata.name}"]
        )
        if returncode == 0:
            info['nodes'] = stdout.split()
        
        return info
    
    def list_nodes(self) -> List[NodeInfo]:
        """列出所有节点"""
        cmd = ["get", "nodes", "-o", "json"]
        returncode, stdout, stderr = self._run_command(cmd)
        
        if returncode != 0:
            console.print(f"[red]Error: {stderr}[/red]")
            return []
        
        try:
            data = json.loads(stdout)
            nodes = []
            for item in data.get('items', []):
                metadata = item.get('metadata', {})
                status = item.get('status', {})
                
                # 获取节点状态
                node_status = "Unknown"
                for condition in status.get('conditions', []):
                    if condition.get('type') == 'Ready':
                        node_status = 'Ready' if condition.get('status') == 'True' else 'NotReady'
                
                # 获取IP地址
                internal_ip = ""
                external_ip = ""
                for addr in status.get('addresses', []):
                    if addr.get('type') == 'InternalIP':
                        internal_ip = addr.get('address', '')
                    elif addr.get('type') == 'ExternalIP':
                        external_ip = addr.get('address', '')
                
                nodes.append(NodeInfo(
                    name=metadata.get('name', ''),
                    status=node_status,
                    roles=','.join(metadata.get('labels', {}).get('kubernetes.io/role', '').split(',')),
                    age=self._calculate_age(metadata.get('creationTimestamp', '')),
                    version=status.get('nodeInfo', {}).get('kubeletVersion', ''),
                    internal_ip=internal_ip,
                    external_ip=external_ip
                ))
            return nodes
        except (json.JSONDecodeError, KeyError) as e:
            console.print(f"[red]Parse error: {e}[/red]")
            return []
    
    def _calculate_age(self, timestamp: str) -> str:
        """计算资源年龄"""
        if not timestamp:
            return "Unknown"
        try:
            created = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            delta = datetime.now(created.tzinfo) - created
            if delta.days > 0:
                return f"{delta.days}d"
            elif delta.seconds // 3600 > 0:
                return f"{delta.seconds // 3600}h"
            else:
                return f"{delta.seconds // 60}m"
        except:
            return "Unknown"
    
    def list_pods(self, namespace: Optional[str] = None, 
                  all_namespaces: bool = False,
                  selector: Optional[str] = None) -> List[PodInfo]:
        """列出Pod"""
        cmd = ["get", "pods", "-o", "json"]
        
        if all_namespaces:
            cmd.append("--all-namespaces")
        elif namespace:
            cmd.extend(["-n", namespace])
        else:
            cmd.extend(["-n", self.namespace])
        
        if selector:
            cmd.extend(["-l", selector])
        
        returncode, stdout, stderr = self._run_command(cmd)
        
        if returncode != 0:
            console.print(f"[red]Error: {stderr}[/red]")
            return []
        
        try:
            data = json.loads(stdout)
            pods = []
            for item in data.get('items', []):
                metadata = item.get('metadata', {})
                status = item.get('status', {})
                spec = item.get('spec', {})
                
                # 计算ready状态
                container_statuses = status.get('containerStatuses', [])
                ready_count = sum(1 for c in container_statuses if c.get('ready', False))
                total_count = len(container_statuses)
                
                # 计算重启次数
                restarts = sum(c.get('restartCount', 0) for c in container_statuses)
                
                pods.append(PodInfo(
                    name=metadata.get('name', ''),
                    namespace=metadata.get('namespace', ''),
                    ready=f"{ready_count}/{total_count}",
                    status=status.get('phase', 'Unknown'),
                    restarts=str(restarts),
                    age=self._calculate_age(metadata.get('creationTimestamp', '')),
                    ip=status.get('podIP', '<none>'),
                    node=spec.get('nodeName', '<none>')
                ))
            return pods
        except (json.JSONDecodeError, KeyError) as e:
            console.print(f"[red]Parse error: {e}[/red]")
            return []
    
    def describe_pod(self, name: str, namespace: Optional[str] = None) -> str:
        """查看Pod详情"""
        ns = namespace or self.namespace
        returncode, stdout, stderr = self._run_command(
            ["describe", "pod", name, "-n", ns]
        )
        if returncode == 0:
            return stdout
        return f"Error: {stderr}"
    
    def get_pod_logs(self, name: str, namespace: Optional[str] = None,
                     tail: Optional[int] = None, follow: bool = False,
                     previous: bool = False, container: Optional[str] = None) -> str:
        """获取Pod日志"""
        ns = namespace or self.namespace
        cmd = ["logs", name, "-n", ns]
        
        if tail:
            cmd.extend(["--tail", str(tail)])
        if previous:
            cmd.append("--previous")
        if container:
            cmd.extend(["-c", container])
        if follow:
            cmd.append("-f")
        
        returncode, stdout, stderr = self._run_command(cmd, capture_output=not follow)
        if returncode == 0:
            return stdout
        return f"Error: {stderr}"
    
    def exec_in_pod(self, name: str, command: str, namespace: Optional[str] = None,
                    interactive: bool = False, tty: bool = False) -> bool:
        """在Pod中执行命令"""
        ns = namespace or self.namespace
        cmd = ["exec", name, "-n", ns]
        
        if interactive:
            cmd.append("-i")
        if tty:
            cmd.append("-t")
        
        cmd.append("--")
        cmd.extend(command.split())
        
        returncode, _, stderr = self._run_command(cmd, capture_output=False)
        if returncode != 0:
            console.print(f"[red]Error: {stderr}[/red]")
        return returncode == 0
    
    def delete_pod(self, name: str, namespace: Optional[str] = None, force: bool = False) -> bool:
        """删除Pod"""
        ns = namespace or self.namespace
        cmd = ["delete", "pod", name, "-n", ns]
        
        if force:
            cmd.append("--force")
        
        returncode, stdout, stderr = self._run_command(cmd)
        if returncode == 0:
            console.print(f"[green]{stdout}[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def port_forward(self, name: str, port_mapping: str, 
                     namespace: Optional[str] = None) -> bool:
        """端口转发"""
        ns = namespace or self.namespace
        cmd = ["port-forward", name, port_mapping, "-n", ns]
        
        returncode, _, _ = self._run_command(cmd, capture_output=False)
        return returncode == 0
    
    def list_deployments(self, namespace: Optional[str] = None,
                        all_namespaces: bool = False) -> List[DeploymentInfo]:
        """列出Deployment"""
        cmd = ["get", "deployments", "-o", "json"]
        
        if all_namespaces:
            cmd.append("--all-namespaces")
        elif namespace:
            cmd.extend(["-n", namespace])
        else:
            cmd.extend(["-n", self.namespace])
        
        returncode, stdout, stderr = self._run_command(cmd)
        
        if returncode != 0:
            console.print(f"[red]Error: {stderr}[/red]")
            return []
        
        try:
            data = json.loads(stdout)
            deployments = []
            for item in data.get('items', []):
                metadata = item.get('metadata', {})
                status = item.get('status', {})
                spec = item.get('spec', {})
                
                replicas = spec.get('replicas', 0)
                ready = status.get('readyReplicas', 0)
                updated = status.get('updatedReplicas', 0)
                available = status.get('availableReplicas', 0)
                
                deployments.append(DeploymentInfo(
                    name=metadata.get('name', ''),
                    namespace=metadata.get('namespace', ''),
                    ready=f"{ready}/{replicas}",
                    up_to_date=str(updated),
                    available=str(available),
                    age=self._calculate_age(metadata.get('creationTimestamp', ''))
                ))
            return deployments
        except (json.JSONDecodeError, KeyError) as e:
            console.print(f"[red]Parse error: {e}[/red]")
            return []
    
    def create_deployment(self, name: str, image: str, replicas: int = 1,
                          port: Optional[int] = None, namespace: Optional[str] = None,
                          env: Optional[List[str]] = None) -> bool:
        """创建Deployment"""
        ns = namespace or self.namespace
        cmd = ["create", "deployment", name, "--image", image, "-n", ns]
        
        if replicas:
            cmd.extend(["--replicas", str(replicas)])
        if port:
            cmd.extend(["--port", str(port)])
        
        returncode, stdout, stderr = self._run_command(cmd)
        if returncode == 0:
            console.print(f"[green]Deployment {name} created successfully[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def set_deployment_image(self, name: str, container_image: str,
                             namespace: Optional[str] = None) -> bool:
        """更新Deployment镜像"""
        ns = namespace or self.namespace
        cmd = ["set", "image", f"deployment/{name}", container_image, "-n", ns]
        
        returncode, stdout, stderr = self._run_command(cmd)
        if returncode == 0:
            console.print(f"[green]Image updated for deployment {name}[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def scale_deployment(self, name: str, replicas: int,
                        namespace: Optional[str] = None) -> bool:
        """扩缩容Deployment"""
        ns = namespace or self.namespace
        cmd = ["scale", "deployment", name, f"--replicas={replicas}", "-n", ns]
        
        returncode, stdout, stderr = self._run_command(cmd)
        if returncode == 0:
            console.print(f"[green]{stdout}[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def rollout_status(self, name: str, namespace: Optional[str] = None,
                      timeout: Optional[str] = None) -> str:
        """查看滚动更新状态"""
        ns = namespace or self.namespace
        cmd = ["rollout", "status", f"deployment/{name}", "-n", ns]
        
        if timeout:
            cmd.extend(["--timeout", timeout])
        
        returncode, stdout, stderr = self._run_command(cmd)
        return stdout if returncode == 0 else stderr
    
    def rollout_undo(self, name: str, namespace: Optional[str] = None,
                    to_revision: Optional[int] = None) -> bool:
        """回滚Deployment"""
        ns = namespace or self.namespace
        cmd = ["rollout", "undo", f"deployment/{name}", "-n", ns]
        
        if to_revision:
            cmd.extend(["--to-revision", str(to_revision)])
        
        returncode, stdout, stderr = self._run_command(cmd)
        if returncode == 0:
            console.print(f"[green]{stdout}[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def rollout_history(self, name: str, namespace: Optional[str] = None) -> str:
        """查看Deployment历史"""
        ns = namespace or self.namespace
        returncode, stdout, stderr = self._run_command(
            ["rollout", "history", f"deployment/{name}", "-n", ns]
        )
        return stdout if returncode == 0 else stderr
    
    def delete_deployment(self, name: str, namespace: Optional[str] = None) -> bool:
        """删除Deployment"""
        ns = namespace or self.namespace
        returncode, stdout, stderr = self._run_command(
            ["delete", "deployment", name, "-n", ns]
        )
        if returncode == 0:
            console.print(f"[green]{stdout}[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def list_services(self, namespace: Optional[str] = None,
                     all_namespaces: bool = False) -> List[ServiceInfo]:
        """列出Service"""
        cmd = ["get", "services", "-o", "json"]
        
        if all_namespaces:
            cmd.append("--all-namespaces")
        elif namespace:
            cmd.extend(["-n", namespace])
        else:
            cmd.extend(["-n", self.namespace])
        
        returncode, stdout, stderr = self._run_command(cmd)
        
        if returncode != 0:
            console.print(f"[red]Error: {stderr}[/red]")
            return []
        
        try:
            data = json.loads(stdout)
            services = []
            for item in data.get('items', []):
                metadata = item.get('metadata', {})
                spec = item.get('spec', {})
                status = item.get('status', {})
                
                # 格式化端口
                ports = spec.get('ports', [])
                port_str = ','.join([
                    f"{p.get('port', '')}:{p.get('targetPort', '')}/{p.get('protocol', 'TCP')}"
                    for p in ports
                ]) if ports else "<none>"
                
                # 获取ExternalIP
                external_ips = status.get('loadBalancer', {}).get('ingress', [])
                external_ip = ','.join([
                    ip.get('ip', ip.get('hostname', '')) for ip in external_ips
                ]) if external_ips else "<none>"
                
                services.append(ServiceInfo(
                    name=metadata.get('name', ''),
                    namespace=metadata.get('namespace', ''),
                    type=spec.get('type', 'ClusterIP'),
                    cluster_ip=spec.get('clusterIP', '<none>'),
                    external_ip=external_ip,
                    ports=port_str,
                    age=self._calculate_age(metadata.get('creationTimestamp', ''))
                ))
            return services
        except (json.JSONDecodeError, KeyError) as e:
            console.print(f"[red]Parse error: {e}[/red]")
            return []
    
    def expose_service(self, resource: str, resource_name: str,
                      port: int, target_port: Optional[int] = None,
                      service_type: str = "ClusterIP",
                      namespace: Optional[str] = None) -> bool:
        """暴露资源为Service"""
        ns = namespace or self.namespace
        cmd = ["expose", resource, resource_name, "-n", ns]
        
        cmd.extend(["--port", str(port)])
        if target_port:
            cmd.extend(["--target-port", str(target_port)])
        cmd.extend(["--type", service_type])
        
        returncode, stdout, stderr = self._run_command(cmd)
        if returncode == 0:
            console.print(f"[green]{stdout}[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def apply_manifest(self, path: str, namespace: Optional[str] = None,
                      dry_run: bool = False) -> bool:
        """应用YAML配置"""
        cmd = ["apply", "-f", path]
        
        if namespace:
            cmd.extend(["-n", namespace])
        if dry_run:
            cmd.append("--dry-run=client")
        
        returncode, stdout, stderr = self._run_command(cmd)
        if returncode == 0:
            console.print(f"[green]{stdout}[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def delete_resource(self, path: str, namespace: Optional[str] = None) -> bool:
        """删除资源"""
        cmd = ["delete", "-f", path]
        
        if namespace:
            cmd.extend(["-n", namespace])
        
        returncode, stdout, stderr = self._run_command(cmd)
        if returncode == 0:
            console.print(f"[green]{stdout}[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False


def print_pods(pods: List[PodInfo], output_format: str = "table"):
    """打印Pod列表"""
    if not pods:
        console.print("[yellow]No pods found[/yellow]")
        return
    
    if output_format == "json":
        console.print(json.dumps([asdict(p) for p in pods], indent=2))
    elif output_format == "yaml":
        console.print(yaml.dump([asdict(p) for p in pods], default_flow_style=False))
    else:
        table = Table(title="Pods")
        table.add_column("Namespace", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Ready", style="blue")
        table.add_column("Status", style="yellow")
        table.add_column("Restarts")
        table.add_column("Age")
        table.add_column("IP")
        table.add_column("Node")
        
        for p in pods:
            status_color = "green" if p.status == "Running" else "red" if p.status == "Error" else "yellow"
            table.add_row(
                p.namespace, p.name, p.ready,
                f"[{status_color}]{p.status}[/{status_color}]",
                p.restarts, p.age, p.ip, p.node
            )
        console.print(table)


def print_deployments(deployments: List[DeploymentInfo], output_format: str = "table"):
    """打印Deployment列表"""
    if not deployments:
        console.print("[yellow]No deployments found[/yellow]")
        return
    
    if output_format == "json":
        console.print(json.dumps([asdict(d) for d in deployments], indent=2))
    elif output_format == "yaml":
        console.print(yaml.dump([asdict(d) for d in deployments], default_flow_style=False))
    else:
        table = Table(title="Deployments")
        table.add_column("Namespace", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Ready", style="blue")
        table.add_column("Up-to-date")
        table.add_column("Available")
        table.add_column("Age")
        
        for d in deployments:
            table.add_row(d.namespace, d.name, d.ready, d.up_to_date, d.available, d.age)
        console.print(table)


def print_services(services: List[ServiceInfo], output_format: str = "table"):
    """打印Service列表"""
    if not services:
        console.print("[yellow]No services found[/yellow]")
        return
    
    if output_format == "json":
        console.print(json.dumps([asdict(s) for s in services], indent=2))
    elif output_format == "yaml":
        console.print(yaml.dump([asdict(s) for s in services], default_flow_style=False))
    else:
        table = Table(title="Services")
        table.add_column("Namespace", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="blue")
        table.add_column("Cluster-IP")
        table.add_column("External-IP")
        table.add_column("Ports")
        table.add_column("Age")
        
        for s in services:
            table.add_row(s.namespace, s.name, s.type, s.cluster_ip, s.external_ip, s.ports, s.age)
        console.print(table)


def print_nodes(nodes: List[NodeInfo], output_format: str = "table"):
    """打印节点列表"""
    if not nodes:
        console.print("[yellow]No nodes found[/yellow]")
        return
    
    if output_format == "json":
        console.print(json.dumps([asdict(n) for n in nodes], indent=2))
    elif output_format == "yaml":
        console.print(yaml.dump([asdict(n) for n in nodes], default_flow_style=False))
    else:
        table = Table(title="Nodes")
        table.add_column("Name", style="green")
        table.add_column("Status", style="cyan")
        table.add_column("Roles")
        table.add_column("Age")
        table.add_column("Version")
        table.add_column("Internal-IP")
        table.add_column("External-IP")
        
        for n in nodes:
            status_color = "green" if n.status == "Ready" else "red"
            table.add_row(
                n.name, f"[{status_color}]{n.status}[/{status_color}]",
                n.roles, n.age, n.version, n.internal_ip, n.external_ip
            )
        console.print(table)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Kubernetes Skill - Kubernetes集群管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--namespace", "-n", default="default", help="命名空间")
    parser.add_argument("--all-namespaces", "-A", action="store_true", help="所有命名空间")
    parser.add_argument("--output", "-o", choices=["table", "json", "yaml"], 
                       default="table", help="输出格式")
    parser.add_argument("--context", help="kubectl上下文")
    parser.add_argument("--kubeconfig", help="kubeconfig文件路径")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # Cluster命令
    cluster_parser = subparsers.add_parser("cluster", help="集群信息")
    cluster_subparsers = cluster_parser.add_subparsers(dest="cluster_action")
    cluster_subparsers.add_parser("info", help="集群信息")
    
    # Node命令
    node_parser = subparsers.add_parser("node", help="节点管理")
    node_subparsers = node_parser.add_subparsers(dest="node_action")
    node_subparsers.add_parser("ls", help="列出节点")
    
    describe_node = node_subparsers.add_parser("describe", help="节点详情")
    describe_node.add_argument("name", help="节点名称")
    
    # Pod命令
    pod_parser = subparsers.add_parser("pod", help="Pod管理")
    pod_subparsers = pod_parser.add_subparsers(dest="pod_action")
    
    pod_ls = pod_subparsers.add_parser("ls", help="列出Pod")
    pod_ls.add_argument("--selector", "-l", help="标签选择器")
    
    pod_describe = pod_subparsers.add_parser("describe", help="Pod详情")
    pod_describe.add_argument("name", help="Pod名称")
    
    pod_logs = pod_subparsers.add_parser("logs", help="查看日志")
    pod_logs.add_argument("name", help="Pod名称")
    pod_logs.add_argument("--tail", "-n", type=int, help="显示最后N行")
    pod_logs.add_argument("--follow", "-f", action="store_true", help="实时跟踪")
    pod_logs.add_argument("--previous", "-p", action="store_true", help="之前容器")
    pod_logs.add_argument("--container", "-c", help="容器名称")
    
    pod_exec = pod_subparsers.add_parser("exec", help="执行命令")
    pod_exec.add_argument("name", help="Pod名称")
    pod_exec.add_argument("--", dest="command", help="要执行的命令")
    pod_exec.add_argument("-it", action="store_true", help="交互式TTY")
    
    pod_delete = pod_subparsers.add_parser("delete", help="删除Pod")
    pod_delete.add_argument("name", help="Pod名称")
    pod_delete.add_argument("--force", action="store_true", help="强制删除")
    
    pod_port_fwd = pod_subparsers.add_parser("port-forward", help="端口转发")
    pod_port_fwd.add_argument("name", help="Pod名称")
    pod_port_fwd.add_argument("mapping", help="端口映射 (如 8080:80)")
    
    # Deployment命令
    deploy_parser = subparsers.add_parser("deployment", help="Deployment管理")
    deploy_subparsers = deploy_parser.add_subparsers(dest="deploy_action")
    
    deploy_subparsers.add_parser("ls", help="列出Deployment")
    
    deploy_create = deploy_subparsers.add_parser("create", help="创建Deployment")
    deploy_create.add_argument("name", help="Deployment名称")
    deploy_create.add_argument("--image", required=True, help="容器镜像")
    deploy_create.add_argument("--replicas", type=int, default=1, help="副本数")
    deploy_create.add_argument("--port", type=int, help="容器端口")
    
    deploy_set_image = deploy_subparsers.add_parser("set-image", help="更新镜像")
    deploy_set_image.add_argument("name", help="Deployment名称")
    deploy_set_image.add_argument("container_image", help="容器=镜像格式")
    
    deploy_scale = deploy_subparsers.add_parser("scale", help="扩缩容")
    deploy_scale.add_argument("name", help="Deployment名称")
    deploy_scale.add_argument("--replicas", type=int, required=True, help="副本数")
    
    deploy_status = deploy_subparsers.add_parser("rollout-status", help="滚动状态")
    deploy_status.add_argument("name", help="Deployment名称")
    deploy_status.add_argument("--timeout", help="超时时间")
    
    deploy_undo = deploy_subparsers.add_parser("rollout-undo", help="回滚")
    deploy_undo.add_argument("name", help="Deployment名称")
    deploy_undo.add_argument("--to-revision", type=int, help="回滚到版本")
    
    deploy_history = deploy_subparsers.add_parser("rollout-history", help="历史")
    deploy_history.add_argument("name", help="Deployment名称")
    
    deploy_delete = deploy_subparsers.add_parser("delete", help="删除Deployment")
    deploy_delete.add_argument("name", help="Deployment名称")
    
    # Service命令
    svc_parser = subparsers.add_parser("service", help="Service管理")
    svc_subparsers = svc_parser.add_subparsers(dest="svc_action")
    
    svc_subparsers.add_parser("ls", help="列出Service")
    
    svc_expose = svc_subparsers.add_parser("expose", help="暴露服务")
    svc_expose.add_argument("resource", choices=["deployment", "pod", "replicaset"])
    svc_expose.add_argument("name", help="资源名称")
    svc_expose.add_argument("--port", type=int, required=True, help="服务端口")
    svc_expose.add_argument("--target-port", type=int, help="目标端口")
    svc_expose.add_argument("--type", default="ClusterIP", 
                           choices=["ClusterIP", "NodePort", "LoadBalancer"])
    
    svc_delete = svc_subparsers.add_parser("delete", help="删除Service")
    svc_delete.add_argument("name", help="Service名称")
    
    # Apply命令
    apply_parser = subparsers.add_parser("apply", help="应用配置")
    apply_parser.add_argument("-f", "--filename", required=True, help="文件或目录")
    apply_parser.add_argument("--dry-run", action="store_true", help="预览")
    
    # Delete命令
    delete_parser = subparsers.add_parser("delete", help="删除资源")
    delete_parser.add_argument("-f", "--filename", required=True, help="文件或目录")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    kubectl = KubectlClient(
        kubeconfig=args.kubeconfig,
        context=args.context,
        namespace=args.namespace
    )
    
    ns = None if args.all_namespaces else args.namespace
    
    try:
        if args.command == "cluster":
            if args.cluster_action == "info":
                info = kubectl.get_cluster_info()
                console.print(Panel(json.dumps(info, indent=2), title="Cluster Info"))
        
        elif args.command == "node":
            if args.node_action == "ls":
                nodes = kubectl.list_nodes()
                print_nodes(nodes, args.output)
            elif args.node_action == "describe":
                returncode, stdout, _ = kubectl._run_command(
                    ["describe", "node", args.name]
                )
                console.print(stdout)
        
        elif args.command == "pod":
            if args.pod_action == "ls":
                pods = kubectl.list_pods(
                    namespace=ns,
                    all_namespaces=args.all_namespaces,
                    selector=args.selector
                )
                print_pods(pods, args.output)
            elif args.pod_action == "describe":
                console.print(kubectl.describe_pod(args.name, ns))
            elif args.pod_action == "logs":
                logs = kubectl.get_pod_logs(
                    args.name, ns,
                    tail=args.tail,
                    follow=args.follow,
                    previous=args.previous,
                    container=args.container
                )
                if not args.follow:
                    console.print(logs)
            elif args.pod_action == "exec":
                kubectl.exec_in_pod(
                    args.name, args.command, ns,
                    interactive=args.it, tty=args.it
                )
            elif args.pod_action == "delete":
                kubectl.delete_pod(args.name, ns, args.force)
            elif args.pod_action == "port-forward":
                kubectl.port_forward(args.name, args.mapping, ns)
        
        elif args.command == "deployment":
            if args.deploy_action == "ls":
                deployments = kubectl.list_deployments(ns, args.all_namespaces)
                print_deployments(deployments, args.output)
            elif args.deploy_action == "create":
                kubectl.create_deployment(
                    args.name, args.image,
                    replicas=args.replicas,
                    port=args.port,
                    namespace=ns
                )
            elif args.deploy_action == "set-image":
                kubectl.set_deployment_image(args.name, args.container_image, ns)
            elif args.deploy_action == "scale":
                kubectl.scale_deployment(args.name, args.replicas, ns)
            elif args.deploy_action == "rollout-status":
                console.print(kubectl.rollout_status(args.name, ns, args.timeout))
            elif args.deploy_action == "rollout-undo":
                kubectl.rollout_undo(args.name, ns, args.to_revision)
            elif args.deploy_action == "rollout-history":
                console.print(kubectl.rollout_history(args.name, ns))
            elif args.deploy_action == "delete":
                kubectl.delete_deployment(args.name, ns)
        
        elif args.command == "service":
            if args.svc_action == "ls":
                services = kubectl.list_services(ns, args.all_namespaces)
                print_services(services, args.output)
            elif args.svc_action == "expose":
                kubectl.expose_service(
                    args.resource, args.name,
                    args.port, args.target_port,
                    args.type, ns
                )
            elif args.svc_action == "delete":
                returncode, stdout, stderr = kubectl._run_command(
                    ["delete", "service", args.name, "-n", ns or kubectl.namespace]
                )
                if returncode == 0:
                    console.print(f"[green]Service {args.name} deleted[/green]")
                else:
                    console.print(f"[red]Error: {stderr}[/red]")
        
        elif args.command == "apply":
            kubectl.apply_manifest(args.filename, ns, args.dry_run)
        
        elif args.command == "delete":
            kubectl.delete_resource(args.filename, ns)
        
        return 0
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
        return 130
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
