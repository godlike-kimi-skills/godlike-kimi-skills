#!/usr/bin/env python3
"""
Tests for Regex Skill
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from main import RegexSkill, MatchResult, TestCase


class TestRegexSkill:
    """Test cases for RegexSkill"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.skill = RegexSkill()
    
    def test_match_simple(self):
        """Test basic matching"""
        results = self.skill.match(r'\d+', 'Price: $100 and $200')
        assert len(results) == 2
        assert results[0].text == '100'
        assert results[1].text == '200'
    
    def test_match_with_groups(self):
        """Test matching with capture groups"""
        results = self.skill.match(r'(\w+)@(\w+)\.\w+', 'Contact: user@example.com or admin@test.org')
        assert len(results) == 2
        assert results[0].groups == ['user', 'example']
        assert results[1].groups == ['admin', 'test']
    
    def test_match_no_results(self):
        """Test matching with no results"""
        results = self.skill.match(r'xyz', 'abc def')
        assert len(results) == 0
    
    def test_match_flags_ignorecase(self):
        """Test case-insensitive matching"""
        results = self.skill.match(r'hello', 'Hello HELLO hello', ['ignorecase'])
        assert len(results) == 3
    
    def test_search_found(self):
        """Test search finding match"""
        result = self.skill.search(r'\d+', 'abc123def')
        assert result is not None
        assert result.text == '123'
        assert result.start == 3
        assert result.end == 6
    
    def test_search_not_found(self):
        """Test search not finding match"""
        result = self.skill.search(r'xyz', 'abc def')
        assert result is None
    
    def test_validate_match(self):
        """Test validation with match"""
        is_valid = self.skill.validate(r'\d{3}-\d{4}', '123-4567')
        assert is_valid is True
    
    def test_validate_no_match(self):
        """Test validation without full match"""
        is_valid = self.skill.validate(r'\d+', 'abc123def')
        assert is_valid is False
    
    def test_validate_partial(self):
        """Test validation - partial match is not enough"""
        is_valid = self.skill.validate(r'\d+', '123abc')
        assert is_valid is False
    
    def test_replace_all(self):
        """Test replace all occurrences"""
        new_text, count = self.skill.replace(r'\d+', 'X', 'a1b2c3')
        assert new_text == 'aXbXcX'
        assert count == 3
    
    def test_replace_limited(self):
        """Test replace with count limit"""
        new_text, count = self.skill.replace(r'\d+', 'X', 'a1b2c3', count=2)
        assert new_text == 'aXbXc3'
        assert count == 2
    
    def test_replace_backreference(self):
        """Test replace with backreference"""
        new_text, count = self.skill.replace(r'(\w+)@(\w+)', r'\2@\1', 'user@example.com')
        assert new_text == 'example@user.com'
    
    def test_split_simple(self):
        """Test simple split"""
        parts = self.skill.split(r'\s+', 'a b  c   d')
        assert parts == ['a', 'b', 'c', 'd']
    
    def test_split_maxsplit(self):
        """Test split with maxsplit"""
        parts = self.skill.split(r',', 'a,b,c,d', maxsplit=2)
        assert parts == ['a', 'b', 'c,d']
    
    def test_split_with_groups(self):
        """Test split keeping delimiters"""
        parts = self.skill.split(r'(,)', 'a,b,c')
        assert parts == ['a', ',', 'b', ',', 'c']
    
    def test_test_all_pass(self):
        """Test regex test - all pass"""
        cases = ['123-4567', '999-9999', '000-0000']
        results = self.skill.test(r'^\d{3}-\d{4}$', cases)
        assert results['passed'] == 3
        assert results['failed'] == 0
        assert results['success_rate'] == 1.0
    
    def test_test_all_fail(self):
        """Test regex test - all fail"""
        cases = ['12-3456', '123-456', 'abc-defg']
        results = self.skill.test(r'^\d{3}-\d{4}$', cases)
        assert results['passed'] == 0
        assert results['failed'] == 3
        assert results['success_rate'] == 0.0
    
    def test_test_mixed(self):
        """Test regex test - mixed results"""
        cases = [
            TestCase('user@example.com', True, 'Valid email'),
            TestCase('invalid', False, 'Invalid email'),
            TestCase('test@test.org', True, 'Another valid'),
        ]
        results = self.skill.test(r'^[\w.-]+@[\w.-]+\.\w+$', cases)
        assert results['passed'] == 2
        assert results['failed'] == 1
    
    def test_generate_email(self):
        """Test generating email pattern"""
        pattern_info = self.skill.generate('email')
        assert pattern_info is not None
        assert 'pattern' in pattern_info
        assert '@' in pattern_info['pattern']
    
    def test_generate_not_found(self):
        """Test generating non-existent pattern"""
        pattern_info = self.skill.generate('nonexistent')
        assert pattern_info is None
    
    def test_list_patterns(self):
        """Test listing all patterns"""
        patterns = self.skill.list_patterns()
        assert 'email' in patterns
        assert 'url' in patterns
        assert 'ip' in patterns
    
    def test_explain_simple(self):
        """Test explaining simple pattern"""
        explanations = self.skill.explain(r'^\d+$')
        assert len(explanations) > 0
        # Should have ^, \d, +, $
        chars = [e['char'] for e in explanations]
        assert '^' in chars
        assert '$' in chars
    
    def test_explain_groups(self):
        """Test explaining pattern with groups"""
        explanations = self.skill.explain(r'(\d+)-(\w+)')
        chars = [e['char'] for e in explanations]
        assert '(' in chars
        assert ')' in chars
    
    def test_explain_character_class(self):
        """Test explaining character class"""
        explanations = self.skill.explain(r'[a-z]+')
        has_char_class = any(e['type'] == 'character_class' for e in explanations)
        assert has_char_class
    
    def test_extract_groups_numbered(self):
        """Test extracting numbered groups"""
        results = self.skill.extract_groups(r'(\w+)@(\w+)\.\w+', 'user@example.com')
        assert len(results) == 1
        assert results[0]['full_match'] == 'user@example.com'
        assert results[0]['groups'] == ['user', 'example']
    
    def test_extract_groups_named(self):
        """Test extracting named groups"""
        results = self.skill.extract_groups(r'(?P<user>\w+)@(?P<domain>\w+)', 'admin@test.com')
        assert len(results) == 1
        assert results[0]['named_groups'] == {'user': 'admin', 'domain': 'test'}
    
    def test_extract_multiple_matches(self):
        """Test extracting from multiple matches"""
        results = self.skill.extract_groups(r'(\d+)', 'a1b2c3')
        assert len(results) == 3
        assert results[0]['groups'] == ['1']
        assert results[1]['groups'] == ['2']
        assert results[2]['groups'] == ['3']
    
    def test_builtin_patterns(self):
        """Test all built-in patterns with valid examples"""
        test_cases = {
            'email': ('user@example.com', True),
            'url': ('https://example.com', True),
            'ip': ('192.168.1.1', True),
            'date_iso': ('2024-01-15', True),
            'uuid': ('550e8400-e29b-41d4-a716-446655440000', True),
            'hex_color': ('#FF5733', True),
            'username': ('john_doe-123', True),
        }
        
        for name, (test_input, expected) in test_cases.items():
            pattern_info = self.skill.generate(name)
            if pattern_info:
                is_valid = self.skill.validate(pattern_info['pattern'], test_input)
                assert is_valid == expected, f"Pattern {name} failed for input {test_input}"
    
    def test_match_result_to_dict(self):
        """Test MatchResult to_dict method"""
        result = MatchResult(
            matched=True,
            groups=['a', 'b'],
            start=0,
            end=5,
            text='hello'
        )
        d = result.to_dict()
        assert d['matched'] is True
        assert d['groups'] == ['a', 'b']
        assert d['start'] == 0
        assert d['end'] == 5
        assert d['text'] == 'hello'
    
    def test_parse_flags(self):
        """Test flag parsing"""
        flags = self.skill._parse_flags(['ignorecase', 'multiline'])
        assert flags & re.IGNORECASE
        assert flags & re.MULTILINE
    
    def test_parse_flags_short(self):
        """Test short flag names"""
        flags = self.skill._parse_flags(['i', 'm', 's'])
        assert flags & re.IGNORECASE
        assert flags & re.MULTILINE
        assert flags & re.DOTALL


def run_tests():
    """Run all tests"""
    import pytest
    pytest.main([__file__, '-v'])


if __name__ == '__main__':
    run_tests()
