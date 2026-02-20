#!/usr/bin/env python3
"""
Regex Skill - Regular Expression Tool
Supports: matching, validation, replacement, testing, generation, explanation
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union, Match, Pattern
from dataclasses import dataclass
from enum import Enum


class RegexFlag(Enum):
    """Regex compilation flags"""
    IGNORECASE = re.IGNORECASE
    MULTILINE = re.MULTILINE
    DOTALL = re.DOTALL
    VERBOSE = re.VERBOSE
    UNICODE = re.UNICODE
    ASCII = re.ASCII


@dataclass
class MatchResult:
    """Result of a regex match"""
    matched: bool
    groups: List[str]
    start: int
    end: int
    text: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'matched': self.matched,
            'groups': self.groups,
            'start': self.start,
            'end': self.end,
            'text': self.text
        }


@dataclass
class TestCase:
    """Test case for regex testing"""
    input: str
    expected: bool
    description: str = ""


class RegexSkill:
    """Main skill class for regex operations"""
    
    # Built-in regex patterns for common use cases
    BUILT_IN_PATTERNS = {
        'email': {
            'pattern': r'^[\w.-]+@[\w.-]+\.\w{2,}$',
            'description': 'Email address validation'
        },
        'url': {
            'pattern': r'^https?://[^\s<>"{}|\\^`\[\]]+$',
            'description': 'HTTP/HTTPS URL'
        },
        'ip': {
            'pattern': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
            'description': 'IPv4 address'
        },
        'phone': {
            'pattern': r'^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}$',
            'description': 'Phone number'
        },
        'date_iso': {
            'pattern': r'^\d{4}-\d{2}-\d{2}$',
            'description': 'ISO date (YYYY-MM-DD)'
        },
        'date_us': {
            'pattern': r'^\d{1,2}/\d{1,2}/\d{4}$',
            'description': 'US date (MM/DD/YYYY)'
        },
        'uuid': {
            'pattern': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            'description': 'UUID v4'
        },
        'credit_card': {
            'pattern': r'^(?:\d{4}[-\s]?){3}\d{4}$',
            'description': 'Credit card number'
        },
        'hex_color': {
            'pattern': r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
            'description': 'Hex color code'
        },
        'username': {
            'pattern': r'^[a-zA-Z0-9_-]{3,32}$',
            'description': 'Username (3-32 chars, alphanumeric + _-)'
        },
        'password_strong': {
            'pattern': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
            'description': 'Strong password (8+ chars, upper, lower, digit, special)'
        },
        'password_medium': {
            'pattern': r'^(?=.*[a-zA-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{6,}$',
            'description': 'Medium password (6+ chars, letters + digits)'
        },
        'ipv6': {
            'pattern': r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$',
            'description': 'IPv6 address'
        },
        'mac_address': {
            'pattern': r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
            'description': 'MAC address'
        },
        'slug': {
            'pattern': r'^[a-z0-9]+(?:-[a-z0-9]+)*$',
            'description': 'URL slug'
        },
        'zip_us': {
            'pattern': r'^\d{5}(-\d{4})?$',
            'description': 'US ZIP code'
        }
    }
    
    def __init__(self):
        self.name = "regex-skill"
        self.version = "1.0.0"
        self._compiled_cache: Dict[str, Pattern] = {}
    
    def _compile(self, pattern: str, flags: int = 0) -> Pattern:
        """Compile regex pattern with caching"""
        cache_key = f"{pattern}:{flags}"
        if cache_key not in self._compiled_cache:
            self._compiled_cache[cache_key] = re.compile(pattern, flags)
        return self._compiled_cache[cache_key]
    
    def _parse_flags(self, flag_names: List[str]) -> int:
        """Parse flag names to regex flags"""
        flags = 0
        for name in flag_names:
            name = name.upper()
            if name == 'IGNORECASE' or name == 'I':
                flags |= re.IGNORECASE
            elif name == 'MULTILINE' or name == 'M':
                flags |= re.MULTILINE
            elif name == 'DOTALL' or name == 'S':
                flags |= re.DOTALL
            elif name == 'VERBOSE' or name == 'X':
                flags |= re.VERBOSE
            elif name == 'ASCII' or name == 'A':
                flags |= re.ASCII
        return flags
    
    def match(self, pattern: str, text: str, flags: List[str] = None) -> List[MatchResult]:
        """
        Find all matches of pattern in text
        
        Args:
            pattern: Regular expression pattern
            text: Text to search in
            flags: List of flag names (ignorecase, multiline, dotall, verbose)
            
        Returns:
            List of MatchResult objects
        """
        try:
            flag_val = self._parse_flags(flags or [])
            compiled = self._compile(pattern, flag_val)
            
            results = []
            for match in compiled.finditer(text):
                result = MatchResult(
                    matched=True,
                    groups=list(match.groups()),
                    start=match.start(),
                    end=match.end(),
                    text=match.group(0)
                )
                results.append(result)
            
            return results
        except re.error as e:
            return [MatchResult(matched=False, groups=[], start=-1, end=-1, text=f"Regex error: {e}")]
    
    def search(self, pattern: str, text: str, flags: List[str] = None) -> Optional[MatchResult]:
        """
        Search for first match of pattern in text
        
        Args:
            pattern: Regular expression pattern
            text: Text to search in
            flags: List of flag names
            
        Returns:
            MatchResult or None if not found
        """
        try:
            flag_val = self._parse_flags(flags or [])
            compiled = self._compile(pattern, flag_val)
            
            match = compiled.search(text)
            if match:
                return MatchResult(
                    matched=True,
                    groups=list(match.groups()),
                    start=match.start(),
                    end=match.end(),
                    text=match.group(0)
                )
            return None
        except re.error as e:
            return MatchResult(matched=False, groups=[], start=-1, end=-1, text=f"Regex error: {e}")
    
    def validate(self, pattern: str, text: str, flags: List[str] = None) -> bool:
        """
        Validate if text fully matches the pattern
        
        Args:
            pattern: Regular expression pattern
            text: Text to validate
            flags: List of flag names
            
        Returns:
            True if entire text matches pattern
        """
        try:
            flag_val = self._parse_flags(flags or [])
            compiled = self._compile(pattern, flag_val)
            return bool(compiled.fullmatch(text))
        except re.error:
            return False
    
    def replace(self, pattern: str, replacement: str, text: str, 
                count: int = 0, flags: List[str] = None) -> Tuple[str, int]:
        """
        Replace matches in text
        
        Args:
            pattern: Regular expression pattern
            replacement: Replacement string (can use backreferences)
            text: Text to process
            count: Maximum replacements (0 = all)
            flags: List of flag names
            
        Returns:
            Tuple of (new_text, num_replacements)
        """
        try:
            flag_val = self._parse_flags(flags or [])
            compiled = self._compile(pattern, flag_val)
            new_text, num = compiled.subn(replacement, text, count=count)
            return new_text, num
        except re.error as e:
            return text, 0
    
    def split(self, pattern: str, text: str, maxsplit: int = 0, flags: List[str] = None) -> List[str]:
        """
        Split text by pattern
        
        Args:
            pattern: Regular expression pattern
            text: Text to split
            maxsplit: Maximum splits (0 = all)
            flags: List of flag names
            
        Returns:
            List of split parts
        """
        try:
            flag_val = self._parse_flags(flags or [])
            compiled = self._compile(pattern, flag_val)
            return compiled.split(text, maxsplit=maxsplit)
        except re.error as e:
            return [text]
    
    def test(self, pattern: str, test_cases: List[Union[str, TestCase]], 
             flags: List[str] = None) -> Dict[str, Any]:
        """
        Test regex pattern against multiple inputs
        
        Args:
            pattern: Regular expression pattern
            test_cases: List of test strings or TestCase objects
            flags: List of flag names
            
        Returns:
            Dictionary with test results
        """
        results = []
        passed = 0
        failed = 0
        
        for case in test_cases:
            if isinstance(case, str):
                test_input = case
                expected = True
                description = ""
            else:
                test_input = case.input
                expected = case.expected
                description = case.description
            
            actual = self.validate(pattern, test_input, flags)
            status = "PASS" if actual == expected else "FAIL"
            
            if status == "PASS":
                passed += 1
            else:
                failed += 1
            
            results.append({
                'input': test_input,
                'expected': expected,
                'actual': actual,
                'status': status,
                'description': description
            })
        
        return {
            'total': len(test_cases),
            'passed': passed,
            'failed': failed,
            'success_rate': passed / len(test_cases) if test_cases else 0,
            'results': results
        }
    
    def generate(self, pattern_name: str) -> Dict[str, str]:
        """
        Get a built-in regex pattern
        
        Args:
            pattern_name: Name of built-in pattern
            
        Returns:
            Dictionary with pattern and description
        """
        if pattern_name in self.BUILT_IN_PATTERNS:
            return self.BUILT_IN_PATTERNS[pattern_name]
        return None
    
    def list_patterns(self) -> Dict[str, Dict[str, str]]:
        """
        List all available built-in patterns
        
        Returns:
            Dictionary of pattern definitions
        """
        return self.BUILT_IN_PATTERNS.copy()
    
    def explain(self, pattern: str) -> List[Dict[str, str]]:
        """
        Explain regex pattern components
        
        Args:
            pattern: Regular expression to explain
            
        Returns:
            List of pattern component explanations
        """
        explanations = []
        
        # Simple pattern breakdown
        i = 0
        while i < len(pattern):
            char = pattern[i]
            
            # Anchors
            if char == '^':
                explanations.append({'char': '^', 'meaning': 'Start of string', 'type': 'anchor'})
            elif char == '$':
                explanations.append({'char': '$', 'meaning': 'End of string', 'type': 'anchor'})
            
            # Quantifiers
            elif char == '*':
                explanations.append({'char': '*', 'meaning': 'Zero or more of preceding', 'type': 'quantifier'})
            elif char == '+':
                explanations.append({'char': '+', 'meaning': 'One or more of preceding', 'type': 'quantifier'})
            elif char == '?':
                explanations.append({'char': '?', 'meaning': 'Zero or one of preceding (optional)', 'type': 'quantifier'})
            elif char == '{':
                # Look for closing brace
                end = pattern.find('}', i)
                if end != -1:
                    content = pattern[i:end+1]
                    explanations.append({'char': content, 'meaning': f'Quantifier: {content}', 'type': 'quantifier'})
                    i = end
            
            # Character classes
            elif char == '.':
                explanations.append({'char': '.', 'meaning': 'Any character (except newline)', 'type': 'character_class'})
            elif char == '[':
                end = pattern.find(']', i)
                if end != -1:
                    content = pattern[i:end+1]
                    explanations.append({'char': content, 'meaning': f'Character class: {content}', 'type': 'character_class'})
                    i = end
            elif char == '\\':
                if i + 1 < len(pattern):
                    next_char = pattern[i + 1]
                    if next_char == 'd':
                        explanations.append({'char': '\\d', 'meaning': 'Digit [0-9]', 'type': 'character_class'})
                    elif next_char == 'w':
                        explanations.append({'char': '\\w', 'meaning': 'Word character [a-zA-Z0-9_]', 'type': 'character_class'})
                    elif next_char == 's':
                        explanations.append({'char': '\\s', 'meaning': 'Whitespace character', 'type': 'character_class'})
                    elif next_char == 'D':
                        explanations.append({'char': '\\D', 'meaning': 'Non-digit', 'type': 'character_class'})
                    elif next_char == 'W':
                        explanations.append({'char': '\\W', 'meaning': 'Non-word character', 'type': 'character_class'})
                    elif next_char == 'S':
                        explanations.append({'char': '\\S', 'meaning': 'Non-whitespace character', 'type': 'character_class'})
                    elif next_char == 'n':
                        explanations.append({'char': '\\n', 'meaning': 'Newline character', 'type': 'escape'})
                    elif next_char == 't':
                        explanations.append({'char': '\\t', 'meaning': 'Tab character', 'type': 'escape'})
                    elif next_char.isdigit():
                        explanations.append({'char': f'\\{next_char}', 'meaning': f'Backreference to group {next_char}', 'type': 'backreference'})
                    else:
                        explanations.append({'char': f'\\{next_char}', 'meaning': f'Escaped character: {next_char}', 'type': 'escape'})
                    i += 1
            
            # Groups
            elif char == '(':
                if i + 1 < len(pattern) and pattern[i + 1] == '?':
                    if i + 2 < len(pattern):
                        if pattern[i + 2] == ':':
                            explanations.append({'char': '(?:', 'meaning': 'Non-capturing group', 'type': 'group'})
                        elif pattern[i + 2] == '=':
                            explanations.append({'char': '(?=', 'meaning': 'Positive lookahead', 'type': 'assertion'})
                        elif pattern[i + 2] == '!':
                            explanations.append({'char': '(?!', 'meaning': 'Negative lookahead', 'type': 'assertion'})
                        i += 2
                else:
                    explanations.append({'char': '(', 'meaning': 'Start of capturing group', 'type': 'group'})
            elif char == ')':
                explanations.append({'char': ')', 'meaning': 'End of group', 'type': 'group'})
            
            # Alternation
            elif char == '|':
                explanations.append({'char': '|', 'meaning': 'Alternation (OR)', 'type': 'operator'})
            
            # Literal characters
            elif char.isalnum():
                explanations.append({'char': char, 'meaning': f'Literal character: {char}', 'type': 'literal'})
            else:
                explanations.append({'char': char, 'meaning': f'Literal: {char}', 'type': 'literal'})
            
            i += 1
        
        return explanations
    
    def extract_groups(self, pattern: str, text: str, flags: List[str] = None) -> List[Dict[str, Any]]:
        """
        Extract named and numbered groups from matches
        
        Args:
            pattern: Regular expression pattern
            text: Text to search in
            flags: List of flag names
            
        Returns:
            List of dictionaries with group information
        """
        try:
            flag_val = self._parse_flags(flags or [])
            compiled = self._compile(pattern, flag_val)
            
            results = []
            for match in compiled.finditer(text):
                match_data = {
                    'full_match': match.group(0),
                    'groups': [],
                    'named_groups': {}
                }
                
                # Get numbered groups
                for i in range(1, compiled.groups + 1):
                    match_data['groups'].append(match.group(i))
                
                # Get named groups
                if compiled.groupindex:
                    for name, index in compiled.groupindex.items():
                        match_data['named_groups'][name] = match.group(name)
                
                results.append(match_data)
            
            return results
        except re.error as e:
            return [{'error': str(e)}]


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='Regular Expression Tool')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Match command
    match_parser = subparsers.add_parser('match', help='Find all matches')
    match_parser.add_argument('pattern', help='Regex pattern')
    match_parser.add_argument('text', help='Text to search')
    match_parser.add_argument('--flags', '-f', nargs='+', help='Regex flags')
    match_parser.add_argument('--file', help='Read text from file')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for first match')
    search_parser.add_argument('pattern', help='Regex pattern')
    search_parser.add_argument('text', help='Text to search')
    search_parser.add_argument('--flags', '-f', nargs='+', help='Regex flags')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate string')
    validate_parser.add_argument('pattern', help='Regex pattern')
    validate_parser.add_argument('text', help='Text to validate')
    validate_parser.add_argument('--flags', '-f', nargs='+', help='Regex flags')
    
    # Replace command
    replace_parser = subparsers.add_parser('replace', help='Replace matches')
    replace_parser.add_argument('pattern', help='Regex pattern')
    replace_parser.add_argument('replacement', help='Replacement string')
    replace_parser.add_argument('text', help='Text to process')
    replace_parser.add_argument('--count', '-n', type=int, default=0, help='Max replacements')
    replace_parser.add_argument('--flags', '-f', nargs='+', help='Regex flags')
    
    # Split command
    split_parser = subparsers.add_parser('split', help='Split by pattern')
    split_parser.add_argument('pattern', help='Regex pattern')
    split_parser.add_argument('text', help='Text to split')
    split_parser.add_argument('--max', type=int, default=0, help='Max splits')
    split_parser.add_argument('--flags', '-f', nargs='+', help='Regex flags')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test regex')
    test_parser.add_argument('pattern', help='Regex pattern')
    test_parser.add_argument('--file', '-f', help='File with test cases')
    test_parser.add_argument('--cases', '-c', nargs='+', help='Test cases')
    test_parser.add_argument('--flags', nargs='+', help='Regex flags')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate pattern')
    gen_parser.add_argument('name', help='Pattern name')
    gen_parser.add_argument('--list', '-l', action='store_true', help='List patterns')
    
    # Explain command
    explain_parser = subparsers.add_parser('explain', help='Explain pattern')
    explain_parser.add_argument('pattern', help='Regex pattern')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract groups')
    extract_parser.add_argument('pattern', help='Regex pattern')
    extract_parser.add_argument('text', help='Text to process')
    extract_parser.add_argument('--flags', '-f', nargs='+', help='Regex flags')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    skill = RegexSkill()
    
    if args.command == 'match':
        text = args.text
        if args.file:
            text = Path(args.file).read_text()
        
        results = skill.match(args.pattern, text, args.flags)
        if results:
            for i, result in enumerate(results, 1):
                print(f"Match {i}:")
                print(f"  Text: {result.text}")
                print(f"  Position: {result.start}-{result.end}")
                if result.groups:
                    print(f"  Groups: {result.groups}")
        else:
            print("No matches found")
    
    elif args.command == 'search':
        result = skill.search(args.pattern, args.text, args.flags)
        if result:
            print(f"Match: {result.text}")
            print(f"Position: {result.start}-{result.end}")
            if result.groups:
                print(f"Groups: {result.groups}")
        else:
            print("No match found")
    
    elif args.command == 'validate':
        is_valid = skill.validate(args.pattern, args.text, args.flags)
        print("Valid" if is_valid else "Invalid")
        sys.exit(0 if is_valid else 1)
    
    elif args.command == 'replace':
        new_text, count = skill.replace(args.pattern, args.replacement, args.text, args.count, args.flags)
        print(new_text)
        if count > 0:
            print(f"\n({count} replacements made)", file=sys.stderr)
    
    elif args.command == 'split':
        parts = skill.split(args.pattern, args.text, args.max, args.flags)
        for i, part in enumerate(parts):
            print(f"[{i}]: {part}")
    
    elif args.command == 'test':
        if args.list:
            patterns = skill.list_patterns()
            for name, info in patterns.items():
                print(f"{name}: {info['description']}")
                print(f"  Pattern: {info['pattern']}\n")
            return
        
        cases = args.cases or []
        if args.file:
            lines = Path(args.file).read_text().strip().split('\n')
            cases.extend(lines)
        
        if not cases:
            print("No test cases provided")
            return
        
        results = skill.test(args.pattern, cases, args.flags)
        print(f"Results: {results['passed']}/{results['total']} passed")
        for r in results['results']:
            status_icon = "✓" if r['status'] == 'PASS' else "✗"
            print(f"{status_icon} {r['input']}: expected={r['expected']}, actual={r['actual']}")
    
    elif args.command == 'generate':
        if args.list or args.name == 'list':
            patterns = skill.list_patterns()
            for name, info in patterns.items():
                print(f"{name}: {info['description']}")
                print(f"  Pattern: {info['pattern']}\n")
        else:
            pattern_info = skill.generate(args.name)
            if pattern_info:
                print(f"Pattern: {pattern_info['pattern']}")
                print(f"Description: {pattern_info['description']}")
            else:
                print(f"Pattern '{args.name}' not found")
                print("Use --list to see available patterns")
    
    elif args.command == 'explain':
        explanations = skill.explain(args.pattern)
        print(f"Pattern: {args.pattern}\n")
        print(f"{'Component':<20} {'Type':<15} {'Meaning'}")
        print("-" * 60)
        for exp in explanations:
            char = exp['char'][:18]
            print(f"{char:<20} {exp['type']:<15} {exp['meaning']}")
    
    elif args.command == 'extract':
        results = skill.extract_groups(args.pattern, args.text, args.flags)
        for i, result in enumerate(results, 1):
            print(f"Match {i}:")
            print(f"  Full: {result['full_match']}")
            if result['groups']:
                print(f"  Groups: {result['groups']}")
            if result['named_groups']:
                print(f"  Named Groups: {result['named_groups']}")


if __name__ == '__main__':
    main()
