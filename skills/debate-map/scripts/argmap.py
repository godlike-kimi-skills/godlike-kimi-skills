#!/usr/bin/env python3
"""Argument Mapper - Create structured argument maps"""
import sys

def create_map(claim, pros, cons):
    print(f"\n{'='*50}")
    print(f"CLAIM: {claim}")
    print(f"{'='*50}")
    
    print("\n[SUPPORTING ARGUMENTS]")
    for i, pro in enumerate(pros, 1):
        print(f"  {i}. {pro}")
    
    print("\n[OPPOSING ARGUMENTS]")
    for i, con in enumerate(cons, 1):
        print(f"  {i}. {con}")
    
    print("\n[ANALYSIS]")
    score = len(pros) - len(cons)
    if score > 0:
        print(f"  Score: +{score} (Pro argument stronger)")
    elif score < 0:
        print(f"  Score: {score} (Con argument stronger)")
    else:
        print(f"  Score: 0 (Balanced - need more evidence)")

def main():
    if len(sys.argv) < 2:
        print("Usage: python argmap.py '[claim]'")
        print("\nInteractive mode:")
        claim = input("Claim: ")
        pros = input("Pros (comma-separated): ").split(",")
        cons = input("Cons (comma-separated): ").split(",")
        create_map(claim, [p.strip() for p in pros], [c.strip() for c in cons])
    else:
        print("Argument Mapper - Template:")
        print("  Claim: [Your proposition]")
        print("  Pros: [Evidence for]")
        print("  Cons: [Evidence against]")

if __name__ == "__main__":
    main()
