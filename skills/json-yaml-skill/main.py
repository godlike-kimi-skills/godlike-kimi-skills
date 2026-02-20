#!/usr/bin/env python3
"""
JSON/YAML Skill - Format processing tool
Supports: conversion, validation, query, beautify, merge, diff
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Any, Union, Tuple, List, Optional
from difflib import unified_diff

try:
    import yaml
    from yaml import SafeLoader, SafeDumper
except ImportError:
    yaml = None

try:
    from jsonpath_ng import parse
    JSONPATH_AVAILABLE = True
except ImportError:
    JSONPATH_AVAILABLE = False


class JsonYamlSkill:
    """Main skill class for JSON/YAML processing"""
    
    def __init__(self):
        self.name = "json-yaml-skill"
        self.version = "1.0.0"
    
    def parse_json(self, content: Union[str, bytes, Path]) -> Tuple[Any, Optional[str]]:
        """
        Parse JSON content
        
        Args:
            content: JSON string, bytes, or file path
            
        Returns:
            Tuple of (parsed_data, error_message)
        """
        try:
            if isinstance(content, Path):
                with open(content, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif isinstance(content, bytes):
                content = content.decode('utf-8')
            
            data = json.loads(content)
            return data, None
        except json.JSONDecodeError as e:
            return None, f"JSON parse error: {e}"
        except Exception as e:
            return None, f"Error: {e}"
    
    def parse_yaml(self, content: Union[str, bytes, Path]) -> Tuple[Any, Optional[str]]:
        """
        Parse YAML content
        
        Args:
            content: YAML string, bytes, or file path
            
        Returns:
            Tuple of (parsed_data, error_message)
        """
        if yaml is None:
            return None, "PyYAML not installed. Run: pip install pyyaml"
        
        try:
            if isinstance(content, Path):
                with open(content, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif isinstance(content, bytes):
                content = content.decode('utf-8')
            
            data = yaml.load(content, Loader=SafeLoader)
            return data, None
        except yaml.YAMLError as e:
            return None, f"YAML parse error: {e}"
        except Exception as e:
            return None, f"Error: {e}"
    
    def json_to_yaml(self, content: Union[str, Any], indent: int = 2) -> Tuple[str, Optional[str]]:
        """
        Convert JSON to YAML
        
        Args:
            content: JSON string or parsed data
            indent: YAML indentation level
            
        Returns:
            Tuple of (yaml_string, error_message)
        """
        if yaml is None:
            return None, "PyYAML not installed"
        
        try:
            if isinstance(content, str):
                data, error = self.parse_json(content)
                if error:
                    return None, error
            else:
                data = content
            
            yaml_str = yaml.dump(
                data,
                Dumper=SafeDumper,
                default_flow_style=False,
                indent=indent,
                allow_unicode=True,
                sort_keys=False
            )
            return yaml_str, None
        except Exception as e:
            return None, f"Conversion error: {e}"
    
    def yaml_to_json(self, content: Union[str, Any], indent: int = 2, sort_keys: bool = False) -> Tuple[str, Optional[str]]:
        """
        Convert YAML to JSON
        
        Args:
            content: YAML string or parsed data
            indent: JSON indentation level
            sort_keys: Whether to sort keys
            
        Returns:
            Tuple of (json_string, error_message)
        """
        try:
            if isinstance(content, str):
                data, error = self.parse_yaml(content)
                if error:
                    return None, error
            else:
                data = content
            
            json_str = json.dumps(data, indent=indent, ensure_ascii=False, sort_keys=sort_keys)
            return json_str, None
        except Exception as e:
            return None, f"Conversion error: {e}"
    
    def validate_json(self, content: Union[str, Path]) -> Tuple[bool, Optional[str]]:
        """
        Validate JSON syntax
        
        Args:
            content: JSON string or file path
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        data, error = self.parse_json(content)
        if error:
            return False, error
        return True, None
    
    def validate_yaml(self, content: Union[str, Path]) -> Tuple[bool, Optional[str]]:
        """
        Validate YAML syntax
        
        Args:
            content: YAML string or file path
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        data, error = self.parse_yaml(content)
        if error:
            return False, error
        return True, None
    
    def query_json(self, content: Union[str, Any, Path], query: str) -> Tuple[Any, Optional[str]]:
        """
        Query JSON/YAML data using JSONPath
        
        Args:
            content: Data content or file path
            query: JSONPath expression
            
        Returns:
            Tuple of (results, error_message)
        """
        if not JSONPATH_AVAILABLE:
            return None, "jsonpath-ng not installed. Run: pip install jsonpath-ng"
        
        try:
            if isinstance(content, Path):
                with open(content, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Try JSON first, then YAML
                data, error = self.parse_json(content)
                if error:
                    data, error = self.parse_yaml(content)
            elif isinstance(content, str):
                data, error = self.parse_json(content)
                if error:
                    data, error = self.parse_yaml(content)
            else:
                data = content
                error = None
            
            if error:
                return None, error
            
            jsonpath_expr = parse(query)
            results = [match.value for match in jsonpath_expr.find(data)]
            return results, None
        except Exception as e:
            return None, f"Query error: {e}"
    
    def beautify_json(self, content: Union[str, Any, Path], indent: int = 2, sort_keys: bool = False) -> Tuple[str, Optional[str]]:
        """
        Beautify JSON output
        
        Args:
            content: JSON content or file path
            indent: Indentation level
            sort_keys: Whether to sort keys
            
        Returns:
            Tuple of (formatted_json, error_message)
        """
        try:
            if isinstance(content, Path):
                data, error = self.parse_json(content)
            elif isinstance(content, str):
                data, error = self.parse_json(content)
            else:
                data = content
                error = None
            
            if error:
                return None, error
            
            return json.dumps(data, indent=indent, ensure_ascii=False, sort_keys=sort_keys), None
        except Exception as e:
            return None, f"Beautify error: {e}"
    
    def beautify_yaml(self, content: Union[str, Any, Path], indent: int = 2) -> Tuple[str, Optional[str]]:
        """
        Beautify YAML output
        
        Args:
            content: YAML content or file path
            indent: Indentation level
            
        Returns:
            Tuple of (formatted_yaml, error_message)
        """
        if yaml is None:
            return None, "PyYAML not installed"
        
        try:
            if isinstance(content, Path):
                data, error = self.parse_yaml(content)
            elif isinstance(content, str):
                data, error = self.parse_yaml(content)
            else:
                data = content
                error = None
            
            if error:
                return None, error
            
            return yaml.dump(data, Dumper=SafeDumper, default_flow_style=False, indent=indent, allow_unicode=True, sort_keys=False), None
        except Exception as e:
            return None, f"Beautify error: {e}"
    
    def minify_json(self, content: Union[str, Any, Path]) -> Tuple[str, Optional[str]]:
        """
        Minify JSON (remove whitespace)
        
        Args:
            content: JSON content or file path
            
        Returns:
            Tuple of (minified_json, error_message)
        """
        try:
            if isinstance(content, Path):
                data, error = self.parse_json(content)
            elif isinstance(content, str):
                data, error = self.parse_json(content)
            else:
                data = content
                error = None
            
            if error:
                return None, error
            
            return json.dumps(data, separators=(',', ':'), ensure_ascii=False), None
        except Exception as e:
            return None, f"Minify error: {e}"
    
    def merge_json(self, files: List[Union[str, Path]], merge_strategy: str = "deep") -> Tuple[Any, Optional[str]]:
        """
        Merge multiple JSON/YAML files
        
        Args:
            files: List of file paths
            merge_strategy: "shallow" or "deep" merge
            
        Returns:
            Tuple of (merged_data, error_message)
        """
        try:
            merged = {}
            
            for file_path in files:
                path = Path(file_path)
                if not path.exists():
                    return None, f"File not found: {file_path}"
                
                # Try JSON first, then YAML
                data, error = self.parse_json(path)
                if error:
                    data, error = self.parse_yaml(path)
                
                if error:
                    return None, f"Error parsing {file_path}: {error}"
                
                if merge_strategy == "deep":
                    merged = self._deep_merge(merged, data)
                else:
                    merged.update(data)
            
            return merged, None
        except Exception as e:
            return None, f"Merge error: {e}"
    
    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def diff_files(self, file1: Union[str, Path], file2: Union[str, Path]) -> Tuple[str, Optional[str]]:
        """
        Compare two JSON/YAML files
        
        Args:
            file1: First file path
            file2: Second file path
            
        Returns:
            Tuple of (diff_output, error_message)
        """
        try:
            # Parse both files
            data1, error1 = self.parse_json(file1)
            if error1:
                data1, error1 = self.parse_yaml(file1)
            
            data2, error2 = self.parse_json(file2)
            if error2:
                data2, error2 = self.parse_yaml(file2)
            
            if error1:
                return None, f"Error parsing file1: {error1}"
            if error2:
                return None, f"Error parsing file2: {error2}"
            
            # Convert to formatted JSON for comparison
            str1 = json.dumps(data1, indent=2, sort_keys=True, ensure_ascii=False)
            str2 = json.dumps(data2, indent=2, sort_keys=True, ensure_ascii=False)
            
            lines1 = str1.splitlines()
            lines2 = str2.splitlines()
            
            diff = list(unified_diff(lines1, lines2, lineterm='', fromfile=str(file1), tofile=str(file2)))
            
            return '\n'.join(diff) if diff else "No differences found", None
        except Exception as e:
            return None, f"Diff error: {e}"


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='JSON/YAML Processing Tool')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert between formats')
    convert_parser.add_argument('input', help='Input file')
    convert_parser.add_argument('output', help='Output file')
    convert_parser.add_argument('--indent', type=int, default=2, help='Indentation level')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate file')
    validate_parser.add_argument('file', help='File to validate')
    validate_parser.add_argument('--format', choices=['json', 'yaml', 'auto'], default='auto', help='Format type')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query data with JSONPath')
    query_parser.add_argument('file', help='File to query')
    query_parser.add_argument('expression', help='JSONPath expression')
    
    # Beautify command
    beautify_parser = subparsers.add_parser('beautify', help='Beautify file')
    beautify_parser.add_argument('file', help='File to beautify')
    beautify_parser.add_argument('--indent', type=int, default=2, help='Indentation level')
    beautify_parser.add_argument('--output', '-o', help='Output file')
    
    # Minify command
    minify_parser = subparsers.add_parser('minify', help='Minify JSON file')
    minify_parser.add_argument('file', help='File to minify')
    minify_parser.add_argument('--output', '-o', help='Output file')
    
    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Merge multiple files')
    merge_parser.add_argument('files', nargs='+', help='Files to merge')
    merge_parser.add_argument('--output', '-o', required=True, help='Output file')
    merge_parser.add_argument('--strategy', choices=['shallow', 'deep'], default='deep', help='Merge strategy')
    
    # Diff command
    diff_parser = subparsers.add_parser('diff', help='Compare two files')
    diff_parser.add_argument('file1', help='First file')
    diff_parser.add_argument('file2', help='Second file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    skill = JsonYamlSkill()
    
    if args.command == 'convert':
        input_path = Path(args.input)
        output_path = Path(args.output)
        
        # Determine conversion direction based on extensions
        if input_path.suffix.lower() in ['.yaml', '.yml'] and output_path.suffix.lower() == '.json':
            result, error = skill.yaml_to_json(input_path, indent=args.indent)
        elif input_path.suffix.lower() == '.json' and output_path.suffix.lower() in ['.yaml', '.yml']:
            result, error = skill.json_to_yaml(input_path, indent=args.indent)
        else:
            # Auto-detect: try parsing as both formats
            data, error = skill.parse_json(input_path)
            if error:
                data, error = skill.parse_yaml(input_path)
            if error:
                print(f"Error: Could not parse input file: {error}")
                return
            
            if output_path.suffix.lower() == '.json':
                result, error = skill.yaml_to_json(data, indent=args.indent)
            else:
                result, error = skill.json_to_yaml(data, indent=args.indent)
        
        if error:
            print(f"Error: {error}")
            return
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Converted: {args.input} -> {args.output}")
    
    elif args.command == 'validate':
        if args.format == 'json':
            is_valid, error = skill.validate_json(args.file)
        elif args.format == 'yaml':
            is_valid, error = skill.validate_yaml(args.file)
        else:
            is_valid, error = skill.validate_json(args.file)
            if not is_valid:
                is_valid, error = skill.validate_yaml(args.file)
        
        if is_valid:
            print(f"✓ {args.file} is valid")
        else:
            print(f"✗ {args.file} is invalid: {error}")
    
    elif args.command == 'query':
        results, error = skill.query_json(args.file, args.expression)
        if error:
            print(f"Error: {error}")
            return
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    elif args.command == 'beautify':
        input_path = Path(args.file)
        if input_path.suffix.lower() == '.json':
            result, error = skill.beautify_json(input_path, indent=args.indent)
        else:
            result, error = skill.beautify_yaml(input_path, indent=args.indent)
        
        if error:
            print(f"Error: {error}")
            return
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"Beautified: {args.file} -> {args.output}")
        else:
            print(result)
    
    elif args.command == 'minify':
        result, error = skill.minify_json(args.file)
        if error:
            print(f"Error: {error}")
            return
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"Minified: {args.file} -> {args.output}")
        else:
            print(result)
    
    elif args.command == 'merge':
        merged, error = skill.merge_json(args.files, args.strategy)
        if error:
            print(f"Error: {error}")
            return
        
        output_path = Path(args.output)
        if output_path.suffix.lower() == '.json':
            content = json.dumps(merged, indent=2, ensure_ascii=False)
        else:
            content, _ = skill.json_to_yaml(merged)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Merged {len(args.files)} files -> {args.output}")
    
    elif args.command == 'diff':
        diff, error = skill.diff_files(args.file1, args.file2)
        if error:
            print(f"Error: {error}")
            return
        print(diff)


if __name__ == '__main__':
    main()
