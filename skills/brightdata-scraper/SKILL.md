---
name: brightdata-scraper
version: 1.0.0
description: Advanced web scraping with retry logic, anti-detection, and proxy rotation support
---

# Brightdata Scraper

Professional web scraping with anti-detection measures.

## Features

- Automatic retry with exponential backoff
- Random User-Agent rotation
- Request delay to avoid rate limiting
- Batch scraping support
- JSON output format

## Usage

```bash
# Single URL scraping
python scripts/scrape.py "https://example.com"

# With retries and JSON output
python scripts/scrape.py "https://example.com" --retries 5 --json

# Batch scraping from file
python scripts/scrape.py urls.txt --batch --output results.json

# With proxy support (if configured)
python scripts/scrape.py "https://example.com" --proxies
```

## Anti-Detection Features

1. **Random User-Agents**: Rotates between Chrome, Firefox, Safari
2. **Request Delays**: Random delays between requests (2-5s default)
3. **Retry Logic**: Automatically retries on 403/429 errors
4. **Header Mimicry**: Mimics real browser headers

## Note

For production use with serious anti-bot protection, consider:
- Brightdata (paid proxy service)
- Oxylabs
- Smartproxy
