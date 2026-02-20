#!/usr/bin/env python3
"""Vite Skill - 项目创建示例"""

import sys
sys.path.insert(0, '..')

from main import ViteGenerator

def main():
    generator = ViteGenerator()
    
    print("=" * 70)
    print("Vite Skill - 项目创建示例")
    print("=" * 70)
    
    # 示例1: 创建不同模板的项目
    print("\n1. 创建项目命令")
    print("-" * 50)
    
    templates = ["vanilla", "vanilla-ts", "react-ts", "vue-ts"]
    
    for template in templates:
        print(f"\n--- {template} 模板 ---")
        commands = generator.get_project_commands(f"my-{template}-app", template)
        for cmd in commands:
            print(f"  {cmd}")
    
    # 示例2: 官方模板列表
    print("\n2. 官方模板列表")
    print("-" * 50)
    
    for template in generator.OFFICIAL_TEMPLATES:
        print(f"  - {template}")
    
    # 示例3: 优化建议
    print("\n3. 构建优化建议")
    print("-" * 50)
    
    suggestions = generator.get_optimization_suggestions()
    for i, sugg in enumerate(suggestions, 1):
        print(f"\n  {i}. {sugg['category']}")
        print(f"     建议: {sugg['tip']}")
        print(f"     示例: {sugg['example']}")
    
    # 示例4: 代理配置
    print("\n4. 开发服务器代理配置")
    print("-" * 50)
    
    proxy_configs = [
        {
            "/api": "http://localhost:3000",
            "/auth": "http://localhost:3000"
        },
        {
            "/graphql": "http://localhost:4000",
            "/ws": "ws://localhost:4001"
        }
    ]
    
    for i, proxies in enumerate(proxy_configs, 1):
        print(f"\n  配置 {i}:")
        config = generator.generate_proxy_config(proxies)
        for path, settings in config.items():
            print(f"    {path} -> {settings['target']}")
    
    # 示例5: 完整项目配置
    print("\n5. 完整项目配置示例")
    print("-" * 50)
    
    import json
    
    # React + TypeScript项目
    print("\n  React + TypeScript项目:")
    
    # package.json
    pkg = generator.generate_package_json(
        "my-react-app",
        "react-ts",
        dependencies=["react-router-dom", "axios"]
    )
    print("  package.json:")
    print(json.dumps(pkg, indent=4))
    
    # vite.config.ts
    config = generator.generate_config(
        framework="react-ts",
        base="/",
        server_options={
            "port": 5173,
            "open": True,
            "proxy": generator.generate_proxy_config({"/api": "http://localhost:3000"})
        },
        build_options={
            "outDir": "dist",
            "sourcemap": True,
            "minify": "terser"
        },
        optimize_deps=["react", "react-dom", "react-router-dom"]
    )
    print("\n  vite.config.ts:")
    print(config)
    
    # 环境变量
    print("\n  .env.development:")
    print(generator.generate_env("development", {
        "VITE_API_BASE_URL": "/api",
        "VITE_APP_TITLE": "My React App"
    }))
    
    print("\n  .env.production:")
    print(generator.generate_env("production", {
        "VITE_API_BASE_URL": "https://api.example.com",
        "VITE_APP_TITLE": "My React App"
    }))
    
    # HTML模板
    print("\n  index.html:")
    print(generator.generate_html_template("My React App", "zh-CN"))
    
    print("\n" + "=" * 70)
    print("示例运行完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
