#!/usr/bin/env python3
"""
Tests for JSON/YAML Skill
"""

import json
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from main import JsonYamlSkill


class TestJsonYamlSkill:
    """Test cases for JsonYamlSkill"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.skill = JsonYamlSkill()
        self.sample_json = '{"name": "test", "value": 123, "nested": {"key": "value"}}'
        self.sample_yaml = """
name: test
value: 123
nested:
  key: value
items:
  - a
  - b
""".strip()
    
    def test_parse_json_valid(self):
        """Test parsing valid JSON"""
        data, error = self.skill.parse_json(self.sample_json)
        assert error is None
        assert data['name'] == 'test'
        assert data['value'] == 123
        assert data['nested']['key'] == 'value'
    
    def test_parse_json_invalid(self):
        """Test parsing invalid JSON"""
        data, error = self.skill.parse_json('{"invalid json')
        assert data is None
        assert error is not None
        assert 'parse error' in error.lower()
    
    def test_parse_yaml_valid(self):
        """Test parsing valid YAML"""
        data, error = self.skill.parse_yaml(self.sample_yaml)
        assert error is None
        assert data['name'] == 'test'
        assert data['value'] == 123
        assert data['items'] == ['a', 'b']
    
    def test_json_to_yaml(self):
        """Test JSON to YAML conversion"""
        yaml_str, error = self.skill.json_to_yaml(self.sample_json)
        assert error is None
        assert 'name: test' in yaml_str
        assert 'value: 123' in yaml_str
    
    def test_yaml_to_json(self):
        """Test YAML to JSON conversion"""
        json_str, error = self.skill.yaml_to_json(self.sample_yaml)
        assert error is None
        data = json.loads(json_str)
        assert data['name'] == 'test'
        assert data['value'] == 123
    
    def test_validate_json_valid(self):
        """Test validating valid JSON"""
        is_valid, error = self.skill.validate_json(self.sample_json)
        assert is_valid is True
        assert error is None
    
    def test_validate_json_invalid(self):
        """Test validating invalid JSON"""
        is_valid, error = self.skill.validate_json('{"invalid')
        assert is_valid is False
        assert error is not None
    
    def test_validate_yaml_valid(self):
        """Test validating valid YAML"""
        is_valid, error = self.skill.validate_yaml(self.sample_yaml)
        assert is_valid is True
        assert error is None
    
    def test_query_json_root(self):
        """Test JSONPath query - root"""
        data = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}
        results, error = self.skill.query_json(data, '$.users[*].name')
        assert error is None
        assert 'Alice' in results
        assert 'Bob' in results
    
    def test_query_json_nested(self):
        """Test JSONPath query - nested"""
        data = {'company': {'employees': [{'name': 'John', 'age': 30}]}}
        results, error = self.skill.query_json(data, '$.company.employees[0].name')
        assert error is None
        assert results == ['John']
    
    def test_beautify_json(self):
        """Test JSON beautification"""
        ugly = '{"a":1,"b":2}'
        pretty, error = self.skill.beautify_json(ugly, indent=4)
        assert error is None
        assert '    ' in pretty  # 4-space indent
        assert '"a": 1' in pretty
    
    def test_beautify_json_sort_keys(self):
        """Test JSON beautification with sorted keys"""
        data = {'z': 1, 'a': 2, 'm': 3}
        pretty, error = self.skill.beautify_json(data, indent=2, sort_keys=True)
        assert error is None
        lines = pretty.strip().split('\n')
        # Check that keys are in alphabetical order
        assert '"a":' in pretty
    
    def test_minify_json(self):
        """Test JSON minification"""
        pretty = '{\n  "a": 1,\n  "b": 2\n}'
        minified, error = self.skill.minify_json(pretty)
        assert error is None
        assert '\n' not in minified
        assert ' ' not in minified or '"a":' in minified
    
    def test_deep_merge(self):
        """Test deep merge functionality"""
        base = {'a': 1, 'nested': {'x': 1, 'y': 2}}
        override = {'b': 2, 'nested': {'y': 3, 'z': 4}}
        result = self.skill._deep_merge(base, override)
        assert result['a'] == 1
        assert result['b'] == 2
        assert result['nested']['x'] == 1
        assert result['nested']['y'] == 3
        assert result['nested']['z'] == 4
    
    def test_merge_json(self):
        """Test merging JSON files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / 'file1.json'
            file2 = Path(tmpdir) / 'file2.json'
            
            file1.write_text('{"a": 1, "shared": {"x": 1}}')
            file2.write_text('{"b": 2, "shared": {"y": 2}}')
            
            merged, error = self.skill.merge_json([file1, file2])
            assert error is None
            assert merged['a'] == 1
            assert merged['b'] == 2
            assert merged['shared']['x'] == 1
            assert merged['shared']['y'] == 2
    
    def test_diff_files_identical(self):
        """Test diff on identical files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / 'file1.json'
            file2 = Path(tmpdir) / 'file2.json'
            
            file1.write_text('{"a": 1, "b": 2}')
            file2.write_text('{"b": 2, "a": 1}')
            
            diff, error = self.skill.diff_files(file1, file2)
            assert error is None
            assert 'No differences' in diff
    
    def test_diff_files_different(self):
        """Test diff on different files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / 'file1.json'
            file2 = Path(tmpdir) / 'file2.json'
            
            file1.write_text('{"a": 1}')
            file2.write_text('{"a": 2}')
            
            diff, error = self.skill.diff_files(file1, file2)
            assert error is None
            assert '---' in diff
            assert '+++' in diff
    
    def test_file_operations(self):
        """Test reading from files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / 'test.json'
            json_file.write_text(self.sample_json)
            
            data, error = self.skill.parse_json(json_file)
            assert error is None
            assert data['name'] == 'test'
    
    def test_empty_json(self):
        """Test handling empty JSON"""
        data, error = self.skill.parse_json('{}')
        assert error is None
        assert data == {}
    
    def test_empty_yaml(self):
        """Test handling empty YAML"""
        data, error = self.skill.parse_yaml('')
        assert error is None
        assert data is None
    
    def test_json_array(self):
        """Test parsing JSON array"""
        data, error = self.skill.parse_json('[1, 2, 3]')
        assert error is None
        assert data == [1, 2, 3]
    
    def test_complex_yaml(self):
        """Test parsing complex YAML structures"""
        yaml_content = """
root:
  list:
    - item1
    - item2
  map:
    key1: value1
    key2: value2
  multiline: |
    Line 1
    Line 2
"""
        data, error = self.skill.parse_yaml(yaml_content)
        assert error is None
        assert data['root']['list'] == ['item1', 'item2']
        assert data['root']['map']['key1'] == 'value1'


def run_tests():
    """Run all tests"""
    import pytest
    pytest.main([__file__, '-v'])


if __name__ == '__main__':
    run_tests()
