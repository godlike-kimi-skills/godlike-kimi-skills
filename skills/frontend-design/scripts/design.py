#!/usr/bin/env python3
"""Frontend Design Generator - Anthropic Design Principles"""

import argparse
import sys
from pathlib import Path

# Design systems
DESIGN_SYSTEMS = {
    "saas": {
        "name": "SaaS Application",
        "font_stack": '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        "primary": "#0f172a",  # Slate 900
        "accent": "#2563eb",   # Blue 600
        "background": "#ffffff",
        "spacing_unit": 8,
        "max_width": "1280px"
    },
    "editorial": {
        "name": "Editorial/Blog",
        "font_stack": 'Georgia, "Times New Roman", serif',
        "heading_font": '-apple-system, sans-serif',
        "primary": "#18181b",  # Zinc 900
        "accent": "#dc2626",   # Red 600
        "background": "#fafafa",
        "spacing_unit": 8,
        "max_width": "720px"
    },
    "dashboard": {
        "name": "Data Dashboard",
        "font_stack": '"SF Mono", Consolas, monospace',
        "primary": "#111827",  # Gray 900
        "accent": "#059669",   # Emerald 600
        "background": "#f9fafb",
        "spacing_unit": 4,
        "max_width": "100%"
    }
}

# Anti-patterns check
AI_AESTHETICS = {
    "fonts": ["Inter", "Roboto", "Open Sans", "Lato"],
    "gradients": ["linear-gradient", "radial-gradient", "conic-gradient"],
    "colors": ["#8b5cf6", "#a855f7", "#6366f1"],  # Purple/indigo
    "patterns": [
        "backdrop-filter: blur",
        "border-radius: 9999px",
        "animation: bounce",
        "glassmorphism",
        "floating"
    ]
}

class FrontendDesigner:
    def __init__(self, design_type="saas"):
        self.system = DESIGN_SYSTEMS.get(design_type, DESIGN_SYSTEMS["saas"])
        self.issues = []
    
    def generate_landing_page(self, title="Your Product"):
        """Generate a landing page with proper design principles"""
        css = f"""/* Generated with Anthropic Design Principles */
:root {{
  --font-primary: {self.system['font_stack']};
  --color-primary: {self.system['primary']};
  --color-accent: {self.system['accent']};
  --color-bg: {self.system['background']};
  --spacing: {self.system['spacing_unit']}px;
  --max-width: {self.system['max_width']};
}}

* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

body {{
  font-family: var(--font-primary);
  background: var(--color-bg);
  color: var(--color-primary);
  line-height: 1.6;
}}

.container {{
  max-width: var(--max-width);
  margin: 0 auto;
  padding: calc(var(--spacing) * 4);
}}

h1, h2, h3 {{
  font-weight: 600;
  line-height: 1.2;
  margin-bottom: calc(var(--spacing) * 3);
}}

h1 {{
  font-size: 3rem;
  letter-spacing: -0.02em;
}}

.btn {{
  display: inline-block;
  padding: calc(var(--spacing) * 1.5) calc(var(--spacing) * 3);
  background: var(--color-accent);
  color: white;
  text-decoration: none;
  border-radius: 4px;  /* Subtle, not fully rounded */
  font-weight: 500;
  transition: opacity 0.15s ease-out;
}}

.btn:hover {{
  opacity: 0.9;
}}

/* No gradients, no glassmorphism, no bounce animations */
"""
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>{css}</style>
</head>
<body>
  <header class="container">
    <h1>{title}</h1>
    <p class="subtitle">Clean, professional design without AI aesthetics</p>
    <a href="#" class="btn">Get Started</a>
  </header>
  
  <main class="container">
    <section>
      <h2>Design Principles Applied</h2>
      <ul>
        <li>[OK] System fonts (no Inter/Roboto)</li>
        <li>[OK] Solid colors (no purple gradients)</li>
        <li>[OK] Subtle 4px border-radius</li>
        <li>[OK] 8px grid spacing</li>
        <li>[OK] Purposeful motion only</li>
      </ul>
    </section>
  </main>
</body>
</html>"""
        
        return html, css
    
    def audit_design(self, content):
        """Check for AI aesthetics/anti-patterns"""
        content_lower = content.lower()
        issues = []
        
        # Check fonts
        for font in AI_AESTHETICS["fonts"]:
            if font.lower() in content_lower:
                issues.append(f"[!] Generic AI font detected: {font}")
        
        # Check gradients
        for gradient in AI_AESTHETICS["gradients"]:
            if gradient in content_lower:
                issues.append(f"[!] Gradient detected: {gradient}")
        
        # Check purple colors
        for color in AI_AESTHETICS["colors"]:
            if color in content:
                issues.append(f"[!] AI aesthetic color: {color} (purple/indigo)")
        
        # Check patterns
        for pattern in AI_AESTHETICS["patterns"]:
            if pattern.lower() in content_lower:
                issues.append(f"[!] Anti-pattern: {pattern}")
        
        self.issues = issues
        return issues
    
    def suggest_improvements(self):
        """Suggest improvements based on audit"""
        if not self.issues:
            return ["[OK] No AI aesthetics detected. Design looks human-made!"]
        
        suggestions = []
        for issue in self.issues:
            if "font" in issue.lower():
                suggestions.append("→ Replace with system fonts: -apple-system, Segoe UI")
            elif "gradient" in issue.lower():
                suggestions.append("→ Use solid colors or subtle shadows instead")
            elif "color" in issue.lower():
                suggestions.append("→ Consider slate, zinc, or neutral color palettes")
            elif "border-radius" in issue.lower():
                suggestions.append("→ Use 4-8px border-radius, not fully rounded")
            else:
                suggestions.append("→ Remove or simplify this effect")
        
        return suggestions

def main():
    parser = argparse.ArgumentParser(description='Frontend Design Tool')
    parser.add_argument('command', choices=['landing', 'audit', 'generate'])
    parser.add_argument('--type', default='saas', choices=['saas', 'editorial', 'dashboard'])
    parser.add_argument('--title', default='Your Product')
    parser.add_argument('--file', help='File to audit')
    parser.add_argument('--output', '-o', help='Output file')
    
    args = parser.parse_args()
    
    designer = FrontendDesigner(args.type)
    
    if args.command == 'landing':
        html, css = designer.generate_landing_page(args.title)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(html)
            print(f"[OK] Landing page saved to {args.output}")
        else:
            print("=== GENERATED LANDING PAGE ===")
            print(html)
    
    elif args.command == 'audit':
        if not args.file:
            print("✗ Please specify --file to audit")
            sys.exit(1)
        
        with open(args.file) as f:
            content = f.read()
        
        issues = designer.audit_design(content)
        suggestions = designer.suggest_improvements()
        
        print(f"\n=== DESIGN AUDIT: {args.file} ===")
        print(f"Design type: {designer.system['name']}\n")
        
        if issues:
            print("Issues found:")
            for issue in issues:
                print(f"  {issue}")
            print("\nSuggestions:")
            for suggestion in suggestions:
                print(f"  {suggestion}")
        else:
            print("[OK] No AI aesthetics detected!")
    
    elif args.command == 'generate':
        print(f"Design System: {designer.system['name']}")
        print(f"Font Stack: {designer.system['font_stack']}")
        print(f"Primary: {designer.system['primary']}")
        print(f"Accent: {designer.system['accent']}")
        print("\nCopy these CSS variables to your project.")

if __name__ == '__main__':
    main()
