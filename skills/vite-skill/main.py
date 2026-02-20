#!/usr/bin/env python3
"""
Vite Skill - 构建工具管理工具
支持项目创建、配置优化、插件管理
"""

import json
import os
import sys
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from colorama import init, Fore, Style

init()


@dataclass
class VitePlugin:
    """Vite插件配置"""
    name: str
    import_name: str
    package: str
    config: Dict[str, Any] = field(default_factory=dict)
    description: str = ""


class VitePlugins:
    """Vite常用插件库"""
    
    PLUGINS = {
        "react": VitePlugin(
            name="react",
            import_name="react",
            package="@vitejs/plugin-react",
            description="Official React plugin for Vite"
        ),
        "react-swc": VitePlugin(
            name="react",
            import_name="react",
            package="@vitejs/plugin-react-swc",
            description="React plugin using SWC for Fast Refresh"
        ),
        "vue": VitePlugin(
            name="vue",
            import_name="vue",
            package="@vitejs/plugin-vue",
            description="Official Vue plugin for Vite"
        ),
        "svelte": VitePlugin(
            name="svelte",
            import_name="svelte",
            package="@sveltejs/vite-plugin-svelte",
            description="Official Svelte plugin for Vite"
        ),
        "legacy": VitePlugin(
            name="legacy",
            import_name="legacy",
            package="@vitejs/plugin-legacy",
            description="Generate legacy chunks for older browsers",
            config={"targets": ["defaults", "not IE 11"]}
        ),
        "pwa": VitePlugin(
            name="VitePWA",
            import_name="VitePWA",
            package="vite-plugin-pwa",
            description="Zero-config PWA Plugin for Vite",
            config={
                "registerType": "autoUpdate",
                "manifest": {
                    "name": "My App",
                    "short_name": "MyApp"
                }
            }
        ),
        "svgr": VitePlugin(
            name="svgr",
            import_name="svgr",
            package="vite-plugin-svgr",
            description="Transform SVGs into React components"
        ),
        "md": VitePlugin(
            name="md",
            import_name="md",
            package="vite-plugin-md",
            description="Markdown as Vue components"
        ),
        "checker": VitePlugin(
            name="checker",
            import_name="checker",
            package="vite-plugin-checker",
            description="Run TypeScript checker in worker thread",
            config={"typescript": True}
        ),
        "compression": VitePlugin(
            name="compression",
            import_name="compression",
            package="vite-plugin-compression",
            description="Use gzip or brotli to compress resources"
        ),
        "visualizer": VitePlugin(
            name="visualizer",
            import_name="visualizer",
            package="rollup-plugin-visualizer",
            description="Visualize and analyze your Rollup bundle"
        ),
        "dts": VitePlugin(
            name="dts",
            import_name="dts",
            package="vite-plugin-dts",
            description="Generate declaration files from TS"
        ),
    }
    
    @classmethod
    def get_plugin(cls, name: str) -> Optional[VitePlugin]:
        """获取插件配置"""
        return cls.PLUGINS.get(name)
    
    @classmethod
    def list_plugins(cls) -> List[str]:
        """列出所有可用插件"""
        return list(cls.PLUGINS.keys())
    
    @classmethod
    def get_plugins_for_framework(cls, framework: str) -> List[str]:
        """获取框架推荐插件"""
        framework_plugins = {
            "react": ["react", "svgr"],
            "react-swc": ["react-swc", "svgr"],
            "vue": ["vue"],
            "svelte": ["svelte"],
            "vanilla": []
        }
        return framework_plugins.get(framework, [])


