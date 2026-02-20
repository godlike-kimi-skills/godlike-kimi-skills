#!/usr/bin/env python3
"""Check wallet balances"""
import sys, json, urllib.request, os

def get_solana_balance(address):
    try:
        url = "https://api.mainnet-beta.solana.com"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [address]
        }
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            lamports = result['result']['value']
            return lamports / 1e9  # Convert to SOL
    except Exception as e:
        return {"error": str(e)}

def get_solana_usdc(address):
    try:
        url = "https://api.mainnet-beta.solana.com"
        usdc = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [address, {"mint": usdc}, {"encoding": "jsonParsed"}]
        }
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            total = 0
            for acc in result['result']['value']:
                amount = acc['account']['data']['parsed']['info']['tokenAmount']['uiAmount']
                total += amount
            return total
    except:
        return 0

if __name__ == "__main__":
    sol_addr = os.getenv('SOLANA_WALLET_ADDRESS', '5VnAZyLJMxJkPhDWSX99UPNuyz8Y1hXJJa558WHHSCtW')
    
    print(json.dumps({
        "solana_address": sol_addr,
        "sol_balance": get_solana_balance(sol_addr),
        "usdc_balance": get_solana_usdc(sol_addr)
    }, indent=2))
