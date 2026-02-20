# Doc Gen Skill

**文档生成工具** - 基于 MkDocs 和 Docusaurus

项目文档、API文档、博客自动生成。

---

## 核心特性

### 📄 文档类型

| 类型 | 说明 |
|------|------|
| **API文档** | 从代码注释生成 |
| **项目文档** | README、使用指南 |
| **技术博客** | Markdown博客生成 |
| **PDF导出** | 文档转PDF |

### 🔄 生成流程

```
源代码 → 解析 → 模板 → 生成 → 部署
```

---

## 使用方法

### 生成API文档
```bash
doc-gen-skill api --source ./src --output ./docs
```

### 生成项目文档
```bash
doc-gen-skill project --template mkdocs
```

### 导出PDF
```bash
doc-gen-skill export --input ./docs --format pdf
```

---

## 参考实现

- **MkDocs**: 项目文档生成
- **Docusaurus**: 静态网站生成器
- **Sphinx**: Python文档工具

---

## 版本信息

- **Version**: 1.0.0
- **Author**: KbotGenesis

---

# 多维度分析报告与改进路线图

## 分析报告

本Skill已通过**第一性原理**、**系统思维**、**贝叶斯决策**、**博弈论**、**精益思想**五个维度进行深度分析。

详细分析报告见: `analysis-reports/doc-gen-skill-multi-lens-analysis.md`

---

## 核心发现

### 第一性原理分析
- **本质**: 文档的本质是**知识的时空传递媒介**
- **基本事实**: 知识不对称、认知负荷、时效衰减、多模态需求
- **关键差距**: 功能描述过于简略，缺乏详细使用指南
- **改进方向**: CI/CD集成、智能同步、多格式输出

### 系统思维分析
- **反馈回路**: 文档质量回路(健康) vs 文档腐烂回路(危险)
- **系统边界**: 需要与源代码、CI/CD、读者形成完整生态
- **改进方向**: 建立双向反馈循环、自动同步机制

### 贝叶斯决策分析
- **文档策略**: 可基于项目特征决策投入多少文档资源
- **质量评估**: 通过自动化检查更新质量概率
- **改进方向**: README和API文档优先级最高

### 博弈论分析
- **信号博弈**: 文档是作者向读者传递知识的信号
- **公共品博弈**: 多开发者团队中文档贡献是囚徒困境
- **改进方向**: 降低文档编写成本、建立贡献激励机制

### 精益思想分析
- **严重浪费**: 等待(手动触发)、库存(过时文档)、过度生产
- **价值流**: 当前手工流程，可通过自动化优化
- **改进方向**: CI/CD集成、增量生成、实时预览

---

## 改进路线图

### 立即实施 (1-2周)

1. **详细使用指南** [P0]
   - 完整的命令示例
   - 常见用例演示
   - 故障排除指南
   - 多语言支持说明(Python/JS/Go等)

2. **快速开始模板** [P0]
   ```bash
   # 初始化文档项目
   doc-gen-skill init --template mkdocs --project-name "My Project"
   
   # 生成API文档
   doc-gen-skill api --source ./src --language python --output ./docs/api
   
   # 本地预览
   doc-gen-skill serve --port 8000
   ```

3. **配置说明** [P1]
   - mkdocs.yml配置详解
   - docusaurus.config.js配置
   - 自定义主题指南

### 短期改进 (1-2个月)

4. **CI/CD集成** [P0]
   - GitHub Actions工作流模板
   - 自动部署到GitHub Pages
   - 代码提交触发文档更新
   ```yaml
   # .github/workflows/docs.yml
   name: Deploy Docs
   on:
     push:
       branches: [main]
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Generate Docs
           run: doc-gen-skill api --source ./src --output ./docs
         - name: Deploy
           run: doc-gen-skill deploy --target github-pages
   ```

5. **多语言支持** [P1]
   - Python (Sphinx/pdoc)
   - JavaScript/TypeScript (TypeDoc/JSDoc)
   - Go (godoc)
   - Rust (rustdoc)

6. **模板库** [P1]
   - 多种项目类型模板
   - API项目模板
   - 工具库模板
   - 应用项目模板

7. **质量检查** [P1]
   - 坏链接检测
   - 代码示例验证
   - 可读性评分
   - 过时文档检测

### 中期愿景 (3-6个月)

8. **智能同步** [P1]
   - 代码变更自动识别相关文档
   - 智能更新建议
   - 增量生成（仅更新变更部分）

9. **读者分析** [P2]
   - 访问统计
   - 热点内容识别
   - 改进建议生成

