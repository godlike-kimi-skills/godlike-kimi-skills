# Cron Skill Examples

## Basic Usage

### Validate Cron Expression
```python
from main import CronSkill

skill = CronSkill()

# Validate expression
is_valid, error = skill.validate('0 9 * * 1-5')
if is_valid:
    print("✓ Valid expression")
else:
    print(f"✗ Invalid: {error}")
```

### Get Next Execution Time
```python
from main import CronSkill
from datetime import datetime

skill = CronSkill()

# Get next run time
next_run, error = skill.get_next('0 0 * * *')  # Daily at midnight
print(f"Next run: {next_run}")

# Get next run from specific time
from_time = datetime(2024, 1, 15, 10, 30)
next_run, error = skill.get_next('0 */6 * * *', from_time)
print(f"Next run from {from_time}: {next_run}")
```

### Get Multiple Execution Times
```python
# Get next 5 execution times
times, error = skill.get_next_n('*/30 * * * *', n=5)
for i, t in enumerate(times, 1):
    print(f"{i}. {t.strftime('%Y-%m-%d %H:%M')}")
```

**Output:**
```
1. 2024-01-15 11:00
2. 2024-01-15 11:30
3. 2024-01-15 12:00
4. 2024-01-15 12:30
5. 2024-01-15 13:00
```

### Describe Expression
```python
# Get human-readable description
description, error = skill.describe('0 9 * * 1-5')
print(description)  # "At 09:00 on Monday, Tuesday, Wednesday, Thursday and Friday"
```

### Generate Expression
```python
# Generate from natural language
expression, error = skill.generate('every 5 minutes')
print(expression)  # "*/5 * * * *"

expression, error = skill.generate('daily at 9am')
print(expression)  # "0 9 * * *"
```

## Common Cron Patterns

### Time-based Schedules
```python
# Every minute
skill.validate('* * * * *')

# Every 5 minutes
skill.validate('*/5 * * * *')

# Every hour
skill.validate('0 * * * *')

# Every 2 hours
skill.validate('0 */2 * * *')

# Daily at midnight
skill.validate('0 0 * * *')

# Daily at 9 AM
skill.validate('0 9 * * *')

# Twice daily
skill.validate('0 9,18 * * *')
```

### Day-based Schedules
```python
# Every weekday at 9 AM
skill.validate('0 9 * * 1-5')

# Every weekend at 10 AM
skill.validate('0 10 * * 0,6')

# Every Monday at 8 AM
skill.validate('0 8 * * 1')

# First day of every month at midnight
skill.validate('0 0 1 * *')

# Every 15th at noon
skill.validate('0 12 15 * *')
```

### Complex Schedules
```python
# Every 30 minutes during business hours on weekdays
description, _ = skill.describe('*/30 9-17 * * 1-5')
print(description)
# Output: "Every minute of hours 9, 10, 11, 12, 13, 14, 15, 16 and 17 on Monday, Tuesday, Wednesday, Thursday and Friday"

# At 00:00, 06:00, 12:00, 18:00 every day
description, _ = skill.describe('0 0,6,12,18 * * *')
print(description)
# Output: "At 00:00, 06:00, 12:00 and 18:00"

# Every 5 minutes on the hour during work hours
description, _ = skill.describe('0-59/5 9-17 * * 1-5')
print(description)
```

## Practical Workflows

### Job Scheduler
```python
#!/usr/bin/env python3
"""Simple job scheduler using cron expressions"""

from main import CronSkill
from datetime import datetime, timedelta

skill = CronSkill()

jobs = [
    {'name': 'Backup Database', 'cron': '0 2 * * *', 'command': 'backup.sh'},
    {'name': 'Clean Logs', 'cron': '0 3 * * 0', 'command': 'clean-logs.sh'},
    {'name': 'Send Report', 'cron': '0 9 * * 1', 'command': 'send-report.sh'},
]

def show_job_schedule(jobs, count=5):
    """Show upcoming executions for all jobs"""
    for job in jobs:
        print(f"\n📋 {job['name']}")
        print(f"   Expression: {job['cron']}")
        
        desc, _ = skill.describe(job['cron'])
        print(f"   Schedule: {desc}")
        
        times, _ = skill.get_next_n(job['cron'], n=count)
        print(f"   Next {count} runs:")
        for t in times:
            print(f"      - {t.strftime('%Y-%m-%d %H:%M')}")

show_job_schedule(jobs)
```

