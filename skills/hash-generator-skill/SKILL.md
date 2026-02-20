# Hash Generator Skill

**Category:** Utility  
**Version:** 1.0.0  
**Author:** godlike-kimi-skills

---

## Use When

- Generating checksums for file integrity verification
- Creating secure hashes for password storage (use proper key derivation in production)
- Generating HMAC for message authentication
- Verifying downloaded files against published checksums
- Comparing files for duplicates via hash comparison
- Creating unique identifiers from data
- Batch hashing multiple files
- Cryptographic verification of data integrity

---

## Out of Scope

- Password cracking or brute force attacks
- Encryption/decryption of data
- Digital signature generation/verification
- Certificate management
- Secure random number generation
- Key exchange protocols
- Blockchain hashing
- GPU-accelerated hashing
- Hash rainbow table generation

---

## Quick Reference

### Core Methods

```python
from skills.hash_generator_skill.main import HashGeneratorSkill

skill = HashGeneratorSkill()

# String hashing
md5 = skill.hash_string("Hello World", "md5")
sha256 = skill.hash_string("Hello World", "sha256")
sha512 = skill.hash_string("Hello World", "sha512")

# File hashing (memory-efficient for large files)
file_hash = skill.hash_file("document.pdf", "sha256")

# HMAC generation
hmac = skill.hmac_string("message", "secret_key", "sha256")
hmac_file = skill.hmac_file("document.pdf", "secret_key", "sha256")

# Hash verification
is_valid = skill.verify_string("Hello World", expected_hash, "sha256")
is_valid = skill.verify_file("document.pdf", expected_hash, "sha256")

# Batch operations
hashes = skill.batch_hash_files(["file1.txt", "file2.txt"], "sha256")
dir_hashes = skill.hash_directory("./documents/", "sha256")

# Checksum file generation
skill.generate_checksum_file(["file1.txt", "file2.txt"], "checksums.sha256")
results = skill.verify_checksum_file("checksums.sha256")
```

---

## Supported Algorithms

### Secure Algorithms (Recommended)

| Algorithm | Digest Size | Security Level |
|-----------|-------------|----------------|
| `sha256` | 64 chars | High |
| `sha384` | 96 chars | High |
| `sha512` | 128 chars | High |
| `sha3_256` | 64 chars | Very High |
| `sha3_512` | 128 chars | Very High |
| `blake2b` | 128 chars | Very High |

### Legacy Algorithms (Compatibility Only)

| Algorithm | Digest Size | Security Level |
|-----------|-------------|----------------|
| `md5` | 32 chars | Broken |
| `sha1` | 40 chars | Weakened |

### Other Algorithms

- `sha224`, `sha512` - SHA-2 variants
- `sha3_224`, `sha3_384` - SHA-3 variants
- `blake2s` - BLAKE2s variant

---

## CLI Usage

```bash
# Hash string
python main.py string "Hello World" sha256

# Hash file
python main.py file document.pdf sha256

# HMAC
python main.py hmac "message" "secret_key" sha256

# Verify file
python main.py verify document.pdf <expected_hash> sha256

# Compare hashes
python main.py compare <hash1> <hash2>

# Batch hash files
python main.py batch file1.txt file2.txt file3.txt sha256

# Generate checksum file
python main.py checksum checksums.sha256 file1.txt file2.txt

# Algorithm info
python main.py info sha256

# List algorithms
python main.py list
```

---

## Method Reference

### String/Bytes Hashing

- `hash_string(data, algorithm='sha256')` - Hash a string or bytes
- `hash_bytes(data, algorithm='sha256')` - Hash and return raw bytes

### File Hashing

- `hash_file(file_path, algorithm='sha256')` - Hash a file (streaming)

### HMAC Operations

- `hmac_string(data, key, algorithm='sha256')` - Generate HMAC for string
- `hmac_file(file_path, key, algorithm='sha256')` - Generate HMAC for file

### Verification

- `compare_hashes(hash1, hash2)` - Securely compare two hashes
- `verify_string(data, expected_hash, algorithm='sha256')` - Verify string
- `verify_file(file_path, expected_hash, algorithm='sha256')` - Verify file

### Batch Operations

- `batch_hash_files(file_paths, algorithm='sha256')` - Hash multiple files
- `hash_directory(directory, algorithm='sha256', pattern='*')` - Hash directory contents

### Checksum Files

- `generate_checksum_file(file_paths, output_path, algorithm='sha256')` - Create checksum file
- `verify_checksum_file(checksum_path)` - Verify against checksum file

### Information

- `get_algorithm_info(algorithm)` - Get algorithm details
- `list_algorithms()` - List all supported algorithms

---

## Dependencies

```
# No external dependencies required
# Uses Python standard library: hashlib, hmac
```

---

## Security Notes

⚠️ **Important:**

1. **MD5 and SHA-1 are insecure** - Use only for compatibility with legacy systems
2. **Use constant-time comparison** - Always use `compare_hashes()` instead of `==`
3. **For password hashing** - Use proper key derivation functions (bcrypt, Argon2, PBKDF2)
4. **Protect secret keys** - HMAC keys should be kept secure

---

## Examples

### File Integrity Verification

```python
skill = HashGeneratorSkill()

# Generate hash for original file
original_hash = skill.hash_file("important.doc", "sha256")
print(f"Original hash: {original_hash}")

# Later, verify file integrity
current_hash = skill.hash_file("important.doc", "sha256")
if skill.compare_hashes(original_hash, current_hash):
    print("File is intact ✓")
else:
    print("File has been modified!")
```

### API Request Signing

```python
skill = HashGeneratorSkill()

# Sign API request
api_key = "your_secret_api_key"
payload = "user_id=123&action=transfer&amount=100"

signature = skill.hmac_string(payload, api_key, "sha256")

# Verify on server
is_valid = skill.verify_string(payload, signature, "sha256")
```

### Duplicate File Detection

```python
skill = HashGeneratorSkill()

# Hash all files in directory
hashes = skill.hash_directory("./downloads/", "sha256")

# Find duplicates
seen = {}
duplicates = []

for filepath, filehash in hashes.items():
    if filehash in seen:
        duplicates.append((filepath, seen[filehash]))
    else:
        seen[filehash] = filepath

print(f"Found {len(duplicates)} duplicate file pairs")
```

### Checksum File Workflow

```python
skill = HashGeneratorSkill()

# Create checksums for distribution
files_to_distribute = ["app.exe", "data.db", "config.json"]
skill.generate_checksum_file(files_to_distribute, "SHA256SUMS")

# Users verify
time.sleep(1)  # Simulate download
results = skill.verify_checksum_file("SHA256SUMS")

for filepath, valid in results.items():
    status = "✓" if valid else "✗"
    print(f"{status} {filepath}")
```
