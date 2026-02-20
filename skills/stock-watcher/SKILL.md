---
name: stock-watcher
description: Stock market monitoring and watchlist management. Use when tracking stocks, monitoring prices, or managing investment watchlists.
---

# Stock Watcher

Stock market monitoring and watchlist.

## Features

- Track stock prices
- Manage watchlists
- Price alerts
- Performance summary

## Usage

```bash
# Add stock to watchlist
python D:/kimi/skills/stock-watcher/scripts/stock.py add 000001

# Check prices
python D:/kimi/skills/stock-watcher/scripts/stock.py check

# Performance summary
python D:/kimi/skills/stock-watcher/scripts/stock.py summary

# Set alert
python D:/kimi/skills/stock-watcher/scripts/stock.py alert 000001 --above 10.5
```

## Data Source

Uses 10jqka.com.cn for A-shares.
