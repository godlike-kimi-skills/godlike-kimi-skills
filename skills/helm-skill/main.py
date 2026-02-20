#!/usr/bin/env python3
"""
Helm Skill - Helm包管理器工具

功能：Helm Chart管理。Use when managing Helm charts, deploying applications with Helm, 
or when user mentions 'helm', 'chart', 'release', 'helm repo'。
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
class ReleaseInfo:
    """Release信息数据类"""
    name: str
    namespace: str
    revision: str
    updated: str
    status: str
    chart: str
    app_version: str


@dataclass
class RepoInfo:
    """仓库信息数据类"""
    name: str
    url: str


@dataclass
class ChartInfo:
    """Chart信息数据类"""
    name: str
    version: str
    app_version: str
    description: str


class HelmClient:
    """Helm客户端封装"""
    
    def __init__(self, kubeconfig: Optional[str] = None,
                 namespace: str = "default",
                 helm_path: Optional[str] = None):
        self.kubeconfig = kubeconfig
        self.namespace = namespace
        self.helm_path = helm_path or "helm"
    
    def _build_cmd(self, args: List[str]) -> List[str]:
        """构建Helm命令"""
        cmd = [self.helm_path]
        
        if self.kubeconfig:
            cmd.extend(["--kubeconfig", self.kubeconfig])
        
        cmd.extend(args)
        return cmd
    
    def _run_command(self, cmd: List[str], capture_output: bool = True,
                    timeout: int = 60) -> tuple:
        """执行Helm命令"""
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
    
    def list_repos(self) -> List[RepoInfo]:
        """列出仓库"""
        returncode, stdout, stderr = self._run_command(["repo", "list", "--output", "json"])
        
        if returncode != 0:
            if "no repositories configured" in stderr.lower():
                return []
            console.print(f"[red]Error: {stderr}[/red]")
            return []
        
        try:
            repos = json.loads(stdout)
            return [RepoInfo(
                name=r.get('name', ''),
                url=r.get('url', '')
            ) for r in repos]
        except json.JSONDecodeError:
            return []
    
    def add_repo(self, name: str, url: str) -> bool:
        """添加仓库"""
        returncode, stdout, stderr = self._run_command(
            ["repo", "add", name, url]
        )
        if returncode == 0:
            console.print(f"[green]Repository {name} added successfully[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def remove_repo(self, name: str) -> bool:
        """删除仓库"""
        returncode, stdout, stderr = self._run_command(
            ["repo", "remove", name]
        )
        if returncode == 0:
            console.print(f"[green]Repository {name} removed successfully[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def update_repos(self) -> bool:
        """更新仓库"""
        returncode, stdout, stderr = self._run_command(
            ["repo", "update"],
            timeout=120
        )
        if returncode == 0:
            console.print(f"[green]{stdout}[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def search_repo(self, keyword: str) -> List[ChartInfo]:
        """搜索仓库"""
        returncode, stdout, stderr = self._run_command(
            ["search", "repo", keyword, "--output", "json"]
        )
        if returncode != 0:
            console.print(f"[red]Error: {stderr}[/red]")
            return []
        
        try:
            charts = json.loads(stdout)
            return [ChartInfo(
                name=c.get('name', ''),
                version=c.get('version', ''),
                app_version=c.get('app_version', ''),
                description=c.get('description', '')
            ) for c in charts]
        except json.JSONDecodeError:
            return []
    
    def search_hub(self, keyword: str) -> str:
        """搜索Helm Hub"""
        returncode, stdout, stderr = self._run_command(
            ["search", "hub", keyword],
            timeout=30
        )
        return stdout if returncode == 0 else stderr
    
    def list_releases(self, namespace: Optional[str] = None,
                     all_namespaces: bool = False) -> List[ReleaseInfo]:
        """列出Release"""
        cmd = ["list", "--output", "json"]
        
        if all_namespaces:
            cmd.append("--all-namespaces")
        elif namespace:
            cmd.extend(["--namespace", namespace])
        else:
            cmd.extend(["--namespace", self.namespace])
        
        returncode, stdout, stderr = self._run_command(cmd)
        
        if returncode != 0:
            console.print(f"[red]Error: {stderr}[/red]")
            return []
        
        try:
            releases = json.loads(stdout)
            return [ReleaseInfo(
                name=r.get('name', ''),
                namespace=r.get('namespace', ''),
                revision=str(r.get('revision', '')),
                updated=r.get('updated', ''),
                status=r.get('status', ''),
                chart=r.get('chart', ''),
                app_version=r.get('app_version', '')
            ) for r in releases]
        except json.JSONDecodeError:
            return []
    
    def release_status(self, name: str, namespace: Optional[str] = None) -> str:
        """查看Release状态"""
        ns = namespace or self.namespace
        returncode, stdout, stderr = self._run_command(
            ["status", name, "--namespace", ns]
        )
        return stdout if returncode == 0 else stderr
    
    def release_history(self, name: str, namespace: Optional[str] = None,
                       max_versions: int = 20) -> str:
        """查看Release历史"""
        ns = namespace or self.namespace
        returncode, stdout, stderr = self._run_command(
            ["history", name, "--namespace", ns, "--max", str(max_versions)]
        )
        return stdout if returncode == 0 else stderr
    
    def release_values(self, name: str, namespace: Optional[str] = None,
                      all_values: bool = False) -> str:
        """查看Release值"""
        ns = namespace or self.namespace
        cmd = ["get", "values", name, "--namespace", ns]
        if all_values:
            cmd.append("--all")
        
        returncode, stdout, stderr = self._run_command(cmd)
        return stdout if returncode == 0 else stderr
    
    def release_manifest(self, name: str, namespace: Optional[str] = None) -> str:
        """查看Release清单"""
        ns = namespace or self.namespace
        returncode, stdout, stderr = self._run_command(
            ["get", "manifest", name, "--namespace", ns]
        )
        return stdout if returncode == 0 else stderr
    
    def release_notes(self, name: str, namespace: Optional[str] = None) -> str:
        """查看Release notes"""
        ns = namespace or self.namespace
        returncode, stdout, stderr = self._run_command(
            ["get", "notes", name, "--namespace", ns]
        )
        return stdout if returncode == 0 else stderr
    
    def install(self, name: str, chart: str, namespace: Optional[str] = None,
                version: Optional[str] = None, values_files: Optional[List[str]] = None,
                set_values: Optional[List[str]] = None, dry_run: bool = False,
                wait: bool = False, timeout: Optional[str] = None,
                create_namespace: bool = False, generate_name: bool = False) -> bool:
        """安装Chart"""
        ns = namespace or self.namespace
        
        if generate_name:
            cmd = ["install", chart, "--generate-name", "--namespace", ns]
        else:
            cmd = ["install", name, chart, "--namespace", ns]
        
        if version:
            cmd.extend(["--version", version])
        if values_files:
            for f in values_files:
                cmd.extend(["-f", f])
        if set_values:
            for v in set_values:
                cmd.extend(["--set", v])
        if dry_run:
            cmd.append("--dry-run")
        if wait:
            cmd.append("--wait")
        if timeout:
            cmd.extend(["--timeout", timeout])
        if create_namespace:
            cmd.append("--create-namespace")
        
        returncode, stdout, stderr = self._run_command(cmd, capture_output=not dry_run)
        
        if dry_run:
            console.print(Panel(stdout or stderr, title="Dry Run Output"))
            return returncode == 0
        elif returncode == 0:
            console.print(f"[green]Release installed successfully[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def upgrade(self, name: str, chart: str, namespace: Optional[str] = None,
                version: Optional[str] = None, values_files: Optional[List[str]] = None,
                set_values: Optional[List[str]] = None, dry_run: bool = False,
                wait: bool = False, timeout: Optional[str] = None,
                install: bool = False, force: bool = False,
                reuse_values: bool = False) -> bool:
        """升级Release"""
        ns = namespace or self.namespace
        cmd = ["upgrade", name, chart, "--namespace", ns]
        
        if version:
            cmd.extend(["--version", version])
        if values_files:
            for f in values_files:
                cmd.extend(["-f", f])
        if set_values:
            for v in set_values:
                cmd.extend(["--set", v])
        if dry_run:
            cmd.append("--dry-run")
        if wait:
            cmd.append("--wait")
        if timeout:
            cmd.extend(["--timeout", timeout])
        if install:
            cmd.append("--install")
        if force:
            cmd.append("--force")
        if reuse_values:
            cmd.append("--reuse-values")
        
        returncode, stdout, stderr = self._run_command(cmd, capture_output=not dry_run)
        
        if dry_run:
            console.print(Panel(stdout or stderr, title="Dry Run Output"))
            return returncode == 0
        elif returncode == 0:
            console.print(f"[green]Release upgraded successfully[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def rollback(self, name: str, revision: int,
                namespace: Optional[str] = None, wait: bool = False) -> bool:
        """回滚Release"""
        ns = namespace or self.namespace
        cmd = ["rollback", name, str(revision), "--namespace", ns]
        
        if wait:
            cmd.append("--wait")
        
        returncode, stdout, stderr = self._run_command(cmd)
        if returncode == 0:
            console.print(f"[green]{stdout}[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def uninstall(self, names: List[str], namespace: Optional[str] = None,
                 keep_history: bool = False) -> bool:
        """卸载Release"""
        ns = namespace or self.namespace
        cmd = ["uninstall"] + names
        cmd.extend(["--namespace", ns])
        
        if keep_history:
            cmd.append("--keep-history")
        
        returncode, stdout, stderr = self._run_command(cmd)
        if returncode == 0:
            console.print(f"[green]{stdout}[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def create_chart(self, name: str) -> bool:
        """创建新Chart"""
        returncode, stdout, stderr = self._run_command(
            ["create", name]
        )
        if returncode == 0:
            console.print(f"[green]Chart {name} created successfully[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def package_chart(self, path: str, destination: Optional[str] = None,
                     sign: bool = False, key: Optional[str] = None) -> bool:
        """打包Chart"""
        cmd = ["package", path]
        
        if destination:
            cmd.extend(["--destination", destination])
        if sign:
            cmd.append("--sign")
        if key:
            cmd.extend(["--key", key])
        
        returncode, stdout, stderr = self._run_command(cmd)
        if returncode == 0:
            console.print(f"[green]{stdout}[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def lint_chart(self, path: str, strict: bool = False) -> bool:
        """验证Chart"""
        cmd = ["lint", path]
        
        if strict:
            cmd.append("--strict")
        
        returncode, stdout, stderr = self._run_command(cmd)
        console.print(stdout)
        if returncode == 0:
            console.print("[green]Chart is valid[/green]")
            return True
        else:
            console.print("[red]Chart has issues[/red]")
            return False
    
    def template_chart(self, name: str, chart: str,
                      namespace: Optional[str] = None,
                      values_files: Optional[List[str]] = None,
                      set_values: Optional[List[str]] = None,
                      show_only: Optional[List[str]] = None) -> str:
        """模板渲染"""
        ns = namespace or self.namespace
        cmd = ["template", name, chart, "--namespace", ns]
        
        if values_files:
            for f in values_files:
                cmd.extend(["-f", f])
        if set_values:
            for v in set_values:
                cmd.extend(["--set", v])
        if show_only:
            for s in show_only:
                cmd.extend(["--show-only", s])
        
        returncode, stdout, stderr = self._run_command(cmd)
        return stdout if returncode == 0 else stderr
    
    def show_chart_info(self, chart: str, info_type: str = "all") -> str:
        """显示Chart信息"""
        valid_types = ["all", "chart", "values", "readme"]
        if info_type not in valid_types:
            info_type = "all"
        
        returncode, stdout, stderr = self._run_command(
            ["show", info_type, chart]
        )
        return stdout if returncode == 0 else stderr
    
    def dependency_update(self, path: str) -> bool:
        """更新依赖"""
        returncode, stdout, stderr = self._run_command(
            ["dependency", "update", path],
            timeout=120
        )
        if returncode == 0:
            console.print(f"[green]{stdout}[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def dependency_build(self, path: str) -> bool:
        """构建依赖"""
        returncode, stdout, stderr = self._run_command(
            ["dependency", "build", path],
            timeout=120
        )
        if returncode == 0:
            console.print(f"[green]{stdout}[/green]")
            return True
        else:
            console.print(f"[red]Error: {stderr}[/red]")
            return False
    
    def dependency_list(self, path: str) -> str:
        """列出依赖"""
        returncode, stdout, stderr = self._run_command(
            ["dependency", "list", path]
        )
        return stdout if returncode == 0 else stderr


def print_releases(releases: List[ReleaseInfo], output_format: str = "table"):
    """打印Release列表"""
    if not releases:
        console.print("[yellow]No releases found[/yellow]")
        return
    
    if output_format == "json":
        console.print(json.dumps([asdict(r) for r in releases], indent=2))
    elif output_format == "yaml":
        console.print(yaml.dump([asdict(r) for r in releases], default_flow_style=False))
    else:
        table = Table(title="Helm Releases")
        table.add_column("Name", style="green")
        table.add_column("Namespace", style="cyan")
        table.add_column("Revision")
        table.add_column("Updated", style="blue")
        table.add_column("Status", style="yellow")
        table.add_column("Chart")
        table.add_column("App Version")
        
        for r in releases:
            status_color = "green" if r.status == "deployed" else "red" if "failed" in r.status.lower() else "yellow"
            table.add_row(
                r.name, r.namespace, r.revision, r.updated,
                f"[{status_color}]{r.status}[/{status_color}]",
                r.chart, r.app_version
            )
        console.print(table)


def print_repos(repos: List[RepoInfo], output_format: str = "table"):
    """打印仓库列表"""
    if not repos:
        console.print("[yellow]No repositories configured[/yellow]")
        return
    
    if output_format == "json":
        console.print(json.dumps([asdict(r) for r in repos], indent=2))
    elif output_format == "yaml":
        console.print(yaml.dump([asdict(r) for r in repos], default_flow_style=False))
    else:
        table = Table(title="Helm Repositories")
        table.add_column("Name", style="green")
        table.add_column("URL", style="blue")
        
        for r in repos:
            table.add_row(r.name, r.url)
        console.print(table)


def print_charts(charts: List[ChartInfo], output_format: str = "table"):
    """打印Chart列表"""
    if not charts:
        console.print("[yellow]No charts found[/yellow]")
        return
    
    if output_format == "json":
        console.print(json.dumps([asdict(c) for c in charts], indent=2))
    elif output_format == "yaml":
        console.print(yaml.dump([asdict(c) for c in charts], default_flow_style=False))
    else:
        table = Table(title="Helm Charts")
        table.add_column("Name", style="green")
        table.add_column("Version", style="cyan")
        table.add_column("App Version")
        table.add_column("Description")
        
        for c in charts:
            table.add_row(c.name, c.version, c.app_version, c.description)
        console.print(table)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Helm Skill - Helm包管理器工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--namespace", "-n", default="default", help="命名空间")
    parser.add_argument("--all-namespaces", "-A", action="store_true", help="所有命名空间")
    parser.add_argument("--output", "-o", choices=["table", "json", "yaml"], 
                       default="table", help="输出格式")
    parser.add_argument("--kubeconfig", help="kubeconfig文件路径")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # Repo命令
    repo_parser = subparsers.add_parser("repo", help="仓库管理")
    repo_subparsers = repo_parser.add_subparsers(dest="repo_action")
    
    repo_subparsers.add_parser("ls", help="列出仓库")
    
    repo_add = repo_subparsers.add_parser("add", help="添加仓库")
    repo_add.add_argument("name", help="仓库名称")
    repo_add.add_argument("url", help="仓库URL")
    
    repo_remove = repo_subparsers.add_parser("remove", help="删除仓库")
    repo_remove.add_argument("name", help="仓库名称")
    
    repo_subparsers.add_parser("update", help="更新仓库")
    
    # Search命令
    search_parser = subparsers.add_parser("search", help="搜索Chart")
    search_subparsers = search_parser.add_subparsers(dest="search_type")
    
    search_repo = search_subparsers.add_parser("repo", help="搜索仓库")
    search_repo.add_argument("keyword", help="搜索关键词")
    
    search_hub = search_subparsers.add_parser("hub", help="搜索Hub")
    search_hub.add_argument("keyword", help="搜索关键词")
    
    # Release命令
    release_parser = subparsers.add_parser("release", help="Release管理")
    release_subparsers = release_parser.add_subparsers(dest="release_action")
    
    release_subparsers.add_parser("ls", help="列出Release")
    
    release_status = release_subparsers.add_parser("status", help="Release状态")
    release_status.add_argument("name", help="Release名称")
    
    release_history = release_subparsers.add_parser("history", help="Release历史")
    release_history.add_argument("name", help="Release名称")
    release_history.add_argument("--max", type=int, default=20, help="最大版本数")
    
    release_values = release_subparsers.add_parser("values", help="Release值")
    release_values.add_argument("name", help="Release名称")
    release_values.add_argument("--all", action="store_true", help="显示所有值")
    
    release_manifest = release_subparsers.add_parser("get-manifest", help="Release清单")
    release_manifest.add_argument("name", help="Release名称")
    
    release_notes = release_subparsers.add_parser("get-notes", help="Release notes")
    release_notes.add_argument("name", help="Release名称")
    
    # Install命令
    install_parser = subparsers.add_parser("install", help="安装Chart")
    install_parser.add_argument("name", nargs="?", help="Release名称")
    install_parser.add_argument("chart", help="Chart名称或路径")
    install_parser.add_argument("--version", help="Chart版本")
    install_parser.add_argument("-f", "--values", action="append", help="Values文件")
    install_parser.add_argument("--set", action="append", help="设置值")
    install_parser.add_argument("--dry-run", action="store_true", help="模拟执行")
    install_parser.add_argument("--wait", action="store_true", help="等待就绪")
    install_parser.add_argument("--timeout", help="超时时间")
    install_parser.add_argument("--create-namespace", action="store_true", help="创建命名空间")
    install_parser.add_argument("--generate-name", action="store_true", help="生成名称")
    
    # Upgrade命令
    upgrade_parser = subparsers.add_parser("upgrade", help="升级Release")
    upgrade_parser.add_argument("name", help="Release名称")
    upgrade_parser.add_argument("chart", help="Chart名称或路径")
    upgrade_parser.add_argument("--version", help="Chart版本")
    upgrade_parser.add_argument("-f", "--values", action="append", help="Values文件")
    upgrade_parser.add_argument("--set", action="append", help="设置值")
    upgrade_parser.add_argument("--dry-run", action="store_true", help="模拟执行")
    upgrade_parser.add_argument("--wait", action="store_true", help="等待就绪")
    upgrade_parser.add_argument("--timeout", help="超时时间")
    upgrade_parser.add_argument("--install", action="store_true", help="如果不存在则安装")
    upgrade_parser.add_argument("--force", action="store_true", help="强制升级")
    upgrade_parser.add_argument("--reuse-values", action="store_true", help="重用值")
    
    # Rollback命令
    rollback_parser = subparsers.add_parser("rollback", help="回滚Release")
    rollback_parser.add_argument("name", help="Release名称")
    rollback_parser.add_argument("revision", type=int, help="回滚到版本")
    rollback_parser.add_argument("--wait", action="store_true", help="等待就绪")
    
    # Uninstall命令
    uninstall_parser = subparsers.add_parser("uninstall", help="卸载Release")
    uninstall_parser.add_argument("names", nargs="+", help="Release名称")
    uninstall_parser.add_argument("--keep-history", action="store_true", help="保留历史")
    
    # Create命令
    create_parser = subparsers.add_parser("create", help="创建Chart")
    create_parser.add_argument("name", help="Chart名称")
    
    # Package命令
    package_parser = subparsers.add_parser("package", help="打包Chart")
    package_parser.add_argument("path", help="Chart路径")
    package_parser.add_argument("-d", "--destination", help="输出目录")
    package_parser.add_argument("--sign", action="store_true", help="签名")
    package_parser.add_argument("--key", help="签名密钥")
    
    # Lint命令
    lint_parser = subparsers.add_parser("lint", help="验证Chart")
    lint_parser.add_argument("path", help="Chart路径")
    lint_parser.add_argument("--strict", action="store_true", help="严格模式")
    
    # Template命令
    template_parser = subparsers.add_parser("template", help="模板渲染")
    template_parser.add_argument("name", help="Release名称")
    template_parser.add_argument("chart", help="Chart路径")
    template_parser.add_argument("-f", "--values", action="append", help="Values文件")
    template_parser.add_argument("--set", action="append", help="设置值")
    template_parser.add_argument("--show-only", action="append", help="只显示指定文件")
    
    # Show命令
    show_parser = subparsers.add_parser("show", help="显示Chart信息")
    show_parser.add_argument("info_type", choices=["all", "chart", "values", "readme"],
                            default="all", help="信息类型")
    show_parser.add_argument("chart", help="Chart名称或路径")
    
    # Dependency命令
    dep_parser = subparsers.add_parser("dependency", help="依赖管理")
    dep_subparsers = dep_parser.add_subparsers(dest="dep_action")
    
    dep_update = dep_subparsers.add_parser("update", help="更新依赖")
    dep_update.add_argument("path", help="Chart路径")
    
    dep_build = dep_subparsers.add_parser("build", help="构建依赖")
    dep_build.add_argument("path", help="Chart路径")
    
    dep_list = dep_subparsers.add_parser("list", help="列出依赖")
    dep_list.add_argument("path", help="Chart路径")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    helm = HelmClient(
        kubeconfig=args.kubeconfig,
        namespace=args.namespace
    )
    
    ns = None if args.all_namespaces else args.namespace
    
    try:
        if args.command == "repo":
            if args.repo_action == "ls":
                repos = helm.list_repos()
                print_repos(repos, args.output)
            elif args.repo_action == "add":
                helm.add_repo(args.name, args.url)
            elif args.repo_action == "remove":
                helm.remove_repo(args.name)
            elif args.repo_action == "update":
                helm.update_repos()
        
        elif args.command == "search":
            if args.search_type == "repo":
                charts = helm.search_repo(args.keyword)
                print_charts(charts, args.output)
            elif args.search_type == "hub":
                console.print(helm.search_hub(args.keyword))
        
        elif args.command == "release":
            if args.release_action == "ls":
                releases = helm.list_releases(ns, args.all_namespaces)
                print_releases(releases, args.output)
            elif args.release_action == "status":
                console.print(helm.release_status(args.name, ns))
            elif args.release_action == "history":
                console.print(helm.release_history(args.name, ns, args.max))
            elif args.release_action == "values":
                console.print(helm.release_values(args.name, ns, args.all))
            elif args.release_action == "get-manifest":
                console.print(helm.release_manifest(args.name, ns))
            elif args.release_action == "get-notes":
                console.print(helm.release_notes(args.name, ns))
        
        elif args.command == "install":
            if args.generate_name:
                helm.install(
                    None, args.chart, ns,
                    version=args.version,
                    values_files=args.values,
                    set_values=args.set,
                    dry_run=args.dry_run,
                    wait=args.wait,
                    timeout=args.timeout,
                    create_namespace=args.create_namespace,
                    generate_name=True
                )
            else:
                helm.install(
                    args.name, args.chart, ns,
                    version=args.version,
                    values_files=args.values,
                    set_values=args.set,
                    dry_run=args.dry_run,
                    wait=args.wait,
                    timeout=args.timeout,
                    create_namespace=args.create_namespace
                )
        
        elif args.command == "upgrade":
            helm.upgrade(
                args.name, args.chart, ns,
                version=args.version,
                values_files=args.values,
                set_values=args.set,
                dry_run=args.dry_run,
                wait=args.wait,
                timeout=args.timeout,
                install=args.install,
                force=args.force,
                reuse_values=args.reuse_values
            )
        
        elif args.command == "rollback":
            helm.rollback(args.name, args.revision, ns, args.wait)
        
        elif args.command == "uninstall":
            helm.uninstall(args.names, ns, args.keep_history)
        
        elif args.command == "create":
            helm.create_chart(args.name)
        
        elif args.command == "package":
            helm.package_chart(args.path, args.destination, args.sign, args.key)
        
        elif args.command == "lint":
            helm.lint_chart(args.path, args.strict)
        
        elif args.command == "template":
            output = helm.template_chart(
                args.name, args.chart, ns,
                args.values, args.set, args.show_only
            )
            console.print(output)
        
        elif args.command == "show":
            console.print(helm.show_chart_info(args.chart, args.info_type))
        
        elif args.command == "dependency":
            if args.dep_action == "update":
                helm.dependency_update(args.path)
            elif args.dep_action == "build":
                helm.dependency_build(args.path)
            elif args.dep_action == "list":
                console.print(helm.dependency_list(args.path))
        
        return 0
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
        return 130
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
