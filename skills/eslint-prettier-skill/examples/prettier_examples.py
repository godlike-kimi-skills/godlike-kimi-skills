#!/usr/bin/env python3
"""ESLint Prettier Skill - Prettier配置示例"""

import sys
sys.path.insert(0, '..')

from main import PrettierGenerator, PrettierPresets
import json

def main():
    generator = PrettierGenerator()
    
    print("=" * 70)
    print("ESLint Prettier Skill - Prettier配置示例")
    print("=" * 70)
    
    # 示例1: 默认配置
    print("\n1. 默认配置")
    print("-" * 50)
    
    default_config = generator.generate_config()
    print(json.dumps(default_config, indent=2))
    
    # 示例2: 无分号配置
    print("\n2. 无分号配置")
    print("-" * 50)
    
    no_semi_config = generator.generate_config(semi=False)
    print(json.dumps(no_semi_config, indent=2))
    
    # 示例3: 双引号配置
    print("\n3. 双引号配置")
    print("-" * 50)
    
    double_quote_config = generator.generate_config(single_quote=False)
    print(json.dumps(double_quote_config, indent=2))
    
    # 示例4: Tab缩进配置
    print("\n4. Tab缩进配置")
    print("-" * 50)
    
    tab_config = generator.generate_config(use_tabs=True, tab_width=4)
    print(json.dumps(tab_config, indent=2))
    
    # 示例5: 宽松换行配置
    print("\n5. 宽松换行配置 (printWidth: 120)")
    print("-" * 50)
    
    wide_config = generator.generate_config(print_width=120)
    print(json.dumps(wide_config, indent=2))
    
    # 示例6: 严格换行配置
    print("\n6. 严格换行配置 (printWidth: 80)")
    print("-" * 50)
    
    narrow_config = generator.generate_config(print_width=80)
    print(json.dumps(narrow_config, indent=2))
    
    # 示例7: 预设配置
    print("\n7. 预设配置")
    print("-" * 50)
    
    presets = ["default", "minimal", "airbnb", "google"]
    for preset_name in presets:
        preset = generator.generate_from_preset(preset_name)
        print(f"\n--- {preset_name} ---")
        print(json.dumps(preset, indent=2))
    
    # 示例8: 带覆盖的配置
    print("\n8. 带覆盖的配置")
    print("-" * 50)
    
    override_config = generator.generate_config(
        semi=True,
        single_quote=True,
        overrides=[
            {
                "files": "*.json",
                "options": {
                    "parser": "json",
                    "tabWidth": 2
                }
            },
            {
                "files": "*.md",
                "options": {
                    "parser": "markdown",
                    "proseWrap": "always"
                }
            }
        ]
    )
    print(json.dumps(override_config, indent=2))
    
    # 示例9: JSX配置
    print("\n9. JSX特定配置")
    print("-" * 50)
    
    jsx_config = generator.generate_config(
        jsx_single_quote=True,
        bracket_same_line=True,
        print_width=100
    )
    print(json.dumps(jsx_config, indent=2))
    
    # 示例10: 完整配置对比
    print("\n10. 常见配置对比")
    print("-" * 50)
    
    configs = [
        ("JavaScript Standard", {
            "semi": False,
            "singleQuote": True,
            "trailing_comma": "none"
        }),
        ("Airbnb", {
            "semi": True,
            "singleQuote": True,
            "trailing_comma": "all",
            "print_width": 100
        }),
        ("Google", {
            "semi": True,
            "singleQuote": True,
            "print_width": 80,
            "bracketSpacing": False
        }),
        ("Node.js", {
            "semi": True,
            "singleQuote": True,
            "trailing_comma": "es5",
            "print_width": 100
        }),
    ]
    
    for name, options in configs:
        config = generator.generate_config(**options)
        print(f"\n--- {name} ---")
        for key, value in config.items():
            if key != "overrides":
                print(f"  {key}: {value}")
    
    # 示例11: 忽略文件
    print("\n11. .prettierignore")
    print("-" * 50)
    
    for pattern in generator.generate_ignore_config():
        print(f"  {pattern}")
    
    # 示例12: package.json脚本
    print("\n12. 推荐的package.json脚本")
    print("-" * 50)
    
    scripts = generator.generate_integrated_script("npm")
    for name, cmd in scripts.items():
        print(f'  "{name}": "{cmd}"')
    
    print("\n" + "=" * 70)
    print("示例运行完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
