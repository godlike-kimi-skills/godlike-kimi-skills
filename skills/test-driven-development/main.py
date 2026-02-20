#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Driven Development (TDD) Skill
测试驱动开发方法论指导工具

提供完整的TDD工作流指导、测试用例生成、代码覆盖率分析和测试模板生成。
"""

import argparse
import os
import sys
import subprocess
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from string import Template

# TDD工作流指导内容
TDD_WORKFLOW_GUIDE = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    测试驱动开发 (TDD) 方法论指导                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

📌 TDD 核心原则：
   1. 测试优先：先写测试，后写实现代码
   2. 小步快跑：每次只关注一个小功能点
   3. 快速反馈：通过测试快速验证代码正确性
   4. 持续重构：在测试保护下不断优化代码

🔄 TDD 循环（红-绿-重构）：

   ┌─────────┐    ┌─────────┐    ┌─────────┐
   │  编写    │ → │  运行    │ → │  看到    │
   │  测试    │    │  测试    │    │  失败    │
   └─────────┘    └────┬────┘    └────┬────┘
        ↑              │ FAIL         │
        │              ↓              │
   ┌────┴────┐    ┌─────────┐         │
   │  重构    │ ← │  看到    │         │
   │  代码    │    │  通过    │         │
   └────┬────┘    └────┬────┘         │
        ↑           PASS│              │
        │              ↓               │
        └──────── ┌─────────┐ ←───────┘
                  │  编写    │
                  │  代码    │
                  └─────────┘

📝 当前任务：{feature}

🎯 第一步：编写失败的测试（Red）
   □ 分析需求，确定功能边界
   □ 设计测试用例（正常情况、边界情况、异常情况）
   □ 编写最简单的测试代码
   □ 运行测试，确认测试失败（红色）

🎯 第二步：编写最简代码通过测试（Green）
   □ 编写最简单的实现代码
   □ 目标：让测试通过，不求完美
   □ 可以使用硬编码、简化逻辑
   □ 运行测试，确认测试通过（绿色）

🎯 第三步：重构代码（Refactor）
   □ 消除重复代码
   □ 优化命名和结构
   □ 保持测试通过
   □ 遵循SOLID原则

💡 测试用例设计原则（AAA模式）：
   • Arrange（准备）：设置测试数据和前置条件
   • Act（执行）：调用被测试的功能
   • Assert（断言）：验证结果是否符合预期

⚠️  常见反模式：
   ✗ 测试代码中存在逻辑判断
   ✗ 一个测试验证多个功能点
   ✗ 测试依赖外部资源（数据库、网络）
   ✗ 测试代码与实现代码耦合
"""

# 测试框架配置
TEST_FRAMEWORKS = {
    "python": {
        "pytest": {
            "install": "pip install pytest pytest-cov",
            "run": "pytest {test_path} -v --cov={source_path} --cov-report=term-missing",
            "extension": "py"
        },
        "unittest": {
            "install": "pip install coverage",
            "run": "python -m unittest {test_path} -v",
            "extension": "py"
        }
    },
    "javascript": {
        "jest": {
            "install": "npm install --save-dev jest",
            "run": "npx jest {test_path} --coverage",
            "extension": "js"
        },
        "mocha": {
            "install": "npm install --save-dev mocha chai",
            "run": "npx mocha {test_path}",
            "extension": "js"
        }
    },
    "typescript": {
        "jest": {
            "install": "npm install --save-dev jest @types/jest ts-jest",
            "run": "npx jest {test_path} --coverage",
            "extension": "ts"
        }
    },
    "java": {
        "junit": {
            "install": "Maven: junit:junit:4.13.2 或 JUnit 5",
            "run": "mvn test",
            "extension": "java"
        },
        "testng": {
            "install": "Maven: org.testng:testng:7.8.0",
            "run": "mvn test",
            "extension": "java"
        }
    },
    "go": {
        "builtin": {
            "install": "内置测试框架",
            "run": "go test -v -cover ./...",
            "extension": "go"
        }
    },
    "rust": {
        "builtin": {
            "install": "内置测试框架",
            "run": "cargo test",
            "extension": "rs"
        }
    },
    "cpp": {
        "gtest": {
            "install": "安装 Google Test",
            "run": "运行编译后的测试可执行文件",
            "extension": "cpp"
        },
        "catch2": {
            "install": "安装 Catch2",
            "run": "运行编译后的测试可执行文件",
            "extension": "cpp"
        }
    }
}

