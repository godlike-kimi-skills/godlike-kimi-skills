#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare Wrangler Skill - CLI封装工具
简化Cloudflare Workers开发与部署流程
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import yaml
import toml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


class WranglerAction(Enum):
    """支持的Wrangler操作类型"""
    DEPLOY = "deploy"
    DEV = "dev"
    KV = "kv"
    D1 = "d1"
    R2 = "r2"
    TAIL = "tail"
    INIT = "init"
    CONFIG = "config"
    STATUS = "status"
    LOGS = "logs"


@dataclass
class WranglerConfig:
    """Wrangler配置类"""
    name: str = ""
    account_id: str = ""
    compatibility_date: str = ""
    main: str = "src/index.js"
    
    def to_toml(self) -> str:
        """转换为TOML格式"""
        data = {
            "name": self.name,
            "account_id": self.account_id,
            "compatibility_date": self.compatibility_date or "2024-01-01",
            "main": self.main
        }
        return toml.dumps(data)
    
    @classmethod
    def from_file(cls, path: str) -> "WranglerConfig":
        """从文件加载配置"""
        path = Path(path)
        if not path.exists():
            return cls()
        
        content = path.read_text(encoding="utf-8")
        
        if path.suffix == ".toml":
            data = toml.loads(content)
        elif path.suffix in [".yaml", ".yml"]:
            data = yaml.safe_load(content)
        else:
            data = {}
        
        return cls(
            name=data.get("name", ""),
            account_id=data.get("account_id", ""),
            compatibility_date=data.get("compatibility_date", ""),
            main=data.get("main", "src/index.js")
        )


