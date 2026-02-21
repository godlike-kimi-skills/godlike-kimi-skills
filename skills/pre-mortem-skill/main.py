#!/usr/bin/env python3
"""
Pre-Mortem Skill - Risk Analysis & Failure Prevention Tool

Helps teams identify potential failure points before starting projects.
Based on Gary Klein's research showing 30% improvement in risk identification.
"""

import os
import sys
import json
import argparse
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Fix encoding on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class RiskLevel(Enum):
    """Risk severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class RiskCategory(Enum):
    """Categories of project risks."""
    TECHNICAL = "technical"
    PEOPLE = "people"
    PROCESS = "process"
    EXTERNAL = "external"
    USER = "user"
    FINANCIAL = "financial"


@dataclass
class Risk:
    """Represents a potential project risk."""
    description: str
    category: RiskCategory
    probability: RiskLevel
    impact: RiskLevel
    prevention_actions: List[str]
    early_warnings: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'description': self.description,
            'category': self.category.value,
            'probability': self.probability.value,
            'impact': self.impact.value,
            'prevention_actions': self.prevention_actions,
            'early_warnings': self.early_warnings
        }
    
    @property
    def risk_score(self) -> int:
        """Calculate risk score (1-25)."""
        prob_scores = {
            RiskLevel.CRITICAL: 5,
            RiskLevel.HIGH: 4,
            RiskLevel.MEDIUM: 3,
            RiskLevel.LOW: 2,
            RiskLevel.MINIMAL: 1
        }
        return prob_scores.get(self.probability, 3) * prob_scores.get(self.impact, 3)
    
    @property
    def priority(self) -> str:
        """Get priority label based on risk matrix."""
        if self.probability in [RiskLevel.HIGH, RiskLevel.CRITICAL] and \
           self.impact in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return "🔴 CRITICAL - Act Immediately"
        elif self.probability in [RiskLevel.HIGH, RiskLevel.CRITICAL] or \
             self.impact in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return "🟠 HIGH - Monitor Closely"
        elif self.probability == RiskLevel.MEDIUM and self.impact == RiskLevel.MEDIUM:
            return "🟡 MEDIUM - Track Regularly"
        else:
            return "🟢 LOW - Accept/Monitor"


@dataclass
class PreMortemSession:
    """Represents a pre-mortem analysis session."""
    project_name: str
    project_description: str
    timeline: str
    stakeholders: List[str]
    created_at: datetime
    risks: List[Risk]
    
    def to_dict(self) -> Dict:
        return {
            'project_name': self.project_name,
            'project_description': self.project_description,
            'timeline': self.timeline,
            'stakeholders': self.stakeholders,
            'created_at': self.created_at.isoformat(),
            'risks': [r.to_dict() for r in self.risks]
        }


class PreMortemSkill:
    """Main skill class for conducting pre-mortem analysis."""
    
    # Common failure patterns by category
    FAILURE_PATTERNS = {
        RiskCategory.TECHNICAL: [
            ("Technical debt accumulated too fast", RiskLevel.HIGH, RiskLevel.HIGH),
            ("Third-party API/service failures", RiskLevel.MEDIUM, RiskLevel.HIGH),
            ("Scalability issues under load", RiskLevel.MEDIUM, RiskLevel.CRITICAL),
            ("Security vulnerabilities discovered", RiskLevel.LOW, RiskLevel.CRITICAL),
            ("Integration complexity underestimated", RiskLevel.HIGH, RiskLevel.MEDIUM),
            ("Legacy system compatibility issues", RiskLevel.MEDIUM, RiskLevel.MEDIUM),
            ("Data migration failures", RiskLevel.LOW, RiskLevel.HIGH),
            ("Testing coverage insufficient", RiskLevel.HIGH, RiskLevel.MEDIUM),
        ],
        RiskCategory.PEOPLE: [
            ("Key team member leaves", RiskLevel.MEDIUM, RiskLevel.HIGH),
            ("Skill gaps not identified early", RiskLevel.MEDIUM, RiskLevel.MEDIUM),
            ("Team burnout from tight deadlines", RiskLevel.HIGH, RiskLevel.MEDIUM),
            ("Communication breakdown", RiskLevel.MEDIUM, RiskLevel.HIGH),
            ("New hire onboarding delays", RiskLevel.MEDIUM, RiskLevel.LOW),
            ("Knowledge silos create bottlenecks", RiskLevel.HIGH, RiskLevel.MEDIUM),
            ("Conflicting priorities across teams", RiskLevel.HIGH, RiskLevel.MEDIUM),
            ("Remote work collaboration issues", RiskLevel.MEDIUM, RiskLevel.MEDIUM),
        ],
        RiskCategory.PROCESS: [
            ("Timeline unrealistic", RiskLevel.HIGH, RiskLevel.HIGH),
            ("Requirements change frequently", RiskLevel.HIGH, RiskLevel.MEDIUM),
            ("Decision-making too slow", RiskLevel.MEDIUM, RiskLevel.MEDIUM),
            ("Budget overruns", RiskLevel.MEDIUM, RiskLevel.HIGH),
            ("Scope creep uncontrolled", RiskLevel.HIGH, RiskLevel.MEDIUM),
            ("Quality gates skipped", RiskLevel.MEDIUM, RiskLevel.HIGH),
            ("Documentation neglected", RiskLevel.HIGH, RiskLevel.LOW),
            ("Vendor delays", RiskLevel.MEDIUM, RiskLevel.MEDIUM),
        ],
        RiskCategory.EXTERNAL: [
            ("Market conditions change", RiskLevel.MEDIUM, RiskLevel.HIGH),
            ("Competitor launches first", RiskLevel.LOW, RiskLevel.HIGH),
            ("New regulations affect product", RiskLevel.LOW, RiskLevel.CRITICAL),
            ("Supply chain disruptions", RiskLevel.LOW, RiskLevel.HIGH),
            ("Economic downturn", RiskLevel.LOW, RiskLevel.HIGH),
            ("Customer needs shift", RiskLevel.MEDIUM, RiskLevel.HIGH),
            ("Technology becomes obsolete", RiskLevel.LOW, RiskLevel.CRITICAL),
            ("Partnership falls through", RiskLevel.LOW, RiskLevel.MEDIUM),
        ],
        RiskCategory.USER: [
            ("User adoption lower than expected", RiskLevel.MEDIUM, RiskLevel.CRITICAL),
            ("Product-market fit not achieved", RiskLevel.MEDIUM, RiskLevel.CRITICAL),
            ("User experience confusing", RiskLevel.MEDIUM, RiskLevel.HIGH),
            ("Onboarding friction too high", RiskLevel.HIGH, RiskLevel.MEDIUM),
            ("Customer support overwhelmed", RiskLevel.MEDIUM, RiskLevel.MEDIUM),
            ("Negative viral feedback", RiskLevel.LOW, RiskLevel.CRITICAL),
            ("Accessibility issues discovered", RiskLevel.LOW, RiskLevel.MEDIUM),
            ("Mobile experience poor", RiskLevel.MEDIUM, RiskLevel.HIGH),
        ],
        RiskCategory.FINANCIAL: [
            ("Revenue projections too optimistic", RiskLevel.MEDIUM, RiskLevel.HIGH),
            ("Hidden costs emerge", RiskLevel.MEDIUM, RiskLevel.MEDIUM),
            ("Pricing strategy fails", RiskLevel.LOW, RiskLevel.HIGH),
            ("Funding runs out", RiskLevel.LOW, RiskLevel.CRITICAL),
            ("Currency/exchange rate impact", RiskLevel.LOW, RiskLevel.MEDIUM),
            ("Payment system issues", RiskLevel.LOW, RiskLevel.HIGH),
        ]
    }
    
    PREVENTION_TEMPLATES = {
        "Technical debt accumulated too fast": [
            "Set code quality gates in CI/CD pipeline",
            "Allocate 20% time for refactoring",
            "Conduct weekly architecture reviews",
            "Measure and track technical debt metrics"
        ],
        "Key team member leaves": [
            "Document all critical knowledge",
            "Cross-train team members",
            "Identify and develop backups for key roles",
            "Maintain competitive compensation"
        ],
        "Timeline unrealistic": [
            "Add 30% buffer to estimates",
            "Break into milestones with checkpoints",
            "Identify parallelizable work streams",
            "Plan for iterative delivery"
        ],
        "User adoption lower than expected": [
            "Conduct 20+ user interviews pre-launch",
            "Build MVP for beta testing",
            "Create detailed onboarding flow",
            "Plan marketing campaign in advance"
        ],
    }
    
    EARLY_WARNING_SIGNS = {
        "Technical debt": [
            "Bug count increasing",
            "Developer velocity decreasing",
            "Build times getting longer"
        ],
        "Team burnout": [
            "Increasing overtime",
            "Missed personal deadlines",
            "Declining meeting participation"
        ],
        "Timeline risk": [
            "First milestone delayed",
            "Scope increases without time adjustment",
            "Dependencies not ready"
        ],
    }
    
    def __init__(self):
        self.session: Optional[PreMortemSession] = None
    
    def start_session(self, project_name: str, description: str, 
                     timeline: str, stakeholders: List[str]) -> PreMortemSession:
        """Initialize a new pre-mortem session."""
        self.session = PreMortemSession(
            project_name=project_name,
            project_description=description,
            timeline=timeline,
            stakeholders=stakeholders,
            created_at=datetime.now(),
            risks=[]
        )
        return self.session
    
    def generate_risk_library(self, project_type: str = "general") -> List[Risk]:
        """Generate a library of potential risks based on project patterns."""
        risks = []
        
        for category, patterns in self.FAILURE_PATTERNS.items():
            for pattern_desc, prob, impact in patterns[:3]:  # Top 3 per category
                prevention = self.PREVENTION_TEMPLATES.get(
                    pattern_desc, 
                    ["Create specific prevention plan", "Set up monitoring", "Assign owner"]
                )
                
                early_warnings = []
                for key, signs in self.EARLY_WARNING_SIGNS.items():
                    if key.lower() in pattern_desc.lower():
                        early_warnings = signs
                        break
                
                if not early_warnings:
                    early_warnings = ["Track metrics weekly", "Set up alerts", "Regular retrospectives"]
                
                risk = Risk(
                    description=pattern_desc,
                    category=category,
                    probability=prob,
                    impact=impact,
                    prevention_actions=prevention,
                    early_warnings=early_warnings
                )
                risks.append(risk)
        
        # Sort by risk score
        risks.sort(key=lambda r: r.risk_score, reverse=True)
        return risks
    
    def add_custom_risk(self, description: str, category: RiskCategory,
                       probability: RiskLevel, impact: RiskLevel,
                       prevention: List[str], warnings: List[str]) -> Risk:
        """Add a custom risk to the session."""
        risk = Risk(
            description=description,
            category=category,
            probability=probability,
            impact=impact,
            prevention_actions=prevention,
            early_warnings=warnings
        )
        if self.session:
            self.session.risks.append(risk)
        return risk
    
    def generate_report(self) -> str:
        """Generate a formatted pre-mortem report."""
        if not self.session:
            return "No active session. Start a session first."
        
        lines = []
        
        # Header
        lines.extend([
            "╔═══════════════════════════════════════════════════════════╗",
            "║                   🔮 PRE-MORTEM ANALYSIS                  ║",
            f"║              Project: {self.session.project_name[:40]:40} ║",
            "╚═══════════════════════════════════════════════════════════╝",
            ""
        ])
        
        # Scenario Setting
        future_date = (datetime.now() + self._parse_timeline(self.session.timeline)).strftime("%Y-%m-%d")
        lines.extend([
            "📋 PROJECT DETAILS",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"Description: {self.session.project_description}",
            f"Timeline: {self.session.timeline}",
            f"Stakeholders: {', '.join(self.session.stakeholders)}",
            "",
            "🎭 FAILURE SCENARIO",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"Imagine it's {future_date}...",
            f"The project '{self.session.project_name}' has FAILED spectacularly.",
            "It is considered a complete disaster.",
            "What went wrong? Let's trace the failure paths:",
            ""
        ])
        
        # Risks by Priority
        if self.session.risks:
            lines.extend([
                "⚠️  IDENTIFIED RISKS (Prioritized)",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                ""
            ])
            
            # Group by priority
            critical = [r for r in self.session.risks if r.priority.startswith("🔴")]
            high = [r for r in self.session.risks if r.priority.startswith("🟠")]
            medium = [r for r in self.session.risks if r.priority.startswith("🟡")]
            low = [r for r in self.session.risks if r.priority.startswith("🟢")]
            
            for label, risks in [("🔴 CRITICAL", critical), ("🟠 HIGH", high), 
                                  ("🟡 MEDIUM", medium), ("🟢 LOW", low)]:
                if risks:
                    lines.append(f"\n{label}")
                    lines.append("─" * 50)
                    for i, risk in enumerate(risks, 1):
                        lines.extend([
                            f"\n  {i}. {risk.description}",
                            f"     Category: {risk.category.value.upper()}",
                            f"     Priority: {risk.priority}",
                            f"     Risk Score: {risk.risk_score}/25",
                            "",
                            "     Prevention Actions:",
                        ])
                        for action in risk.prevention_actions:
                            lines.append(f"       □ {action}")
                        lines.append("")
                        lines.append("     Early Warning Signs:")
                        for warning in risk.early_warnings:
                            lines.append(f"       ⚠️  {warning}")
                        lines.append("")
        
        # Summary Stats
        if self.session.risks:
            total = len(self.session.risks)
            critical_count = len([r for r in self.session.risks if "CRITICAL" in r.priority])
            high_count = len([r for r in self.session.risks if "HIGH" in r.priority])
            
            lines.extend([
                "📊 RISK SUMMARY",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                f"Total Risks Identified: {total}",
                f"Critical Risks: {critical_count}",
                f"High Risks: {high_count}",
                f"Average Risk Score: {sum(r.risk_score for r in self.session.risks) / total:.1f}/25",
                ""
            ])
        
        # Action Items Summary
        lines.extend([
            "✅ NEXT STEPS",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "1. Review all identified risks with the team",
            "2. Assign owners to each prevention action",
            "3. Set up early warning monitoring",
            "4. Schedule weekly risk review meetings",
            "5. Create contingency plans for top 3 risks",
            "",
            "💡 Remember: The goal isn't pessimism—it's preparation.",
            "   By imagining failure, we make success more likely.",
            "",
            "═" * 59,
            f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "Pre-Mortem Skill | Based on Gary Klein's research",
            "═" * 59
        ])
        
        return '\n'.join(lines)
    
    def generate_template(self, format_type: str = "markdown") -> str:
        """Generate a pre-mortem worksheet template."""
        if format_type == "markdown":
            return self._markdown_template()
        elif format_type == "json":
            return self._json_template()
        else:
            return self._text_template()
    
    def _markdown_template(self) -> str:
        """Generate Markdown worksheet template."""
        return """# Pre-Mortem Analysis Worksheet

