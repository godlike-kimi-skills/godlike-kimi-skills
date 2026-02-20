#!/usr/bin/env python3
"""Socratic Questioning Generator"""
import sys

QUESTIONS = {
    "clarification": [
        "What exactly do you mean by that?",
        "Can you give me a specific example?",
        "What are you assuming?"
    ],
    "evidence": [
        "How do you know that's true?",
        "What evidence supports this?",
        "Are there counter-examples?"
    ],
    "alternatives": [
        "What other explanations could there be?",
        "How would someone else view this?",
        "What's the strongest argument against?"
    ],
    "consequences": [
        "What follows from this?",
        "What are the implications?",
        "What would happen if the opposite were true?"
    ]
}

def generate_questions(topic):
    print(f"\n=== Socratic Questions for: {topic} ===\n")
    
    for category, questions in QUESTIONS.items():
        print(f"[{category.upper()}]")
        for q in questions:
            print(f"  • {q}")
        print()

def main():
    if len(sys.argv) < 2:
        print("Usage: python socratic.py '[topic]'")
        print("\nGenerates Socratic questions for critical thinking")
        return
    
    generate_questions(sys.argv[1])

if __name__ == "__main__":
    main()
