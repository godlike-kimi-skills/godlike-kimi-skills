#!/usr/bin/env python3
"""
Reasoning Tools Quick Reference
Quick lookup for 523 reasoning tools across 34 domains
"""

import sys

DOMAINS = {
    "decision": ["Bayesian Statistics", "Meteorology", "Intelligence Analysis", "Emergency Medicine"],
    "persuasion": ["Game Theory (Signaling)", "Social Psychology", "Classical Rhetoric"],
    "creative": ["Design Thinking", "Evolutionary Biology"],
    "systems": ["System Dynamics", "Network Science", "Ecology", "Accident Investigation"],
    "learning": ["Learning Theory", "Sports Science", "Expertise Studies"],
    "coordination": ["Mechanism Design", "Organizational Behavior", "Constitutional Design"],
    "truth": ["Formal Verification", "Experimental Design", "Investigative Journalism", "Logic & Critical Thinking"],
    "conflict": ["Military Strategy", "Competitive Game Theory", "Litigation Strategy"],
    "resources": ["Economics", "Information Economics", "Behavioral Economics", "Operations Research", "Portfolio Management", "Distributive Justice"],
    "patterns": ["Machine Learning", "Medical Diagnostics"]
}

QUICK_TOOLS = {
    "decision": ["Base Rate Integration", "Expected Value", "Minimax", "Satisficing"],
    "problem": ["Root Cause Analysis", "Five Whys", "Fishbone Diagram", "First Principles"],
    "creativity": ["Lateral Thinking", "Morphological Analysis", "SCAMPER", "Analogical Reasoning"],
    "analysis": ["Red Teaming", "Pre-Mortem", "Devil's Advocate", "Steelmanning"]
}

def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_ref.py [domain|tool]")
        print("\nAvailable domains:")
        for key in DOMAINS:
            print(f"  - {key}")
        print("\nQuick tools:")
        for key in QUICK_TOOLS:
            print(f"  - {key}")
        return
    
    query = sys.argv[1].lower()
    
    # Search domains
    for key, tools in DOMAINS.items():
        if query in key:
            print(f"\n=== {key.upper()} ===")
            for tool in tools:
                print(f"  • {tool}")
    
    # Search quick tools
    for key, tools in QUICK_TOOLS.items():
        if query in key:
            print(f"\n=== {key.upper()} TOOLS ===")
            for tool in tools:
                print(f"  • {tool}")

if __name__ == "__main__":
    main()
