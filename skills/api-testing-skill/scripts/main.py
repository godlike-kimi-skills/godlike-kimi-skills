#!/usr/bin/env python3
"""
API Testing Skill - Main module for API automation testing.

Features:
- Test case definition (JSON/YAML)
- Assertion validation (status, JSON, headers)
- Batch test execution
- Report generation (HTML/JSON)
- Environment variables
- Request chaining
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests
import yaml
from jsonschema import validate, ValidationError as JSONSchemaError


@dataclass
class TestResult:
    """Test execution result container."""
    name: str
    passed: bool
    duration_ms: float
    assertions: List[Dict] = field(default_factory=list)
    error_message: Optional[str] = None
    request_info: Dict = field(default_factory=dict)
    response_info: Dict = field(default_factory=dict)


@dataclass
class TestCase:
    """Test case definition container."""
    name: str
    request: Dict
    assertions: List[Dict]
    description: str = ""
    skip: bool = False
    depends_on: Optional[str] = None
    variables: Dict = field(default_factory=dict)


class APITester:
    """
    API automation testing framework.
    
    Features:
    - YAML/JSON test case definitions
    - Multiple assertion types
    - Environment variable substitution
    - Test chaining with variable extraction
    - HTML/JSON report generation
    """
    
    def __init__(self, env_vars: Optional[Dict[str, str]] = None):
        """
        Initialize API tester.
        
        Args:
            env_vars: Environment variables for substitution
        """
        self.env_vars = env_vars or {}
        self.session = requests.Session()
        self.test_results: List[TestResult] = []
        self.variables: Dict[str, Any] = {}  # Runtime variables
    
    def _substitute_variables(self, value: Any) -> Any:
        """Substitute environment variables in value."""
        if isinstance(value, str):
            # Pattern: ${VAR_NAME} or ${VAR_NAME:default}
            pattern = r'\$\{(\w+)(?::([^}]+))?\}'
            
            def replacer(match):
                var_name = match.group(1)
                default = match.group(2)
                
                # Check runtime variables first
                if var_name in self.variables:
                    return str(self.variables[var_name])
                
                # Then environment variables
                if var_name in self.env_vars:
                    return str(self.env_vars[var_name])
                
                # Then system environment
                result = os.environ.get(var_name, default)
                if result is None:
                    raise ValueError(f"Variable '{var_name}' not found")
                return result
            
            return re.sub(pattern, replacer, value)
        elif isinstance(value, dict):
            return {k: self._substitute_variables(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._substitute_variables(v) for v in value]
        return value
    
    def _extract_json_value(self, data: Any, path: str) -> Any:
        """Extract value from JSON using dot or bracket notation."""
        current = data
        
        # Handle bracket notation: $['key'] or $.key
        tokens = re.findall(r"\['([^']+)'\]|\.(\w+)", path.replace('$', ''))
        
        for bracket_key, dot_key in tokens:
            key = bracket_key if bracket_key else dot_key
            
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list):
                try:
                    idx = int(key)
                    current = current[idx] if 0 <= idx < len(current) else None
                except ValueError:
                    current = None
            else:
                current = None
            
            if current is None:
                return None
        
        return current
    
    def _execute_assertion(
        self,
        assertion: Dict,
        response: requests.Response
    ) -> Dict:
        """Execute single assertion and return result."""
        assertion_type = assertion.get('type', 'status_code')
        result = {
            'type': assertion_type,
            'passed': False,
            'message': ''
        }
        
        try:
            if assertion_type == 'status_code':
                expected = assertion['expected']
                actual = response.status_code
                result['passed'] = actual == expected
                result['message'] = f"Expected {expected}, got {actual}"
                result['actual'] = actual
                result['expected'] = expected
            
            elif assertion_type == 'json_path':
                path = assertion['path']
                expected = self._substitute_variables(assertion['expected'])
                data = response.json()
                actual = self._extract_json_value(data, path)
                
                result['passed'] = actual == expected
                result['message'] = f"Path '{path}': Expected {expected}, got {actual}"
                result['actual'] = actual
                result['expected'] = expected
            
            elif assertion_type == 'header':
                name = assertion['name']
                expected = self._substitute_variables(assertion['expected'])
                actual = response.headers.get(name)
                
                result['passed'] = actual == expected
                result['message'] = f"Header '{name}': Expected {expected}, got {actual}"
                result['actual'] = actual
                result['expected'] = expected
            
            elif assertion_type == 'body_contains':
                expected = self._substitute_variables(assertion['expected'])
                actual = response.text
                
                result['passed'] = expected in actual
                result['message'] = f"Body contains '{expected}'"
                result['actual'] = 'contains' if expected in actual else 'not contains'
            
            elif assertion_type == 'json_schema':
                schema = assertion['schema']
                if isinstance(schema, str) and schema.startswith('file:'):
                    schema_path = schema[5:]
                    with open(schema_path) as f:
                        schema = json.load(f)
                
                data = response.json()
                validate(instance=data, schema=schema)
                result['passed'] = True
                result['message'] = "JSON schema validation passed"
            
            elif assertion_type == 'response_time':
                expected_max = assertion.get('max_ms', 1000)
                actual_ms = response.elapsed.total_seconds() * 1000
                
                result['passed'] = actual_ms <= expected_max
                result['message'] = f"Response time: {actual_ms:.2f}ms (max: {expected_max}ms)"
                result['actual'] = actual_ms
            
            else:
                result['message'] = f"Unknown assertion type: {assertion_type}"
        
        except Exception as e:
            result['passed'] = False
            result['message'] = f"Assertion error: {str(e)}"
        
        return result
    
    def _extract_variables(
        self,
        response: requests.Response,
        extractions: List[Dict]
    ):
        """Extract variables from response for chaining."""
        try:
            json_data = response.json()
        except:
            json_data = None
        
        for extraction in extractions:
            name = extraction['name']
            source = extraction.get('source', 'json_body')
            path = extraction.get('path')
            
            if source == 'json_body' and json_data and path:
                self.variables[name] = self._extract_json_value(json_data, path)
            elif source == 'header':
                self.variables[name] = response.headers.get(path)
            elif source == 'status_code':
                self.variables[name] = response.status_code
    
    def run_test(self, test_case: TestCase) -> TestResult:
        """
        Execute single test case.
        
        Args:
            test_case: Test case definition
        
        Returns:
            TestResult with execution details
        """
        if test_case.skip:
            return TestResult(
                name=test_case.name,
                passed=True,
                duration_ms=0,
                error_message="Skipped"
            )
        
        start_time = datetime.now()
        assertions = []
        
        try:
            # Substitute variables in request
            request_config = self._substitute_variables(test_case.request)
            
            # Prepare request
            method = request_config.get('method', 'GET').upper()
            url = request_config['url']
            headers = request_config.get('headers', {})
            params = request_config.get('params')
            
            # Body handling
            data = None
            json_data = None
            if 'json' in request_config:
                json_data = request_config['json']
            elif 'data' in request_config:
                data = request_config['data']
            
            # Execute request
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                timeout=request_config.get('timeout', 30)
            )
            
            # Extract variables if configured
            if 'extract' in request_config:
                self._extract_variables(response, request_config['extract'])
            
            # Run assertions
            all_passed = True
            for assertion in test_case.assertions:
                result = self._execute_assertion(assertion, response)
                assertions.append(result)
                if not result['passed']:
                    all_passed = False
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return TestResult(
                name=test_case.name,
                passed=all_passed,
                duration_ms=duration,
                assertions=assertions,
                request_info={
                    'method': method,
                    'url': url,
                    'headers': headers
                },
                response_info={
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'body_preview': response.text[:500]
                }
            )
        
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return TestResult(
                name=test_case.name,
                passed=False,
                duration_ms=duration,
                assertions=assertions,
                error_message=str(e)
            )
    
    def run_from_file(self, filepath: str) -> List[TestResult]:
        """
        Load and run tests from YAML/JSON file.
        
        Args:
            filepath: Path to test file
        
        Returns:
            List of test results
        """
        path = Path(filepath)
        
        with open(path) as f:
            if path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        # Handle single test or test suite
        if 'tests' in data:
            # Test suite
            results = []
            for test_data in data['tests']:
                test_case = TestCase(
                    name=test_data.get('name', 'Unnamed'),
                    request=test_data['request'],
                    assertions=test_data.get('assertions', []),
                    description=test_data.get('description', ''),
                    skip=test_data.get('skip', False)
                )
                results.append(self.run_test(test_case))
            return results
        else:
            # Single test
            test_case = TestCase(
                name=data.get('name', 'Unnamed'),
                request=data['request'],
                assertions=data.get('assertions', []),
                description=data.get('description', ''),
                skip=data.get('skip', False)
            )
            return [self.run_test(test_case)]
    
    def generate_report(
        self,
        results: List[TestResult],
        format_type: str = 'text'
    ) -> str:
        """Generate test report."""
        if format_type == 'json':
            return self._generate_json_report(results)
        elif format_type == 'html':
            return self._generate_html_report(results)
        else:
            return self._generate_text_report(results)
    
    def _generate_text_report(self, results: List[TestResult]) -> str:
        """Generate text report."""
        lines = [
            "=" * 70,
            "API Test Results",
            "=" * 70,
            f"Total: {len(results)} | Passed: {sum(1 for r in results if r.passed)} | Failed: {sum(1 for r in results if not r.passed)}",
            ""
        ]
        
        for result in results:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            lines.append(f"{status} - {result.name} ({result.duration_ms:.2f}ms)")
            
            if result.error_message and result.error_message != "Skipped":
                lines.append(f"  Error: {result.error_message}")
            
            for assertion in result.assertions:
                a_status = "✓" if assertion['passed'] else "✗"
                lines.append(f"  {a_status} {assertion['type']}: {assertion['message']}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_json_report(self, results: List[TestResult]) -> str:
        """Generate JSON report."""
        report = {
            'summary': {
                'total': len(results),
                'passed': sum(1 for r in results if r.passed),
                'failed': sum(1 for r in results if not r.passed),
                'timestamp': datetime.now().isoformat()
            },
            'results': []
        }
        
        for result in results:
            report['results'].append({
                'name': result.name,
                'passed': result.passed,
                'duration_ms': result.duration_ms,
                'error': result.error_message,
                'assertions': result.assertions
            })
        
        return json.dumps(report, indent=2)
    
    def _generate_html_report(self, results: List[TestResult]) -> str:
        """Generate HTML report."""
        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if not r.passed)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>API Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .summary {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .test {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .assertion {{ margin-left: 20px; font-size: 14px; }}
        pre {{ background: #f5f5f5; padding: 10px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>API Test Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p>Total: {len(results)} | <span class="passed">Passed: {passed}</span> | <span class="failed">Failed: {failed}</span></p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    <h2>Test Results</h2>
"""
        
        for result in results:
            status_class = 'passed' if result.passed else 'failed'
            status_text = 'PASS' if result.passed else 'FAIL'
            
            html += f"""
    <div class="test">
        <h3 class="{status_class}">{status_text} - {result.name}</h3>
        <p>Duration: {result.duration_ms:.2f}ms</p>
"""
            if result.error_message:
                html += f"        <p class='failed'>Error: {result.error_message}</p>\n"
            
            for assertion in result.assertions:
                a_class = 'passed' if assertion['passed'] else 'failed'
                a_icon = '✓' if assertion['passed'] else '✗'
                html += f"""
        <div class="assertion {a_class}">
            {a_icon} {assertion['type']}: {assertion['message']}
        </div>
"""
            html += "    </div>\n"
        
        html += "</body>\n</html>"
        return html


def parse_env_vars(env_list: list) -> Dict[str, str]:
    """Parse environment variable strings."""
    result = {}
    for env in env_list:
        if '=' in env:
            key, value = env.split('=', 1)
            result[key] = value
    return result


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="API Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s test.yaml
  %(prog)s suite.yaml --env TOKEN=abc123 --env BASE_URL=https://api.example.com
  %(prog)s tests/ --format html --output report.html
        """
    )
    
    parser.add_argument("test_file", help="Test file or directory")
    parser.add_argument("--env", action="append", default=[],
                       help="Environment variable (KEY=VALUE)")
    parser.add_argument("--format", choices=['text', 'json', 'html'], default='text',
                       help="Output format (default: text)")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Parse environment variables
    env_vars = parse_env_vars(args.env)
    
    try:
        tester = APITester(env_vars=env_vars)
        
        # Run tests
        results = tester.run_from_file(args.test_file)
        
        # Generate report
        report = tester.generate_report(results, args.format)
        
        # Output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"Report saved to {args.output}")
        else:
            print(report)
        
        # Exit with error code if any tests failed
        sys.exit(0 if all(r.passed for r in results) else 1)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
