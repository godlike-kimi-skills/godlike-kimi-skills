#!/usr/bin/env python3
"""
ESLint Prettier Skill - 代码质量工具配置
支持规则配置、自动修复、集成设置
"""

import json
import sys
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from colorama import init, Fore, Style

init()


@dataclass
class RuleSet:
    """规则集定义"""
    name: str
    rules: Dict[str, Any]
    description: str = ""


class ESLintPresets:
    """ESLint预设规则库"""
    
    # React推荐规则
    REACT_RULES = {
        "react/react-in-jsx-scope": "off",
        "react/prop-types": "off",
        "react/jsx-uses-react": "off",
        "react-hooks/rules-of-hooks": "error",
        "react-hooks/exhaustive-deps": "warn",
        "react/jsx-key": "warn",
        "react/no-array-index-key": "warn",
        "react/jsx-no-target-blank": "warn",
    }
    
    # Vue推荐规则
    VUE_RULES = {
        "vue/html-self-closing": ["error", {"html": {"void": "always"}}],
        "vue/max-attributes-per-line": ["error", {"singleline": 3}],
        "vue/singleline-html-element-content-newline": "off",
        "vue/multiline-html-element-content-newline": "off",
        "vue/require-default-prop": "off",
        "vue/require-prop-types": "off",
    }
    
    # TypeScript推荐规则
    TYPESCRIPT_RULES = {
        "@typescript-eslint/no-unused-vars": ["error", {"argsIgnorePattern": "^_"}],
        "@typescript-eslint/explicit-function-return-type": "off",
        "@typescript-eslint/explicit-module-boundary-types": "off",
        "@typescript-eslint/no-explicit-any": "warn",
        "@typescript-eslint/no-non-null-assertion": "warn",
        "@typescript-eslint/prefer-nullish-coalescing": "warn",
        "@typescript-eslint/prefer-optional-chain": "warn",
    }
    
    # 通用最佳实践
    BEST_PRACTICES = {
        "no-console": ["warn", {"allow": ["warn", "error"]}],
        "no-debugger": "error",
        "no-alert": "warn",
        "no-var": "error",
        "prefer-const": "error",
        "eqeqeq": ["error", "always"],
        "curly": ["error", "all"],
        "no-throw-literal": "error",
        "prefer-promise-reject-errors": "error",
    }
    
    # 代码风格规则
    STYLE_RULES = {
        "indent": ["error", 2],
        "quotes": ["error", "single"],
        "semi": ["error", "always"],
        "comma-dangle": ["error", "always-multiline"],
        "object-curly-spacing": ["error", "always"],
        "array-bracket-spacing": ["error", "never"],
        "arrow-parens": ["error", "always"],
        "max-len": ["warn", {"code": 120, "ignoreUrls": True}],
    }
    
    # 导入规则
    IMPORT_RULES = {
        "import/order": ["error", {"groups": ["builtin", "external", "internal"]}],
        "import/no-duplicates": "error",
        "import/no-unresolved": "error",
        "import/named": "error",
    }


class PrettierPresets:
    """Prettier预设配置"""
    
    DEFAULT = {
        "semi": True,
        "singleQuote": True,
        "tabWidth": 2,
        "trailingComma": "es5",
        "printWidth": 100,
        "bracketSpacing": True,
        "arrowParens": "always",
        "endOfLine": "lf",
    }
    
    MINIMAL = {
        "semi": False,
        "singleQuote": True,
        "tabWidth": 2,
        "trailingComma": "none",
        "printWidth": 80,
    }
    
    AIRBNB = {
        "semi": True,
        "singleQuote": True,
        "tabWidth": 2,
        "trailingComma": "all",
        "printWidth": 100,
        "bracketSpacing": True,
    }
    
    GOOGLE = {
        "semi": True,
        "singleQuote": True,
        "tabWidth": 2,
        "trailingComma": "es5",
        "printWidth": 80,
        "bracketSpacing": False,
    }
    
    @classmethod
    def get_preset(cls, name: str) -> Dict[str, Any]:
        """获取预设配置"""
        presets = {
            "default": cls.DEFAULT,
            "minimal": cls.MINIMAL,
            "airbnb": cls.AIRBNB,
            "google": cls.GOOGLE,
        }
        return presets.get(name, cls.DEFAULT).copy()


