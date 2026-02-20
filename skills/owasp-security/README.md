# OWASP Security 🔒🛡️

基于 OWASP Top 10 2025 标准的安全漏洞检测工具，提供全面的代码安全审查和合规检查。

## ✨ 功能特性

- **🎯 OWASP Top 10 覆盖** - 全面检测2025年十大安全风险
- **🔍 静态代码分析** - 深度扫描安全漏洞
- **📦 依赖安全检查** - 扫描第三方组件漏洞
- **⚠️ 风险评级** - CVSS评分和风险等级
- **💡 修复建议** - 详细的修复方案
- **📊 可视化报告** - HTML/Markdown/JSON多种格式

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 命令行使用

```bash
# 扫描单个文件
python main.py ./src/app.js

# 扫描整个项目
python main.py ./src

# 指定输出文件
python main.py ./src security-report.html
```

### 编程使用

```python
from main import OWASPSecuritySkill, RiskLevel

# 创建实例
skill = OWASPSecuritySkill(config={
    'auto_fix': False
})

# 扫描单个文件
result = skill.scan_file("./src/app.js")
print(f"发现问题: {result.summary['total_findings']}")
print(f"风险评级: {result.summary['risk_rating']}")

# 扫描整个目录
result = skill.scan_directory("./src")

# 生成HTML报告
report = skill.generate_report(result, "security-report.html", format="html")

# 生成Markdown报告
report = skill.generate_report(result, "security-report.md", format="md")

# 生成JSON报告
report = skill.generate_report(result, "security-report.json", format="json")
```

## 🛡️ OWASP Top 10 覆盖

| ID | 分类 | 检测项 |
|----|------|--------|
| A01 | 失效的访问控制 | IDOR、权限绕过 |
| A02 | 加密失败 | 弱算法、硬编码密钥 |
| A03 | 注入攻击 | SQL注入、XSS、命令注入 |
| A04 | 不安全设计 | 安全设计缺陷 |
| A05 | 安全配置错误 | 调试模式、错误配置 |
| A06 | 易受攻击组件 | 过期依赖、已知漏洞 |
| A07 | 身份认证失效 | 弱密码、会话管理 |
| A08 | 软件和数据完整性 | 反序列化、依赖完整性 |
| A09 | 日志监控不足 | 敏感信息日志 |
| A10 | SSRF | 服务器端请求伪造 |

## 📋 安全规则

### 严重 (Critical)

| 规则ID | 检测项 | CWE |
|--------|--------|-----|
| SEC-A02-002 | 硬编码密钥 | CWE-798 |
| SEC-A03-001 | SQL注入 | CWE-89 |
| SEC-A03-002 | 命令注入 | CWE-78 |

### 高危 (High)

| 规则ID | 检测项 | CWE |
|--------|--------|-----|
| SEC-A01-001 | IDOR | CWE-639 |
| SEC-A02-001 | 弱加密算法 | CWE-327 |
| SEC-A03-003 | XSS漏洞 | CWE-79 |
| SEC-A07-002 | 不安全会话 | CWE-1004 |
| SEC-A10-001 | SSRF | CWE-918 |

### 中危 (Medium)

| 规则ID | 检测项 | CWE |
|--------|--------|-----|
| SEC-A05-001 | 调试模式 | CWE-489 |
| SEC-A07-001 | 弱密码策略 | CWE-521 |
| SEC-A09-001 | 敏感信息日志 | CWE-532 |

## 📊 报告示例

### HTML报告

生成的HTML报告包含：
- 风险评分和评级
- 严重程度分布图表
- 详细发现问题列表
- 代码片段和修复建议

### JSON输出

```json
{
  "target_path": "./src",
  "scan_time": "2025-01-15T10:30:00",
  "findings": [
    {
      "rule_id": "SEC-A03-001",
      "title": "SQL注入风险",
      "risk_level": "critical",
      "owasp_category": "A03:2021-Injection",
      "file_path": "/path/to/file.js",
      "line_number": 45,
      "code_snippet": "db.query(`SELECT * FROM users WHERE id = ${userId}`)",
      "remediation": "使用参数化查询或ORM框架",
      "cwe_id": "CWE-89",
      "cvss_score": 9.8
    }
  ],
  "summary": {
    "total_findings": 5,
    "risk_score": 45.5,
    "risk_rating": "HIGH",
    "severity_distribution": {
      "critical": 1,
      "high": 2,
      "medium": 1,
      "low": 1,
      "info": 0
    }
  }
}
```

## 🔧 配置选项

```python
config = {
    'auto_fix': False,              # 自动修复（谨慎使用）
    'excluded_paths': [             # 排除路径
        'node_modules',
        '.git',
        'dist',
        'build'
    ]
}
```

## 🧪 运行测试

```bash
cd tests
python -m pytest test_basic.py -v
```

## 📁 项目结构

```
owasp-security/
├── skill.json          # Skill 元数据配置
├── SKILL.md            # Kimi CLI 内部使用文档
├── README.md           # 项目说明文档
├── main.py             # 主程序代码 (~500行)
├── requirements.txt    # Python 依赖
├── LICENSE             # MIT 许可证
└── tests/
    └── test_basic.py   # 基础测试用例
```

## 🤝 贡献指南

欢迎提交安全规则和检测器的改进！

1. Fork 本仓库
2. 创建特性分支
3. 添加或改进检测规则
4. 提交更改
5. 打开 Pull Request

## 📝 许可证

本项目基于 [MIT](LICENSE) 许可证开源。

## 📚 参考资料

- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [CVSS v3.1](https://www.first.org/cvss/)

## ⚠️ 免责声明

此工具仅用于教育和防御目的。请确保您有权扫描目标代码。作者不对任何滥用行为负责。

---

由 [Godlike Kimi Skills](https://github.com/godlike-kimi-skills) 精心打造 ❤️
