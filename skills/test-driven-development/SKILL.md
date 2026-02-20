# Test-Driven Development (TDD) Skill

## 简介

本Skill提供完整的**测试驱动开发 (Test-Driven Development)** 方法论指导，帮助开发者遵循TDD最佳实践进行软件开发。

TDD是一种软件开发方法论，核心思想是：**先写测试，后写代码**，通过短周期的"红-绿-重构"循环逐步构建高质量的软件。

---

## 核心功能

| 功能 | 描述 |
|------|------|
| 🎯 **TDD工作流指导** | 完整的方法论指导和最佳实践 |
| 📝 **测试用例生成** | 基于功能描述生成测试用例建议 |
| 📊 **代码覆盖率分析** | 分析测试覆盖率，提供改进建议 |
| 🧩 **测试模板生成** | 为多种语言和框架生成测试模板 |
| 🔄 **红绿重构指导** | 详细的循环指导，帮助掌握TDD节奏 |

---

## 支持的编程语言和测试框架

| 语言 | 支持的测试框架 |
|------|---------------|
| Python | pytest, unittest |
| JavaScript | Jest, Mocha |
| TypeScript | Jest |
| Java | JUnit, TestNG |
| Go | 内置测试框架 |
| Rust | 内置测试框架 |
| C++ | Google Test, Catch2 |

---

## 使用方法

### 1. TDD工作流指导

获取完整的TDD方法论指导：

```bash
python main.py --action workflow --language python --feature "实现用户登录功能"
```

**参数说明：**
- `--language`: 编程语言
- `--feature`: 功能描述

**输出内容包括：**
- TDD核心原则
- 红-绿-重构循环详解
- 测试用例设计原则（AAA模式）
- 常见反模式提醒

---

### 2. 生成测试用例建议

根据功能描述生成测试用例建议：

```bash
python main.py --action generate \
  --language python \
  --test_framework pytest \
  --feature "计算购物车总价，包括折扣和税费" \
  --output_dir ./tests
```

**输出内容包括：**
- 正常路径测试用例
- 边界值测试用例
- 异常情况测试用例
- 特殊情况测试用例
- 对应的代码模板

---

### 3. 生成测试模板

为指定类和方法生成测试文件模板：

```bash
python main.py --action template \
  --language python \
  --test_framework pytest \
  --class_name Calculator \
  --method_name add \
  --output_dir ./tests
```

**生成的测试文件包含：**

```python
import pytest
from calculator import Calculator


class TestCalculator:
    """Calculator 测试类"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.instance = Calculator()
    
    def test_add_normal_case(self):
        """测试正常情况"""
        # Arrange
        input_data = None
        expected = None
        
        # Act
        result = self.instance.add(input_data)
        
        # Assert
        assert result == expected
    
    def test_add_edge_case(self):
        """测试边界情况"""
        # Arrange
        input_data = None
        expected = None
        
        # Act
        result = self.instance.add(input_data)
        
        # Assert
        assert result == expected
    
    def test_add_invalid_input(self):
        """测试无效输入"""
        # Arrange
        input_data = None
        
        # Act & Assert
        with pytest.raises(ValueError):
            self.instance.add(input_data)
```

---

### 4. 代码覆盖率分析

获取代码覆盖率分析建议：

```bash
python main.py --action coverage \
  --file_path src/calculator.py \
  --test_file_path tests/test_calculator.py \
  --coverage_threshold 85
```

**输出内容包括：**
- 覆盖率阈值检查
- 运行测试的命令
- 覆盖率改进建议

---

### 5. 红绿重构循环指导

获取详细的红绿重构循环指导：

```bash
python main.py --action red-green-refactor
```

**输出内容包括：**
- 🔴 Red 阶段详细指导
- 🟢 Green 阶段详细指导  
- 🔵 Refactor 阶段详细指导
- 循环节奏建议
- 质量检查点

---

## TDD 最佳实践

### 红-绿-重构循环

```
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
```

### 测试用例设计原则（AAA模式）

| 阶段 | 英文 | 中文 | 说明 |
|------|------|------|------|
| Arrange | 准备 | 准备测试数据和前置条件 |
| Act | 执行 | 调用被测试的功能 |
| Assert | 断言 | 验证结果是否符合预期 |

### 测试命名规范

