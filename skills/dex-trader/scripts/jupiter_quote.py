#!/usr/bin/env python3
"""Get Jupiter DEX quotes"""
import sys, json, urllib.request

def get_quote(input_mint, output_mint, amount):
    try:
        url = f"https://quote-api.jup.ag/v6/quote?inputMint={input_mint}&outputMint={output_mint}&amount={amount}&slippageBps=100"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # SOL -> USDC
    sol = "So11111111111111111111111111111111111111112"
    usdc = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    result = get_quote(sol, usdc, 1000000000)  # 1 SOL
    print(json.dumps(result, indent=2))