# 测试模板
TEST_TEMPLATES = {
    "python": {
        "pytest": '''import pytest
from ${module_name} import ${class_name}


class Test${class_name}:
    """${class_name} 测试类"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.instance = ${class_name}()
    
    def teardown_method(self):
        """每个测试方法后执行"""
        pass
    
    def test_${method_name}_normal_case(self):
        """测试正常情况"""
        # Arrange
        input_data = None
        expected = None
        
        # Act
        result = self.instance.${method_name}(input_data)
        
        # Assert
        assert result == expected
    
    def test_${method_name}_edge_case(self):
        """测试边界情况"""
        # Arrange
        input_data = None
        expected = None
        
        # Act
        result = self.instance.${method_name}(input_data)
        
        # Assert
        assert result == expected
    
    def test_${method_name}_invalid_input(self):
        """测试无效输入"""
        # Arrange
        input_data = None
        
        # Act & Assert
        with pytest.raises(ValueError):
            self.instance.${method_name}(input_data)
''',
        "unittest": '''import unittest
from ${module_name} import ${class_name}


class Test${class_name}(unittest.TestCase):
    """${class_name} 测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.instance = ${class_name}()
    
    def tearDown(self):
        """测试后清理"""
        pass
    
    def test_${method_name}_normal_case(self):
        """测试正常情况"""
        # Arrange
        input_data = None
        expected = None
        
        # Act
        result = self.instance.${method_name}(input_data)
        
        # Assert
        self.assertEqual(result, expected)
    
    def test_${method_name}_edge_case(self):
        """测试边界情况"""
        # Arrange
        input_data = None
        expected = None
        
        # Act
        result = self.instance.${method_name}(input_data)
        
        # Assert
        self.assertEqual(result, expected)
    
    def test_${method_name}_invalid_input(self):
        """测试无效输入"""
        # Arrange
        input_data = None
        
        # Act & Assert
        with self.assertRaises(ValueError):
            self.instance.${method_name}(input_data)


if __name__ == '__main__':
    unittest.main()
'''
    },
    "javascript": {
        "jest": '''const ${class_name} = require('${module_path}');

describe('${class_name}', () => {{
    let instance;
    
    beforeEach(() => {{
        instance = new ${class_name}();
    }});
    
    afterEach(() => {{
        // 清理工作
    }});
    
    describe('${method_name}', () => {{
        test('should handle normal case', () => {{
            // Arrange
            const input = null;
            const expected = null;
            
            // Act
            const result = instance.${method_name}(input);
            
            // Assert
            expect(result).toBe(expected);
        }});
        
        test('should handle edge case', () => {{
            // Arrange
            const input = null;
            const expected = null;
            
            // Act
            const result = instance.${method_name}(input);
            
            // Assert
            expect(result).toBe(expected);
        }});
        
        test('should throw error for invalid input', () => {{
            // Arrange
            const input = null;
            
            // Act & Assert
            expect(() => instance.${method_name}(input)).toThrow();
        }});
    }});
}});
'''
    },
    "java": {
        "junit": '''package ${package_name};

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class ${class_name}Test {{
    
    private ${class_name} instance;
    
    @BeforeEach
    void setUp() {{
        instance = new ${class_name}();
    }}
    
    @AfterEach
    void tearDown() {{
        // 清理工作
    }}
    
    @Test
    void test${method_name_pascal}NormalCase() {{
        // Arrange
        Object input = null;
        Object expected = null;
        
        // Act
        Object result = instance.${method_name}(input);
        
        // Assert
        assertEquals(expected, result);
    }}
    
    @Test
    void test${method_name_pascal}EdgeCase() {{
        // Arrange
        Object input = null;
        Object expected = null;
        
        // Act
        Object result = instance.${method_name}(input);
        
        // Assert
        assertEquals(expected, result);
    }}
    
    @Test
    void test${method_name_pascal}InvalidInput() {{
        // Arrange
        Object input = null;
        
        // Act & Assert
        assertThrows(IllegalArgumentException.class, () -> {{
            instance.${method_name}(input);
        }});
    }}
}}
'''
    }
}


class TDDManager:
    """TDD管理器类"""
    
    def __init__(self, language: str = "python", test_framework: str = "pytest"):
        self.language = language
        self.test_framework = test_framework
    
    def show_workflow_guide(self, feature: str = "") -> str:
        """显示TDD工作流指导"""
        guide = TDD_WORKFLOW_GUIDE.format(feature=feature or "实现新功能")
        return guide
    
    def generate_test_cases(self, feature: str, output_file: Optional[str] = None) -> str:
        """
        根据功能描述生成测试用例建议
        
        Args:
            feature: 功能描述
            output_file: 输出文件路径
        
        Returns:
            测试用例建议文本
        """
        test_cases = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        测试用例生成建议                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 功能描述：{feature}

