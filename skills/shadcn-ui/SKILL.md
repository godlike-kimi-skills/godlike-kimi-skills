# shadcn-ui Skill

[English](README.md) | 中文

一个强大的 [shadcn/ui](https://ui.shadcn.com) 组件库集成工具，简化 React 项目中 shadcn/ui 的使用，快速添加、管理和生成 UI 组件。

## 功能特性

- 🚀 **快速初始化** - 一键初始化 shadcn/ui 项目
- 📦 **组件管理** - 安装、更新、移除组件
- 🔍 **智能搜索** - 快速查找所需组件
- 🎨 **主题配置** - 轻松切换主题色
- 🏥 **项目诊断** - 检查项目配置完整性
- 📝 **组件生成** - 快速生成自定义组件模板
- 🔧 **CLI 封装** - 友好的命令行交互

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 初始化项目

```bash
# 在当前目录初始化 shadcn/ui
python main.py --action init

# 指定项目路径
python main.py --action init --project_path ./my-app

# 自动确认并指定主题色
python main.py --action init --yes --base_color zinc
```

### 安装组件

```bash
# 安装单个组件
python main.py --action add --component button

# 批量安装多个组件
python main.py --action add --component button,card,input

# 覆盖已有组件
python main.py --action add --component button --overwrite
```

## 命令详解

### `init` / `install` - 初始化项目

初始化 shadcn/ui 到项目中。

```bash
python main.py --action init [选项]
```

**选项：**
- `--project_path, -p` - 项目路径（默认：当前目录）
- `--base_color` - 基础主题色：`slate` | `zinc` | `neutral` | `gray` | `stone`
- `--yes, -y` - 自动确认所有提示

### `add` - 添加组件

安装一个或多个组件到项目中。

```bash
python main.py --action add --component <组件名> [选项]
```

**示例：**
```bash
python main.py -a add -c button
python main.py -a add -c card,input,button,select
python main.py -a add -c dialog --overwrite --yes
```

### `list` - 列出组件

显示所有可用的 shadcn/ui 组件。

```bash
python main.py --action list
```

输出包含组件名、分类和描述信息。

### `search` - 搜索组件

根据关键词搜索组件。

```bash
python main.py --action search --component <关键词>
```

**示例：**
```bash
python main.py -a search -c form
python main.py -a search -c input
```

### `remove` - 移除组件

删除已安装的组件文件。

```bash
python main.py --action remove --component <组件名>
```

**示例：**
```bash
python main.py -a remove -c button,card
```

### `update` - 更新组件

更新所有已安装的组件到最新版本。

```bash
python main.py --action update
```

### `theme` - 主题配置

查看或修改主题配置。

```bash
# 查看当前主题
python main.py --action theme

# 修改主题色
python main.py --action theme --base_color zinc
```

**可用主题色：**
- `slate` - 石板灰（默认）
- `zinc` - 锌灰
- `neutral` - 中性灰
- `gray` - 灰色
- `stone` - 石灰

### `doctor` - 项目诊断

检查项目配置是否完整。

```bash
python main.py --action doctor
```

诊断项包括：
- ✓ components.json 配置
- ✓ 组件目录结构
- ✓ Tailwind CSS 配置
- ✓ package.json 存在性

### `generate` - 生成组件

生成自定义组件模板。

```bash
python main.py --action generate --component <组件名>
```

**示例：**
```bash
python main.py -a generate -c MyComponent
```

## 组件分类

shadcn/ui 提供 40+ 个高质量组件：

| 分类 | 组件 |
|------|------|
| **Layout** | accordion, aspect-ratio, card, collapsible, resizable, scroll-area, separator, sheet, tabs |
| **Form** | button, checkbox, combobox, command, form, input, input-otp, label, radio-group, select, slider, switch, textarea, toggle, toggle-group |
| **Overlay** | alert-dialog, dialog, drawer, hover-card, popover, sheet, toast, sonner, tooltip |
| **Display** | alert, badge, breadcrumb, calendar, carousel, chart, pagination, progress, skeleton, table |
| **Navigation** | dropdown-menu, menubar, navigation-menu, context-menu, command |

## 项目结构

使用本 skill 初始化后的项目结构：

```
my-app/
├── components/
│   └── ui/              # shadcn/ui 组件目录
│       ├── button.tsx
│       ├── card.tsx
│       └── ...
├── lib/
│   └── utils.ts         # 工具函数
├── components.json      # shadcn/ui 配置
├── tailwind.config.ts   # Tailwind 配置
└── package.json
```

## 配置说明

### components.json

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "app/globals.css",
    "baseColor": "slate",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

## 依赖要求

- **Node.js** >= 18
- **npx** >= 10
- **Python** >= 3.8
- **React** >= 18
- **Tailwind CSS** >= 3.0

## 常见问题

### Q: 如何批量安装组件？

使用逗号分隔组件名：
```bash
python main.py -a add -c button,card,input,select,tabs
```

### Q: 如何覆盖已安装的组件？

使用 `--overwrite` 选项：
```bash
python main.py -a add -c button --overwrite
```

### Q: 如何修改主题色？

```bash
python main.py -a theme --base_color zinc
```

修改后需要重新安装组件以应用新主题。

### Q: 项目诊断显示缺少配置怎么办？

1. 确保在项目根目录执行
2. 运行 `python main.py -a init` 重新初始化
3. 检查 `components.json` 是否存在

### Q: 如何查看已安装的组件？

```bash
python main.py -a doctor
```

诊断信息会显示已安装的组件数量。

## 最佳实践

1. **初始化前** - 确保项目已配置好 Tailwind CSS
2. **组件命名** - 使用小写和连字符，如 `date-picker`
3. **版本管理** - 定期运行 `update` 获取最新组件
4. **自定义主题** - 在 `globals.css` 中修改 CSS 变量
5. **组件组织** - 将自定义组件放在 `components/` 根目录，shadcn 组件放在 `components/ui/`

## 高级用法

### 集成到 CI/CD

```yaml
# .github/workflows/update-components.yml
- name: Update shadcn/ui components
  run: |
    pip install -r requirements.txt
    python main.py --action update
```

### 自定义 Registry

修改 `components.json` 中的 `url` 字段使用私有 registry。

### 扩展组件

基于 shadcn/ui 组件创建业务组件：

```tsx
// components/custom/user-card.tsx
import { Card, CardHeader, CardTitle } from "@/components/ui/card"

export function UserCard({ user }: { user: User }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{user.name}</CardTitle>
      </CardHeader>
    </Card>
  )
}
```

## 相关链接

- [shadcn/ui 官网](https://ui.shadcn.com)
- [组件文档](https://ui.shadcn.com/docs/components)
- [主题生成器](https://ui.shadcn.com/themes)
- [GitHub](https://github.com/shadcn-ui/ui)

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
