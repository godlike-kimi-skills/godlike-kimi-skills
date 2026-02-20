# Firecrawl

**Web 数据提取与爬取引擎** - 专为 AI 应用设计的智能爬虫 API

网站地图生成、全站爬取、结构化数据提取，将互联网数据转化为 AI 可用格式。

---

## 核心能力

### 🕷️ 爬取模式

| 功能 | 描述 | 适用场景 |
|------|------|----------|
| **单页爬取** (/scrape) | 提取单个 URL | 快速提取 |
| **全站爬取** (/crawl) | 递归爬取整个网站 | 站点备份 |
| **网站地图** (/map) | 生成站点结构 | 站点分析 |
| **批量爬取** (/batch) | 批量 URL 处理 | 大规模提取 |
| **搜索爬取** (/search) | 搜索+提取 | 研究采集 |

### 📄 输出格式

```
输出选项:
├── Markdown (默认) - 适合 LLM 处理
├── HTML - 原始网页内容
├── Screenshot - 页面截图
├── Links - 提取链接
└── Structured Data - 结构化数据 (LLM提取)
```

---

## 使用方法

### CLI 命令

```bash
# 单页爬取
firecrawl scrape "https://example.com/docs"

# 全站爬取
firecrawl crawl "https://example.com" --output sitemap.md

# 生成网站地图
firecrawl map "https://example.com" --limit 1000

# 批量处理
firecrawl batch --urls urls.txt --output ./data/

# 带截图
firecrawl scrape "https://example.com" --formats markdown,screenshot

# 提取特定内容
firecrawl scrape "https://example.com" --extract "产品名称,价格,描述"
```

### API 调用

```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="fc-...")

# 单页爬取
result = app.scrape_url("https://example.com", params={
    "formats": ["markdown", "html"]
})

# 全站爬取
crawl_result = app.crawl_url("https://example.com", params={
    "limit": 100,
    "scrapeOptions": {
        "formats": ["markdown"]
    }
}, wait_until_done=True)

# 网站地图
map_result = app.map_url("https://example.com", params={
    "search": "documentation",
    "limit": 1000
})
```

---

## 高级功能

### LLM 提取

```python
# 使用 LLM 提取结构化数据
result = app.scrape_url("https://example.com/product/123", params={
    "formats": ["markdown"],
    "extract": {
        "schema": {
            "type": "object",
            "properties": {
                "product_name": {"type": "string"},
                "price": {"type": "number"},
                "description": {"type": "string"},
                "features": {"type": "array", "items": {"type": "string"}}
            }
        }
    }
})
```

### 自定义行为

```python
# 等待特定元素
result = app.scrape_url(url, params={
    "waitFor": 2000,  # 等待 2 秒
    "actions": [
        {"type": "click", "selector": "button.load-more"},
        {"type": "wait", "milliseconds": 1000}
    ]
})

# 移动端爬取
result = app.scrape_url(url, params={
    "mobile": True,
    "viewport": {"width": 375, "height": 667}
})
```

### 批量处理

```python
# 批量 URL
urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    ...
]

batch_result = app.batch_scrape_urls(urls, params={
    "formats": ["markdown"]
})
```

---

## 最佳实践

### 爬取策略

```
1. 尊重 robots.txt
2. 控制爬取频率 (建议 > 1s/请求)
3. 使用 sitemap 限制范围
4. 处理 JavaScript 渲染
5. 错误重试机制
```

### 速率限制

```
免费计划: 500 credits/month
├── /scrape: 1 credit
├── /crawl: 5 credits + 1/page
└── /map: 1 credit

付费计划: 从 $16/month 起
```

### 数据清洗

```python
from firecrawl_connector import Cleaner

cleaner = Cleaner()

# 清洗 Markdown
clean_md = cleaner.clean(
    result["markdown"],
    remove_navigation=True,
    remove_ads=True,
    remove_footer=True
)

# 提取正文
main_content = cleaner.extract_main_content(clean_md)
```

---

## 与 Tavily 对比

| 特性 | Firecrawl | Tavily |
|------|-----------|--------|
| **主要功能** | 网站爬取 | 搜索引擎 |
| **数据范围** | 指定网站 | 全网搜索 |
| **输出格式** | Markdown/HTML | 摘要+链接 |
| **结构化** | LLM 提取 | 基础提取 |
| **实时性** | 取决于目标站 | 实时搜索 |
| **使用场景** | 站点分析、文档提取 | 信息检索 |

### 组合使用

```python
# 1. 搜索发现
tavily_results = tavily.search("best practices", max_results=10)
urls = [r["url"] for r in tavily_results["results"]]

# 2. 深度爬取
for url in urls:
    content = firecrawl.scrape(url)
    # 处理内容...
```

---

## 参考来源

- **Firecrawl**: https://firecrawl.dev
- **文档**: https://docs.firecrawl.dev
- **GitHub**: https://github.com/mendableai/firecrawl

---

## 版本信息

- **Version**: 2.0.0 (2025 增强版)
- **Author**: KbotGenesis
- **API Version**: v1
- **Last Updated**: 2026-02-19
