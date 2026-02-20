#!/usr/bin/env python3
"""Vite Skill - 插件配置示例"""

import sys
sys.path.insert(0, '..')

from main import VitePlugins, ViteGenerator

def main():
    generator = ViteGenerator()
    
    print("=" * 70)
    print("Vite Skill - 插件配置示例")
    print("=" * 70)
    
    # 示例1: 列出所有插件
    print("\n1. 可用插件列表")
    print("-" * 50)
    
    plugins = VitePlugins.list_plugins()
    for plugin_name in plugins:
        plugin = VitePlugins.get_plugin(plugin_name)
        print(f"  {plugin_name:15} - {plugin.description}")
    
    # 示例2: 框架推荐插件
    print("\n2. 框架推荐插件")
    print("-" * 50)
    
    frameworks = ["react", "react-swc", "vue", "svelte"]
    for fw in frameworks:
        recommended = VitePlugins.get_plugins_for_framework(fw)
        print(f"  {fw:15} -> {', '.join(recommended) if recommended else 'None'}")
    
    # 示例3: PWA插件配置
    print("\n3. PWA插件完整配置")
    print("-" * 50)
    
    pwa_config = generator.generate_config(
        framework="react",
        plugins=["pwa"],
        build_options={
            "outDir": "dist"
        }
    )
    print(pwa_config)
    
    # 示例4: Legacy插件配置
    print("\n4. Legacy插件配置")
    print("-" * 50)
    
    legacy_config = generator.generate_config(
        framework="react",
        plugins=["legacy"],
        build_options={
            "target": "es2015"
        }
    )
    print(legacy_config)
    
    # 示例5: 多插件组合
    print("\n5. 多插件组合配置")
    print("-" * 50)
    
    combo_config = generator.generate_config(
        framework="react",
        plugins=["legacy", "compression", "visualizer"],
        build_options={
            "outDir": "dist",
            "sourcemap": True
        }
    )
    print(combo_config)
    
    # 示例6: 开发插件配置
    print("\n6. 开发插件配置（TypeScript检查）")
    print("-" * 50)
    
    dev_config = generator.generate_config(
        framework="react",
        plugins=["checker"],
        server_options={
            "port": 5173
        }
    )
    print(dev_config)
    
    # 示例7: 插件详细信息
    print("\n7. 插件详细信息")
    print("-" * 50)
    
    for plugin_name in ["pwa", "svgr", "dts"]:
        plugin = VitePlugins.get_plugin(plugin_name)
        print(f"\n  {plugin.name}:")
        print(f"    Package: {plugin.package}")
        print(f"    Import:  {plugin.import_name}")
        print(f"    Desc:    {plugin.description}")
        if plugin.config:
            import json
            print(f"    Config:  {json.dumps(plugin.config)}")
    
    print("\n" + "=" * 70)
    print("示例运行完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
