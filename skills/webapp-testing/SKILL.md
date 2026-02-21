# Webapp Testing - Web应用自动化测试

> 完整的Web应用端到端测试解决方案，支持多浏览器测试、视觉回归测试、性能测试和截图对比

---

## 功能概述

本Skill提供企业级的Web应用测试能力，基于Playwright构建，支持多种测试类型和报告生成。

## 何时使用本Skill

**Use this skill when:**
- 需要创建Web应用的端到端(E2E)测试
- 执行视觉回归测试，对比页面截图
- 进行Web应用性能测试
- 多浏览器兼容性测试
- 自动化测试流程集成

**触发关键词：** "web testing", "E2E test", "browser automation test", "visual testing", "screenshot comparison", "性能测试", "回归测试"

**典型场景：**
1. 新功能上线前的回归测试
2. UI改版后的视觉对比
3. 页面加载性能监控
4. 跨浏览器兼容性验证
5. 持续集成中的自动化测试

### 核心能力

1. **端到端测试** - 模拟用户操作流程，验证业务逻辑
2. **视觉回归测试** - 像素级截图对比，检测UI变化
3. **性能测试** - 收集Web Vitals指标，分析页面性能
4. **多浏览器支持** - Chromium、Firefox、WebKit三大引擎
5. **报告生成** - HTML/JSON格式测试报告

---

## 使用方法

### 基础用法

```bash
# 运行基础测试
kimi skill run webapp-testing --params "action=test&url=https://example.com"

# 截取页面截图
kimi skill run webapp-testing --params "action=visual&url=https://example.com&screenshot_path=./screenshot.png"

# 运行性能测试
kimi skill run webapp-testing --params "action=performance&url=https://example.com"

# 对比两张截图
kimi skill run webapp-testing --params "action=compare&baseline_path=./baseline.png&screenshot_path=./current.png"

# 生成配置文件模板
kimi skill run webapp-testing --params "action=generate-config"
```

### 高级用法

```bash
# 指定浏览器和视口大小
kimi skill run webapp-testing \
  --params "action=visual&url=https://example.com&browser=firefox&viewport_width=1280&viewport_height=720"

# 带视觉对比的测试
kimi skill run webapp-testing \
  --params "action=visual&url=https://example.com&baseline_path=./baseline.png&threshold=0.05"

# 非无头模式（可见浏览器）
kimi skill run webapp-testing \
  --params "action=test&url=https://example.com&headless=false"
```

---

## 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|-------|------|------|-------|------|
| `action` | string | 是 | - | 操作类型: test/visual/performance/compare/generate-config |
| `url` | string | 条件 | - | 目标网页URL |
| `browser` | string | 否 | chromium | 浏览器: chromium/firefox/webkit |
| `headless` | boolean | 否 | true | 是否无头模式 |
| `screenshot_path` | string | 否 | auto | 截图保存路径 |
| `baseline_path` | string | 否 | - | 基准截图路径 |
| `output_dir` | string | 否 | ./test-results | 输出目录 |
| `viewport_width` | integer | 否 | 1920 | 视口宽度 |
| `viewport_height` | integer | 否 | 1080 | 视口高度 |
| `threshold` | float | 否 | 0.1 | 视觉对比阈值(0-1) |
| `timeout` | integer | 否 | 30000 | 超时时间(毫秒) |

---

## 示例

### 示例1：电商网站结账流程测试

```bash
kimi skill run webapp-testing \
  --params "action=test&url=https://shop.example.com"
```

测试步骤配置(test-config.json):
```json
{
  "tests": [
    {
      "name": "Add to Cart",
      "steps": [
        {"action": "navigate", "url": "https://shop.example.com/product/123"},
        {"action": "click", "selector": "[data-testid='add-to-cart']"},
        {"action": "wait", "selector": "[data-testid='cart-count']"},
        {"action": "assert", "selector": "[data-testid='cart-count']", "text": "1"}
      ]
    }
  ]
}
```

### 示例2：视觉回归测试

```bash
# 1. 先生成基准截图
kimi skill run webapp-testing \
  --params "action=visual&url=https://app.example.com&screenshot_path=./baselines/homepage.png"

# 2. 开发后对比
kimi skill run webapp-testing \
  --params "action=visual&url=https://app.example.com&baseline_path=./baselines/homepage.png&threshold=0.05"
```