## Project Information
- **Project Name**: 
- **Description**: 
- **Timeline**: 
- **Stakeholders**: 
- **Date**: 

---

## The Premise 🔮

**Imagine it's [future date]. The project has completely FAILED.**

It is considered a disaster. Stakeholders are disappointed. The team is demoralized.

**What went wrong?**

---

## Failure Path Analysis

### Technical Failures 🔧
_What broke? What didn't scale? What integrations failed?_

1. 
2. 
3. 

### People/Team Failures 👥
_Who left? What skills were missing? What communication broke down?_

1. 
2. 
3. 

### Process/Planning Failures 📋
_What assumptions were wrong? What took longer than expected?_

1. 
2. 
3. 

### External/Market Failures 🌍
_What changed in the market? What did competitors do?_

1. 
2. 
3. 

### User/Customer Failures 👤
_Why didn't users adopt it? What frustrated them?_

1. 
2. 
3. 

---

## Risk Prioritization Matrix

| Risk | Category | Probability | Impact | Priority |
|------|----------|-------------|--------|----------|
|      |          |             |        |          |

---

## Prevention Actions

### Critical Risks (Act Now)
- [ ] 
- [ ] 

### High Risks (Monitor Closely)
- [ ] 
- [ ] 

### Medium Risks (Track Regularly)
- [ ] 
- [ ] 

