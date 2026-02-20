#!/usr/bin/env python3
"""
Check USDC payments for Kbot wallets
Supports Base and Solana networks
"""

import json
import requests
import sys
from datetime import datetime, timedelta

# Wallet addresses
BASE_ADDRESS = "0xf94a193585df05B083152171BbD526B8FeD3F8B6"
SOLANA_ADDRESS = "5VnAZyLJMxJkPhDWSX99UPNuyz8Y1hXJJa558WHHSCtW"

# USDC contracts
BASE_USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
SOLANA_USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"


def check_base_payments(min_amount=0.1, hours_back=24):
    """
    Check Base network for USDC payments
    Uses Basescan API (free tier available)
    """
    try:
        # Note: This uses public API, for production use API key
        url = f"https://api.basescan.org/api"
        params = {
            "module": "account",
            "action": "tokentx",
            "address": BASE_ADDRESS,
            "contractaddress": BASE_USDC,
            "sort": "desc",
        }
        
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        
        if data.get("status") != "1":
            return {"error": data.get("message", "API error")}
        
        transactions = data.get("result", [])
        payments = []
        
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        for tx in transactions:
            if tx.get("to", "").lower() != BASE_ADDRESS.lower():
                continue  # Not incoming
            
            # Parse amount (USDC has 6 decimals)
            amount_raw = int(tx.get("value", 0))
            amount = amount_raw / 1_000_000
            
            if amount < min_amount:
                continue
            
            # Parse timestamp
            tx_time = datetime.fromtimestamp(int(tx.get("timeStamp", 0)))
            if tx_time < cutoff_time:
                continue
            
            payments.append({
                "network": "base",
                "tx_hash": tx.get("hash"),
                "from": tx.get("from"),
                "amount": amount,
                "timestamp": tx_time.isoformat(),
                "confirmations": int(tx.get("confirmations", 0)),
            })
        
        return {
            "success": True,
            "address": BASE_ADDRESS,
            "payments": payments,
            "total_received": sum(p["amount"] for p in payments),
        }
        
    except Exception as e:
        return {"error": str(e)}


def check_solana_payments(min_amount=0.1, hours_back=24):
    """
    Check Solana for USDC payments
    Uses Solscan API (free)
    """
    try:
        url = f"https://api.solscan.io/account/transactions"
        params = {
            "address": SOLANA_ADDRESS,
            "limit": 50,
        }
        
        headers = {
            "Accept": "application/json",
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        data = response.json()
        
        if not data.get("success"):
            return {"error": "API error"}
        
        transactions = data.get("data", [])
        payments = []
        
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        for tx in transactions:
            # Check if it's a token transfer
            if tx.get("parsedInstructions"):
                for instruction in tx["parsedInstructions"]:
                    if instruction.get("type") == "spl-transfer":
                        # Check if USDC
                        token_address = instruction.get("params", {}).get("tokenAddress")
                        if token_address != SOLANA_USDC:
                            continue
                        
                        # Check if incoming
                        destination = instruction.get("params", {}).get("destination")
                        if destination != SOLANA_ADDRESS:
                            continue
                        
                        # Parse amount (USDC has 6 decimals)
                        amount_raw = float(instruction.get("params", {}).get("amount", 0))
                        amount = amount_raw / 1_000_000
                        
                        if amount < min_amount:
                            continue
                        
                        # Parse timestamp
                        tx_time = datetime.fromtimestamp(tx.get("blockTime", 0))
                        if tx_time < cutoff_time:
                            continue
                        
                        payments.append({
                            "network": "solana",
                            "tx_hash": tx.get("txHash"),
                            "from": instruction.get("params", {}).get("source"),
                            "amount": amount,
                            "timestamp": tx_time.isoformat(),
                            "status": tx.get("status"),
                        })
        
        return {
            "success": True,
            "address": SOLANA_ADDRESS,
            "payments": payments,
            "total_received": sum(p["amount"] for p in payments),
        }
        
    except Exception as e:
        return {"error": str(e)}


def main():
    print("=" * 60)
    print("Kbot Payment Checker")
    print("=" * 60)
    print(f"Time: {datetime.now()}")
    print()
    
    # Check Base
    print("[1/2] Checking Base network...")
    base_result = check_base_payments(min_amount=0.1, hours_back=24)
    
    if base_result.get("success"):
        print(f"  Address: {base_result['address'][:20]}...")
        print(f"  Payments (24h): {len(base_result['payments'])}")
        print(f"  Total received: {base_result['total_received']:.2f} USDC")
        for p in base_result['payments'][:3]:  # Show first 3
            print(f"    - {p['amount']:.2f} USDC from {p['from'][:10]}...")
    else:
        print(f"  Error: {base_result.get('error')}")
    
    print()
    
    # Check Solana
    print("[2/2] Checking Solana network...")
    solana_result = check_solana_payments(min_amount=0.1, hours_back=24)
    
    if solana_result.get("success"):
        print(f"  Address: {solana_result['address'][:20]}...")
        print(f"  Payments (24h): {len(solana_result['payments'])}")
        print(f"  Total received: {solana_result['total_received']:.2f} USDC")
        for p in solana_result['payments'][:3]:
            print(f"    - {p['amount']:.2f} USDC from {p['from'][:10]}...")
    else:
        print(f"  Error: {solana_result.get('error')}")
    
    print()
    print("=" * 60)
    total = base_result.get("total_received", 0) + solana_result.get("total_received", 0)
    print(f"Total revenue (24h): {total:.2f} USDC")
    print("=" * 60)


if __name__ == "__main__":
    main()
