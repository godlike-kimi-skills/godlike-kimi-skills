---
name: next-best-practices
description: Next.js 开发最佳实践检查工具。用于检查 App Router 模式、Server Components、性能优化、SEO、缓存策略和代码模式。当用户需要验证 Next.js 项目结构、优化性能、检查 SEO 配置、分析缓存策略或获取代码改进建议时使用此技能。
---

# Next.js 最佳实践检查器

用于分析和改进 Next.js 项目的专业工具，专注于 App Router 架构的最佳实践。

## 核心功能

- **项目结构检查** - 验证 Next.js 项目目录结构是否符合最佳实践
- **App Router 验证** - 检查 App Router 模式、路由配置和嵌套布局
- **性能优化** - 分析图片、字体、脚本加载等性能关键项
- **SEO 检查** - 验证元数据、OpenGraph、结构化数据
- **缓存策略** - 分析 fetch 缓存、路由段配置和 revalidate 设置
- **代码模式** - 检查 Server/Client Components 使用模式

## 使用方法

### 基本用法

```bash
# 检查整个项目
python main.py --action check --file-path ./my-nextjs-app

# 检查特定文件
python main.py --action check --file-path ./my-nextjs-app/app/page.tsx

# 指定检查类型
python main.py --action check --check-type performance --file-path ./my-nextjs-app

# 输出 JSON 格式
python main.py --action check --output-format json --file-path ./my-nextjs-app
```

### 参数说明

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `--action` | string | 是 | 操作类型: check, fix, suggest, analyze |
| `--file-path` | string | 否 | 目标文件或目录路径 |
| `--check-type` | string | 否 | 检查类型: all, structure, performance, seo, caching, app-router, code-patterns |
| `--output-format` | string | 否 | 输出格式: json, markdown, console |
| `--severity` | string | 否 | 最低报告级别: error, warning, info, suggestion |

### 操作类型详解

#### check - 全面检查
检查项目中存在的问题和可优化项：

```bash
python main.py --action check --file-path ./my-app --check-type all
```

#### fix - 自动修复
尝试自动修复检测到的问题（谨慎使用，建议先备份）：

```bash
python main.py --action fix --file-path ./my-app/app/page.tsx
```

#### suggest - 提供建议
基于项目结构提供改进建议：

```bash
python main.py --action suggest --file-path ./my-app
```

#### analyze - 深度分析
生成详细的项目分析报告：

```bash
python main.py --action analyze --file-path ./my-app --output-format markdown
```

## 检查项目详解

### 1. 项目结构检查 (structure)

验证标准 Next.js 项目结构：

```
my-app/
├── app/                    # App Router (推荐)
│   ├── layout.tsx         # 根布局
│   ├── page.tsx           # 首页
│   ├── loading.tsx        # 加载状态
│   ├── error.tsx          # 错误处理
│   └── globals.css        # 全局样式
├── components/            # React 组件
├── lib/                   # 工具函数
├── public/                # 静态资源
├── next.config.js         # Next.js 配置
├── tsconfig.json          # TypeScript 配置
└── package.json
```

### 2. App Router 验证 (app-router)

检查 App Router 特有模式：

- **文件约定** - layout.tsx, page.tsx, loading.tsx, error.tsx, not-found.tsx
- **嵌套布局** - 验证布局嵌套结构
- **动态路由** - [id], [...slug], [[...catchall]] 使用
- **路由组** - (group) 组织路由
- **并行路由** - @team, @analytics 使用
- **拦截路由** - (.)same-level, (..)parent-level

### 3. 性能优化检查 (performance)

#### 图片优化
```tsx
// ✅ 推荐 - 使用 Next.js Image
import Image from 'next/image'

<Image
  src="/photo.jpg"
  alt="Description"
  width={800}
  height={600}
  priority={true}  // 首屏图片
/>

// ❌ 避免 - 原生 img 标签
<img src="/photo.jpg" alt="Description" />
```

#### 字体优化
```tsx
// ✅ 推荐 - 使用 next/font
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

// ❌ 避免 - 外部字体链接
<link href="https://fonts.googleapis.com/..." />
```

#### 脚本加载
```tsx
// ✅ 推荐 - 使用 next/script
import Script from 'next/script'

<Script
  src="https://analytics.com/script.js"
  strategy="lazyOnload"
/>
```

### 4. SEO 检查 (seo)

验证元数据和 SEO 配置：

```tsx
// ✅ 推荐 - 使用 Metadata API
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '页面标题',
  description: '页面描述',
  openGraph: {
    title: 'OG 标题',
    description: 'OG 描述',
    images: ['/og-image.jpg'],
  },
  robots: {
    index: true,
    follow: true,
  },
}
```

检查项包括：
- 标题和描述
- OpenGraph 标签
- Twitter Cards
- Robots 配置
- Canonical URL
- 结构化数据 (JSON-LD)

### 5. 缓存策略 (caching)

分析数据获取和缓存配置：

