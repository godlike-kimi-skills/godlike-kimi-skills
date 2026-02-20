# Kanban Skill - Markdown看板管理工具

基于Markdown文件的看板管理工具，支持YAML frontmatter元数据，纯文件系统存储，无需数据库。

## 功能特性

- 📝 **纯Markdown存储** - 所有看板和卡片以 `.md` 文件形式存储
- 🏷️ **YAML Frontmatter** - 支持丰富的卡片元数据
- 📊 **多列看板** - 可自定义看板列
- 🔍 **统计报告** - 追踪卡片分布和进度
- 💾 **JSON导出** - 支持导出为JSON格式
- 🔒 **自动备份** - 内置备份功能
- 🌐 **多语言支持** - 完整支持Unicode/中文

## 安装依赖

```bash
pip install -r requirements.txt
```

依赖列表：
- pyyaml >= 6.0
- markdown >= 3.5.0
- python-dateutil >= 2.8.2

## 快速开始

### 1. 创建看板

```bash
python main.py create "我的项目看板" --desc "项目任务管理" --columns 待办 进行中 已完成
```

### 2. 添加卡片

```bash
python main.py add my_project_board "设计首页" --priority high --tags 前端,紧急 --due 2024-12-31
```

### 3. 查看所有看板

```bash
python main.py list
```

### 4. 移动卡片

```bash
python main.py move my_project_board card_0 进行中
```

### 5. 查看统计

```bash
python main.py stats my_project_board
```

## 编程使用

```python
from main import KanbanManager

# 初始化管理器
manager = KanbanManager("./kanban_boards")

# 创建看板
board = manager.create_board(
    name="开发任务",
    description="Sprint 1 任务",
    columns=["待办", "进行中", "审核中", "已完成"]
)

# 添加卡片
card = manager.add_card(
    board_id=board.id,
    title="实现API接口",
    column="待办",
    priority="high",
    tags=["后端", "API"],
    assignee="张三"
)

# 移动卡片
manager.move_card(board.id, card.id, "进行中")

# 获取统计
stats = manager.get_statistics(board.id)
print(f"总卡片数: {stats['total_cards']}")

# 导出JSON
json_data = manager.export_json(board.id, "board.json")
```

## 文件结构

每个看板存储为一个Markdown文件，结构如下：

```markdown
---
id: my_board
name: 我的看板
description: 看板描述
columns:
  - 待办
  - 进行中
  - 已完成
created_at: '2024-01-01T00:00:00'
updated_at: '2024-01-01T00:00:00'
---

看板描述内容...

## 待办

### 任务标题

---
id: task_1
title: 任务标题
column: 待办
priority: high
tags:
  - 标签1
  - 标签2
created_at: '2024-01-01T00:00:00'
updated_at: '2024-01-01T00:00:00'
---

任务描述内容...
```

## 卡片属性

| 属性 | 类型 | 描述 |
|------|------|------|
| id | 字符串 | 唯一标识符 |
| title | 字符串 | 卡片标题 |
| column | 字符串 | 当前所在列 |
| description | 字符串 | 卡片内容 |
| priority | 字符串 | 优先级: low/medium/high/urgent |
| tags | 列表 | 标签列表 |
| due_date | 字符串 | 截止日期 (ISO格式) |
| assignee | 字符串 | 负责人 |
| metadata | 字典 | 自定义元数据 |

## 命令行参考

### create - 创建看板
```bash
python main.py create "看板名称" --desc "描述" --columns 列1 列2 列3
```

### list - 列出看板
```bash
python main.py list
```

### add - 添加卡片
```bash
python main.py add 看板ID "卡片标题" --column 列名 --priority high --tags 标签1,标签2 --due 2024-12-31
```

参数说明：
- `--column`: 目标列（默认第一列）
- `--priority`: 优先级 (low/medium/high/urgent)
- `--tags`: 标签列表（空格分隔）
- `--due`: 截止日期

### move - 移动卡片
```bash
python main.py move 看板ID 卡片ID 目标列
```

### stats - 查看统计
```bash
python main.py stats 看板ID
```

### export - 导出看板
```bash
python main.py export 看板ID --output board.json
```

## 配置

创建 `.env` 文件：

```env
KANBAN_DIR=./kanban_boards
DEFAULT_COLUMNS=待办,进行中,已完成
ENABLE_AUTO_BACKUP=true
BACKUP_DIR=./kanban_backups
DATE_FORMAT=%Y-%m-%d
```

## API参考

### KanbanManager

#### 构造函数
```python
manager = KanbanManager(base_dir="./kanban_boards")
```

#### 方法

| 方法 | 描述 |
|------|------|
| `create_board(name, description, columns)` | 创建新看板 |
| `get_board(board_id)` | 获取看板 |
| `save_board(board)` | 保存看板 |
| `delete_board(board_id)` | 删除看板 |
| `list_boards()` | 列出所有看板 |
| `add_card(board_id, title, ...)` | 添加卡片 |
| `move_card(board_id, card_id, column)` | 移动卡片 |
| `delete_card(board_id, card_id)` | 删除卡片 |
| `get_statistics(board_id)` | 获取统计 |
| `export_json(board_id, output_path)` | 导出JSON |
| `backup(backup_dir)` | 备份所有看板 |

## 测试

```bash
python test_main.py
```

测试覆盖率：
- 看板CRUD操作
- 卡片CRUD操作
- 移动和统计功能
- Markdown解析和生成
- 备份功能

## 使用场景

1. **个人任务管理** - 追踪日常待办事项
2. **项目管理** - 团队协作和进度追踪
3. **内容创作** - 管理文章/视频制作流程
4. **学习计划** - 追踪学习进度

## 扩展开发

可通过继承 `KanbanManager` 类来扩展功能：

```python
class AdvancedKanbanManager(KanbanManager):
    def filter_cards(self, board_id, tag=None, priority=None):
        """按标签或优先级筛选卡片"""
        board = self.get_board(board_id)
        cards = board.cards
        
        if tag:
            cards = [c for c in cards if tag in c.tags]
        if priority:
            cards = [c for c in cards if c.priority == priority]
        
        return cards
```

## 许可证

MIT License