### 示例3：性能基准测试

```bash
kimi skill run webapp-testing \
  --params "action=performance&url=https://app.example.com&browser=chromium"
```

输出示例:
```json
{
  "url": "https://app.example.com",
  "timestamp": "2026-02-21T10:30:00",
  "load_time_ms": 1250.5,
  "dom_content_loaded_ms": 680.2,
  "first_paint_ms": 520.0,
  "first_contentful_paint_ms": 680.0,
  "largest_contentful_paint_ms": 1200.0,
  "total_resource_size_kb": 2450.5,
  "resource_count": 45
}
```

### 示例4：多浏览器测试

```bash
# Chromium
kimi skill run webapp-testing \
  --params "action=visual&url=https://example.com&browser=chromium&screenshot_path=./chromium.png"

# Firefox
kimi skill run webapp-testing \
  --params "action=visual&url=https://example.com&browser=firefox&screenshot_path=./firefox.png"

# WebKit (Safari)
kimi skill run webapp-testing \
  --params "action=visual&url=https://example.com&browser=webkit&screenshot_path=./webkit.png"
```

---

## 测试报告

### HTML报告

测试完成后自动生成可视化HTML报告，包含:
- 测试汇总统计
- 通过/失败状态
- 详细步骤结果
- 错误信息
- 截图对比结果

报告位置: `./test-results/report.html`

### JSON报告

结构化数据报告，便于CI/CD集成:
```json
{
  "timestamp": "2026-02-21T10:30:00",
  "results": {
    "total": 10,
    "passed": 9,
    "failed": 1,
    "steps": [...]
  }
}
```

---

## 最佳实践

### 1. 视觉测试策略

```bash
# 设置合理的对比阈值
# - 0.01 (1%): 非常严格，像素级对比
# - 0.05 (5%): 推荐值，忽略微小差异
# - 0.10 (10%): 宽松，允许动画等差异

kimi skill run webapp-testing \
  --params "action=visual&url=https://example.com&threshold=0.05"
```

### 2. 性能测试标准

| 指标 | 良好 | 需改进 | 差 |
|------|------|--------|-----|
| LCP | < 2.5s | 2.5-4s | > 4s |
| FID | < 100ms | 100-300ms | > 300ms |
| CLS | < 0.1 | 0.1-0.25 | > 0.25 |

### 3. CI/CD集成

```yaml
# .github/workflows/test.yml
name: Web Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run E2E Tests
        run: |
          kimi skill run webapp-testing \
            --params "action=test&url=http://localhost:3000"
      - name: Upload Test Results
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: ./test-results/
```

---

## 技术细节

### 依赖要求

- Python 3.10+
- Playwright 1.40+
- Pillow 10.0+
- NumPy 1.24+

### 浏览器支持

| 浏览器 | 引擎 | 支持状态 |
|--------|------|---------|
| Chrome/Edge | Chromium | ✅ 完全支持 |
| Firefox | Gecko | ✅ 完全支持 |
| Safari | WebKit | ✅ 完全支持 |

### 视觉对比算法

1. **像素差异计算** - 使用PIL ImageChops
2. **相似度评分** - 基于差异像素比例
3. **阈值判断** - 可配置的通过/失败标准
4. **差异可视化** - 生成高亮差异图

---

## 故障排除

### 常见问题

**Q: 浏览器启动失败**
```bash
# 安装浏览器依赖
playwright install
playwright install-deps
```

**Q: 截图对比不准确**
- 检查页面是否完全加载完成
- 调整threshold参数
- 确保截图尺寸一致

**Q: 性能指标为null**
- 某些指标需要实际用户交互才能触发
- 确保页面使用标准Web Vitals API

---

## API参考

### WebAppTester类

```python
async with WebAppTester(config) as tester:
    await tester.navigate("https://example.com")
    await tester.take_screenshot("./screenshot.png")
    metrics = await tester.run_performance_test()
```

### VisualComparator类

```python
result = VisualComparator.compare_images(
    baseline_path="./baseline.png",
    current_path="./current.png",
    threshold=0.1
)
print(f"Similarity: {result.similarity_score}")
print(f"Passed: {result.passed}")
```

---

*Version: 1.0.0 | License: MIT | Author: Godlike Kimi Skills*
