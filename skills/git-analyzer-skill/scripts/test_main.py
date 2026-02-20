#!/usr/bin/env python3
"""Tests for Git Analyzer Skill."""

import os
import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from git import Repo
from git.exc import InvalidGitRepositoryError

from main import (
    GitAnalyzer, CommitInfo, ContributorStats, CodeStats,
    format_summary, format_contributors, format_code_stats
)


class TestGitAnalyzer(unittest.TestCase):
    """Test GitAnalyzer functionality."""
    
    def setUp(self):
        """Create temporary Git repository."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo = Repo.init(self.temp_dir)
        
        # Configure git user
        config = self.repo.config_writer()
        config.set_value("user", "name", "Test User")
        config.set_value("user", "email", "test@example.com")
        config.release()
        
        # Create initial commit
        self._create_file("README.md", "# Test Repository")
        self.repo.index.add(["README.md"])
        self.repo.index.commit("Initial commit")
        
        self.analyzer = GitAnalyzer(self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary directory."""
        self.analyzer = None
        shutil.rmtree(self.temp_dir)
    
    def _create_file(self, filename: str, content: str):
        """Helper to create files."""
        filepath = Path(self.temp_dir) / filename
        filepath.write_text(content)
    
    def test_init_invalid_repo(self):
        """Test initialization with invalid repository."""
        with self.assertRaises(InvalidGitRepositoryError):
            GitAnalyzer(tempfile.mkdtemp())
    
    def test_get_commit_history(self):
        """Test commit history retrieval."""
        commits = self.analyzer.get_commit_history()
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0].message, "Initial commit")
        self.assertEqual(commits[0].author, "Test User")
    
    def test_get_commit_history_with_limit(self):
        """Test commit history with limit."""
        # Add more commits
        for i in range(5):
            self._create_file(f"file{i}.txt", f"content {i}")
            self.repo.index.add([f"file{i}.txt"])
            self.repo.index.commit(f"Commit {i}")
        
        commits = self.analyzer.get_commit_history(limit=3)
        self.assertEqual(len(commits), 3)
    
    def test_get_contributor_stats(self):
        """Test contributor statistics."""
        # Add more commits
        self._create_file("test.py", "print('hello')")
        self.repo.index.add(["test.py"])
        self.repo.index.commit("Add test file")
        
        contributors = self.analyzer.get_contributor_stats()
        self.assertEqual(len(contributors), 1)
        self.assertEqual(contributors[0].name, "Test User")
        self.assertGreaterEqual(contributors[0].commit_count, 2)
    
    def test_get_code_stats(self):
        """Test code statistics."""
        # Create Python file
        self._create_file("main.py", "# Main file\nprint('hello')\n")
        
        stats = self.analyzer.get_code_stats()
        self.assertGreater(stats.total_files, 0)
        self.assertGreater(stats.total_lines, 0)
        
        # Check language detection
        self.assertIn("Markdown", stats.languages)
        self.assertIn("Python", stats.languages)
    
    def test_get_branch_tree(self):
        """Test branch tree retrieval."""
        # Create a new branch
        self.repo.create_head("feature-branch")
        
        branches = self.analyzer.get_branch_tree()
        branch_names = [b.name for b in branches]
        self.assertIn("main", branch_names)
        self.assertIn("feature-branch", branch_names)
    
    def test_get_repository_summary(self):
        """Test repository summary."""
        summary = self.analyzer.get_repository_summary()
        
        self.assertEqual(summary['path'], str(Path(self.temp_dir).resolve()))
        self.assertIn(summary['active_branch'], ['main', 'master'])
        self.assertGreaterEqual(summary['commit_count'], 1)
        self.assertGreaterEqual(summary['branch_count'], 1)
    
    def test_find_large_files(self):
        """Test large file detection."""
        # Create a large file
        large_content = "x" * (2 * 1024 * 1024)  # 2MB
        self._create_file("large_file.bin", large_content)
        self.repo.index.add(["large_file.bin"])
        self.repo.index.commit("Add large file")
        
        large_files = self.analyzer.find_large_files(size_threshold_mb=1.0)
        self.assertTrue(any("large_file.bin" in f[0] for f in large_files))


