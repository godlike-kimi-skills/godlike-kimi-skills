#!/usr/bin/env python3
"""Image Generation Assistant - Prompt Engineering & Style Guide"""

import argparse
from pathlib import Path

class ImagenAssistant:
    def __init__(self):
        self.styles = {
            "photorealistic": {
                "keywords": ["8k", "highly detailed", "photorealistic", "cinematic lighting"],
                "negative": ["cartoon", "illustration", "painting", "sketch"]
            },
            "digital_art": {
                "keywords": ["digital art", "concept art", "trending on artstation", "vibrant colors"],
                "negative": ["blurry", "low quality", "watermark"]
            },
            "minimalist": {
                "keywords": ["minimalist", "clean lines", "simple", "elegant", "white background"],
                "negative": ["cluttered", "busy", "complex", "ornate"]
            },
            "professional": {
                "keywords": ["professional", "corporate", "clean", "modern", "sleek"],
                "negative": ["casual", "messy", "unprofessional", "dated"]
            }
        }
        
        self.aspect_ratios = {
            "square": (1, 1),
            "portrait": (2, 3),
            "landscape": (3, 2),
            "widescreen": (16, 9),
            "mobile": (9, 16)
        }
    
    def optimize_prompt(self, base_prompt, style=None, aspect_ratio="square"):
        """Optimize image generation prompt"""
        print(f"\n[ART] Prompt Optimization")
        print("=" * 60)
        print(f"Original: {base_prompt}")
        
        # Detect and enhance
        enhanced = base_prompt
        
        # Add quality boosters
        quality_terms = ["high quality", "detailed", "sharp focus"]
        for term in quality_terms:
            if term not in enhanced.lower():
                enhanced += f", {term}"
        
        # Add style modifiers
        if style and style in self.styles:
            style_data = self.styles[style]
            enhanced += ", " + ", ".join(style_data["keywords"])
            negative = ", ".join(style_data["negative"])
        else:
            negative = "low quality, blurry, distorted, watermark, signature"
        
        print(f"\n[SPARKLE] Optimized: {enhanced}")
        print(f"\n[BLOCK] Negative prompt: {negative}")
        
        # Aspect ratio
        ratio = self.aspect_ratios.get(aspect_ratio, (1, 1))
        print(f"\n[LAYOUT] Aspect ratio: {aspect_ratio} ({ratio[0]}:{ratio[1]})")
        
        # Recommendations
        print("\n[TIP] Recommendations:")
        print("  - Use specific descriptors (colors, lighting, materials)")
        print("  - Mention camera type for photorealism (DSLR, 50mm lens)")
        print("  - Include artistic references when relevant")
        print("  - Keep total prompt under 75 tokens for best results")
        
        return {
            "original": base_prompt,
            "optimized": enhanced,
            "negative": negative,
            "aspect_ratio": aspect_ratio
        }
    
    def analyze_concept(self, concept):
        """Analyze image concept and provide guidance"""
        print(f"\n[SEARCH] Concept Analysis: {concept}")
        print("=" * 60)
        
        # Auto-detect style
        detected_style = self._detect_style(concept)
        print(f"Detected style: {detected_style}")
        
        # Composition suggestions
        print("\n[LAYOUT] Composition suggestions:")
        compositions = [
            "Rule of thirds - Place subject at intersection points",
            "Leading lines - Use natural lines to guide viewer",
            "Framing - Use elements to frame the main subject",
            "Symmetry - Balance elements for formal feel",
            "Depth - Include foreground, midground, background"
        ]
        for comp in compositions:
            print(f"  - {comp}")
        
        # Lighting recommendations
        print("\n[TIP] Lighting recommendations:")
        lighting = [
            "Golden hour - Warm, soft light (sunrise/sunset)",
            "Blue hour - Cool, dramatic light (twilight)",
            "Overcast - Soft, diffused light (no harsh shadows)",
            "Studio - Controlled, professional lighting",
            "Dramatic - High contrast, strong shadows"
        ]
        for light in lighting:
            print(f"  - {light}")
        
        # Color palette suggestions
        print("\n[ART] Color palette suggestions:")
        palettes = {
            "Complementary": "Opposite colors for high contrast",
            "Analogous": "Adjacent colors for harmony",
            "Monochromatic": "Single color with variations",
            "Triadic": "Three evenly spaced colors"
        }
        for name, desc in palettes.items():
            print(f"  - {name}: {desc}")
    
    def _detect_style(self, concept):
        """Auto-detect style from concept"""
        concept_lower = concept.lower()
        
        if any(word in concept_lower for word in ["photo", "realistic", "dslr", "camera"]):
            return "Photorealistic"
        elif any(word in concept_lower for word in ["art", "painting", "illustration"]):
            return "Digital Art"
        elif any(word in concept_lower for word in ["minimal", "simple", "clean"]):
            return "Minimalist"
        else:
            return "Digital Art (default)"
    
    def get_style_guide(self, mood="creative"):
        """Get comprehensive style guide"""
        print(f"\n[BOOK] Style Guide: {mood.title()}")
        print("=" * 60)
        
        guides = {
            "creative": {
                "mood": "Imaginative, artistic, unique",
                "keywords": ["creative", "artistic", "unique", "innovative", "whimsical"],
                "techniques": ["Unexpected color combinations", "Surreal elements", "Abstract forms"]
            },
            "professional": {
                "mood": "Corporate, clean, trustworthy",
                "keywords": ["professional", "corporate", "clean", "modern", "sleek"],
                "techniques": ["Neutral color palette", "Minimal composition", "Clear typography"]
            },
            "dramatic": {
                "mood": "Intense, emotional, cinematic",
                "keywords": ["dramatic", "cinematic", "intense", "atmospheric", "moody"],
                "techniques": ["High contrast lighting", "Deep shadows", "Rich saturation"]
            },
            "calm": {
                "mood": "Peaceful, serene, relaxing",
                "keywords": ["serene", "peaceful", "calm", "tranquil", "soft"],
                "techniques": ["Soft lighting", "Pastel colors", "Minimal contrast"]
            }
        }
        
        guide = guides.get(mood, guides["creative"])
        
        print(f"Mood: {guide['mood']}")
        print(f"\nKeywords: {', '.join(guide['keywords'])}")
        print("\nTechniques:")
        for tech in guide['techniques']:
            print(f"  - {tech}")
        
        print("\n[TARGET] Prompt template:")
        print(f"[Subject], {', '.join(guide['keywords'][:3])}, "
              f"{guide['techniques'][0].lower()}, highly detailed, 8k")

def main():
    parser = argparse.ArgumentParser(description='Image Generation Assistant')
    parser.add_argument('command', choices=['prompt', 'analyze', 'style'])
    parser.add_argument('text', nargs='?', help='Input text/prompt')
    parser.add_argument('--style', '-s', default='digital_art',
                       choices=['photorealistic', 'digital_art', 'minimalist', 'professional'])
    parser.add_argument('--aspect', '-a', default='square',
                       choices=['square', 'portrait', 'landscape', 'widescreen', 'mobile'])
    parser.add_argument('--mood', '-m', default='creative',
                       choices=['creative', 'professional', 'dramatic', 'calm'])
    
    args = parser.parse_args()
    
    imagen = ImagenAssistant()
    
    if args.command == 'prompt':
        if not args.text:
            print("[X] Please provide a prompt")
            return
        imagen.optimize_prompt(args.text, args.style, args.aspect)
    
    elif args.command == 'analyze':
        if not args.text:
            print("[X] Please provide a concept")
            return
        imagen.analyze_concept(args.text)
    
    elif args.command == 'style':
        imagen.get_style_guide(args.mood)

if __name__ == '__main__':
    main()
