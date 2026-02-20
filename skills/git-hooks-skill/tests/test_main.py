#!/usr/bin/env python3
"""
Tests for Git Hooks Skill
"""

import unittest
import sys
import os
import tempfile
import shutil
import stat

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.main import (
    GitHooksManager, HookType, HookConfig,
    CommitMessageConfig
)

class TestHookType(unittest.TestCase):
    
    def test_hook_type_values(self):
        """Test hook type enum values"""
        self.assertEqual(HookType.PRE_COMMIT.value, "pre-commit")
        self.assertEqual(HookType.PRE_PUSH.value, "pre-push")
        self.assertEqual(HookType.COMMIT_MSG.value, "commit-msg")
        self.assertEqual(HookType.POST_CHECKOUT.value, "post-checkout")
        self.assertEqual(HookType.POST_MERGE.value, "post-merge")

class TestCommitMessageConfig(unittest.TestCase):
    
    def test_default_values(self):
        """Test default commit message config"""
        config = CommitMessageConfig()
        self.assertTrue(config.enabled)
        self.assertTrue(config.require_type)
        self.assertFalse(config.require_scope)
        self.assertEqual(config.max_length, 72)
        self.assertEqual(config.min_length, 10)
        self.assertIsNone(config.pattern)
    
    def test_allowed_types(self):
        """Test default allowed types"""
        config = CommitMessageConfig()
        self.assertIn("feat", config.allowed_types)
        self.assertIn("fix", config.allowed_types)
        self.assertIn("docs", config.allowed_types)
    
    def test_custom_types(self):
        """Test custom type configuration"""
        config = CommitMessageConfig(
            allowed_types=["custom", "types"]
        )
        self.assertEqual(config.allowed_types, ["custom", "types"])

