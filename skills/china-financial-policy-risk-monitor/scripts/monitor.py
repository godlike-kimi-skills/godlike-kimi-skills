#!/usr/bin/env python3
"""China Financial Policy Risk Monitor"""

import argparse
import json
from datetime import datetime


POLICY_DB = {
    'monetary': [
        {'date': '2024-02-20', 'policy': '5年期LPR下调25BP至3.95%', 'impact': 'positive'},
        {'date': '2024-01-24', 'policy': '降准0.5个百分点', 'impact': 'positive'},
    ],
    'regulatory': [
        {'date': '2024-01-15', 'policy': '证监会发布减持新规', 'impact': 'neutral'},
        {'date': '2024-01-10', 'policy': '加强IPO审核', 'impact': 'neutral'},
    ],
    'industry': [
        {'date': '2024-02-01', 'policy': '新能源汽车购置税减免延续', 'impact': 'positive', 'sectors': ['新能源汽车']},
        {'date': '2024-01-20', 'policy': '房地产融资协调机制', 'impact': 'positive', 'sectors': ['房地产']},
    ]
}


def get_latest_policies():
    """Get latest policies"""
    all_policies = []
    for category, policies in POLICY_DB.items():
        for p in policies:
            p['category'] = category
            all_policies.append(p)
    
    return sorted(all_policies, key=lambda x: x['date'], reverse=True)


def analyze_sector_impact(sector: str):
    """Analyze policy impact on sector"""
    impacts = []
    for category, policies in POLICY_DB.items():
        for p in policies:
            sectors = p.get('sectors', [])
            if sector in sectors or not sectors:
                impacts.append(p)
    
    return {
        'sector': sector,
        'relevant_policies': impacts,
        'risk_level': 'low' if not impacts else 'medium',
        'recommendation': 'Monitor policy changes'
    }


def set_alert(policy_type: str, keyword: str):
    """Set policy alert"""
    alert = {
        'type': policy_type,
        'keyword': keyword,
        'created_at': datetime.now().isoformat(),
        'status': 'active'
    }
    print(f"Alert set: {json.dumps(alert, indent=2, ensure_ascii=False)}")


def main():
    parser = argparse.ArgumentParser(description='China Financial Policy Risk Monitor')
    subparsers = parser.add_subparsers(dest='command')
    
    subparsers.add_parser('latest')
    
    analyze_parser = subparsers.add_parser('analyze')
    analyze_parser.add_argument('--sector', required=True)
    
    alert_parser = subparsers.add_parser('alert')
    alert_parser.add_argument('--type', required=True)
    alert_parser.add_argument('--keyword', required=True)
    
    args = parser.parse_args()
    
    if args.command == 'latest':
        data = get_latest_policies()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.command == 'analyze':
        data = analyze_sector_impact(args.sector)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.command == 'alert':
        set_alert(args.type, args.keyword)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
