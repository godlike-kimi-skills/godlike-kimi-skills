# Agent Browser

**生产级网页自动化** - 借鉴 Playwright, Scrapy, Puppeteer

支持浏览器自动化、内容提取、数据抓取、JavaScript渲染、反检测机制。

---

## 核心特性

### 🌐 浏览器引擎 (借鉴 Playwright)

| 特性 | 实现 | 说明 |
|------|------|------|
| **多浏览器** | Chromium/Firefox/WebKit | 跨浏览器支持 |
| **Headless** | 无头模式 | 后台运行 |
| **移动模拟** | 设备仿真 | 手机/平板模式 |
| **代理支持** | HTTP/SOCKS5 | IP轮换 |
| **Cookie管理** | 持久化存储 | 会话保持 |
| **JS渲染** | 完整引擎 | 动态内容 |

### 🕷️ 爬虫框架 (借鉴 Scrapy)

```
架构:
┌──────────┐    ┌──────────┐    ┌──────────┐
│ Scheduler│───→│ Downloader│───→│  Parser  │
└──────────┘    └──────────┘    └──────────┘
      ↑                              │
      └──────────┐                   │
                 ↓                   ↓
            ┌──────────┐    ┌──────────┐
            │  Pipeline │←───│ Item     │
            └──────────┘    └──────────┘
```

### 🛡️ 反检测机制

| 机制 | 实现 |
|------|------|
| User-Agent轮换 | 真实浏览器UA库 |
| 指纹混淆 | WebGL/Canvas噪声 |
| 行为模拟 | 人类化鼠标移动 |
| 请求间隔 | 随机延迟 |
| Cookie管理 | 自动Jar管理 |

---

## 使用方法

### 基础浏览
```bash
# 获取网页内容
python ~/.kimi/skills/agent-browser/scripts/browser.py fetch \
  --url "https://example.com" \
  --output page.html

# 截图
python ~/.kimi/skills/agent-browser/scripts/browser.py screenshot \
  --url "https://example.com" \
  --output screenshot.png \
  --full-page

# PDF导出
python ~/.kimi/skills/agent-browser/scripts/browser.py pdf \
  --url "https://example.com" \
  --output page.pdf
```

### 内容提取
```bash
# CSS选择器提取
python ~/.kimi/skills/agent-browser/scripts/extract.py \
  --url "https://news.ycombinator.com" \
  --selector ".titleline>a" \
  --limit 10

# XPath提取
python ~/.kimi/skills/agent-browser/scripts/extract.py \
  --url "https://example.com" \
  --xpath "//h1/text()"

# 结构化提取 (JSON Schema)
python ~/.kimi/skills/agent-browser/scripts/extract.py \
  --url "https://example.com/product" \
  --schema '{"name": "h1", "price": ".price", "description": ".desc"}'
```

### 浏览器自动化
```bash
# 表单填写
python ~/.kimi/skills/agent-browser/scripts/automate.py \
  --url "https://example.com/login" \
  --actions '[
    {"type": "fill", "selector": "#username", "value": "user"},
    {"type": "fill", "selector": "#password", "value": "pass"},
    {"type": "click", "selector": "#submit"}
  ]'

# 滚动截取长页面
python ~/.kimi/skills/agent-browser/scripts/automate.py \
  --url "https://example.com/long-page" \
  --scroll --output full.png
```

---

## 参考实现

### 开源项目
- **Playwright**: https://playwright.dev/ - Microsoft的浏览器自动化
- **Scrapy**: https://scrapy.org/ - Python爬虫框架
- **Puppeteer**: https://pptr.dev/ - Google的Node.js自动化
- **Selenium**: https://www.selenium.dev/ - WebDriver标准

### 浏览器协议
- **Chrome DevTools Protocol (CDP)**: 调试协议
- **WebDriver BiDi**: 下一代WebDriver标准

---

## 版本信息

- **Version**: 2.0.0
- **Author**: KbotGenesis
- **References**: Playwright, Scrapy, Puppeteer