---

## Early Warning Indicators

| Risk | Warning Sign | How to Monitor |
|------|--------------|----------------|
|      |              |                |

---

## Follow-up Actions

- [ ] Share findings with team
- [ ] Assign action item owners
- [ ] Set up monitoring dashboard
- [ ] Schedule weekly risk reviews
- [ ] Create contingency plans

---

## Notes

"""
    
    def _json_template(self) -> str:
        """Generate JSON template."""
        template = {
            "project_name": "",
            "description": "",
            "timeline": "",
            "stakeholders": [],
            "risks": [
                {
                    "description": "",
                    "category": "technical|people|process|external|user|financial",
                    "probability": "low|medium|high|critical",
                    "impact": "low|medium|high|critical",
                    "prevention_actions": [],
                    "early_warnings": []
                }
            ]
        }
        return json.dumps(template, indent=2)
    
    def _text_template(self) -> str:
        """Generate plain text template."""
        return """PRE-MORTEM WORKSHEET
====================

PROJECT: ___________________
DATE: ___________________

THE SCENARIO:
Imagine it's [future date]. The project has FAILED completely.

FAILURE PATHS:

[ ] Technical: _________________________________

[ ] People: ____________________________________

[ ] Process: ___________________________________

[ ] External: __________________________________

[ ] User: ______________________________________

