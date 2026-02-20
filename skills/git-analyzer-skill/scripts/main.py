#!/usr/bin/env python3
"""
Git Analyzer Skill - Main module for Git repository analysis.

Features:
- Commit history analysis
- Code statistics and metrics
- Contributor statistics
- Branch visualization
- Repository health checks
"""

import argparse
import os
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from git import Repo, Commit
from git.exc import InvalidGitRepositoryError


@dataclass
class CommitInfo:
    """Commit information container."""
    hash: str
    author: str
    email: str
    date: datetime
    message: str
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0


@dataclass
class ContributorStats:
    """Contributor statistics container."""
    name: str
    email: str
    commit_count: int = 0
    lines_added: int = 0
    lines_deleted: int = 0
    files_changed: int = 0
    first_commit: Optional[datetime] = None
    last_commit: Optional[datetime] = None


@dataclass
class CodeStats:
    """Code statistics container."""
    total_files: int = 0
    total_lines: int = 0
    blank_lines: int = 0
    comment_lines: int = 0
    code_lines: int = 0
    languages: Dict[str, int] = field(default_factory=dict)
    file_types: Dict[str, int] = field(default_factory=dict)


@dataclass
class BranchInfo:
    """Branch information container."""
    name: str
    is_remote: bool
    commit_count: int = 0
    last_commit_date: Optional[datetime] = None
    merged_branches: List[str] = field(default_factory=list)


