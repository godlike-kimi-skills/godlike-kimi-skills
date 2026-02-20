#!/usr/bin/env python3
"""ESLint Prettier Skill - ESLint配置示例"""

import sys
sys.path.insert(0, '..')

from main import ESLintGenerator
import json

def main():
    generator = ESLintGenerator()
    
    print("=" * 70)
    print("ESLint Prettier Skill - ESLint配置示例")
    print("=" * 70)
    
    # 示例1: 基础JavaScript配置
    print("\n1. 基础JavaScript配置")
    print("-" * 50)
    
    js_config = generator.generate_config(
        framework="vanilla",
        environment="browser"
    )
    print(json.dumps(js_config, indent=2))
    
    # 示例2: React配置
    print("\n2. React配置")
    print("-" * 50)
    
    react_config = generator.generate_config(
        framework="react",
        environment="browser",
        rules={
            "react/prop-types": "off",
            "react/react-in-jsx-scope": "off"
        }
    )
    print(json.dumps(react_config, indent=2))
    
    # 示例3: React + TypeScript配置
    print("\n3. React + TypeScript配置")
    print("-" * 50)
    
    react_ts_config = generator.generate_config(
        framework="react",
        typescript=True,
        rules={
            "@typescript-eslint/explicit-function-return-type": "off",
            "@typescript-eslint/no-explicit-any": "warn"
        }
    )
    print(json.dumps(react_ts_config, indent=2))
    
    # 示例4: Vue配置
    print("\n4. Vue 3配置")
    print("-" * 50)
    
    vue_config = generator.generate_config(
        framework="vue",
        environment="browser"
    )
    print(json.dumps(vue_config, indent=2))
    
    # 示例5: Vue + TypeScript配置
    print("\n5. Vue 3 + TypeScript配置")
    print("-" * 50)
    
    vue_ts_config = generator.generate_config(
        framework="vue",
        typescript=True
    )
    print(json.dumps(vue_ts_config, indent=2))
    
    # 示例6: Node.js配置
    print("\n6. Node.js配置")
    print("-" * 50)
    
    node_config = generator.generate_config(
        framework="vanilla",
        environment="node",
        ecma_version=2022
    )
    print(json.dumps(node_config, indent=2))
    
    # 示例7: 自定义规则配置
    print("\n7. 自定义规则配置")
    print("-" * 50)
    
    custom_config = generator.generate_config(
        framework="react",
        typescript=True,
        rules={
            "no-console": ["warn", {"allow": ["error"]}],
            "no-debugger": "error",
            "prefer-const": "error",
            "react-hooks/exhaustive-deps": "warn",
            "@typescript-eslint/no-unused-vars": ["error", {"argsIgnorePattern": "^_"}]
        },
        extends_list=["plugin:import/recommended"],
        plugins=["import"]
    )
    print(json.dumps(custom_config, indent=2))
    
    # 示例8: Flat Config格式（ESLint v9+）
    print("\n8. Flat Config格式 (ESLint v9+)")
    print("-" * 50)
    
    flat_config = generator.generate_flat_config(
        framework="react",
        typescript=True
    )
    print(flat_config)
    
    # 示例9: 安装命令
    print("\n9. 安装命令")
    print("-" * 50)
    
    configs = [
        ("vanilla", False),
        ("react", True),
        ("vue", True),
    ]
    
    for fw, ts in configs:
        print(f"\n--- {fw} {'+ TypeScript' if ts else ''} ---")
        for pm in ["npm", "yarn", "pnpm"]:
            cmd = generator.get_install_command(fw, ts, pm)
            print(f"  {pm}: {cmd}")
    
    # 示例10: 忽略文件
    print("\n10. .eslintignore")
    print("-" * 50)
    
    for pattern in generator.generate_ignore_config():
        print(f"  {pattern}")
    
    print("\n" + "=" * 70)
    print("示例运行完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
