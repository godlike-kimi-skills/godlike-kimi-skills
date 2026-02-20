#!/usr/bin/env python3
"""A-Stock Restriction Lifting Tracker"""

import argparse
import json
from datetime import datetime, timedelta
from calendar import monthrange


def get_lifting_calendar(month: str):
    """Get restriction lifting calendar for month"""
    year, mon = map(int, month.split('-'))
    _, days_in_month = monthrange(year, mon)
    
    calendar = []
    base = datetime(year, mon, 1)
    
    # Simulated data
    for day in [5, 12, 18, 25]:
        if day <= days_in_month:
            date = base.replace(day=day)
            calendar.append({
                'date': date.strftime('%Y-%m-%d'),
                'stocks': [
                    {'code': f'{day:06d}.SZ', 'name': f'股票{day}', 'volume': f'{day * 100}万股', 'market_cap': f'{day * 500}万'}
                ]
            })
    
    return calendar


def get_stock_lifting(ts_code: str):
    """Get restriction lifting info for specific stock"""
    return {
        'ts_code': ts_code,
        'upcoming_lifts': [
            {
                'date': '2024-06-15',
                'volume': '5000万股',
                'holders': ['大股东A', '机构B'],
                'market_cap': '2.5亿',
                'impact': '高'
            }
        ],
        'history': [
            {'date': '2023-12-01', 'volume': '3000万股', 'price_change': '-2.5%'}
        ]
    }


def alert_large_lifting(threshold: float):
    """Alert on large restriction lifting"""
    alerts = [
        {'code': '000001.SZ', 'name': '平安银行', 'lift_date': '2024-06-15', 'market_cap': 5.2, 'alert': True},
        {'code': '000002.SZ', 'name': '万科A', 'lift_date': '2024-06-20', 'market_cap': 3.8, 'alert': False},
    ]
    
    triggered = [a for a in alerts if a['market_cap'] >= threshold]
    return {
        'threshold': f'{threshold}亿',
        'alerts_triggered': len(triggered),
        'stocks': triggered
    }


def main():
    parser = argparse.ArgumentParser(description='A-Stock Restriction Lifting Tracker')
    subparsers = parser.add_subparsers(dest='command')
    
    calendar_parser = subparsers.add_parser('calendar')
    calendar_parser.add_argument('--month', required=True, help='Format: YYYY-MM')
    
    stock_parser = subparsers.add_parser('stock')
    stock_parser.add_argument('--code', required=True)
    
    alert_parser = subparsers.add_parser('alert')
    alert_parser.add_argument('--threshold', type=float, required=True, help='In 亿')
    
    args = parser.parse_args()
    
    if args.command == 'calendar':
        data = get_lifting_calendar(args.month)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.command == 'stock':
        data = get_stock_lifting(args.code)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.command == 'alert':
        data = alert_large_lifting(args.threshold)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
