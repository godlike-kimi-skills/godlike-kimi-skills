# React Best Practices ⚛️✨

React 开发最佳实践指南，提供全面的代码审查、设计模式建议和性能优化检查。

## ✨ 功能特性

- **🔍 代码审查** - 自动检测代码中的问题和不良实践
- **📐 模式建议** - 推荐最佳设计模式和架构方案
- **⚡ 性能优化** - 识别性能瓶颈并提供优化建议
- **🔒 安全检查** - 检测常见的安全漏洞
- **♿ 可访问性** - 审计 A11y 合规性
- **📘 TypeScript** - 类型检查和最佳实践建议

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 命令行使用

```bash
# 分析单个文件
python main.py ./src/App.tsx

# 分析整个项目
python main.py ./src
```

### 编程使用

```python
from main import ReactBestPracticesSkill

# 创建实例
skill = ReactBestPracticesSkill(config={
    'react_version': '18.0',
    'typescript_preferred': True
})

# 分析单个文件
result = skill.analyze_file("./src/App.tsx")
print(f"代码质量分数: {result.score}/100")

# 查看问题
for issue in result.issues:
    print(f"[{issue.severity.value}] {issue.message}")
    print(f"  建议: {issue.suggestion}")

# 分析整个目录
results = skill.analyze_directory("./src")

# 生成报告
report = skill.generate_report(results, "react-analysis-report.md")
```

## 📋 检查规则

### 性能优化 (PERF)

| 规则ID | 说明 | 严重程度 |
|--------|------|----------|
| PERF-001 | 内联函数定义导致重渲染 | Medium |
| PERF-002 | 列表渲染缺少key属性 | High |
| PERF-003 | 组件使用过多Hooks | Low |

### 安全检查 (SEC)

| 规则ID | 说明 | 严重程度 |
|--------|------|----------|
| SEC-001 | 使用dangerouslySetInnerHTML | Critical |
| SEC-002 | 使用eval() | Critical |

### 可访问性 (A11Y)

| 规则ID | 说明 | 严重程度 |
|--------|------|----------|
| A11Y-001 | 图片缺少alt属性 | Medium |
| A11Y-002 | button缺少type属性 | Low |

### React 模式 (REACT)

| 规则ID | 说明 | 严重程度 |
|--------|------|----------|
| REACT-001 | 建议使用函数组件 | Info |
| REACT-002 | useEffect缺少清理函数 | High |

### TypeScript (TS)

| 规则ID | 说明 | 严重程度 |
|--------|------|----------|
| TS-001 | 使用any类型 | Medium |

### 可维护性 (MAINT)

| 规则ID | 说明 | 严重程度 |
|--------|------|----------|
| MAINT-001 | 存在console语句 | Low |
| MAINT-002 | 文件过长 | Medium |

## 📊 输出示例

```json
{
  "file_path": "./src/App.tsx",
  "score": 85.5,
  "issues": [
    {
      "severity": "high",
      "category": "performance",
      "message": "列表渲染缺少key属性",
      "line": 45,
      "rule_id": "PERF-002",
      "suggestion": "为列表项添加唯一的key属性"
    }
  ],
  "statistics": {
    "total_lines": 120,
    "issue_count": 3,
    "severity_counts": {
      "critical": 0,
      "high": 1,
      "medium": 1,
      "low": 1,
      "info": 0
    }
  }
}
```

## 🧪 运行测试

```bash
cd tests
python -m pytest test_basic.py -v
```

## 📁 项目结构

```
react-best-practices/
├── skill.json          # Skill 元数据配置
├── SKILL.md            # Kimi CLI 内部使用文档
├── README.md           # 项目说明文档
├── main.py             # 主程序代码 (~400行)
├── requirements.txt    # Python 依赖
├── LICENSE             # MIT 许可证
└── tests/
    └── test_basic.py   # 基础测试用例
```

## 🤝 贡献指南

欢迎提交 Pull Request 或 Issue！

1. Fork 本仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 打开 Pull Request

## 📝 许可证

本项目基于 [MIT](LICENSE) 许可证开源。

## 📚 参考资料

- [React 官方文档](https://react.dev/)
- [React TypeScript 速查表](https://react-typescript-cheatsheet.netlify.app/)
- [Web Accessibility Guidelines](https://www.w3.org/WAI/standards-guidelines/wcag/)

---

由 [Godlike Kimi Skills](https://github.com/godlike-kimi-skills) 精心打造 ❤️
