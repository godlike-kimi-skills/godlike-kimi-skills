#!/usr/bin/env python3
"""
Git Toolkit - Robust Git operations with timeout and retry
"""

import subprocess
import sys
import os
import argparse
import json
import time
from pathlib import Path
from typing import Optional, Tuple, List
import concurrent.futures

# Default configuration
DEFAULT_TIMEOUT = 10
DEFAULT_RETRY = 3
DEFAULT_RETRY_DELAY = 5

class GitOperationError(Exception):
    """Git operation failed"""
    pass

class GitToolkit:
    def __init__(self, repo_path: str = ".", timeout: int = DEFAULT_TIMEOUT, 
                 retry: int = DEFAULT_RETRY, retry_delay: int = DEFAULT_RETRY_DELAY):
        self.repo_path = Path(repo_path).resolve()
        self.timeout = timeout
        self.retry = retry
        self.retry_delay = retry_delay
        
    def _run_git(self, args: List[str], check_stdout: bool = True) -> Tuple[int, str, str]:
        """Run git command with timeout"""
        cmd = ["git", "-C", str(self.repo_path)] + args
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding='utf-8',
                errors='ignore'
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Timeout after {self.timeout}s"
        except Exception as e:
            return -1, "", str(e)
    
    def _run_with_retry(self, args: List[str], operation_name: str) -> Tuple[bool, str]:
        """Run git command with retry logic"""
        for attempt in range(1, self.retry + 1):
            returncode, stdout, stderr = self._run_git(args)
            
            if returncode == 0:
                return True, stdout
            
            # Check if it's a network error
            error_text = stderr.lower()
            is_network_error = any(err in error_text for err in [
                "timeout", "connection", "reset", "refused", "could not resolve",
                "failed to connect", "unable to access"
            ])
            
            if is_network_error and attempt < self.retry:
                print(f"  [!] {operation_name} failed (network), retrying {attempt}/{self.retry}...")
                time.sleep(self.retry_delay)
                continue
            else:
                return False, stderr
        
        return False, f"Failed after {self.retry} attempts"
    
    def is_git_repo(self) -> bool:
        """Check if path is a git repository"""
        returncode, _, _ = self._run_git(["rev-parse", "--git-dir"])
        return returncode == 0
    
    def quick_status(self) -> dict:
        """Get quick local status (no network)"""
        result = {
            "is_repo": self.is_git_repo(),
            "branch": None,
            "commit": None,
            "dirty": False,
            "ahead": 0,
            "behind": 0,
            "untracked": 0,
            "modified": 0,
            "staged": 0
        }
        
        if not result["is_repo"]:
            return result
        
        # Get branch
        _, stdout, _ = self._run_git(["branch", "--show-current"])
        result["branch"] = stdout.strip() if stdout else "HEAD"
        
        # Get commit
        _, stdout, _ = self._run_git(["rev-parse", "--short", "HEAD"])
        result["commit"] = stdout.strip() if stdout else "unknown"
        
        # Check dirty
        _, stdout, _ = self._run_git(["status", "--porcelain"])
        if stdout:
            lines = stdout.strip().split('\n')
            result["dirty"] = True
            for line in lines:
                if line.startswith('??'):
                    result["untracked"] += 1
                elif line.startswith('M') or line.startswith(' M'):
                    result["modified"] += 1
                elif line.startswith('A') or line.startswith('A '):
                    result["staged"] += 1
        
        return result
    
    def check_remote(self) -> dict:
        """Check if behind/ahead of remote"""
        result = {
            "has_remote": False,
            "local_commit": None,
            "remote_commit": None,
            "behind": 0,
            "ahead": 0,
            "needs_update": False
        }
        
        if not self.is_git_repo():
            return result
        
        # Get local commit
        _, stdout, _ = self._run_git(["rev-parse", "HEAD"])
        result["local_commit"] = stdout.strip()[:7] if stdout else None
        
        # Check remote with retry
        success, _ = self._run_with_retry(["fetch", "origin", "--depth=1"], "Fetch")
        
        if success:
            result["has_remote"] = True
            _, stdout, _ = self._run_git(["rev-parse", "origin/master"])
            result["remote_commit"] = stdout.strip()[:7] if stdout else None
            
            # Count behind/ahead
            _, stdout, _ = self._run_git(["rev-list", "--count", "HEAD..origin/master"])
            if stdout.strip().isdigit():
                result["behind"] = int(stdout.strip())
            
            _, stdout, _ = self._run_git(["rev-list", "--count", "origin/master..HEAD"])
            if stdout.strip().isdigit():
                result["ahead"] = int(stdout.strip())
            
            result["needs_update"] = result["behind"] > 0
        
        return result
    
    def safe_pull(self) -> Tuple[bool, str]:
        """Pull with retry and backup"""
        if not self.is_git_repo():
            return False, "Not a git repository"
        
        # Check for uncommitted changes
        status = self.quick_status()
        if status["dirty"]:
            return False, f"Repository has uncommitted changes ({status['modified']} modified, {status['untracked']} untracked)"
        
        # Stash backup (optional safety)
        # self._run_git(["stash", "push", "-m", "auto-backup-before-pull"])
        
        # Pull with retry
        success, output = self._run_with_retry(["pull", "origin", "master"], "Pull")
        
        if success:
            return True, "Pull successful"
        else:
            return False, f"Pull failed: {output}"
    
    def safe_push(self) -> Tuple[bool, str]:
        """Push with retry"""
        if not self.is_git_repo():
            return False, "Not a git repository"
        
        success, output = self._run_with_retry(["push", "origin", "master"], "Push")
        
        if success:
            return True, "Push successful"
        else:
            return False, f"Push failed: {output}"
    
    def commit_and_push(self, message: str) -> Tuple[bool, str]:
        """Commit all changes and push"""
        if not self.is_git_repo():
            return False, "Not a git repository"
        
        # Add all
        self._run_git(["add", "-A"])
        
        # Commit
        success, output = self._run_with_retry(["commit", "-m", message], "Commit")
        if not success:
            return False, f"Commit failed: {output}"
        
        # Push
        return self.safe_push()


