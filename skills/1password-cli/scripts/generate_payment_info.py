#!/usr/bin/env python3
"""
Generate public payment information from 1Password
Retrieves only addresses (not private keys) for customer payment instructions
"""

import json
import subprocess
import sys
from pathlib import Path

def get_from_1password(item_name, field):
    """Retrieve field from 1Password item"""
    try:
        result = subprocess.run(
            ["op", "item", "get", item_name, f"--fields={field}"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Could not retrieve {field} from {item_name}")
        print(f"        Make sure you're signed in: op signin")
        return None
    except FileNotFoundError:
        print("[ERROR] 1Password CLI (op) not found in PATH")
        print("        Please restart your terminal or run: refreshenv")
        return None

def main():
    print("=" * 60)
    print("Kbot Payment Information Generator")
    print("=" * 60)
    print()
    print("Retrieving wallet addresses from 1Password...")
    print()
    
    # Get addresses (safe to share)
    base_address = get_from_1password("Kbot Base Wallet", "address")
    solana_address = get_from_1password("Kbot Solana Wallet", "address")
    
    if not base_address or not solana_address:
        print()
        print("[FALLBACK] Using local wallet file...")
        # Fallback to local file if 1Password not configured
        wallet_file = Path(r"D:\kimi\memory\state\kbot_wallets.json")
        if wallet_file.exists():
            with open(wallet_file, 'r') as f:
                data = json.load(f)
            base_address = data['wallets']['base']['address']
            solana_address = data['wallets']['solana']['address']
        else:
            print("[ERROR] Wallet file not found!")
            sys.exit(1)
    
    # Generate payment info
    print()
    print("=" * 60)
    print("PAYMENT INFORMATION (Safe to Share)")
    print("=" * 60)
    print()
    print("Send USDC to either address:")
    print()
    print(f"[Base]")
    print(f"  Address: {base_address}")
    print(f"  Network: Base Mainnet (Chain ID: 8453)")
    print(f"  Currency: USDC")
    print()
    print(f"[Solana]")
    print(f"  Address: {solana_address}")
    print(f"  Network: Solana Mainnet")
    print(f"  Currency: USDC")
    print()
    print("=" * 60)
    print("Choose whichever network is easier for you!")
    print("=" * 60)
    
    # Save to public file
    payment_info = {
        "note": "PUBLIC PAYMENT INFORMATION - Safe to share with customers",
        "base": {
            "address": base_address,
            "network": "Base Mainnet",
            "chain_id": 8453,
            "currency": "USDC",
            "contract": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        },
        "solana": {
            "address": solana_address,
            "network": "Solana Mainnet",
            "currency": "USDC",
            "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        }
    }
    
    output_file = Path(r"D:\kimi\memory\state\payment_info_public.json")
    with open(output_file, 'w') as f:
        json.dump(payment_info, f, indent=2)
    
    print()
    print(f"[OK] Payment info saved to: {output_file}")

if __name__ == "__main__":
    main()
