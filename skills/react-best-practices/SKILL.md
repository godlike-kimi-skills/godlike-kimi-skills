# React Best Practices Skill

React开发最佳实践指南 Skill，用于 Kimi Code CLI。

## 用途

提供React代码审查、设计模式建议、性能优化检查等功能，帮助开发者遵循React最佳实践。

## 功能

- **代码审查**: 自动检测代码问题和不良实践
- **性能检查**: 识别性能瓶颈
- **安全检查**: 检测XSS等安全漏洞
- **可访问性**: A11y合规性检查
- **TypeScript**: 类型检查建议
- **代码质量评分**: 综合质量评估

## 使用方法

### 分析文件

```python
from skills.react_best_practices.main import ReactBestPracticesSkill

skill = ReactBestPracticesSkill()
result = skill.analyze_file("./src/App.tsx")

for issue in result.issues:
    print(f"{issue.severity}: {issue.message}")
```

### 分析目录

```python
results = skill.analyze_directory("./src")
report = skill.generate_report(results, "report.md")
```

### 作为Skill使用

```bash
kimi -c "使用react-best-practices检查当前项目的React代码质量"
```

## 检查类别

1. **PERFORMANCE** - 性能优化
2. **SECURITY** - 安全漏洞
3. **ACCESSIBILITY** - 可访问性
4. **MAINTAINABILITY** - 可维护性
5. **BEST_PRACTICE** - 最佳实践
6. **TYPESCRIPT** - TypeScript规范
7. **REACT_PATTERNS** - React设计模式

## 严重程度

- **CRITICAL** - 严重，必须立即修复
- **HIGH** - 高危，优先修复
- **MEDIUM** - 中危，计划修复
- **LOW** - 低危，建议修复
- **INFO** - 信息，仅供参考

## 配置选项

```python
config = {
    'react_version': '18.0',
    'typescript_preferred': True,
    'strict_mode': True
}
```

## 依赖

- tree-sitter >= 0.20.0
- regex >= 2023.10.0
- pydantic >= 2.5.0

## 输出格式

分析结果包含：
- 代码质量分数 (0-100)
- 问题列表（含位置、建议）
- 统计信息（问题分类统计）
- 详细报告（Markdown/HTML）

## 维护者

Godlike Kimi Skills
