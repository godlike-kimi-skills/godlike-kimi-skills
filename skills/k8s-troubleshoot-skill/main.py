#!/usr/bin/env python3
"""
K8s Troubleshoot Skill - Kubernetes故障排查工具

功能：Kubernetes故障排查。Use when troubleshooting Kubernetes issues, diagnosing pod failures, 
or when user mentions 'troubleshoot', 'debug', 'pod crash', 'network problem'。
"""

import argparse
import json
import sys
import subprocess
import os
import re
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import Counter

import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
from rich.prompt import Confirm


console = Console()


@dataclass
class PodDiagnostic:
    """Pod诊断结果"""
    name: str
    namespace: str
    status: str
    phase: str
    ready: str
    restarts: int
    issues: List[str]
    recommendations: List[str]


@dataclass
class ResourceUsage:
    """资源使用情况"""
    name: str
    cpu_request: str
    cpu_limit: str
    cpu_usage: str
    memory_request: str
    memory_limit: str
    memory_usage: str
    status: str


class TroubleshootClient:
    """故障排查客户端"""
    
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
        
        cmd.extend(args)
        return cmd
    
    def _run_command(self, cmd: List[str], capture_output: bool = True,
                    timeout: int = 60) -> tuple:
        """执行kubectl命令"""
        full_cmd = self._build_cmd(cmd)
        try:
            result = subprocess.run(
                full_cmd,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                encoding='utf-8'
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return -1, "", str(e)
    
    def diagnose_pod(self, name: str, namespace: Optional[str] = None) -> PodDiagnostic:
        """全面诊断Pod"""
        ns = namespace or self.namespace
        issues = []
        recommendations = []
        
        # 获取Pod详情
        returncode, stdout, stderr = self._run_command(
            ["get", "pod", name, "-n", ns, "-o", "json"]
        )
        
        if returncode != 0:
            return PodDiagnostic(
                name=name, namespace=ns, status="Unknown",
                phase="Unknown", ready="Unknown", restarts=0,
                issues=[f"无法获取Pod信息: {stderr}"],
                recommendations=["检查Pod名称和命名空间是否正确"]
            )
        
        try:
            pod_data = json.loads(stdout)
            metadata = pod_data.get('metadata', {})
            status = pod_data.get('status', {})
            spec = pod_data.get('spec', {})
            
            phase = status.get('phase', 'Unknown')
            container_statuses = status.get('containerStatuses', [])
            
            ready_count = sum(1 for c in container_statuses if c.get('ready', False))
            total_count = len(container_statuses)
            restarts = sum(c.get('restartCount', 0) for c in container_statuses)
            
            # 分析状态
            if phase == "Pending":
                issues.append("Pod处于Pending状态，未被调度")
                recommendations.append("1. 检查节点资源是否充足: python main.py resource pressure")
                recommendations.append("2. 检查节点选择器配置")
                recommendations.append("3. 检查污点和容忍设置")
            
            elif phase == "Failed":
                issues.append("Pod处于Failed状态")
                recommendations.append("1. 查看Pod事件: python main.py pod events " + name)
                recommendations.append("2. 查看日志: kubectl logs " + name)
            
            elif restarts > 5:
                issues.append(f"Pod重启次数过多 ({restarts}次)")
                recommendations.append("1. 分析崩溃日志: python main.py logs pattern " + name)
                recommendations.append("2. 检查资源限制是否充足")
            
            # 检查容器状态
            for container in container_statuses:
                state = container.get('state', {})
                
                if 'waiting' in state:
                    waiting = state['waiting']
                    reason = waiting.get('reason', 'Unknown')
                    message = waiting.get('message', '')
                    issues.append(f"容器 {container.get('name')} 处于等待状态: {reason}")
                    if message:
                        issues.append(f"  消息: {message}")
                    
                    if reason == "ImagePullBackOff":
                        recommendations.append("检查镜像名称和仓库访问权限")
                    elif reason == "CrashLoopBackOff":
                        recommendations.append("检查应用配置和依赖服务")
                    elif reason == "CreateContainerConfigError":
                        recommendations.append("检查ConfigMap/Secret挂载配置")
                
                elif 'terminated' in state:
                    terminated = state['terminated']
                    exit_code = terminated.get('exitCode', -1)
                    if exit_code != 0:
                        issues.append(f"容器 {container.get('name')} 异常退出，退出码: {exit_code}")
            
            # 检查资源限制
            containers = spec.get('containers', [])
            for container in containers:
                resources = container.get('resources', {})
                if not resources.get('requests') and not resources.get('limits'):
                    issues.append(f"容器 {container.get('name')} 未设置资源限制")
                    recommendations.append(f"建议为容器 {container.get('name')} 设置CPU/内存请求和限制")
            
            return PodDiagnostic(
                name=name,
                namespace=ns,
                status=status.get('conditions', [{}])[0].get('status', 'Unknown') if status.get('conditions') else 'Unknown',
                phase=phase,
                ready=f"{ready_count}/{total_count}",
                restarts=restarts,
                issues=issues,
                recommendations=recommendations
            )
            
        except json.JSONDecodeError:
            return PodDiagnostic(
                name=name, namespace=ns, status="Error",
                phase="Error", ready="Unknown", restarts=0,
                issues=["解析Pod数据失败"],
                recommendations=["检查kubectl输出格式"]
            )
    
    def get_pod_events(self, name: str, namespace: Optional[str] = None,
                      since: str = "1h") -> List[Dict[str, str]]:
        """获取Pod相关事件"""
        ns = namespace or self.namespace
        
        returncode, stdout, stderr = self._run_command(
            ["get", "events", "-n", ns, "--field-selector", f"involvedObject.name={name}",
             "--sort-by", ".lastTimestamp", "-o", "json"]
        )
        
        if returncode != 0:
            return []
        
        try:
            data = json.loads(stdout)
            events = []
            for item in data.get('items', []):
                events.append({
                    'time': item.get('lastTimestamp', 'Unknown'),
                    'type': item.get('type', 'Unknown'),
                    'reason': item.get('reason', 'Unknown'),
                    'message': item.get('message', '')
                })
            return events
        except json.JSONDecodeError:
            return []
    
    def check_node_resources(self) -> List[Dict[str, Any]]:
        """检查节点资源使用"""
        nodes = []
        
        # 获取节点列表
        returncode, stdout, _ = self._run_command(
            ["get", "nodes", "-o", "json"]
        )
        
        if returncode != 0:
            return nodes
        
        try:
            data = json.loads(stdout)
            for item in data.get('items', []):
                metadata = item.get('metadata', {})
                status = item.get('status', {})
                
                node_info = {
                    'name': metadata.get('name', 'Unknown'),
                    'capacity': status.get('capacity', {}),
                    'allocatable': status.get('allocatable', {}),
                    'conditions': status.get('conditions', [])
                }
                nodes.append(node_info)
        except json.JSONDecodeError:
            pass
        
        return nodes
    
    def check_resource_pressure(self) -> List[Dict[str, str]]:
        """检查资源压力"""
        pressures = []
        
        returncode, stdout, _ = self._run_command(
            ["get", "nodes", "-o", "json"]
        )
        
        if returncode != 0:
            return pressures
        
        try:
            data = json.loads(stdout)
            for item in data.get('items', []):
                metadata = item.get('metadata', {})
                status = item.get('status', {})
                
                node_name = metadata.get('name', 'Unknown')
                
                # 检查条件
                for condition in status.get('conditions', []):
                    cond_type = condition.get('type', '')
                    cond_status = condition.get('status', 'Unknown')
                    
                    if cond_type in ['MemoryPressure', 'DiskPressure', 'PIDPressure'] and cond_status == 'True':
                        pressures.append({
                            'node': node_name,
                            'type': cond_type,
                            'message': condition.get('message', '')
                        })
        except json.JSONDecodeError:
            pass
        
        return pressures
    
    def check_services(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """检查Service配置"""
        ns = namespace or self.namespace
        services = []
        
        returncode, stdout, _ = self._run_command(
            ["get", "services", "-n", ns, "-o", "json"]
        )
        
        if returncode != 0:
            return services
        
        try:
            data = json.loads(stdout)
            for item in data.get('items', []):
                metadata = item.get('metadata', {})
                spec = item.get('spec', {})
                
                services.append({
                    'name': metadata.get('name', ''),
                    'type': spec.get('type', 'ClusterIP'),
                    'cluster_ip': spec.get('clusterIP', ''),
                    'ports': spec.get('ports', []),
                    'selector': spec.get('selector', {})
                })
        except json.JSONDecodeError:
            pass
        
        return services
    
    def check_network_policies(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """检查网络策略"""
        ns = namespace or self.namespace
        policies = []
        
        returncode, stdout, _ = self._run_command(
            ["get", "networkpolicies", "-n", ns, "-o", "json"]
        )
        
        if returncode != 0:
            return policies
        
        try:
            data = json.loads(stdout)
            for item in data.get('items', []):
                metadata = item.get('metadata', {})
                spec = item.get('spec', {})
                
                policies.append({
                    'name': metadata.get('name', ''),
                    'pod_selector': spec.get('podSelector', {}),
                    'policy_types': spec.get('policyTypes', [])
                })
        except json.JSONDecodeError:
            pass
        
        return policies
    
    def check_storage(self, namespace: Optional[str] = None) -> Tuple[List[Dict], List[Dict]]:
        """检查存储状态"""
        ns = namespace or self.namespace
        pvs = []
        pvcs = []
        
        # 获取PV
        returncode, stdout, _ = self._run_command(
            ["get", "pv", "-o", "json"]
        )
        if returncode == 0:
            try:
                data = json.loads(stdout)
                for item in data.get('items', []):
                    pvs.append({
                        'name': item.get('metadata', {}).get('name', ''),
                        'capacity': item.get('spec', {}).get('capacity', {}).get('storage', ''),
                        'phase': item.get('status', {}).get('phase', ''),
                        'storage_class': item.get('spec', {}).get('storageClassName', '')
                    })
            except json.JSONDecodeError:
                pass
        
        # 获取PVC
        returncode, stdout, _ = self._run_command(
            ["get", "pvc", "-n", ns, "-o", "json"]
        )
        if returncode == 0:
            try:
                data = json.loads(stdout)
                for item in data.get('items', []):
                    pvcs.append({
                        'name': item.get('metadata', {}).get('name', ''),
                        'namespace': item.get('metadata', {}).get('namespace', ''),
                        'phase': item.get('status', {}).get('phase', ''),
                        'capacity': item.get('status', {}).get('capacity', {}).get('storage', ''),
                        'storage_class': item.get('spec', {}).get('storageClassName', '')
                    })
            except json.JSONDecodeError:
                pass
        
        return pvs, pvcs
    
    def analyze_logs(self, name: str, namespace: Optional[str] = None,
                    since: str = "1h", tail: int = 1000) -> Dict[str, Any]:
        """分析Pod日志"""
        ns = namespace or self.namespace
        
        returncode, stdout, _ = self._run_command(
            ["logs", name, "-n", ns, "--since", since, "--tail", str(tail)]
        )
        
        if returncode != 0:
            return {'error': '无法获取日志'}
        
        lines = stdout.split('\n')
        
        # 错误模式匹配
        error_patterns = [
            (r'ERROR|FATAL|CRITICAL', 'error'),
            (r'Exception|Traceback', 'exception'),
            (r'OutOfMemory|OOM', 'oom'),
            (r'Connection refused|Connection timeout', 'connection'),
            (r'Permission denied', 'permission'),
        ]
        
        findings = {key: [] for _, key in error_patterns}
        
        for line in lines:
            for pattern, key in error_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings[key].append(line[:200])  # 限制行长度
        
        # 统计
        return {
            'total_lines': len(lines),
            'error_counts': {k: len(v) for k, v in findings.items()},
            'samples': {k: v[:5] for k, v in findings.items() if v}
        }
    
    def check_cluster_health(self) -> Dict[str, Any]:
        """检查集群健康状态"""
        health = {
            'control_plane': {},
            'nodes': [],
            'events': [],
            'issues': []
        }
        
        # 检查控制平面组件
        components = ['kube-apiserver', 'kube-controller-manager', 'kube-scheduler', 'etcd']
        for component in components:
            returncode, stdout, _ = self._run_command(
                ["get", "componentstatuses", component, "-o", "json"]
            )
            if returncode == 0:
                try:
                    data = json.loads(stdout)
                    conditions = data.get('conditions', [])
                    for cond in conditions:
                        health['control_plane'][component] = {
                            'status': cond.get('status'),
                            'message': cond.get('message', '')
                        }
                except json.JSONDecodeError:
                    pass
        
        # 检查节点
        nodes = self.check_node_resources()
        for node in nodes:
            ready = any(
                c.get('type') == 'Ready' and c.get('status') == 'True'
                for c in node.get('conditions', [])
            )
            health['nodes'].append({
                'name': node['name'],
                'ready': ready
            })
        
        return health
    
    def get_exit_code_info(self, name: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """获取容器退出码信息"""
        ns = namespace or self.namespace
        
        returncode, stdout, _ = self._run_command(
            ["get", "pod", name, "-n", ns, "-o", "json"]
        )
        
        if returncode != 0:
            return {'error': '无法获取Pod信息'}
        
        try:
            data = json.loads(stdout)
            container_statuses = data.get('status', {}).get('containerStatuses', [])
            
            exit_info = []
            for container in container_statuses:
                state = container.get('lastState', {})
                if 'terminated' in state:
                    terminated = state['terminated']
                    exit_info.append({
                        'container': container.get('name'),
                        'exit_code': terminated.get('exitCode'),
                        'reason': terminated.get('reason'),
                        'message': terminated.get('message', '')[:200]
                    })
            
            return {'containers': exit_info}
        except json.JSONDecodeError:
            return {'error': '解析失败'}


def print_diagnostic(diagnostic: PodDiagnostic):
    """打印诊断报告"""
    console.print(Panel.fit(
        f"[bold]Pod诊断报告: {diagnostic.name}[/bold]\n"
        f"命名空间: {diagnostic.namespace}\n"
        f"状态: {diagnostic.status}\n"
        f"阶段: {diagnostic.phase}\n"
        f"就绪: {diagnostic.ready}\n"
        f"重启次数: {diagnostic.restarts}",
        title="🔍 Pod诊断"
    ))
    
    if diagnostic.issues:
        console.print("\n[bold red]⚠️ 发现问题:[/bold red]")
        for i, issue in enumerate(diagnostic.issues, 1):
            console.print(f"  {i}. {issue}")
    
    if diagnostic.recommendations:
        console.print("\n[bold green]💡 建议操作:[/bold green]")
        for i, rec in enumerate(diagnostic.recommendations, 1):
            console.print(f"  {i}. {rec}")


def print_events(events: List[Dict[str, str]]):
    """打印事件"""
    if not events:
        console.print("[yellow]无事件[/yellow]")
        return
    
    table = Table(title="Pod事件")
    table.add_column("时间", style="cyan")
    table.add_column("类型", style="yellow")
    table.add_column("原因")
    table.add_column("消息")
    
    for e in events:
        type_color = "red" if e['type'] == 'Warning' else "green"
        table.add_row(
            e['time'],
            f"[{type_color}]{e['type']}[/{type_color}]",
            e['reason'],
            e['message'][:80]
        )
    
    console.print(table)


def print_nodes(nodes: List[Dict[str, Any]]):
    """打印节点信息"""
    table = Table(title="节点资源")
    table.add_column("节点", style="green")
    table.add_column("CPU容量")
    table.add_column("内存容量")
    table.add_column("状态")
    
    for node in nodes:
        ready = any(
            c.get('type') == 'Ready' and c.get('status') == 'True'
            for c in node.get('conditions', [])
        )
        status_color = "green" if ready else "red"
        
        table.add_row(
            node['name'],
            node.get('capacity', {}).get('cpu', 'N/A'),
            node.get('capacity', {}).get('memory', 'N/A'),
            f"[{status_color}]{'Ready' if ready else 'NotReady'}[/{status_color}]"
        )
    
    console.print(table)


def print_pressures(pressures: List[Dict[str, str]]):
    """打印资源压力"""
    if not pressures:
        console.print("[green]✓ 无资源压力[/green]")
        return
    
    table = Table(title="资源压力警告")
    table.add_column("节点", style="red")
    table.add_column("压力类型")
    table.add_column("消息")
    
    for p in pressures:
        table.add_row(p['node'], p['type'], p.get('message', ''))
    
    console.print(table)


def print_storage(pvs: List[Dict], pvcs: List[Dict]):
    """打印存储信息"""
    # PV表
    if pvs:
        pv_table = Table(title="Persistent Volumes")
        pv_table.add_column("名称", style="green")
        pv_table.add_column("容量")
        pv_table.add_column("状态", style="cyan")
        pv_table.add_column("存储类")
        
        for pv in pvs:
            status_color = "green" if pv['phase'] == 'Bound' else "yellow"
            pv_table.add_row(
                pv['name'],
                pv['capacity'],
                f"[{status_color}]{pv['phase']}[/{status_color}]",
                pv['storage_class']
            )
        console.print(pv_table)
    
    # PVC表
    if pvcs:
        pvc_table = Table(title="Persistent Volume Claims")
        pvc_table.add_column("名称", style="green")
        pvc_table.add_column("命名空间")
        pvc_table.add_column("状态", style="cyan")
        pvc_table.add_column("容量")
        
        for pvc in pvcs:
            status_color = "green" if pvc['phase'] == 'Bound' else "red"
            pvc_table.add_row(
                pvc['name'],
                pvc['namespace'],
                f"[{status_color}]{pvc['phase']}[/{status_color}]",
                pvc['capacity'] or 'Pending'
            )
        console.print(pvc_table)


def print_log_analysis(analysis: Dict[str, Any]):
    """打印日志分析"""
    if 'error' in analysis:
        console.print(f"[red]{analysis['error']}[/red]")
        return
    
    console.print(Panel.fit(
        f"总日志行数: {analysis['total_lines']}\n"
        f"错误数: {analysis['error_counts'].get('error', 0)}\n"
        f"异常数: {analysis['error_counts'].get('exception', 0)}\n"
        f"OOM事件: {analysis['error_counts'].get('oom', 0)}\n"
        f"连接问题: {analysis['error_counts'].get('connection', 0)}",
        title="📊 日志分析"
    ))
    
    for error_type, samples in analysis.get('samples', {}).items():
        if samples:
            console.print(f"\n[bold]{error_type.upper()} 示例:[/bold]")
            for sample in samples[:3]:
                console.print(f"  • {sample[:100]}")


def print_cluster_health(health: Dict[str, Any]):
    """打印集群健康状态"""
    console.print(Panel.fit(
        "集群健康检查",
        title="🏥 集群状态"
    ))
    
    # 控制平面
    console.print("\n[bold]控制平面组件:[/bold]")
    for component, info in health.get('control_plane', {}).items():
        status = info.get('status', 'Unknown')
        color = "green" if status == 'True' else "red"
        console.print(f"  {component}: [{color}]{status}[/{color}]")
    
    # 节点
    console.print("\n[bold]节点状态:[/bold]")
    ready_count = sum(1 for n in health.get('nodes', []) if n.get('ready'))
    total_count = len(health.get('nodes', []))
    console.print(f"  就绪节点: {ready_count}/{total_count}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="K8s Troubleshoot Skill - Kubernetes故障排查工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--namespace", "-n", default="default", help="命名空间")
    parser.add_argument("--all-namespaces", "-A", action="store_true", help="所有命名空间")
    parser.add_argument("--output", "-o", choices=["table", "json", "yaml"], 
                       default="table", help="输出格式")
    parser.add_argument("--kubeconfig", help="kubeconfig文件路径")
    parser.add_argument("--context", help="kubectl上下文")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # Pod命令
    pod_parser = subparsers.add_parser("pod", help="Pod诊断")
    pod_subparsers = pod_parser.add_subparsers(dest="pod_action")
    
    pod_diagnose = pod_subparsers.add_parser("diagnose", help="全面诊断")
    pod_diagnose.add_argument("name", help="Pod名称")
    
    pod_events = pod_subparsers.add_parser("events", help="查看事件")
    pod_events.add_argument("name", help="Pod名称")
    pod_events.add_argument("--since", default="1h", help="时间范围")
    
    pod_status = pod_subparsers.add_parser("status", help="查看状态")
    pod_status.add_argument("name", nargs="?", help="Pod名称")
    pod_status.add_argument("-l", "--selector", help="标签选择器")
    
    pod_exit = pod_subparsers.add_parser("exit-code", help="退出码分析")
    pod_exit.add_argument("name", help="Pod名称")
    
    # Network命令
    net_parser = subparsers.add_parser("network", help="网络诊断")
    net_subparsers = net_parser.add_subparsers(dest="net_action")
    
    net_service = net_subparsers.add_parser("service", help="Service诊断")
    net_service.add_argument("name", nargs="?", help="Service名称")
    
    net_dns = net_subparsers.add_parser("dns", help="DNS测试")
    net_dns.add_argument("domain", help="域名")
    
    net_policy = net_subparsers.add_parser("policy", help="网络策略")
    
    # Resource命令
    res_parser = subparsers.add_parser("resource", help="资源分析")
    res_subparsers = res_parser.add_subparsers(dest="res_action")
    
    res_subparsers.add_parser("node", help="节点资源")
    res_subparsers.add_parser("pressure", help="资源压力")
    res_subparsers.add_parser("capacity", help="容量分析")
    
    # Storage命令
    storage_parser = subparsers.add_parser("storage", help="存储诊断")
    storage_subparsers = storage_parser.add_subparsers(dest="storage_action")
    
    storage_subparsers.add_parser("pv", help="PV状态")
    storage_subparsers.add_parser("pvc", help="PVC状态")
    
    # Cluster命令
    cluster_parser = subparsers.add_parser("cluster", help="集群健康")
    cluster_subparsers = cluster_parser.add_subparsers(dest="cluster_action")
    
    cluster_subparsers.add_parser("health", help="健康检查")
    cluster_subparsers.add_parser("nodes", help="节点状态")
    
    # Logs命令
    logs_parser = subparsers.add_parser("logs", help="日志分析")
    logs_subparsers = logs_parser.add_subparsers(dest="logs_action")
    
    logs_analyze = logs_subparsers.add_parser("analyze", help="分析日志")
    logs_analyze.add_argument("name", help="Pod名称")
    logs_analyze.add_argument("--since", default="1h", help="时间范围")
    logs_analyze.add_argument("--tail", type=int, default=1000, help="行数")
    
    logs_errors = logs_subparsers.add_parser("errors", help="错误分析")
    logs_errors.add_argument("-l", "--selector", help="标签选择器")
    logs_errors.add_argument("--since", default="1h", help="时间范围")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    client = TroubleshootClient(
        kubeconfig=args.kubeconfig,
        context=args.context,
        namespace=args.namespace
    )
    
    ns = None if args.all_namespaces else args.namespace
    
    try:
        if args.command == "pod":
            if args.pod_action == "diagnose":
                diagnostic = client.diagnose_pod(args.name, ns)
                print_diagnostic(diagnostic)
            
            elif args.pod_action == "events":
                events = client.get_pod_events(args.name, ns, args.since)
                print_events(events)
            
            elif args.pod_action == "status":
                if args.name:
                    diagnostic = client.diagnose_pod(args.name, ns)
                    print_diagnostic(diagnostic)
                else:
                    console.print("[yellow]请指定Pod名称或使用标签选择器[/yellow]")
            
            elif args.pod_action == "exit-code":
                exit_info = client.get_exit_code_info(args.name, ns)
                if 'error' in exit_info:
                    console.print(f"[red]{exit_info['error']}[/red]")
                else:
                    for container in exit_info.get('containers', []):
                        console.print(f"\n容器: {container['container']}")
                        console.print(f"  退出码: {container['exit_code']}")
                        console.print(f"  原因: {container['reason']}")
                        if container['message']:
                            console.print(f"  消息: {container['message']}")
        
        elif args.command == "network":
            if args.net_action == "service":
                services = client.check_services(ns)
                table = Table(title="Service诊断")
                table.add_column("名称", style="green")
                table.add_column("类型")
                table.add_column("ClusterIP")
                table.add_column("端口")
                for svc in services:
                    ports = ','.join([f"{p.get('port')}/{p.get('protocol', 'TCP')}" 
                                    for p in svc.get('ports', [])])
                    table.add_row(svc['name'], svc['type'], svc['cluster_ip'], ports)
                console.print(table)
            
            elif args.net_action == "dns":
                console.print(f"DNS测试: {args.domain}")
                console.print("[yellow]提示: 使用kubectl运行DNS测试Pod[/yellow]")
            
            elif args.net_action == "policy":
                policies = client.check_network_policies(ns)
                if policies:
                    table = Table(title="网络策略")
                    table.add_column("名称", style="green")
                    table.add_column("策略类型")
                    for policy in policies:
                        types = ','.join(policy.get('policy_types', []))
                        table.add_row(policy['name'], types)
                    console.print(table)
                else:
                    console.print("[yellow]未配置网络策略[/yellow]")
        
        elif args.command == "resource":
            if args.res_action == "node":
                nodes = client.check_node_resources()
                print_nodes(nodes)
            
            elif args.res_action == "pressure":
                pressures = client.check_resource_pressure()
                print_pressures(pressures)
            
            elif args.res_action == "capacity":
                console.print("[yellow]容量分析功能需要metrics-server[/yellow]")
        
        elif args.command == "storage":
            if args.storage_action in ["pv", "pvc"]:
                pvs, pvcs = client.check_storage(ns)
                print_storage(pvs, pvcs)
        
        elif args.command == "cluster":
            if args.cluster_action == "health":
                health = client.check_cluster_health()
                print_cluster_health(health)
            
            elif args.cluster_action == "nodes":
                nodes = client.check_node_resources()
                print_nodes(nodes)
        
        elif args.command == "logs":
            if args.logs_action == "analyze":
                analysis = client.analyze_logs(args.name, ns, args.since, args.tail)
                print_log_analysis(analysis)
            
            elif args.logs_action == "errors":
                console.print("[yellow]聚合多Pod错误日志需要指定Pod名称或实现额外逻辑[/yellow]")
        
        return 0
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
        return 130
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
