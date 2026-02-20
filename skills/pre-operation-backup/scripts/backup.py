#!/usr/bin/env python3
"""
Pre-Operation Backup - 敏感操作前自动备份
在执行危险操作前创建系统快照
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class PreOperationBackup:
    """操作前备份管理器"""
    
    def __init__(self):
        self.kimi_home = Path.home() / ".kimi"
        self.backup_root = Path("D:/kimi/Backups/pre-operation")
        self.config_file = self.kimi_home / "config" / "pre-op-backup.json"
        self.log_file = self.backup_root / "operations.log"
        
        # 确保目录存在
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        # 默认配置
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置"""
        default_config = {
            "version": "1.0.0",
            "auto_protect": True,
            "default_level": "standard",
            "retention": {
                "light": {"hours": 24, "max_count": 20},
                "standard": {"days": 7, "max_count": 10},
                "full": {"days": 30, "max_count": 5}
            },
            "dangerous_keywords": [
                "delete skill", "remove skill", "rm -rf", "del /f",
                "git reset", "git clean", "git checkout --force",
                "format", "批量删除", "卸载"
            ]
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return {**default_config, **json.load(f)}
            except:
                pass
        
        return default_config
    
    def _save_config(self):
        """保存配置"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def create_snapshot(self, level: str = "standard", reason: str = "") -> str:
        """
        创建操作前快照
        
        Args:
            level: light/standard/full
            reason: 操作原因描述
        """
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        snapshot_name = f"pre-op-{timestamp}-{level}"
        if reason:
            # 清理reason中的非法字符
            clean_reason = "".join(c if c.isalnum() or c in '-_' else '-' for c in reason)[:30]
            snapshot_name += f"-{clean_reason}"
        
        snapshot_dir = self.backup_root / snapshot_name
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"[INFO] Creating {level} snapshot: {snapshot_name}")
        
        # 根据级别备份不同内容
        if level == "light":
            self._backup_light(snapshot_dir)
        elif level == "standard":
            self._backup_standard(snapshot_dir)
        else:  # full
            self._backup_full(snapshot_dir)
        
        # 保存快照信息
        snapshot_info = {
            "name": snapshot_name,
            "level": level,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "path": str(snapshot_dir)
        }
        
        with open(snapshot_dir / "snapshot-info.json", 'w', encoding='utf-8') as f:
            json.dump(snapshot_info, f, indent=2, ensure_ascii=False)
        
        # 记录日志
        self._log_operation(f"CREATED: {snapshot_name} ({level}) - {reason}")
        
        # 清理旧快照
        self._cleanup_old_snapshots(level)
        
        print(f"[OK] Snapshot created: {snapshot_dir}")
        return str(snapshot_dir)
    
    def _backup_light(self, snapshot_dir: Path):
        """轻量备份 - 仅P0关键文件"""
        print("  [LIGHT] Backing up P0 critical files...")
        
        critical_files = [
            (self.kimi_home / "config.toml", "config"),
            (self.kimi_home / "kimi.json", "config"),
            (self.kimi_home / "memory" / "hot" / "MEMORY.md", "memory"),
            (self.kimi_home / "memory" / "hot" / "IDENTITY.md", "memory"),
            (self.kimi_home / "isolator" / "active.json", "isolator"),
        ]
        
        for src, subdir in critical_files:
            if src.exists():
                dst = snapshot_dir / subdir / src.name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"    [OK] {src.name}")
    
    def _backup_standard(self, snapshot_dir: Path):
        """标准备份 - 配置 + Memory + Isolator"""
        print("  [STANDARD] Backing up config, memory, and isolator...")
        
        # 先执行light备份
        self._backup_light(snapshot_dir)
        
        # 额外备份
        additional_items = [
            (self.kimi_home / "memory" / "warm" / "blocks", "memory/blocks"),
            (self.kimi_home / "isolator", "isolator"),
            (self.kimi_home / "skills", "skills", ["SKILL.md"]),  # 只备份SKILL.md
        ]
        
        for item in additional_items:
            src = item[0]
            dst_subdir = item[1]
            patterns = item[2] if len(item) > 2 else None
            
            if src.exists():
                dst = snapshot_dir / dst_subdir
                dst.parent.mkdir(parents=True, exist_ok=True)
                
                if src.is_dir():
                    if patterns:
                        # 只备份匹配的文件
                        dst.mkdir(parents=True, exist_ok=True)
                        for pattern in patterns:
                            for f in src.rglob(pattern):
                                rel_path = f.relative_to(src)
                                dst_file = dst / rel_path
                                dst_file.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(f, dst_file)
                    else:
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
                
                print(f"    [OK] {src.name}")
    
    def _backup_full(self, snapshot_dir: Path):
        """完整备份 - 整个.kimi目录"""
        print("  [FULL] Creating full system backup...")
        
        # 要备份的目录
        backup_items = [
            "config.toml",
            "kimi.json",
            "skills",
            "scripts",
            "memory",
            "isolator",
            "rules",
            "hooks",
        ]
        
        for item in backup_items:
            src = self.kimi_home / item
            if src.exists():
                dst = snapshot_dir / item
                
                if src.is_dir():
                    # 使用robocopy风格的复制
                    self._copy_tree_with_exclude(src, dst)
                else:
                    shutil.copy2(src, dst)
                
                print(f"    [OK] {item}")
    
    def _copy_tree_with_exclude(self, src: Path, dst: Path):
        """复制目录，排除缓存文件"""
        exclude_patterns = ['__pycache__', '*.pyc', '.git', 'node_modules', 'cache', 'logs', 'temp']
        
        dst.mkdir(parents=True, exist_ok=True)
        
        for item in src.iterdir():
            # 检查是否在排除列表
            if any(pattern in str(item) for pattern in exclude_patterns):
                continue
            
            dst_item = dst / item.name
            
            if item.is_dir():
                self._copy_tree_with_exclude(item, dst_item)
            else:
                shutil.copy2(item, dst_item)
    
    def _cleanup_old_snapshots(self, level: str):
        """清理旧快照"""
        retention = self.config["retention"][level]
        max_count = retention.get("max_count", 10)
        
        # 获取该级别的所有快照
        snapshots = []
        for snapshot_dir in self.backup_root.iterdir():
            if snapshot_dir.is_dir() and f"-{level}-" in snapshot_dir.name:
                try:
                    mtime = datetime.fromtimestamp(snapshot_dir.stat().st_mtime)
                    snapshots.append((snapshot_dir, mtime))
                except:
                    pass
        
        # 按时间排序，保留最新的
        snapshots.sort(key=lambda x: x[1], reverse=True)
        
        for snapshot_dir, _ in snapshots[max_count:]:
            try:
                shutil.rmtree(snapshot_dir)
                print(f"  [CLEANUP] Removed old snapshot: {snapshot_dir.name}")
            except:
                pass
    
    def _log_operation(self, message: str):
        """记录操作日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def list_snapshots(self, level: str = None) -> List[Dict]:
        """列出所有快照"""
        snapshots = []
        
        for snapshot_dir in self.backup_root.iterdir():
            if not snapshot_dir.is_dir():
                continue
            
            info_file = snapshot_dir / "snapshot-info.json"
            if info_file.exists():
                try:
                    with open(info_file, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                        
                        if level and info.get("level") != level:
                            continue
                        
                        # 计算大小
                        size = sum(f.stat().st_size for f in snapshot_dir.rglob("*") if f.is_file())
                        info["size_mb"] = round(size / 1024 / 1024, 2)
                        
                        snapshots.append(info)
                except:
                    pass
        
        # 按时间排序
        snapshots.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return snapshots
    
    def restore_snapshot(self, snapshot_name: str = None, target_path: str = None):
        """恢复快照"""
        if not snapshot_name:
            # 使用最新的快照
            snapshots = self.list_snapshots()
            if not snapshots:
                print("[ERROR] No snapshots found")
                return False
            
            snapshot = snapshots[0]
            snapshot_name = snapshot["name"]
        
        snapshot_dir = self.backup_root / snapshot_name
        if not snapshot_dir.exists():
            print(f"[ERROR] Snapshot not found: {snapshot_name}")
            return False
        
        print(f"[INFO] Restoring snapshot: {snapshot_name}")
        
        # 先创建当前状态的快照（以防万一）
        self.create_snapshot("light", "pre-restore-safety")
        
        # 恢复文件
        restore_target = Path(target_path) if target_path else self.kimi_home
        
        for item in snapshot_dir.iterdir():
            if item.name == "snapshot-info.json":
                continue
            
            dst = restore_target / item.name
            
            if item.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(item, dst)
            else:
                shutil.copy2(item, dst)
            
            print(f"  [OK] Restored: {item.name}")
        
        self._log_operation(f"RESTORED: {snapshot_name} to {restore_target}")
        print(f"[OK] Snapshot restored: {snapshot_name}")
        return True
    
    def check_dangerous_operation(self, operation: str) -> bool:
        """检查是否为危险操作"""
        keywords = self.config.get("dangerous_keywords", [])
        
        operation_lower = operation.lower()
        for keyword in keywords:
            if keyword.lower() in operation_lower:
                return True
        
        return False
    
    def auto_protect(self, operation: str) -> Optional[str]:
        """自动保护 - 如果是危险操作则自动备份"""
        if not self.config.get("auto_protect", True):
            return None
        
        if self.check_dangerous_operation(operation):
            print(f"[WARNING] Detected dangerous operation: {operation}")
            print("[INFO] Auto-creating pre-operation snapshot...")
            
            level = self.config.get("default_level", "standard")
            snapshot_path = self.create_snapshot(level, f"auto-protect: {operation[:50]}")
            
            return snapshot_path
        
        return None


def main():
    parser = argparse.ArgumentParser(description='Pre-Operation Backup')
    subparsers = parser.add_subparsers(dest='command')
    
    # create command
    create_parser = subparsers.add_parser('create', help='Create pre-operation snapshot')
    create_parser.add_argument('--level', choices=['light', 'standard', 'full'], default='standard')
    create_parser.add_argument('--reason', default='')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List all snapshots')
    list_parser.add_argument('--level', choices=['light', 'standard', 'full'])
    
    # restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from snapshot')
    restore_parser.add_argument('--name', help='Snapshot name')
    restore_parser.add_argument('--path', help='Target restore path')
    
    # check command
    check_parser = subparsers.add_parser('check', help='Check if operation is dangerous')
    check_parser.add_argument('operation', help='Operation description')
    
    # auto-protect command
    auto_parser = subparsers.add_parser('auto-protect', help='Auto protect if dangerous')
    auto_parser.add_argument('operation', help='Operation description')
    
    # config command
    config_parser = subparsers.add_parser('config', help='Configure auto-protect')
    config_parser.add_argument('--enable', action='store_true', help='Enable auto-protect')
    config_parser.add_argument('--disable', action='store_true', help='Disable auto-protect')
    config_parser.add_argument('--level', choices=['light', 'standard', 'full'], help='Default level')
    
    args = parser.parse_args()
    
    backup = PreOperationBackup()
    
    if args.command == 'create':
        backup.create_snapshot(args.level, args.reason)
    
    elif args.command == 'list':
        snapshots = backup.list_snapshots(args.level)
        print(f"\nFound {len(snapshots)} snapshots:\n")
        print(f"{'Name':<50} {'Level':<10} {'Size':<10} {'Time':<20}")
        print("-" * 90)
        for snap in snapshots:
            name = snap['name'][:48]
            level = snap['level']
            size = f"{snap.get('size_mb', 0)}MB"
            time = snap['timestamp'][:19]
            print(f"{name:<50} {level:<10} {size:<10} {time:<20}")
    
    elif args.command == 'restore':
        backup.restore_snapshot(args.name, args.path)
    
    elif args.command == 'check':
        is_dangerous = backup.check_dangerous_operation(args.operation)
        if is_dangerous:
            print(f"[WARNING] Operation is DANGEROUS: {args.operation}")
            sys.exit(1)
        else:
            print(f"[OK] Operation is safe: {args.operation}")
            sys.exit(0)
    
    elif args.command == 'auto-protect':
        snapshot = backup.auto_protect(args.operation)
        if snapshot:
            print(f"[OK] Auto-protected: {snapshot}")
        else:
            print(f"[OK] No protection needed: {args.operation}")
    
    elif args.command == 'config':
        if args.enable:
            backup.config['auto_protect'] = True
            backup._save_config()
            print("[OK] Auto-protect enabled")
        elif args.disable:
            backup.config['auto_protect'] = False
            backup._save_config()
            print("[OK] Auto-protect disabled")
        elif args.level:
            backup.config['default_level'] = args.level
            backup._save_config()
            print(f"[OK] Default level set to: {args.level}")
        else:
            print(json.dumps(backup.config, indent=2))
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
