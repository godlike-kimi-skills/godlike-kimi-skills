# curl-wget-skill

cURL/wget-style HTTP download tool with resume capability, batch downloads, and progress tracking.

Use when scanning networks, managing remote servers, or when user mentions 'SSH', 'DNS', 'network'.

## Overview

This skill provides robust HTTP file downloading capabilities with support for resume, batch operations, and checksum verification.

## Triggers

- "download file"
- "wget"
- "curl"
- "batch download"
- "http download"
- "download from URL"

## Functions

### download(url, **kwargs)

Download a single file from URL.

**Parameters:**
- `url` (str): URL to download
- `output_path` (str): Local save path (optional)
- `resume` (bool): Enable resume capability (default: True)
- `verify_checksum` (str): Expected checksum for verification
- `checksum_algorithm` (str): Hash algorithm (default: "sha256")
- `headers` (dict): Additional HTTP headers
- `timeout` (int): Request timeout in seconds

**Returns:**
Dictionary with download status, file info, and metrics.

### batch_download(urls, **kwargs)

Download multiple files concurrently.

**Parameters:**
- `urls` (list): List of URLs to download
- `output_dir` (str): Output directory (default: ".")
- `max_concurrent` (int): Maximum concurrent downloads (default: 3)
- `resume` (bool): Enable resume capability

**Returns:**
Dictionary with batch results and individual download statuses.

## Examples

```python
# Simple download
download("https://example.com/file.zip")

# Download with custom output
download("https://example.com/file.zip", output_path="/tmp/file.zip")

# Resume interrupted download
download("https://example.com/large.iso", resume=True)

# Verify checksum
download(
    "https://example.com/file.zip",
    verify_checksum="sha256_hash_here"
)

# Batch download
batch_download([
    "https://example.com/1.zip",
    "https://example.com/2.zip"
], output_dir="downloads", max_concurrent=2)
```

## Features

- **Progress Bars**: Visual download progress with tqdm
- **Speed Calculation**: Real-time download speed
- **Retry Logic**: Automatic retry on failure
- **Checksum Support**: SHA256, SHA1, MD5 verification
- **Range Requests**: Server-side resume support
- **Concurrent Downloads**: Parallel file downloads

## Error Handling

The skill handles common errors:
- Network timeouts
- HTTP errors (404, 500, etc.)
- Disk space issues
- Checksum mismatches

## Requirements

- Python 3.8+
- requests, tqdm, aiohttp, aiofiles