```tsx
// ✅ 推荐 - 显式配置 fetch 缓存
// 静态数据 - 长期缓存
const data = await fetch('https://api.example.com/data', {
  cache: 'force-cache',
})

// 动态数据 - 每次请求
const data = await fetch('https://api.example.com/data', {
  cache: 'no-store',
})

// 增量静态再生成
const data = await fetch('https://api.example.com/data', {
  next: { revalidate: 3600 },
})
```

路由段配置：

```tsx
// ✅ 推荐 - 显式声明渲染模式
// app/page.tsx
export const dynamic = 'auto' // 'auto' | 'force-dynamic' | 'error' | 'force-static'
export const revalidate = 3600 // 秒
export const fetchCache = 'auto' // 'auto' | 'default-cache' | 'only-cache' | 'force-cache' | 'force-no-store' | 'default-no-store' | 'only-no-store'
```

### 6. 代码模式 (code-patterns)

#### Server vs Client Components

```tsx
// ✅ Server Component - 默认，无 directive
// 可以直接访问数据库、文件系统等
async function ServerComponent() {
  const data = await db.query('SELECT * FROM users')
  return <div>{data.length} users</div>
}

// ✅ Client Component - 需要 'use client'
'use client'

import { useState } from 'react'

function ClientComponent() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>
}
```

#### 数据获取模式

```tsx
// ✅ 推荐 - 在 Server Component 中获取数据
async function Page() {
  const data = await getData() // 直接 await
  return <Component data={data} />
}

// ✅ 推荐 - 并行获取
async function Page() {
  const [users, posts] = await Promise.all([
    getUsers(),
    getPosts(),
  ])
  return <Component users={users} posts={posts} />
}
```

#### Streaming 模式

```tsx
// ✅ 推荐 - 使用 Suspense 实现流式渲染
import { Suspense } from 'react'

export default function Page() {
  return (
    <>
      <h1>立即渲染的标题</h1>
      <Suspense fallback={<Loading />}>
        <SlowComponent />
      </Suspense>
    </>
  )
}
```

## 输出示例

### Console 输出

```
🔍 Next.js Best Practices Check
==============================

📁 Project Structure
  ✅ app/ directory exists
  ✅ layout.tsx found
  ✅ page.tsx found
  ✅ globals.css found

🚀 App Router
  ✅ Using App Router architecture
  ⚠️  Missing loading.tsx (建议添加)
  ✅ error.tsx found

⚡ Performance
  ✅ Using next/image for images
  ✅ Using next/font for fonts
  ⚠️  Script without strategy (app/layout.tsx:25)

🔍 SEO
  ✅ Metadata configured
  ✅ OpenGraph tags present
  ⚠️  Missing robots.txt

📦 Caching
  ✅ Fetch cache configured
  ⚠️  Route without revalidate (app/blog/page.tsx)

📊 Code Patterns
  ✅ Proper Server Component usage
  ⚠️  Client Component without 'use client' (components/Chart.tsx:1)

==============================
Results: 12 passed, 5 warnings, 0 errors
```

### JSON 输出

```json
{
  "summary": {
    "total": 17,
    "passed": 12,
    "warnings": 5,
    "errors": 0
  },
  "checks": {
    "structure": { "status": "pass", "items": [...] },
    "appRouter": { "status": "pass", "items": [...] },
    "performance": { "status": "warning", "items": [...] },
    "seo": { "status": "warning", "items": [...] },
    "caching": { "status": "warning", "items": [...] },
    "codePatterns": { "status": "pass", "items": [...] }
  }
}
```

## 最佳实践速查表

### 必做项
- [ ] 使用 App Router (app/ 目录)
- [ ] 使用 next/image 代替 img 标签
- [ ] 使用 next/font 加载字体
- [ ] 配置 Metadata API
- [ ] 添加 error.tsx 和 loading.tsx
- [ ] 显式配置 fetch cache

### 推荐项
- [ ] 使用 TypeScript
- [ ] 使用 ESLint + Prettier
- [ ] 实现 ISR 用于动态内容
- [ ] 配置 Image domains
- [ ] 添加 sitemap.xml
- [ ] 配置 robots.txt

### 避免项
- [ ] 在 Client Component 中直接导入 Server Component
- [ ] 在 Server Component 中使用浏览器 API
- [ ] 混合 async/await 和 useEffect 获取数据
- [ ] 忽略 Image 的 width/height
- [ ] 使用内联脚本而非 next/script

## 故障排除

### 常见问题

**Q: 检查器报告 "Missing 'use client'" 但组件确实是 Server Component**
A: 确保没有在 Client Component 中导入该组件。

**Q: 图片优化检查失败但使用了 next/image**
A: 检查是否配置了 next.config.js 中的 images.domains。

**Q: 缓存检查报告动态路由没有配置**
A: 动态路由默认是动态的，如需静态生成请添加 generateStaticParams。

## 相关资源

- [Next.js 官方文档](https://nextjs.org/docs)
- [App Router 文档](https://nextjs.org/docs/app)
- [Next.js 性能最佳实践](https://nextjs.org/docs/app/building-your-application/optimizing)
- [Core Web Vitals](https://web.dev/vitals/)
