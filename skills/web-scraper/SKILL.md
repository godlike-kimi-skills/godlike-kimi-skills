---
name: web-scraper
version: 1.0.0
description: Lightweight web scraping for AI agents - Check web pages without API access
---

# Web Scraper Skill

Simple web scraping for Kbot to check web pages when APIs are not available.

## Use Cases
- Check Moltbook web page for replies
- Monitor competitor pricing
- Extract data from websites

## Tools
- Python requests + BeautifulSoup (static sites)
- Playwright (dynamic/JavaScript sites)

## Usage

```bash
# Basic page check
python scripts/scrape.py --url "https://example.com"

# Extract specific content
python scripts/scrape.py --url "URL" --selector ".content"

# Check for new content
python scripts/scrape.py --url "URL" --compare
```
