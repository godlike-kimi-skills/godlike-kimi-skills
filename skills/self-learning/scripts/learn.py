#!/usr/bin/env python3
"""
Self Learning System
Based on RLHF and LangChain Memory patterns
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class LearningMemory:
    """Stores learning data"""

    DATA_FILE = Path.home() / '.self_learning.json'

    def __init__(self):
        self.preferences: Dict[str, any] = {}
        self.feedback: List[Dict] = []
        self.corrections: List[Dict] = []
        self.load()

    def load(self):
        """Load learning data"""
        if self.DATA_FILE.exists():
            try:
                with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.preferences = data.get('preferences', {})
                    self.feedback = data.get('feedback', [])
                    self.corrections = data.get('corrections', [])
            except Exception:
                pass

    def save(self):
        """Save learning data"""
        with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'preferences': self.preferences,
                'feedback': self.feedback,
                'corrections': self.corrections
            }, f, indent=2)

    def add_feedback(self, feedback: str, context: str = None):
        """Add user feedback"""
        self.feedback.append({
            'feedback': feedback,
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
        self.save()

    def add_correction(self, original: str, corrected: str):
        """Add correction"""
        self.corrections.append({
            'original': original,
            'corrected': corrected,
            'timestamp': datetime.now().isoformat()
        })
        self.save()

    def set_preference(self, key: str, value: any):
        """Set preference"""
        self.preferences[key] = value
        self.save()

    def get_stats(self) -> Dict:
        """Get learning statistics"""
        return {
            'preferences_count': len(self.preferences),
            'feedback_count': len(self.feedback),
            'corrections_count': len(self.corrections),
            'preferences': self.preferences
        }


def main():
    parser = argparse.ArgumentParser(description='Self Learning')
    subparsers = parser.add_subparsers(dest='command')

    feedback_parser = subparsers.add_parser('feedback')
    feedback_parser.add_argument('text')
    feedback_parser.add_argument('--context')

    correct_parser = subparsers.add_parser('correct')
    correct_parser.add_argument('--original', required=True)
    correct_parser.add_argument('--corrected', required=True)

    pref_parser = subparsers.add_parser('preference')
    pref_parser.add_argument('--key', required=True)
    pref_parser.add_argument('--value', required=True)

    subparsers.add_parser('status')
    subparsers.add_parser('reset')
    subparsers.add_parser('export')

    args = parser.parse_args()
    memory = LearningMemory()

    if args.command == 'feedback':
        memory.add_feedback(args.text, args.context)
        print('Feedback recorded')

    elif args.command == 'correct':
        memory.add_correction(args.original, args.corrected)
        print('Correction recorded')

    elif args.command == 'preference':
        memory.set_preference(args.key, args.value)
        print(f'Preference set: {args.key} = {args.value}')

    elif args.command == 'status':
        stats = memory.get_stats()
        print(json.dumps(stats, indent=2))

    elif args.command == 'reset':
        memory.preferences = {}
        memory.feedback = []
        memory.corrections = []
        memory.save()
        print('Learning data reset')

    elif args.command == 'export':
        data = {
            'preferences': memory.preferences,
            'feedback': memory.feedback,
            'corrections': memory.corrections,
            'exported_at': datetime.now().isoformat()
        }
        print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
