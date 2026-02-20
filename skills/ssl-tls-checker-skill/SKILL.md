# SSL/TLS Checker Skill

SSL/TLS certificate and configuration analyzer for security assessment. Use when auditing code security, scanning for vulnerabilities, or when user mentions 'security', 'vulnerability', 'CVE'.

## Features

- **Certificate validation**: Expiry, chain, and revocation checks
- **Configuration analysis**: Cipher suites, protocols, HSTS
- **Security grading**: A-F rating based on configuration
- **Vulnerability detection**: Heartbleed, POODLE, BEAST, etc.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Basic scan
python scripts/main.py --host example.com

# With port specification
python scripts/main.py --host example.com --port 443

# Full analysis with vulnerabilities
python scripts/main.py --host example.com --full-analysis

# Batch scan from file
python scripts/main.py --file hosts.txt

# Generate report
python scripts/main.py --host example.com --output ssl_report.json
```

### As Module

```python
from scripts.main import SSLChecker

checker = SSLChecker()
results = checker.check_host("example.com", port=443)
checker.generate_report(results, "report.json")
```

## Security Grading

| Grade | Criteria |
|-------|----------|
| A+ | TLS 1.3 only, perfect forward secrecy, HSTS |
| A | TLS 1.2+, strong ciphers, valid certificate |
| B | TLS 1.2, acceptable ciphers, minor issues |
| C | TLS 1.0/1.1 support or weak ciphers |
| D | SSLv3 support or serious vulnerabilities |
| F | Certificate errors or critical vulnerabilities |

## Checked Vulnerabilities

- **Heartbleed** (CVE-2014-0160)
- **POODLE** (CVE-2014-3566)
- **BEAST** (CVE-2011-3389)
- **CRIME** (CVE-2012-4929)
- **BREACH** (CVE-2013-3587)
- **Logjam** (CVE-2015-4000)
- **SWEET32** (CVE-2016-2183)

## Output Format

```json
{
  "scan_info": {
    "host": "example.com",
    "port": 443,
    "timestamp": "2024-01-20T10:00:00Z",
    "ip_address": "93.184.216.34"
  },
  "certificate": {
    "subject": "CN=example.com",
    "issuer": "CN=DigiCert TLS RSA SHA256 2020 CA1",
    "valid_from": "2023-01-15T00:00:00Z",
    "valid_until": "2024-01-15T23:59:59Z",
    "days_until_expiry": 360,
    "serial_number": "1234567890abcdef",
    "signature_algorithm": "sha256WithRSAEncryption",
    "key_size": 2048,
    "san": ["example.com", "www.example.com"]
  },
  "configuration": {
    "protocols": ["TLSv1.2", "TLSv1.3"],
    "cipher_suites": ["TLS_AES_256_GCM_SHA384", "TLS_CHACHA20_POLY1305_SHA256"],
    "supports_hsts": true,
    "hsts_max_age": 31536000
  },
  "vulnerabilities": [],
  "grade": "A+"
}
```

## Skill Metadata

- **Name**: ssl-tls-checker-skill
- **Category**: security
- **Author**: Godlike Kimi Skills
- **Version**: 1.0.0
- **License**: MIT
