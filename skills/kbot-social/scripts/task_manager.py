#!/usr/bin/env python3
"""
Kbot Task Manager
Handle service requests from customers
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path

TASK_QUEUE_FILE = Path(r"D:\kimi\memory\state\task_queue.json")
DELIVERY_DIR = Path(r"D:\kimi\deliveries")

# Ensure directories exist
DELIVERY_DIR.mkdir(parents=True, exist_ok=True)

class TaskManager:
    def __init__(self):
        self.queue_file = TASK_QUEUE_FILE
        self.delivery_dir = DELIVERY_DIR
        self.tasks = self._load_queue()
    
    def _load_queue(self):
        """Load task queue from file"""
        if self.queue_file.exists():
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"tasks": [], "completed": [], "stats": {"total": 0, "revenue": 0}}
    
    def _save_queue(self):
        """Save task queue to file"""
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)
    
    def add_task(self, customer, task_type, description, quoted_price):
        """Add new task from customer"""
        task = {
            "id": str(uuid.uuid4())[:8],
            "customer": customer,
            "type": task_type,  # express, standard, complex
            "description": description,
            "quoted_price": quoted_price,
            "status": "pending_payment",  # pending_payment, paid, in_progress, completed, failed
            "created_at": datetime.now().isoformat(),
            "paid_at": None,
            "completed_at": None,
            "payment_tx": None,
            "delivery_files": [],
            "notes": "",
        }
        
        self.tasks["tasks"].append(task)
        self._save_queue()
        
        return task
    
    def mark_paid(self, task_id, payment_tx, network):
        """Mark task as paid"""
        for task in self.tasks["tasks"]:
            if task["id"] == task_id:
                task["status"] = "paid"
                task["paid_at"] = datetime.now().isoformat()
                task["payment_tx"] = f"{network}:{payment_tx}"
                self._save_queue()
                return task
        return None
    
    def get_next_task(self):
        """Get next paid task to execute"""
        for task in self.tasks["tasks"]:
            if task["status"] == "paid":
                return task
        return None
    
    def execute_task(self, task_id):
        """Execute task based on type"""
        task = self._find_task(task_id)
        if not task:
            return None
        
        task["status"] = "in_progress"
        self._save_queue()
        
        # Route to appropriate handler
        handlers = {
            "powershell": self._execute_powershell,
            "file_conversion": self._execute_file_conversion,
            "excel": self._execute_excel,
            "compatibility_test": self._execute_compatibility_test,
            "automation": self._execute_automation,
        }
        
        handler = handlers.get(task["type"], self._execute_generic)
        result = handler(task)
        
        return result
    
    def _find_task(self, task_id):
        """Find task by ID"""
        for task in self.tasks["tasks"]:
            if task["id"] == task_id:
                return task
        return None
    
    def _execute_powershell(self, task):
        """Execute PowerShell command"""
        import subprocess
        
        cmd = task["description"]
        try:
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n[Errors]:\n{result.stderr}"
            
            # Save output to file
            output_file = self.delivery_dir / f"task_{task['id']}_output.txt"
            output_file.write_text(output, encoding='utf-8')
            
            return {
                "success": True,
                "output": output[:1000],  # Truncated for display
                "files": [str(output_file)],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_file_conversion(self, task):
        """Handle file conversion tasks"""
        # Placeholder - would use pandas for Excel, etc.
        return {"success": True, "message": "File conversion placeholder"}
    
    def _execute_excel(self, task):
        """Handle Excel automation"""
        return {"success": True, "message": "Excel automation placeholder"}
    
    def _execute_compatibility_test(self, task):
        """Run compatibility tests"""
        return {"success": True, "message": "Compatibility test placeholder"}
    
    def _execute_automation(self, task):
        """Create automation scripts"""
        return {"success": True, "message": "Automation script placeholder"}
    
    def _execute_generic(self, task):
        """Generic task handler"""
        return {"success": True, "message": "Task received, manual processing required"}
    
    def complete_task(self, task_id, delivery_files, notes=""):
        """Mark task as completed"""
        for task in self.tasks["tasks"]:
            if task["id"] == task_id:
                task["status"] = "completed"
                task["completed_at"] = datetime.now().isoformat()
                task["delivery_files"] = delivery_files
                task["notes"] = notes
                
                # Move to completed
                self.tasks["completed"].append(task)
                self.tasks["tasks"] = [t for t in self.tasks["tasks"] if t["id"] != task_id]
                
                # Update stats
                self.tasks["stats"]["total"] += 1
                self.tasks["stats"]["revenue"] += task["quoted_price"]
                
                self._save_queue()
                return task
        return None
    
    def get_stats(self):
        """Get service statistics"""
        return self.tasks["stats"]
    
    def list_pending(self):
        """List all pending tasks"""
        return [t for t in self.tasks["tasks"] if t["status"] in ["pending_payment", "paid"]]


def main():
    """CLI interface for task manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Kbot Task Manager")
    parser.add_argument("--add", help="Add new task (customer|type|description|price)")
    parser.add_argument("--list", action="store_true", help="List pending tasks")
    parser.add_argument("--execute", help="Execute task by ID")
    parser.add_argument("--complete", help="Complete task by ID")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    
    args = parser.parse_args()
    
    tm = TaskManager()
    
    if args.add:
        parts = args.add.split("|")
        if len(parts) == 4:
            task = tm.add_task(parts[0], parts[1], parts[2], float(parts[3]))
            print(f"[OK] Task added: {task['id']}")
        else:
            print("[ERROR] Format: customer|type|description|price")
    
    elif args.list:
        pending = tm.list_pending()
        print(f"Pending tasks: {len(pending)}")
        for t in pending:
            print(f"  [{t['id']}] {t['type']} - {t['status']} - ${t['quoted_price']}")
    
    elif args.execute:
        result = tm.execute_task(args.execute)
        print(json.dumps(result, indent=2))
    
    elif args.complete:
        task = tm.complete_task(args.complete, [])
        if task:
            print(f"[OK] Task completed: {task['id']}")
        else:
            print("[ERROR] Task not found")
    
    elif args.stats:
        stats = tm.get_stats()
        print(f"Total tasks: {stats['total']}")
        print(f"Revenue: ${stats['revenue']} USDC")


if __name__ == "__main__":
    main()
