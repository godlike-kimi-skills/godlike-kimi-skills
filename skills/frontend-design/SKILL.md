---
name: frontend-design
version: 1.0
description: Professional frontend design skill based on Anthropic design principles. Avoids generic AI aesthetics (Inter/Roboto fonts, purple gradients) and provides human-centered, accessible, performant design solutions.
---

# Frontend Design Skill

Professional frontend design system avoiding generic AI aesthetics.

## Core Principles

### 1. Typography (Avoid Inter/Roboto)
- **System fonts first**: `-apple-system, BlinkMacSystemFont, "Segoe UI"`
- **Serif alternatives**: Georgia, Times New Roman for editorial
- **Monospace**: SF Mono, Consolas for code
- **Web fonts**: Use variable fonts for performance (e.g., "Source Sans 3", "Work Sans")

### 2. Color (Avoid Purple Gradients)
- **Neutral grays**: Slate, Zinc, Neutral palettes
- **Single accent color**: Maximum 2-3 color combinations
- **High contrast**: WCAG AA minimum, AAA preferred
- **No gradients for primary UI**: Use solid colors or subtle shadows

### 3. Motion (Purposeful Animation)
- **Respect reduced-motion**: Always check `prefers-reduced-motion`
- **Subtle transitions**: 150-300ms, ease-out curves
- **No bouncing/overshoot**: Professional, restrained motion
- **Scroll-linked effects**: Sparingly, with performance in mind

### 4. Layout (Grid-Based)
- **8px grid system**: All spacing multiples of 8
- **Max-width constraints**: 1200-1400px for readability
- **Generous whitespace**: Let content breathe
- **Mobile-first**: Responsive breakpoints at 640, 768, 1024px

## Anti-Patterns (AI Aesthetics to Avoid)

❌ Inter or Roboto as primary font
❌ Purple/blue gradients
❌ Floating abstract shapes
❌ Glassmorphism overlays
❌ Excessive border-radius (fully rounded buttons)
❌ Gradient text
❌ Auto-playing animations

## Usage

```bash
# Design a landing page
python D:/kimi/skills/frontend-design/scripts/design.py landing --type saas

# Check design for AI aesthetics
python D:/kimi/skills/frontend-design/scripts/audit.py design.html

# Generate CSS with design system
python D:/kimi/skills/frontend-design/scripts/generate.py --palette slate --font system
```
