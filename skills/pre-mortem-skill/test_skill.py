#!/usr/bin/env python3
"""
Tests for Pre-Mortem Skill
"""

import unittest
import json
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import (
    PreMortemSkill,
    Risk,
    PreMortemSession,
    RiskLevel,
    RiskCategory
)


class TestRisk(unittest.TestCase):
    """Test Risk dataclass."""
    
    def test_risk_creation(self):
        """Test creating a Risk object."""
        risk = Risk(
            description="Test risk",
            category=RiskCategory.TECHNICAL,
            probability=RiskLevel.HIGH,
            impact=RiskLevel.HIGH,
            prevention_actions=["Action 1", "Action 2"],
            early_warnings=["Warning 1"]
        )
        
        self.assertEqual(risk.description, "Test risk")
        self.assertEqual(risk.category, RiskCategory.TECHNICAL)
        self.assertEqual(risk.probability, RiskLevel.HIGH)
        self.assertEqual(risk.impact, RiskLevel.HIGH)
    
    def test_risk_score(self):
        """Test risk score calculation."""
        # High probability + High impact = 25
        risk = Risk(
            description="Critical risk",
            category=RiskCategory.TECHNICAL,
            probability=RiskLevel.CRITICAL,
            impact=RiskLevel.CRITICAL,
            prevention_actions=[],
            early_warnings=[]
        )
        self.assertEqual(risk.risk_score, 25)
        
        # Medium probability + Medium impact = 9
        risk2 = Risk(
            description="Medium risk",
            category=RiskCategory.PROCESS,
            probability=RiskLevel.MEDIUM,
            impact=RiskLevel.MEDIUM,
            prevention_actions=[],
            early_warnings=[]
        )
        self.assertEqual(risk2.risk_score, 9)
    
    def test_risk_priority_critical(self):
        """Test priority calculation for critical risk."""
        risk = Risk(
            description="Critical",
            category=RiskCategory.TECHNICAL,
            probability=RiskLevel.HIGH,
            impact=RiskLevel.CRITICAL,
            prevention_actions=[],
            early_warnings=[]
        )
        self.assertIn("CRITICAL", risk.priority)
        self.assertIn("🔴", risk.priority)
    
    def test_risk_priority_low(self):
        """Test priority calculation for low risk."""
        risk = Risk(
            description="Low",
            category=RiskCategory.TECHNICAL,
            probability=RiskLevel.LOW,
            impact=RiskLevel.LOW,
            prevention_actions=[],
            early_warnings=[]
        )
        self.assertIn("LOW", risk.priority)
        self.assertIn("🟢", risk.priority)
    
    def test_risk_to_dict(self):
        """Test Risk serialization."""
        risk = Risk(
            description="Test",
            category=RiskCategory.USER,
            probability=RiskLevel.MEDIUM,
            impact=RiskLevel.HIGH,
            prevention_actions=["Action"],
            early_warnings=["Warning"]
        )
        
        data = risk.to_dict()
        self.assertEqual(data['description'], "Test")
        self.assertEqual(data['category'], "user")
        self.assertEqual(data['probability'], "medium")
        self.assertEqual(data['impact'], "high")


class TestPreMortemSession(unittest.TestCase):
    """Test PreMortemSession dataclass."""
    
    def test_session_creation(self):
        """Test creating a session."""
        session = PreMortemSession(
            project_name="Test Project",
            project_description="A test project",
            timeline="3 months",
            stakeholders=["Alice", "Bob"],
            created_at=datetime.now(),
            risks=[]
        )
        
        self.assertEqual(session.project_name, "Test Project")
        self.assertEqual(len(session.stakeholders), 2)
    
    def test_session_to_dict(self):
        """Test session serialization."""
        session = PreMortemSession(
            project_name="Test",
            project_description="Desc",
            timeline="1 month",
            stakeholders=["Team"],
            created_at=datetime(2026, 1, 1),
            risks=[
                Risk(
                    description="Risk 1",
                    category=RiskCategory.TECHNICAL,
                    probability=RiskLevel.HIGH,
                    impact=RiskLevel.MEDIUM,
                    prevention_actions=["Fix it"],
                    early_warnings=["Watch it"]
                )
            ]
        )
        
        data = session.to_dict()
        self.assertEqual(data['project_name'], "Test")
        self.assertEqual(len(data['risks']), 1)


