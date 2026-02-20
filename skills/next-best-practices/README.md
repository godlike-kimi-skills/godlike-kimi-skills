# Next.js Best Practices

<p align="center">
  <strong>🚀 A comprehensive Next.js development best practices checker</strong><br>
  <em>专注于 App Router 架构的智能代码检查工具</em>
</p>

<p align="center">
  <a href="#english">English</a> | <a href="#chinese">中文</a>
</p>

---

<a name="english"></a>
## 🇺🇸 English

A professional tool for analyzing and improving Next.js projects, with focus on App Router architecture best practices.

### ✨ Features

- **📁 Project Structure** - Validate Next.js project directory structure
- **🚀 App Router** - Check App Router patterns, routing configs, nested layouts
- **⚡ Performance** - Analyze images, fonts, scripts, and loading performance
- **🔍 SEO** - Validate metadata, OpenGraph, structured data
- **📦 Caching** - Analyze fetch cache, route segment config, revalidate
- **📝 Code Patterns** - Check Server/Client Components usage patterns

### 🚀 Quick Start

```bash
# Clone the skill
cd your-nextjs-project

# Check entire project
python main.py --action check --file-path .

# Check specific file
python main.py --action check --file-path ./app/page.tsx

# Check specific aspect
python main.py --action check --check-type performance --file-path .

# Output as JSON
python main.py --action check --output-format json --file-path .
```

### 📋 Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--action` | string | Yes | Action type: check, fix, suggest, analyze |
| `--file-path` | string | No | Target file or directory path |
| `--check-type` | string | No | Check type: all, structure, performance, seo, caching, app-router, code-patterns |
| `--output-format` | string | No | Output format: json, markdown, console |
| `--severity` | string | No | Minimum severity: error, warning, info, suggestion |

### 🔍 Check Types

#### Structure Check
```bash
python main.py --action check --check-type structure --file-path ./my-app
```

Validates standard Next.js project structure including:
- `app/` directory with App Router
- `components/`, `lib/`, `public/` directories
- Configuration files (next.config.js, tsconfig.json, etc.)

#### App Router Check
```bash
python main.py --action check --check-type app-router --file-path ./my-app
```

Checks App Router specific patterns:
- File conventions (layout.tsx, page.tsx, loading.tsx, error.tsx)
- Nested layouts structure
- Dynamic routes ([id], [...slug], [[...catchall]])
- Route groups ((group))
- Parallel routes (@team, @analytics)
- Intercept routes ((.), (..), (...))

#### Performance Check
```bash
python main.py --action check --check-type performance --file-path ./my-app
```

Analyzes performance optimizations:
- ✅ Using `next/image` instead of `img`
- ✅ Using `next/font` for font loading
- ✅ Using `next/script` with proper strategy
- ⚠️ Large bundle size indicators
- ⚠️ Unoptimized images

#### SEO Check
```bash
python main.py --action check --check-type seo --file-path ./my-app
```

Validates SEO configurations:
- Metadata API usage
- OpenGraph tags
- Twitter Cards
- Robots configuration
- Canonical URLs
- Structured data (JSON-LD)

#### Caching Check
```bash
python main.py --action check --check-type caching --file-path ./my-app
```

Analyzes caching strategies:
- Fetch cache configuration
- Route segment config (dynamic, revalidate)
- ISR implementation
- Cache headers

#### Code Patterns Check
```bash
python main.py --action check --check-type code-patterns --file-path ./my-app
```

Checks Server/Client Component patterns:
- Proper use of 'use client' directive
- Server Component data fetching
- Suspense and Streaming
- Component composition patterns

### 📊 Output Example

```
🔍 Next.js Best Practices Check
==============================

📁 Project Structure
  ✅ app/ directory exists
  ✅ layout.tsx found
  ✅ page.tsx found

🚀 App Router
  ✅ Using App Router architecture
  ⚠️  Missing loading.tsx

⚡ Performance
  ✅ Using next/image for images
  ✅ Using next/font for fonts

==============================
Results: 12 passed, 1 warning, 0 errors
```

---

<a name="chinese"></a>
## 🇨🇳 中文

