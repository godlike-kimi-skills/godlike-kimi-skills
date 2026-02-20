---
name: api-testing-skill
description: API automation testing framework. Use when writing API tests, automating endpoint testing, validating API responses, or when user mentions 'API test', 'endpoint test', 'integration test', 'assertion', 'test case', 'API validation', 'response check', 'automated testing', 'test suite'. Supports test case definition, assertion validation, test reports, and batch testing.
---

# API Testing Skill

API automation testing framework for comprehensive endpoint validation and test automation.

## Capabilities

- **Test Case Definition**: JSON/YAML test specifications
- **Assertion Validation**: Status codes, JSON schema, response values
- **Batch Testing**: Run multiple tests in sequence
- **Test Reports**: HTML/JSON report generation
- **Environment Variables**: Configurable test environments
- **Request Chaining**: Use response data in subsequent tests
- **Hooks**: Pre/post test actions

## Use When

- Writing automated API tests
- Validating REST API responses
- Creating regression test suites
- Testing API endpoints systematically
- Generating test reports
- Setting up CI/CD API testing
- Validating JSON schema compliance

## Out of Scope

- Performance/load testing (use load-testing skill)
- UI/browser automation
- Database testing
- Mobile app testing
- Security penetration testing

## Quick Start

### Define Test Case

```yaml
# test_case.yaml
name: User API Test
request:
  method: GET
  url: https://api.example.com/users/1
  headers:
    Authorization: Bearer ${TOKEN}
assertions:
  - type: status_code
    expected: 200
  - type: json_path
    path: $.name
    expected: "John Doe"
  - type: header
    name: Content-Type
    expected: "application/json"
```

### Run Tests

```python
from scripts.main import APITester

tester = APITester()
results = tester.run_from_file("test_case.yaml")
```

### CLI Usage

```bash
# Run single test
python scripts/main.py test_case.yaml

# Run test suite
python scripts/main.py suite.yaml --report

# With environment variables
python scripts/main.py test.yaml --env TOKEN=abc123

# Generate HTML report
python scripts/main.py suite.yaml --format html --output report.html
```

## Test Case Format

See [references/test_format.md](references/test_format.md) for complete test case specification.

## Assertion Types

- `status_code`: HTTP status code check
- `json_path`: JSON value extraction and comparison
- `header`: Response header validation
- `body_contains`: Body content search
- `json_schema`: JSON schema validation
- `response_time`: Response time threshold

## Reference

See [references/examples.md](references/examples.md) for example test cases.
