#!/usr/bin/env python3
"""China Macro Economic Tracker"""

import argparse
import json
from datetime import datetime


MACRO_DATA = {
    'GDP': {
        '2024 Q1': {'value': 29.63, 'unit': '万亿', 'yoy': 5.3},
        '2023': {'value': 126.06, 'unit': '万亿', 'yoy': 5.2},
    },
    'CPI': {
        '2024-01': {'value': 99.8, 'yoy': -0.8, 'mom': 0.3},
        '2024-02': {'value': 100.7, 'yoy': 0.7, 'mom': 1.0},
    },
    'PPI': {
        '2024-01': {'value': 97.5, 'yoy': -2.5, 'mom': -0.2},
        '2024-02': {'value': 97.8, 'yoy': -2.7, 'mom': -0.2},
    },
    'PMI': {
        '2024-01': {'value': 49.2, 'trend': '收缩'},
        '2024-02': {'value': 49.1, 'trend': '收缩'},
    },
    'M2': {
        '2024-01': {'value': 297.63, 'unit': '万亿', 'yoy': 8.7},
    },
    'LPR': {
        '2024-01': {'1Y': 3.45, '5Y': 3.95},
    }
}


def get_gdp_data(period: str = 'quarterly'):
    """Get GDP data"""
    return MACRO_DATA.get('GDP', {})


def get_cpi_data(start_year: int = 2020):
    """Get CPI data"""
    return MACRO_DATA.get('CPI', {})


def get_m2_data(chart: bool = False):
    """Get M2 money supply data"""
    data = MACRO_DATA.get('M2', {})
    if chart:
        print("M2 Trend Chart (simulated)")
        for period, values in data.items():
            bar = '█' * int(values['value'] / 10)
            print(f"{period}: {bar} {values['value']}{values['unit']}")
    return data


def get_all_macro():
    """Get all macro indicators"""
    return {
        'timestamp': datetime.now().isoformat(),
        'indicators': {
            'GDP': get_gdp_data(),
            'CPI': get_cpi_data(),
            'PPI': MACRO_DATA.get('PPI'),
            'PMI': MACRO_DATA.get('PMI'),
            'M2': get_m2_data(),
            'LPR': MACRO_DATA.get('LPR')
        }
    }


def main():
    parser = argparse.ArgumentParser(description='China Macro Economic Tracker')
    subparsers = parser.add_subparsers(dest='command')
    
    gdp_parser = subparsers.add_parser('gdp')
    gdp_parser.add_argument('--period', default='quarterly')
    
    cpi_parser = subparsers.add_parser('cpi')
    cpi_parser.add_argument('--start', type=int, default=2020)
    
    m2_parser = subparsers.add_parser('m2')
    m2_parser.add_argument('--chart', action='store_true')
    
    subparsers.add_parser('all')
    
    args = parser.parse_args()
    
    if args.command == 'gdp':
        data = get_gdp_data(args.period)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.command == 'cpi':
        data = get_cpi_data(args.start)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.command == 'm2':
        data = get_m2_data(args.chart)
        if not args.chart:
            print(json.dumps(data, indent=2))
    elif args.command == 'all':
        data = get_all_macro()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
