#!/usr/bin/env python3
"""
Tests for UUID Generator Skill
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from main import UUIDGeneratorSkill, UUIDInfo


class TestUUIDGeneratorSkill:
    """Test cases for UUIDGeneratorSkill"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.skill = UUIDGeneratorSkill()
    
    def test_uuid_v4_format(self):
        """Test UUID v4 format"""
        u = self.skill.uuid_v4()
        # Check format: 8-4-4-4-12 hex digits
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        assert re.match(pattern, u), f"Invalid UUID v4 format: {u}"
    
    def test_uuid_v1_format(self):
        """Test UUID v1 format"""
        u = self.skill.uuid_v1()
        # v1 starts with timestamp
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-1[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        assert re.match(pattern, u), f"Invalid UUID v1 format: {u}"
    
    def test_uuid_v7_format(self):
        """Test UUID v7 format"""
        u = self.skill.uuid_v7()
        # v7 starts with timestamp, has version 7
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        assert re.match(pattern, u), f"Invalid UUID v7 format: {u}"
    
    def test_uuid_v7_sortable(self):
        """Test that UUID v7 is time-sortable"""
        uuids = [self.skill.uuid_v7() for _ in range(5)]
        # UUIDs should be in ascending order by time
        assert uuids == sorted(uuids), "UUID v7 not sortable by time"
    
    def test_uuid_uniqueness(self):
        """Test UUID uniqueness"""
        uuids = [self.skill.uuid_v4() for _ in range(100)]
        assert len(set(uuids)) == 100, "UUIDs not unique"
    
    def test_batch_uuid(self):
        """Test batch UUID generation"""
        uuids = self.skill.batch_uuid(count=5, version=4)
        assert len(uuids) == 5
        for u in uuids:
            assert self.skill.validate(u)
    
    def test_short_id_length(self):
        """Test short ID length"""
        for length in [6, 8, 12, 16]:
            sid = self.skill.short_id(length)
            assert len(sid) == length, f"Short ID length mismatch: expected {length}, got {len(sid)}"
    
    def test_short_id_charset(self):
        """Test short ID character set"""
        sid = self.skill.short_id(100)  # Long string to check all chars
        allowed = set(self.skill.BASE62_ALPHABET)
        assert set(sid).issubset(allowed), "Short ID contains invalid characters"
    
    def test_short_id_uniqueness(self):
        """Test short ID uniqueness"""
        ids = [self.skill.short_id(8) for _ in range(1000)]
        assert len(set(ids)) == 1000, "Short IDs not unique"
    
    def test_nanoid_length(self):
        """Test NanoID length"""
        for size in [10, 16, 21, 32]:
            nid = self.skill.nanoid(size)
            assert len(nid) == size, f"NanoID length mismatch: expected {size}, got {len(nid)}"
    
    def test_nanoid_charset(self):
        """Test NanoID character set"""
        nid = self.skill.nanoid(100)
        allowed = set(self.skill.NANOID_ALPHABET)
        assert set(nid).issubset(allowed), "NanoID contains invalid characters"
    
    def test_cuid_format(self):
        """Test CUID format"""
        c = self.skill.cuid()
        # CUID starts with 'c' followed by base36 characters
        assert c.startswith('c'), "CUID should start with 'c'"
        assert len(c) == 25, f"CUID length should be 25, got {len(c)}"
        assert re.match(r'^c[a-z0-9]{24}$', c), "Invalid CUID format"
    
    def test_cuid_uniqueness(self):
        """Test CUID uniqueness"""
        cuids = [self.skill.cuid() for _ in range(100)]
        assert len(set(cuids)) == 100, "CUIDs not unique"
    
    def test_random_string_default(self):
        """Test random string with default options"""
        s = self.skill.random_string(32)
        assert len(s) == 32
        # Should contain uppercase, lowercase, and digits
        assert any(c.isupper() for c in s)
        assert any(c.islower() for c in s)
        assert any(c.isdigit() for c in s)
    
    def test_random_string_uppercase_only(self):
        """Test random string with uppercase only"""
        s = self.skill.random_string(32, use_uppercase=True, use_lowercase=False, use_digits=False)
        assert all(c.isupper() for c in s)
    
    def test_random_string_digits_only(self):
        """Test random string with digits only"""
        s = self.skill.random_string(32, use_uppercase=False, use_lowercase=False, use_digits=True)
        assert all(c.isdigit() for c in s)
    
    def test_alphanumeric(self):
        """Test alphanumeric generation"""
        s = self.skill.alphanumeric(32)
        assert len(s) == 32
        assert s.isalnum()
    
    def test_hex_string(self):
        """Test hex string generation"""
        s = self.skill.hex_string(32)
        assert len(s) == 32
        assert all(c in '0123456789abcdef' for c in s.lower())
    
    def test_base64_string(self):
        """Test base64 string generation"""
        s = self.skill.base64_string(32)
        assert len(s) == 32
        allowed = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-=')
        assert set(s).issubset(allowed)
    
    def test_validate_valid_uuid(self):
        """Test validating valid UUID"""
        u = self.skill.uuid_v4()
        assert self.skill.validate(u) is True
    
    def test_validate_valid_uuid_uppercase(self):
        """Test validating uppercase UUID"""
        u = self.skill.uuid_v4().upper()
        assert self.skill.validate(u) is True
    
    def test_validate_invalid_uuid(self):
        """Test validating invalid UUID"""
        assert self.skill.validate('not-a-uuid') is False
        assert self.skill.validate('12345') is False
        assert self.skill.validate('') is False
        assert self.skill.validate('550e8400-e29b-41d4-a716-44665544000') is False  # Too short
        assert self.skill.validate('550e8400-e29b-41d4-a716-4466554400000') is False  # Too long
    
    def test_parse_valid_v4(self):
        """Test parsing valid UUID v4"""
        u = self.skill.uuid_v4()
        info = self.skill.parse(u)
        assert info is not None
        assert info.version == 4
        assert info.is_valid is True
    
    def test_parse_valid_v1(self):
        """Test parsing valid UUID v1"""
        u = self.skill.uuid_v1()
        info = self.skill.parse(u)
        assert info is not None
        assert info.version == 1
        assert info.time is not None
    
    def test_parse_valid_v7(self):
        """Test parsing valid UUID v7"""
        u = self.skill.uuid_v7()
        info = self.skill.parse(u)
        assert info is not None
        assert info.version == 7
        assert info.time is not None
    
    def test_parse_invalid(self):
        """Test parsing invalid UUID"""
        info = self.skill.parse('invalid')
        assert info is None
    
    def test_slug_generation(self):
        """Test slug generation from UUID"""
        u = self.skill.uuid_v4()
        slug = self.skill.slug(u)
        assert len(slug) < 36  # Slug should be shorter than UUID
        assert all(c in self.skill.BASE62_ALPHABET for c in slug)
    
    def test_slug_new_uuid(self):
        """Test generating slug from new UUID"""
        slug = self.skill.slug()
        assert slug
        assert all(c in self.skill.BASE62_ALPHABET for c in slug)
    
    def test_slug_invalid_uuid(self):
        """Test slug with invalid UUID"""
        try:
            self.skill.slug('invalid')
            assert False, "Should raise ValueError"
        except ValueError:
            pass
    
    def test_random_string_error_no_charset(self):
        """Test error when no character set selected"""
        try:
            self.skill.random_string(32, use_uppercase=False, use_lowercase=False, use_digits=False)
            assert False, "Should raise ValueError"
        except ValueError:
            pass


def run_tests():
    """Run all tests"""
    import pytest
    pytest.main([__file__, '-v'])


if __name__ == '__main__':
    run_tests()
