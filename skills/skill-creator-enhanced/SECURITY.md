# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do Not Open a Public Issue

Security vulnerabilities should not be reported through public GitHub issues.

### 2. Contact Us Directly

Email: security@godlike-kimi-skills.org

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### 3. Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 5 business days
- **Fix Timeline**: Based on severity
  - Critical: 7 days
  - High: 14 days
  - Medium: 30 days
  - Low: 90 days

### 4. Disclosure Policy

We follow responsible disclosure:

1. Vulnerability reported
2. We acknowledge and assess
3. We develop and test fix
4. Fix released
5. Public disclosure after 30 days or with reporter's consent

## Security Best Practices

When using Skill Creator Enhanced:

### Do's

- ✅ Review generated code before deployment
- ✅ Use in isolated environments for testing
- ✅ Keep dependencies updated
- ✅ Validate user inputs
- ✅ Use strong authentication

### Don'ts

- ❌ Hardcode secrets in generated skills
- ❌ Run untrusted skills without review
- ❌ Use in production without testing
- ❌ Ignore security warnings

## Security Features

Skill Creator Enhanced includes:

- No hardcoded secrets in templates
- Input validation examples
- Error handling patterns
- Security best practices documentation

## Dependency Security

We monitor dependencies for vulnerabilities:

- Automated dependency updates
- Security scanning in CI/CD
- Prompt patches for known vulnerabilities

## Security Checklist for Generated Skills

When creating skills, ensure:

- [ ] No hardcoded API keys or passwords
- [ ] Input validation implemented
- [ ] Error messages don't leak sensitive info
- [ ] File operations are sandboxed
- [ ] Network requests use HTTPS
- [ ] User permissions are checked
- [ ] Logs don't contain sensitive data

## Contact

For security concerns:

- Email: security@godlike-kimi-skills.org
- PGP Key: [Available upon request]

For general questions, use GitHub Issues or Discussions.

## Acknowledgments

We thank security researchers who have responsibly disclosed vulnerabilities:

*None yet - be the first!*
