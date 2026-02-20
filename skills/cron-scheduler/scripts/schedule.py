#!/usr/bin/env python3
"""Schedule tasks"""
import sys, json

def schedule_task(task, interval_minutes):
    return {
        "task": task,
        "interval": interval_minutes,
        "status": "scheduled",
        "next_run": "calculated"
    }

if __name__ == "__main__":
    print(json.dumps({"scheduler": "active", "tasks": []}))
