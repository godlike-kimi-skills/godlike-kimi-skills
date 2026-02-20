#!/usr/bin/env python3
"""
Tests for Cron Skill
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from main import CronSkill, CronSchedule


class TestCronSkill:
    """Test cases for CronSkill"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.skill = CronSkill()
        self.base_time = datetime(2024, 1, 15, 10, 30, 0)  # Monday 10:30 AM
    
    def test_parse_simple(self):
        """Test parsing simple expression"""
        schedule, error = self.skill.parse('0 0 * * *')
        assert error is None
        assert schedule.minute.allowed_values == [0]
        assert schedule.hour.allowed_values == [0]
    
    def test_parse_asterisk(self):
        """Test parsing asterisk"""
        schedule, error = self.skill.parse('* * * * *')
        assert error is None
        assert schedule.minute.allowed_values == list(range(60))
        assert schedule.hour.allowed_values == list(range(24))
    
    def test_parse_step(self):
        """Test parsing step expression"""
        schedule, error = self.skill.parse('*/5 * * * *')
        assert error is None
        assert schedule.minute.allowed_values == list(range(0, 60, 5))
    
    def test_parse_range(self):
        """Test parsing range expression"""
        schedule, error = self.skill.parse('0 9-17 * * *')
        assert error is None
        assert schedule.hour.allowed_values == list(range(9, 18))
    
    def test_parse_list(self):
        """Test parsing list expression"""
        schedule, error = self.skill.parse('0,30 * * * *')
        assert error is None
        assert schedule.minute.allowed_values == [0, 30]
    
    def test_parse_invalid_fields_count(self):
        """Test parsing with wrong number of fields"""
        schedule, error = self.skill.parse('0 0 * *')
        assert schedule is None
        assert '5 fields' in error
    
    def test_parse_invalid_value(self):
        """Test parsing with invalid value"""
        schedule, error = self.skill.parse('70 * * * *')
        assert schedule is None
        assert 'out of bounds' in error.lower()
    
    def test_parse_invalid_range(self):
        """Test parsing with invalid range"""
        schedule, error = self.skill.parse('0 25 * * *')
        assert schedule is None
    
    def test_parse_preset_yearly(self):
        """Test parsing @yearly preset"""
        schedule, error = self.skill.parse('@yearly')
        assert error is None
        assert schedule.minute.allowed_values == [0]
        assert schedule.hour.allowed_values == [0]
        assert schedule.day_of_month.allowed_values == [1]
        assert schedule.month.allowed_values == [1]
    
    def test_parse_preset_daily(self):
        """Test parsing @daily preset"""
        schedule, error = self.skill.parse('@daily')
        assert error is None
        assert schedule.minute.allowed_values == [0]
        assert schedule.hour.allowed_values == [0]
    
    def test_validate_valid(self):
        """Test validating valid expression"""
        is_valid, error = self.skill.validate('0 0 * * *')
        assert is_valid is True
        assert error is None
    
    def test_validate_invalid(self):
        """Test validating invalid expression"""
        is_valid, error = self.skill.validate('invalid')
        assert is_valid is False
        assert error is not None
    
    def test_get_next_simple(self):
        """Test getting next execution time"""
        next_time, error = self.skill.get_next('0 11 * * *', self.base_time)
        assert error is None
        assert next_time.hour == 11
        assert next_time.minute == 0
        assert next_time > self.base_time
    
    def test_get_next_same_hour(self):
        """Test getting next execution in same hour"""
        next_time, error = self.skill.get_next('35 * * * *', self.base_time)
        assert error is None
        assert next_time.hour == 10
        assert next_time.minute == 35
    
    def test_get_next_next_day(self):
        """Test getting next execution next day"""
        next_time, error = self.skill.get_next('0 9 * * *', self.base_time)
        assert error is None
        # Since it's 10:30 now, next 9:00 is tomorrow
        assert next_time.day == 16
        assert next_time.hour == 9
    
    def test_get_next_weekday(self):
        """Test getting next weekday execution"""
        # Every Monday at 9 AM (Monday=0 in Python, but 1 in cron)
        # Actually, in standard cron: 0=Sunday, 1=Monday
        next_time, error = self.skill.get_next('0 9 * * 1', self.base_time)
        assert error is None
        assert next_time.weekday() == 0  # Monday (Python: Monday=0)
        assert next_time.hour == 9
    
    def test_get_next_n(self):
        """Test getting multiple next execution times"""
        times, error = self.skill.get_next_n('0 11 * * *', n=3, from_time=self.base_time)
        assert error is None
        assert len(times) == 3
        # All should be at 11:00
        for t in times:
            assert t.hour == 11
            assert t.minute == 0
    
    def test_describe_every_minute(self):
        """Test describing every minute"""
        description, error = self.skill.describe('* * * * *')
        assert error is None
        assert 'Every minute' in description or 'every minute' in description
    
    def test_describe_daily(self):
        """Test describing daily"""
        description, error = self.skill.describe('0 0 * * *')
        assert error is None
        assert 'midnight' in description.lower()
    
    def test_describe_hourly(self):
        """Test describing hourly"""
        description, error = self.skill.describe('0 * * * *')
        assert error is None
        assert 'hour' in description.lower()
    
    def test_describe_weekday(self):
        """Test describing weekday"""
        description, error = self.skill.describe('0 9 * * 1-5')
        assert error is None
        assert 'Monday' in description or 'weekday' in description.lower()
    
    def test_describe_preset(self):
        """Test describing preset"""
        description, error = self.skill.describe('@daily')
        assert error is None
        assert 'midnight' in description.lower()
    
    def test_generate_every_minute(self):
        """Test generating every minute"""
        expression, error = self.skill.generate('every minute')
        assert error is None
        assert expression == '* * * * *'
    
    def test_generate_every_5_minutes(self):
        """Test generating every 5 minutes"""
        expression, error = self.skill.generate('every 5 minutes')
        assert error is None
        assert expression == '*/5 * * * *'
    
    def test_generate_every_hour(self):
        """Test generating every hour"""
        expression, error = self.skill.generate('every hour')
        assert error is None
        assert expression == '0 * * * *'
    
    def test_generate_daily(self):
        """Test generating daily"""
        expression, error = self.skill.generate('daily')
        assert error is None
        assert expression == '0 0 * * *'
    
    def test_generate_at_time(self):
        """Test generating at specific time"""
        expression, error = self.skill.generate('at 9:30')
        assert error is None
        assert expression == '30 9 * * *'
    
    def test_generate_unknown(self):
        """Test generating unknown description"""
        expression, error = self.skill.generate('something impossible xyz')
        assert expression is None
        assert error is not None
    
    def test_get_field_info(self):
        """Test getting field information"""
        fields = self.skill.get_field_info()
        assert 'minute' in fields
        assert 'hour' in fields
        assert 'day_of_month' in fields
        assert 'month' in fields
        assert 'day_of_week' in fields
    
    def test_get_presets(self):
        """Test getting presets"""
        presets = self.skill.get_presets()
        assert '@yearly' in presets
        assert '@daily' in presets
        assert '@hourly' in presets
    
    def test_is_scheduled(self):
        """Test _is_scheduled method"""
        schedule, _ = self.skill.parse('0 10 * * *')  # 10:00 AM
        
        dt_match = datetime(2024, 1, 15, 10, 0, 0)
        dt_no_match = datetime(2024, 1, 15, 11, 0, 0)
        
        assert self.skill._is_scheduled(dt_match, schedule) is True
        assert self.skill._is_scheduled(dt_no_match, schedule) is False
    
    def test_complex_expression(self):
        """Test complex expression with multiple constraints"""
        # Every 15 minutes, during business hours, on weekdays
        schedule, error = self.skill.parse('*/15 9-17 * * 1-5')
        assert error is None
        assert schedule.minute.allowed_values == [0, 15, 30, 45]
        assert schedule.hour.allowed_values == list(range(9, 18))
        assert schedule.day_of_week.allowed_values == [1, 2, 3, 4, 5]
    
    def test_step_with_range(self):
        """Test step with range"""
        schedule, error = self.skill.parse('1-30/5 * * * *')
        assert error is None
        assert schedule.minute.allowed_values == [1, 6, 11, 16, 21, 26]


def run_tests():
    """Run all tests"""
    import pytest
    pytest.main([__file__, '-v'])


if __name__ == '__main__':
    run_tests()
