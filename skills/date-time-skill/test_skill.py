#!/usr/bin/env python3
"""
Tests for Date Time Skill
"""

import unittest
from datetime import datetime
from skills.date_time_skill.main import DateTimeSkill


class TestDateTimeSkill(unittest.TestCase):
    """Test cases for DateTimeSkill"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.skill = DateTimeSkill()
    
    def test_parse_date(self):
        """Test date parsing"""
        dt = self.skill.parse_date("2026-02-20")
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 2)
        self.assertEqual(dt.day, 20)
    
    def test_convert_timezone(self):
        """Test timezone conversion"""
        # Convert UTC to a known timezone
        result = self.skill.convert_timezone(
            "2026-02-20 12:00:00", 
            "UTC", 
            "Asia/Shanghai"
        )
        # Shanghai is UTC+8
        self.assertIn("20:00:00", result)
    
    def test_add_days(self):
        """Test adding days"""
        result = self.skill.add_days("2026-02-20", 10)
        self.assertEqual(result, "2026-03-02")
    
    def test_add_days_negative(self):
        """Test subtracting days"""
        result = self.skill.add_days("2026-02-20", -10)
        self.assertEqual(result, "2026-02-10")
    
    def test_add_months(self):
        """Test adding months"""
        result = self.skill.add_months("2026-01-15", 3)
        self.assertEqual(result, "2026-04-15")
    
    def test_add_years(self):
        """Test adding years"""
        result = self.skill.add_years("2026-06-15", 5)
        self.assertEqual(result, "2031-06-15")
    
    def test_date_difference_days(self):
        """Test date difference in days"""
        result = self.skill.date_difference("2026-01-01", "2026-01-31")
        self.assertEqual(result, 30)
    
    def test_date_difference_weeks(self):
        """Test date difference in weeks"""
        result = self.skill.date_difference("2026-01-01", "2026-01-15", unit='weeks')
        self.assertAlmostEqual(result, 2.0, places=0)
    
    def test_is_weekend_true(self):
        """Test weekend detection (true case)"""
        # 2026-02-21 is Saturday
        result = self.skill.is_weekend("2026-02-21")
        self.assertTrue(result)
    
    def test_is_weekend_false(self):
        """Test weekend detection (false case)"""
        # 2026-02-20 is Friday
        result = self.skill.is_weekend("2026-02-20")
        self.assertFalse(result)
    
    def test_is_leap_year_true(self):
        """Test leap year detection (true)"""
        result = self.skill.is_leap_year(2024)
        self.assertTrue(result)
    
    def test_is_leap_year_false(self):
        """Test leap year detection (false)"""
        result = self.skill.is_leap_year(2025)
        self.assertFalse(result)
    
    def test_get_week_number(self):
        """Test week number calculation"""
        result = self.skill.get_week_number("2026-01-01")
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 1)
        self.assertLessEqual(result, 53)
    
    def test_get_day_of_week(self):
        """Test day of week"""
        # 2026-02-20 is Friday
        result = self.skill.get_day_of_week("2026-02-20")
        self.assertEqual(result, "Friday")
    
    def test_get_days_in_month(self):
        """Test days in month"""
        # February 2026 (non-leap year)
        result = self.skill.get_days_in_month(2026, 2)
        self.assertEqual(result, 28)
        
        # February 2024 (leap year)
        result = self.skill.get_days_in_month(2024, 2)
        self.assertEqual(result, 29)
    
    def test_count_business_days(self):
        """Test business day counting"""
        # A week should have 5 business days
        result = self.skill.count_business_days("2026-02-16", "2026-02-22")
        self.assertEqual(result, 5)
    
    def test_add_business_days(self):
        """Test adding business days"""
        # Starting from Monday, add 5 business days = Friday
        result = self.skill.add_business_days("2026-02-16", 5)
        self.assertEqual(result, "2026-02-23")  # Skips weekend
    
    def test_format_date_iso(self):
        """Test ISO date formatting"""
        result = self.skill.format_date("2026-02-20", "iso_date")
        self.assertEqual(result, "2026-02-20")
    
    def test_list_timezones(self):
        """Test timezone listing"""
        zones = self.skill.list_timezones()
        self.assertGreater(len(zones), 400)
        self.assertIn("UTC", zones)
    
    def test_list_timezones_filtered(self):
        """Test filtered timezone listing"""
        zones = self.skill.list_timezones("America")
        self.assertTrue(all(z.startswith("America") for z in zones))
    
    def test_get_timezone_info(self):
        """Test timezone info"""
        info = self.skill.get_timezone_info("UTC")
        self.assertEqual(info['name'], "UTC")
        self.assertIn('utc_offset', info)


if __name__ == '__main__':
    unittest.main()
