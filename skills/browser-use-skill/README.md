# Browser Use Skill 🤖🌐

AI浏览器自动化工具，提供类似 [browser-use](https://github.com/browser-use/browser-use) 框架的功能，支持智能网页浏览、表单填写、数据提取和截图。

## ✨ 功能特性

- **🌍 智能网页浏览** - 基于 Playwright 的高性能浏览器自动化
- **📝 表单自动填写** - 智能识别和填写各类网页表单
- **🔍 结构化数据提取** - 从网页中提取链接、图片、表格、表单等数据
- **📸 页面截图** - 支持全页面或特定元素截图
- **⚡ 异步高性能** - 完全基于 asyncio 的异步架构
- **🔐 安全可控** - 支持 Cookie 管理和用户代理设置

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
playwright install
```

### 基础用法

```python
import asyncio
from main import BrowserUseSkill, BrowserConfig

async def main():
    # 创建配置
    config = BrowserConfig(
        headless=False,  # 显示浏览器窗口
        viewport_width=1920,
        viewport_height=1080
    )
    
    # 使用异步上下文管理器
    async with BrowserUseSkill(config) as skill:
        # 访问网页
        await skill.navigate("https://example.com")
        
        # 提取页面数据
        data = await skill.extract_data()
        print(f"页面标题: {data.title}")
        print(f"链接数量: {len(data.links)}")
        
        # 截图
        screenshot_path = await skill.screenshot("example.png")
        print(f"截图保存: {screenshot_path}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 表单填写示例

```python
async with BrowserUseSkill() as skill:
    await skill.navigate("https://example.com/login")
    
    # 填写登录表单
    await skill.fill_form({
        "#username": "myuser",
        "#password": "mypass"
    }, submit=True)
    
    # 等待页面加载
    await skill.wait_for_element(".dashboard")
```

### 数据提取示例

```python
# 提取特定数据
selectors = {
    "price": ".product-price",
    "title": "h1.product-title",
    "description": ".product-desc"
}

data = await skill.extract_data(selectors)
for element in data.elements:
    print(f"{element['name']}: {element['text']}")
```

## 📖 API 文档

### BrowserConfig

配置浏览器行为：

```python
@dataclass
class BrowserConfig:
    headless: bool = True              # 无头模式
    viewport_width: int = 1920         # 视口宽度
    viewport_height: int = 1080        # 视口高度
    timeout: int = 30000               # 超时时间(ms)
    user_agent: str = "..."            # 用户代理
    download_dir: str = "./downloads"  # 下载目录
    screenshot_dir: str = "./screenshots"  # 截图目录
```

### BrowserUseSkill 方法

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `start()` | 启动浏览器 | `self` |
| `stop()` | 关闭浏览器 | `None` |
| `navigate(url)` | 导航到URL | `bool` |
| `fill_form(data, submit)` | 填写表单 | `bool` |
| `click(selector)` | 点击元素 | `bool` |
| `extract_data(selectors)` | 提取数据 | `ExtractedData` |
| `screenshot(filename)` | 截图 | `str` |
| `execute_javascript(script)` | 执行JS | `Any` |
| `scroll_to_bottom()` | 滚动到底部 | `None` |
| `wait_for_element(selector)` | 等待元素 | `bool` |

## 🧪 运行测试

```bash
cd tests
python -m pytest test_basic.py -v
```

## 📁 项目结构

```
browser-use-skill/
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

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 许可证

本项目基于 [MIT](LICENSE) 许可证开源。

## 🙏 致谢

- [Playwright](https://playwright.dev/) - 强大的浏览器自动化框架
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML解析库

---

由 [Godlike Kimi Skills](https://github.com/godlike-kimi-skills) 精心打造 ❤️
