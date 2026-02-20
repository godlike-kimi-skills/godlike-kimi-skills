# Kanban Skill

A Markdown-based Kanban board management tool with YAML frontmatter support. No database required - everything is stored as plain text files.

## Features

- 📝 **Pure Markdown Storage** - All boards and cards stored as `.md` files
- 🏷️ **YAML Frontmatter** - Rich metadata support for cards
- 📊 **Multiple Columns** - Customizable Kanban columns
- 🔍 **Statistics & Reports** - Track card distribution and progress
- 💾 **JSON Export** - Export boards to JSON format
- 🔒 **Automatic Backup** - Built-in backup functionality
- 🌐 **Multi-language Support** - Full Unicode/Chinese support

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Create a Board

```bash
python main.py create "My Project Board" --desc "Project tasks" --columns 待办 进行中 已完成
```

### Add a Card

```bash
python main.py add my_project_board "Design Homepage" --priority high --tags frontend,urgent --due 2024-12-31
```

### List All Boards

```bash
python main.py list
```

### Move a Card

```bash
python main.py move my_project_board card_0 进行中
```

### View Statistics

```bash
python main.py stats my_project_board
```

## Programmatic Usage

```python
from main import KanbanManager

# Initialize manager
manager = KanbanManager("./kanban_boards")

# Create board
board = manager.create_board(
    name="Development Tasks",
    description="Sprint 1 tasks",
    columns=["Backlog", "In Progress", "Review", "Done"]
)

# Add cards
card = manager.add_card(
    board_id=board.id,
    title="Implement API",
    column="Backlog",
    priority="high",
    tags=["backend", "api"],
    assignee="John Doe"
)

# Move card
manager.move_card(board.id, card.id, "In Progress")

# Get statistics
stats = manager.get_statistics(board.id)
print(f"Total cards: {stats['total_cards']}")

# Export to JSON
json_data = manager.export_json(board.id, "board.json")
```

## File Structure

Each board is stored as a Markdown file with the following structure:

```markdown
---
id: my_board
name: My Board
description: Board description
columns:
  - To Do
  - In Progress
  - Done
created_at: '2024-01-01T00:00:00'
updated_at: '2024-01-01T00:00:00'
---

## To Do

### Task Title

---
id: task_1
title: Task Title
column: To Do
priority: high
tags:
  - tag1
  - tag2
created_at: '2024-01-01T00:00:00'
updated_at: '2024-01-01T00:00:00'
---

Task description goes here.
```

## Configuration

Create a `.env` file:

```env
KANBAN_DIR=./kanban_boards
DEFAULT_COLUMNS=待办,进行中,已完成
ENABLE_AUTO_BACKUP=true
BACKUP_DIR=./kanban_backups
```

## Card Properties

| Property | Type | Description |
|----------|------|-------------|
| id | str | Unique identifier |
| title | str | Card title |
| column | str | Current column |
| description | str | Card content |
| priority | str | low/medium/high/urgent |
| tags | list | List of tags |
| due_date | str | Due date (ISO format) |
| assignee | str | Assigned person |
| metadata | dict | Custom metadata |

## Testing

```bash
python test_main.py
```

## License

MIT
