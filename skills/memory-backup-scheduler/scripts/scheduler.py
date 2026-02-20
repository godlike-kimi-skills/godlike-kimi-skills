#!/usr/bin/env python3
"""
Memory Backup Scheduler - Implementation
工作记忆备份调度实现

借鉴 Claude Code层叠配置和OpenClaw自动归档
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class MemoryBackupScheduler:
    """记忆备份调度器"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.path.expanduser("~/.kimi"))
        self.backup_root = Path("D:/kimi/Backups")
        self.config_file = self.base_path / "backup_config.json"
        
    def init_scheduler(self):
        """初始化调度器"""
        # 创建备份目录结构
        dirs = [
            "hot",          # 实时备份
            "incremental",  # 增量备份
            "full",         # 完整备份
            "archive",      # 归档
            "logs"          # 日志
        ]
        
        for d in dirs:
            (self.backup_root / d).mkdir(parents=True, exist_ok=True)
            
        # 创建默认配置
        self._create_default_config()
        
        print("[OK] Backup scheduler initialized")
        print(f"     Backup root: {self.backup_root}")
        
    def _create_default_config(self):
        """创建默认配置"""
        config = {
            "version": "1.0.0",
            "enabled": True,
            "schedules": [
                {
                    "name": "hourly_incremental",
                    "cron": "0 * * * *",
                    "type": "incremental",
                    "targets": ["local"],
                    "priority": "P1"
                },
                {
                    "name": "daily_backup",
                    "cron": "0 3 * * *",
                    "type": "incremental",
                    "targets": ["local", "github"],
                    "priority": "P0+P1"
                }
            ],
            "retention": {
                "hot": {"count": 10},
                "incremental": {"days": 7},
                "full": {"weeks": 4}
            },
            "sources": {
                "P0": [
                    "memory/hot/MEMORY.md",
                    "memory/hot/IDENTITY.md",
                    "config.toml"
                ],
                "P1": [
                    "skills/*/SKILL.md",
                    "memory/warm/blocks/*.json",
                    "isolator/channels/*"
                ]
            },
            "github": {
                "repo": "wangjohnny9955/Kbot-backup",
                "branch": "main",
                "auto_push": True
            }
        }
        
        if not self.config_file.exists():
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
    def backup(self, backup_type: str = "incremental", priority: str = "P1") -> str:
        """执行备份"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        backup_name = f"{backup_type}-{timestamp}"
        backup_dir = self.backup_root / backup_type / backup_name
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 备份P0内容
        if priority in ["P0", "P0+P1", "all"]:
            self._backup_p0(backup_dir)
            
        # 备份P1内容
        if priority in ["P1", "P0+P1", "all"]:
            self._backup_p1(backup_dir)
            
        # 创建备份报告
        report = {
            "backup_id": backup_name,
            "type": backup_type,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "source": str(self.base_path),
            "destination": str(backup_dir)
        }
        
        with open(backup_dir / "backup_report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        # 更新latest链接
        latest_link = self.backup_root / backup_type / "latest"
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
            
        try:
            latest_link.symlink_to(backup_dir, target_is_directory=True)
        except:
            pass  # Windows可能需要管理员权限
            
        print(f"[OK] Backup completed: {backup_name}")
        return str(backup_dir)
        
    def _backup_p0(self, backup_dir: Path):
        """备份P0关键内容"""
        p0_dir = backup_dir / "P0"
        p0_dir.mkdir(exist_ok=True)
        
        sources = [
            "memory/hot/MEMORY.md",
            "memory/hot/IDENTITY.md", 
            "config.toml",
            "kimi.json"
        ]
        
        for src in sources:
            src_path = self.base_path / src
            if src_path.exists():
                dst = p0_dir / src.replace("/", "_")
                if src_path.is_file():
                    shutil.copy2(src_path, dst)
                else:
                    shutil.copytree(src_path, dst, dirs_exist_ok=True)
                    
    def _backup_p1(self, backup_dir: Path):
        """备份P1重要内容"""
        p1_dir = backup_dir / "P1"
        p1_dir.mkdir(exist_ok=True)
        
        # 备份skills
        skills_src = self.base_path / "skills"
        if skills_src.exists():
            for skill_dir in skills_src.iterdir():
                if skill_dir.is_dir():
                    skill_backup = p1_dir / "skills" / skill_dir.name
                    skill_backup.mkdir(parents=True, exist_ok=True)
                    
                    # 只备份SKILL.md
                    skill_md = skill_dir / "SKILL.md"
                    if skill_md.exists():
                        shutil.copy2(skill_md, skill_backup / "SKILL.md")
                        
        # 备份Memory Blocks
        blocks_src = self.base_path / "memory" / "warm" / "blocks"
        if blocks_src.exists():
            blocks_dst = p1_dir / "blocks"
            blocks_dst.mkdir(exist_ok=True)
            for f in blocks_src.glob("*.json"):
                shutil.copy2(f, blocks_dst)
                
    def push_to_github(self, backup_dir: str) -> bool:
        """推送到GitHub"""
        try:
            github_dir = self.backup_root / "github-sync"
            
            # 初始化git仓库
            if not (github_dir / ".git").exists():
                github_dir.mkdir(parents=True, exist_ok=True)
                subprocess.run(["git", "init"], cwd=github_dir, check=True, capture_output=True)
                subprocess.run(["git", "remote", "add", "origin", 
                    "https://github.com/wangjohnny9955/Kbot-backup.git"], 
                    cwd=github_dir, capture_output=True)
                    
            # 复制备份内容
            if Path(backup_dir).exists():
                for item in Path(backup_dir).iterdir():
                    dst = github_dir / item.name
                    if item.is_dir():
                        if dst.exists():
                            shutil.rmtree(dst)
                        shutil.copytree(item, dst)
                    else:
                        shutil.copy2(item, dst)
                        
            # Git操作
            subprocess.run(["git", "add", "-A"], cwd=github_dir, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", f"Backup: {datetime.now().isoformat()}"], 
                cwd=github_dir, capture_output=True)
            result = subprocess.run(["git", "push", "origin", "HEAD:main"], 
                cwd=github_dir, capture_output=True, text=True)
                
            if result.returncode == 0:
                print("[OK] GitHub push successful")
                return True
            else:
                print(f"[WARN] GitHub push failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[ERROR] GitHub push error: {e}")
            return False
            
    def list_backups(self, backup_type: str = None, days: int = 7) -> List[Dict]:
        """列出备份"""
        backups = []
        
        types = [backup_type] if backup_type else ["hot", "incremental", "full"]
        
        for t in types:
            type_dir = self.backup_root / t
            if not type_dir.exists():
                continue
                
            for backup_dir in type_dir.iterdir():
                if backup_dir.is_dir() and backup_dir.name != "latest":
                    try:
                        mtime = datetime.fromtimestamp(backup_dir.stat().st_mtime)
                        if (datetime.now() - mtime).days <= days:
                            report_file = backup_dir / "backup_report.json"
                            if report_file.exists():
                                with open(report_file, 'r', encoding='utf-8') as f:
                                    report = json.load(f)
                                    backups.append(report)
                            else:
                                backups.append({
                                    "backup_id": backup_dir.name,
                                    "type": t,
                                    "timestamp": mtime.isoformat()
                                })
                    except:
                        pass
                        
        return sorted(backups, key=lambda x: x.get("timestamp", ""), reverse=True)
        
    def get_status(self) -> Dict:
        """获取备份状态"""
        status = {
            "last_backup": None,
            "total_backups": 0,
            "storage_usage": {}
        }
        
        backups = self.list_backups(days=30)
        if backups:
            status["last_backup"] = backups[0].get("timestamp")
            status["total_backups"] = len(backups)
            
        # 计算存储使用
        for t in ["hot", "incremental", "full"]:
            type_dir = self.backup_root / t
            if type_dir.exists():
                size = sum(f.stat().st_size for f in type_dir.rglob("*") if f.is_file())
                status["storage_usage"][t] = f"{size // 1024 // 1024}MB"
                
        return status


def main():
    scheduler = MemoryBackupScheduler()
    
    if len(sys.argv) < 2:
        print("Usage: scheduler.py <command> [args]")
        print("Commands: init, backup, push, list, status")
        return
        
    cmd = sys.argv[1]
    
    if cmd == "init":
        scheduler.init_scheduler()
    elif cmd == "backup":
        btype = sys.argv[2] if len(sys.argv) > 2 else "incremental"
        priority = sys.argv[3] if len(sys.argv) > 3 else "P1"
        scheduler.backup(btype, priority)
    elif cmd == "push":
        backup_dir = sys.argv[2] if len(sys.argv) > 2 else None
        if backup_dir:
            scheduler.push_to_github(backup_dir)
        else:
            print("请指定备份目录")
    elif cmd == "list":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        backups = scheduler.list_backups(days=days)
        print(json.dumps(backups, indent=2, ensure_ascii=False))
    elif cmd == "status":
        status = scheduler.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
