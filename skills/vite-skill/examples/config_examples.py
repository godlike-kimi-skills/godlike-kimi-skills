#!/usr/bin/env python3
"""Vite Skill - 配置生成示例"""

import sys
sys.path.insert(0, '..')

from main import ViteGenerator

def main():
    generator = ViteGenerator()
    
    print("=" * 70)
    print("Vite Skill - 配置生成示例")
    print("=" * 70)
    
    # 示例1: React项目配置
    print("\n1. React项目配置")
    print("-" * 50)
    
    react_config = generator.generate_config(
        framework="react",
        base="/",
        server_options={
            "port": 5173,
            "open": True
        },
        build_options={
            "outDir": "dist",
            "sourcemap": True
        }
    )
    print(react_config)
    
    # 示例2: Vue项目配置（带代理）
    print("\n2. Vue项目配置（带代理）")
    print("-" * 50)
    
    proxy_config = generator.generate_proxy_config({
        "/api": "http://localhost:3000",
        "/uploads": "http://localhost:3000"
    })
    
    vue_config = generator.generate_config(
        framework="vue",
        server_options={
            "port": 5173,
            "proxy": proxy_config
        }
    )
    print(vue_config)
    
    # 示例3: 带插件的配置
    print("\n3. 带多插件的配置")
    print("-" * 50)
    
    advanced_config = generator.generate_config(
        framework="react",
        plugins=["legacy", "pwa", "compression"],
        base="/app/",
        build_options={
            "outDir": "dist",
            "minify": "terser",
            "rollupOptions": {
                "output": {
                    "manualChunks": {
                        "vendor": ["react", "react-dom"]
                    }
                }
            }
        },
        optimize_deps=["lodash-es", "moment"]
    )
    print(advanced_config)
    
    # 示例4: 库模式配置
    print("\n4. 库模式配置")
    print("-" * 50)
    
    lib_config = generator.generate_config(
        framework="vanilla",
        plugins=["dts"],
        build_options={
            "lib": {
                "entry": "src/index.ts",
                "name": "MyLib",
                "fileName": "my-lib"
            },
            "rollupOptions": {
                "external": ["vue"]
            }
        }
    )
    print(lib_config)
    
    # 示例5: SSR配置
    print("\n5. SSR配置")
    print("-" * 50)
    
    ssr_config = generator.generate_config(
        framework="react",
        build_options={
            "ssr": True,
            "outDir": "dist/server"
        }
    )
    print(ssr_config)
    
    # 示例6: package.json生成
    print("\n6. Package.json 生成")
    print("-" * 50)
    
    import json
    
    for framework in ["react-ts", "vue", "svelte-ts"]:
        pkg = generator.generate_package_json(f"my-{framework}-app", framework)
        print(f"\n--- {framework} ---")
        print(json.dumps(pkg, indent=2))
    
    # 示例7: 环境变量
    print("\n7. 环境变量文件")
    print("-" * 50)
    
    print("# Development")
    print(generator.generate_env("development", {"VITE_API_URL": "http://localhost:3000"}))
    
    print("\n# Production")
    print(generator.generate_env("production", {"VITE_API_URL": "https://api.example.com"}))
    
    # 示例8: HTML模板
    print("\n8. HTML模板")
    print("-" * 50)
    
    html = generator.generate_html_template(
        title="My Awesome App",
        lang="zh-CN",
        meta=[
            {"charset": "UTF-8"},
            {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
            {"name": "description", "content": "A Vite-powered application"}
        ]
    )
    print(html)
    
    print("\n" + "=" * 70)
    print("示例运行完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