class GitAnalyzer:
    """
    Git repository analyzer for comprehensive repository insights.
    
    Features:
    - Commit history analysis with filtering
    - Contributor statistics and activity patterns
    - Code metrics by language and file type
    - Branch tree visualization
    - Repository health checks
    """
    
    # File extensions to language mapping
    LANGUAGE_MAP = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.jsx': 'React JSX',
        '.tsx': 'React TSX',
        '.java': 'Java',
        '.c': 'C',
        '.cpp': 'C++',
        '.h': 'C/C++ Header',
        '.hpp': 'C++ Header',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.r': 'R',
        '.m': 'MATLAB/Objective-C',
        '.cs': 'C#',
        '.fs': 'F#',
        '.vb': 'Visual Basic',
        '.sh': 'Shell',
        '.bash': 'Bash',
        '.ps1': 'PowerShell',
        '.sql': 'SQL',
        '.html': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        '.sass': 'Sass',
        '.less': 'Less',
        '.xml': 'XML',
        '.json': 'JSON',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.toml': 'TOML',
        '.ini': 'INI',
        '.md': 'Markdown',
        '.rst': 'reStructuredText',
        '.tex': 'LaTeX',
        '.dockerfile': 'Dockerfile',
        '.tf': 'Terraform',
    }
    
    def __init__(self, repo_path: str = "."):
        """
        Initialize Git analyzer.
        
        Args:
            repo_path: Path to Git repository
        
        Raises:
            InvalidGitRepositoryError: If path is not a valid Git repository
        """
        self.repo_path = Path(repo_path).resolve()
        try:
            self.repo = Repo(self.repo_path)
        except InvalidGitRepositoryError:
            raise InvalidGitRepositoryError(
                f"'{repo_path}' is not a valid Git repository"
            )
    
    def get_commit_history(
        self,
        branch: str = "HEAD",
        limit: Optional[int] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        author: Optional[str] = None
    ) -> List[CommitInfo]:
        """
        Get commit history with optional filtering.
        
        Args:
            branch: Branch or ref to traverse
            limit: Maximum number of commits
            since: Start date filter
            until: End date filter
            author: Author name or email filter
        
        Returns:
            List of CommitInfo objects
        """
        commits = []
        iterator = self.repo.iter_commits(branch, max_count=limit)
        
        for commit in iterator:
            commit_date = datetime.fromtimestamp(commit.committed_date)
            
            # Apply filters
            if since and commit_date < since:
                continue
            if until and commit_date > until:
                continue
            if author and author not in str(commit.author):
                continue
            
            # Get stats if available
            files_changed = len(commit.stats.files)
            insertions = commit.stats.total.get('insertions', 0)
            deletions = commit.stats.total.get('deletions', 0)
            
            commits.append(CommitInfo(
                hash=commit.hexsha[:8],
                author=str(commit.author),
                email=commit.author.email or "",
                date=commit_date,
                message=commit.message.strip(),
                files_changed=files_changed,
                insertions=insertions,
                deletions=deletions
            ))
        
        return commits
    
    def get_contributor_stats(self) -> List[ContributorStats]:
        """
        Get contributor statistics.
        
        Returns:
            List of ContributorStats sorted by commit count
        """
        contributors = defaultdict(lambda: {
            'name': '',
            'email': '',
            'commits': 0,
            'insertions': 0,
            'deletions': 0,
            'files': set(),
            'dates': []
        })
        
        for commit in self.repo.iter_commits():
            email = commit.author.email or "unknown"
            contributors[email]['name'] = str(commit.author)
            contributors[email]['email'] = email
            contributors[email]['commits'] += 1
            contributors[email]['insertions'] += commit.stats.total.get('insertions', 0)
            contributors[email]['deletions'] += commit.stats.total.get('deletions', 0)
            contributors[email]['files'].update(commit.stats.files.keys())
            contributors[email]['dates'].append(
                datetime.fromtimestamp(commit.committed_date)
            )
        
        # Convert to sorted list
        result = []
        for email, data in contributors.items():
            dates = sorted(data['dates'])
            result.append(ContributorStats(
                name=data['name'],
                email=data['email'],
                commit_count=data['commits'],
                lines_added=data['insertions'],
                lines_deleted=data['deletions'],
                files_changed=len(data['files']),
                first_commit=dates[0] if dates else None,
                last_commit=dates[-1] if dates else None
            ))
        
        return sorted(result, key=lambda x: x.commit_count, reverse=True)
    
    def get_code_stats(self, path: str = ".") -> CodeStats:
        """
        Get code statistics for the repository.
        
        Args:
            path: Subdirectory path to analyze
        
        Returns:
            CodeStats object with metrics
        """
        stats = CodeStats()
        target_path = self.repo_path / path
        
        if not target_path.exists():
            return stats
        
        for root, dirs, files in os.walk(target_path):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in {
                '.git', 'node_modules', '__pycache__', '.venv', 'venv',
                'dist', 'build', '.pytest_cache', '.mypy_cache'
            }]
            
            for file in files:
                file_path = Path(root) / file
                
                # Skip binary files
                if self._is_binary(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    
                    total_lines = len(lines)
                    blank_lines = sum(1 for line in lines if not line.strip())
                    comment_lines = self._count_comment_lines(file_path, lines)
                    
                    stats.total_files += 1
                    stats.total_lines += total_lines
                    stats.blank_lines += blank_lines
                    stats.comment_lines += comment_lines
                    stats.code_lines += (total_lines - blank_lines - comment_lines)
                    
                    # Track languages
                    ext = file_path.suffix.lower()
                    lang = self.LANGUAGE_MAP.get(ext, 'Other')
                    stats.languages[lang] = stats.languages.get(lang, 0) + total_lines
                    
                    # Track file types
                    stats.file_types[ext or 'no_extension'] = \
                        stats.file_types.get(ext or 'no_extension', 0) + 1
                    
                except (IOError, OSError):
                    continue
        
        return stats
    
    def _is_binary(self, file_path: Path) -> bool:
        """Check if file is binary."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\x00' in chunk
        except:
            return True
    
    def _count_comment_lines(self, file_path: Path, lines: List[str]) -> int:
        """Count comment lines based on file type."""
        ext = file_path.suffix.lower()
        comment_patterns = {
            '.py': ['#'],
            '.js': ['//', '/*'],
            '.ts': ['//', '/*'],
            '.java': ['//', '/*'],
            '.c': ['//', '/*'],
            '.cpp': ['//', '/*'],
            '.go': ['//'],
            '.rb': ['#'],
            '.sh': ['#'],
            '.php': ['//', '#', '/*'],
            '.swift': ['//', '/*'],
            '.kt': ['//', '/*'],
            '.rs': ['//', '/*'],
        }
        
        patterns = comment_patterns.get(ext, [])
        count = 0
        in_block_comment = False
        
        for line in lines:
            stripped = line.strip()
            
            if '/*' in patterns:
                if '/*' in stripped and '*/' not in stripped:
                    in_block_comment = True
                    count += 1
                    continue
                elif in_block_comment:
                    count += 1
                    if '*/' in stripped:
                        in_block_comment = False
                    continue
                elif '/*' in stripped and '*/' in stripped:
                    count += 1
                    continue
            
            for pattern in patterns:
                if pattern != '/*' and stripped.startswith(pattern):
                    count += 1
                    break
        
        return count
    
    def get_branch_tree(self) -> List[BranchInfo]:
        """
        Get branch information and tree structure.
        
        Returns:
            List of BranchInfo objects
        """
        branches = []
        
        for branch in self.repo.branches:
            commits = list(self.repo.iter_commits(branch.name, max_count=1000))
            
            # Find merged branches
            merged = []
            for other in self.repo.branches:
                if other.name != branch.name:
                    try:
                        merge_base = self.repo.merge_base(branch, other)
                        if merge_base and merge_base[0].hexsha == other.commit.hexsha:
                            merged.append(other.name)
                    except:
                        pass
            
            branches.append(BranchInfo(
                name=branch.name,
                is_remote=False,
                commit_count=len(commits),
                last_commit_date=datetime.fromtimestamp(branch.commit.committed_date),
                merged_branches=merged
            ))
        
        # Add remote branches
        for remote in self.repo.remotes:
            for ref in remote.refs:
                branch_name = ref.name.split('/', 1)[-1]
                commits = list(self.repo.iter_commits(ref.name, max_count=1000))
                branches.append(BranchInfo(
                    name=f"{remote.name}/{branch_name}",
                    is_remote=True,
                    commit_count=len(commits),
                    last_commit_date=datetime.fromtimestamp(ref.commit.committed_date)
                ))
        
        return branches
    
    def find_large_files(self, size_threshold_mb: float = 1.0) -> List[Tuple[str, float]]:
        """
        Find large files in repository history.
        
        Args:
            size_threshold_mb: Size threshold in MB
        
        Returns:
            List of (file_path, size_mb) tuples
        """
        large_files = []
        threshold_bytes = size_threshold_mb * 1024 * 1024
        
        for commit in self.repo.iter_commits():
            for obj in commit.tree.traverse():
                if obj.type == 'blob':
                    size_mb = obj.size / (1024 * 1024)
                    if obj.size > threshold_bytes:
                        large_files.append((obj.path, size_mb))
        
        # Remove duplicates and sort
        seen = set()
        unique = []
        for path, size in sorted(large_files, key=lambda x: -x[1]):
            if path not in seen:
                seen.add(path)
                unique.append((path, size))
        
        return unique[:20]  # Return top 20
    
    def get_repository_summary(self) -> Dict:
        """Get comprehensive repository summary."""
        head = self.repo.head
        
        return {
            'path': str(self.repo_path),
            'is_bare': self.repo.bare,
            'active_branch': head.ref.name if not self.repo.head.is_detached else 'DETACHED',
            'commit_count': sum(1 for _ in self.repo.iter_commits()),
            'branch_count': len(list(self.repo.branches)),
            'remote_count': len(self.repo.remotes),
            'contributor_count': len(self.get_contributor_stats()),
            'remotes': [
                {'name': r.name, 'url': r.url}
                for r in self.repo.remotes
            ]
        }


def format_summary(summary: Dict) -> str:
    """Format repository summary for display."""
    lines = [
        "=" * 60,
        "Git Repository Analysis",
        "=" * 60,
        f"Path: {summary['path']}",
        f"Active Branch: {summary['active_branch']}",
        f"Commits: {summary['commit_count']}",
        f"Branches: {summary['branch_count']}",
        f"Remotes: {summary['remote_count']}",
        f"Contributors: {summary['contributor_count']}",
        ""
    ]
    
    if summary['remotes']:
        lines.append("Remotes:")
        for remote in summary['remotes']:
            lines.append(f"  {remote['name']}: {remote['url']}")
    
    return "\n".join(lines)


def format_contributors(contributors: List[ContributorStats]) -> str:
    """Format contributor stats for display."""
    lines = [
        "=" * 60,
        "Top Contributors",
        "=" * 60,
        f"{'Rank':<6}{'Commits':<10}{'Lines +/-':<15}{'Name':<30}",
        "-" * 60
    ]
    
    for i, c in enumerate(contributors[:10], 1):
        lines.append(
            f"{i:<6}{c.commit_count:<10}{c.lines_added:+d}/{c.lines_deleted:<+d}   {c.name[:28]:<30}"
        )
    
    return "\n".join(lines)


def format_code_stats(stats: CodeStats) -> str:
    """Format code statistics for display."""
    lines = [
        "=" * 60,
        "Code Statistics",
        "=" * 60,
        f"Total Files: {stats.total_files}",
        f"Total Lines: {stats.total_lines:,}",
        f"  Code: {stats.code_lines:,}",
        f"  Comments: {stats.comment_lines:,}",
        f"  Blank: {stats.blank_lines:,}",
        ""
    ]
    
    if stats.languages:
        lines.append("Languages (by lines):")
        sorted_langs = sorted(stats.languages.items(), key=lambda x: -x[1])
        for lang, lines_count in sorted_langs[:10]:
            pct = (lines_count / stats.total_lines * 100) if stats.total_lines else 0
            lines.append(f"  {lang}: {lines_count:,} ({pct:.1f}%)")
    
    return "\n".join(lines)


def format_branches(branches: List[BranchInfo]) -> str:
    """Format branch information for display."""
    lines = [
        "=" * 60,
        "Branch Tree",
        "=" * 60,
        f"{'Branch':<30}{'Commits':<10}{'Last Commit':<20}",
        "-" * 60
    ]
    
    local_branches = [b for b in branches if not b.is_remote]
    remote_branches = [b for b in branches if b.is_remote]
    
    lines.append("\nLocal Branches:")
    for b in local_branches:
        date_str = b.last_commit_date.strftime("%Y-%m-%d") if b.last_commit_date else "N/A"
        lines.append(f"  {b.name:<28}{b.commit_count:<10}{date_str:<20}")
    
    if remote_branches:
        lines.append("\nRemote Branches:")
        for b in remote_branches[:10]:
            date_str = b.last_commit_date.strftime("%Y-%m-%d") if b.last_commit_date else "N/A"
            lines.append(f"  {b.name:<28}{b.commit_count:<10}{date_str:<20}")
    
    return "\n".join(lines)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Git Repository Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/repo
  %(prog)s /path/to/repo --commits --limit 20
  %(prog)s /path/to/repo --contributors
  %(prog)s /path/to/repo --stats
  %(prog)s /path/to/repo --branches
        """
    )
    
    parser.add_argument("repo_path", nargs="?", default=".",
                       help="Path to Git repository (default: current directory)")
    parser.add_argument("--commits", action="store_true",
                       help="Show commit history")
    parser.add_argument("--contributors", action="store_true",
                       help="Show contributor statistics")
    parser.add_argument("--stats", action="store_true",
                       help="Show code statistics")
    parser.add_argument("--branches", action="store_true",
                       help="Show branch tree")
    parser.add_argument("--large-files", action="store_true",
                       help="Find large files")
    parser.add_argument("--limit", type=int, default=10,
                       help="Limit for commit history (default: 10)")
    parser.add_argument("--all", action="store_true",
                       help="Show all information")
    
    args = parser.parse_args()
    
    try:
        analyzer = GitAnalyzer(args.repo_path)
        
        # If no specific flag, show summary
        if not any([args.commits, args.contributors, args.stats, 
                   args.branches, args.large_files]):
            args.all = True
        
        if args.all:
            print(format_summary(analyzer.get_repository_summary()))
            print()
        
        if args.all or args.contributors:
            print(format_contributors(analyzer.get_contributor_stats()))
            print()
        
        if args.all or args.stats:
            print(format_code_stats(analyzer.get_code_stats()))
            print()
        
        if args.all or args.branches:
            print(format_branches(analyzer.get_branch_tree()))
            print()
        
        if args.commits:
            print("=" * 60)
            print("Recent Commits")
            print("=" * 60)
            for commit in analyzer.get_commit_history(limit=args.limit):
                print(f"\n{commit.hash} - {commit.date.strftime('%Y-%m-%d %H:%M')}")
                print(f"Author: {commit.author}")
                print(f"Message: {commit.message[:80]}")
        
        if args.large_files:
            large = analyzer.find_large_files()
            if large:
                print("\n" + "=" * 60)
                print("Large Files (>1MB)")
                print("=" * 60)
                for path, size in large:
                    print(f"  {size:.2f}MB - {path}")
        
    except InvalidGitRepositoryError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
