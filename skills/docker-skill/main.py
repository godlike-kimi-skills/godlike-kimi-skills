#!/usr/bin/env python3
"""
Docker Skill - Docker容器管理工具

功能：Docker容器管理。Use when managing Docker containers, deploying containers, 
or when user mentions 'docker', 'container', 'docker-compose', '镜像'。
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


console = Console()


@dataclass
class ContainerInfo:
    """容器信息数据类"""
    id: str
    name: str
    image: str
    status: str
    ports: str
    created: str
    command: str


@dataclass
class ImageInfo:
    """镜像信息数据类"""
    id: str
    repository: str
    tag: str
    size: str
    created: str


class DockerClient:
    """Docker客户端封装"""
    
    def __init__(self, host: Optional[str] = None, timeout: int = 60):
        self.host = host
        self.timeout = timeout
        self.base_cmd = ["docker"]
        if host:
            self.base_cmd.extend(["-H", host])
    
    def _run_command(self, cmd: List[str], capture_output: bool = True) -> tuple:
        """执行Docker命令"""
        full_cmd = self.base_cmd + cmd
        try:
            result = subprocess.run(
                full_cmd,
                capture_output=capture_output,
                text=True,
                timeout=self.timeout,
                encoding='utf-8'
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {self.timeout} seconds"
        except Exception as e:
            return -1, "", str(e)
    
    def list_containers(self, all_containers: bool = False) -> List[ContainerInfo]:
        """列出容器"""
        cmd = ["ps", "--format", "{{json .}}"]
        if all_containers:
            cmd.append("-a")
        
        returncode, stdout, stderr = self._run_command(cmd)
        
        if returncode != 0:
            console.print(f"[red]Error: {stderr}[/red]")
            return []
        
        containers = []
        for line in stdout.strip().split('\n'):
            if line:
                try:
                    data = json.loads(line)
                    containers.append(ContainerInfo(
                        id=data.get('ID', '')[:12],
                        name=data.get('Names', ''),
                        image=data.get('Image', ''),
                        status=data.get('Status', ''),
                        ports=data.get('Ports', ''),
                        created=data.get('CreatedAt', ''),
                        command=data.get('Command', '')
                    ))
                except json.JSONDecodeError:
                    continue
        return containers
    
    def start_container(self, container_id: str) -> bool:
        """启动容器"""
        returncode, stdout, stderr = self._run_command(["start", container_id])
        if returncode == 0:
            console.print(f"[green]Container {container_id} started successfully[/green]")
            return True
        else:
            console.print(f"[red]Failed to start container: {stderr}[/red]")
            return False
    
    def stop_container(self, container_id: str, timeout: int = 10) -> bool:
        """停止容器"""
        returncode, stdout, stderr = self._run_command(["stop", "-t", str(timeout), container_id])
        if returncode == 0:
            console.print(f"[green]Container {container_id} stopped successfully[/green]")
            return True
        else:
            console.print(f"[red]Failed to stop container: {stderr}[/red]")
            return False
    
    def restart_container(self, container_id: str, timeout: int = 10) -> bool:
        """重启容器"""
        returncode, stdout, stderr = self._run_command(["restart", "-t", str(timeout), container_id])
        if returncode == 0:
            console.print(f"[green]Container {container_id} restarted successfully[/green]")
            return True
        else:
            console.print(f"[red]Failed to restart container: {stderr}[/red]")
            return False
    
    def remove_container(self, container_id: str, force: bool = False) -> bool:
        """删除容器"""
        cmd = ["rm"]
        if force:
            cmd.append("-f")
        cmd.append(container_id)
        
        returncode, stdout, stderr = self._run_command(cmd)
        if returncode == 0:
            console.print(f"[green]Container {container_id} removed successfully[/green]")
            return True
        else:
            console.print(f"[red]Failed to remove container: {stderr}[/red]")
            return False
    
    def run_container(self, image: str, **kwargs) -> bool:
        """运行新容器"""
        cmd = ["run"]
        
        if kwargs.get('detach'):
            cmd.append("-d")
        if kwargs.get('name'):
            cmd.extend(["--name", kwargs['name']])
        if kwargs.get('ports'):
            for port in kwargs['ports']:
                cmd.extend(["-p", port])
        if kwargs.get('volumes'):
            for vol in kwargs['volumes']:
                cmd.extend(["-v", vol])
        if kwargs.get('env'):
            for env in kwargs['env']:
                cmd.extend(["-e", env])
        if kwargs.get('network'):
            cmd.extend(["--network", kwargs['network']])
        if kwargs.get('restart'):
            cmd.extend(["--restart", kwargs['restart']])
        
        cmd.append(image)
        
        if kwargs.get('command'):
            cmd.extend(kwargs['command'].split())
        
        returncode, stdout, stderr = self._run_command(cmd, capture_output=False)
        return returncode == 0
    
    def get_container_logs(self, container_id: str, tail: Optional[int] = None, 
                          follow: bool = False, since: Optional[str] = None) -> str:
        """获取容器日志"""
        cmd = ["logs"]
        if tail:
            cmd.extend(["--tail", str(tail)])
        if follow:
            cmd.append("-f")
        if since:
            cmd.extend(["--since", since])
        cmd.append(container_id)
        
        returncode, stdout, stderr = self._run_command(cmd, capture_output=not follow)
        if returncode == 0:
            return stdout
        else:
            return f"Error: {stderr}"
    
    def exec_in_container(self, container_id: str, command: str) -> bool:
        """在容器中执行命令"""
        cmd = ["exec", container_id] + command.split()
        returncode, stdout, stderr = self._run_command(cmd, capture_output=False)
        return returncode == 0
    
    def list_images(self) -> List[ImageInfo]:
        """列出镜像"""
        cmd = ["images", "--format", "{{json .}}"]
        returncode, stdout, stderr = self._run_command(cmd)
        
        if returncode != 0:
            console.print(f"[red]Error: {stderr}[/red]")
            return []
        
        images = []
        for line in stdout.strip().split('\n'):
            if line:
                try:
                    data = json.loads(line)
                    images.append(ImageInfo(
                        id=data.get('ID', '')[:12],
                        repository=data.get('Repository', ''),
                        tag=data.get('Tag', ''),
                        size=data.get('Size', ''),
                        created=data.get('CreatedAt', '')
                    ))
                except json.JSONDecodeError:
                    continue
        return images
    
    def pull_image(self, image: str) -> bool:
        """拉取镜像"""
        returncode, stdout, stderr = self._run_command(["pull", image], capture_output=False)
        if returncode == 0:
            console.print(f"[green]Image {image} pulled successfully[/green]")
            return True
        else:
            console.print(f"[red]Failed to pull image: {stderr}[/red]")
            return False
    
    def build_image(self, path: str, tag: Optional[str] = None, 
                    dockerfile: Optional[str] = None, no_cache: bool = False) -> bool:
        """构建镜像"""
        cmd = ["build"]
        if tag:
            cmd.extend(["-t", tag])
        if dockerfile:
            cmd.extend(["-f", dockerfile])
        if no_cache:
            cmd.append("--no-cache")
        cmd.append(path)
        
        returncode, stdout, stderr = self._run_command(cmd, capture_output=False)
        if returncode == 0:
            console.print(f"[green]Image built successfully[/green]")
            return True
        else:
            console.print(f"[red]Failed to build image: {stderr}[/red]")
            return False
    
    def remove_image(self, image_id: str, force: bool = False) -> bool:
        """删除镜像"""
        cmd = ["rmi"]
        if force:
            cmd.append("-f")
        cmd.append(image_id)
        
        returncode, stdout, stderr = self._run_command(cmd)
        if returncode == 0:
            console.print(f"[green]Image {image_id} removed successfully[/green]")
            return True
        else:
            console.print(f"[red]Failed to remove image: {stderr}[/red]")
            return False
    
    def prune_images(self) -> bool:
        """清理悬空镜像"""
        returncode, stdout, stderr = self._run_command(["image", "prune", "-f"])
        if returncode == 0:
            console.print(f"[green]{stdout}[/green]")
            return True
        return False


class ComposeManager:
    """Docker Compose管理器"""
    
    def __init__(self, compose_file: Optional[str] = None, project_name: Optional[str] = None):
        self.compose_file = compose_file or "docker-compose.yml"
        self.project_name = project_name
    
    def _build_cmd(self, action: str, *args) -> List[str]:
        """构建Compose命令"""
        cmd = ["docker", "compose"]
        if self.compose_file:
            cmd.extend(["-f", self.compose_file])
        if self.project_name:
            cmd.extend(["-p", self.project_name])
        cmd.append(action)
        cmd.extend(args)
        return cmd
    
    def _run_compose(self, cmd: List[str], capture_output: bool = True) -> tuple:
        """执行Compose命令"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                encoding='utf-8'
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)
    
    def up(self, detach: bool = False, build: bool = False, services: Optional[List[str]] = None) -> bool:
        """启动服务"""
        args = []
        if detach:
            args.append("-d")
        if build:
            args.append("--build")
        if services:
            args.extend(services)
        
        cmd = self._build_cmd("up", *args)
        returncode, stdout, stderr = self._run_compose(cmd, capture_output=False)
        
        if returncode == 0:
            console.print("[green]Services started successfully[/green]")
            return True
        else:
            console.print(f"[red]Failed to start services: {stderr}[/red]")
            return False
    
    def down(self, volumes: bool = False, remove_orphans: bool = False) -> bool:
        """停止并删除服务"""
        args = []
        if volumes:
            args.append("-v")
        if remove_orphans:
            args.append("--remove-orphans")
        
        cmd = self._build_cmd("down", *args)
        returncode, stdout, stderr = self._run_compose(cmd)
        
        if returncode == 0:
            console.print("[green]Services stopped and removed successfully[/green]")
            return True
        else:
            console.print(f"[red]Failed to stop services: {stderr}[/red]")
            return False
    
    def restart(self, services: Optional[List[str]] = None) -> bool:
        """重启服务"""
        cmd = self._build_cmd("restart", *(services or []))
        returncode, stdout, stderr = self._run_compose(cmd)
        
        if returncode == 0:
            console.print("[green]Services restarted successfully[/green]")
            return True
        else:
            console.print(f"[red]Failed to restart services: {stderr}[/red]")
            return False
    
    def logs(self, services: Optional[List[str]] = None, tail: Optional[int] = None,
             follow: bool = False) -> str:
        """查看服务日志"""
        args = []
        if tail:
            args.extend(["--tail", str(tail)])
        if follow:
            args.append("-f")
        if services:
            args.extend(services)
        
        cmd = self._build_cmd("logs", *args)
        returncode, stdout, stderr = self._run_compose(cmd, capture_output=not follow)
        
        if returncode == 0:
            return stdout
        else:
            return f"Error: {stderr}"
    
    def ps(self) -> List[Dict[str, Any]]:
        """列出服务状态"""
        cmd = self._build_cmd("ps", "--format", "json")
        returncode, stdout, stderr = self._run_compose(cmd)
        
        if returncode == 0 and stdout:
            try:
                return json.loads(stdout)
            except json.JSONDecodeError:
                pass
        return []
    
    def scale(self, services: Dict[str, int]) -> bool:
        """扩展服务"""
        scale_args = [f"{name}={count}" for name, count in services.items()]
        cmd = self._build_cmd("up", "-d", "--scale", *scale_args)
        returncode, stdout, stderr = self._run_compose(cmd)
        
        if returncode == 0:
            console.print("[green]Services scaled successfully[/green]")
            return True
        else:
            console.print(f"[red]Failed to scale services: {stderr}[/red]")
            return False


