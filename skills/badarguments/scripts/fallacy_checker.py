#!/usr/bin/env python3
"""
Logical Fallacy Checker
Detect common logical fallacies in arguments
"""

import re
import sys

FALLACIES = {
    "ad_hominem": {
        "patterns": [r"you.*(never|can't|don't|aren't)", r"(idiot|stupid|dumb|ignorant)"],
        "description": "Attacking the person instead of the argument"
    },
    "appeal_authority": {
        "patterns": [r"(expert|doctor|professor|study)\s+says", r"according to.*(authority|expert)"],
        "description": "Citing authority without evidence"
    },
    "false_dichotomy": {
        "patterns": [r"either.*or", r"only two (options|choices|ways)"],
        "description": "Presenting only two options when more exist"
    },
    "hasty_generalization": {
        "patterns": [r"everyone knows", r"always|never", r"all.*are"],
        "description": "Conclusion from insufficient sample"
    },
    "slippery_slope": {
        "patterns": [r"lead to|will result in|cascade|domino effect"],
        "description": "Claiming A will inevitably lead to Z"
    },
    "straw_man": {
        "patterns": [r"so you think|you're saying|what you're really saying"],
        "description": "Misrepresenting opponent's argument"
    }
}

def check_fallacies(text):
    """Check text for logical fallacies"""
    text_lower = text.lower()
    detected = []
    
    for fallacy_name, data in FALLACIES.items():
        for pattern in data["patterns"]:
            if re.search(pattern, text_lower):
                detected.append({
                    "name": fallacy_name,
                    "description": data["description"]
                })
                break
    
    return detected

def main():
    if len(sys.argv) < 2:
        print("Usage: python fallacy_checker.py '[argument text]'")
        print("\nChecks for common logical fallacies:")
        for name, data in FALLACIES.items():
            print(f"  • {name}: {data['description']}")
        return
    
    text = sys.argv[1]
    detected = check_fallacies(text)
    
    print("\n=== Fallacy Check Results ===")
    if detected:
        print(f"⚠️  Found {len(detected)} potential fallacies:")
        for d in detected:
            print(f"  • {d['name']}: {d['description']}")
        print("\nRecommendation: Review argument for logical validity")
    else:
        print("✓ No obvious fallacies detected")
        print("Note: Automated detection is limited. Manual review recommended.")

if __name__ == "__main__":
    main()
