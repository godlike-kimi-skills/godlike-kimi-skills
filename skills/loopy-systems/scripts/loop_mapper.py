#!/usr/bin/env python3
"""
System Loop Mapper
Identify and analyze feedback loops in systems
"""

import sys

def identify_loop(variables, relationships):
    """
    Identify feedback loop type
    
    variables: list of system variables
    relationships: dict of {var: [(related_var, sign)]}
                   sign: + for same direction, - for opposite
    """
    # Count negative relationships in loop
    negative_count = sum(1 for rels in relationships.values() 
                        for _, sign in rels if sign == '-')
    
    if negative_count == 0:
        return "Reinforcing (R) - Amplifies change"
    elif negative_count % 2 == 1:
        return "Balancing (B) - Stabilizes system"
    else:
        return "Complex - Multiple feedback paths"

def main():
    if len(sys.argv) < 2:
        print("Usage: python loop_mapper.py [system_type]")
        print("\nSystem types:")
        print("  - growth: Viral growth loop")
        print("  - cost: Cost constraint loop")
        print("  - market: Market saturation loop")
        print("  - reinvest: Reinvestment loop")
        return
    
    system = sys.argv[1].lower()
    
    systems = {
        "growth": {
            "vars": ["Users", "Network Value", "Referrals", "New Users"],
            "loop": "Reinforcing (R)",
            "effect": "Exponential growth",
            "leverage": "Viral coefficient"
        },
        "cost": {
            "vars": ["Revenue", "Costs", "Margin", "Efficiency Focus"],
            "loop": "Balancing (B)",
            "effect": "Profitability enforcement",
            "leverage": "Automation"
        },
        "market": {
            "vars": ["Market Share", "Remaining Market", "Growth Rate"],
            "loop": "Balancing (B)",
            "effect": "Growth ceiling",
            "leverage": "New markets"
        },
        "reinvest": {
            "vars": ["Revenue", "Investment", "Capability", "Quality"],
            "loop": "Reinforcing (R)",
            "effect": "Compound improvement",
            "leverage": "ROI on investment"
        }
    }
    
    if system in systems:
        s = systems[system]
        print(f"\n=== {system.upper()} LOOP ===")
        print(f"Variables: {' → '.join(s['vars'])} → [back to start]")
        print(f"Type: {s['loop']}")
        print(f"Effect: {s['effect']}")
        print(f"Leverage Point: {s['leverage']}")
    else:
        print(f"Unknown system type: {system}")

if __name__ == "__main__":
    main()