class ESLintGenerator:
    """ESLint配置生成器"""
    
    def __init__(self):
        self.presets = ESLintPresets()
    
    def generate_config(
        self,
        framework: str = "vanilla",
        typescript: bool = False,
        environment: str = "browser",
        ecma_version: int = 2020,
        source_type: str = "module",
        rules: Optional[Dict[str, Any]] = None,
        extends_list: Optional[List[str]] = None,
        plugins: Optional[List[str]] = None,
        settings: Optional[Dict[str, Any]] = None,
        parser_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成ESLint配置
        
        Args:
            framework: 框架类型 (react, vue, vanilla)
            typescript: 是否使用TypeScript
            environment: 运行环境
            ecma_version: ECMAScript版本
            source_type: 源码类型
            rules: 自定义规则
            extends_list: 扩展配置列表
            plugins: 插件列表
            settings: 设置
            parser_options: 解析器选项
        
        Returns:
            ESLint配置字典
        """
        config = {
            "env": {},
            "extends": [],
            "parserOptions": {
                "ecmaVersion": ecma_version,
                "sourceType": source_type,
            },
            "plugins": [],
            "rules": {},
        }
        
        # 环境配置
        if environment == "browser":
            config["env"]["browser"] = True
            config["env"]["es2020"] = True
        elif environment == "node":
            config["env"]["node"] = True
            config["env"]["es2020"] = True
        
        # TypeScript配置
        if typescript:
            config["extends"].append("eslint:recommended")
            config["extends"].append("plugin:@typescript-eslint/recommended")
            config["plugins"].append("@typescript-eslint")
            config["parser"] = "@typescript-eslint/parser"
            config["rules"].update(self.presets.TYPESCRIPT_RULES)
        else:
            config["extends"].append("eslint:recommended")
        
        # 框架配置
        if framework == "react":
            config["extends"].append("plugin:react/recommended")
            config["extends"].append("plugin:react-hooks/recommended")
            config["plugins"].extend(["react", "react-hooks"])
            config["settings"] = {"react": {"version": "detect"}}
            config["parserOptions"]["ecmaFeatures"] = {"jsx": True}
            config["rules"].update(self.presets.REACT_RULES)
        
        elif framework == "vue":
            if typescript:
                config["extends"].append("plugin:vue/vue3-recommended")
                config["extends"].append("@vue/typescript/recommended")
            else:
                config["extends"].append("plugin:vue/vue3-recommended")
            config["plugins"].append("vue")
            config["rules"].update(self.presets.VUE_RULES)
        
        elif framework == "svelte":
            config["extends"].append("plugin:svelte/recommended")
            config["plugins"].append("svelte")
        
        # 通用最佳实践
        config["rules"].update(self.presets.BEST_PRACTICES)
        
        # 自定义规则
        if rules:
            config["rules"].update(rules)
        
        # 额外扩展
        if extends_list:
            config["extends"].extend(extends_list)
        
        # 额外插件
        if plugins:
            config["plugins"].extend(plugins)
        
        # 额外设置
        if settings:
            if "settings" not in config:
                config["settings"] = {}
            config["settings"].update(settings)
        
        # 解析器选项
        if parser_options:
            config["parserOptions"].update(parser_options)
        
        # 去重
        config["extends"] = list(dict.fromkeys(config["extends"]))
        config["plugins"] = list(dict.fromkeys(config["plugins"]))
        
        return config
    
    def generate_flat_config(
        self,
        framework: str = "vanilla",
        typescript: bool = False
    ) -> str:
        """
        生成新的Flat Config格式（ESLint v8+）
        
        Args:
            framework: 框架类型
            typescript: 是否使用TypeScript
        
        Returns:
            eslint.config.js内容
        """
        imports = ["import js from '@eslint/js';"]
        configs = ["js.configs.recommended"]
        
        if typescript:
            imports.append("import ts from 'typescript-eslint';")
            configs.append("...ts.configs.recommended")
        
        if framework == "react":
            imports.append("import react from 'eslint-plugin-react';")
            configs.append("react.configs.flat.recommended")
        
        if framework == "vue":
            imports.append("import vue from 'eslint-plugin-vue';")
            configs.append("vue.configs['flat/recommended']")
        
        config_js = "\n".join(imports) + "\n\n"
        config_js += "export default [\n"
        config_js += ",\n".join([f"  {c}" for c in configs])
        config_js += "\n];\n"
        
        return config_js
    
    def generate_ignore_config(self) -> List[str]:
        """生成忽略文件配置"""
        return [
            "node_modules/",
            "dist/",
            "build/",
            ".cache/",
            "coverage/",
            "*.min.js",
            "*.config.js",
            "*.config.ts",
        ]
    
    def get_install_command(
        self,
        framework: str = "vanilla",
        typescript: bool = False,
        package_manager: str = "npm"
    ) -> str:
        """获取安装命令"""
        deps = ["eslint"]
        
        if typescript:
            deps.extend(["typescript", "@typescript-eslint/parser", "@typescript-eslint/eslint-plugin"])
        
        if framework == "react":
            deps.extend(["eslint-plugin-react", "eslint-plugin-react-hooks"])
        elif framework == "vue":
            deps.append("eslint-plugin-vue")
            if typescript:
                deps.append("@vue/eslint-config-typescript")
        
        if package_manager == "npm":
            return f"npm install --save-dev {' '.join(deps)}"
        elif package_manager == "yarn":
            return f"yarn add --dev {' '.join(deps)}"
        elif package_manager == "pnpm":
            return f"pnpm add -D {' '.join(deps)}"
        
        return ""
    
    def save_config(self, config: Dict[str, Any], filepath: str) -> None:
        """保存配置到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)


