---
name: dev-workflow
description: Development workflow management for software projects. Use when starting a new project, setting up project structure, managing development phases, or creating standard workflows for coding tasks.
---

# Dev Workflow

Development workflow management skill for organizing software projects.

## Features

- Project scaffolding and structure setup
- Development phase management
- Standard workflow templates
- Code organization best practices

## Usage

### Initialize a New Project

```bash
python D:/kimi/skills/dev-workflow/scripts/init_project.py <project-name> [--type <type>]
```

Types: `web`, `api`, `cli`, `python-package`, `node-package`

### Create Project Structure

```bash
python D:/kimi/skills/dev-workflow/scripts/init_project.py my-app --type web
```

This creates:
```
my-app/
├── README.md
├── LICENSE
├── .gitignore
├── docs/
├── src/
├── tests/
└── scripts/
```

### Workflow Templates

Available templates:
- **agile** - Sprint-based development
- **github-flow** - Feature branch workflow
- **trunk-based** - Continuous integration

## Best Practices

1. Always start with README
2. Set up version control early
3. Create test structure from day 1
4. Document architecture decisions
