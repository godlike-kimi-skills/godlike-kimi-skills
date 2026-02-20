# Superpowers for Kimi Code CLI

Superpowers 工作流插件已适配到 Kimi Code CLI。

## 安装的技能

| 技能 | 命令 | 用途 |
|------|------|------|
| brainstorming | `/superpowers-brainstorming` | 需求分析、方案探索 |
| tdd | `/superpowers-tdd` | 强制 TDD 开发 |
| debugging | `/superpowers-debugging` | 系统化调试 |
| writing-plans | `/superpowers-plan` | 编写实施计划 |
| code-review | `/superpowers-review` | 代码审查 |

## 核心工作流

```
1. brainstorming → 2. writing-plans → 3. tdd + code-review → 4. (循环)
```

## 使用示例

### 开始新功能

```
用户: 帮我做一个用户登录功能

Kbot: [自动触发 /superpowers-brainstorming]
1. 探索项目上下文
2. 询问澄清问题
3. 提出 2-3 种方案
4. 等待你确认设计
...

设计确认后 → [自动触发 /superpowers-plan]
生成详细实施计划
...

开始编码 → [自动触发 /superpowers-tdd]
强制 RED-GREEN-REFACTOR
...
```

### 调试 Bug

```
用户: 这里报错了

Kbot: [自动触发 /superpowers-debugging]
1. 根因调查
2. 模式分析
3. 假设验证
4. 实施修复
...
```

## 快速参考

### TDD 强制规则
- ❌ 先写代码后写测试 → 必须删除重写
- ✅ 测试失败 → 写最小实现 → 测试通过 → 重构
- ⚠️ 违反规则会被强制纠正

### 调试铁律
- ❌ 没有根因调查就直接修复
- ✅ 4 阶段: 调查→分析→假设→实施
- ⚠️ 3 次修复失败必须质疑架构

## 配置

技能已自动启用。Kbot 会根据对话内容自动识别何时应用 Superpowers 流程。

## 来源

- 原始项目: https://github.com/obra/superpowers
- 适配版本: Kimi Code CLI 兼容版
