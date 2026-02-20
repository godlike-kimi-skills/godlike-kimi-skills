#!/usr/bin/env python3
"""Price monitoring"""
import sys, json, urllib.request

def get_price(token_id):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    token = sys.argv[1] if len(sys.argv) > 1 else "solana"
    print(json.dumps(get_price(token), indent=2))
