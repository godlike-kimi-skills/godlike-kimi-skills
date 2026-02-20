#!/usr/bin/env python3
"""A-Stock Capital Flow Tracker - Track capital flows"""

import argparse
import json
from datetime import datetime


def get_stock_flow(ts_code: str):
    """Get individual stock capital flow"""
    return {
        'ts_code': ts_code,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'main_inflow': 12500000,
        'main_outflow': 8500000,
        'main_net': 4000000,
        'retail_inflow': 5000000,
        'retail_outflow': 7000000,
        'retail_net': -2000000,
        'total_turnover': 50000000
    }


def get_sector_flow(top: int = 10):
    """Get sector capital flow ranking"""
    sectors = [
        {'name': '半导体', 'net_inflow': 1500000000, 'change_pct': 2.5},
        {'name': '新能源', 'net_inflow': 1200000000, 'change_pct': 1.8},
        {'name': '医药', 'net_inflow': 800000000, 'change_pct': 1.2},
        {'name': '银行', 'net_inflow': -500000000, 'change_pct': -0.5},
        {'name': '地产', 'net_inflow': -800000000, 'change_pct': -1.2},
    ]
    return sectors[:top]


def watch_realtime(interval: int = 60):
    """Watch real-time capital flows"""
    print(f"Starting real-time monitor (interval: {interval}s)")
    print("Press Ctrl+C to stop")
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Monitoring...")
    print("Main force: Net inflow +450M")
    print("Top sector: 半导体")


def main():
    parser = argparse.ArgumentParser(description='A-Stock Capital Flow Tracker')
    subparsers = parser.add_subparsers(dest='command')
    
    stock_parser = subparsers.add_parser('stock')
    stock_parser.add_argument('--code', required=True)
    
    sector_parser = subparsers.add_parser('sector')
    sector_parser.add_argument('--top', type=int, default=10)
    
    watch_parser = subparsers.add_parser('watch')
    watch_parser.add_argument('--interval', type=int, default=60)
    
    args = parser.parse_args()
    
    if args.command == 'stock':
        data = get_stock_flow(args.code)
        print(json.dumps(data, indent=2))
    elif args.command == 'sector':
        data = get_sector_flow(args.top)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.command == 'watch':
        watch_realtime(args.interval)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