### Cron Expression Builder
```python
#!/usr/bin/env python3
"""Interactive cron expression builder"""

from main import CronSkill

skill = CronSkill()

def build_cron():
    print("Cron Expression Builder")
    print("-" * 40)
    
    # Minute
    print("\n1. Select minute:")
    print("   a) At specific minute (0-59)")
    print("   b) Every N minutes")
    print("   c) Multiple specific minutes")
    choice = input("   Choice: ")
    
    if choice == 'a':
        minute = input("   Enter minute (0-59): ")
    elif choice == 'b':
        n = input("   Every N minutes: ")
        minute = f"*/{n}"
    else:
        mins = input("   Enter minutes (comma-separated): ")
        minute = mins
    
    # Hour
    print("\n2. Select hour:")
    print("   a) At specific hour")
    print("   b) Every hour")
    print("   c) Business hours (9-17)")
    choice = input("   Choice: ")
    
    if choice == 'a':
        hour = input("   Enter hour (0-23): ")
    elif choice == 'b':
        hour = "*"
    else:
        hour = "9-17"
    
    # Build expression
    expression = f"{minute} {hour} * * *"
    
    # Validate
    is_valid, error = skill.validate(expression)
    if is_valid:
        print(f"\n✓ Generated expression: {expression}")
        desc, _ = skill.describe(expression)
        print(f"  Description: {desc}")
        
        # Show next runs
        times, _ = skill.get_next_n(expression, n=3)
        print(f"  Next 3 runs:")
        for t in times:
            print(f"    - {t}")
    else:
        print(f"✗ Invalid: {error}")

# Uncomment to run interactively
# build_cron()
```

### Cron Migration Tool
```python
#!/usr/bin/env python3
"""Convert between cron formats and validate"""

from main import CronSkill
import json

skill = CronSkill()

def migrate_cron_list(expressions):
    """Migrate and validate a list of cron expressions"""
    results = []
    
    for expr in expressions:
        is_valid, error = skill.validate(expr)
        
        if is_valid:
            desc, _ = skill.describe(expr)
            next_run, _ = skill.get_next(expr)
            
            results.append({
                'expression': expr,
                'valid': True,
                'description': desc,
                'next_run': next_run.isoformat() if next_run else None
            })
        else:
            results.append({
                'expression': expr,
                'valid': False,
                'error': error
            })
    
    return results

# Example: Validate all cron expressions in a config
cron_expressions = [
    '0 0 * * *',
    '0 2 * * 0',
    '*/5 * * * *',
    'invalid expression',
    '0 9-17 * * 1-5'
]

results = migrate_cron_list(cron_expressions)
print(json.dumps(results, indent=2))
```

## CLI Examples

### Validate Expression
```bash
# Simple validation
python main.py validate "0 9 * * 1-5"

# Check preset
python main.py validate "@daily"

# Invalid expression
python main.py validate "invalid"
```

### Get Next Run
```bash
# Get next execution time
python main.py next "0 9 * * *"

# From specific time
python main.py next "0 9 * * *" --from "2024-01-15T10:30:00"

# Check multiple times
python main.py schedule "*/30 * * * *" --count 5
```

### Describe Expression
```bash
# Get human-readable description
python main.py describe "0 9 * * 1-5"

# Describe preset
python main.py describe "@hourly"
```

### Generate Expression
```bash
# Generate from description
python main.py generate "every 5 minutes"

python main.py generate "daily at 9am"

python main.py generate "every hour"
```

### List Presets
```bash
# Show all preset expressions
python main.py presets
```

### Show Field Info
```bash
# Show field information
python main.py fields
```

## Advanced Examples

### Calculate Execution Statistics
```python
#!/usr/bin/env python3
"""Calculate execution statistics for a cron expression"""

from main import CronSkill
from datetime import datetime, timedelta

skill = CronSkill()

def calculate_stats(expression, days=30):
    """Calculate execution statistics"""
    is_valid, error = skill.validate(expression)
    if not is_valid:
        return None, error
    
    start = datetime.now()
    end = start + timedelta(days=days)
    
    # Get all executions in the period
    executions = []
    current = start
    
    while len(executions) < 1000:  # Limit for safety
        next_run, _ = skill.get_next(expression, current)
        if not next_run or next_run > end:
            break
        executions.append(next_run)
        current = next_run + timedelta(minutes=1)
    
    # Calculate statistics
    total = len(executions)
    per_day = total / days
    
    # Hour distribution
    hour_counts = {}
    for e in executions:
        hour = e.hour
        hour_counts[hour] = hour_counts.get(hour, 0) + 1
    
    return {
        'total_executions': total,
        'per_day_average': round(per_day, 2),
        'hour_distribution': hour_counts
    }, None

# Example usage
stats, error = calculate_stats('*/15 9-17 * * 1-5', days=7)
if stats:
    print(f"Total executions: {stats['total_executions']}")
    print(f"Average per day: {stats['per_day_average']}")
    print("Hour distribution:", stats['hour_distribution'])
```

### Compare Cron Expressions
```python
def compare_expressions(expr1, expr2, count=10):
    """Compare two cron expressions"""
    times1, _ = skill.get_next_n(expr1, n=count)
    times2, _ = skill.get_next_n(expr2, n=count)
    
    print(f"Expression 1: {expr1}")
    print(f"Expression 2: {expr2}")
    print("-" * 60)
    
    for i, (t1, t2) in enumerate(zip(times1, times2)):
        same = "✓" if t1 == t2 else "✗"
        print(f"{same} Run {i+1}: {t1} vs {t2}")

# Compare similar expressions
compare_expressions('0 * * * *', '0 */1 * * *', count=5)
```
