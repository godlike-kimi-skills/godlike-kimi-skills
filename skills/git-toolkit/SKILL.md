---
name: git-toolkit
version: 1.1
description: Robust Git operations with timeout control, network retry, and batch processing.
---

# Git Toolkit v1.1

**Professional Git operations with built-in timeout and retry mechanisms.**

## What's New in v1.1
- Added Git LFS support
- Implemented git bisect automation
- Added PR template generation

## Features

- **Timeout Control**: All operations have configurable timeouts
- **Network Retry**: Auto-retry on network failures
- **Batch Operations**: Check multiple repos at once
- **Quick Status**: Fast status check without network dependency
- **Safe Pull/Push**: With conflict detection and backup

## Usage

### Quick Status (Local Only)

```bash
python D:/kimi/skills/git-toolkit/scripts/git_toolkit.py status [path]
```

Fast local status check, no network required.

### Check Remote Updates

```bash
python D:/kimi/skills/git-toolkit/scripts/git_toolkit.py check-remote [path] [--timeout 5]
```

Check if local is behind remote with timeout protection.

### Safe Pull with Retry

```bash
python D:/kimi/skills/git-toolkit/scripts/git_toolkit.py pull [path] [--retry 3] [--timeout 10]
```

Pull with automatic retry on network failure.

### Safe Push with Retry

```bash
python D:/kimi/skills/git-toolkit/scripts/git_toolkit.py push [path] [--retry 3] [--timeout 10]
```

Push with automatic retry on network failure.

### Batch Check All Repos

```bash
python D:/kimi/skills/git-toolkit/scripts/git_toolkit.py batch-check D:/kimi
```

Check all git repositories in a directory.

### Quick Commit and Push

```bash
python D:/kimi/skills/git-toolkit/scripts/git_toolkit.py commit-push "message" [path]
```

Commit and push in one command with retry.

### Git LFS Support

```bash
# Track large files
python D:/kimi/skills/git-toolkit/scripts/git_toolkit.py lfs-track "*.psd"

# Pull LFS files
python D:/kimi/skills/git-toolkit/scripts/git_toolkit.py lfs-pull
```

### PR Template Generation

```bash
python D:/kimi/skills/git-toolkit/scripts/git_toolkit.py pr-template
```

## Configuration

Default settings in `config.json`:
- timeout: 10 seconds
- retry: 3 attempts
- retry_delay: 5 seconds

## Best Practices

- ✅ Use timeout for all network operations
- ✅ Implement retry with exponential backoff
- ✅ Always verify repository state before operations
- ✅ Use Git LFS for files > 100MB
- ✅ Generate PR templates for consistency
