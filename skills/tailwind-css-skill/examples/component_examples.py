#!/usr/bin/env python3
"""Tailwind CSS Skill - 组件生成示例"""

import sys
sys.path.insert(0, '..')

from main import TailwindGenerator

def main():
    generator = TailwindGenerator()
    
    print("=" * 60)
    print("Tailwind CSS Skill - 组件生成示例")
    print("=" * 60)
    
    # 示例1: 按钮组件
    print("\n1. 按钮组件 (Button)")
    print("-" * 40)
    
    variants = ["primary", "secondary", "danger", "ghost", "outline"]
    sizes = ["sm", "md", "lg"]
    
    for variant in variants:
        for size in sizes:
            classes = generator.generate_component("button", variant, size)
            print(f"  [{variant}/{size}]: {classes[:60]}...")
    
    # 示例2: 卡片组件
    print("\n2. 卡片组件 (Card)")
    print("-" * 40)
    
    card_variants = ["default", "outlined", "elevated", "interactive"]
    for variant in card_variants:
        classes = generator.generate_component("card", variant, "md")
        print(f"  [{variant}]: {classes}")
    
    # 示例3: 输入框组件
    print("\n3. 输入框组件 (Input)")
    print("-" * 40)
    
    input_variants = ["default", "error", "success"]
    for variant in input_variants:
        classes = generator.generate_component("input", variant, "md")
        print(f"  [{variant}]: {classes[:70]}...")
    
    # 示例4: 标签组件
    print("\n4. 标签组件 (Badge)")
    print("-" * 40)
    
    badge_variants = ["default", "primary", "success", "warning", "danger", "purple"]
    for variant in badge_variants:
        classes = generator.generate_component("badge", variant, "md")
        print(f"  [{variant}]: {classes}")
    
    # 示例5: 警告框组件
    print("\n5. 警告框组件 (Alert)")
    print("-" * 40)
    
    alert_variants = ["info", "success", "warning", "error"]
    for variant in alert_variants:
        classes = generator.generate_component("alert", variant, "md")
        print(f"  [{variant}]: {classes}")
    
    # 示例6: 状态变体
    print("\n6. 按钮状态 (Button States)")
    print("-" * 40)
    
    states = [None, "disabled", "loading"]
    for state in states:
        classes = generator.generate_component("button", "primary", "md", state)
        state_label = state or "normal"
        print(f"  [{state_label}]: {classes[:60]}...")
    
    print("\n" + "=" * 60)
    print("示例运行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
