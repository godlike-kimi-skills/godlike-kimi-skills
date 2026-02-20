# shadcn-ui Skill

English | [中文](SKILL.md)

A powerful integration tool for [shadcn/ui](https://ui.shadcn.com) component library. Simplifies the usage of shadcn/ui in React projects, enabling rapid addition, management, and generation of UI components.

## Features

- 🚀 **Quick Initialization** - One-click initialization of shadcn/ui projects
- 📦 **Component Management** - Install, update, and remove components
- 🔍 **Smart Search** - Quickly find the components you need
- 🎨 **Theme Configuration** - Easily switch between theme colors
- 🏥 **Project Diagnostics** - Check project configuration integrity
- 📝 **Component Generation** - Rapid generation of custom component templates
- 🔧 **CLI Wrapper** - Friendly command-line interaction

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Initialize Project

```bash
# Initialize shadcn/ui in current directory
python main.py --action init

# Specify project path
python main.py --action init --project_path ./my-app

# Auto-confirm and specify theme color
python main.py --action init --yes --base_color zinc
```

### Install Components

```bash
# Install a single component
python main.py --action add --component button

# Batch install multiple components
python main.py --action add --component button,card,input

# Overwrite existing component
python main.py --action add --component button --overwrite
```

## Command Reference

### `init` / `install` - Initialize Project

Initialize shadcn/ui in your project.

```bash
python main.py --action init [options]
```

**Options:**
- `--project_path, -p` - Project path (default: current directory)
- `--base_color` - Base theme color: `slate` | `zinc` | `neutral` | `gray` | `stone`
- `--yes, -y` - Auto-confirm all prompts

### `add` - Add Components

Install one or more components to your project.

```bash
python main.py --action add --component <name> [options]
```

**Examples:**
```bash
python main.py -a add -c button
python main.py -a add -c card,input,button,select
python main.py -a add -c dialog --overwrite --yes
```

### `list` - List Components

Display all available shadcn/ui components.

```bash
python main.py --action list
```

Output includes component name, category, and description.

### `search` - Search Components

Search for components by keyword.

```bash
python main.py --action search --component <keyword>
```

**Examples:**
```bash
python main.py -a search -c form
python main.py -a search -c input
```

### `remove` - Remove Components

Delete installed component files.

```bash
python main.py --action remove --component <name>
```

**Examples:**
```bash
python main.py -a remove -c button,card
```

### `update` - Update Components

Update all installed components to the latest version.

```bash
python main.py --action update
```

### `theme` - Theme Configuration

View or modify theme settings.

```bash
# View current theme
python main.py --action theme

# Change theme color
python main.py --action theme --base_color zinc
```

**Available theme colors:**
- `slate` - Slate gray (default)
- `zinc` - Zinc gray
- `neutral` - Neutral gray
- `gray` - Gray
- `stone` - Stone

### `doctor` - Project Diagnostics

Check if project configuration is complete.

```bash
python main.py --action doctor
```

Diagnostics include:
- ✓ components.json configuration
- ✓ Component directory structure
- ✓ Tailwind CSS configuration
- ✓ package.json existence

### `generate` - Generate Components

Generate custom component templates.

```bash
python main.py --action generate --component <name>
```

**Examples:**
```bash
python main.py -a generate -c MyComponent
```

## Component Categories

shadcn/ui provides 40+ high-quality components:

| Category | Components |
|----------|------------|
| **Layout** | accordion, aspect-ratio, card, collapsible, resizable, scroll-area, separator, sheet, tabs |
| **Form** | button, checkbox, combobox, command, form, input, input-otp, label, radio-group, select, slider, switch, textarea, toggle, toggle-group |
| **Overlay** | alert-dialog, dialog, drawer, hover-card, popover, sheet, toast, sonner, tooltip |
| **Display** | alert, badge, breadcrumb, calendar, carousel, chart, pagination, progress, skeleton, table |
| **Navigation** | dropdown-menu, menubar, navigation-menu, context-menu, command |

## Project Structure

Project structure after initialization with this skill:

```
my-app/
├── components/
│   └── ui/              # shadcn/ui component directory
│       ├── button.tsx
│       ├── card.tsx
│       └── ...
├── lib/
│   └── utils.ts         # Utility functions
├── components.json      # shadcn/ui configuration
├── tailwind.config.ts   # Tailwind configuration
└── package.json
```

## Configuration

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

## Requirements

- **Node.js** >= 18
- **npx** >= 10
- **Python** >= 3.8
- **React** >= 18
- **Tailwind CSS** >= 3.0

## FAQ

### Q: How to batch install components?

Use comma-separated component names:
```bash
python main.py -a add -c button,card,input,select,tabs
```

### Q: How to overwrite installed components?

Use the `--overwrite` option:
```bash
python main.py -a add -c button --overwrite
```

### Q: How to change the theme color?

```bash
python main.py -a theme --base_color zinc
```

After changing, reinstall components to apply the new theme.

### Q: What if project diagnostics show missing configuration?

1. Ensure you're in the project root directory
2. Run `python main.py -a init` to reinitialize
3. Check if `components.json` exists

### Q: How to see installed components?

```bash
python main.py -a doctor
```

The diagnostic info will show the number of installed components.

## Best Practices

1. **Before initialization** - Ensure Tailwind CSS is configured in your project
2. **Component naming** - Use lowercase and hyphens, e.g., `date-picker`
3. **Version management** - Regularly run `update` to get the latest components
4. **Custom themes** - Modify CSS variables in `globals.css`
5. **Component organization** - Put custom components in `components/` root, shadcn components in `components/ui/`

## Advanced Usage

### Integration with CI/CD

```yaml
# .github/workflows/update-components.yml
- name: Update shadcn/ui components
  run: |
    pip install -r requirements.txt
    python main.py --action update
```

### Custom Registry

Modify the `url` field in `components.json` to use a private registry.

### Extending Components

Create business components based on shadcn/ui components:

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

## Links

- [shadcn/ui Official](https://ui.shadcn.com)
- [Component Documentation](https://ui.shadcn.com/docs/components)
- [Theme Generator](https://ui.shadcn.com/themes)
- [GitHub](https://github.com/shadcn-ui/ui)

## License

MIT License - see [LICENSE](LICENSE) file

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/godlike-kimi">godlike-kimi</a>
</p>
