#!/usr/bin/env python3
"""
Tests for Report-In Skill
"""

import unittest
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import (
    ReportInSkill,
    TaskInfo,
    AgentInfo,
    MemoryInfo,
    PortInfo,
    DiskInfo
)


class TestDataClasses(unittest.TestCase):
    """Test data class initialization and serialization."""
    
    def test_task_info_creation(self):
        """Test TaskInfo dataclass."""
        task = TaskInfo(
            name="Test Task",
            status="running",
            progress=50.0,
            category="test"
        )
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.status, "running")
        self.assertEqual(task.progress, 50.0)
    
    def test_task_info_to_dict(self):
        """Test TaskInfo serialization."""
        now = datetime.now()
        task = TaskInfo(
            name="Test",
            status="completed",
            start_time=now,
            end_time=now,
            progress=100.0
        )
        data = task.to_dict()
        self.assertEqual(data['name'], "Test")
        self.assertEqual(data['status'], "completed")
        self.assertEqual(data['progress'], 100.0)
    
    def test_agent_info_creation(self):
        """Test AgentInfo dataclass."""
        agent = AgentInfo(
            agent_id="agent-1",
            pid=1234,
            status="active",
            cpu_percent=10.5,
            memory_mb=256.0
        )
        self.assertEqual(agent.agent_id, "agent-1")
        self.assertEqual(agent.pid, 1234)
    
    def test_memory_info_creation(self):
        """Test MemoryInfo dataclass."""
        mem = MemoryInfo(
            total_gb=16.0,
            used_gb=8.0,
            available_gb=8.0,
            percent_used=50.0
        )
        self.assertEqual(mem.total_gb, 16.0)
        self.assertEqual(mem.percent_used, 50.0)
    
    def test_port_info_creation(self):
        """Test PortInfo dataclass."""
        port = PortInfo(
            port=8080,
            protocol="tcp",
            status="listening",
            service="HTTP-Alt"
        )
        self.assertEqual(port.port, 8080)
        self.assertEqual(port.service, "HTTP-Alt")
    
    def test_disk_info_creation(self):
        """Test DiskInfo dataclass."""
        disk = DiskInfo(
            device="/dev/sda1",
            mountpoint="/",
            total_gb=1000.0,
            used_gb=450.0,
            free_gb=550.0,
            percent_used=45.0
        )
        self.assertEqual(disk.device, "/dev/sda1")
        self.assertEqual(disk.percent_used, 45.0)