class ViteGenerator:
    """Vite配置生成器"""
    
    # 官方模板列表
    OFFICIAL_TEMPLATES = [
        "vanilla", "vanilla-ts",
        "vue", "vue-ts",
        "react", "react-ts", "react-swc",
        "preact", "preact-ts",
        "lit", "lit-ts",
        "svelte", "svelte-ts"
    ]
    
    # 默认端口
    DEFAULT_PORT = 5173
    
    def __init__(self):
        self.indent = "  "
    
    def generate_config(
        self,
        framework: str = "vanilla",
        plugins: Optional[List[str]] = None,
        base: str = "/",
        build_options: Optional[Dict[str, Any]] = None,
        server_options: Optional[Dict[str, Any]] = None,
        resolve_options: Optional[Dict[str, Any]] = None,
        css_options: Optional[Dict[str, Any]] = None,
        optimize_deps: Optional[List[str]] = None
    ) -> str:
        """
        生成Vite配置文件
        
        Args:
            framework: 框架类型
            plugins: 插件列表
            base: 基础路径
            build_options: 构建选项
            server_options: 服务器选项
            resolve_options: 解析选项
            css_options: CSS选项
            optimize_deps: 依赖预构建列表
        
        Returns:
            Vite配置代码
        """
        lines = []
        
        # 导入语句
        imports = []
        
        # 框架插件
        framework_plugins = VitePlugins.get_plugins_for_framework(framework)
        for plugin_name in framework_plugins:
            plugin = VitePlugins.get_plugin(plugin_name)
            if plugin:
                imports.append(f'import {plugin.import_name} from "{plugin.package}";')
        
        # 额外插件
        if plugins:
            for plugin_name in plugins:
                if plugin_name not in framework_plugins:
                    plugin = VitePlugins.get_plugin(plugin_name)
                    if plugin:
                        imports.append(f'import {plugin.import_name} from "{plugin.package}";')
        
        # 添加defineConfig导入
        imports.insert(0, 'import { defineConfig } from "vite";')
        
        lines.extend(imports)
        lines.append("")
        
        # 配置开始
        lines.append("export default defineConfig({")
        
        # 基础配置
        if base != "/":
            lines.append(f'{self.indent}base: "{base}",')
        
        # 插件配置
        all_plugins = framework_plugins + (plugins or [])
        if all_plugins:
            lines.append(f'{self.indent}plugins: [')
            plugin_lines = []
            for plugin_name in all_plugins:
                plugin = VitePlugins.get_plugin(plugin_name)
                if plugin:
                    if plugin.config:
                        config_str = json.dumps(plugin.config, ensure_ascii=False)
                        config_str = config_str.replace('"', "'").replace('true', 'true').replace('false', 'false')
                        plugin_lines.append(f"{self.indent}{self.indent}{plugin.name}({config_str}),")
                    else:
                        plugin_lines.append(f"{self.indent}{self.indent}{plugin.name}(),")
            lines.extend(plugin_lines)
            lines.append(f'{self.indent}],')
        
        # 解析配置
        if resolve_options:
            lines.append(f'{self.indent}resolve: {self._dict_to_ts(resolve_options)},')
        
        # CSS配置
        if css_options:
            lines.append(f'{self.indent}css: {self._dict_to_ts(css_options)},')
        
        # 服务器配置
        if server_options:
            lines.append(f'{self.indent}server: {self._dict_to_ts(server_options)},')
        
        # 构建配置
        if build_options:
            lines.append(f'{self.indent}build: {self._dict_to_ts(build_options)},')
        
        # 依赖优化
        if optimize_deps:
            deps_str = ", ".join([f'"{dep}"' for dep in optimize_deps])
            lines.append(f'{self.indent}optimizeDeps: {{')
            lines.append(f'{self.indent}{self.indent}include: [{deps_str}],')
            lines.append(f'{self.indent}}},')
        
        lines.append("});")
        
        return "\n".join(lines)
    
    def _dict_to_ts(self, data: Dict[str, Any]) -> str:
        """将字典转换为TypeScript对象字面量"""
        items = []
        for key, value in data.items():
            if isinstance(value, str):
                items.append(f'{key}: "{value}"')
            elif isinstance(value, bool):
                items.append(f'{key}: {str(value).lower()}')
            elif isinstance(value, (int, float)):
                items.append(f'{key}: {value}')
            elif isinstance(value, list):
                list_str = ", ".join([f'"{v}"' if isinstance(v, str) else str(v) for v in value])
                items.append(f'{key}: [{list_str}]')
            elif isinstance(value, dict):
                nested = self._dict_to_ts(value)
                items.append(f'{key}: {nested}')
            else:
                items.append(f'{key}: {value}')
        return "{ " + ", ".join(items) + " }"
    
    def generate_package_json(
        self,
        name: str,
        framework: str = "vanilla",
        dependencies: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        生成package.json
        
        Args:
            name: 项目名称
            framework: 框架类型
            dependencies: 额外依赖
        
        Returns:
            package.json字典
        """
        pkg = {
            "name": name,
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "preview": "vite preview"
            },
            "devDependencies": {
                "vite": "^5.0.0"
            }
        }
        
        # 添加框架依赖
        if framework in ["react", "react-ts", "react-swc"]:
            pkg["dependencies"] = {
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            }
            pkg["devDependencies"]["@types/react"] = "^18.2.0"
            pkg["devDependencies"]["@types/react-dom"] = "^18.2.0"
            if "ts" in framework or framework == "react-swc":
                pkg["devDependencies"]["typescript"] = "^5.0.0"
        
        elif framework in ["vue", "vue-ts"]:
            pkg["dependencies"] = {"vue": "^3.3.0"}
            if "ts" in framework:
                pkg["devDependencies"]["typescript"] = "^5.0.0"
                pkg["devDependencies"]["vue-tsc"] = "^1.8.0"
        
        elif framework in ["svelte", "svelte-ts"]:
            pkg["dependencies"] = {"svelte": "^4.0.0"}
        
        # 添加额外依赖
        if dependencies:
            if "dependencies" not in pkg:
                pkg["dependencies"] = {}
            for dep in dependencies:
                pkg["dependencies"][dep] = "latest"
        
        return pkg
    
    def generate_env(
        self,
        env: str = "development",
        variables: Optional[Dict[str, str]] = None
    ) -> str:
        """
        生成环境变量文件
        
        Args:
            env: 环境名称
            variables: 环境变量字典
        
        Returns:
            环境变量文件内容
        """
        lines = [f"# {env} environment variables"]
        
        if env == "development":
            lines.append("NODE_ENV=development")
            lines.append(f"VITE_APP_BASE_URL=http://localhost:{self.DEFAULT_PORT}")
        elif env == "production":
            lines.append("NODE_ENV=production")
            lines.append("VITE_APP_BASE_URL=https://api.example.com")
        
        if variables:
            for key, value in variables.items():
                lines.append(f"{key}={value}")
        
        return "\n".join(lines)
    
    def generate_env_types(self, variables: List[str]) -> str:
        """生成环境变量类型声明"""
        lines = [
            "/// <reference types=\"vite/client\" />",
            "",
            "interface ImportMetaEnv {"
        ]
        
        for var in variables:
            if var.startswith("VITE_"):
                lines.append(f"  readonly {var}: string;")
        
        lines.extend([
            "}",
            "",
            "interface ImportMeta {",
            "  readonly env: ImportMetaEnv;",
            "}"
        ])
        
        return "\n".join(lines)
    
    def get_project_commands(
        self,
        name: str,
        template: str = "vanilla"
    ) -> List[str]:
        """
        获取项目创建命令
        
        Args:
            name: 项目名称
            template: 模板名称
        
        Returns:
            命令列表
        """
        if template not in self.OFFICIAL_TEMPLATES:
            raise ValueError(f"Unknown template: {template}. Available: {self.OFFICIAL_TEMPLATES}")
        
        package_manager = "npm"  # 默认使用npm
        
        commands = [
            f"# Create project with {template} template",
            f"{package_manager} create vite@latest {name} -- --template {template}",
            f"cd {name}",
            f"{package_manager} install",
            f"{package_manager} run dev"
        ]
        
        return commands
    
    def generate_proxy_config(
        self,
        proxies: Dict[str, str],
        change_origin: bool = True
    ) -> Dict[str, Any]:
        """
        生成代理配置
        
        Args:
            proxies: 代理映射 {路径: 目标URL}
            change_origin: 是否改变origin
        
        Returns:
            代理配置字典
        """
        proxy_config = {}
        
        for path, target in proxies.items():
            proxy_config[path] = {
                "target": target,
                "changeOrigin": change_origin,
                "secure": target.startswith("https")
            }
        
        return proxy_config
    
    def get_optimization_suggestions(
        self,
        build_output: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """
        获取构建优化建议
        
        Args:
            build_output: 构建输出信息
        
        Returns:
            优化建议列表
        """
        suggestions = [
            {
                "category": "依赖优化",
                "tip": "在 optimizeDeps.include 中添加大型依赖",
                "example": "optimizeDeps: { include: ['lodash-es', 'moment'] }"
            },
            {
                "category": "代码分割",
                "tip": "使用动态导入实现路由级代码分割",
                "example": "const Module = await import('./Module.tsx')"
            },
            {
                "category": "资源处理",
                "tip": "配置 assetsInclude 处理额外资源类型",
                "example": "assetsInclude: ['**/*.gltf']"
            },
            {
                "category": "构建优化",
                "tip": "启用 brotli 压缩减少传输大小",
                "example": "build: { reportCompressedSize: true }"
            },
            {
                "category": "缓存策略",
                "tip": "为第三方库配置独立chunk",
                "example": "manualChunks: { vendor: ['react', 'react-dom'] }"
            }
        ]
        
        return suggestions
    
    def generate_html_template(
        self,
        title: str = "Vite App",
        lang: str = "en",
        meta: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """生成HTML模板"""
        meta_tags = meta or [
            {"charset": "UTF-8"},
            {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        ]
        
        meta_str = "\n    ".join([
            f'<meta {" ".join([f\'{k}="{v}"\' for k, v in m.items()])} />'
            for m in meta_tags
        ])
        
        return f'''<!doctype html>
<html lang="{lang}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
'''
    
    def save_config(self, config: str, filepath: str) -> None:
        """保存配置到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(config)


def main():
    """命令行入口"""
    generator = ViteGenerator()
    
    if len(sys.argv) < 2:
        print(f"{Fore.CYAN}Vite Skill v1.0.0{Style.RESET_ALL}")
        print("\nUsage:")
        print("  python main.py config --framework <name> [options]  - Generate vite.config.ts")
        print("  python main.py project <name> --template <tpl>      - Generate project commands")
        print("  python main.py plugin <name> [options]              - Generate plugin config")
        print("  python main.py env <env>                            - Generate .env file")
        print("  python main.py optimize                             - Show optimization tips")
        print("\nExamples:")
        print('  python main.py config --framework react --base /app/')
        print('  python main.py project my-app --template react-ts')
        print('  python main.py plugin legacy --targets "defaults"')
        return
    
    command = sys.argv[1]
    
    if command == "config":
        framework = "vanilla"
        base = "/"
        plugins = []
        
        if "--framework" in sys.argv:
            idx = sys.argv.index("--framework")
            if idx + 1 < len(sys.argv):
                framework = sys.argv[idx + 1]
        
        if "--base" in sys.argv:
            idx = sys.argv.index("--base")
            if idx + 1 < len(sys.argv):
                base = sys.argv[idx + 1]
        
        config = generator.generate_config(framework=framework, base=base, plugins=plugins)
        print(f"{Fore.GREEN}{config}{Style.RESET_ALL}")
    
    elif command == "project":
        if len(sys.argv) < 3:
            print(f"{Fore.RED}Error: Project name required{Style.RESET_ALL}")
            return
        name = sys.argv[2]
        template = "vanilla"
        
        if "--template" in sys.argv:
            idx = sys.argv.index("--template")
            if idx + 1 < len(sys.argv):
                template = sys.argv[idx + 1]
        
        try:
            commands = generator.get_project_commands(name, template)
            print(f"{Fore.GREEN}# Project creation commands:{Style.RESET_ALL}")
            for cmd in commands:
                print(cmd)
        except ValueError as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    
    elif command == "plugin":
        if len(sys.argv) < 3:
            print(f"{Fore.RED}Error: Plugin name required{Style.RESET_ALL}")
            available = VitePlugins.list_plugins()
            print(f"Available plugins: {', '.join(available)}")
            return
        
        plugin_name = sys.argv[2]
        plugin = VitePlugins.get_plugin(plugin_name)
        
        if plugin:
            print(f"{Fore.GREEN}# Plugin: {plugin.name}{Style.RESET_ALL}")
            print(f"Package: {plugin.package}")
            print(f"Description: {plugin.description}")
            if plugin.config:
                print(f"Default config: {json.dumps(plugin.config, indent=2)}")
        else:
            print(f"{Fore.RED}Unknown plugin: {plugin_name}{Style.RESET_ALL}")
    
    elif command == "env":
        env = sys.argv[2] if len(sys.argv) > 2 else "development"
        content = generator.generate_env(env)
        print(f"{Fore.GREEN}{content}{Style.RESET_ALL}")
    
    elif command == "optimize":
        suggestions = generator.get_optimization_suggestions()
        print(f"{Fore.CYAN}Build Optimization Suggestions:{Style.RESET_ALL}\n")
        for i, sugg in enumerate(suggestions, 1):
            print(f"{Fore.YELLOW}{i}. {sugg['category']}{Style.RESET_ALL}")
            print(f"   Tip: {sugg['tip']}")
            print(f"   Example: {Fore.GREEN}{sugg['example']}{Style.RESET_ALL}\n")
    
    else:
        print(f"{Fore.RED}Unknown command: {command}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
