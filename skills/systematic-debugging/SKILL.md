# Systematic Debugging - 系统化调试

## 概述

系统化调试是一个结构化的bug定位和修复方法论框架，帮助开发者采用科学、系统的方式来诊断和解决软件问题。

## 功能特性

- **错误分析**：智能解析错误信息和堆栈跟踪
- **调试策略**：推荐最适合当前问题的调试方法
- **根因分析**：运用科学方法定位问题根源
- **修复建议**：基于最佳实践生成修复方案
- **多语言支持**：支持 Python、JavaScript、Java、C/C++、Go、Rust 等主流语言

## 使用方法

### 基础用法

```bash
python main.py --action full_diagnosis --language python --error "ZeroDivisionError: division by zero"
```

### 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--action` | string | 是 | 操作类型：analyze/strategy/root_cause/suggest_fix/full_diagnosis |
| `--language` | string | 是 | 编程语言 |
| `--error` | string | 否 | 错误信息 |
| `--context` | string | 否 | 代码上下文 |
| `--stack_trace` | string | 否 | 堆栈跟踪 |
| `--output_format` | string | 否 | 输出格式：text/json/markdown |

### 操作类型详解

#### 1. analyze - 错误分析
分析错误类型、严重程度和可能原因

```bash
python main.py --action analyze --language python --error "KeyError: 'user_id'"
```

#### 2. strategy - 调试策略
推荐最适合的调试方法和步骤

```bash
python main.py --action strategy --language javascript --error "TypeError: Cannot read property" --strategy binary_search
```

#### 3. root_cause - 根因分析
运用5 Whys、鱼骨图等方法深入分析

```bash
python main.py --action root_cause --language java --error "NullPointerException" --context "user.getProfile().getName()"
```

#### 4. suggest_fix - 修复建议
生成具体的代码修复方案

```bash
python main.py --action suggest_fix --language python --error "IndexError: list index out of range"
```

#### 5. full_diagnosis - 完整诊断
执行完整的调试流程（分析→策略→根因→修复）

```bash
python main.py --action full_diagnosis --language go --error "panic: runtime error" --stack_trace "..."
```

## 调试策略说明

| 策略 | 适用场景 |
|------|----------|
| binary_search | 大型代码库，问题位置不确定 |
| forward | 从输入开始逐步追踪 |
| backward | 从错误位置反向追踪 |
| deductive | 基于假设进行演绎推理 |
| inductive | 从观察归纳出规律 |
| divide_conquer | 复杂系统，可模块化处理 |

## 示例

### Python 错误分析示例

```bash
python main.py \
  --action full_diagnosis \
  --language python \
  --error "AttributeError: 'NoneType' object has no attribute 'split'" \
  --context "result = data['name'].split('_')" \
  --output_format markdown
```

### JavaScript 调试策略示例

```bash
python main.py \
  --action strategy \
  --language javascript \
  --error "Promise rejection: Network Error" \
  --strategy divide_conquer
```

## 输出说明

工具会输出结构化的调试报告，包括：

1. **错误分类**：错误类型、严重程度
2. **可能原因**：按概率排序的原因列表
3. **调试步骤**：具体的排查步骤
4. **修复方案**：代码级别的修复建议
5. **预防措施**：避免类似问题的最佳实践

## 集成到 Kimi

作为 Kimi Skill，可以直接在对话中使用：

```
@systematic-debugging
语言: python
错误: ValueError: invalid literal for int()
上下文: age = int(user_input)
```

## 注意事项

1. 提供的信息越完整，分析结果越准确
2. 代码上下文不需要完整文件，相关片段即可
3. 堆栈跟踪对定位问题非常有帮助
4. 复杂问题可能需要多次迭代分析

## 许可证

MIT License - 详见 LICENSE 文件