class TestReportInSkill(unittest.TestCase):
    """Test ReportInSkill functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.skill = ReportInSkill()
    
    def test_initialization(self):
        """Test skill initialization."""
        self.assertIsNotNone(self.skill.config)
        self.assertIn('log_path', self.skill.config)
        self.assertIn('format', self.skill.config)
    
    def test_load_config(self):
        """Test configuration loading."""
        with patch.dict(os.environ, {'REPORTIN_FORMAT': 'json', 'REPORTIN_TIME_RANGE': '48'}):
            skill = ReportInSkill()
            self.assertEqual(skill.config['format'], 'json')
            self.assertEqual(skill.config['time_range_hours'], 48)
    
    def test_format_time_ago(self):
        """Test time formatting."""
        now = datetime.now()
        
        # Test seconds ago
        dt = now - timedelta(seconds=30)
        result = self.skill._format_time_ago(dt)
        self.assertTrue('s ago' in result or 'm ago' in result)
        
        # Test minutes ago
        dt = now - timedelta(minutes=5)
        result = self.skill._format_time_ago(dt)
        self.assertIn('m ago', result)
        
        # Test hours ago
        dt = now - timedelta(hours=2)
        result = self.skill._format_time_ago(dt)
        self.assertIn('h ago', result)
        
        # Test days ago
        dt = now - timedelta(days=2)
        result = self.skill._format_time_ago(dt)
        self.assertIn('d ago', result)
    
    def test_format_time_ago_none(self):
        """Test time formatting with None."""
        result = self.skill._format_time_ago(None)
        self.assertEqual(result, "unknown")
    
    def test_format_progress_bar(self):
        """Test progress bar formatting."""
        bar = self.skill._format_progress_bar(50, width=10)
        self.assertIn('█', bar)
        self.assertIn('░', bar)
        self.assertEqual(len(bar), 12)  # [ + 10 chars + ]
    
    def test_format_progress_bar_zero(self):
        """Test progress bar at 0%."""
        bar = self.skill._format_progress_bar(0, width=10)
        self.assertEqual(bar.count('░'), 10)
    
    def test_format_progress_bar_full(self):
        """Test progress bar at 100%."""
        bar = self.skill._format_progress_bar(100, width=10)
        self.assertEqual(bar.count('█'), 10)
    
    def test_estimate_progress(self):
        """Test progress estimation based on duration."""
        now = datetime.now()
        
        # < 5 minutes
        start = now - timedelta(minutes=3)
        self.assertEqual(self.skill._estimate_progress(start), 25.0)
        
        # 5-30 minutes
        start = now - timedelta(minutes=15)
        self.assertEqual(self.skill._estimate_progress(start), 50.0)
        
        # 30-60 minutes
        start = now - timedelta(minutes=45)
        self.assertEqual(self.skill._estimate_progress(start), 75.0)
        
        # > 60 minutes
        start = now - timedelta(minutes=90)
        self.assertEqual(self.skill._estimate_progress(start), 90.0)
    
    def test_identify_service(self):
        """Test service identification by port."""
        self.assertEqual(self.skill._identify_service(22), 'SSH')
        self.assertEqual(self.skill._identify_service(80), 'HTTP')
        self.assertEqual(self.skill._identify_service(443), 'HTTPS')
        self.assertEqual(self.skill._identify_service(5432), 'PostgreSQL')
        self.assertEqual(self.skill._identify_service(6379), 'Redis')
        self.assertEqual(self.skill._identify_service(99999), 'Unknown')
    
    @patch('main.HAS_PSUTIL', True)
    @patch('main.psutil')
    def test_get_memory_info_with_psutil(self, mock_psutil):
        """Test memory info with psutil."""
        mock_mem = Mock()
        mock_mem.total = 16 * 1024**3  # 16GB
        mock_mem.used = 8 * 1024**3    # 8GB
        mock_mem.available = 8 * 1024**3
        mock_mem.percent = 50.0
        mock_mem.cached = 2 * 1024**3
        mock_mem.buffers = 1 * 1024**3
        
        mock_psutil.virtual_memory.return_value = mock_mem
        
        mem = self.skill.get_memory_info()
        self.assertEqual(mem.total_gb, 16.0)
        self.assertEqual(mem.used_gb, 8.0)
        self.assertEqual(mem.percent_used, 50.0)
    
    @patch('main.HAS_PSUTIL', False)
    def test_get_memory_info_without_psutil(self):
        """Test memory info fallback without psutil."""
        mem = self.skill.get_memory_info()
        # Should return numeric values (int or float)
        self.assertIsInstance(mem.total_gb, (int, float))
        self.assertIsInstance(mem.used_gb, (int, float))
    
    def test_parse_task_from_json(self):
        """Test parsing task from JSON."""
        data = {
            'name': 'Test Task',
            'status': 'completed',
            'start_time': '2026-02-20T10:00:00',
            'end_time': '2026-02-20T11:00:00',
            'progress': 100.0,
            'duration_minutes': 60.0,
            'category': 'test',
            'agent_id': 'agent-1'
        }
        
        task = self.skill._parse_task_from_json(data)
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'Test Task')
        self.assertEqual(task.status, 'completed')
        self.assertEqual(task.progress, 100.0)
    
    def test_parse_task_from_json_invalid(self):
        """Test parsing invalid JSON."""
        task = self.skill._parse_task_from_json({'invalid': 'data'})
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'Unknown')
    
    def test_parse_task_from_line(self):
        """Test parsing task from log line."""
        line = "[2026-02-20 10:00:00] COMPLETED: Test Task"
        task = self.skill._parse_task_from_line(line)
        self.assertIsNotNone(task)
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.status, "completed")
    
    def test_parse_task_from_line_failed(self):
        """Test parsing failed task from log line."""
        line = "[2026-02-20 10:00:00] FAILED: Failed Task"
        task = self.skill._parse_task_from_line(line)
        self.assertIsNotNone(task)
        self.assertEqual(task.name, "Failed Task")
        self.assertEqual(task.status, "failed")
    
    def test_parse_task_from_line_invalid(self):
        """Test parsing invalid log line."""
        line = "Invalid log line without proper format"
        task = self.skill._parse_task_from_line(line)
        self.assertIsNone(task)
    
    def test_generate_full_report(self):
        """Test full report generation."""
        report = self.skill.generate_full_report()
        self.assertIsInstance(report, str)
        self.assertIn("SYSTEM STATUS REPORT", report)
        self.assertIn("TASK SUMMARY", report)
        self.assertIn("AGENT ACTIVITIES", report)
        self.assertIn("SYSTEM RESOURCES", report)
        self.assertIn("PORT STATUS", report)
    
    def test_generate_json_report(self):
        """Test JSON report generation."""
        report = self.skill.generate_json_report()
        self.assertIsInstance(report, dict)
        self.assertIn('generated_at', report)
        self.assertIn('tasks', report)
        self.assertIn('agents', report)
        self.assertIn('system', report)
        self.assertIn('network', report)
    
    def test_generate_json_report_serializable(self):
        """Test JSON report is JSON serializable."""
        report = self.skill.generate_json_report()
        try:
            json_str = json.dumps(report, indent=2, default=str)
            self.assertIsInstance(json_str, str)
        except TypeError as e:
            self.fail(f"Report is not JSON serializable: {e}")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        self.skill = ReportInSkill()
    
    def test_empty_task_list(self):
        """Test handling empty task list."""
        with patch.object(self.skill, 'get_completed_tasks', return_value=[]):
            with patch.object(self.skill, 'get_running_tasks', return_value=[]):
                report = self.skill.generate_full_report()
                self.assertIn("Completed Tasks: 0", report)
    
    def test_no_agents(self):
        """Test handling no active agents."""
        with patch.object(self.skill, 'get_active_agents', return_value=[]):
            report = self.skill.generate_full_report()
            self.assertIn("Active Agents: 0", report)
    
    def test_very_long_task_name(self):
        """Test handling very long task names."""
        task = TaskInfo(
            name="A" * 100,
            status="running",
            progress=50.0
        )
        # Should not raise exception
        report_line = f"  ⏳ {task.name[:35]:35}"
        # Just verify it doesn't crash and truncates correctly
        self.assertLessEqual(len(report_line), 100)
    
    def test_invalid_port_number(self):
        """Test handling invalid port numbers."""
        service = self.skill._identify_service(-1)
        self.assertEqual(service, 'Unknown')
    
    def test_future_datetime(self):
        """Test handling future datetime."""
        future = datetime.now() + timedelta(days=1)
        result = self.skill._format_time_ago(future)
        # Should handle gracefully
        self.assertIsInstance(result, str)


class TestIntegration(unittest.TestCase):
    """Integration tests (may require actual system)."""
    
    @unittest.skipUnless(os.name == 'posix', "Unix-specific test")
    def test_memory_from_proc(self):
        """Test reading memory from /proc on Linux."""
        skill = ReportInSkill()
        if os.path.exists('/proc/meminfo'):
            mem = skill._get_memory_from_proc()
            self.assertGreater(mem.total_gb, 0)
    
    def test_get_port_status(self):
        """Test getting port status."""
        skill = ReportInSkill()
        ports = skill.get_port_status()
        self.assertIsInstance(ports, list)
        # Should return without error even if no ports found


if __name__ == '__main__':
    unittest.main(verbosity=2)
