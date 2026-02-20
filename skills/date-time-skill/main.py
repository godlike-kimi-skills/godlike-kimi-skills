#!/usr/bin/env python3
"""
Date Time Skill - Comprehensive date and time utility
Supports timezone conversion, date calculations, and formatting
"""

from datetime import datetime, timedelta
from typing import Optional, Union, List, Dict
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta
import pytz


class DateTimeSkill:
    """
    A comprehensive date and time utility class providing:
    - Timezone conversion between 500+ timezones
    - Date arithmetic (add/subtract days, months, years)
    - Date difference calculations
    - Multiple formatting options
    - Business days calculation
    """
    
    def __init__(self):
        """Initialize the DateTimeSkill with timezone data"""
        self._common_formats = {
            'iso': '%Y-%m-%dT%H:%M:%S',
            'iso_date': '%Y-%m-%d',
            'iso_datetime': '%Y-%m-%d %H:%M:%S',
            'us': '%m/%d/%Y',
            'us_datetime': '%m/%d/%Y %I:%M %p',
            'eu': '%d/%m/%Y',
            'eu_datetime': '%d/%m/%Y %H:%M',
            'full': '%A, %B %d, %Y',
            'compact': '%Y%m%d',
            'rfc2822': '%a, %d %b %Y %H:%M:%S %z',
        }
        self._all_timezones = set(pytz.all_timezones)
    
    def parse_date(self, date_string: str) -> datetime:
        """
        Parse a date string into a datetime object
        
        Args:
            date_string: Date string in various formats
            
        Returns:
            datetime object
            
        Raises:
            ValueError: If date string cannot be parsed
        """
        try:
            return date_parser.parse(date_string)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Unable to parse date: {date_string}") from e
    
    def convert_timezone(
        self, 
        date_string: str, 
        from_tz: str, 
        to_tz: str,
        output_format: str = 'iso_datetime'
    ) -> str:
        """
        Convert a datetime from one timezone to another
        
        Args:
            date_string: The date/time to convert
            from_tz: Source timezone (e.g., 'Asia/Shanghai', 'UTC')
            to_tz: Target timezone (e.g., 'America/New_York', 'Europe/London')
            output_format: Output format key or custom format string
            
        Returns:
            Converted datetime as string
            
        Raises:
            ValueError: If timezone is invalid
        """
        if from_tz not in self._all_timezones:
            raise ValueError(f"Invalid source timezone: {from_tz}")
        if to_tz not in self._all_timezones:
            raise ValueError(f"Invalid target timezone: {to_tz}")
        
        # Parse the input date
        dt = self.parse_date(date_string)
        
        # Localize to source timezone
        source_tz = pytz.timezone(from_tz)
        if dt.tzinfo is None:
            dt = source_tz.localize(dt)
        else:
            dt = dt.astimezone(source_tz)
        
        # Convert to target timezone
        target_tz = pytz.timezone(to_tz)
        converted_dt = dt.astimezone(target_tz)
        
        # Format output
        fmt = self._common_formats.get(output_format, output_format)
        return converted_dt.strftime(fmt)
    
    def get_current_time(self, timezone: str = 'UTC', output_format: str = 'iso_datetime') -> str:
        """
        Get current time in specified timezone
        
        Args:
            timezone: Target timezone
            output_format: Output format
            
        Returns:
            Current time as formatted string
        """
        if timezone not in self._all_timezones:
            raise ValueError(f"Invalid timezone: {timezone}")
        
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        fmt = self._common_formats.get(output_format, output_format)
        return now.strftime(fmt)
    
    def add_days(self, date_string: str, days: int) -> str:
        """
        Add days to a date
        
        Args:
            date_string: Base date
            days: Number of days to add (negative to subtract)
            
        Returns:
            Resulting date as ISO format string (YYYY-MM-DD)
        """
        dt = self.parse_date(date_string)
        result = dt + timedelta(days=days)
        return result.strftime('%Y-%m-%d')
    
    def add_months(self, date_string: str, months: int) -> str:
        """
        Add months to a date
        
        Args:
            date_string: Base date
            months: Number of months to add (negative to subtract)
            
        Returns:
            Resulting date as ISO format string (YYYY-MM-DD)
        """
        dt = self.parse_date(date_string)
        result = dt + relativedelta(months=months)
        return result.strftime('%Y-%m-%d')
    
    def add_years(self, date_string: str, years: int) -> str:
        """
        Add years to a date
        
        Args:
            date_string: Base date
            years: Number of years to add (negative to subtract)
            
        Returns:
            Resulting date as ISO format string (YYYY-MM-DD)
        """
        dt = self.parse_date(date_string)
        result = dt + relativedelta(years=years)
        return result.strftime('%Y-%m-%d')
    
    def date_difference(self, date1: str, date2: str, unit: str = 'days') -> Union[int, float]:
        """
        Calculate difference between two dates
        
        Args:
            date1: First date
            date2: Second date
            unit: Unit of difference ('days', 'hours', 'minutes', 'seconds', 'weeks', 'months', 'years')
            
        Returns:
            Difference as number
        """
        dt1 = self.parse_date(date1)
        dt2 = self.parse_date(date2)
        
        delta = dt2 - dt1
        
        if unit == 'days':
            return delta.days
        elif unit == 'hours':
            return delta.total_seconds() / 3600
        elif unit == 'minutes':
            return delta.total_seconds() / 60
        elif unit == 'seconds':
            return delta.total_seconds()
        elif unit == 'weeks':
            return delta.days / 7
        elif unit == 'months':
            rd = relativedelta(dt2, dt1)
            return rd.months + rd.years * 12
        elif unit == 'years':
            rd = relativedelta(dt2, dt1)
            return rd.years
        else:
            raise ValueError(f"Unsupported unit: {unit}")
    
    def format_date(self, date_string: str, output_format: str = 'iso_date') -> str:
        """
        Format a date to specified format
        
        Args:
            date_string: Input date
            output_format: Output format key or custom format string
            
        Returns:
            Formatted date string
        """
        dt = self.parse_date(date_string)
        fmt = self._common_formats.get(output_format, output_format)
        return dt.strftime(fmt)
    
    def is_weekend(self, date_string: str) -> bool:
        """
        Check if a date falls on weekend
        
        Args:
            date_string: Date to check
            
        Returns:
            True if weekend, False otherwise
        """
        dt = self.parse_date(date_string)
        return dt.weekday() >= 5  # 5 = Saturday, 6 = Sunday
    
    def is_leap_year(self, year: Union[int, str]) -> bool:
        """
        Check if a year is a leap year
        
        Args:
            year: Year to check (integer or string)
            
        Returns:
            True if leap year, False otherwise
        """
        if isinstance(year, str):
            year = int(year)
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    
    def get_week_number(self, date_string: str) -> int:
        """
        Get ISO week number for a date
        
        Args:
            date_string: Date to check
            
        Returns:
            ISO week number (1-53)
        """
        dt = self.parse_date(date_string)
        return dt.isocalendar()[1]
    
    def get_day_of_week(self, date_string: str) -> str:
        """
        Get day of week name
        
        Args:
            date_string: Date to check
            
        Returns:
            Day name (Monday, Tuesday, etc.)
        """
        dt = self.parse_date(date_string)
        return dt.strftime('%A')
    
    def get_days_in_month(self, year: int, month: int) -> int:
        """
        Get number of days in a month
        
        Args:
            year: Year number
            month: Month number (1-12)
            
        Returns:
            Number of days in month
        """
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        last_day = next_month - timedelta(days=1)
        return last_day.day
    
    def count_business_days(self, start_date: str, end_date: str) -> int:
        """
        Count business days between two dates (excluding weekends)
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            Number of business days
        """
        start = self.parse_date(start_date)
        end = self.parse_date(end_date)
        
        if start > end:
            start, end = end, start
        
        business_days = 0
        current = start
        while current <= end:
            if current.weekday() < 5:  # Monday = 0, Friday = 4
                business_days += 1
            current += timedelta(days=1)
        
        return business_days
    
    def add_business_days(self, date_string: str, days: int) -> str:
        """
        Add business days to a date (skipping weekends)
        
        Args:
            date_string: Base date
            days: Number of business days to add
            
        Returns:
            Resulting date as ISO format string
        """
        dt = self.parse_date(date_string)
        added = 0
        direction = 1 if days > 0 else -1
        
        while abs(added) < abs(days):
            dt += timedelta(days=direction)
            if dt.weekday() < 5:
                added += direction
        
        return dt.strftime('%Y-%m-%d')
    
    def list_timezones(self, region: Optional[str] = None) -> List[str]:
        """
        List available timezones
        
        Args:
            region: Filter by region (e.g., 'America', 'Europe', 'Asia')
            
        Returns:
            List of timezone names
        """
        if region:
            return [tz for tz in pytz.common_timezones if tz.startswith(region)]
        return list(pytz.common_timezones)
    
    def get_timezone_info(self, timezone: str) -> Dict:
        """
        Get information about a timezone
        
        Args:
            timezone: Timezone name
            
        Returns:
            Dictionary with timezone information
        """
        if timezone not in self._all_timezones:
            raise ValueError(f"Invalid timezone: {timezone}")
        
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        
        return {
            'name': timezone,
            'utc_offset': now.strftime('%z'),
            'dst_active': bool(now.dst()),
            'local_time': now.strftime('%Y-%m-%d %H:%M:%S')
        }


