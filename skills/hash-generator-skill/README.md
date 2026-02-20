# Hash Generator Skill

A cryptographic hash generation utility for Kimi CLI supporting MD5, SHA family, HMAC, and file hashing.

## Features

- 🔐 **Multiple Algorithms**: MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512, SHA3
- 🔑 **HMAC Support**: Hash-based message authentication codes
- 📁 **File Hashing**: Calculate hashes for files of any size
- 🆚 **Hash Comparison**: Compare hashes for integrity verification
- ⚡ **Batch Processing**: Hash multiple files efficiently

## Installation

```bash
# Copy skill to Kimi skills directory
cp -r hash-generator-skill ~/.kimi/skills/

# Install dependencies
pip install -r ~/.kimi/skills/hash-generator-skill/requirements.txt
```

## Quick Start

```python
from skills.hash_generator_skill.main import HashGeneratorSkill

skill = HashGeneratorSkill()

# Generate MD5 hash
md5 = skill.hash_string("Hello World", "md5")
print(f"MD5: {md5}")

# Generate SHA-256 hash
sha256 = skill.hash_string("Hello World", "sha256")
print(f"SHA-256: {sha256}")

# File hash
file_hash = skill.hash_file("document.pdf", "sha256")
print(f"File SHA-256: {file_hash}")

# HMAC
hmac_hash = skill.hmac_string("message", "secret_key", "sha256")
print(f"HMAC: {hmac_hash}")
```

## Documentation

- [SKILL.md](./SKILL.md) - Detailed usage guide
- [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md) - Example use cases

## License

MIT License
