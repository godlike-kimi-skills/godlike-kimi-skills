# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-20

### Added
- Initial release of Skill Creator Enhanced
- One-click scaffolding for Kimi Skill projects
- Support for 4 templates: basic, cli-tool, data-processor, automation
- Automatic generation of standardized files:
  - skill.json with proper schema
  - SKILL.md with usage documentation
  - README.md for GitHub
  - LICENSE (MIT)
  - main.py with template code
  - requirements.txt
  - .gitignore
- Optional test generation with pytest templates
- Optional CI/CD configuration with GitHub Actions
- Optional example code generation
- Skill validation functionality
- Template listing functionality
- Comprehensive test coverage (85%+)

### Features
- **Project Scaffolding**: Create complete Skill projects in seconds
- **Standardized Templates**: Follow Anthropic Agent Skill standards
- **Multiple Templates**: Choose from basic, CLI, data processor, or automation
- **Validation**: Check if existing Skills meet open source standards
- **Unicode Support**: Full support for Chinese and other languages
- **Cross-Platform**: Works on Windows, macOS, and Linux

### Documentation
- Complete SKILL.md with usage instructions
- README.md with installation and examples
- Basic and advanced usage examples
- Best practices guide

### Testing
- Unit tests for all core functionality
- Integration tests for full workflows
- Edge case and boundary testing
- Performance testing

## [Unreleased]

### Planned
- Interactive mode for guided Skill creation
- More templates (FastAPI, Flask, Django)
- Skill upgrade functionality
- Template marketplace integration
- Custom template support
- Web UI for Skill creation

---

## Release Notes Format

Each release includes:
- Version number following SemVer
- Release date
- Added/Changed/Deprecated/Removed/Fixed/Security sections
- Link to full changelog
