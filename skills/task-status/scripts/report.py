#!/usr/bin/env python3
"""Generate task status report"""
import json

def generate_report():
    return {
        "active_tasks": 3,
        "completed_tasks": 6,
        "failed_tasks": 0,
        "total_earnings": 3900
    }

if __name__ == "__main__":
    print(json.dumps(generate_report(), indent=2))
