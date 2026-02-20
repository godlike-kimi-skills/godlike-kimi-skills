#!/usr/bin/env python3
"""Tailwind CSS Skill - 响应式设计示例"""

import sys
sys.path.insert(0, '..')

from main import TailwindGenerator

def main():
    generator = TailwindGenerator()
    
    print("=" * 70)
    print("Tailwind CSS Skill - 响应式设计示例")
    print("=" * 70)
    
    # 示例1: 响应式网格
    print("\n1. 响应式网格布局")
    print("-" * 50)
    
    grid_configs = [
        {"default": 1, "md": 2, "lg": 3},
        {"default": 1, "sm": 2, "md": 3, "lg": 4},
        {"default": 1, "md": 2, "lg": 3, "xl": 5},
    ]
    
    for i, cols in enumerate(grid_configs, 1):
        classes = generator.generate_grid(cols, gap="6")
        print(f"  配置 {i}: {classes}")
    
    # 示例2: 响应式字体大小
    print("\n2. 响应式字体")
    print("-" * 50)
    
    typography = {
        "default": "text-sm",
        "md": "text-base",
        "lg": "text-lg",
        "xl": "text-xl"
    }
    classes = generator.generate_responsive(typography)
    print(f"  标题字体: {classes}")
    
    # 示例3: 响应式显示/隐藏
    print("\n3. 响应式显示控制")
    print("-" * 50)
    
    display_configs = [
        {"default": "hidden", "md": "block"},
        {"default": "block", "lg": "hidden"},
    ]
    
    for config in display_configs:
        classes = generator.generate_responsive(config)
        print(f"  显示规则: {classes}")
    
    # 示例4: 响应式间距
    print("\n4. 响应式间距")
    print("-" * 50)
    
    spacing_configs = [
        {"default": "p-4", "md": "p-8", "lg": "p-12"},
        {"default": "gap-2", "sm": "gap-4", "lg": "gap-8"},
    ]
    
    for config in spacing_configs:
        classes = generator.generate_responsive(config)
        print(f"  间距规则: {classes}")
    
    # 示例5: 响应式Flex方向
    print("\n5. 响应式Flex方向")
    print("-" * 50)
    
    flex_configs = [
        {"default": "flex-col", "md": "flex-row"},
        {"default": "flex-row", "lg": "flex-col"},
    ]
    
    for config in flex_configs:
        classes = generator.generate_responsive(config)
        print(f"  Flex方向: {classes}")
    
    # 示例6: 完整响应式布局
    print("\n6. 完整响应式布局组合")
    print("-" * 50)
    
    container_classes = generator.generate_responsive({
        "default": "px-4",
        "sm": "px-6",
        "lg": "px-8"
    })
    print(f"  容器内边距: {container_classes}")
    
    max_width_classes = generator.generate_responsive({
        "default": "max-w-full",
        "md": "max-w-3xl",
        "lg": "max-w-5xl",
        "xl": "max-w-7xl"
    })
    print(f"  最大宽度: {max_width_classes}")
    
    sidebar_classes = generator.generate_responsive({
        "default": "hidden",
        "lg": "block w-64"
    })
    print(f"  侧边栏: {sidebar_classes}")
    
    print("\n" + "=" * 70)
    print("示例运行完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
