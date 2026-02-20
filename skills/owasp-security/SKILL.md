# OWASP Security Skill

基于OWASP Top 10 2025的安全漏洞检测工具 Skill，用于 Kimi Code CLI。

## 用途

提供安全漏洞检测、代码审查、合规检查等功能，基于OWASP Top 10 2025标准。

## 功能

- **漏洞检测**: 基于规则的静态代码分析
- **OWASP覆盖**: 完整的Top 10 2025风险检测
- **风险评级**: CVSS评分和严重程度分级
- **修复建议**: 详细的修复方案和安全参考
- **报告生成**: 支持HTML/Markdown/JSON格式

## 使用方法

### 扫描文件

```python
from skills.owasp_security.main import OWASPSecuritySkill

skill = OWASPSecuritySkill()
result = skill.scan_file("./src/app.js")

for finding in result.findings:
    print(f"{finding.risk_level}: {finding.title}")
    print(f"  修复: {finding.remediation}")
```

### 扫描目录

```python
result = skill.scan_directory("./src")
report = skill.generate_report(result, "report.html", format="html")
```

### 作为Skill使用

```bash
kimi -c "使用owasp-security检查当前项目的安全漏洞"
```

## OWASP Top 10 2025 检测项

| 分类 | 检测规则 |
|------|----------|
| A01 - 失效的访问控制 | SEC-A01-001: IDOR |
| A02 - 加密失败 | SEC-A02-001: 弱加密算法, SEC-A02-002: 硬编码密钥 |
| A03 - 注入攻击 | SEC-A03-001: SQL注入, SEC-A03-002: 命令注入, SEC-A03-003: XSS |
| A05 - 安全配置错误 | SEC-A05-001: 调试模式 |
| A07 - 身份认证失效 | SEC-A07-001: 弱密码, SEC-A07-002: 不安全会话 |
| A09 - 日志监控不足 | SEC-A09-001: 敏感信息日志 |
| A10 - SSRF | SEC-A10-001: 服务器端请求伪造 |

## 风险等级

- **CRITICAL** (9.0-10.0): 必须立即修复
- **HIGH** (7.0-8.9): 优先修复
- **MEDIUM** (4.0-6.9): 计划修复
- **LOW** (0.1-3.9): 建议修复
- **INFO** (0): 仅供参考

## 配置选项

```python
config = {
    'auto_fix': False,              # 是否尝试自动修复
    'excluded_paths': [             # 排除路径
        'node_modules', '.git', 'dist'
    ]
}
```

## 依赖

- bandit >= 1.7.5
- semgrep >= 1.50.0
- safety >= 2.3.0
- cryptography >= 41.0.0

## 输出格式

### HTML报告
包含风险评分、分布图表、详细发现问题、代码片段和修复建议。

### Markdown报告
结构化文档，适合GitHub/GitLab集成。

### JSON输出
结构化数据，适合CI/CD集成和进一步处理。

## 安全考虑

⚠️ 警告：
1. 此工具仅用于您拥有权限的代码
2. 扫描结果可能包含误报，需要人工验证
3. 不保证发现所有安全漏洞
4. 定期更新规则和签名

## 维护者

Godlike Kimi Skills

## 参考资料

- [OWASP Top 10](https://owasp.org/Top10/)
- [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/)
- [CWE](https://cwe.mitre.org/)
