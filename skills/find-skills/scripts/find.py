#!/usr/bin/env python3
"""Find Skills Implementation"""
import sys, os, json
from pathlib import Path

def find_skills(keyword=None):
    skills_dir = Path.home() / ".kimi" / "skills"
    installed = []
    
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    installed.append(skill_dir.name)
    
    # 模拟在线技能库
    available = [
        "tavily", "agent-browser", "find-skills", "long-term-memory",
        "persistent-agent", "self-learning", "proactive-agent",
        "coding-agent", "python-env-manager", "cron-scheduler"
    ]
    
    if keyword:
        available = [s for s in available if keyword.lower() in s.lower()]
    
    return {
        "installed": installed,
        "available_online": available,
        "total_installed": len(installed),
        "total_available": len(available)
    }

if __name__ == "__main__":
    keyword = sys.argv[1] if len(sys.argv) > 1 else None
    print(json.dumps(find_skills(keyword), indent=2))
