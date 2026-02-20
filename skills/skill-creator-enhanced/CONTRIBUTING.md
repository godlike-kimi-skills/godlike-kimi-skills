# Contributing to Skill Creator Enhanced

Thank you for your interest in contributing to Skill Creator Enhanced! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to:

- Being respectful and inclusive
- Welcoming newcomers
- Focusing on constructive feedback
- Prioritizing the community's success

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/skill-creator-enhanced.git
   cd skill-creator-enhanced
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/godlike-kimi-skills/skill-creator-enhanced.git
   ```

## Development Setup

### Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_basic.py
```

## How to Contribute

### Reporting Bugs

Before creating a bug report, please:

1. Check if the issue already exists
2. Use the latest version
3. Include:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version)
   - Error messages or logs

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:

1. Check if the enhancement has already been suggested
2. Provide clear use case
3. Explain expected behavior
4. Consider implementation approach

### Adding New Templates

To add a new template:

1. Add template configuration to `TEMPLATES` dict in `main.py`
2. Create template generation method (e.g., `_get_new_template`)
3. Add tests in `tests/test_advanced.py`
4. Update documentation
5. Add example usage

### Improving Documentation

Documentation improvements are always welcome:

- Fix typos
- Clarify instructions
- Add examples
- Translate to other languages

## Pull Request Process

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make Changes**
   - Write clear, concise code
   - Add tests for new functionality
   - Update documentation
   - Follow coding standards

3. **Test Your Changes**
   ```bash
   python -m pytest tests/
   flake8 main.py
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "type: clear description of changes"
   ```
   
   Commit message format:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test additions/changes
   - `refactor:` Code refactoring
   - `style:` Formatting changes

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   Then create a pull request on GitHub.

6. **PR Review**
   - Address review comments
   - Keep discussions focused
   - Be patient and respectful

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- Maximum line length: 100 characters
- Use double quotes for strings
- Add docstrings to all functions and classes

### Type Hints

Use type hints for function parameters and return values:

```python
def create_skill(
    self,
    skill_name: str,
    skill_title: str,
    description: str,
    category: str = "other"
) -> Path:
    """Create a new skill project."""
    ...
```

### Documentation

All functions should have docstrings:

```python
def process_data(data: List[Dict]) -> List[Dict]:
    """
    Process input data and return results.
    
    Args:
        data: List of dictionaries containing input data
        
    Returns:
        Processed data as list of dictionaries
        
    Raises:
        ValueError: If data format is invalid
    """
    ...
```

## Testing

### Test Coverage

Aim for 80%+ test coverage. Tests should cover:

- Normal operation
- Edge cases
- Error conditions
- Different input types

### Writing Tests

```python
def test_feature_description(self):
    """Test that feature works as expected."""
    # Arrange
    input_data = "test"
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    self.assertEqual(result, expected_output)
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific test
pytest tests/test_basic.py::TestClass::test_method

# Verbose output
pytest -v
```

## Documentation

### Code Documentation

- Use clear, concise comments
- Explain "why" not "what"
- Keep docstrings up to date

### User Documentation

When adding features, update:

1. `SKILL.md` - Usage instructions
2. `README.md` - Project overview
3. `examples/` - Working examples
4. `CHANGELOG.md` - Release notes

## Questions?

- Open an issue for questions
- Join discussions in GitHub Discussions
- Contact maintainers

## Recognition

Contributors will be:

- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing to Skill Creator Enhanced!