class PrettierGenerator:
    """Prettier配置生成器"""
    
    def __init__(self):
        self.presets = PrettierPresets()
    
    def generate_config(
        self,
        semi: bool = True,
        single_quote: bool = True,
        tab_width: int = 2,
        trailing_comma: str = "es5",
        print_width: int = 100,
        bracket_spacing: bool = True,
        arrow_parens: str = "always",
        end_of_line: str = "lf",
        use_tabs: bool = False,
        jsx_single_quote: bool = False,
        bracket_same_line: bool = False,
        overrides: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        生成Prettier配置
        
        Args:
            semi: 是否使用分号
            single_quote: 是否使用单引号
            tab_width: 缩进宽度
            trailing_comma: 尾随逗号设置
            print_width: 打印宽度
            bracket_spacing: 括号间距
            arrow_parens: 箭头函数参数括号
            end_of_line: 行尾字符
            use_tabs: 使用制表符
            jsx_single_quote: JSX中使用单引号
            bracket_same_line: 多行标签的 > 放在最后一行
            overrides: 覆盖配置
        
        Returns:
            Prettier配置字典
        """
        config = {
            "semi": semi,
            "singleQuote": single_quote,
            "tabWidth": tab_width,
            "trailingComma": trailing_comma,
            "printWidth": print_width,
            "bracketSpacing": bracket_spacing,
            "arrowParens": arrow_parens,
            "endOfLine": end_of_line,
            "useTabs": use_tabs,
            "jsxSingleQuote": jsx_single_quote,
            "bracketSameLine": bracket_same_line,
        }
        
        if overrides:
            config["overrides"] = overrides
        
        return config
    
    def generate_from_preset(self, preset_name: str) -> Dict[str, Any]:
        """从预设生成配置"""
        return self.presets.get_preset(preset_name)
    
    def generate_ignore_config(self) -> List[str]:
        """生成忽略文件配置"""
        return [
            "node_modules/",
            "dist/",
            "build/",
            ".cache/",
            "coverage/",
            "*.min.js",
            "*.min.css",
            ".env*",
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
        ]
    
    def generate_integrated_script(self, package_manager: str = "npm") -> Dict[str, str]:
        """生成package.json中的脚本"""
        if package_manager == "npm":
            return {
                "format": "prettier --write .",
                "format:check": "prettier --check .",
                "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
                "lint:fix": "eslint . --ext .js,.jsx,.ts,.tsx --fix"
            }
        return {}
    
    def save_config(self, config: Dict[str, Any], filepath: str) -> None:
        """保存配置到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)


class IntegrationHelper:
    """ESLint和Prettier集成助手"""
    
    @staticmethod
    def generate_prettier_eslint_config(
        framework: str = "vanilla",
        typescript: bool = False
    ) -> Dict[str, Any]:
        """
        生成ESLint配置（包含Prettier集成）
        
        Args:
            framework: 框架类型
            typescript: 是否使用TypeScript
        
        Returns:
            ESLint配置字典
        """
        eslint_gen = ESLintGenerator()
        
        config = eslint_gen.generate_config(
            framework=framework,
            typescript=typescript
        )
        
        # 添加Prettier集成
        config["extends"].append("prettier")
        config["plugins"].append("prettier")
        config["rules"]["prettier/prettier"] = "error"
        
        # 去重
        config["extends"] = list(dict.fromkeys(config["extends"]))
        config["plugins"] = list(dict.fromkeys(config["plugins"]))
        
        return config
    
    @staticmethod
    def get_recommended_deps(
        framework: str = "vanilla",
        typescript: bool = False,
        package_manager: str = "npm"
    ) -> Dict[str, List[str]]:
        """获取推荐的依赖列表"""
        deps = {
            "eslint": ["eslint", "eslint-config-prettier", "eslint-plugin-prettier"],
            "prettier": ["prettier"],
        }
        
        if typescript:
            deps["eslint"].extend([
                "typescript",
                "@typescript-eslint/parser",
                "@typescript-eslint/eslint-plugin"
            ])
        
        if framework == "react":
            deps["eslint"].extend(["eslint-plugin-react", "eslint-plugin-react-hooks"])
        elif framework == "vue":
            deps["eslint"].append("eslint-plugin-vue")
            if typescript:
                deps["eslint"].append("@vue/eslint-config-typescript")
        
        return deps
    
    @staticmethod
    def generate_setup_guide(
        framework: str = "vanilla",
        typescript: bool = False,
        package_manager: str = "npm"
    ) -> List[str]:
        """生成设置指南"""
        guide = []
        
        # 安装依赖
        deps = IntegrationHelper.get_recommended_deps(framework, typescript, package_manager)
        all_deps = deps["eslint"] + deps["prettier"]
        
        if package_manager == "npm":
            install_cmd = f"npm install --save-dev {' '.join(all_deps)}"
        elif package_manager == "yarn":
            install_cmd = f"yarn add --dev {' '.join(all_deps)}"
        else:
            install_cmd = f"pnpm add -D {' '.join(all_deps)}"
        
        guide.extend([
            "# Setup ESLint and Prettier",
            "",
            "## 1. Install dependencies",
            install_cmd,
            "",
            "## 2. Create configuration files",
            "See generated .eslintrc.json and .prettierrc",
            "",
            "## 3. Add npm scripts to package.json",
            '"lint": "eslint . --ext .js,.jsx,.ts,.tsx"',
            '"lint:fix": "eslint . --ext .js,.jsx,.ts,.tsx --fix"',
            '"format": "prettier --write ."',
            "",
            "## 4. Setup IDE integration",
            "- VSCode: Install ESLint and Prettier extensions",
            "- Enable 'Format On Save' in settings",
            "- Configure ESLint to run on save",
        ])
        
        return guide


