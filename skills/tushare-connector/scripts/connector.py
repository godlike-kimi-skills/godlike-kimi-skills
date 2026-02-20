#!/usr/bin/env python3
"""Tushare Connector - China financial data connector"""

import argparse
import json
from datetime import datetime
from pathlib import Path


CONFIG_FILE = Path.home() / '.kimi' / 'config' / 'tushare.json'


def load_config():
    """Load Tushare configuration"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_config(token: str):
    """Save Tushare token"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    config = {
        'token': token,
        'configured_at': datetime.now().isoformat()
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    print("Tushare token configured successfully")


def get_stock_list(market: str = 'A'):
    """Get stock list"""
    # Simulated data
    stocks = [
        {'ts_code': '000001.SZ', 'name': '平安银行', 'market': '主板'},
        {'ts_code': '000002.SZ', 'name': '万科A', 'market': '主板'},
        {'ts_code': '600000.SH', 'name': '浦发银行', 'market': '主板'},
        {'ts_code': '600519.SH', 'name': '贵州茅台', 'market': '主板'},
    ]
    return [s for s in stocks if market in ['A', 'ALL']]


def get_daily_data(ts_code: str, start_date: str):
    """Get daily price data"""
    # Simulated OHLCV data
    return {
        'ts_code': ts_code,
        'start_date': start_date,
        'data': [
            {'trade_date': '20240101', 'open': 10.0, 'high': 10.5, 'low': 9.8, 'close': 10.2, 'vol': 100000},
            {'trade_date': '20240102', 'open': 10.2, 'high': 10.8, 'low': 10.1, 'close': 10.6, 'vol': 120000},
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='Tushare Connector')
    subparsers = parser.add_subparsers(dest='command')
    
    config_parser = subparsers.add_parser('config')
    config_parser.add_argument('--token', required=True)
    
    stocks_parser = subparsers.add_parser('stocks')
    stocks_parser.add_argument('--market', default='A')
    
    daily_parser = subparsers.add_parser('daily')
    daily_parser.add_argument('--code', required=True)
    daily_parser.add_argument('--start', required=True)
    
    args = parser.parse_args()
    
    if args.command == 'config':
        save_config(args.token)
    elif args.command == 'stocks':
        stocks = get_stock_list(args.market)
        print(json.dumps(stocks, indent=2, ensure_ascii=False))
    elif args.command == 'daily':
        data = get_daily_data(args.code, args.start)
        print(json.dumps(data, indent=2))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