用于分析和改进 Next.js 项目的专业工具，专注于 App Router 架构的最佳实践。

### ✨ 功能特性

- **📁 项目结构检查** - 验证 Next.js 项目目录结构
- **🚀 App Router 验证** - 检查 App Router 模式、路由配置、嵌套布局
- **⚡ 性能优化** - 分析图片、字体、脚本和加载性能
- **🔍 SEO 检查** - 验证元数据、OpenGraph、结构化数据
- **📦 缓存策略** - 分析 fetch 缓存、路由段配置、重新验证
- **📝 代码模式** - 检查 Server/Client Components 使用模式

### 🚀 快速开始

```bash
# 进入你的 Next.js 项目
cd your-nextjs-project

# 检查整个项目
python main.py --action check --file-path .

# 检查特定文件
python main.py --action check --file-path ./app/page.tsx

# 检查特定方面
python main.py --action check --check-type performance --file-path .

# 输出 JSON 格式
python main.py --action check --output-format json --file-path .
```

### 📋 参数说明

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `--action` | string | 是 | 操作类型: check, fix, suggest, analyze |
| `--file-path` | string | 否 | 目标文件或目录路径 |
| `--check-type` | string | 否 | 检查类型: all, structure, performance, seo, caching, app-router, code-patterns |
| `--output-format` | string | 否 | 输出格式: json, markdown, console |
| `--severity` | string | 否 | 最低严重级别: error, warning, info, suggestion |

### 🔍 检查类型

#### 结构检查
```bash
python main.py --action check --check-type structure --file-path ./my-app
```

验证标准 Next.js 项目结构，包括：
- `app/` 目录使用 App Router
- `components/`, `lib/`, `public/` 目录
- 配置文件 (next.config.js, tsconfig.json 等)

#### App Router 检查
```bash
python main.py --action check --check-type app-router --file-path ./my-app
```

检查 App Router 特有模式：
- 文件约定 (layout.tsx, page.tsx, loading.tsx, error.tsx)
- 嵌套布局结构
- 动态路由 ([id], [...slug], [[...catchall]])
- 路由组 ((group))
- 并行路由 (@team, @analytics)
- 拦截路由 ((.), (..), (...))

#### 性能检查
```bash
python main.py --action check --check-type performance --file-path ./my-app
```

分析性能优化：
- ✅ 使用 `next/image` 代替 `img`
- ✅ 使用 `next/font` 加载字体
- ✅ 使用 `next/script` 并配置策略
- ⚠️ 大包体积指示
- ⚠️ 未优化的图片

#### SEO 检查
```bash
python main.py --action check --check-type seo --file-path ./my-app
```

验证 SEO 配置：
- Metadata API 使用
- OpenGraph 标签
- Twitter Cards
- Robots 配置
- Canonical URL
- 结构化数据 (JSON-LD)

#### 缓存检查
```bash
python main.py --action check --check-type caching --file-path ./my-app
```

分析缓存策略：
- Fetch 缓存配置
- 路由段配置 (dynamic, revalidate)
- ISR 实现
- 缓存头

#### 代码模式检查
```bash
python main.py --action check --check-type code-patterns --file-path ./my-app
```

检查 Server/Client Component 模式：
- 正确使用 'use client' 指令
- Server Component 数据获取
- Suspense 和 Streaming
- 组件组合模式

### 📊 输出示例

```
🔍 Next.js Best Practices Check
==============================

📁 Project Structure
  ✅ app/ directory exists
  ✅ layout.tsx found
  ✅ page.tsx found

🚀 App Router
  ✅ Using App Router architecture
  ⚠️  Missing loading.tsx

⚡ Performance
  ✅ Using next/image for images
  ✅ Using next/font for fonts

==============================
Results: 12 passed, 1 warning, 0 errors
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 🔗 Links

- [Next.js Documentation](https://nextjs.org/docs)
- [App Router Guide](https://nextjs.org/docs/app)
- [Next.js Performance](https://nextjs.org/docs/app/building-your-application/optimizing)

---

<p align="center">
  Made with ❤️ for the Next.js community
</p>
