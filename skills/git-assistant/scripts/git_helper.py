#!/usr/bin/env python3
"""
Git assistant for development workflows.
Usage: git_helper.py <command> [options]
"""

import os
import re
import sys
import subprocess
import argparse
from pathlib import Path


def run_git(args, capture=True):
    """Run a git command."""
    cmd = ['git'] + args
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, check=True)
            return None
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e}", file=sys.stderr)
        return None


def is_git_repo():
    """Check if current directory is a git repo."""
    result = run_git(['rev-parse', '--git-dir'], capture=True)
    return result is not None


def get_repo_name():
    """Get repository name."""
    remote_url = run_git(['remote', 'get-url', 'origin'], capture=True)
    if remote_url:
        # Extract name from URL
        match = re.search(r'/([^/]+?)(?:\.git)?$', remote_url)
        if match:
            return match.group(1)
    return "unknown"


def get_current_branch():
    """Get current branch name."""
    return run_git(['branch', '--show-current'], capture=True)


def get_status():
    """Get repository status."""
    if not is_git_repo():
        print("❌ Not a git repository!")
        return None
    
    branch = get_current_branch()
    repo = get_repo_name()
    
    print(f"\n📁 Repository: {repo}")
    print(f"🌿 Branch: {branch}\n")
    
    # Status
    status = run_git(['status', '--short'], capture=True)
    if status:
        print("Changes:")
        for line in status.split('\n'):
            if line:
                status_code = line[:2]
                file = line[3:]
                icon = "🆕" if status_code.strip() in ['??', 'A'] else \
                       "✏️" if status_code.strip() in ['M', 'MM'] else \
                       "🗑️" if status_code.strip() == 'D' else "📄"
                print(f"  {icon} {line}")
    else:
        print("  ✅ Working directory clean")
    
    # Untracked files
    untracked = run_git(['ls-files', '--others', '--exclude-standard'], capture=True)
    if untracked:
        print(f"\n🆕 Untracked files: {len(untracked.split(chr(10)))}")
    
    # Recent commits
    print("\nRecent commits:")
    log = run_git(['log', '--oneline', '-5'], capture=True)
    if log:
        for line in log.split('\n'):
            print(f"  • {line}")
    
    print()
    return True


def suggest_commit_message():
    """Suggest a commit message based on staged changes."""
    # Get staged files
    staged = run_git(['diff', '--cached', '--name-only'], capture=True)
    if not staged:
        print("No staged changes. Stage files with: git add <file>")
        return None
    
    files = staged.split('\n')
    print(f"Staged files ({len(files)}):")
    for f in files:
        print(f"  • {f}")
    
    # Analyze file types
    types = set()
    for f in files:
        if f.endswith('.py'):
            types.add('python')
        elif f.endswith('.js') or f.endswith('.ts'):
            types.add('javascript')
        elif f.endswith('.md') or f.endswith('.txt'):
            types.add('docs')
        elif f.endswith('.json') or f.endswith('.yml') or f.endswith('.yaml'):
            types.add('config')
        elif f.endswith('.html') or f.endswith('.css'):
            types.add('frontend')
    
    # Get diff stats
    stats = run_git(['diff', '--cached', '--stat'], capture=True)
    
    # Suggest messages
    print("\nSuggested commit messages:")
    print()
    
    if 'docs' in types and len(types) == 1:
        print("  📝 docs: Update documentation")
    elif 'config' in types and len(types) == 1:
        print("  ⚙️  config: Update configuration")
    elif 'frontend' in types:
        print("  🎨 feat: Update UI/components")
    elif 'python' in types or 'javascript' in types:
        print("  ✨ feat: Add new feature")
        print("  🐛 fix: Fix bug in module")
        print("  ♻️  refactor: Refactor code")
    else:
        print("  ✨ feat: Implement changes")
    
    print("\nTo commit with a message:")
    print('  git commit -m "your message"')
    
    return True


def create_branch(branch_type, name):
    """Create a new branch following conventions."""
    branch_name = f"{branch_type}/{name}"
    
    # Check if branch exists
    existing = run_git(['branch', '--list', branch_name], capture=True)
    if existing:
        print(f"⚠️ Branch '{branch_name}' already exists!")
        return False
    
    # Create and checkout
    run_git(['checkout', '-b', branch_name], capture=False)
    print(f"✅ Created and switched to branch: {branch_name}")
    return True