class TestCommitInfo(unittest.TestCase):
    """Test CommitInfo dataclass."""
    
    def test_creation(self):
        """Test CommitInfo creation."""
        info = CommitInfo(
            hash="abc123",
            author="Test",
            email="test@test.com",
            date=datetime.now(),
            message="Test commit"
        )
        self.assertEqual(info.hash, "abc123")
        self.assertEqual(info.files_changed, 0)


class TestContributorStats(unittest.TestCase):
    """Test ContributorStats dataclass."""
    
    def test_creation(self):
        """Test ContributorStats creation."""
        stats = ContributorStats(
            name="John Doe",
            email="john@example.com",
            commit_count=5
        )
        self.assertEqual(stats.commit_count, 5)
        self.assertEqual(stats.lines_added, 0)


class TestCodeStats(unittest.TestCase):
    """Test CodeStats dataclass."""
    
    def test_default_values(self):
        """Test CodeStats default values."""
        stats = CodeStats()
        self.assertEqual(stats.total_files, 0)
        self.assertEqual(stats.total_lines, 0)
        self.assertEqual(stats.languages, {})


class TestFormatFunctions(unittest.TestCase):
    """Test formatting functions."""
    
    def test_format_summary(self):
        """Test summary formatting."""
        summary = {
            'path': '/test/path',
            'is_bare': False,
            'active_branch': 'main',
            'commit_count': 10,
            'branch_count': 3,
            'remote_count': 1,
            'contributor_count': 2,
            'remotes': [{'name': 'origin', 'url': 'git@github.com:test/repo.git'}]
        }
        
        output = format_summary(summary)
        self.assertIn('Git Repository Analysis', output)
        self.assertIn('/test/path', output)
        self.assertIn('main', output)
    
    def test_format_contributors(self):
        """Test contributor formatting."""
        contributors = [
            ContributorStats(
                name="Alice",
                email="alice@example.com",
                commit_count=10,
                lines_added=100,
                lines_deleted=50
            ),
            ContributorStats(
                name="Bob",
                email="bob@example.com",
                commit_count=5,
                lines_added=50,
                lines_deleted=25
            )
        ]
        
        output = format_contributors(contributors)
        self.assertIn('Top Contributors', output)
        self.assertIn('Alice', output)
        self.assertIn('Bob', output)
    
    def test_format_code_stats(self):
        """Test code stats formatting."""
        stats = CodeStats(
            total_files=10,
            total_lines=1000,
            code_lines=700,
            comment_lines=200,
            blank_lines=100,
            languages={'Python': 500, 'JavaScript': 300}
        )
        
        output = format_code_stats(stats)
        self.assertIn('Code Statistics', output)
        self.assertIn('Python', output)
        self.assertIn('1000', output)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases."""
    
    def test_empty_repository(self):
        """Test with fresh empty repository."""
        temp_dir = tempfile.mkdtemp()
        try:
            repo = Repo.init(temp_dir)
            config = repo.config_writer()
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@test.com")
            config.release()
            
            # Create file and commit
            filepath = Path(temp_dir) / "file.txt"
            filepath.write_text("content")
            repo.index.add(["file.txt"])
            repo.index.commit("Initial")
            
            analyzer = GitAnalyzer(temp_dir)
            summary = analyzer.get_repository_summary()
            self.assertEqual(summary['commit_count'], 1)
        finally:
            shutil.rmtree(temp_dir)
    
    def test_binary_file_detection(self):
        """Test binary file detection."""
        temp_dir = tempfile.mkdtemp()
        try:
            repo = Repo.init(temp_dir)
            config = repo.config_writer()
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@test.com")
            config.release()
            
            # Create binary file
            filepath = Path(temp_dir) / "binary.bin"
            with open(filepath, 'wb') as f:
                f.write(b'\x00\x01\x02\x03')
            
            analyzer = GitAnalyzer(temp_dir)
            self.assertTrue(analyzer._is_binary(filepath))
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
