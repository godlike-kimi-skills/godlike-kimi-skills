# Browser Use Skill

AI浏览器自动化工具 Skill，用于 Kimi Code CLI。

## 用途

提供智能网页浏览、表单填写、数据提取和截图功能，支持Playwright驱动的高性能浏览器自动化操作。

## 功能

- **网页浏览**：导航、前进、后退、刷新
- **表单填写**：自动识别表单字段并填写
- **数据提取**：提取链接、图片、表格、表单结构
- **截图**：全页面或元素级截图
- **JavaScript执行**：在页面中执行自定义JS
- **Cookie管理**：获取和设置Cookies

## 使用方法

### 基础用法

```python
from skills.browser_use_skill.main import BrowserUseSkill, BrowserConfig

async with BrowserUseSkill() as browser:
    await browser.navigate("https://example.com")
    data = await browser.extract_data()
```

### 作为Skill使用

```bash
kimi -c "使用browser-use-skill访问 https://example.com 并提取所有链接"
```

### Python API

详见 main.py 中的 `BrowserUseSkill` 类文档。

## 配置选项

- `headless`: 是否使用无头模式 (默认: True)
- `viewport`: 视口尺寸 (默认: 1920x1080)
- `timeout`: 操作超时时间 (默认: 30s)
- `user_agent`: 自定义User-Agent

## 依赖

- playwright >= 1.40.0
- beautifulsoup4 >= 4.12.0
- Pillow >= 10.0.0

## 安装

```bash
pip install -r requirements.txt
playwright install chromium
```

## 注意事项

1. 首次使用需要运行 `playwright install` 安装浏览器
2. 无头模式下截图可能有所不同
3. 某些网站可能有反爬虫机制

## 维护者

Godlike Kimi Skills
