# Git Hooks Guide

## Table of Contents
1. [Hook Types](#hook-types)
2. [Pre-commit Hooks](#pre-commit)
3. [Commit Message Validation](#commit-msg)
4. [Husky Integration](#husky)
5. [Best Practices](#best-practices)

## Hook Types <a name="hook-types"></a>

### Client-Side Hooks
| Hook | Timing | Use Case |
|------|--------|----------|
| pre-commit | Before commit | Lint, format, quick tests |
| prepare-commit-msg | Before editor | Modify default message |
| commit-msg | After message | Validate message format |
| post-commit | After commit | Notifications, metrics |
| pre-rebase | Before rebase | Prevent rebasing shared branches |
| post-checkout | After checkout | Setup environment |
| post-merge | After merge | Install dependencies |
| pre-push | Before push | Full test suite, security scans |

### Exit Codes
- **0**: Success, continue operation
- **Non-zero**: Failure, abort operation

## Pre-commit Hooks <a name="pre-commit"></a>

### Linting Example
```bash
#!/bin/sh
# Run flake8 on Python files
changed_python_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -n "$changed_python_files" ]; then
    flake8 $changed_python_files
    if [ $? -ne 0 ]; then
        echo "Linting failed. Fix errors before committing."
        exit 1
    fi
fi
```

### Running Tests
```bash
#!/bin/sh
# Run relevant tests
pytest tests/ -x --tb=short
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

### Secret Detection
```bash
#!/bin/sh
# Check for potential secrets
git diff --cached --name-only | xargs git secrets --scan
if [ $? -ne 0 ]; then
    echo "Potential secrets detected!"
    exit 1
fi
```

## Commit Message Validation <a name="commit-msg"></a>

### Conventional Commits Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **style**: Formatting, missing semi colons, etc
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Performance improvement
- **test**: Adding tests
- **chore**: Build process or auxiliary tool changes

### Validation Script
```bash
#!/bin/sh
commit_msg_file=$1
commit_msg=$(cat $commit_msg_file)

# Check format
if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|perf|test|chore)(\(.+\))?: .+"; then
    echo "Invalid commit message format."
    echo "Expected: <type>(<scope>): <subject>"
    exit 1
fi

# Check length
subject=$(echo "$commit_msg" | head -1)
if [ ${#subject} -gt 72 ]; then
    echo "Subject line too long (max 72 characters)"
    exit 1
fi
```

## Husky Integration <a name="husky"></a>

### Husky v7+ Setup
```bash
# Install Husky
npx husky-init && npm install

# Add hooks
npx husky add .husky/pre-commit "npm test"
npx husky add .husky/commit-msg 'npx --no-install commitlint --edit "$1"'
```

### package.json Configuration
```json
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged",
      "commit-msg": "commitlint -E HUSKY_GIT_PARAMS"
    }
  },
  "lint-staged": {
    "*.js": ["eslint --fix", "git add"],
    "*.py": ["flake8", "black"]
  }
}
```

### Lint-Staged Configuration
```javascript
// lint-staged.config.js
module.exports = {
  '*.js': ['eslint --fix', 'prettier --write'],
  '*.py': ['flake8', 'black'],
  '*.{json,md}': ['prettier --write']
};
```

## Best Practices <a name="best-practices"></a>

### Do's
1. **Keep hooks fast**: Aim for < 5 seconds for pre-commit
2. **Fail early**: Exit on first error
3. **Be informative**: Print helpful error messages
4. **Use absolute paths**: Avoid PATH issues
5. **Test hooks**: Run them manually before relying on them

### Don'ts
1. **Don't run full test suite in pre-commit**: Use pre-push instead
2. **Don't modify files without notifying**: User should know what changed
3. **Don't use hooks for CI/CD**: Use proper CI pipelines
4. **Don't block for too long**: Consider async checks for slow operations

### Performance Tips
```bash
#!/bin/sh
# Only check changed files
changed_files=$(git diff --cached --name-only --diff-filter=ACM)

# Run tools only on relevant files
python_files=$(echo "$changed_files" | grep '\.py$' || true)
if [ -n "$python_files" ]; then
    flake8 $python_files
fi
```

### Skipping Hooks
```bash
# Skip all hooks
git commit --no-verify -m "WIP"

# Skip specific hook (Husky)
HUSKY=0 git commit -m "WIP"
```

### Debugging Hooks
```bash
#!/bin/sh
# Add debug output
set -x

# Your hook logic here

echo "Hook completed with exit code $?"
```

### Shared Hooks
For team-wide hooks, consider:
1. **Template directory**: `git config --global init.templateDir ~/.git-template`
2. **Symlink approach**: Link to shared hook directory
3. **Git LFS**: For version-controlled hooks

### Windows Compatibility
```bash
#!/bin/sh
# Use sh for cross-platform compatibility
# Avoid bash-specific features
# Use forward slashes in paths
```