def main():
    """命令行入口"""
    eslint_gen = ESLintGenerator()
    prettier_gen = PrettierGenerator()
    
    if len(sys.argv) < 2:
        print(f"{Fore.CYAN}ESLint Prettier Skill v1.0.0{Style.RESET_ALL}")
        print("\nUsage:")
        print("  python main.py eslint [options]        - Generate ESLint config")
        print("  python main.py prettier [options]      - Generate Prettier config")
        print("  python main.py integrate [options]     - Generate integrated config")
        print("  python main.py ignore                  - Generate ignore files")
        print("  python main.py guide [options]         - Generate setup guide")
        print("\nExamples:")
        print('  python main.py eslint --framework react --typescript')
        print('  python main.py prettier --semi --single-quote')
        print('  python main.py integrate --framework vue')
        return
    
    command = sys.argv[1]
    
    if command == "eslint":
        framework = "vanilla"
        typescript = "--typescript" in sys.argv
        
        if "--framework" in sys.argv:
            idx = sys.argv.index("--framework")
            if idx + 1 < len(sys.argv):
                framework = sys.argv[idx + 1]
        
        config = eslint_gen.generate_config(framework=framework, typescript=typescript)
        print(f"{Fore.GREEN}{json.dumps(config, indent=2)}{Style.RESET_ALL}")
    
    elif command == "prettier":
        semi = "--no-semi" not in sys.argv
        single_quote = "--single-quote" in sys.argv or "--double-quote" not in sys.argv
        tab_width = 2
        
        if "--tab-width" in sys.argv:
            idx = sys.argv.index("--tab-width")
            if idx + 1 < len(sys.argv):
                tab_width = int(sys.argv[idx + 1])
        
        config = prettier_gen.generate_config(semi=semi, single_quote=single_quote, tab_width=tab_width)
        print(f"{Fore.GREEN}{json.dumps(config, indent=2)}{Style.RESET_ALL}")
    
    elif command == "integrate":
        framework = "vanilla"
        typescript = "--typescript" in sys.argv
        
        if "--framework" in sys.argv:
            idx = sys.argv.index("--framework")
            if idx + 1 < len(sys.argv):
                framework = sys.argv[idx + 1]
        
        config = IntegrationHelper.generate_prettier_eslint_config(framework, typescript)
        print(f"{Fore.GREEN}{json.dumps(config, indent=2)}{Style.RESET_ALL}")
    
    elif command == "ignore":
        print(f"{Fore.CYAN}.eslintignore:{Style.RESET_ALL}")
        for line in eslint_gen.generate_ignore_config():
            print(line)
        
        print(f"\n{Fore.CYAN}.prettierignore:{Style.RESET_ALL}")
        for line in prettier_gen.generate_ignore_config():
            print(line)
    
    elif command == "guide":
        framework = "vanilla"
        typescript = "--typescript" in sys.argv
        
        if "--framework" in sys.argv:
            idx = sys.argv.index("--framework")
            if idx + 1 < len(sys.argv):
                framework = sys.argv[idx + 1]
        
        guide = IntegrationHelper.generate_setup_guide(framework, typescript)
        print(f"{Fore.GREEN}{chr(10).join(guide)}{Style.RESET_ALL}")
    
    else:
        print(f"{Fore.RED}Unknown command: {command}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