📋 建议测试用例列表：

1️⃣ 正常路径测试（Happy Path）
   ━━━━━━━━━━━━━━━━━━━━━━━━━
   □ 标准输入下的正常行为
   □ 预期输出验证
   □ 状态变化验证

2️⃣ 边界值测试（Boundary Values）
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   □ 最小值/最大值输入
   □ 空值/零值处理
   □ 极限数据量测试

3️⃣ 异常情况测试（Error Cases）
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━
   □ 无效输入类型
   □ 非法参数范围
   □ 资源不足情况

4️⃣ 特殊情况测试（Edge Cases）
   ━━━━━━━━━━━━━━━━━━━━━━━━━
   □ 并发访问处理
   □ 空集合/空字符串
   □ 特殊字符处理

💻 测试结构模板（{self.language} / {self.test_framework}）：

"""
        # 添加代码模板
        template = self._get_test_template("MyClass", "my_method")
        test_cases += template
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(test_cases)
            test_cases += f"\n✅ 测试建议已保存至: {output_file}\n"
        
        return test_cases
    
    def _get_test_template(self, class_name: str, method_name: str) -> str:
        """获取测试模板"""
        lang_templates = TEST_TEMPLATES.get(self.language, {})
        template = lang_templates.get(self.test_framework, "")
        
        if not template:
            return f"# 暂不支持 {self.language}/{self.test_framework} 的模板"
        
        # 渲染模板
        tpl = Template(template)
        return tpl.safe_substitute(
            class_name=class_name,
            method_name=method_name,
            method_name_pascal=method_name.replace('_', ' ').title().replace(' ', ''),
            module_name=class_name.lower(),
            module_path=f"./{class_name.lower()}",
            package_name="com.example"
        )
    
    def generate_test_template(self, class_name: str, method_name: str, 
                                output_dir: str = "./tests") -> str:
        """
        生成测试文件模板
        
        Args:
            class_name: 类名
            method_name: 方法名
            output_dir: 输出目录
        
        Returns:
            生成的文件路径
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取文件扩展名
        framework_info = TEST_FRAMEWORKS.get(self.language, {}).get(self.test_framework, {})
        extension = framework_info.get("extension", "py")
        
        # 生成文件名
        test_filename = f"test_{class_name.lower()}.{extension}"
        output_path = os.path.join(output_dir, test_filename)
        
        # 生成测试代码
        test_code = self._get_test_template(class_name, method_name)
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(test_code)
        
        return output_path
    
    def analyze_coverage(self, source_path: str, test_path: str,
                         threshold: float = 80.0) -> Dict:
        """
        分析代码覆盖率
        
        Args:
            source_path: 源代码路径
            test_path: 测试文件路径
            threshold: 覆盖率阈值
        
        Returns:
            覆盖率分析结果
        """
        result = {
            "source_path": source_path,
            "test_path": test_path,
            "threshold": threshold,
            "coverage_percent": 0.0,
            "pass": False,
            "details": []
        }
        
        # 获取运行命令
        framework_info = TEST_FRAMEWORKS.get(self.language, {}).get(self.test_framework, {})
        run_cmd = framework_info.get("run", "")
        
        if not run_cmd:
            result["details"].append(f"不支持的组合: {self.language}/{self.test_framework}")
            return result
        
        # 替换路径变量
        run_cmd = run_cmd.format(test_path=test_path, source_path=source_path)
        
        result["command"] = run_cmd
        result["details"].append(f"执行命令: {run_cmd}")
        result["details"].append(f"覆盖率阈值: {threshold}%")
        result["details"].append("建议：")
        result["details"].append("  • 确保测试覆盖所有分支")
        result["details"].append("  • 关注复杂逻辑的边界条件")
        result["details"].append("  • 使用覆盖率报告识别未测试代码")
        
        return result
    
    def red_green_refactor_guide(self) -> str:
        """红绿重构循环指导"""
        return """
╔══════════════════════════════════════════════════════════════════════════════╗
║                     红-绿-重构 (Red-Green-Refactor) 循环                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

🔴 阶段一：Red（编写失败的测试）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
目的：定义功能需求，建立测试基准

行动清单：
  ✓ 分析需求，明确功能边界
  ✓ 思考接口设计（从使用者角度）
  ✓ 编写第一个最简单的测试
  ✓ 运行测试，确认失败（红色）
  ✓ 失败的错误信息应该清晰可读

注意事项：
  ⚠ 不要跳过看测试失败的过程
  ⚠ 失败信息应该是有意义的
  ⚠ 测试应该针对具体的行为

🟢 阶段二：Green（编写代码通过测试）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
目的：让测试通过，建立功能基线

行动清单：
  ✓ 编写最简单的实现代码
  ✓ 可以作弊（硬编码返回预期值）
  ✓ 目标是绿色，不求完美
  ✓ 运行测试，确认通过（绿色）

原则：
  • 最快路径原则：选择最快让测试通过的方法
  • 稍后优化：现在不需要好代码，只需要能工作的代码
  • 保持测试通过：一旦变绿，保持绿色

🔵 阶段三：Refactor（重构代码）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
目的：在测试保护下优化代码质量

行动清单：
  ✓ 消除重复代码（DRY原则）
  ✓ 优化命名（有意义的命名）
  ✓ 简化复杂逻辑
  ✓ 提取方法/类
  ✓ 持续运行测试确保通过

重构时机：
  • 代码有重复时
  • 方法过长时（>20行）
  • 类职责不单一
  • 命名不清晰
  • 条件逻辑复杂

⚡ 循环节奏：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  理想节奏：2-3分钟完成一个循环
  测试粒度：小而专注的测试
  提交频率：每个绿点都可以提交

📊 质量检查点：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  □ 测试是否独立，不相互依赖？
  □ 测试是否快速执行？
  □ 测试是否清晰可读？
  □ 测试是否只验证一个概念？
  □ 生产代码是否有对应的测试？
"""


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="测试驱动开发(TDD)方法论指导工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --action workflow --language python --feature "用户登录功能"
  python main.py --action generate --language python --test_framework pytest --feature "购物车计算"
  python main.py --action template --language javascript --test_framework jest --output_dir ./tests
  python main.py --action coverage --file_path src/calc.py --test_file_path tests/test_calc.py
  python main.py --action red-green-refactor
        """
    )
    
    parser.add_argument('--action', '-a', required=True,
                       choices=['workflow', 'generate', 'template', 'coverage', 'red-green-refactor'],
                       help='操作类型')
    parser.add_argument('--language', '-l', default='python',
                       choices=['python', 'javascript', 'typescript', 'java', 'go', 'rust', 'cpp'],
                       help='编程语言')
    parser.add_argument('--test_framework', '-f', default='pytest',
                       choices=['pytest', 'unittest', 'jest', 'mocha', 'junit', 'testng', 'gtest', 'catch2'],
                       help='测试框架')
    parser.add_argument('--feature', '-e', default='',
                       help='功能描述')
    parser.add_argument('--file_path', '-s', default='',
                       help='源代码文件路径')
    parser.add_argument('--test_file_path', '-t', default='',
                       help='测试文件路径')
    parser.add_argument('--output_dir', '-o', default='./tests',
                       help='输出目录')
    parser.add_argument('--coverage_threshold', '-c', type=float, default=80.0,
                       help='覆盖率阈值')
    parser.add_argument('--class_name', default='MyClass',
                       help='类名（用于模板生成）')
    parser.add_argument('--method_name', default='my_method',
                       help='方法名（用于模板生成）')
    
    args = parser.parse_args()
    
    # 创建TDD管理器
    tdd = TDDManager(language=args.language, test_framework=args.test_framework)
    
    # 执行对应操作
    if args.action == 'workflow':
        print(tdd.show_workflow_guide(args.feature))
    
    elif args.action == 'generate':
        output_file = None
        if args.output_dir:
            os.makedirs(args.output_dir, exist_ok=True)
            output_file = os.path.join(args.output_dir, 'test_cases_guide.md')
        print(tdd.generate_test_cases(args.feature, output_file))
    
    elif args.action == 'template':
        output_path = tdd.generate_test_template(
            args.class_name, 
            args.method_name, 
            args.output_dir
        )
        print(f"✅ 测试模板已生成: {output_path}")
        print(f"\n生成的测试文件包含：")
        print(f"  • 正常情况测试")
        print(f"  • 边界情况测试")
        print(f"  • 异常情况测试")
        print(f"\n框架: {args.language} / {args.test_framework}")
    
    elif args.action == 'coverage':
        if not args.file_path:
            print("❌ 错误: 请提供源代码文件路径 (--file_path)")
            sys.exit(1)
        
        result = tdd.analyze_coverage(
            args.file_path,
            args.test_file_path or f"test_{os.path.basename(args.file_path)}",
            args.coverage_threshold
        )
        
        print("\n╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                          代码覆盖率分析报告                                    ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝\n")
        
        for detail in result["details"]:
            print(f"  {detail}")
        
        print(f"\n  执行命令示例:")
        print(f"  $ {result['command']}")
    
    elif args.action == 'red-green-refactor':
        print(tdd.red_green_refactor_guide())


if __name__ == '__main__':
    main()