def cmd_status(args):
    """Quick status command"""
    path = args.path or "."
    toolkit = GitToolkit(path, timeout=args.timeout)
    
    if not toolkit.is_git_repo():
        print(f"[X] Not a git repository: {path}")
        return 1
    
    status = toolkit.quick_status()
    
    print(f"\n[Git Status: {path}]")
    print(f"  Branch: {status['branch']}")
    print(f"  Commit: {status['commit']}")
    print(f"  Clean: {'No' if status['dirty'] else 'Yes'}")
    
    if status['dirty']:
        print(f"  Modified: {status['modified']}")
        print(f"  Untracked: {status['untracked']}")
        print(f"  Staged: {status['staged']}")
    
    return 0


def cmd_check_remote(args):
    """Check remote updates"""
    path = args.path or "."
    toolkit = GitToolkit(path, timeout=args.timeout, retry=args.retry)
    
    if not toolkit.is_git_repo():
        print(f"[X] Not a git repository: {path}")
        return 1
    
    print(f"\n[Checking Remote: {path}]")
    print("  Fetching... (timeout: {}s)".format(args.timeout))
    
    remote = toolkit.check_remote()
    
    print(f"  Local: {remote['local_commit']}")
    print(f"  Remote: {remote['remote_commit'] or 'N/A'}")
    
    if remote['behind'] > 0:
        print(f"  [!] Behind by {remote['behind']} commits")
        return 2  # Special exit code for updates available
    elif remote['ahead'] > 0:
        print(f"  [!] Ahead by {remote['ahead']} commits (needs push)")
        return 3
    else:
        print(f"  [OK] Up to date")
        return 0


def cmd_pull(args):
    """Safe pull with retry"""
    path = args.path or "."
    toolkit = GitToolkit(path, timeout=args.timeout, retry=args.retry)
    
    print(f"\n[Pulling: {path}]")
    success, message = toolkit.safe_pull()
    
    if success:
        print(f"  [OK] {message}")
        return 0
    else:
        print(f"  [X] {message}")
        return 1