TOP RISKS:
1. _____________________________________________
   Prevention: __________________________________
   
2. _____________________________________________
   Prevention: __________________________________
   
3. _____________________________________________
   Prevention: __________________________________

ACTION ITEMS:
□ _____________________________________________
□ _____________________________________________
□ _____________________________________________
"""
    
    def _parse_timeline(self, timeline: str) -> timedelta:
        """Parse timeline string to timedelta."""
        timeline = timeline.lower()
        if "month" in timeline:
            try:
                months = int(''.join(filter(str.isdigit, timeline)))
                return timedelta(days=months * 30)
            except:
                return timedelta(days=90)
        elif "week" in timeline:
            try:
                weeks = int(''.join(filter(str.isdigit, timeline)))
                return timedelta(weeks=weeks)
            except:
                return timedelta(weeks=4)
        else:
            return timedelta(days=90)
    
    def interactive_session(self) -> None:
        """Run an interactive pre-mortem session."""
        print("\n" + "="*60)
        print("🔮  INTERACTIVE PRE-MORTEM SESSION")
        print("="*60 + "\n")
        
        # Gather project info
        print("Step 1: Project Information")
        print("-" * 40)
        project_name = input("Project name: ").strip()
        description = input("Brief description: ").strip()
        timeline = input("Timeline (e.g., '3 months'): ").strip()
        stakeholders_str = input("Key stakeholders (comma-separated): ").strip()
        stakeholders = [s.strip() for s in stakeholders_str.split(",") if s.strip()]
        
        self.start_session(project_name, description, timeline, stakeholders)
        
        # Generate initial risks
        print("\n🤖 Generating initial risk library based on project patterns...")
        initial_risks = self.generate_risk_library()
        self.session.risks = initial_risks[:10]  # Top 10
        
        print(f"\n✅ Identified {len(self.session.risks)} potential risks.")
        
        # Allow user to add custom risks
        print("\nStep 2: Add Custom Risks")
        print("-" * 40)
        print("What specific failure modes worry you? (Press Enter to skip)")
        
        while True:
            custom_risk = input("\nRisk description (or Enter to finish): ").strip()
            if not custom_risk:
                break
            
            print("Category options:")
            for i, cat in enumerate(RiskCategory, 1):
                print(f"  {i}. {cat.value}")
            
            try:
                cat_choice = int(input("Select category (1-6): "))
                category = list(RiskCategory)[cat_choice - 1]
            except:
                category = RiskCategory.PROCESS
            
            print("\nProbability options:")
            for i, level in enumerate(RiskLevel, 1):
                print(f"  {i}. {level.value}")
            
            try:
                prob_choice = int(input("Select probability (1-5): "))
                probability = list(RiskLevel)[prob_choice - 1]
            except:
                probability = RiskLevel.MEDIUM
            
            prevention = input("Prevention action: ").strip()
            if prevention:
                prevention_actions = [prevention]
            else:
                prevention_actions = ["Create specific prevention plan"]
            
            self.add_custom_risk(
                description=custom_risk,
                category=category,
                probability=probability,
                impact=RiskLevel.HIGH,
                prevention=prevention_actions,
                warnings=["Monitor closely"]
            )
            print("✓ Risk added!")
        
        # Generate final report
        print("\n" + "="*60)
        print("📊 GENERATING FINAL REPORT...")
        print("="*60 + "\n")
        
        report = self.generate_report()
        print(report)


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Pre-Mortem Skill - Risk Analysis & Failure Prevention',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze --project "Mobile App" --timeline "3 months"
  %(prog)s template --format markdown --output worksheet.md
  %(prog)s session                    # Interactive mode
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run pre-mortem analysis')
    analyze_parser.add_argument('--project', required=True, help='Project name')
    analyze_parser.add_argument('--description', default='', help='Project description')
    analyze_parser.add_argument('--timeline', default='3 months', help='Project timeline')
    analyze_parser.add_argument('--stakeholders', default='', help='Comma-separated stakeholders')
    
    # Template command
    template_parser = subparsers.add_parser('template', help='Generate worksheet template')
    template_parser.add_argument('--format', choices=['markdown', 'json', 'text'], 
                                  default='markdown', help='Template format')
    template_parser.add_argument('--output', help='Output file path')
    
    # Session command
    session_parser = subparsers.add_parser('session', help='Interactive pre-mortem session')
    
    args = parser.parse_args()
    
    skill = PreMortemSkill()
    
    if args.command == 'analyze':
        stakeholders = [s.strip() for s in args.stakeholders.split(",") if s.strip()]
        skill.start_session(
            project_name=args.project,
            description=args.description,
            timeline=args.timeline,
            stakeholders=stakeholders if stakeholders else ["Team"]
        )
        
        # Generate and add risks
        risks = skill.generate_risk_library()
        skill.session.risks = risks[:12]  # Top 12 risks
        
        report = skill.generate_report()
        print(report)
        
    elif args.command == 'template':
        template = skill.generate_template(args.format)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(template)
            print(f"✅ Template saved to: {args.output}")
        else:
            print(template)
            
    elif args.command == 'session':
        skill.interactive_session()
        
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
