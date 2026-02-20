#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kanban Skill 测试文件
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
import unittest

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import KanbanManager, KanbanBoard, KanbanCard


class TestKanbanManager(unittest.TestCase):
    """看板管理器测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试前准备"""
        cls.test_dir = tempfile.mkdtemp()
        cls.manager = KanbanManager(base_dir=cls.test_dir)
    
    @classmethod
    def tearDownClass(cls):
        """测试后清理"""
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    def test_create_board(self):
        """测试创建看板"""
        board = self.manager.create_board(
            name="测试看板",
            description="这是一个测试看板",
            columns=["待办", "进行中", "已完成"]
        )
        
        self.assertEqual(board.name, "测试看板")
        self.assertEqual(board.description, "这是一个测试看板")
        self.assertEqual(len(board.columns), 3)
        self.assertIn("待办", board.columns)
    
    def test_get_board(self):
        """测试获取看板"""
        # 创建看板
        created = self.manager.create_board(name="获取测试")
        
        # 获取看板
        fetched = self.manager.get_board(created.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, "获取测试")
        
        # 获取不存在的看板
        not_found = self.manager.get_board("non_existent")
        self.assertIsNone(not_found)
    
    def test_add_card(self):
        """测试添加卡片"""
        board = self.manager.create_board(name="卡片测试")
        
        # 添加卡片
        card = self.manager.add_card(
            board_id=board.id,
            title="测试卡片",
            priority="high",
            tags=["重要", "紧急"],
            due_date="2024-12-31"
        )
        
        self.assertIsNotNone(card)
        self.assertEqual(card.title, "测试卡片")
        self.assertEqual(card.priority, "high")
        self.assertEqual(len(card.tags), 2)
        self.assertEqual(card.column, "待办")  # 默认列
        
        # 验证看板中的卡片
        updated_board = self.manager.get_board(board.id)
        self.assertEqual(len(updated_board.cards), 1)
    
    def test_move_card(self):
        """测试移动卡片"""
        board = self.manager.create_board(name="移动测试")
        card = self.manager.add_card(board_id=board.id, title="移动卡片")
        
        # 移动卡片
        success = self.manager.move_card(board.id, card.id, "进行中")
        self.assertTrue(success)
        
        # 验证位置
        updated_board = self.manager.get_board(board.id)
        updated_card = updated_board.cards[0]
        self.assertEqual(updated_card.column, "进行中")
        
        # 移动到不存在的列
        fail = self.manager.move_card(board.id, card.id, "不存在")
        self.assertFalse(fail)
    
    def test_delete_card(self):
        """测试删除卡片"""
        board = self.manager.create_board(name="删除测试")
        card = self.manager.add_card(board_id=board.id, title="删除卡片")
        
        # 删除卡片
        success = self.manager.delete_card(board.id, card.id)
        self.assertTrue(success)
        
        # 验证删除
        updated_board = self.manager.get_board(board.id)
        self.assertEqual(len(updated_board.cards), 0)
    
    def test_delete_board(self):
        """测试删除看板"""
        board = self.manager.create_board(name="删除看板测试")
        
        # 删除看板
        success = self.manager.delete_board(board.id)
        self.assertTrue(success)
        
        # 验证删除
        not_found = self.manager.get_board(board.id)
        self.assertIsNone(not_found)
    
    def test_list_boards(self):
        """测试列出看板"""
        # 创建几个看板
        self.manager.create_board(name="列表测试1")
        self.manager.create_board(name="列表测试2")
        
        # 列出看板
        boards = self.manager.list_boards()
        self.assertIsInstance(boards, list)
        self.assertTrue(len(boards) >= 2)
        
        # 验证字段
        for b in boards:
            self.assertIn("id", b)
            self.assertIn("name", b)
            self.assertIn("card_count", b)
    
    def test_get_statistics(self):
        """测试统计功能"""
        board = self.manager.create_board(name="统计测试")
        
        # 添加不同优先级的卡片
        self.manager.add_card(board.id, "卡片1", priority="high")
        self.manager.add_card(board.id, "卡片2", priority="medium")
        self.manager.add_card(board.id, "卡片3", priority="low")
        
        # 移动一张卡片
        board_with_cards = self.manager.get_board(board.id)
        self.manager.move_card(board.id, board_with_cards.cards[0].id, "已完成")
        
        # 获取统计
        stats = self.manager.get_statistics(board.id)
        self.assertEqual(stats["total_cards"], 3)
        self.assertEqual(stats["by_priority"]["high"], 1)
        self.assertEqual(stats["by_priority"]["medium"], 1)
        self.assertEqual(stats["by_priority"]["low"], 1)
        self.assertEqual(stats["by_column"]["待办"], 2)
        self.assertEqual(stats["by_column"]["已完成"], 1)
    
    def test_export_json(self):
        """测试导出JSON"""
        board = self.manager.create_board(name="导出测试", description="测试导出")
        self.manager.add_card(board.id, "导出卡片")
        
        # 导出
        json_str = self.manager.export_json(board.id)
        data = json.loads(json_str)
        
        self.assertEqual(data["name"], "导出测试")
        self.assertEqual(data["description"], "测试导出")
        self.assertEqual(len(data["cards"]), 1)
    
    def test_board_to_markdown(self):
        """测试看板转Markdown"""
        board = KanbanBoard(
            id="test_md",
            name="Markdown测试",
            columns=["待办", "进行中"],
            cards=[
                KanbanCard(
                    id="c1",
                    title="卡片1",
                    column="待办",
                    priority="high",
                    tags=["标签1"]
                )
            ]
        )
        
        markdown = self.manager.board_to_markdown(board)
        
        # 验证包含关键内容
        self.assertIn("Markdown测试", markdown)
        self.assertIn("待办", markdown)
        self.assertIn("卡片1", markdown)
        self.assertIn("high", markdown)
        self.assertIn("标签1", markdown)
    
    def test_backup(self):
        """测试备份功能"""
        # 创建一些看板
        self.manager.create_board(name="备份测试1")
        self.manager.create_board(name="备份测试2")
        
        # 备份
        backup_path = self.manager.backup(backup_dir=os.path.join(self.test_dir, "backups"))
        
        # 验证备份目录存在
        self.assertTrue(os.path.exists(backup_path))
        
        # 验证备份文件
        backup_files = list(Path(backup_path).glob("*.md"))
        self.assertTrue(len(backup_files) >= 2)


class TestKanbanCard(unittest.TestCase):
    """看板卡片测试类"""
    
    def test_card_defaults(self):
        """测试卡片默认值"""
        card = KanbanCard(id="c1", title="测试", column="待办")
        
        self.assertEqual(card.priority, "medium")
        self.assertEqual(card.tags, [])
        self.assertEqual(card.metadata, {})
        self.assertIsNotNone(card.created_at)
    
    def test_card_with_data(self):
        """测试带数据的卡片"""
        card = KanbanCard(
            id="c2",
            title="完整卡片",
            column="进行中",
            description="描述内容",
            priority="urgent",
            tags=["重要", "紧急"],
            assignee="张三",
            metadata={"source": "test"}
        )
        
        self.assertEqual(card.description, "描述内容")
        self.assertEqual(card.priority, "urgent")
        self.assertEqual(len(card.tags), 2)
        self.assertEqual(card.assignee, "张三")
        self.assertEqual(card.metadata["source"], "test")


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestKanbanManager))
    suite.addTests(loader.loadTestsFromTestCase(TestKanbanCard))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