def cmd_push(args):
    """Safe push with retry"""
    path = args.path or "."
    toolkit = GitToolkit(path, timeout=args.timeout, retry=args.retry)
    
    print(f"\n[Pushing: {path}]")
    success, message = toolkit.safe_push()
    
    if success:
        print(f"  [OK] {message}")
        return 0
    else:
        print(f"  [X] {message}")
        return 1


def cmd_batch_check(args):
    """Batch check all repos in directory"""
    base_path = Path(args.directory)
    
    if not base_path.exists():
        print(f"[X] Directory not found: {base_path}")
        return 1
    
    print(f"\n[Batch Check: {base_path}]")
    
    # Find all git repos
    git_repos = []
    for item in base_path.iterdir():
        if item.is_dir():
            git_dir = item / ".git"
            if git_dir.exists():
                git_repos.append(item)
    
    print(f"  Found {len(git_repos)} git repositories\n")
    
    # Check each repo
    needs_update = []
    for repo in git_repos:
        toolkit = GitToolkit(repo, timeout=5)
        status = toolkit.quick_status()
        
        name = repo.name
        branch = status['branch'] or 'N/A'
        dirty = "*" if status['dirty'] else ""
        
        print(f"  {name:20} [{branch:15}] {dirty}")
        
        # Check remote (quick)
        remote = toolkit.check_remote()
        if remote['behind'] > 0:
            print(f"    [!] Behind by {remote['behind']} commits")
            needs_update.append((name, remote['behind']))
    
    print(f"\n  Summary: {len(needs_update)} repos need update")
    return 0


def cmd_commit_push(args):
    """Commit and push"""
    path = args.path or "."
    toolkit = GitToolkit(path, timeout=args.timeout, retry=args.retry)
    
    print(f"\n[Commit & Push: {path}]")
    print(f"  Message: {args.message}")
    
    success, message = toolkit.commit_and_push(args.message)
    
    if success:
        print(f"  [OK] {message}")
        return 0
    else:
        print(f"  [X] {message}")
        return 1


def main():
    parser = argparse.ArgumentParser(description='Git Toolkit - Robust Git Operations')
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Global options
    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT, help='Timeout in seconds')
    parser.add_argument('--retry', type=int, default=DEFAULT_RETRY, help='Retry attempts')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Quick local status')
    status_parser.add_argument('path', nargs='?', help='Repository path')
    
    # Check-remote command
    check_parser = subparsers.add_parser('check-remote', help='Check for remote updates')
    check_parser.add_argument('path', nargs='?', help='Repository path')
    check_parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT, help='Timeout in seconds')
    check_parser.add_argument('--retry', type=int, default=DEFAULT_RETRY, help='Retry attempts')
    
    # Pull command
    pull_parser = subparsers.add_parser('pull', help='Safe pull with retry')
    pull_parser.add_argument('path', nargs='?', help='Repository path')
    pull_parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT, help='Timeout in seconds')
    pull_parser.add_argument('--retry', type=int, default=DEFAULT_RETRY, help='Retry attempts')
    
    # Push command
    push_parser = subparsers.add_parser('push', help='Safe push with retry')
    push_parser.add_argument('path', nargs='?', help='Repository path')
    push_parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT, help='Timeout in seconds')
    push_parser.add_argument('--retry', type=int, default=DEFAULT_RETRY, help='Retry attempts')
    
    # Batch-check command
    batch_parser = subparsers.add_parser('batch-check', help='Check all repos in directory')
    batch_parser.add_argument('directory', help='Base directory')
    
    # Commit-push command
    commit_parser = subparsers.add_parser('commit-push', help='Commit and push')
    commit_parser.add_argument('message', help='Commit message')
    commit_parser.add_argument('path', nargs='?', help='Repository path')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        return cmd_status(args)
    elif args.command == 'check-remote':
        return cmd_check_remote(args)
    elif args.command == 'pull':
        return cmd_pull(args)
    elif args.command == 'push':
        return cmd_push(args)
    elif args.command == 'batch-check':
        return cmd_batch_check(args)
    elif args.command == 'commit-push':
        return cmd_commit_push(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
