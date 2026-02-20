#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例1 / Usage Example 1

展示技能的基本用法 / Demonstrate basic usage of the skill
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from main import process


def main():
    """
    示例：基础使用场景
    Example: Basic usage scenario
    """
    print("=" * 60)
    print("示例1: 基础使用 / Example 1: Basic Usage")
    print("=" * 60)
    print()
    
    # 中文：准备输入参数
    # English: Prepare input parameters
    params = {
        "required_param": "示例值 / Example value",
        # "optional_param": "可选值 / Optional value"
    }
    
    print("输入参数 / Input parameters:")
    print(f"  {params}")
    print()
    
    # 中文：执行处理
    # English: Execute processing
    result = process(params)
    
    print("输出结果 / Output result:")
    print(f"  状态 / Status: {result['status']}")
    print(f"  消息 / Message: {result['message']}")
    print(f"  数据 / Data: {result['data']}")
    
    print()
    print("=" * 60)


if __name__ == '__main__':
    main()