class WranglerSkill:
    """Wrangler Skill主类"""
    
    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.wrangler_toml = self.project_path / "wrangler.toml"
        self.config = WranglerConfig.from_file(self.wrangler_toml)
        self.dry_run = False
    
    def _run_wrangler(self, args: List[str], capture: bool = False) -> Tuple[int, str, str]:
        """
        执行wrangler命令
        
        Args:
            args: wrangler命令参数
            capture: 是否捕获输出
            
        Returns:
            (returncode, stdout, stderr)
        """
        cmd = ["wrangler"] + args
        
        if self.dry_run:
            console.print(f"[yellow][DRY RUN] {' '.join(cmd)}[/yellow]")
            return 0, "", ""
        
        console.print(f"[dim]执行: {' '.join(cmd)}[/dim]")
        
        try:
            if capture:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=self.project_path
                )
                return result.returncode, result.stdout, result.stderr
            else:
                result = subprocess.run(cmd, cwd=self.project_path)
                return result.returncode, "", ""
        except FileNotFoundError:
            console.print("[red]错误: 未找到wrangler命令，请先安装: npm install -g wrangler[/red]")
            return 1, "", "wrangler not found"
    
    def _check_project(self) -> bool:
        """检查项目配置是否有效"""
        if not self.wrangler_toml.exists():
            console.print(f"[red]错误: 未找到wrangler.toml，请先运行 init 命令[/red]")
            return False
        return True
    
    def init(self, name: Optional[str] = None, template: str = "worker") -> bool:
        """
        初始化新项目
        
        Args:
            name: 项目名称
            template: 项目模板
            
        Returns:
            是否成功
        """
        args = ["init"]
        if name:
            args.append(name)
        if template:
            args.extend(["--template", template])
        
        code, stdout, stderr = self._run_wrangler(args)
        
        if code == 0:
            console.print(f"[green]✓ 项目初始化成功[/green]")
            return True
        else:
            console.print(f"[red]✗ 初始化失败: {stderr}[/red]")
            return False
    
    def deploy(self, env: Optional[str] = None, dry_run: bool = False) -> bool:
        """
        部署Worker
        
        Args:
            env: 环境名称
            dry_run: 是否模拟运行
            
        Returns:
            是否成功
        """
        if not self._check_project():
            return False
        
        args = ["deploy"]
        if env:
            args.extend(["--env", env])
        if dry_run:
            args.append("--dry-run")
        
        code, _, stderr = self._run_wrangler(args)
        
        if code == 0:
            console.print(f"[green]✓ 部署成功[/green]")
            return True
        else:
            console.print(f"[red]✗ 部署失败: {stderr}[/red]")
            return False
    
    def dev(self, port: Optional[int] = None, remote: bool = False) -> bool:
        """
        启动开发服务器
        
        Args:
            port: 端口号
            remote: 是否使用远程资源
            
        Returns:
            是否成功
        """
        if not self._check_project():
            return False
        
        args = ["dev"]
        if port:
            args.extend(["--port", str(port)])
        if remote:
            args.append("--remote")
        
        code, _, _ = self._run_wrangler(args)
        return code == 0
    
    def tail(self, follow: bool = False, format_json: bool = False) -> bool:
        """
        查看实时日志
        
        Args:
            follow: 是否持续跟踪
            format_json: 是否格式化JSON
            
        Returns:
            是否成功
        """
        if not self._check_project():
            return False
        
        args = ["tail"]
        if format_json:
            args.append("--format-json")
        
        code, _, _ = self._run_wrangler(args)
        return code == 0
    
    # ========== KV 操作 ==========
    
    def kv_list(self, namespace: str) -> bool:
        """列出KV命名空间中的键"""
        args = ["kv", "key", "list", "--namespace-id", namespace]
        code, stdout, _ = self._run_wrangler(args, capture=True)
        
        if code == 0:
            try:
                keys = json.loads(stdout)
                table = Table(title=f"KV Keys - {namespace}")
                table.add_column("Name", style="cyan")
                table.add_column("Expiration", style="dim")
                
                for key in keys:
                    table.add_row(
                        key.get("name", ""),
                        str(key.get("expiration", "-"))
                    )
                console.print(table)
                return True
            except json.JSONDecodeError:
                console.print(stdout)
                return True
        return False
    
    def kv_get(self, namespace: str, key: str) -> bool:
        """获取KV值"""
        args = ["kv", "key", "get", key, "--namespace-id", namespace]
        code, stdout, _ = self._run_wrangler(args, capture=True)
        
        if code == 0:
            console.print(Panel(stdout, title=f"KV: {key}"))
            return True
        return False
    
    def kv_put(self, namespace: str, key: str, value: str, file: Optional[str] = None) -> bool:
        """设置KV值"""
        args = ["kv", "key", "put", key, "--namespace-id", namespace]
        
        if file:
            args.extend(["--path", file])
        else:
            args.append(value)
        
        code, _, _ = self._run_wrangler(args)
        
        if code == 0:
            console.print(f"[green]✓ KV键 {key} 设置成功[/green]")
            return True
        return False
    
    def kv_delete(self, namespace: str, key: str) -> bool:
        """删除KV键"""
        args = ["kv", "key", "delete", key, "--namespace-id", namespace]
        code, _, _ = self._run_wrangler(args)
        
        if code == 0:
            console.print(f"[green]✓ KV键 {key} 删除成功[/green]")
            return True
        return False
    
    def kv_namespace_list(self) -> bool:
        """列出KV命名空间"""
        args = ["kv", "namespace", "list"]
        code, stdout, _ = self._run_wrangler(args, capture=True)
        
        if code == 0:
            try:
                namespaces = json.loads(stdout)
                table = Table(title="KV Namespaces")
                table.add_column("ID", style="dim")
                table.add_column("Title", style="cyan")
                
                for ns in namespaces:
                    table.add_row(
                        ns.get("id", "")[:20] + "...",
                        ns.get("title", "")
                    )
                console.print(table)
                return True
            except json.JSONDecodeError:
                console.print(stdout)
                return True
        return False
    
    # ========== D1 操作 ==========
    
    def d1_list(self) -> bool:
        """列出D1数据库"""
        args = ["d1", "list"]
        code, stdout, _ = self._run_wrangler(args, capture=True)
        
        if code == 0:
            try:
                databases = json.loads(stdout)
                table = Table(title="D1 Databases")
                table.add_column("UUID", style="dim")
                table.add_column("Name", style="cyan")
                table.add_column("Version", style="yellow")
                
                for db in databases:
                    table.add_row(
                        db.get("uuid", "")[:20] + "...",
                        db.get("name", ""),
                        str(db.get("version", ""))
                    )
                console.print(table)
                return True
            except json.JSONDecodeError:
                console.print(stdout)
                return True
        return False
    
    def d1_query(self, database: str, query: str) -> bool:
        """执行D1查询"""
        args = ["d1", "execute", database, "--command", query]
        code, stdout, _ = self._run_wrangler(args, capture=True)
        
        if code == 0:
            console.print(Panel(stdout, title="Query Result"))
            return True
        return False
    
    def d1_create(self, name: str) -> bool:
        """创建D1数据库"""
        args = ["d1", "create", name]
        code, _, _ = self._run_wrangler(args)
        
        if code == 0:
            console.print(f"[green]✓ D1数据库 {name} 创建成功[/green]")
            return True
        return False
    
    # ========== R2 操作 ==========
    
    def r2_list_buckets(self) -> bool:
        """列出R2存储桶"""
        args = ["r2", "bucket", "list"]
        code, stdout, _ = self._run_wrangler(args, capture=True)
        
        if code == 0:
            try:
                buckets = json.loads(stdout)
                table = Table(title="R2 Buckets")
                table.add_column("Name", style="cyan")
                table.add_column("Creation Date", style="dim")
                
                for bucket in buckets:
                    table.add_row(
                        bucket.get("name", ""),
                        bucket.get("creation_date", "")
                    )
                console.print(table)
                return True
            except json.JSONDecodeError:
                console.print(stdout)
                return True
        return False
    
    def r2_create_bucket(self, name: str) -> bool:
        """创建R2存储桶"""
        args = ["r2", "bucket", "create", name]
        code, _, _ = self._run_wrangler(args)
        
        if code == 0:
            console.print(f"[green]✓ R2存储桶 {name} 创建成功[/green]")
            return True
        return False
    
    def r2_delete_bucket(self, name: str) -> bool:
        """删除R2存储桶"""
        args = ["r2", "bucket", "delete", name]
        code, _, _ = self._run_wrangler(args)
        
        if code == 0:
            console.print(f"[green]✓ R2存储桶 {name} 删除成功[/green]")
            return True
        return False
    
    # ========== 配置管理 ==========
    
    def show_config(self) -> bool:
        """显示当前配置"""
        if not self._check_project():
            return False
        
        content = self.wrangler_toml.read_text(encoding="utf-8")
        syntax = Syntax(content, "toml", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="wrangler.toml"))
        return True
    
    def status(self) -> bool:
        """显示项目状态"""
        table = Table(title="Project Status")
        table.add_column("Item", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Project Path", str(self.project_path))
        table.add_row("Wrangler.toml Exists", "✓" if self.wrangler_toml.exists() else "✗")
        
        if self.wrangler_toml.exists():
            table.add_row("Worker Name", self.config.name or "N/A")
            table.add_row("Account ID", self.config.account_id or "N/A")
            table.add_row("Main Entry", self.config.main)
            table.add_row("Compatibility Date", self.config.compatibility_date or "N/A")
        
        console.print(table)
        return True


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="Cloudflare Wrangler Skill - 简化Workers开发部署",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 初始化新项目
  python main.py --action init --project my-worker

  # 部署到生产环境
  python main.py --action deploy --env production

  # 查看KV列表
  python main.py --action kv --command list --namespace <namespace-id>

  # 启动开发服务器
  python main.py --action dev

  # 查看实时日志
  python main.py --action tail --follow
        """
    )
    
    parser.add_argument("--action", "-a", required=True,
                       choices=[e.value for e in WranglerAction],
                       help="操作类型")
    parser.add_argument("--project", "-p", default=".",
                       help="项目路径 (默认: 当前目录)")
    parser.add_argument("--command", "-c",
                       help="子命令 (如: list, get, put, delete)")
    parser.add_argument("--env", "-e",
                       help="环境名称")
    parser.add_argument("--namespace", "-n",
                       help="KV/D1/R2 命名空间ID或数据库名称")
    parser.add_argument("--key", "-k",
                       help="KV键名")
    parser.add_argument("--value", "-v",
                       help="KV值")
    parser.add_argument("--file", "-f",
                       help="文件路径")
    parser.add_argument("--query", "-q",
                       help="SQL查询语句")
    parser.add_argument("--follow", action="store_true",
                       help="持续跟踪日志")
    parser.add_argument("--dry-run", action="store_true",
                       help="模拟运行")
    
    args = parser.parse_args()
    
    skill = WranglerSkill(args.project)
    skill.dry_run = args.dry_run
    
    action = WranglerAction(args.action)
    success = False
    
    try:
        if action == WranglerAction.INIT:
            success = skill.init(args.project)
        
        elif action == WranglerAction.DEPLOY:
            success = skill.deploy(args.env, args.dry_run)
        
        elif action == WranglerAction.DEV:
            success = skill.dev()
        
        elif action == WranglerAction.TAIL:
            success = skill.tail(args.follow)
        
        elif action == WranglerAction.CONFIG:
            success = skill.show_config()
        
        elif action == WranglerAction.STATUS:
            success = skill.status()
        
        elif action == WranglerAction.KV:
            cmd = args.command or "list"
            namespace = args.namespace
            
            if cmd == "list" and namespace:
                success = skill.kv_list(namespace)
            elif cmd == "get" and namespace and args.key:
                success = skill.kv_get(namespace, args.key)
            elif cmd == "put" and namespace and args.key:
                success = skill.kv_put(namespace, args.key, args.value or "", args.file)
            elif cmd == "delete" and namespace and args.key:
                success = skill.kv_delete(namespace, args.key)
            elif cmd == "namespace":
                success = skill.kv_namespace_list()
            else:
                console.print("[red]错误: KV操作需要指定namespace和相应的key/value[/red]")
        
        elif action == WranglerAction.D1:
            cmd = args.command or "list"
            
            if cmd == "list":
                success = skill.d1_list()
            elif cmd == "query" and args.namespace and args.query:
                success = skill.d1_query(args.namespace, args.query)
            elif cmd == "create" and args.namespace:
                success = skill.d1_create(args.namespace)
            else:
                console.print("[red]错误: D1操作需要指定database和相应的参数[/red]")
        
        elif action == WranglerAction.R2:
            cmd = args.command or "list"
            
            if cmd == "list":
                success = skill.r2_list_buckets()
            elif cmd == "create" and args.namespace:
                success = skill.r2_create_bucket(args.namespace)
            elif cmd == "delete" and args.namespace:
                success = skill.r2_delete_bucket(args.namespace)
            else:
                console.print("[red]错误: R2操作需要指定bucket名称[/red]")
        
        sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
