#!/usr/bin/env python3
"""
Cron Skill - Cron Expression Tool
Supports: validation, next execution calculation, description, generation
"""

import re
import sys
import argparse
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum


@dataclass
class CronField:
    """Represents a field in a cron expression"""
    name: str
    min_value: int
    max_value: int
    allowed_values: List[int]
    
    def __str__(self):
        return f"{self.name}: {self.allowed_values}"


@dataclass
class CronSchedule:
    """Parsed cron expression"""
    minute: CronField
    hour: CronField
    day_of_month: CronField
    month: CronField
    day_of_week: CronField
    expression: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'expression': self.expression,
            'minute': self.minute.allowed_values,
            'hour': self.hour.allowed_values,
            'day_of_month': self.day_of_month.allowed_values,
            'month': self.month.allowed_values,
            'day_of_week': self.day_of_week.allowed_values,
        }


class CronSkill:
    """Main skill class for cron expression operations"""
    
    # Field definitions
    FIELD_DEFINITIONS = {
        'minute': {'min': 0, 'max': 59, 'name': 'Minute'},
        'hour': {'min': 0, 'max': 23, 'name': 'Hour'},
        'day_of_month': {'min': 1, 'max': 31, 'name': 'Day of Month'},
        'month': {'min': 1, 'max': 12, 'name': 'Month'},
        'day_of_week': {'min': 0, 'max': 6, 'name': 'Day of Week'}
    }
    
    # Day of week names
    DAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    MONTH_NAMES = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    # Preset expressions
    PRESETS = {
        '@yearly': {'expression': '0 0 1 1 *', 'description': 'Once a year at midnight on Jan 1st'},
        '@annually': {'expression': '0 0 1 1 *', 'description': 'Once a year at midnight on Jan 1st'},
        '@monthly': {'expression': '0 0 1 * *', 'description': 'Once a month at midnight on the 1st'},
        '@weekly': {'expression': '0 0 * * 0', 'description': 'Once a week at midnight on Sunday'},
        '@daily': {'expression': '0 0 * * *', 'description': 'Once a day at midnight'},
        '@midnight': {'expression': '0 0 * * *', 'description': 'Once a day at midnight'},
        '@hourly': {'expression': '0 * * * *', 'description': 'Once an hour at the start of the hour'},
        '@reboot': {'expression': None, 'description': 'At system startup (non-standard)'}
    }
    
    def __init__(self):
        self.name = "cron-skill"
        self.version = "1.0.0"
    
    def _parse_field(self, field_str: str, field_name: str) -> Tuple[Optional[List[int]], Optional[str]]:
        """
        Parse a single cron field
        
        Args:
            field_str: The field value string
            field_name: Name of the field for error messages
            
        Returns:
            Tuple of (list_of_values, error_message)
        """
        field_def = self.FIELD_DEFINITIONS[field_name]
        min_val = field_def['min']
        max_val = field_def['max']
        
        values = set()
        
        # Handle asterisk
        if field_str == '*':
            return list(range(min_val, max_val + 1)), None
        
        # Handle asterisk with step
        if field_str.startswith('*/'):
            try:
                step = int(field_str[2:])
                if step <= 0:
                    return None, f"Invalid step value in {field_name}: {step}"
                return list(range(min_val, max_val + 1, step)), None
            except ValueError:
                return None, f"Invalid step in {field_name}: {field_str}"
        
        # Handle step with range
        if '/' in field_str:
            parts = field_str.split('/')
            if len(parts) != 2:
                return None, f"Invalid step format in {field_name}: {field_str}"
            
            range_part = parts[0]
            try:
                step = int(parts[1])
                if step <= 0:
                    return None, f"Invalid step value in {field_name}: {step}"
            except ValueError:
                return None, f"Invalid step in {field_name}: {parts[1]}"
            
            if range_part == '*':
                start, end = min_val, max_val
            elif '-' in range_part:
                range_parts = range_part.split('-')
                if len(range_parts) != 2:
                    return None, f"Invalid range in {field_name}: {range_part}"
                try:
                    start = int(range_parts[0])
                    end = int(range_parts[1])
                except ValueError:
                    return None, f"Invalid range values in {field_name}: {range_part}"
            else:
                try:
                    start = int(range_part)
                    end = max_val
                except ValueError:
                    return None, f"Invalid start value in {field_name}: {range_part}"
            
            if start < min_val or end > max_val:
                return None, f"Range {start}-{end} out of bounds for {field_name} ({min_val}-{max_val})"
            
            return list(range(start, end + 1, step)), None
        
        # Handle comma-separated values and ranges
        parts = field_str.split(',')
        for part in parts:
            if '-' in part:
                range_parts = part.split('-')
                if len(range_parts) != 2:
                    return None, f"Invalid range in {field_name}: {part}"
                try:
                    start = int(range_parts[0])
                    end = int(range_parts[1])
                except ValueError:
                    return None, f"Invalid range values in {field_name}: {part}"
                
                if start < min_val or end > max_val:
                    return None, f"Range {start}-{end} out of bounds for {field_name} ({min_val}-{max_val})"
                
                values.update(range(start, end + 1))
            else:
                try:
                    val = int(part)
                    if val < min_val or val > max_val:
                        return None, f"Value {val} out of bounds for {field_name} ({min_val}-{max_val})"
                    values.add(val)
                except ValueError:
                    return None, f"Invalid value in {field_name}: {part}"
        
        return sorted(list(values)), None
    
    def parse(self, expression: str) -> Tuple[Optional[CronSchedule], Optional[str]]:
        """
        Parse a cron expression
        
        Args:
            expression: Cron expression string
            
        Returns:
            Tuple of (CronSchedule, error_message)
        """
        # Check for presets
        if expression in self.PRESETS:
            preset = self.PRESETS[expression]
            if preset['expression'] is None:
                return None, f"Preset {expression} is not a standard cron expression"
            expression = preset['expression']
        
        # Split expression into fields
        parts = expression.split()
        if len(parts) != 5:
            return None, f"Invalid cron expression: expected 5 fields, got {len(parts)}"
        
        minute, hour, day_of_month, month, day_of_week = parts
        
        # Parse each field
        minute_vals, error = self._parse_field(minute, 'minute')
        if error:
            return None, error
        
        hour_vals, error = self._parse_field(hour, 'hour')
        if error:
            return None, error
        
        day_of_month_vals, error = self._parse_field(day_of_month, 'day_of_month')
        if error:
            return None, error
        
        month_vals, error = self._parse_field(month, 'month')
        if error:
            return None, error
        
        day_of_week_vals, error = self._parse_field(day_of_week, 'day_of_week')
        if error:
            return None, error
        
        schedule = CronSchedule(
            minute=CronField('minute', 0, 59, minute_vals),
            hour=CronField('hour', 0, 23, hour_vals),
            day_of_month=CronField('day_of_month', 1, 31, day_of_month_vals),
            month=CronField('month', 1, 12, month_vals),
            day_of_week=CronField('day_of_week', 0, 6, day_of_week_vals),
            expression=expression
        )
        
        return schedule, None
    
    def validate(self, expression: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a cron expression
        
        Args:
            expression: Cron expression string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        schedule, error = self.parse(expression)
        if error:
            return False, error
        return True, None
    
    def _is_scheduled(self, dt: datetime, schedule: CronSchedule) -> bool:
        """Check if a datetime matches the schedule"""
        return (
            dt.minute in schedule.minute.allowed_values and
            dt.hour in schedule.hour.allowed_values and
            dt.day in schedule.day_of_month.allowed_values and
            dt.month in schedule.month.allowed_values and
            dt.weekday() in schedule.day_of_week.allowed_values
        )
    
    def get_next(self, expression: str, from_time: datetime = None) -> Tuple[Optional[datetime], Optional[str]]:
        """
        Get the next execution time from a given time
        
        Args:
            expression: Cron expression string
            from_time: Starting time (default: now)
            
        Returns:
            Tuple of (next_time, error_message)
        """
        schedule, error = self.parse(expression)
        if error:
            return None, error
        
        if from_time is None:
            from_time = datetime.now()
        
        # Start from the next minute
        current = from_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
        
        # Search for next match (max 4 years to avoid infinite loop)
        max_iterations = 366 * 24 * 60 * 4  # 4 years in minutes
        iterations = 0
        
        while iterations < max_iterations:
            if self._is_scheduled(current, schedule):
                return current, None
            current += timedelta(minutes=1)
            iterations += 1
        
        return None, "Could not find next execution time within 4 years"
    
    def get_next_n(self, expression: str, n: int = 5, from_time: datetime = None) -> Tuple[Optional[List[datetime]], Optional[str]]:
        """
        Get the next N execution times
        
        Args:
            expression: Cron expression string
            n: Number of times to get
            from_time: Starting time (default: now)
            
        Returns:
            Tuple of (list_of_times, error_message)
        """
        schedule, error = self.parse(expression)
        if error:
            return None, error
        
        if from_time is None:
            from_time = datetime.now()
        
        times = []
        current = from_time.replace(second=0, microsecond=0)
        
        # Search for next n matches
        max_iterations = 366 * 24 * 60 * 4  # 4 years in minutes
        iterations = 0
        
        while len(times) < n and iterations < max_iterations:
            if self._is_scheduled(current, schedule):
                times.append(current)
            current += timedelta(minutes=1)
            iterations += 1
        
        if len(times) < n:
            return times, f"Only found {len(times)} occurrences within 4 years"
        
        return times, None
    
    def describe(self, expression: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Convert cron expression to human-readable description
        
        Args:
            expression: Cron expression string
            
        Returns:
            Tuple of (description, error_message)
        """
        # Check for presets
        if expression in self.PRESETS:
            return self.PRESETS[expression]['description'], None
        
        schedule, error = self.parse(expression)
        if error:
            return None, error
        
        parts = []
        
        # Describe minute
        if schedule.minute.allowed_values == list(range(60)):
            minute_desc = "every minute"
        elif len(schedule.minute.allowed_values) == 1:
            m = schedule.minute.allowed_values[0]
            minute_desc = f"at minute {m}"
        else:
            minute_desc = f"at minutes {self._format_list(schedule.minute.allowed_values)}"
        
        # Describe hour
        if schedule.hour.allowed_values == list(range(24)):
            hour_desc = "every hour"
        elif len(schedule.hour.allowed_values) == 1:
            h = schedule.hour.allowed_values[0]
            hour_desc = f"{h:02d}:00"
        else:
            hour_desc = f"hours {self._format_list(schedule.hour.allowed_values)}"
        
        # Describe day of month
        if schedule.day_of_month.allowed_values == list(range(1, 32)):
            day_desc = "every day"
        elif len(schedule.day_of_month.allowed_values) == 1:
            d = schedule.day_of_month.allowed_values[0]
            day_desc = f"on day {d} of the month"
        else:
            day_desc = f"on days {self._format_list(schedule.day_of_month.allowed_values)}"
        
        # Describe month
        if schedule.month.allowed_values == list(range(1, 13)):
            month_desc = "every month"
        elif len(schedule.month.allowed_values) == 1:
            m = schedule.month.allowed_values[0]
            month_desc = f"in {self.MONTH_NAMES[m]}"
        else:
            month_names = [self.MONTH_NAMES[m] for m in schedule.month.allowed_values]
            month_desc = f"in {self._format_list(month_names)}"
        
        # Describe day of week
        if schedule.day_of_week.allowed_values == list(range(7)):
            dow_desc = "every day of the week"
        elif len(schedule.day_of_week.allowed_values) == 1:
            d = schedule.day_of_week.allowed_values[0]
            dow_desc = f"on {self.DAY_NAMES[d]}"
        else:
            day_names = [self.DAY_NAMES[d] for d in schedule.day_of_week.allowed_values]
            dow_desc = f"on {self._format_list(day_names)}"
        
        # Build description
        if schedule.minute.allowed_values == [0] and schedule.hour.allowed_values == [0]:
            time_desc = "At midnight"
        elif schedule.minute.allowed_values == [0]:
            if len(schedule.hour.allowed_values) == 1:
                time_desc = f"At {schedule.hour.allowed_values[0]:02d}:00"
            else:
                time_desc = f"At {hour_desc}"
        elif schedule.minute.allowed_values == list(range(60)) and schedule.hour.allowed_values == list(range(24)):
            time_desc = "Every minute"
        else:
            if schedule.minute.allowed_values == list(range(60)):
                time_desc = f"Every minute of {hour_desc}"
            elif len(schedule.minute.allowed_values) == 1 and len(schedule.hour.allowed_values) == 1:
                time_desc = f"At {schedule.hour.allowed_values[0]:02d}:{schedule.minute.allowed_values[0]:02d}"
            else:
                time_desc = f"{minute_desc} of {hour_desc}"
        
        # Combine with date restrictions
        if schedule.day_of_week.allowed_values != list(range(7)):
            description = f"{time_desc} {dow_desc}"
        elif schedule.day_of_month.allowed_values != list(range(1, 32)):
            description = f"{time_desc} {day_desc}"
        elif schedule.month.allowed_values != list(range(1, 13)):
            description = f"{time_desc} {month_desc}"
        else:
            description = time_desc
        
        return description, None
    
    def _format_list(self, items: List[Any]) -> str:
        """Format a list for display"""
        if len(items) <= 2:
            return " and ".join(str(x) for x in items)
        return ", ".join(str(x) for x in items[:-1]) + f" and {items[-1]}"
    
    def generate(self, description: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate a cron expression from a description
        
        Args:
            description: Natural language description
            
        Returns:
            Tuple of (expression, error_message)
        """
        desc = description.lower().strip()
        
        # Common patterns
        patterns = [
            (r'every (\d+) minutes?', lambda m: f"*/{m.group(1)} * * * *"),
            (r'every (\d+) hours?', lambda m: f"0 */{m.group(1)} * * *"),
            (r'every (\d+) days?', lambda m: f"0 0 */{m.group(1)} * *"),
            (r'every minute', lambda m: "* * * * *"),
            (r'every hour', lambda m: "0 * * * *"),
            (r'every day', lambda m: "0 0 * * *"),
            (r'daily', lambda m: "0 0 * * *"),
            (r'hourly', lambda m: "0 * * * *"),
            (r'minutely', lambda m: "* * * * *"),
            (r'every (monday|tuesday|wednesday|thursday|friday|saturday|sunday)', self._parse_day_of_week),
            (r'at (\d+):(\d+)', lambda m: f"{int(m.group(2))} {int(m.group(1))} * * *"),
            (r'at (\d+)(?:am|pm)?', self._parse_hour),
        ]
        
        for pattern, handler in patterns:
            match = re.search(pattern, desc)
            if match:
                result = handler(match)
                if result:
                    return result, None
        
        return None, f"Could not understand description: {description}"
    
    def _parse_day_of_week(self, match) -> str:
        """Parse day of week from match"""
        day_map = {
            'sunday': 0, 'monday': 1, 'tuesday': 2, 'wednesday': 3,
            'thursday': 4, 'friday': 5, 'saturday': 6
        }
        day = match.group(1)
        return f"0 0 * * {day_map.get(day, '*')}"
    
    def _parse_hour(self, match) -> str:
        """Parse hour from match"""
        hour = int(match.group(1))
        return f"0 {hour} * * *"
    
    def get_field_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about cron fields"""
        return {
            'minute': {
                'description': 'Minute (0-59)',
                'special_chars': ['*', ',', '-', '/'],
                'examples': ['0', '*/5', '0,30', '9-17']
            },
            'hour': {
                'description': 'Hour (0-23)',
                'special_chars': ['*', ',', '-', '/'],
                'examples': ['0', '*/2', '9-17', '0,12']
            },
            'day_of_month': {
                'description': 'Day of Month (1-31)',
                'special_chars': ['*', ',', '-', '/'],
                'examples': ['1', '*/5', '1,15']
            },
            'month': {
                'description': 'Month (1-12)',
                'special_chars': ['*', ',', '-', '/'],
                'examples': ['*', '1-6', '1,4,7,10']
            },
            'day_of_week': {
                'description': 'Day of Week (0-6, Sunday=0)',
                'special_chars': ['*', ',', '-', '/'],
                'examples': ['*', '1-5', '0,6']
            }
        }
    
    def get_presets(self) -> Dict[str, Dict[str, str]]:
        """Get all preset expressions"""
        return self.PRESETS.copy()


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='Cron Expression Tool')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate expression')
    validate_parser.add_argument('expression', help='Cron expression')
    
    # Next command
    next_parser = subparsers.add_parser('next', help='Get next execution time')
    next_parser.add_argument('expression', help='Cron expression')
    next_parser.add_argument('--from', dest='from_time', help='Start time (ISO format)')
    
    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Get multiple execution times')
    schedule_parser.add_argument('expression', help='Cron expression')
    schedule_parser.add_argument('--count', '-n', type=int, default=5, help='Number of times')
    schedule_parser.add_argument('--from', dest='from_time', help='Start time (ISO format)')
    
    # Describe command
    describe_parser = subparsers.add_parser('describe', help='Describe expression')
    describe_parser.add_argument('expression', help='Cron expression')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate expression')
    gen_parser.add_argument('description', help='Description of schedule')
    
    # Presets command
    presets_parser = subparsers.add_parser('presets', help='List presets')
    
    # Fields command
    fields_parser = subparsers.add_parser('fields', help='Show field information')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    skill = CronSkill()
    
    if args.command == 'validate':
        is_valid, error = skill.validate(args.expression)
        if is_valid:
            print(f"✓ Valid cron expression: {args.expression}")
        else:
            print(f"✗ Invalid: {error}")
            sys.exit(1)
    
    elif args.command == 'next':
        from_time = None
        if args.from_time:
            from_time = datetime.fromisoformat(args.from_time)
        
        next_time, error = skill.get_next(args.expression, from_time)
        if error:
            print(f"Error: {error}")
            sys.exit(1)
        print(next_time.isoformat())
    
    elif args.command == 'schedule':
        from_time = None
        if args.from_time:
            from_time = datetime.fromisoformat(args.from_time)
        
        times, error = skill.get_next_n(args.expression, args.count, from_time)
        if error:
            print(f"Warning: {error}")
        
        for i, t in enumerate(times, 1):
            print(f"{i}. {t.isoformat()}")
    
    elif args.command == 'describe':
        description, error = skill.describe(args.expression)
        if error:
            print(f"Error: {error}")
            sys.exit(1)
        print(description)
    
    elif args.command == 'generate':
        expression, error = skill.generate(args.description)
        if error:
            print(f"Error: {error}")
            sys.exit(1)
        print(expression)
    
    elif args.command == 'presets':
        presets = skill.get_presets()
        for name, info in presets.items():
            if info['expression']:
                print(f"{name:<12} {info['expression']:<20} # {info['description']}")
            else:
                print(f"{name:<12} {'(non-standard)':<20} # {info['description']}")
    
    elif args.command == 'fields':
        fields = skill.get_field_info()
        for name, info in fields.items():
            print(f"\n{name}:")
            print(f"  Description: {info['description']}")
            print(f"  Special chars: {', '.join(info['special_chars'])}")
            print(f"  Examples: {', '.join(info['examples'])}")


if __name__ == '__main__':
    main()