10. **多格式输出** [P2]
    - Confluence集成
    - Notion导出
    - Word/PDF模板
    - 电子书生成

11. **交互式文档** [P2]
    - 可执行代码示例
    - 交互式图表
    - 评论和反馈

---

## 更新后的架构愿景 (v2.0)

```
Doc Gen Skill v2.0
├── 输入层
│   ├── 源码解析
│   │   ├── Python (Sphinx/pdoc兼容)
│   │   ├── JavaScript/TypeScript (TypeDoc/JSDoc)
│   │   ├── Go (godoc)
│   │   └── Rust (rustdoc)
│   ├── Markdown处理
│   └── 配置文件读取
├── 处理层
│   ├── 文档生成
│   │   ├── API文档
│   │   ├── 用户指南
│   │   └── 开发者文档
│   ├── 模板引擎
│   │   ├── MkDocs模板
│   │   ├── Docusaurus模板
│   │   └── 自定义模板
│   ├── 质量检查
│   │   ├── 链接检查
│   │   ├── 代码验证
│   │   └── 可读性分析
│   └── 同步管理
│       ├── 变更检测
│       └── 增量更新
├── 输出层
│   ├── 静态站点 (HTML)
│   ├── PDF文档
│   ├── Wiki集成
│   └── IDE插件
└── 集成层
    ├── GitHub Actions
    ├── GitLab CI
    ├── Pre-commit hooks
    └── 本地开发服务器
```

---

## 使用示例

### Python项目完整流程

```bash
# 1. 初始化文档项目
doc-gen-skill init --template mkdocs --name "My Python Project"

# 2. 配置文档源
cat > doc-gen.config.yml << EOF
source:
  - ./src
  - ./README.md
  - ./CHANGELOG.md

api:
  parser: sphinx
  include_private: false
  
output:
  format: mkdocs
  path: ./docs
  theme: material

quality:
  check_links: true
  validate_examples: true
  readability_threshold: 80
EOF

# 3. 生成API文档
doc-gen-skill api --config doc-gen.config.yml

# 4. 本地预览
doc-gen-skill serve --port 8000

# 5. 构建
doc-gen-skill build --output ./site

# 6. 部署
doc-gen-skill deploy --target github-pages
```

### CI/CD自动部署

```yaml
# .github/workflows/docs.yml
name: Documentation

on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'docs/**'
      - 'README.md'

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Dependencies
        run: |
          pip install doc-gen-skill
          pip install -e .
      
      - name: Generate API Docs
        run: doc-gen-skill api --source ./src --output ./docs/api
      
      - name: Check Quality
        run: doc-gen-skill check --path ./docs --strict
      
      - name: Build Site
        run: doc-gen-skill build --config mkdocs.yml
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./site
```

---

## 度量指标

| 指标 | 当前 | 目标 | 测量方法 |
|------|------|------|----------|
| 生成时间 | 手动 | <30秒 | 自动化后测量 |
| 同步延迟 | 无 | <5分钟 | CI/CD触发到部署 |
| 文档覆盖率 | - | >80% | 有文档的API比例 |
| 坏链接率 | - | 0% | 链接检查 |
| 读者满意度 | - | >4/5 | 反馈收集 |

---

## 与其他Skill的协同

```
Doc Gen Skill ←→ Coding Agent
    ↓
自动生成代码文档 + 代码审查反馈

Doc Gen Skill ←→ Git Automation
    ↓
代码提交触发文档更新

Doc Gen Skill ←→ One-Click Backup
    ↓
文档站点备份

Doc Gen Skill ←→ Python Env Manager
    ↓
管理文档生成工具依赖
```

---

## 最佳实践

### 文档策略

```
小型项目:
├── README.md (必需)
├── API文档 (如提供库)
└── 极简配置

中型项目:
├── README.md
├── 用户指南
├── API文档
├── 开发指南
└── Changelog

大型项目:
├── 完整文档站点
├── 多版本支持
├── 多语言支持
├── 搜索功能
└── 社区贡献指南
```

### 文档质量门禁

```
Level 1: 生成时
├── 所有公共API有文档
├── 代码示例可执行
└── 无坏链接

Level 2: 提交前
├── 可读性评分>80
├── 无拼写错误
└── 格式统一

Level 3: 发布前
├── 用户指南完整
├── 快速开始可用
└── 示例代码测试通过
```

---

*多维度分析报告生成时间: 2026-02-19*  
*方法论: 第一性原理 + 系统思维 + 贝叶斯决策 + 博弈论 + 精益思想*
