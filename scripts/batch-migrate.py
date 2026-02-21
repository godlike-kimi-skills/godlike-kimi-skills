#!/usr/bin/env python3
"""
batch-migrate.py - 批量迁移 skills 从本地到 Godlike 仓库
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

def load_skill_metadata(skill_dir):
    """加载 skill 的元数据"""
    skill_file = Path(skill_dir) / "SKILL.md"
    if not skill_file.exists():
        return None
    
    content = skill_file.read_text(encoding='utf-8')
    
    # 解析 frontmatter
    metadata = {
        'name': skill_dir.name,
        'has_skill_md': True,
        'size': len(content)
    }
    
    # 提取标题（第一行 # 后面的内容）
    for line in content.split('\n'):
        if line.startswith('# ') and not line.startswith('# ---'):
            metadata['title'] = line[2:].strip()
            break
    
    # 提取描述（标题后的第一段）
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('# ') and not line.startswith('# ---'):
            # 找下一段非空文本
            for j in range(i+1, min(i+10, len(lines))):
                if lines[j].strip() and not lines[j].startswith('#'):
                    metadata['description'] = lines[j].strip()[:100]
                    break
            break
    
    return metadata

def migrate_skill(source_dir, target_dir):
    """迁移单个 skill"""
    source = Path(source_dir)
    target = Path(target_dir)
    
    if not source.exists():
        print(f"❌ 源目录不存在: {source}")
        return False
    
    if target.exists():
        print(f"⚠️ 目标已存在，跳过: {target.name}")
        return False
    
    try:
        shutil.copytree(source, target)
        print(f"✅ 已迁移: {source.name}")
        return True
    except Exception as e:
        print(f"❌ 迁移失败 {source.name}: {e}")
        return False

def batch_migrate(source_base, target_base, skill_list=None):
    """批量迁移 skills"""
    source_base = Path(source_base)
    target_base = Path(target_base)
    
    if skill_list:
        # 迁移指定列表
        skills_to_migrate = skill_list
    else:
        # 迁移所有 skills
        skills_to_migrate = [d.name for d in source_base.iterdir() if d.is_dir()]
    
    results = {
        'total': len(skills_to_migrate),
        'success': 0,
        'failed': 0,
        'skipped': 0,
        'details': []
    }
    
    print(f"\n开始批量迁移 {len(skills_to_migrate)} 个 skills...")
    print("=" * 50)
    
    for skill_name in skills_to_migrate:
        source = source_base / skill_name
        target = target_base / skill_name
        
        if target.exists():
            results['skipped'] += 1
            results['details'].append({'name': skill_name, 'status': 'skipped'})
        else:
            if migrate_skill(source, target):
                results['success'] += 1
                results['details'].append({'name': skill_name, 'status': 'success'})
            else:
                results['failed'] += 1
                results['details'].append({'name': skill_name, 'status': 'failed'})
    
    print("=" * 50)
    print(f"总计: {results['total']} | 成功: {results['success']} | 跳过: {results['skipped']} | 失败: {results['failed']}")
    
    return results

def generate_skill_index(target_base):
    """生成 skill 索引文件"""
    target_base = Path(target_base)
    skills = []
    
    for skill_dir in sorted(target_base.iterdir()):
        if skill_dir.is_dir():
            metadata = load_skill_metadata(skill_dir)
            if metadata:
                skills.append(metadata)
    
    index = {
        'generated_at': datetime.now().isoformat(),
        'total': len(skills),
        'skills': skills
    }
    
    index_file = Path('docs') / 'skill-index.json'
    index_file.parent.mkdir(exist_ok=True)
    index_file.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding='utf-8')
    
    print(f"\n索引已生成: {index_file} ({len(skills)} 个 skills)")
    return index

if __name__ == '__main__':
    import sys
    
    # 默认配置
    SOURCE_SKILLS = 'D:/kimi/skills'  # 本地 skills 目录
    TARGET_SKILLS = './skills'  # Godlike 仓库 skills 目录
    
    # 首批核心 skills（已迁移）
    CORE_SKILLS = [
        'coding-agent', 'git-toolkit', 'dev-workflow', 'code-search', 'debug-master',
        'long-term-memory', 'brave-search', 'stock-watcher', 'file-organizer', 'doc-gen-skill'
    ]
    
    print("Godlike Skills 批量迁移工具")
    print("=" * 50)
    print(f"源目录: {SOURCE_SKILLS}")
    print(f"目标目录: {TARGET_SKILLS}")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        # 迁移所有（排除已迁移的）
        print("\n模式: 迁移所有未迁移的 skills")
        results = batch_migrate(SOURCE_SKILLS, TARGET_SKILLS)
    else:
        # 显示已迁移的核心 skills
        print("\n核心 skills 已迁移:")
        for skill in CORE_SKILLS:
            print(f"  ✅ {skill}")
        print("\n使用 --all 参数迁移所有 skills")
        results = None
    
    # 生成索引
    generate_skill_index(TARGET_SKILLS)
    
    print("\n完成!")
