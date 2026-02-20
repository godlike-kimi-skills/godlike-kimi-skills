#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kanban Skill - 基于Markdown的看板管理工具
支持YAML frontmatter，纯文件系统存储，无需数据库
"""

import os
import re
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import yaml


@dataclass
class KanbanCard:
    """看板卡片数据类"""
    id: str
    title: str
    column: str
    description: str = ""
    priority: str = "medium"  # low, medium, high, urgent
    tags: List[str] = None
    due_date: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    assignee: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


@dataclass
class KanbanBoard:
    """看板数据类"""
    id: str
    name: str
    description: str = ""
    columns: List[str] = None
    cards: List[KanbanCard] = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if self.columns is None:
            self.columns = ["待办", "进行中", "已完成"]
        if self.cards is None:
            self.cards = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


class KanbanManager:
    """看板管理器"""
    
    def __init__(self, base_dir: str = "./kanban_boards"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _sanitize_filename(self, name: str) -> str:
        """清理文件名"""
        return re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
    
    def _get_board_path(self, board_id: str) -> Path:
        """获取看板文件路径"""
        return self.base_dir / f"{board_id}.md"
    
    def _card_to_markdown(self, card: KanbanCard) -> str:
        """将卡片转换为Markdown格式"""
        lines = ["---"]
        
        # YAML frontmatter
        frontmatter = {
            "id": card.id,
            "title": card.title,
            "column": card.column,
            "priority": card.priority,
            "tags": card.tags,
            "due_date": card.due_date,
            "created_at": card.created_at,
            "updated_at": card.updated_at,
            "assignee": card.assignee,
        }
        lines.append(yaml.dump(frontmatter, allow_unicode=True, sort_keys=False))
        lines.append("---")
        
        # 卡片内容
        if card.description:
            lines.append(f"\n{card.description}\n")
        
        # 元数据
        if card.metadata:
            lines.append("\n<!-- metadata -->")
            lines.append(f"```json\n{json.dumps(card.metadata, ensure_ascii=False, indent=2)}\n```")
        
        return "\n".join(lines)
    
    def _parse_card_markdown(self, content: str, column: str) -> KanbanCard:
        """解析Markdown格式的卡片"""
        # 提取YAML frontmatter
        yaml_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        
        if yaml_match:
            try:
                frontmatter = yaml.safe_load(yaml_match.group(1))
                body = yaml_match.group(2).strip()
            except yaml.YAMLError:
                frontmatter = {}
                body = content
        else:
            frontmatter = {}
            body = content
        
        # 提取元数据
        metadata_match = re.search(r'<!-- metadata -->\s*```json\n(.*?)\n```', body, re.DOTALL)
        metadata = {}
        if metadata_match:
            try:
                metadata = json.loads(metadata_match.group(1))
                body = re.sub(r'\s*<!-- metadata -->.*', '', body, flags=re.DOTALL).strip()
            except json.JSONDecodeError:
                pass
        
        return KanbanCard(
            id=frontmatter.get("id", ""),
            title=frontmatter.get("title", "Untitled"),
            column=column,
            description=body,
            priority=frontmatter.get("priority", "medium"),
            tags=frontmatter.get("tags", []),
            due_date=frontmatter.get("due_date"),
            created_at=frontmatter.get("created_at", ""),
            updated_at=frontmatter.get("updated_at", ""),
            assignee=frontmatter.get("assignee", ""),
            metadata=metadata
        )
    
    def board_to_markdown(self, board: KanbanBoard) -> str:
        """将看板转换为Markdown格式"""
        lines = ["---"]
        
        # 看板YAML frontmatter
        frontmatter = {
            "id": board.id,
            "name": board.name,
            "description": board.description,
            "columns": board.columns,
            "created_at": board.created_at,
            "updated_at": board.updated_at,
        }
        lines.append(yaml.dump(frontmatter, allow_unicode=True, sort_keys=False))
        lines.append("---")
        
        # 看板描述
        if board.description:
            lines.append(f"\n{board.description}\n")
        
        # 各列的卡片
        for column in board.columns:
            lines.append(f"\n## {column}\n")
            column_cards = [c for c in board.cards if c.column == column]
            for card in column_cards:
                lines.append(f"\n### {card.title}\n")
                lines.append(self._card_to_markdown(card))
                lines.append("\n---\n")
        
        return "\n".join(lines)
    
    def parse_board_markdown(self, content: str, board_id: str) -> KanbanBoard:
        """解析Markdown格式的看板"""
        # 提取看板YAML frontmatter
        yaml_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        
        if yaml_match:
            try:
                frontmatter = yaml.safe_load(yaml_match.group(1))
                body = yaml_match.group(2)
            except yaml.YAMLError:
                frontmatter = {}
                body = content
        else:
            frontmatter = {}
            body = content
        
        columns = frontmatter.get("columns", ["待办", "进行中", "已完成"])
        
        # 解析卡片
        cards = []
        current_column = columns[0] if columns else "待办"
        
        lines = body.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # 检测列标题
            column_match = re.match(r'^##\s+(.+)$', line)
            if column_match:
                current_column = column_match.group(1).strip()
                i += 1
                continue
            
            # 检测卡片标题
            card_match = re.match(r'^###\s+(.+)$', line)
            if card_match:
                card_title = card_match.group(1).strip()
                card_lines = []
                i += 1
                
                # 收集卡片内容直到下一个卡片或列
                while i < len(lines):
                    next_line = lines[i]
                    if re.match(r'^(###|##)\s+', next_line) or next_line.strip() == '---':
                        if next_line.strip() == '---':
                            i += 1
                        break
                    card_lines.append(next_line)
                    i += 1
                
                card_content = '\n'.join(card_lines).strip()
                if card_content:
                    card = self._parse_card_markdown(card_content, current_column)
                    if not card.id:
                        card.id = f"card_{len(cards)}"
                    if not card.title:
                        card.title = card_title
                    cards.append(card)
                continue
            
            i += 1
        
        return KanbanBoard(
            id=frontmatter.get("id", board_id),
            name=frontmatter.get("name", "Untitled Board"),
            description=frontmatter.get("description", ""),
            columns=columns,
            cards=cards,
            created_at=frontmatter.get("created_at", ""),
            updated_at=frontmatter.get("updated_at", "")
        )
    
    def create_board(self, name: str, description: str = "", columns: List[str] = None) -> KanbanBoard:
        """创建新看板"""
        board_id = self._sanitize_filename(name)
        board = KanbanBoard(
            id=board_id,
            name=name,
            description=description,
            columns=columns or ["待办", "进行中", "已完成"]
        )
        self.save_board(board)
        return board
    
    def get_board(self, board_id: str) -> Optional[KanbanBoard]:
        """获取看板"""
        board_path = self._get_board_path(board_id)
        if not board_path.exists():
            return None
        
        content = board_path.read_text(encoding='utf-8')
        return self.parse_board_markdown(content, board_id)
    
    def save_board(self, board: KanbanBoard) -> None:
        """保存看板"""
        board.updated_at = datetime.now().isoformat()
        content = self.board_to_markdown(board)
        board_path = self._get_board_path(board.id)
        board_path.write_text(content, encoding='utf-8')
    
    def delete_board(self, board_id: str) -> bool:
        """删除看板"""
        board_path = self._get_board_path(board_id)
        if board_path.exists():
            board_path.unlink()
            return True
        return False
    
    def list_boards(self) -> List[Dict[str, str]]:
        """列出所有看板"""
        boards = []
        for md_file in self.base_dir.glob("*.md"):
            board_id = md_file.stem
            board = self.get_board(board_id)
            if board:
                boards.append({
                    "id": board.id,
                    "name": board.name,
                    "card_count": len(board.cards),
                    "updated_at": board.updated_at
                })
        return boards
    
    def add_card(self, board_id: str, title: str, column: str = None, **kwargs) -> Optional[KanbanCard]:
        """添加卡片"""
        board = self.get_board(board_id)
        if not board:
            return None
        
        target_column = column or board.columns[0]
        if target_column not in board.columns:
            board.columns.append(target_column)
        
        card = KanbanCard(
            id=f"{board_id}_card_{len(board.cards)}",
            title=title,
            column=target_column,
            **kwargs
        )
        board.cards.append(card)
        self.save_board(board)
        return card
    
    def move_card(self, board_id: str, card_id: str, target_column: str) -> bool:
        """移动卡片"""
        board = self.get_board(board_id)
        if not board:
            return False
        
        if target_column not in board.columns:
            return False
        
        for card in board.cards:
            if card.id == card_id:
                card.column = target_column
                card.updated_at = datetime.now().isoformat()
                self.save_board(board)
                return True
        return False
    
    def delete_card(self, board_id: str, card_id: str) -> bool:
        """删除卡片"""
        board = self.get_board(board_id)
        if not board:
            return False
        
        for i, card in enumerate(board.cards):
            if card.id == card_id:
                board.cards.pop(i)
                self.save_board(board)
                return True
        return False
    
    def get_statistics(self, board_id: str) -> Dict[str, Any]:
        """获取看板统计信息"""
        board = self.get_board(board_id)
        if not board:
            return {}
        
        stats = {
            "total_cards": len(board.cards),
            "by_column": {},
            "by_priority": {},
            "overdue": 0
        }
        
        now = datetime.now()
        
        for card in board.cards:
            # 按列统计
            stats["by_column"][card.column] = stats["by_column"].get(card.column, 0) + 1
            
            # 按优先级统计
            stats["by_priority"][card.priority] = stats["by_priority"].get(card.priority, 0) + 1
            
            # 检查逾期
            if card.due_date:
                try:
                    due = datetime.fromisoformat(card.due_date.replace('Z', '+00:00'))
                    if due < now:
                        stats["overdue"] += 1
                except:
                    pass
        
        return stats
    
    def export_json(self, board_id: str, output_path: str = None) -> str:
        """导出为JSON格式"""
        board = self.get_board(board_id)
        if not board:
            raise ValueError(f"Board {board_id} not found")
        
        data = asdict(board)
        
        if output_path:
            Path(output_path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def backup(self, backup_dir: str = "./kanban_backups") -> str:
        """备份所有看板"""
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"kanban_backup_{timestamp}"
        backup_subdir = backup_path / backup_name
        backup_subdir.mkdir(exist_ok=True)
        
        for md_file in self.base_dir.glob("*.md"):
            shutil.copy2(md_file, backup_subdir / md_file.name)
        
        return str(backup_subdir)


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Kanban Skill - Markdown-based Kanban Board")
    parser.add_argument("--dir", default="./kanban_boards", help="看板存储目录")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 创建看板
    create_parser = subparsers.add_parser("create", help="创建新看板")
    create_parser.add_argument("name", help="看板名称")
    create_parser.add_argument("--desc", default="", help="看板描述")
    create_parser.add_argument("--columns", nargs="+", default=["待办", "进行中", "已完成"], help="列名")
    
    # 列出看板
    subparsers.add_parser("list", help="列出所有看板")
    
    # 添加卡片
    add_parser = subparsers.add_parser("add", help="添加卡片")
    add_parser.add_argument("board_id", help="看板ID")
    add_parser.add_argument("title", help="卡片标题")
    add_parser.add_argument("--column", help="目标列")
    add_parser.add_argument("--priority", default="medium", choices=["low", "medium", "high", "urgent"])
    add_parser.add_argument("--tags", nargs="+", help="标签")
    add_parser.add_argument("--due", help="截止日期 (YYYY-MM-DD)")
    
    # 移动卡片
    move_parser = subparsers.add_parser("move", help="移动卡片")
    move_parser.add_argument("board_id", help="看板ID")
    move_parser.add_argument("card_id", help="卡片ID")
    move_parser.add_argument("column", help="目标列")
    
    # 统计
    stats_parser = subparsers.add_parser("stats", help="查看统计")
    stats_parser.add_argument("board_id", help="看板ID")
    
    # 导出
    export_parser = subparsers.add_parser("export", help="导出看板")
    export_parser.add_argument("board_id", help="看板ID")
    export_parser.add_argument("--output", help="输出文件路径")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = KanbanManager(args.dir)
    
    if args.command == "create":
        board = manager.create_board(args.name, args.desc, args.columns)
        print(f"✓ 看板已创建: {board.name} (ID: {board.id})")
    
    elif args.command == "list":
        boards = manager.list_boards()
        if not boards:
            print("暂无看板")
        else:
            print(f"{'ID':<20} {'名称':<30} {'卡片数':<10} {'更新时间'}")
            print("-" * 70)
            for b in boards:
                print(f"{b['id']:<20} {b['name']:<30} {b['card_count']:<10} {b['updated_at'][:19]}")
    
    elif args.command == "add":
        card = manager.add_card(
            args.board_id, args.title, args.column,
            priority=args.priority, tags=args.tags or [], due_date=args.due
        )
        if card:
            print(f"✓ 卡片已添加: {card.title} (ID: {card.id})")
        else:
            print(f"✗ 看板不存在: {args.board_id}")
    
    elif args.command == "move":
        if manager.move_card(args.board_id, args.card_id, args.column):
            print(f"✓ 卡片已移动到: {args.column}")
        else:
            print(f"✗ 移动失败")
    
    elif args.command == "stats":
        stats = manager.get_statistics(args.board_id)
        if not stats:
            print(f"✗ 看板不存在: {args.board_id}")
        else:
            print(f"\n看板统计: {args.board_id}")
            print(f"总卡片数: {stats['total_cards']}")
            print(f"逾期卡片: {stats['overdue']}")
            print("\n按列分布:")
            for col, count in stats['by_column'].items():
                print(f"  {col}: {count}")
            print("\n按优先级分布:")
            for pri, count in stats['by_priority'].items():
                print(f"  {pri}: {count}")
    
    elif args.command == "export":
        try:
            json_str = manager.export_json(args.board_id, args.output)
            if args.output:
                print(f"✓ 已导出到: {args.output}")
            else:
                print(json_str)
        except ValueError as e:
            print(f"✗ {e}")


if __name__ == "__main__":
    main()
