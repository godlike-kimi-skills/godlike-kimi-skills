#!/usr/bin/env python3
"""Mental Model Finder - Suggest models for situations"""
import sys

MODELS = {
    "decision": ["First Principles", "Inversion", "Second-Order Thinking", "Probabilistic Thinking"],
    "problem": ["Root Cause Analysis", "Five Whys", "First Principles"],
    "strategy": ["Second-Order Thinking", "Network Effects", "Compounding", "Opportunity Cost"],
    "risk": ["Margin of Safety", "Probabilistic Thinking", "Inversion", "Scenario Planning"],
    "growth": ["Network Effects", "Compounding", "Feedback Loops", "Virality"],
    "conflict": ["Game Theory", "Incentives", "Seeing the Front", "OODA Loop"],
    "learning": ["Compounding", "Deliberate Practice", "Feedback Loops"],
    "team": ["Incentives", "Alignment", "Specialization", "Trade-offs"]
}

def suggest_models(situation):
    situation = situation.lower()
    suggestions = []
    
    for keyword, models in MODELS.items():
        if keyword in situation:
            suggestions.extend(models)
    
    if not suggestions:
        suggestions = ["First Principles", "Inversion", "Second-Order Thinking"]
    
    return list(set(suggestions))[:5]

def main():
    if len(sys.argv) < 2:
        print("Usage: python model_finder.py '[situation]'")
        print("\nExample situations:")
        for k in MODELS:
            print(f"  - {k}")
        return
    
    situation = sys.argv[1]
    models = suggest_models(situation)
    
    print(f"\n=== Suggested Mental Models for: {situation} ===\n")
    for i, model in enumerate(models, 1):
        print(f"  {i}. {model}")
    print("\nUse /apply [model] to apply a specific model")

if __name__ == "__main__":
    main()