```
test_<方法名>_<场景描述>

例如：
- test_add_positive_numbers     # 测试正数相加
- test_add_negative_numbers     # 测试负数相加
- test_add_zero                 # 测试加零
- test_add_invalid_input        # 测试无效输入
```

### 避免的反模式

| ❌ 反模式 | ✅ 正确做法 |
|----------|------------|
| 测试代码中有逻辑判断 | 每个测试应该有确定的输入和输出 |
| 一个测试验证多个功能点 | 每个测试只验证一个概念 |
| 测试依赖外部资源 | 使用Mock/Stub隔离外部依赖 |
| 测试与实现耦合 | 测试应该验证行为，而非实现细节 |
| 忽略测试失败 | 永远不要让失败的测试累积 |

---

## 不同语言的TDD示例

### Python + pytest

```python
# test_calculator.py
import pytest
from calculator import Calculator

class TestCalculator:
    def test_add_two_positive_numbers(self):
        # Arrange
        calc = Calculator()
        
        # Act
        result = calc.add(2, 3)
        
        # Assert
        assert result == 5
    
    def test_add_negative_number(self):
        calc = Calculator()
        result = calc.add(-1, 1)
        assert result == 0
```

### JavaScript + Jest

```javascript
// calculator.test.js
const Calculator = require('./calculator');

describe('Calculator', () => {
    let calc;
    
    beforeEach(() => {
        calc = new Calculator();
    });
    
    test('adds two positive numbers', () => {
        // Arrange & Act
        const result = calc.add(2, 3);
        
        // Assert
        expect(result).toBe(5);
    });
});
```

### Java + JUnit 5

```java
// CalculatorTest.java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class CalculatorTest {
    
    @Test
    void testAddTwoPositiveNumbers() {
        // Arrange
        Calculator calc = new Calculator();
        
        // Act
        int result = calc.add(2, 3);
        
        // Assert
        assertEquals(5, result);
    }
}
```

---

## 参数参考

| 参数 | 简写 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|------|--------|------|
| --action | -a | string | 是 | - | 操作类型 |
| --language | -l | string | 否 | python | 编程语言 |
| --test_framework | -f | string | 否 | pytest | 测试框架 |
| --feature | -e | string | 否 | "" | 功能描述 |
| --file_path | -s | string | 否 | "" | 源代码文件路径 |
| --test_file_path | -t | string | 否 | "" | 测试文件路径 |
| --output_dir | -o | string | 否 | ./tests | 输出目录 |
| --coverage_threshold | -c | float | 否 | 80.0 | 覆盖率阈值 |
| --class_name | - | string | 否 | MyClass | 类名 |
| --method_name | - | string | 否 | my_method | 方法名 |

---

## 依赖安装

```bash
# 安装依赖
pip install -r requirements.txt
```

主要依赖：
- `pytest>=7.0.0` - Python测试框架
- `pytest-cov>=4.0.0` - 覆盖率插件
- `jinja2>=3.1.0` - 模板引擎
- `click>=8.0.0` - 命令行工具

---

## 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行测试并生成覆盖率报告
pytest tests/ --cov=. --cov-report=html
```

---

## 常见问题和解决方案

### Q: 如何开始第一个TDD项目？

**A:** 按照以下步骤：
1. 选择一个简单功能开始
2. 编写第一个失败的测试
3. 运行测试，确认失败（红色）
4. 编写最简单的代码让测试通过（绿色）
5. 重构代码，保持测试通过
6. 重复步骤2-5

### Q: 测试应该写多细？

**A:** 
- 测试应该验证行为，而非实现
- 每个测试只验证一个概念
- 保持测试简单、独立、快速

### Q: 如何处理外部依赖？

**A:**
- 使用 Mock 对象替代真实外部服务
- 使用依赖注入便于测试
- 将外部依赖抽象成接口

---

## 学习资源

### 推荐书籍
- 《测试驱动开发》- Kent Beck
- 《重构》- Martin Fowler
- 《敏捷软件开发》- Robert C. Martin

### 在线资源
- [pytest官方文档](https://docs.pytest.org/)
- [Jest官方文档](https://jestjs.io/)
- [JUnit 5用户指南](https://junit.org/junit5/docs/current/user-guide/)

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

提交前请确保：
1. 代码通过所有测试
2. 新增功能有对应的测试
3. 遵循现有代码风格

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
