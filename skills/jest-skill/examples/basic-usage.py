#!/usr/bin/env python3
"""
Jest Skill 基础使用示例
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import JestSkill, TestConfig, MockConfig


def example_generate_basic_test():
    """示例1: 生成基础单元测试"""
    print("=" * 60)
    print("示例1: 生成基础单元测试")
    print("=" * 60)
    
    skill = JestSkill()
    
    source_code = """
function calculateTotal(price, quantity, discount = 0) {
    const subtotal = price * quantity;
    const discountAmount = subtotal * discount;
    return subtotal - discountAmount;
}
"""
    
    test_code = skill.generate_test(
        source_code=source_code,
        test_type="unit"
    )
    
    print(test_code)
    print()


def example_generate_async_test():
    """示例2: 生成异步函数测试"""
    print("=" * 60)
    print("示例2: 生成异步函数测试")
    print("=" * 60)
    
    skill = JestSkill()
    
    source_code = """
async function fetchUserData(userId) {
    const response = await fetch(`/api/users/${userId}`);
    if (!response.ok) {
        throw new Error('Failed to fetch user');
    }
    return response.json();
}
"""
    
    test_code = skill.generate_test(
        source_code=source_code,
        test_type="unit"
    )
    
    print(test_code)
    print()


def example_generate_mock():
    """示例3: 生成Mock代码"""
    print("=" * 60)
    print("示例3: 生成Mock代码")
    print("=" * 60)
    
    skill = JestSkill()
    
    # 基础mock
    mock_code = skill.generate_mock(
        module_name="axios",
        methods=["get", "post", "put", "delete"]
    )
    print("基础Mock:")
    print(mock_code)
    print()
    
    # 带返回值的mock
    config = MockConfig(
        module_name="api",
        methods=["fetchUsers", "createUser"],
        return_values={
            "fetchUsers": "[{ id: 1, name: 'John' }]",
            "createUser": "{ id: 2, name: 'Jane' }"
        }
    )
    
    mock_code_with_values = skill.generate_mock(
        module_name="api",
        methods=["fetchUsers", "createUser"],
        config=config
    )
    print("带返回值的Mock:")
    print(mock_code_with_values)
    print()


def example_generate_snapshot_test():
    """示例4: 生成Snapshot测试"""
    print("=" * 60)
    print("示例4: 生成Snapshot测试")
    print("=" * 60)
    
    skill = JestSkill()
    
    source_code = """
function formatUserProfile(user) {
    return {
        fullName: `${user.firstName} ${user.lastName}`,
        email: user.email,
        role: user.role || 'user',
        createdAt: new Date(user.createdAt).toISOString()
    };
}
"""
    
    test_code = skill.generate_test(
        source_code=source_code,
        test_type="snapshot"
    )
    
    print(test_code)
    print()


def example_setup_environment():
    """示例5: 设置测试环境"""
    print("=" * 60)
    print("示例5: 设置测试环境")
    print("=" * 60)
    
    config = TestConfig(
        test_environment="jsdom",
        coverage_threshold=85.0,
        test_match=["**/*.test.js", "**/*.spec.js"]
    )
    
    skill = JestSkill(config)
    files = skill.setup_test_environment("./my-project")
    
    for filename, content in files.items():
        print(f"\n--- {filename} ---")
        print(content[:500] + "..." if len(content) > 500 else content)
    print()


def example_create_test_suite():
    """示例6: 创建完整测试套件"""
    print("=" * 60)
    print("示例6: 创建完整测试套件")
    print("=" * 60)
    
    skill = JestSkill()
    
    functions = [
        {"name": "validateEmail", "params": ["email"]},
        {"name": "formatPhone", "params": ["phone"]},
        {"name": "parseDate", "params": ["dateString"]}
    ]
    
    suite = skill.create_test_suite(
        module_name="utils",
        functions=functions,
        options={"include_mocks": True, "include_setup": True}
    )
    
    print(suite)
    print()


def example_optimize_tests():
    """示例7: 优化测试代码"""
    print("=" * 60)
    print("示例7: 优化测试代码")
    print("=" * 60)
    
    skill = JestSkill()
    
    poorly_written_test = '''
describe('UserService', () => {
  beforeEach(() => { setup1(); });
  beforeEach(() => { setup2(); });
  
  test('test1', () => {
    // Arrange
    // Act
    // Assert - missing!
  });
  
  test('test2', () => {
    // Arrange
    const result = doSomething();
    // Missing assertion
  });
  
  test('very long test', () => {
    // Many lines of code...
    // Line 1
    // Line 2
    // ... more lines
  });
});
'''
    
    optimized = skill.optimize_tests(poorly_written_test)
    print(optimized)
    print()


if __name__ == '__main__':
    example_generate_basic_test()
    example_generate_async_test()
    example_generate_mock()
    example_generate_snapshot_test()
    example_setup_environment()
    example_create_test_suite()
    example_optimize_tests()
    
    print("\n所有示例执行完成!")