class TestPreMortemSkill(unittest.TestCase):
    """Test PreMortemSkill functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.skill = PreMortemSkill()
    
    def test_start_session(self):
        """Test starting a new session."""
        session = self.skill.start_session(
            project_name="Mobile App",
            description="A mobile app project",
            timeline="6 months",
            stakeholders=["Dev Team", "Product Manager"]
        )
        
        self.assertIsNotNone(self.skill.session)
        self.assertEqual(session.project_name, "Mobile App")
        self.assertEqual(len(session.stakeholders), 2)
    
    def test_generate_risk_library(self):
        """Test risk library generation."""
        risks = self.skill.generate_risk_library()
        
        self.assertGreater(len(risks), 0)
        
        # Check that risks are sorted by score
        for i in range(len(risks) - 1):
            self.assertGreaterEqual(
                risks[i].risk_score,
                risks[i + 1].risk_score
            )
    
    def test_add_custom_risk(self):
        """Test adding custom risk."""
        self.skill.start_session(
            project_name="Test",
            description="Test",
            timeline="1 month",
            stakeholders=["Team"]
        )
        
        risk = self.skill.add_custom_risk(
            description="Custom risk",
            category=RiskCategory.PEOPLE,
            probability=RiskLevel.HIGH,
            impact=RiskLevel.HIGH,
            prevention=["Action 1"],
            warnings=["Warning 1"]
        )
        
        self.assertEqual(risk.description, "Custom risk")
        self.assertEqual(len(self.skill.session.risks), 1)
    
    def test_generate_report_no_session(self):
        """Test report generation without session."""
        report = self.skill.generate_report()
        self.assertIn("No active session", report)
    
    def test_generate_report_with_session(self):
        """Test report generation with active session."""
        self.skill.start_session(
            project_name="Test Project",
            description="A test project",
            timeline="3 months",
            stakeholders=["Team A", "Team B"]
        )
        
        # Add some risks
        self.skill.session.risks = [
            Risk(
                description="Technical debt",
                category=RiskCategory.TECHNICAL,
                probability=RiskLevel.HIGH,
                impact=RiskLevel.HIGH,
                prevention_actions=["Code reviews", "Refactoring"],
                early_warnings=["Slow builds"]
            ),
            Risk(
                description="Timeline slip",
                category=RiskCategory.PROCESS,
                probability=RiskLevel.MEDIUM,
                impact=RiskLevel.MEDIUM,
                prevention_actions=["Buffer time"],
                early_warnings=["Missed milestones"]
            )
        ]
        
        report = self.skill.generate_report()
        
        # Check report contains expected sections
        self.assertIn("PRE-MORTEM ANALYSIS", report)
        self.assertIn("Test Project", report)
        self.assertIn("Technical debt", report)
        self.assertIn("Timeline slip", report)
        self.assertIn("CRITICAL", report)
        self.assertIn("Code reviews", report)
        self.assertIn("Slow builds", report)
    
    def test_generate_template_markdown(self):
        """Test Markdown template generation."""
        template = self.skill.generate_template("markdown")
        
        self.assertIn("# Pre-Mortem Analysis Worksheet", template)
        self.assertIn("Project Information", template)
        self.assertIn("Failure Path Analysis", template)
        self.assertIn("Risk Prioritization Matrix", template)
    
    def test_generate_template_json(self):
        """Test JSON template generation."""
        template = self.skill.generate_template("json")
        
        # Should be valid JSON
        data = json.loads(template)
        self.assertIn("project_name", data)
        self.assertIn("risks", data)
    
    def test_generate_template_text(self):
        """Test plain text template generation."""
        template = self.skill.generate_template("text")
        
        self.assertIn("PRE-MORTEM WORKSHEET", template)
        self.assertIn("PROJECT:", template)
        self.assertIn("FAILURE PATHS:", template)
    
    def test_parse_timeline_months(self):
        """Test timeline parsing for months."""
        delta = self.skill._parse_timeline("3 months")
        self.assertEqual(delta.days, 90)
    
    def test_parse_timeline_weeks(self):
        """Test timeline parsing for weeks."""
        delta = self.skill._parse_timeline("4 weeks")
        self.assertEqual(delta.days, 28)
    
    def test_parse_timeline_default(self):
        """Test timeline parsing default."""
        delta = self.skill._parse_timeline("invalid")
        self.assertEqual(delta.days, 90)


class TestRiskCategories(unittest.TestCase):
    """Test risk categories and patterns."""
    
    def test_failure_patterns_exist(self):
        """Test that failure patterns are defined."""
        skill = PreMortemSkill()
        
        self.assertIn(RiskCategory.TECHNICAL, skill.FAILURE_PATTERNS)
        self.assertIn(RiskCategory.PEOPLE, skill.FAILURE_PATTERNS)
        self.assertIn(RiskCategory.PROCESS, skill.FAILURE_PATTERNS)
        self.assertIn(RiskCategory.EXTERNAL, skill.FAILURE_PATTERNS)
        self.assertIn(RiskCategory.USER, skill.FAILURE_PATTERNS)
        self.assertIn(RiskCategory.FINANCIAL, skill.FAILURE_PATTERNS)
    
    def test_prevention_templates_exist(self):
        """Test that prevention templates are defined."""
        skill = PreMortemSkill()
        
        self.assertGreater(len(skill.PREVENTION_TEMPLATES), 0)
        self.assertIn("Technical debt accumulated too fast", 
                     skill.PREVENTION_TEMPLATES)
    
    def test_early_warning_signs_exist(self):
        """Test that early warning signs are defined."""
        skill = PreMortemSkill()
        
        self.assertGreater(len(skill.EARLY_WARNING_SIGNS), 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases."""
    
    def test_empty_prevention_actions(self):
        """Test risk with empty prevention actions."""
        risk = Risk(
            description="Test",
            category=RiskCategory.TECHNICAL,
            probability=RiskLevel.LOW,
            impact=RiskLevel.LOW,
            prevention_actions=[],
            early_warnings=[]
        )
        
        self.assertEqual(risk.prevention_actions, [])
        self.assertEqual(risk.risk_score, 4)  # 2 * 2
    
    def test_very_long_project_name(self):
        """Test handling very long project name."""
        skill = PreMortemSkill()
        long_name = "A" * 100
        
        session = skill.start_session(
            project_name=long_name,
            description="Test",
            timeline="1 month",
            stakeholders=["Team"]
        )
        
        report = skill.generate_report()
        # Should not crash
        self.assertIn("PRE-MORTEM", report)


if __name__ == '__main__':
    unittest.main(verbosity=2)