# CLI interface for direct execution
if __name__ == '__main__':
    import sys
    import json
    
    skill = DateTimeSkill()
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <command> [args...]")
        print("Commands: convert, now, add, diff, format")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'convert':
        if len(sys.argv) < 5:
            print("Usage: python main.py convert <date> <from_tz> <to_tz>")
            sys.exit(1)
        result = skill.convert_timezone(sys.argv[2], sys.argv[3], sys.argv[4])
        print(result)
    
    elif command == 'now':
        tz = sys.argv[2] if len(sys.argv) > 2 else 'UTC'
        print(skill.get_current_time(tz))
    
    elif command == 'add':
        if len(sys.argv) < 4:
            print("Usage: python main.py add <date> <days>")
            sys.exit(1)
        result = skill.add_days(sys.argv[2], int(sys.argv[3]))
        print(result)
    
    elif command == 'diff':
        if len(sys.argv) < 4:
            print("Usage: python main.py diff <date1> <date2>")
            sys.exit(1)
        result = skill.date_difference(sys.argv[2], sys.argv[3])
        print(f"Days: {result}")
    
    elif command == 'format':
        if len(sys.argv) < 3:
            print("Usage: python main.py format <date> [format]")
            sys.exit(1)
        fmt = sys.argv[3] if len(sys.argv) > 3 else 'full'
        print(skill.format_date(sys.argv[2], fmt))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
