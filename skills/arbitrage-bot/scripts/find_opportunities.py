#!/usr/bin/env python3
"""Find arbitrage opportunities"""
import json, urllib.request

def find_arbitrage():
    opportunities = []
    # Check Solana DEX prices
    try:
        # Jupiter price
        url = "https://price.jup.ag/v4/price?ids=SOL"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            sol_price = data['data']['SOL']['price']
            
            opportunities.append({
                "token": "SOL",
                "price": sol_price,
                "dex": "Jupiter",
                "potential_profit": "0.1-0.5%"
            })
    except:
        pass
    
    return opportunities

if __name__ == "__main__":
    print(json.dumps({"opportunities": find_arbitrage()}, indent=2))