def print_containers(containers: List[ContainerInfo], output_format: str = "table"):
    """打印容器列表"""
    if not containers:
        console.print("[yellow]No containers found[/yellow]")
        return
    
    if output_format == "json":
        console.print(json.dumps([asdict(c) for c in containers], indent=2))
    elif output_format == "yaml":
        console.print(yaml.dump([asdict(c) for c in containers], default_flow_style=False))
    else:
        table = Table(title="Docker Containers")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Image", style="blue")
        table.add_column("Status", style="yellow")
        table.add_column("Ports")
        table.add_column("Created")
        
        for c in containers:
            status_color = "green" if "Up" in c.status else "red"
            table.add_row(
                c.id, c.name, c.image, 
                f"[{status_color}]{c.status}[/{status_color}]",
                c.ports, c.created
            )
        console.print(table)


def print_images(images: List[ImageInfo], output_format: str = "table"):
    """打印镜像列表"""
    if not images:
        console.print("[yellow]No images found[/yellow]")
        return
    
    if output_format == "json":
        console.print(json.dumps([asdict(i) for i in images], indent=2))
    elif output_format == "yaml":
        console.print(yaml.dump([asdict(i) for i in images], default_flow_style=False))
    else:
        table = Table(title="Docker Images")
        table.add_column("ID", style="cyan")
        table.add_column("Repository", style="green")
        table.add_column("Tag", style="blue")
        table.add_column("Size", style="yellow")
        table.add_column("Created")
        
        for i in images:
            table.add_row(i.id, i.repository, i.tag, i.size, i.created)
        console.print(table)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Docker Skill - Docker容器管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--format", choices=["table", "json", "yaml"], 
                       default="table", help="输出格式")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 容器命令
    container_parser = subparsers.add_parser("container", help="容器管理")
    container_subparsers = container_parser.add_subparsers(dest="container_action")
    
    # container ls
    ls_parser = container_subparsers.add_parser("ls", help="列出容器")
    ls_parser.add_argument("--all", "-a", action="store_true", help="显示所有容器")
    
    # container start/stop/restart/rm
    for action in ["start", "stop", "restart"]:
        p = container_subparsers.add_parser(action, help=f"{action}容器")
        p.add_argument("containers", nargs="+", help="容器ID或名称")
        if action == "stop":
            p.add_argument("--timeout", "-t", type=int, default=10, help="超时时间")
    
    rm_parser = container_subparsers.add_parser("rm", help="删除容器")
    rm_parser.add_argument("containers", nargs="+", help="容器ID或名称")
    rm_parser.add_argument("--force", "-f", action="store_true", help="强制删除")
    
    # container run
    run_parser = container_subparsers.add_parser("run", help="运行新容器")
    run_parser.add_argument("image", help="镜像名称")
    run_parser.add_argument("--name", help="容器名称")
    run_parser.add_argument("--port", "-p", action="append", help="端口映射")
    run_parser.add_argument("--volume", "-v", action="append", help="卷挂载")
    run_parser.add_argument("--env", "-e", action="append", help="环境变量")
    run_parser.add_argument("--network", help="网络")
    run_parser.add_argument("--detach", "-d", action="store_true", help="后台运行")
    run_parser.add_argument("--restart", help="重启策略")
    run_parser.add_argument("command", nargs="?", help="执行的命令")
    
    # container logs
    logs_parser = container_subparsers.add_parser("logs", help="查看容器日志")
    logs_parser.add_argument("container", help="容器ID或名称")
    logs_parser.add_argument("--tail", "-n", type=int, help="显示最后N行")
    logs_parser.add_argument("--follow", "-f", action="store_true", help="实时跟踪")
    
    # container exec
    exec_parser = container_subparsers.add_parser("exec", help="在容器中执行命令")
    exec_parser.add_argument("container", help="容器ID或名称")
    exec_parser.add_argument("command", help="要执行的命令")
    
    # 镜像命令
    image_parser = subparsers.add_parser("image", help="镜像管理")
    image_subparsers = image_parser.add_subparsers(dest="image_action")
    
    # image ls
    image_subparsers.add_parser("ls", help="列出镜像")
    
    # image pull
    pull_parser = image_subparsers.add_parser("pull", help="拉取镜像")
    pull_parser.add_argument("image", help="镜像名称")
    
    # image build
    build_parser = image_subparsers.add_parser("build", help="构建镜像")
    build_parser.add_argument("path", default=".", help="构建路径")
    build_parser.add_argument("--tag", "-t", help="镜像标签")
    build_parser.add_argument("--file", "-f", help="Dockerfile路径")
    build_parser.add_argument("--no-cache", action="store_true", help="不使用缓存")
    
    # image rm
    image_rm_parser = image_subparsers.add_parser("rm", help="删除镜像")
    image_rm_parser.add_argument("images", nargs="+", help="镜像ID或名称")
    image_rm_parser.add_argument("--force", "-f", action="store_true", help="强制删除")
    
    # image prune
    image_subparsers.add_parser("prune", help="清理悬空镜像")
    
    # Compose命令
    compose_parser = subparsers.add_parser("compose", help="Docker Compose操作")
    compose_parser.add_argument("--file", "-f", help="Compose文件路径")
    compose_parser.add_argument("--project-name", "-p", help="项目名称")
    
    compose_subparsers = compose_parser.add_subparsers(dest="compose_action")
    
    # compose up
    up_parser = compose_subparsers.add_parser("up", help="启动服务")
    up_parser.add_argument("--detach", "-d", action="store_true", help="后台运行")
    up_parser.add_argument("--build", action="store_true", help="重新构建")
    up_parser.add_argument("services", nargs="*", help="服务名称")
    
    # compose down
    down_parser = compose_subparsers.add_parser("down", help="停止服务")
    down_parser.add_argument("--volumes", "-v", action="store_true", help="删除卷")
    down_parser.add_argument("--remove-orphans", action="store_true", help="删除孤儿容器")
    
    # compose restart
    restart_parser = compose_subparsers.add_parser("restart", help="重启服务")
    restart_parser.add_argument("services", nargs="*", help="服务名称")
    
    # compose logs
    compose_logs_parser = compose_subparsers.add_parser("logs", help="查看日志")
    compose_logs_parser.add_argument("--tail", "-n", type=int, help="显示最后N行")
    compose_logs_parser.add_argument("--follow", "-f", action="store_true", help="实时跟踪")
    compose_logs_parser.add_argument("services", nargs="*", help="服务名称")
    
    # compose ps
    compose_subparsers.add_parser("ps", help="查看服务状态")
    
    # compose scale
    scale_parser = compose_subparsers.add_parser("scale", help="扩展服务")
    scale_parser.add_argument("services", nargs="+", help="服务=数量")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    docker = DockerClient()
    
    try:
        if args.command == "container":
            if args.container_action == "ls":
                containers = docker.list_containers(all_containers=args.all)
                print_containers(containers, args.format)
            
            elif args.container_action in ["start", "stop", "restart"]:
                for c in args.containers:
                    if args.container_action == "start":
                        docker.start_container(c)
                    elif args.container_action == "stop":
                        docker.stop_container(c, args.timeout)
                    else:
                        docker.restart_container(c, args.timeout)
            
            elif args.container_action == "rm":
                for c in args.containers:
                    docker.remove_container(c, args.force)
            
            elif args.container_action == "run":
                docker.run_container(
                    args.image,
                    name=args.name,
                    ports=args.port,
                    volumes=args.volume,
                    env=args.env,
                    network=args.network,
                    detach=args.detach,
                    restart=args.restart,
                    command=args.command
                )
            
            elif args.container_action == "logs":
                logs = docker.get_container_logs(
                    args.container, 
                    tail=args.tail, 
                    follow=args.follow
                )
                if not args.follow:
                    console.print(logs)
            
            elif args.container_action == "exec":
                docker.exec_in_container(args.container, args.command)
        
        elif args.command == "image":
            if args.image_action == "ls":
                images = docker.list_images()
                print_images(images, args.format)
            
            elif args.image_action == "pull":
                docker.pull_image(args.image)
            
            elif args.image_action == "build":
                docker.build_image(
                    args.path,
                    tag=args.tag,
                    dockerfile=args.file,
                    no_cache=args.no_cache
                )
            
            elif args.image_action == "rm":
                for img in args.images:
                    docker.remove_image(img, args.force)
            
            elif args.image_action == "prune":
                docker.prune_images()
        
        elif args.command == "compose":
            compose = ComposeManager(
                compose_file=args.file,
                project_name=args.project_name
            )
            
            if args.compose_action == "up":
                compose.up(
                    detach=args.detach,
                    build=args.build,
                    services=args.services
                )
            
            elif args.compose_action == "down":
                compose.down(
                    volumes=args.volumes,
                    remove_orphans=args.remove_orphans
                )
            
            elif args.compose_action == "restart":
                compose.restart(args.services)
            
            elif args.compose_action == "logs":
                logs = compose.logs(
                    services=args.services,
                    tail=args.tail,
                    follow=args.follow
                )
                if not args.follow:
                    console.print(logs)
            
            elif args.compose_action == "ps":
                services = compose.ps()
                if services:
                    console.print(services)
                else:
                    console.print("[yellow]No services running[/yellow]")
            
            elif args.compose_action == "scale":
                scale_map = {}
                for s in args.services:
                    if "=" in s:
                        name, count = s.split("=", 1)
                        scale_map[name] = int(count)
                compose.scale(scale_map)
        
        return 0
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
        return 130
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
