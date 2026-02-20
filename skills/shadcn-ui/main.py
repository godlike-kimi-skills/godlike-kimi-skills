#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shadcn-ui Skill - shadcn/ui 组件库集成工具
简化 shadcn/ui 的使用，快速添加和管理组件
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict

import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@dataclass
class ShadcnConfig:
    """shadcn/ui 配置"""
    project_path: str = "."
    base_color: str = "slate"
    css_framework: str = "tailwind"
    base_url: str = "https://ui.shadcn.com"
    components_path: str = "@/components/ui"
    utils_path: str = "@/lib/utils"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_file(cls, path: str = "components.json") -> "ShadcnConfig":
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls(
                project_path=os.path.dirname(path) or ".",
                base_color=data.get('baseColor', 'slate'),
                css_framework=data.get('framework', 'tailwind'),
                components_path=data.get('aliases', {}).get('components', '@/components/ui'),
                utils_path=data.get('aliases', {}).get('utils', '@/lib/utils')
            )
        except FileNotFoundError:
            return cls()


class ShadcnUI:
    """shadcn/ui 管理器"""
    
    POPULAR_COMPONENTS = [
        "accordion", "alert", "alert-dialog", "aspect-ratio", "avatar", "badge",
        "breadcrumb", "button", "calendar", "card", "carousel", "chart", "checkbox",
        "collapsible", "combobox", "command", "context-menu", "dialog", "drawer",
        "dropdown-menu", "form", "hover-card", "input", "input-otp", "label",
        "menubar", "navigation-menu", "pagination", "popover", "progress",
        "radio-group", "resizable", "scroll-area", "select", "separator", "sheet",
        "skeleton", "slider", "sonner", "switch", "table", "tabs", "textarea",
        "toast", "toggle", "toggle-group", "tooltip"
    ]
    
    def __init__(self, config: ShadcnConfig):
        self.config = config
        self.project_path = Path(config.project_path).resolve()
        self.components_json = self.project_path / "components.json"
    
    def _run_command(self, cmd: List[str], cwd: Optional[str] = None, 
                     check: bool = True) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(cmd, cwd=cwd or str(self.project_path),
                capture_output=True, text=True, encoding='utf-8', check=check)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]命令失败: {' '.join(cmd)}[/red]")
            console.print(f"[red]错误: {e.stderr}[/red]")
            raise
    
    def _check_npx(self) -> bool:
        try:
            return self._run_command(["npx", "--version"], check=False).returncode == 0
        except FileNotFoundError:
            return False
    
    def _is_shadcn_initialized(self) -> bool:
        return self.components_json.exists()
    
    def _get_components_dir(self) -> Path:
        for path in ["app/components/ui", "components/ui", "src/components/ui"]:
            full_path = self.project_path / path
            if full_path.exists():
                return full_path
        return self.project_path / "components" / "ui"
    
    def _get_installed_components(self) -> List[str]:
        components_dir = self._get_components_dir()
        if not components_dir.exists():
            return []
        return [f.stem for f in components_dir.glob("*.tsx") if f.stem in self.POPULAR_COMPONENTS]
    
    def init(self, yes: bool = False, base_color: Optional[str] = None) -> bool:
        console.print(Panel.fit("[bold blue]初始化 shadcn/ui[/bold blue]"))
        if not self._check_npx():
            console.print("[red]错误: 需要 Node.js 和 npx[/red]")
            return False
        if self._is_shadcn_initialized():
            console.print("[yellow]项目已初始化 shadcn/ui[/yellow]")
            return True
        
        cmd = ["npx", "shadcn@latest", "init"]
        if yes: cmd.append("-y")
        if base_color: cmd.extend(["--base-color", base_color])
        
        try:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
                progress.add_task(description="正在初始化...", total=None)
                result = self._run_command(cmd, check=False)
            
            if result.returncode == 0:
                console.print("[green]✓[/green] shadcn/ui 初始化成功!")
                return True
            console.print(f"[red]初始化失败: {result.stderr}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]错误: {e}[/red]")
            return False
    
    def add(self, components: List[str], overwrite: bool = False, yes: bool = False) -> bool:
        if not self._is_shadcn_initialized():
            console.print("[yellow]项目未初始化，先执行 init[/yellow]")
            return False
        if not components:
            console.print("[yellow]请指定要安装的组件[/yellow]")
            return False
        
        console.print(Panel.fit(f"[bold blue]安装组件: {', '.join(components)}[/bold blue]"))
        cmd = ["npx", "shadcn@latest", "add"] + components
        if overwrite: cmd.append("--overwrite")
        if yes: cmd.append("-y")
        
        try:
            result = self._run_command(cmd, check=False)
            if result.returncode == 0:
                console.print(f"[green]✓[/green] 组件 {', '.join(components)} 安装成功!")
                return True
            console.print("[red]安装失败[/red]")
            return False
        except Exception as e:
            console.print(f"[red]错误: {e}[/red]")
            return False
    
    def remove(self, components: List[str]) -> bool:
        if not components:
            console.print("[yellow]请指定要移除的组件[/yellow]")
            return False
        components_dir = self._get_components_dir()
        removed = []
        for comp in components:
            comp_file = components_dir / f"{comp}.tsx"
            if comp_file.exists():
                comp_file.unlink()
                removed.append(comp)
                console.print(f"[green]✓[/green] 已移除 {comp}")
            else:
                console.print(f"[yellow]组件 {comp} 不存在[/yellow]")
        return len(removed) > 0
    
    def list_components(self, category: Optional[str] = None) -> None:
        console.print(Panel.fit("[bold blue]shadcn/ui 组件列表[/bold blue]"))
        table = Table(title="可用组件")
        table.add_column("组件名", style="cyan")
        table.add_column("分类", style="green")
        table.add_column("描述", style="white")
        
        categories = {
            "layout": ["accordion", "aspect-ratio", "card", "collapsible", "resizable", 
                      "scroll-area", "separator", "sheet", "tabs"],
            "form": ["button", "checkbox", "combobox", "command", "form", "input",
                    "input-otp", "label", "radio-group", "select", "slider", "switch",
                    "textarea", "toggle", "toggle-group"],
            "overlay": ["alert-dialog", "dialog", "drawer", "hover-card", "popover",
                       "sheet", "toast", "sonner", "tooltip"],
            "display": ["alert", "badge", "breadcrumb", "calendar", "carousel", "chart",
                       "pagination", "progress", "skeleton", "table"],
            "navigation": ["dropdown-menu", "menubar", "navigation-menu", "context-menu"]
        }
        descriptions = {"button": "按钮组件", "card": "卡片容器", "input": "输入框",
            "dialog": "对话框", "select": "选择器", "form": "表单组件", "table": "表格",
            "tabs": "标签页", "dropdown-menu": "下拉菜单", "toast": "轻提示",
            "calendar": "日历", "chart": "图表", "command": "命令面板"}
        
        for comp in sorted(self.POPULAR_COMPONENTS):
            comp_category = next((cat for cat, comps in categories.items() if comp in comps), "other")
            if category and comp_category != category: continue
            table.add_row(comp, comp_category, descriptions.get(comp, "-"))
        
        console.print(table)
        console.print(f"\n[dim]共 {len(self.POPULAR_COMPONENTS)} 个组件[/dim]")
    
    def search(self, query: str) -> None:
        console.print(Panel.fit(f"[bold blue]搜索: {query}[/bold blue]"))
        results = [c for c in self.POPULAR_COMPONENTS if query.lower() in c.lower()]
        if not results:
            console.print("[yellow]未找到匹配的组件[/yellow]")
            return
        for comp in results:
            console.print(f"  [green]•[/green] {comp}")
        console.print(f"\n找到 [bold]{len(results)}[/bold] 个组件")
    
    def update(self) -> bool:
        console.print(Panel.fit("[bold blue]更新组件[/bold blue]"))
        installed = self._get_installed_components()
        if not installed:
            console.print("[yellow]未找到已安装的组件[/yellow]")
            return False
        console.print(f"将更新 {len(installed)} 个组件")
        return self.add(installed, overwrite=True, yes=True)
    
    def doctor(self) -> bool:
        console.print(Panel.fit("[bold blue]项目诊断[/bold blue]"))
        issues = []
        
        if self.components_json.exists():
            console.print("[green]✓[/green] components.json 存在")
            try:
                with open(self.components_json, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                console.print(f"  [dim]框架: {config.get('framework', 'unknown')}[/dim]")
                console.print(f"  [dim]基础色: {config.get('baseColor', 'unknown')}[/dim]")
            except json.JSONDecodeError:
                issues.append("components.json 格式错误")
        else:
            issues.append("components.json 不存在")
        
        components_dir = self._get_components_dir()
        if components_dir.exists():
            installed = self._get_installed_components()
            console.print(f"[green]✓[/green] 组件目录存在 ({len(installed)} 个组件)")
        else:
            issues.append("组件目录不存在")
        
        has_tailwind = any((self.project_path / c).exists() for c in ["tailwind.config.js", "tailwind.config.ts"])
        if has_tailwind:
            console.print("[green]✓[/green] Tailwind CSS 配置存在")
        else:
            issues.append("Tailwind 配置不存在")
        
        if (self.project_path / "package.json").exists():
            console.print("[green]✓[/green] package.json 存在")
        else:
            issues.append("package.json 不存在")
        
        if issues:
            console.print("\n[red]发现的问题:[/red]")
            for issue in issues:
                console.print(f"  [red]✗[/red] {issue}")
            return False
        console.print("\n[green]✓ 项目配置正常[/green]")
        return True
    
    def theme(self, base_color: Optional[str] = None) -> bool:
        console.print(Panel.fit("[bold blue]主题配置[/bold blue]"))
        if not self.components_json.exists():
            console.print("[red]项目未初始化[/red]")
            return False
        try:
            with open(self.components_json, 'r', encoding='utf-8') as f:
                config = json.load(f)
            if base_color:
                config['baseColor'] = base_color
                with open(self.components_json, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                console.print(f"[green]✓[/green] 主题色已设置为 {base_color}")
                console.print("[yellow]提示: 需要重新安装组件以应用主题[/yellow]")
            else:
                console.print(f"当前主题色: [bold]{config.get('baseColor', 'slate')}[/bold]")
                console.print(f"\n可用主题色: neutral, gray, zinc, stone, slate")
            return True
        except Exception as e:
            console.print(f"[red]错误: {e}[/red]")
            return False
    
    def generate_component(self, name: str, template: str = "default") -> bool:
        console.print(Panel.fit(f"[bold blue]生成组件: {name}[/bold blue]"))
        components_dir = self._get_components_dir()
        components_dir.mkdir(parents=True, exist_ok=True)
        
        comp_file = components_dir / f"{name}.tsx"
        if comp_file.exists():
            console.print(f"[yellow]组件 {name} 已存在[/yellow]")
            return False
        
        templates = {"default": f'''"use client"

import * as React from "react"
import {{ cn }} from "@/lib/utils"

export interface {name.title()}Props {{
  className?: string
  children?: React.ReactNode
}}

export function {name.title()}({{ className, children, ...props }}: {name.title()}Props) {{
  return (
    <div className={{cn("", className)}} {{...props}}>
      {{children}}
    </div>
  )
}}
''', "button": f'''"use client"

import * as React from "react"
import {{ Slot }} from "@radix-ui/react-slot"
import {{ cva, type VariantProps }} from "class-variance-authority"
import {{ cn }} from "@/lib/utils"

const {name}Variants = cva("inline-flex items-center justify-center", {{
  variants: {{
    variant: {{ default: "bg-primary text-primary-foreground" }},
    size: {{ default: "h-10 px-4 py-2" }}
  }},
  defaultVariants: {{ variant: "default", size: "default" }}
}})

export interface {name.title()}Props extends React.ButtonHTMLAttributes<HTMLButtonElement>,
  VariantProps<typeof {name}Variants> {{ asChild?: boolean }}

export function {name.title()}({{ className, variant, size, asChild = false, ...props }}: {name.title()}Props) {{
  const Comp = asChild ? Slot : "button"
  return <Comp className={{cn({name}Variants({{ variant, size, className }}))}} {{...props}} />
}}
'''}
        
        content = templates.get(template, templates["default"])
        try:
            comp_file.write_text(content, encoding='utf-8')
            console.print(f"[green]✓[/green] 组件 {name} 已生成: {comp_file}")
            return True
        except Exception as e:
            console.print(f"[red]生成失败: {e}[/red]")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="shadcn/ui 组件库集成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --action init                           初始化项目
  %(prog)s --action add --component button         安装 button 组件
  %(prog)s --action add -c card,input,button       批量安装组件
  %(prog)s --action list                           列出所有组件
  %(prog)s --action search -c form                 搜索组件
  %(prog)s --action doctor                         检查项目配置
        """
    )
    
    parser.add_argument("--action", "-a", required=True,
                       choices=["install", "add", "list", "remove", "search", 
                               "theme", "generate", "init", "update", "doctor"],
                       help="操作类型")
    parser.add_argument("--component", "-c", help="组件名称（支持逗号分隔）")
    parser.add_argument("--project_path", "-p", default=".", help="项目路径")
    parser.add_argument("--base_color", default="slate",
                       choices=["neutral", "gray", "zinc", "stone", "slate"],
                       help="基础主题色")
    parser.add_argument("--css_framework", default="tailwind",
                       choices=["tailwind", "css"], help="CSS 框架")
    parser.add_argument("--overwrite", action="store_true", help="覆盖已有组件")
    parser.add_argument("--yes", "-y", action="store_true", help="自动确认")
    
    args = parser.parse_args()
    
    config = ShadcnConfig(
        project_path=args.project_path,
        base_color=args.base_color,
        css_framework=args.css_framework
    )
    shadcn = ShadcnUI(config)
    action = args.action
    
    if action in ["init", "install"]:
        success = shadcn.init(yes=args.yes, base_color=args.base_color)
    elif action == "add":
        components = [c.strip() for c in args.component.split(",")] if args.component else []
        success = shadcn.add(components, overwrite=args.overwrite, yes=args.yes)
    elif action == "remove":
        components = [c.strip() for c in args.component.split(",")] if args.component else []
        success = shadcn.remove(components)
    elif action == "list":
        shadcn.list_components(); success = True
    elif action == "search":
        if not args.component:
            console.print("[red]请指定搜索关键词: --component <keyword>[/red]"); sys.exit(1)
        shadcn.search(args.component); success = True
    elif action == "update":
        success = shadcn.update()
    elif action == "doctor":
        success = shadcn.doctor()
    elif action == "theme":
        success = shadcn.theme(base_color=args.base_color)
    elif action == "generate":
        if not args.component:
            console.print("[red]请指定组件名称: --component <name>[/red]"); sys.exit(1)
        success = shadcn.generate_component(args.component)
    else:
        console.print(f"[red]未知操作: {action}[/red]"); sys.exit(1)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
