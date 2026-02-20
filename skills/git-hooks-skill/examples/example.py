#!/usr/bin/env python3
"""
Git Hooks Skill Usage Examples
"""

import sys
import os
import tempfile
import shutil

sys.path.insert(0, '..')

from scripts.main import GitHooksManager, HookType, CommitMessageConfig

def example_basic_setup():
    """Demonstrate basic hook setup"""
    # Create a temporary git repo for demonstration
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    os.system("git init")
    
    hooks = GitHooksManager(temp_dir)
    
    print(f"Is git repo: {hooks.is_git_repo()}")
    print(f"Git directory: {hooks.git_dir}")
    print(f"Hooks directory: {hooks.hooks_dir}")
    
    # Cleanup
    os.chdir("/")
    shutil.rmtree(temp_dir)

def example_create_pre_commit():
    """Demonstrate pre-commit hook creation"""
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    os.system("git init")
    
    hooks = GitHooksManager(temp_dir)
    
    # Create pre-commit hook with linting and tests
    hook_path = hooks.create_pre_commit_hook(
        lint_cmd="echo 'Running linter...' && exit 0",
        test_cmd="echo 'Running tests...' && exit 0",
        secret_check="echo 'Checking for secrets...' && exit 0"
    )
    
    print(f"Created pre-commit hook: {hook_path}")
    
    # Read hook content
    content = hooks.read_hook(HookType.PRE_COMMIT)
    print(f"\nHook content preview:\n{content[:500]}...")
    
    # Cleanup
    os.chdir("/")
    shutil.rmtree(temp_dir)

def example_create_pre_push():
    """Demonstrate pre-push hook creation"""
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    os.system("git init")
    
    hooks = GitHooksManager(temp_dir)
    
    # Create pre-push hook
    hook_path = hooks.create_pre_push_hook(
        test_cmd="echo 'Running full test suite...' && exit 0",
        branch_check="echo 'Checking branch protection...' && exit 0"
    )
    
    print(f"Created pre-push hook: {hook_path}")
    
    # Cleanup
    os.chdir("/")
    shutil.rmtree(temp_dir)

def example_commit_message_validation():
    """Demonstrate commit message validation"""
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    os.system("git init")
    
    hooks = GitHooksManager(temp_dir)
    
    # Create commit message validator
    config = CommitMessageConfig(
        allowed_types=["feat", "fix", "docs", "style", "refactor"],
        require_scope=True,
        max_length=72,
        min_length=10
    )
    
    hook_path = hooks.create_commit_msg_hook(config)
    print(f"Created commit-msg hook: {hook_path}")
    
    # Test various messages
    test_messages = [
        "feat(auth): add login functionality",
        "fix: resolve bug",  # Too short
        "invalid message",  # Wrong format
        "feat: add feature without scope",  # Missing scope
        "docs(readme): update installation instructions with detailed steps"
    ]
    
    print("\nTesting commit messages:")
    for msg in test_messages:
        is_valid = hooks.test_commit_msg(msg, config)
        status = "✓ Valid" if is_valid else "✗ Invalid"
        print(f"  {status}: {msg}")
    
    # Cleanup
    os.chdir("/")
    shutil.rmtree(temp_dir)

def example_hook_management():
    """Demonstrate hook management (enable/disable/delete)"""
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    os.system("git init")
    
    hooks = GitHooksManager(temp_dir)
    
    # Create some hooks
    hooks.create_pre_commit_hook()
    hooks.create_pre_push_hook()
    
    # List hooks
    print("Created hooks:")
    all_hooks = hooks.list_hooks()
    for name, info in all_hooks.items():
        print(f"  - {name}: {info['size']} bytes")
    
    # Disable a hook
    hooks.disable_hook(HookType.PRE_COMMIT)
    print("\nDisabled pre-commit hook")
    
    # Check status
    hook_info = all_hooks.get("pre-commit", {})
    print(f"Executable: {hook_info.get('executable', False)}")
    
    # Re-enable
    hooks.enable_hook(HookType.PRE_COMMIT)
    print("Re-enabled pre-commit hook")
    
    # Delete a hook
    hooks.delete_hook(HookType.PRE_PUSH)
    print("Deleted pre-push hook")
    
    # List remaining hooks
    print("\nRemaining hooks:")
    remaining = hooks.list_hooks()
    for name in remaining:
        print(f"  - {name}")
    
    # Cleanup
    os.chdir("/")
    shutil.rmtree(temp_dir)

