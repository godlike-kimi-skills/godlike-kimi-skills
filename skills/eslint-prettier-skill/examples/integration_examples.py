#!/usr/bin/env python3
"""ESLint Prettier Skill - 集成配置示例"""

import sys
sys.path.insert(0, '..')

from main import IntegrationHelper, ESLintGenerator, PrettierGenerator
import json

def main():
    eslint_gen = ESLintGenerator()
    prettier_gen = PrettierGenerator()
    
    print("=" * 70)
    print("ESLint Prettier Skill - 集成配置示例")
    print("=" * 70)
    
    # 示例1: ESLint + Prettier集成配置
    print("\n1. ESLint + Prettier集成配置")
    print("-" * 50)
    
    for framework in ["vanilla", "react", "vue"]:
        print(f"\n--- {framework.upper()} ---")
        config = IntegrationHelper.generate_prettier_eslint_config(framework)
        print(json.dumps(config, indent=2))
    
    # 示例2: TypeScript集成配置
    print("\n2. TypeScript集成配置")
    print("-" * 50)
    
    ts_config = IntegrationHelper.generate_prettier_eslint_config("react", typescript=True)
    print(json.dumps(ts_config, indent=2))
    
    # 示例3: 推荐依赖列表
    print("\n3. 推荐依赖列表")
    print("-" * 50)
    
    configs = [
        ("vanilla", False),
        ("react", True),
        ("vue", False),
    ]
    
    for fw, ts in configs:
        print(f"\n--- {fw} {'+ TypeScript' if ts else ''} ---")
        deps = IntegrationHelper.get_recommended_deps(fw, ts)
        print("  ESLint相关:")
        for dep in deps["eslint"]:
            print(f"    - {dep}")
        print("  Prettier相关:")
        for dep in deps["prettier"]:
            print(f"    - {dep}")
    
    # 示例4: 设置指南
    print("\n4. 设置指南 (React + TypeScript)")
    print("-" * 50)
    
    guide = IntegrationHelper.generate_setup_guide("react", typescript=True, package_manager="npm")
    for line in guide:
        print(line)
    
    # 示例5: 完整的项目配置
    print("\n5. 完整的项目配置 (React + TypeScript)")
    print("-" * 50)
    
    # .eslintrc.json
    print("\n  .eslintrc.json:")
    eslint_config = IntegrationHelper.generate_prettier_eslint_config("react", typescript=True)
    print(json.dumps(eslint_config, indent=4))
    
    # .prettierrc
    print("\n  .prettierrc:")
    prettier_config = prettier_gen.generate_config(
        semi=True,
        single_quote=True,
        tab_width=2,
        print_width=100
    )
    print(json.dumps(prettier_config, indent=4))
    
    # .eslintignore
    print("\n  .eslintignore:")
    for pattern in eslint_gen.generate_ignore_config():
        print(f"    {pattern}")
    
    # .prettierignore
    print("\n  .prettierignore:")
    for pattern in prettier_gen.generate_ignore_config():
        print(f"    {pattern}")
    
    # package.json scripts
    print("\n  package.json scripts:")
    scripts = prettier_gen.generate_integrated_script("npm")
    print("    \"scripts\": {")
    for name, cmd in scripts.items():
        print(f'      "{name}": "{cmd}"{"," if name != "lint:fix" else ""}')
    print("    }")
    
    # 安装命令
    print("\n  安装命令:")
    print(f"    {eslint_gen.get_install_command('react', True, 'npm')}")
    
    # 示例6: VSCode设置
    print("\n6. VSCode 推荐设置")
    print("-" * 50)
    
    vscode_settings = {
        "editor.formatOnSave": True,
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.codeActionsOnSave": {
            "source.fixAll.eslint": True
        },
        "eslint.workingDirectories": [{"mode": "auto"}],
        "[javascript]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "[typescript]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "[javascriptreact]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "[typescriptreact]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        }
    }
    print("  .vscode/settings.json:")
    print(json.dumps(vscode_settings, indent=4))
    
    # 示例7: 扩展推荐
    print("\n7. VSCode 扩展推荐")
    print("-" * 50)
    
    extensions = {
        "recommendations": [
            "dbaeumer.vscode-eslint",
            "esbenp.prettier-vscode",
            "bradlc.vscode-tailwindcss",
            "formulahendry.auto-rename-tag",
            "christian-kohler.path-intellisense"
        ]
    }
    print("  .vscode/extensions.json:")
    print(json.dumps(extensions, indent=4))
    
    # 示例8: GitHub Actions工作流
    print("\n8. GitHub Actions 工作流")
    print("-" * 50)
    
    workflow = """name: Lint and Format

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run ESLint
      run: npm run lint
    
    - name: Check formatting
      run: npm run format:check
"""
    print(workflow)
    
    # 示例9: 预提交钩子配置
    print("\n9. Husky + lint-staged 配置")
    print("-" * 50)
    
    husky_config = {
        "scripts": {
            "prepare": "husky install"
        },
        "lint-staged": {
            "*.{js,jsx,ts,tsx}": [
                "eslint --fix",
                "prettier --write"
            ],
            "*.{json,md,css}": [
                "prettier --write"
            ]
        }
    }
    print("  package.json 添加:")
    print(json.dumps(husky_config, indent=4))
    print("\n  安装命令:")
    print("    npm install --save-dev husky lint-staged")
    print("    npx husky install")
    print('    npx husky add .husky/pre-commit "npx lint-staged"')
    
    print("\n" + "=" * 70)
    print("示例运行完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
