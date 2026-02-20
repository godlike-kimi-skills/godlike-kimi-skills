# Skill Creator Enhanced - 增强版技能创建器

> 一键创建符合开源标准的 Kimi Skill 项目

---

## 功能概述

本 Skill 帮助开发者快速创建符合 **Anthropic Agent Skill 标准** 和 **Godlike Kimi Skills 规范** 的开源技能项目。

### 核心能力

1. **项目脚手架生成** - 自动生成完整的 Skill 目录结构
2. **标准化文件模板** - skill.json / SKILL.md / README.md / LICENSE
3. **测试模板生成** - pytest 单元测试框架
4. **CI/CD 配置** - GitHub Actions 自动化工作流
5. **项目验证** - 检查 Skill 是否符合开源标准

---

## 使用方法

### 基础用法：创建新 Skill

```bash
# 交互式创建
kimi skill run skill-creator-enhanced --params "action=create"

# 命令行参数创建
kimi skill run skill-creator-enhanced --params "action=create&skill_name=web-scraper&skill_title=网页数据提取器&description=从网页提取结构化数据&category=automation"
```

### 验证现有 Skill

```bash
kimi skill run skill-creator-enhanced --params "action=validate&skill_path=./my-skill"
```

### 查看可用模板

```bash
kimi skill run skill-creator-enhanced --params "action=list-templates"
```

---

## 生成项目结构

```
my-skill/
├── skill.json              # Skill 清单文件（标准格式）
├── SKILL.md                # 使用说明文档
├── README.md               # GitHub 项目主页
├── LICENSE                 # MIT 许可证
├── CHANGELOG.md            # 变更日志
├── CONTRIBUTING.md         # 贡献指南
├── SECURITY.md             # 安全说明
├── main.py                 # 主入口文件
├── requirements.txt        # Python 依赖
├── .gitignore             # Git 忽略配置
├── tests/
│   ├── __init__.py
│   ├── test_basic.py       # 基础测试
│   └── test_advanced.py    # 高级测试
├── examples/
│   ├── basic_usage.py      # 基础示例
│   └── advanced_usage.py   # 高级示例
└── .github/
    └── workflows/
        ├── ci.yml          # CI/CD 工作流
        └── release.yml     # 发布工作流
```

---

## 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|-------|------|------|-------|------|
| `action` | string | 是 | create | 操作类型: create/validate/list-templates/upgrade |
| `skill_name` | string | 条件 | - | Skill 名称（小写，连字符分隔） |
| `skill_title` | string | 条件 | - | Skill 中文标题 |
| `description` | string | 条件 | - | 一句话描述 |
| `category` | string | 条件 | - | 分类: development/data/automation/security/media/other |
| `output_dir` | string | 否 | ./ | 输出目录 |
| `with_tests` | boolean | 否 | true | 生成测试模板 |
| `with_ci` | boolean | 否 | true | 生成 CI/CD 配置 |
| `with_examples` | boolean | 否 | true | 生成示例代码 |

---

## 最佳实践

### 命名规范

- **skill_name**: 小写，连字符分隔，如 `web-scraper`, `pdf-converter`
- **skill_title**: 中文，简洁明了，如 "网页数据提取器", "PDF转换工具"
- **description**: 一句话说明核心功能，不超过100字

### 分类建议

| 分类 | 适用场景 | 示例 |
|------|---------|------|
| development | 开发工具 | code-formatter, git-helper |
| data | 数据处理 | csv-processor, json-validator |
| automation | 自动化 | web-scraper, file-organizer |
| security | 安全工具 | password-generator, security-check |
| media | 媒体处理 | image-resizer, video-converter |
| other | 其他工具 | calculator, random-generator |

---

## 示例

### 示例1：创建数据处理 Skill

```bash
kimi skill run skill-creator-enhanced \
  --params "action=create&skill_name=csv-processor&skill_title=CSV处理器&description=读取、清洗、转换CSV文件，支持大数据集&category=data"
```

生成项目包含：
- 基于 pandas 的 CSV 处理代码模板
- 数据验证和清洗示例
- 大数据集分块处理示例

### 示例2：创建安全工具 Skill

```bash
kimi skill run skill-creator-enhanced \
  --params "action=create&skill_name=password-generator&skill_title=强密码生成器&description=生成高强度随机密码，支持多种复杂度选项&category=security"
```

生成项目包含：
- 密码强度检测算法
- 多种密码生成策略
- 安全最佳实践说明

---

## 验证规则

本工具会检查以下开源标准：

### 必需文件
- [x] skill.json - 格式正确，必填字段完整
- [x] SKILL.md - 使用说明文档
- [x] README.md - 项目介绍
- [x] LICENSE - MIT 许可证

### 代码质量
- [x] 无硬编码敏感信息
- [x] 完善的错误处理
- [x] 清晰的函数注释
- [x] 最小化依赖

### 测试覆盖
- [x] 至少3个测试用例
- [x] 边界条件测试
- [x] 错误处理测试

---

## 升级现有 Skill

如果你已有 Skill 需要升级到最新标准：

```bash
kimi skill run skill-creator-enhanced \
  --params "action=upgrade&skill_path=./my-old-skill"
```

升级内容包括：
1. 更新 skill.json 到最新 schema
2. 添加缺失的标准化文件
3. 优化 README 结构
4. 添加 CI/CD 配置

---

## 技术细节

### 依赖要求
- Python 3.10+
- 无第三方依赖（标准库实现）

### 支持的模板
1. **basic** - 基础 Skill 模板
2. **cli-tool** - 命令行工具模板
3. **api-service** - API 服务模板
4. **data-processor** - 数据处理模板
5. **automation** - 自动化任务模板

---

## 贡献指南

欢迎提交 Issue 和 PR！

### 开发流程
1. Fork 本仓库
2. 创建功能分支
3. 提交更改
4. 确保测试通过
5. 提交 PR

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 更新日志

### v1.0.0 (2026-02-20)
- 初始版本发布
- 支持项目脚手架生成
- 支持标准化文件模板
- 支持 CI/CD 配置生成

---

**Made with ❤️ by Godlike Kimi Skills**
