#!/usr/bin/env python3
"""Check airdrop opportunities"""
import json

OPPORTUNITIES = [
    {"name": "Ink Network", "reward": "$100-800", "action": "Daily GM on Discord"},
    {"name": "MarginFi", "reward": "$300-1500", "action": "Deposit SOL"},
    {"name": "Drift Protocol", "reward": "$200-1000", "action": "Trade volume"},
    {"name": "Kamino Finance", "reward": "$200-800", "action": "Lend/Borrow"},
    {"name": "Jupiter", "reward": "$500-2000", "action": "Swap & Stake"}
]

if __name__ == "__main__":
    print(json.dumps({"opportunities": OPPORTUNITIES, "total": len(OPPORTUNITIES)}, indent=2))