def list_branches():
    """List all branches with info."""
    current = get_current_branch()
    
    print("\nBranches:\n")
    
    # Local branches
    local = run_git(['branch'], capture=True)
    if local:
        print("Local:")
        for line in local.split('\n'):
            line = line.strip()
            if line.startswith('*'):
                print(f"  🌟 {line[2:]} (current)")
            else:
                print(f"     {line}")
    
    # Remote branches
    remote = run_git(['branch', '-r'], capture=True)
    if remote:
        print("\nRemote:")
        for line in remote.split('\n'):
            line = line.strip()
            if line:
                print(f"  🌐 {line}")
    
    print()


def switch_branch(branch_name):
    """Switch to a branch."""
    # Check if branch exists
    local = run_git(['branch', '--list', branch_name], capture=True)
    remote = run_git(['branch', '-r', '--list', f'origin/{branch_name}'], capture=True)
    
    if local:
        run_git(['checkout', branch_name], capture=False)
    elif remote:
        run_git(['checkout', '-b', branch_name, f'origin/{branch_name}'], capture=False)
    else:
        print(f"❌ Branch '{branch_name}' not found!")
        return False
    
    return True


def start_feature(name):
    """Start a new feature branch."""
    # Save current branch
    current = get_current_branch()
    
    # Switch to main/master
    main_branch = 'main' if run_git(['rev-parse', '--verify', 'main'], capture=True) else 'master'
    run_git(['checkout', main_branch], capture=False)
    
    # Pull latest
    run_git(['pull', 'origin', main_branch], capture=False)
    
    # Create feature branch
    create_branch('feature', name)
    
    print(f"\n✅ Started feature: {name}")
    print(f"   From: {main_branch}")
    print(f"   Previous: {current}")


def finish_feature():
    """Finish current feature branch."""
    current = get_current_branch()
    
    if not current.startswith('feature/'):
        print(f"⚠️ Current branch '{current}' is not a feature branch!")
        return False
    
    # Check for uncommitted changes
    status = run_git(['status', '--porcelain'], capture=True)
    if status:
        print("❌ You have uncommitted changes!")
        print("Commit or stash them first:")
        print("  git add .")
        print('  git commit -m "message"')
        return False
    
    # Switch to main and merge
    main_branch = 'main' if run_git(['rev-parse', '--verify', 'main'], capture=True) else 'master'
    run_git(['checkout', main_branch], capture=False)
    run_git(['pull', 'origin', main_branch], capture=False)
    
    print(f"\nMerging {current} into {main_branch}...")
    run_git(['merge', '--no-ff', current], capture=False)
    
    print(f"\n✅ Feature '{current}' merged!")
    print(f"   To push: git push origin {main_branch}")


def main():
    parser = argparse.ArgumentParser(description='Git assistant')
    subparsers = parser.add_subparsers(dest='command')
    
    # Status
    subparsers.add_parser('status', help='Show repository status')
    
    # Commit
    commit_parser = subparsers.add_parser('commit', help='Suggest commit message')
    
    # Branch
    branch_parser = subparsers.add_parser('branch', help='Create branch')
    branch_parser.add_argument('type', choices=['feature', 'bugfix', 'hotfix', 'release'])
    branch_parser.add_argument('name', help='Branch name')
    
    # Branches
    subparsers.add_parser('branches', help='List branches')
    
    # Switch
    switch_parser = subparsers.add_parser('switch', help='Switch branch')
    switch_parser.add_argument('branch', help='Branch name')
    
    # Start feature
    start_parser = subparsers.add_parser('start-feature', help='Start new feature')
    start_parser.add_argument('name', help='Feature name')
    
    # Finish feature
    subparsers.add_parser('finish-feature', help='Finish feature')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        get_status()
    elif args.command == 'commit':
        suggest_commit_message()
    elif args.command == 'branch':
        create_branch(args.type, args.name)
    elif args.command == 'branches':
        list_branches()
    elif args.command == 'switch':
        switch_branch(args.branch)
    elif args.command == 'start-feature':
        start_feature(args.name)
    elif args.command == 'finish-feature':
        finish_feature()
    else:
        get_status()


if __name__ == '__main__':
    main()
