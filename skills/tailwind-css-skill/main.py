#!/usr/bin/env python3
"""
Tailwind CSS Skill - 样式生成与管理工具
支持类名生成、响应式设计、自定义配置
"""

import json
import re
import sys
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from colorama import init, Fore, Style

init()


@dataclass
class ComponentStyle:
    """组件样式数据类"""
    base: str
    variants: Dict[str, str]
    sizes: Dict[str, str]
    states: Dict[str, str]


class ComponentPresets:
    """预设组件样式库"""
    
    BUTTON = ComponentStyle(
        base="inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2",
        variants={
            "primary": "bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500 active:bg-blue-800",
            "secondary": "bg-gray-200 hover:bg-gray-300 text-gray-800 focus:ring-gray-500 active:bg-gray-400",
            "danger": "bg-red-600 hover:bg-red-700 text-white focus:ring-red-500 active:bg-red-800",
            "ghost": "bg-transparent hover:bg-gray-100 text-gray-700 focus:ring-gray-400 active:bg-gray-200",
            "outline": "border-2 border-gray-300 hover:border-gray-400 bg-transparent text-gray-700 hover:bg-gray-50",
            "link": "bg-transparent text-blue-600 hover:text-blue-800 hover:underline focus:ring-blue-400"
        },
        sizes={
            "xs": "px-2 py-1 text-xs rounded",
            "sm": "px-3 py-1.5 text-sm rounded-md",
            "md": "px-4 py-2 text-base rounded-lg",
            "lg": "px-6 py-3 text-lg rounded-xl",
            "xl": "px-8 py-4 text-xl rounded-2xl"
        },
        states={
            "disabled": "opacity-50 cursor-not-allowed",
            "loading": "cursor-wait opacity-75",
            "active": "transform scale-95"
        }
    )
    
    CARD = ComponentStyle(
        base="bg-white overflow-hidden",
        variants={
            "default": "border border-gray-200 rounded-lg shadow-sm",
            "outlined": "border-2 border-gray-300 rounded-lg",
            "elevated": "rounded-xl shadow-lg",
            "flat": "border border-gray-200 rounded-lg",
            "interactive": "border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer"
        },
        sizes={
            "sm": "p-4",
            "md": "p-6",
            "lg": "p-8"
        },
        states={
            "hover": "hover:shadow-lg",
            "active": "ring-2 ring-blue-500"
        }
    )
    
    INPUT = ComponentStyle(
        base="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 transition-colors",
        variants={
            "default": "border",
            "error": "border-red-500 focus:ring-red-500 focus:border-red-500 text-red-900 placeholder-red-300",
            "success": "border-green-500 focus:ring-green-500 focus:border-green-500",
            "warning": "border-yellow-500 focus:ring-yellow-500 focus:border-yellow-500"
        },
        sizes={
            "sm": "px-3 py-1.5 text-sm",
            "md": "px-4 py-2 text-base",
            "lg": "px-6 py-3 text-lg"
        },
        states={
            "disabled": "bg-gray-100 cursor-not-allowed opacity-75",
            "readonly": "bg-gray-50",
            "focus": "ring-2"
        }
    )
    
    BADGE = ComponentStyle(
        base="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
        variants={
            "default": "bg-gray-100 text-gray-800",
            "primary": "bg-blue-100 text-blue-800",
            "success": "bg-green-100 text-green-800",
            "warning": "bg-yellow-100 text-yellow-800",
            "danger": "bg-red-100 text-red-800",
            "info": "bg-cyan-100 text-cyan-800",
            "purple": "bg-purple-100 text-purple-800",
            "pink": "bg-pink-100 text-pink-800"
        },
        sizes={
            "sm": "px-2 py-0.5 text-xs",
            "md": "px-2.5 py-0.5 text-xs",
            "lg": "px-3 py-1 text-sm"
        },
        states={
            "dot": "before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:mr-1.5"
        }
    )
    
    ALERT = ComponentStyle(
        base="p-4 rounded-lg",
        variants={
            "info": "bg-blue-50 border border-blue-200 text-blue-800",
            "success": "bg-green-50 border border-green-200 text-green-800",
            "warning": "bg-yellow-50 border border-yellow-200 text-yellow-800",
            "error": "bg-red-50 border border-red-200 text-red-800"
        },
        sizes={
            "sm": "p-3 text-sm",
            "md": "p-4 text-base",
            "lg": "p-6 text-lg"
        },
        states={
            "dismissible": "pr-10 relative",
            "icon": "flex items-start gap-3"
        }
    )


