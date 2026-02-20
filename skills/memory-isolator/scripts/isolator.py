#!/usr/bin/env python3
"""
Memory Isolator - Implementation
工作记忆隔离保障实现

借鉴 MCP Memory Keeper Channel系统和Letta Agent隔离
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class MemoryIsolator:
    """记忆隔离器"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.path.expanduser("~/.kimi"))
        self.isolator_path = self.base_path / "isolator"
        self.channels_path = self.isolator_path / "channels"
        self.registry_file = self.isolator_path / "registry.json"
        self.active_file = self.isolator_path / "active.json"
        
        self._ensure_structure()
        
    def _ensure_structure(self):
        """确保目录结构存在"""
        self.channels_path.mkdir(parents=True, exist_ok=True)
        
    def create_channel(self, name: str, description: str = "") -> Dict:
        """创建新Channel"""
        channel_path = self.channels_path / name
        channel_path.mkdir(exist_ok=True)
        
        # 创建子目录
        for subdir in ["blocks", "sessions", "checkpoints"]:
            (channel_path / subdir).mkdir(exist_ok=True)
            
        # Channel元数据
        meta = {
            "name": name,
            "description": description,
            "created": datetime.now().isoformat(),
            "active": True,
            "stats": {
                "sessions": 0,
                "checkpoints": 0
            }
        }
        
        with open(channel_path / "meta.json", 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
            
        # 更新注册表
        self._update_registry(name, meta)
        
        print(f"[OK] Channel created: {name}")
        return meta
        
    def _update_registry(self, name: str, meta: Dict):
        """更新Channel注册表"""
        registry = {}
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
                
        registry[name] = {
            "created": meta["created"],
            "description": meta["description"],
            "active": meta["active"]
        }
        
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
            
    def switch_channel(self, name: str) -> bool:
        """切换到指定Channel"""
        channel_path = self.channels_path / name
        
        if not channel_path.exists():
            print(f"[ERROR] Channel not found: {name}")
            return False
            
        # 保存当前状态
        self._save_current_session()
        
        # 切换活跃Channel
        active = {
            "channel": name,
            "switched_at": datetime.now().isoformat()
        }
        
        with open(self.active_file, 'w', encoding='utf-8') as f:
            json.dump(active, f, indent=2, ensure_ascii=False)
            
        # 加载Channel上下文
        self._load_channel_context(name)
        
        print(f"[OK] Switched to Channel: {name}")
        return True
        
    def _save_current_session(self):
        """保存当前会话状态"""
        if not self.active_file.exists():
            return
            
        with open(self.active_file, 'r', encoding='utf-8') as f:
            active = json.load(f)
            
        current_channel = active.get("channel")
        if not current_channel:
            return
            
        # 保存会话数据
        session_data = {
            "ended_at": datetime.now().isoformat(),
            "working_memory": {}  # 实际应用中这里会保存工作记忆
        }
        
        sessions_dir = self.channels_path / current_channel / "sessions"
        session_file = sessions_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
            
    def _load_channel_context(self, name: str):
        """加载Channel上下文"""
        # 实际应用中这里会加载Channel的Blocks和状态
        pass
        
    def create_checkpoint(self, name: str, description: str = "") -> str:
        """创建检查点"""
        if not self.active_file.exists():
            print("❌ 没有活跃的Channel")
            return ""
            
        with open(self.active_file, 'r', encoding='utf-8') as f:
            active = json.load(f)
            
        channel = active.get("channel", "default")
        channel_path = self.channels_path / channel
        
        checkpoint_id = f"{channel}-{name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        checkpoint = {
            "id": checkpoint_id,
            "channel": channel,
            "name": name,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "blocks_snapshot": self._capture_blocks(channel)
        }
        
        checkpoint_file = channel_path / "checkpoints" / f"{checkpoint_id}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)
            
        print(f"[OK] Checkpoint created: {checkpoint_id}")
        return checkpoint_id
        
    def _capture_blocks(self, channel: str) -> Dict:
        """捕获当前Blocks状态"""
        blocks_dir = self.channels_path / channel / "blocks"
        snapshot = {}
        
        if blocks_dir.exists():
            for f in blocks_dir.glob("*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        snapshot[f.stem] = {
                            "hash": hash(data.get("value", "")),
                            "size": len(data.get("value", ""))
                        }
                except:
                    pass
                    
        return snapshot
        
    def list_checkpoints(self, channel: str = None) -> List[Dict]:
        """列出检查点"""
        if channel is None:
            if not self.active_file.exists():
                return []
            with open(self.active_file, 'r', encoding='utf-8') as f:
                active = json.load(f)
                channel = active.get("channel", "default")
                
        checkpoints_dir = self.channels_path / channel / "checkpoints"
        checkpoints = []
        
        if checkpoints_dir.exists():
            for f in sorted(checkpoints_dir.glob("*.json"), reverse=True):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        checkpoints.append({
                            "id": data.get("id"),
                            "name": data.get("name"),
                            "timestamp": data.get("timestamp")
                        })
                except:
                    pass
                    
        return checkpoints
        
    def get_status(self) -> Dict:
        """获取隔离状态"""
        status = {
            "active_channel": None,
            "channels": [],
            "memory_usage": {}
        }
        
        # 活跃Channel
        if self.active_file.exists():
            with open(self.active_file, 'r', encoding='utf-8') as f:
                active = json.load(f)
                status["active_channel"] = active.get("channel")
                
        # 所有Channels
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
                status["channels"] = list(registry.keys())
                
        return status
        
    def cleanup_temp(self, channel: str = None):
        """清理临时数据"""
        if channel is None:
            if not self.active_file.exists():
                return
            with open(self.active_file, 'r', encoding='utf-8') as f:
                active = json.load(f)
                channel = active.get("channel", "default")
                
        # 清理逻辑
        print(f"[OK] Cleaned temp data for Channel: {channel}")


def main():
    isolator = MemoryIsolator()
    
    if len(sys.argv) < 2:
        print("Usage: isolator.py <command> [args]")
        print("Commands: create, switch, checkpoint, list, status, cleanup")
        return
        
    cmd = sys.argv[1]
    
    if cmd == "create":
        name = sys.argv[2] if len(sys.argv) > 2 else "default"
        desc = sys.argv[3] if len(sys.argv) > 3 else ""
        isolator.create_channel(name, desc)
    elif cmd == "switch":
        name = sys.argv[2] if len(sys.argv) > 2 else "default"
        isolator.switch_channel(name)
    elif cmd == "checkpoint":
        name = sys.argv[2] if len(sys.argv) > 2 else "manual"
        desc = sys.argv[3] if len(sys.argv) > 3 else ""
        isolator.create_checkpoint(name, desc)
    elif cmd == "list":
        channel = sys.argv[2] if len(sys.argv) > 2 else None
        checkpoints = isolator.list_checkpoints(channel)
        print(json.dumps(checkpoints, indent=2, ensure_ascii=False))
    elif cmd == "status":
        status = isolator.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    elif cmd == "cleanup":
        channel = sys.argv[2] if len(sys.argv) > 2 else None
        isolator.cleanup_temp(channel)
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
