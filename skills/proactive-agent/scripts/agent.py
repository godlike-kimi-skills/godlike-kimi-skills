#!/usr/bin/env python3
"""
Proactive Agent - Goal-driven AI
Based on AutoGPT and BabyAGI patterns
"""

import argparse
import json
from datetime import datetime
from typing import Dict, List, Optional


class Task:
    """Represents a task"""

    def __init__(self, description: str, priority: int = 1):
        self.description = description
        self.priority = priority
        self.status = 'pending'
        self.created_at = datetime.now()
        self.completed_at: Optional[datetime] = None

    def complete(self):
        self.status = 'completed'
        self.completed_at = datetime.now()

    def to_dict(self) -> Dict:
        return {
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class ProactiveAgent:
    """Goal-driven proactive agent"""

    def __init__(self, goal: str):
        self.goal = goal
        self.tasks: List[Task] = []
        self.memory: List[str] = []
        self.plan: Optional[List[str]] = None

    def plan_tasks(self) -> List[str]:
        """Break down goal into tasks"""
        # Simplified planning logic
        self.plan = [
            f"Research: {self.goal}",
            f"Analyze findings for {self.goal}",
            f"Generate deliverables for {self.goal}",
            f"Review and finalize {self.goal}"
        ]
        for task_desc in self.plan:
            self.tasks.append(Task(task_desc))
        return self.plan

    def execute_task(self, task_index: int) -> str:
        """Execute a specific task"""
        if task_index >= len(self.tasks):
            return 'Invalid task index'

        task = self.tasks[task_index]
        task.status = 'in_progress'

        # Simulated execution
        result = f"Executed: {task.description}"
        task.complete()
        self.memory.append(result)

        return result

    def run(self) -> Dict:
        """Run the agent to complete goal"""
        self.plan_tasks()

        for i in range(len(self.tasks)):
            self.execute_task(i)

        return {
            'goal': self.goal,
            'plan': self.plan,
            'tasks': [t.to_dict() for t in self.tasks],
            'memory': self.memory,
            'status': 'completed'
        }

    def interactive_mode(self):
        """Run in interactive mode"""
        print(f"Proactive Agent initialized with goal: {self.goal}")
        print("Commands: plan, execute <n>, status, exit")

        while True:
            try:
                cmd = input("\n> ").strip().split()
                if not cmd:
                    continue

                if cmd[0] == 'exit':
                    break
                elif cmd[0] == 'plan':
                    self.plan_tasks()
                    for i, task in enumerate(self.tasks):
                        print(f"{i}. {task.description} [{task.status}]")
                elif cmd[0] == 'execute' and len(cmd) > 1:
                    result = self.execute_task(int(cmd[1]))
                    print(result)
                elif cmd[0] == 'status':
                    print(json.dumps({
                        'goal': self.goal,
                        'tasks_completed': sum(1 for t in self.tasks if t.status == 'completed'),
                        'total_tasks': len(self.tasks)
                    }, indent=2))
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f'Error: {e}')


def main():
    parser = argparse.ArgumentParser(description='Proactive Agent')
    parser.add_argument('--goal', required=True, help='Goal to achieve')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--output', help='Output file')
    args = parser.parse_args()

    agent = ProactiveAgent(args.goal)

    if args.interactive:
        agent.interactive_mode()
    else:
        result = agent.run()
        print(json.dumps(result, indent=2))

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)


if __name__ == '__main__':
    main()