class TailwindGenerator:
    """Tailwind CSS 样式生成器"""
    
    # 标准断点
    BREAKPOINTS = {
        "sm": "640px",
        "md": "768px",
        "lg": "1024px",
        "xl": "1280px",
        "2xl": "1536px"
    }
    
    # 间距比例
    SPACING_SCALE = {
        "0": "0px", "0.5": "2px", "1": "4px", "1.5": "6px",
        "2": "8px", "2.5": "10px", "3": "12px", "3.5": "14px",
        "4": "16px", "5": "20px", "6": "24px", "7": "28px",
        "8": "32px", "9": "36px", "10": "40px", "11": "44px",
        "12": "48px", "14": "56px", "16": "64px", "20": "80px",
        "24": "96px", "28": "112px", "32": "128px", "36": "144px",
        "40": "160px", "44": "176px", "48": "192px", "52": "208px",
        "56": "224px", "60": "240px", "64": "256px", "72": "288px",
        "80": "320px", "96": "384px"
    }
    
    # 颜色调色板
    COLOR_PALETTE = [
        "slate", "gray", "zinc", "neutral", "stone",
        "red", "orange", "amber", "yellow", "lime",
        "green", "emerald", "teal", "cyan", "sky",
        "blue", "indigo", "violet", "purple", "fuchsia",
        "pink", "rose"
    ]
    
    # 颜色色阶
    COLOR_SHADES = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]
    
    def __init__(self):
        self.presets = {
            "button": ComponentPresets.BUTTON,
            "card": ComponentPresets.CARD,
            "input": ComponentPresets.INPUT,
            "badge": ComponentPresets.BADGE,
            "alert": ComponentPresets.ALERT
        }
    
    def generate_component(
        self,
        component_type: str,
        variant: str = "default",
        size: str = "md",
        state: Optional[str] = None,
        extra_classes: Optional[List[str]] = None
    ) -> str:
        """生成组件类名"""
        if component_type not in self.presets:
            available = ", ".join(self.presets.keys())
            raise ValueError(f"Unknown component type: {component_type}. Available: {available}")
        
        preset = self.presets[component_type]
        classes = [preset.base]
        
        if variant in preset.variants:
            classes.append(preset.variants[variant])
        
        if size in preset.sizes:
            classes.append(preset.sizes[size])
        
        if state and state in preset.states:
            classes.append(preset.states[state])
        
        if extra_classes:
            classes.extend(extra_classes)
        
        return " ".join(classes)
    
    def generate_responsive(
        self,
        classes: Dict[str, str],
        mobile_first: bool = True
    ) -> str:
        """生成响应式类名"""
        result = []
        
        for breakpoint, class_str in classes.items():
            if breakpoint == "default" or breakpoint == "mobile":
                result.append(class_str)
            elif breakpoint in self.BREAKPOINTS:
                prefix = f"{breakpoint}:"
                for cls in class_str.split():
                    result.append(f"{prefix}{cls}")
        
        return " ".join(result)
    
    def generate_grid(self, cols: Dict[str, int], gap: str = "4") -> str:
        """生成网格布局类名"""
        classes = ["grid"]
        
        for breakpoint, col_count in cols.items():
            if breakpoint == "default":
                classes.append(f"grid-cols-{col_count}")
            else:
                classes.append(f"{breakpoint}:grid-cols-{col_count}")
        
        classes.append(f"gap-{gap}")
        
        return " ".join(classes)
    
    def generate_flex(
        self,
        direction: str = "row",
        justify: str = "start",
        align: str = "center",
        wrap: str = "nowrap",
        gap: Optional[str] = None
    ) -> str:
        """生成Flexbox布局类名"""
        classes = ["flex"]
        
        if direction != "row":
            classes.append(f"flex-{direction}")
        
        if justify != "start":
            classes.append(f"justify-{justify}")
        
        if align != "stretch":
            classes.append(f"items-{align}")
        
        if wrap != "nowrap":
            classes.append(f"flex-{wrap}")
        
        if gap:
            classes.append(f"gap-{gap}")
        
        return " ".join(classes)
    
    def generate_color(
        self,
        base: str,
        shade: int = 500,
        type_: str = "bg",
        opacity: Optional[int] = None
    ) -> str:
        """生成颜色类名"""
        if shade not in self.COLOR_SHADES:
            raise ValueError(f"Invalid shade: {shade}. Must be one of {self.COLOR_SHADES}")
        
        class_name = f"{type_}-{base}-{shade}"
        
        if opacity is not None:
            class_name = f"{class_name}/{opacity}"
        
        return class_name
    
    def generate_spacing(
        self,
        size: str,
        type_: str = "m",
        direction: str = "all"
    ) -> str:
        """生成间距类名"""
        if direction == "all":
            return f"{type_}-{size}"
        elif direction in ["x", "y"]:
            return f"{type_}{direction}-{size}"
        else:
            direction_map = {"t": "t", "r": "r", "b": "b", "l": "l"}
            if direction in direction_map:
                return f"{type_}{direction_map[direction]}-{size}"
        
        raise ValueError(f"Invalid direction: {direction}")
    
    def generate_config(
        self,
        content: List[str] = None,
        theme_extensions: Dict[str, Any] = None,
        plugins: List[str] = None
    ) -> Dict[str, Any]:
        """生成Tailwind配置文件"""
        if content is None:
            content = [
                "./src/**/*.{js,jsx,ts,tsx,vue}",
                "./public/index.html"
            ]
        
        config = {
            "content": content,
            "theme": {
                "extend": theme_extensions or {}
            },
            "plugins": plugins or []
        }
        
        return config
    
    def generate_typography(
        self,
        size: str = "base",
        weight: str = "normal",
        color: Optional[str] = None,
        align: str = "left"
    ) -> str:
        """生成排版类名"""
        classes = [f"text-{size}"]
        
        if weight != "normal":
            classes.append(f"font-{weight}")
        
        if color:
            classes.append(f"text-{color}")
        
        if align != "left":
            classes.append(f"text-{align}")
        
        return " ".join(classes)
    
    def optimize_classes(self, classes: str) -> str:
        """优化类名字符串（去重、排序）"""
        class_list = classes.split()
        
        seen = set()
        unique_classes = []
        for cls in class_list:
            if cls not in seen:
                seen.add(cls)
                unique_classes.append(cls)
        
        return " ".join(unique_classes)
    
    def validate_classes(self, classes: str) -> Dict[str, any]:
        """验证类名有效性"""
        class_list = classes.split()
        valid = []
        invalid = []
        
        valid_prefixes = [
            "bg-", "text-", "border-", "p-", "m-", "px-", "py-", "mx-", "my-",
            "pt-", "pr-", "pb-", "pl-", "mt-", "mr-", "mb-", "ml-",
            "w-", "h-", "min-w-", "min-h-", "max-w-", "max-h-",
            "grid", "flex", "block", "inline", "hidden",
            "rounded", "shadow", "ring", "opacity",
            "font-", "tracking-", "leading-",
            "transition", "duration", "ease-", "delay-",
            "transform", "scale-", "rotate-", "translate-", "skew-",
            "hover:", "focus:", "active:", "disabled:", "group-hover:",
            "sm:", "md:", "lg:", "xl:", "2xl:"
        ]
        
        for cls in class_list:
            is_valid = any(
                cls.startswith(prefix) or cls == prefix.rstrip(":")
                for prefix in valid_prefixes
            ) or cls in ["container", "mx-auto", "truncate", "uppercase", "lowercase", "capitalize"]
            
            if is_valid:
                valid.append(cls)
            else:
                invalid.append(cls)
        
        return {
            "valid": valid,
            "invalid": invalid,
            "valid_count": len(valid),
            "invalid_count": len(invalid)
        }
    
    def get_suggestions(self, prefix: str) -> List[str]:
        """根据前缀获取类名建议"""
        suggestions = []
        
        if prefix in ["bg", "text", "border"]:
            for color in self.COLOR_PALETTE[:10]:
                suggestions.extend([
                    f"{prefix}-{color}-500",
                    f"{prefix}-{color}-600",
                    f"{prefix}-{color}-700"
                ])
        
        elif prefix in ["p", "m", "px", "py", "mx", "my"]:
            for size in ["2", "4", "6", "8", "12", "16"]:
                suggestions.append(f"{prefix}-{size}")
        
        elif prefix in ["w", "h"]:
            suggestions.extend([
                f"{prefix}-full", f"{prefix}-screen", f"{prefix}-auto",
                f"{prefix}-1/2", f"{prefix}-1/3", f"{prefix}-2/3",
                f"{prefix}-1/4", f"{prefix}-3/4"
            ])
        
        return suggestions[:15]
    
    def save_config(self, config: Dict[str, Any], filepath: str) -> None:
        """保存配置到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("/** @type {import('tailwindcss').Config} */\n")
            f.write("module.exports = ")
            json_str = json.dumps(config, indent=2, ensure_ascii=False)
            json_str = json_str.replace('"', "'")
            f.write(json_str)
            f.write("\n")


def main():
    """命令行入口"""
    generator = TailwindGenerator()
    
    if len(sys.argv) < 2:
        print(f"{Fore.CYAN}Tailwind CSS Skill v1.0.0{Style.RESET_ALL}")
        print("\nUsage:")
        print("  python main.py component <type> [variant] [size] - Generate component classes")
        print("  python main.py responsive <default> <sm> <md> <lg> - Generate responsive classes")
        print("  python main.py flex [direction] [justify] [align] - Generate flex classes")
        print("  python main.py grid <cols> [gap] - Generate grid classes")
        print("  python main.py validate <classes> - Validate class names")
        print("\nExamples:")
        print('  python main.py component button primary md')
        print('  python main.py responsive "grid-cols-1" "" "md:grid-cols-2" "lg:grid-cols-4"')
        print('  python main.py flex row center center')
        return
    
    command = sys.argv[1]
    
    if command == "component":
        if len(sys.argv) < 3:
            print(f"{Fore.RED}Error: Component type required{Style.RESET_ALL}")
            return
        comp_type = sys.argv[2]
        variant = sys.argv[3] if len(sys.argv) > 3 else "default"
        size = sys.argv[4] if len(sys.argv) > 4 else "md"
        
        try:
            classes = generator.generate_component(comp_type, variant, size)
            print(f"{Fore.GREEN}{classes}{Style.RESET_ALL}")
        except ValueError as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    
    elif command == "responsive":
        if len(sys.argv) < 6:
            print(f"{Fore.RED}Error: Need default, sm, md, lg classes{Style.RESET_ALL}")
            return
        classes = {
            "default": sys.argv[2] if sys.argv[2] else None,
            "sm": sys.argv[3] if sys.argv[3] else None,
            "md": sys.argv[4] if sys.argv[4] else None,
            "lg": sys.argv[5] if len(sys.argv) > 5 else None
        }
        classes = {k: v for k, v in classes.items() if v}
        result = generator.generate_responsive(classes)
        print(f"{Fore.GREEN}{result}{Style.RESET_ALL}")
    
    elif command == "flex":
        direction = sys.argv[2] if len(sys.argv) > 2 else "row"
        justify = sys.argv[3] if len(sys.argv) > 3 else "start"
        align = sys.argv[4] if len(sys.argv) > 4 else "center"
        classes = generator.generate_flex(direction, justify, align)
        print(f"{Fore.GREEN}{classes}{Style.RESET_ALL}")
    
    elif command == "grid":
        cols = sys.argv[2] if len(sys.argv) > 2 else "1"
        gap = sys.argv[3] if len(sys.argv) > 3 else "4"
        print(f"{Fore.GREEN}grid grid-cols-{cols} gap-{gap}{Style.RESET_ALL}")
    
    elif command == "validate":
        if len(sys.argv) < 3:
            print(f"{Fore.RED}Error: Classes string required{Style.RESET_ALL}")
            return
        classes = " ".join(sys.argv[2:])
        result = generator.validate_classes(classes)
        print(f"{Fore.GREEN}Valid ({result['valid_count']}):{Style.RESET_ALL} {' '.join(result['valid'])}")
        if result['invalid']:
            print(f"{Fore.YELLOW}Invalid ({result['invalid_count']}):{Style.RESET_ALL} {' '.join(result['invalid'])}")
    
    else:
        print(f"{Fore.RED}Unknown command: {command}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
