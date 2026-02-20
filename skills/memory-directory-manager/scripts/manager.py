#!/usr/bin/env python3
"""
Memory Directory Manager - Implementation
记忆目录架构管理实现

借鉴 OpenClaw P0/P1/P2 优先级系统和 Letta Memory Blocks
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class MemoryDirectoryManager:
    """记忆目录管理器"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.path.expanduser("~/.kimi"))
        self.memory_path = self.base_path / "memory"
        self.config_file = self.memory_path / "manager_config.json"
        self.index_file = self.memory_path / "INDEX.json"
        
    def init_architecture(self):
        """初始化三层记忆架构"""
        dirs = [
            "memory/hot",           # P0/P1 Hot Memory
            "memory/warm/blocks",   # Letta-style Blocks
            "memory/warm/lessons",  # Structured lessons
            "memory/warm/projects", # Project memories
            "memory/cold/archive",  # Archived content
            "memory/logs",          # Operation logs
        ]
        
        for d in dirs:
            (self.base_path / d).mkdir(parents=True, exist_ok=True)
            
        # 创建默认配置文件
        self._create_default_config()
        
        # 创建默认Blocks
        self._create_default_blocks()
        
        # 创建示例 MEMORY.md
        self._create_memory_template()
        
        print("[OK] Memory architecture initialized")
        print(f"     Location: {self.memory_path}")
        
    def _create_default_config(self):
        """创建默认配置"""
        config = {
            "version": "1.0.0",
            "ttl": {
                "p1_days": 90,
                "p2_days": 30
            },
            "limits": {
                "hot_memory_lines": 200,
                "hot_memory_tokens": 2000,
                "block_size_chars": 5000
            },
            "auto_archive": {
                "enabled": True,
                "schedule": "0 4 * * *"
            }
        }
        
        if not self.config_file.exists():
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
    def _create_default_blocks(self):
        """创建默认Memory Blocks"""
        blocks = {
            "human": {
                "label": "human",
                "description": "用户信息、偏好和历史",
                "value": "用户: wang-\n语言偏好: 中文\n专业领域: AI Agent开发",
                "limit": 5000,
                "readonly": False
            },
            "persona": {
                "label": "persona", 
                "description": "AI代理的人格和行为准则",
                "value": "角色: KbotGenesis\n风格: 专业、高效、友好\n专长: 加密交易、记忆管理",
                "limit": 5000,
                "readonly": False
            },
            "knowledge": {
                "label": "knowledge",
                "description": "领域知识库",
                "value": "项目: KbotGenesis_Zero2Alpha_AutoVault\n架构: 三层记忆系统\n技术栈: Python, Kimi CLI",
                "limit": 10000,
                "readonly": False
            }
        }
        
        blocks_dir = self.memory_path / "warm" / "blocks"
        for name, block in blocks.items():
            block_file = blocks_dir / f"{name}.json"
            if not block_file.exists():
                block["last_modified"] = datetime.now().isoformat()
                with open(block_file, 'w', encoding='utf-8') as f:
                    json.dump(block, f, indent=2, ensure_ascii=False)
                    
    def _create_memory_template(self):
        """创建MEMORY.md模板"""
        template = """# MEMORY - KbotGenesis

## [P0] Core Identity (永不过期)
- [P0] 用户偏好中文交流
- [P0] 项目名称: KbotGenesis_Zero2Alpha_AutoVault
- [P0] 安全规则: 交易前必须确认

## [P1] Active Projects (90天TTL)
- [P1][2026-02-19] 记忆管理系统部署完成
- [P1][2026-02-19] 三层记忆架构初始化

## [P2] Temporary Notes (30天TTL)
- [P2][2026-02-19] 创建Memory Blocks模板
"""
        memory_file = self.memory_path / "hot" / "MEMORY.md"
        if not memory_file.exists():
            with open(memory_file, 'w', encoding='utf-8') as f:
                f.write(template)
                
    def analyze_health(self) -> Dict:
        """分析目录健康状况"""
        result = {
            "status": "healthy",
            "issues": [],
            "stats": {}
        }
        
        # 检查目录存在
        for d in ["hot", "warm", "cold"]:
            path = self.memory_path / d
            if not path.exists():
                result["issues"].append(f"缺失目录: {d}")
                result["status"] = "warning"
                
        # 统计大小
        total_size = 0
        for root, dirs, files in os.walk(self.memory_path):
            for f in files:
                fp = Path(root) / f
                total_size += fp.stat().st_size
                
        result["stats"]["total_size_kb"] = total_size // 1024
        
        # 检查重复
        duplicates = self._find_duplicates()
        if duplicates:
            result["issues"].append(f"发现 {len(duplicates)} 个潜在重复文件")
            
        return result
        
    def _find_duplicates(self) -> List:
        """查找重复文件"""
        # 简化实现
        return []
        
    def archive_expired(self, dry_run: bool = True):
        """归档过期内容"""
        now = datetime.now()
        moved = []
        
        # 扫描P2临时文件 (>30天)
        lessons_dir = self.memory_path / "warm" / "lessons"
        if lessons_dir.exists():
            for f in lessons_dir.glob("*.jsonl"):
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if (now - mtime).days > 30:
                    if not dry_run:
                        target = self.memory_path / "cold" / "archive" / f.name
                        f.rename(target)
                    moved.append(f.name)
                    
        action = "Will archive" if dry_run else "Archived"
        print(f"[Archive] {action} {len(moved)} expired files")
        for m in moved[:5]:
            print(f"   - {m}")
            
        return moved
        
    def update_index(self):
        """更新索引"""
        index = {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "architecture": "three-layer",
            "stats": self._calculate_stats(),
            "blocks": self._list_blocks()
        }
        
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
            
        print(f"[OK] Index updated: {self.index_file}")
        
    def _calculate_stats(self) -> Dict:
        """计算统计信息"""
        stats = {"hot_kb": 0, "warm_kb": 0, "cold_kb": 0}
        
        for tier in ["hot", "warm", "cold"]:
            tier_path = self.memory_path / tier
            if tier_path.exists():
                size = sum(f.stat().st_size for f in tier_path.rglob("*") if f.is_file())
                stats[f"{tier}_kb"] = size // 1024
                
        return stats
        
    def _list_blocks(self) -> Dict:
        """列出所有Blocks"""
        blocks = {}
        blocks_dir = self.memory_path / "warm" / "blocks"
        
        if blocks_dir.exists():
            for f in blocks_dir.glob("*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        blocks[f.stem] = {
                            "size": len(data.get("value", "")),
                            "last_modified": data.get("last_modified", "unknown")
                        }
                except:
                    pass
                    
        return blocks


def main():
    manager = MemoryDirectoryManager()
    
    if len(sys.argv) < 2:
        print("Usage: manager.py <command>")
        print("Commands: init, health, archive, index")
        return
        
    cmd = sys.argv[1]
    
    if cmd == "init":
        manager.init_architecture()
    elif cmd == "health":
        result = manager.analyze_health()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif cmd == "archive":
        dry_run = "--dry-run" in sys.argv
        manager.archive_expired(dry_run=dry_run)
    elif cmd == "index":
        manager.update_index()
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
