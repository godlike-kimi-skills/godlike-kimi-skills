---
name: doc-fetcher
description: Fetch and summarize documentation from URLs. Use when the user needs to read documentation from a website, understand API docs, get information from a webpage, or summarize web content for software development.
---

# Doc Fetcher

Fetch and summarize web documentation for software development.

## Features

- Fetch web pages and documentation
- Extract main content from pages
- Summarize long documents
- Cache fetched content locally

## Usage

### Fetch a URL

```bash
python D:/kimi/skills/doc-fetcher/scripts/fetch.py <url> [--summary]
```

### Examples

```bash
# Fetch API documentation
python D:/kimi/skills/doc-fetcher/scripts/fetch.py https://api.example.com/docs

# Fetch with summary
python D:/kimi/skills/doc-fetcher/scripts/fetch.py https://docs.python.org/3/library/asyncio.html --summary

# Save to file
python D:/kimi/skills/doc-fetcher/scripts/fetch.py https://example.com/guide --output guide.md
```

## Supported Sites

- Documentation sites (ReadTheDocs, GitBook, etc.)
- API documentation
- GitHub README files
- Technical blogs
- Stack Overflow posts

## Output Formats

- Markdown (default)
- Plain text
- JSON (structured data)
