#!/usr/bin/env python3
"""AkShare Connector - Open source financial data"""

import argparse
import json
from datetime import datetime


def get_a_spot():
    """Get A-share real-time quotes"""
    # Simulated data
    return [
        {'code': '000001', 'name': '平安银行', 'price': 10.25, 'change': 0.05, 'change_pct': 0.49},
        {'code': '000002', 'name': '万科A', 'price': 15.30, 'change': -0.20, 'change_pct': -1.29},
        {'code': '600519', 'name': '贵州茅台', 'price': 1680.00, 'change': 15.00, 'change_pct': 0.90},
    ]


def get_stock_history(code: str, period: str = 'daily'):
    """Get stock historical data"""
    return {
        'code': code,
        'period': period,
        'data': [
            {'date': '2024-01-01', 'open': 10.0, 'close': 10.2, 'high': 10.5, 'low': 9.8, 'volume': 100000},
            {'date': '2024-01-02', 'open': 10.2, 'close': 10.6, 'high': 10.8, 'low': 10.1, 'volume': 120000},
        ]
    }


def get_macro_indicator(indicator: str):
    """Get macroeconomic indicators"""
    indicators = {
        'GDP': {'value': '126.06万亿', 'growth': '5.2%', 'period': '2024 Q1'},
        'CPI': {'value': '102.1', 'change': '0.2%', 'period': '2024-01'},
        'PPI': {'value': '98.5', 'change': '-2.5%', 'period': '2024-01'},
    }
    return indicators.get(indicator, {'error': 'Indicator not found'})


def main():
    parser = argparse.ArgumentParser(description='AkShare Connector')
    subparsers = parser.add_subparsers(dest='command')
    
    spot_parser = subparsers.add_parser('spot')
    spot_parser.add_argument('--market', default='A')
    
    history_parser = subparsers.add_parser('history')
    history_parser.add_argument('--code', required=True)
    history_parser.add_argument('--period', default='daily')
    
    macro_parser = subparsers.add_parser('macro')
    macro_parser.add_argument('--indicator', required=True)
    
    args = parser.parse_args()
    
    if args.command == 'spot':
        data = get_a_spot()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.command == 'history':
        data = get_stock_history(args.code, args.period)
        print(json.dumps(data, indent=2))
    elif args.command == 'macro':
        data = get_macro_indicator(args.indicator)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