def example_python_hook():
    """Demonstrate Python-based hook creation"""
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    os.system("git init")
    
    hooks = GitHooksManager(temp_dir)
    
    # Create Python-based pre-commit hook
    hook_path = hooks.create_pre_commit_hook(
        lint_cmd="flake8 .",
        test_cmd="pytest tests/",
        use_python=True
    )
    
    print(f"Created Python pre-commit hook: {hook_path}")
    
    content = hooks.read_hook(HookType.PRE_COMMIT)
    print(f"\nHook is Python-based: {'python3' in content}")
    
    # Cleanup
    os.chdir("/")
    shutil.rmtree(temp_dir)

def example_husky_setup():
    """Demonstrate Husky configuration"""
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    os.system("git init")
    os.system("npm init -y")
    
    hooks = GitHooksManager(temp_dir)
    
    # Setup Husky configuration
    config_path = hooks.setup_husky(
        pre_commit="npm run lint && npm test",
        pre_push="npm run test:ci",
        commit_msg="echo 'Validating commit message...'"
    )
    
    print(f"Created Husky config: {config_path}")
    
    # Check if .husky directory was created
    husky_dir = os.path.join(temp_dir, ".husky")
    if os.path.exists(husky_dir):
        print(f"Husky directory created: {husky_dir}")
        hook_files = os.listdir(husky_dir)
        print(f"Hook files: {hook_files}")
    
    # Cleanup
    os.chdir("/")
    shutil.rmtree(temp_dir)

def example_custom_hook():
    """Demonstrate custom hook creation"""
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    os.system("git init")
    
    hooks = GitHooksManager(temp_dir)
    
    # Create custom post-checkout hook
    custom_content = '''#!/bin/sh
# Custom post-checkout hook
echo "Checkout completed!"
echo "Current branch: $(git branch --show-current)"

# Update dependencies if package.json changed
if git diff --name-only HEAD@{1} HEAD | grep -q "package.json"; then
    echo "package.json changed, running npm install..."
    npm install
fi
'''
    
    hook_path = hooks.create_hook(HookType.POST_CHECKOUT, custom_content)
    print(f"Created custom post-checkout hook: {hook_path}")
    
    # Read and verify
    content = hooks.read_hook(HookType.POST_CHECKOUT)
    print(f"Hook contains npm install check: {'npm install' in content}")
    
    # Cleanup
    os.chdir("/")
    shutil.rmtree(temp_dir)

def example_generate_samples():
    """Demonstrate sample hooks generation"""
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    os.system("git init")
    
    hooks = GitHooksManager(temp_dir)
    
    # Generate sample hooks
    created = hooks.generate_sample_hooks()
    
    print(f"Generated {len(created)} sample hooks:")
    for path in created:
        print(f"  - {path}")
    
    # List all hooks
    all_hooks = hooks.list_hooks()
    print(f"\nTotal hooks in repo: {len(all_hooks)}")
    
    # Cleanup
    os.chdir("/")
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("=" * 60)
    print("Git Hooks Skill Examples")
    print("=" * 60)
    
    print("\n1. Basic Setup:")
    example_basic_setup()
    
    print("\n2. Create Pre-commit Hook:")
    example_create_pre_commit()
    
    print("\n3. Create Pre-push Hook:")
    example_create_pre_push()
    
    print("\n4. Commit Message Validation:")
    example_commit_message_validation()
    
    print("\n5. Hook Management:")
    example_hook_management()
    
    print("\n6. Python-based Hook:")
    example_python_hook()
    
    print("\n7. Husky Setup:")
    example_husky_setup()
    
    print("\n8. Custom Hook:")
    example_custom_hook()
    
    print("\n9. Generate Sample Hooks:")
    example_generate_samples()