class TestGitHooksManager(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        # Initialize git repo
        os.system(f"cd {self.temp_dir} && git init > /dev/null 2>&1")
        self.hooks = GitHooksManager(self.temp_dir)
    
    def tearDown(self):
        os.chdir("/")
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_is_git_repo(self):
        """Test git repo detection"""
        self.assertTrue(self.hooks.is_git_repo())
        self.assertIsNotNone(self.hooks.git_dir)
    
    def test_ensure_directories(self):
        """Test directory creation"""
        hooks_dir = self.hooks.ensure_hooks_dir()
        self.assertTrue(os.path.exists(hooks_dir))
    
    def test_create_hook(self):
        """Test hook creation"""
        content = "#!/bin/sh\necho 'test'"
        hook_path = self.hooks.create_hook(HookType.PRE_COMMIT, content)
        
        self.assertTrue(os.path.exists(hook_path))
        with open(hook_path, 'r') as f:
            self.assertEqual(f.read(), content)
    
    def test_create_hook_executable(self):
        """Test hook is made executable"""
        content = "#!/bin/sh\necho 'test'"
        hook_path = self.hooks.create_hook(HookType.PRE_COMMIT, content)
        
        self.assertTrue(os.access(hook_path, os.X_OK))
    
    def test_read_hook(self):
        """Test reading hook content"""
        content = "#!/bin/sh\necho 'test'"
        self.hooks.create_hook(HookType.PRE_COMMIT, content)
        
        read_content = self.hooks.read_hook(HookType.PRE_COMMIT)
        self.assertEqual(read_content, content)
    
    def test_read_nonexistent_hook(self):
        """Test reading non-existent hook"""
        content = self.hooks.read_hook(HookType.PRE_REBASE)
        self.assertIsNone(content)
    
    def test_delete_hook(self):
        """Test hook deletion"""
        content = "#!/bin/sh\necho 'test'"
        self.hooks.create_hook(HookType.PRE_COMMIT, content)
        
        result = self.hooks.delete_hook(HookType.PRE_COMMIT)
        self.assertTrue(result)
        
        hook_path = self.hooks.get_hook_path(HookType.PRE_COMMIT)
        self.assertFalse(os.path.exists(hook_path))
    
    def test_delete_nonexistent_hook(self):
        """Test deleting non-existent hook"""
        result = self.hooks.delete_hook(HookType.PRE_REBASE)
        self.assertFalse(result)
    
    def test_enable_hook(self):
        """Test enabling hook"""
        content = "#!/bin/sh\necho 'test'"
        hook_path = self.hooks.create_hook(HookType.PRE_COMMIT, content, make_executable=False)
        
        # Make non-executable first
        os.chmod(hook_path, stat.S_IRUSR | stat.S_IWUSR)
        self.assertFalse(os.access(hook_path, os.X_OK))
        
        # Enable
        result = self.hooks.enable_hook(HookType.PRE_COMMIT)
        self.assertTrue(result)
        self.assertTrue(os.access(hook_path, os.X_OK))
    
    def test_disable_hook(self):
        """Test disabling hook"""
        content = "#!/bin/sh\necho 'test'"
        self.hooks.create_hook(HookType.PRE_COMMIT, content)
        
        result = self.hooks.disable_hook(HookType.PRE_COMMIT)
        self.assertTrue(result)
        
        hook_path = self.hooks.get_hook_path(HookType.PRE_COMMIT)
        self.assertFalse(os.access(hook_path, os.X_OK))
    
    def test_list_hooks(self):
        """Test listing hooks"""
        # Create some hooks
        self.hooks.create_hook(HookType.PRE_COMMIT, "#!/bin/sh")
        self.hooks.create_hook(HookType.PRE_PUSH, "#!/bin/sh")
        
        hooks = self.hooks.list_hooks()
        
        self.assertIn("pre-commit", hooks)
        self.assertIn("pre-push", hooks)
        self.assertTrue(hooks["pre-commit"]["executable"])
    
    def test_create_pre_commit_hook(self):
        """Test pre-commit hook creation"""
        path = self.hooks.create_pre_commit_hook(
            lint_cmd="flake8 .",
            test_cmd="pytest"
        )
        
        self.assertTrue(os.path.exists(path))
        content = self.hooks.read_hook(HookType.PRE_COMMIT)
        self.assertIn("flake8", content)
        self.assertIn("pytest", content)
    
    def test_create_pre_push_hook(self):
        """Test pre-push hook creation"""
        path = self.hooks.create_pre_push_hook(
            test_cmd="pytest --cov"
        )
        
        self.assertTrue(os.path.exists(path))
        content = self.hooks.read_hook(HookType.PRE_PUSH)
        self.assertIn("pytest --cov", content)
    
    def test_create_commit_msg_hook(self):
        """Test commit-msg hook creation"""
        config = CommitMessageConfig(
            allowed_types=["feat", "fix"],
            require_scope=True
        )
        path = self.hooks.create_commit_msg_hook(config)
        
        self.assertTrue(os.path.exists(path))
        content = self.hooks.read_hook(HookType.COMMIT_MSG)
        self.assertIn("feat", content)
        self.assertIn("fix", content)
    
    def test_test_commit_msg_valid(self):
        """Test commit message validation - valid"""
        config = CommitMessageConfig()
        
        # Valid message
        result = self.hooks.test_commit_msg("feat(auth): add login", config)
        self.assertTrue(result)
    
    def test_test_commit_msg_invalid_length(self):
        """Test commit message validation - invalid length"""
        config = CommitMessageConfig(min_length=20, max_length=50)
        
        # Too short
        result = self.hooks.test_commit_msg("fix: bug", config)
        self.assertFalse(result)
        
        # Too long
        result = self.hooks.test_commit_msg("feat: " + "x" * 100, config)
        self.assertFalse(result)
    
    def test_test_commit_msg_invalid_type(self):
        """Test commit message validation - invalid type"""
        config = CommitMessageConfig(
            allowed_types=["feat", "fix"],
            require_type=True
        )
        
        result = self.hooks.test_commit_msg("invalid: message", config)
        self.assertFalse(result)
    
    def test_generate_sample_hooks(self):
        """Test sample hooks generation"""
        created = self.hooks.generate_sample_hooks()
        
        self.assertGreater(len(created), 0)
        
        # Check that hooks were created
        hooks = self.hooks.list_hooks()
        self.assertGreater(len(hooks), 0)

class TestHookConfig(unittest.TestCase):
    
    def test_initialization(self):
        """Test hook configuration initialization"""
        config = HookConfig(
            hook_type=HookType.PRE_COMMIT,
            enabled=True,
            command="pytest",
            use_python=False
        )
        
        self.assertEqual(config.hook_type, HookType.PRE_COMMIT)
        self.assertTrue(config.enabled)
        self.assertEqual(config.command, "pytest")
        self.assertFalse(config.use_python)
        self.assertTrue(config.fail_on_error)

if __name__ == "__main__":
    unittest.main()
