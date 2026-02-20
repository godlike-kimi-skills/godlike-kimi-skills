#!/usr/bin/env python3
"""Tailwind CSS Skill - 配置生成示例"""

import sys
sys.path.insert(0, '..')

from main import TailwindGenerator
import json

def main():
    generator = TailwindGenerator()
    
    print("=" * 70)
    print("Tailwind CSS Skill - 配置生成示例")
    print("=" * 70)
    
    # 示例1: 基本配置
    print("\n1. 基本配置")
    print("-" * 50)
    
    basic_config = generator.generate_config(
        content=[
            "./src/**/*.{js,jsx,ts,tsx}",
            "./public/index.html"
        ]
    )
    print(json.dumps(basic_config, indent=2))
    
    # 示例2: 带主题扩展的配置
    print("\n2. 带主题扩展的配置")
    print("-" * 50)
    
    theme_config = generator.generate_config(
        content=["./src/**/*.{vue,js}"],
        theme_extensions={
            "colors": {
                "brand": {
                    "50": "#eff6ff",
                    "100": "#dbeafe",
                    "500": "#3b82f6",
                    "600": "#2563eb",
                    "900": "#1e3a8a"
                }
            },
            "fontFamily": {
                "sans": ["Inter", "sans-serif"],
                "display": ["Poppins", "sans-serif"]
            },
            "spacing": {
                "18": "4.5rem",
                "88": "22rem"
            }
        }
    )
    print(json.dumps(theme_config, indent=2))
    
    # 示例3: 颜色工具使用
    print("\n3. 颜色生成工具")
    print("-" * 50)
    
    colors_to_generate = [
        ("blue", 500, "bg"),
        ("red", 600, "text"),
        ("green", 500, "border", 50),
        ("purple", 700, "ring"),
    ]
    
    for color, shade, type_, *opacity in colors_to_generate:
        if opacity:
            cls = generator.generate_color(color, shade, type_, opacity[0])
        else:
            cls = generator.generate_color(color, shade, type_)
        print(f"  颜色 {color}-{shade} ({type_}): {cls}")
    
    # 示例4: 间距工具使用
    print("\n4. 间距生成工具")
    print("-" * 50)
    
    spacing_examples = [
        ("4", "m", "all"),
        ("6", "p", "x"),
        ("8", "m", "y"),
        ("2", "p", "t"),
        ("auto", "m", "x"),
    ]
    
    for size, type_, direction in spacing_examples:
        cls = generator.generate_spacing(size, type_, direction)
        print(f"  间距 ({type_}, {direction}): {cls}")
    
    # 示例5: Flexbox工具
    print("\n5. Flexbox生成工具")
    print("-" * 50)
    
    flex_configs = [
        ("row", "between", "center", "wrap", "4"),
        ("col", "center", "start", "nowrap", "2"),
        ("row-reverse", "end", "end", "wrap", "6"),
    ]
    
    for direction, justify, align, wrap, gap in flex_configs:
        classes = generator.generate_flex(direction, justify, align, wrap, gap)
        print(f"  Flex ({direction}, {justify}, {align}): {classes}")
    
    # 示例6: 排版工具
    print("\n6. 排版生成工具")
    print("-" * 50)
    
    typography_configs = [
        ("xs", "normal", None, "left"),
        ("lg", "semibold", "gray-800", "center"),
        ("2xl", "bold", "blue-600", "left"),
        ("4xl", "extrabold", None, "center"),
    ]
    
    for size, weight, color, align in typography_configs:
        classes = generator.generate_typography(size, weight, color, align)
        print(f"  排版 ({size}, {weight}): {classes}")
    
    print("\n" + "=" * 70)
    print("示例运行完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
