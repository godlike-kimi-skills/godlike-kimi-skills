#!/usr/bin/env python3
"""
update-stats.py - 更新 README 中的统计数据
"""

import re
import json
from pathlib import Path
from datetime import datetime

def count_skills(skills_dir):
    """统计 skills 数量"""
    skills_path = Path(skills_dir)
    if not skills_path.exists():
        return 0, {}
    
    categories = {}
    total = 0
    
    for skill_dir in skills_path.iterdir():
        if skill_dir.is_dir() and (skill_dir / 'SKILL.md').exists():
            total += 1
            # 尝试从 SKILL.md 中提取分类
            skill_md = skill_dir / 'SKILL.md'
            content = skill_md.read_text(encoding='utf-8', errors='ignore')
            
            # 简单分类检测（基于关键词）
            category = '其他'
            if any(kw in content.lower() for kw in ['coding', 'git', 'debug', 'code', 'dev']):
                category = '开发效率'
            elif any(kw in content.lower() for kw in ['ai', 'memory', 'search', 'llm']):
                category = 'AI 增强'
            elif any(kw in content.lower() for kw in ['stock', 'finance', 'crypto', 'trading']):
                category = '金融交易'
            elif any(kw in content.lower() for kw in ['file', 'system', 'monitor']):
                category = '系统工具'
            elif any(kw in content.lower() for kw in ['doc', 'markdown', 'ppt', 'pdf']):
                category = '文档处理'
            
            categories[category] = categories.get(category, 0) + 1
    
    return total, categories

def update_readme_stats(readme_path, total, categories):
    """更新 README 中的统计数据"""
    readme = Path(readme_path)
    if not readme.exists():
        print(f"README 不存在: {readme_path}")
        return False
    
    content = readme.read_text(encoding='utf-8')
    
    # 更新统计数据块
    stats_pattern = r'```\n总 Skills 数: \d+.*?```'
    new_stats = f'''```
总 Skills 数: {total}+ (持续增加中...)
分类数: {len(categories)}+
最后更新: {datetime.now().strftime("%Y-%m-%d")}
更新频率: 每日
```'''
    
    if re.search(stats_pattern, content, re.DOTALL):
        content = re.sub(stats_pattern, new_stats, content, flags=re.DOTALL)
    else:
        # 在 ## 📊 项目统计 后面插入
        content = content.replace(
            '## 📊 项目统计\n',
            f'## 📊 项目统计\n\n{new_stats}\n'
        )
    
    readme.write_text(content, encoding='utf-8')
    print(f"✅ README 统计已更新: {total} 个 skills, {len(categories)} 个分类")
    return True

def generate_category_table(categories):
    """生成分类统计表"""
    lines = ['| 分类 | 数量 |', '|------|------|']
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        lines.append(f'| {cat} | {count} |')
    return '\n'.join(lines)

if __name__ == '__main__':
    print("更新项目统计...\n")
    
    # 统计 skills
    total, categories = count_skills('./skills')
    
    print(f"Skills 总数: {total}")
    print(f"分类统计:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  - {cat}: {count}")
    
    # 更新 README
    update_readme_stats('./README.md', total, categories)
    
    print("\n完成!")
