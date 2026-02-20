# curl-wget-skill

cURL/wget-style HTTP download tool with resume capability, batch downloads, and progress tracking.

Use when scanning networks, managing remote servers, or when user mentions 'SSH', 'DNS', 'network'.

## Features

- **Single File Downloads**: HTTP/HTTPS file downloads
- **Batch Downloads**: Download multiple files concurrently
- **Resume Capability**: Continue interrupted downloads
- **Progress Tracking**: Visual progress bars with speed metrics
- **Checksum Verification**: SHA256/MD5 verification
- **Async Downloads**: High-performance async downloading
- **Custom Headers**: Support for authentication and custom headers

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### As a Skill

```python
from main import download, batch_download

# Single file download
result = download("https://example.com/file.zip")

# Download with custom output
result = download(
    "https://example.com/file.zip",
    output_path="downloads/file.zip"
)

# Resume download
result = download(
    "https://example.com/large-file.iso",
    resume=True
)

# Batch download
urls = [
    "https://example.com/file1.zip",
    "https://example.com/file2.zip",
    "https://example.com/file3.zip"
]
result = batch_download(urls, output_dir="downloads", max_concurrent=3)
```

### Command Line

```bash
# Basic download
python main.py https://example.com/file.zip

# Download with output path
python main.py https://example.com/file.zip -o /path/to/save.zip

# Resume download
python main.py https://example.com/large-file.iso -c

# Batch download
python main.py -b https://example.com/1.zip https://example.com/2.zip
```

## Configuration

Edit `skill.json` to customize:

```json
{
  "config": {
    "default_timeout": 30,
    "chunk_size": 8192,
    "max_retries": 3,
    "user_agent": "curl-wget-skill/1.0.0"
  }
}
```

## Advanced Usage

```python
from main import CurlWgetSkill

skill = CurlWgetSkill()

# Download with checksum verification
result = skill.download(
    url="https://example.com/file.zip",
    output_path="downloads/file.zip",
    verify_checksum="abc123...",
    checksum_algorithm="sha256"
)

# Custom headers
result = skill.download(
    url="https://example.com/protected/file.zip",
    headers={
        "Authorization": "Bearer token123",
        "Accept": "application/zip"
    }
)
```

## Output Format

```json
{
  "url": "https://example.com/file.zip",
  "status": "success",
  "local_path": "downloads/file.zip",
  "file_size": 10485760,
  "downloaded_size": 10485760,
  "speed": 5242880,
  "time_elapsed": 2.0,
  "checksum": "abc123..."
}
```

## Batch Download Results

```json
{
  "success": true,
  "total": 3,
  "successful": 3,
  "failed": 0,
  "results": [
    {
      "url": "https://example.com/file1.zip",
      "status": "success",
      ...
    }
  ]
}
```

## Testing

```bash
python -m pytest tests/
```

## License

MIT License - See LICENSE file
