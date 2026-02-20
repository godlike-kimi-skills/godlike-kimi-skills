# Hash Generator Skill - Usage Examples

## Example 1: File Integrity Verification

Verify downloaded files or backups:

```python
from skills.hash_generator_skill.main import HashGeneratorSkill
import os

skill = HashGeneratorSkill()

# Create hash database for important files
important_files = [
    "contract.pdf",
    "database_backup.sql",
    "source_code.zip",
]

hash_db = {}
for filepath in important_files:
    if os.path.exists(filepath):
        file_hash = skill.hash_file(filepath, "sha256")
        hash_db[filepath] = file_hash
        print(f"{filepath}: {file_hash}")

# Save hash database
import json
with open("file_hashes.json", "w") as f:
    json.dump(hash_db, f, indent=2)

# Later, verify files
print("\nVerifying files...")
for filepath, original_hash in hash_db.items():
    if os.path.exists(filepath):
        is_valid = skill.verify_file(filepath, original_hash, "sha256")
        status = "✓ VALID" if is_valid else "✗ MODIFIED"
        print(f"{filepath}: {status}")
```

## Example 2: API Request Signing

Implement HMAC authentication for API calls:

```python
skill = HashGeneratorSkill()
import time

class APIClient:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.skill = HashGeneratorSkill()
    
    def sign_request(self, method, endpoint, params=None):
        """Sign API request with HMAC"""
        timestamp = str(int(time.time()))
        
        # Build payload string
        payload_parts = [method.upper(), endpoint, timestamp]
        if params:
            param_str = '&'.join(f"{k}={v}" for k, v in sorted(params.items()))
            payload_parts.append(param_str)
        
        payload = '|'.join(payload_parts)
        
        # Generate HMAC
        signature = self.skill.hmac_string(payload, self.api_secret, "sha256")
        
        return {
            'X-API-Key': self.api_key,
            'X-Timestamp': timestamp,
            'X-Signature': signature,
        }
    
    def verify_response(self, response_data, signature):
        """Verify API response"""
        expected = self.skill.hmac_string(response_data, self.api_secret, "sha256")
        return self.skill.compare_hashes(signature, expected)

# Usage
client = APIClient("my_api_key", "my_secret_key")
headers = client.sign_request("POST", "/api/transfer", {"amount": "100"})
print(f"Request headers: {headers}")
```

## Example 3: Duplicate File Finder

Find and manage duplicate files:

```python
skill = HashGeneratorSkill()
import os
from collections import defaultdict

def find_duplicates(directory, algorithm='sha256'):
    """Find duplicate files in directory"""
    
    # Build hash index
    hashes = skill.hash_directory(directory, algorithm)
    
    # Group by hash
    by_hash = defaultdict(list)
    for filepath, file_hash in hashes.items():
        if not file_hash.startswith("Error"):
            by_hash[file_hash].append(filepath)
    
    # Find duplicates
    duplicates = {h: files for h, files in by_hash.items() if len(files) > 1}
    
    return duplicates

# Find duplicates
duplicates = find_duplicates("./downloads/")

print(f"Found {len(duplicates)} sets of duplicates:")
for file_hash, files in duplicates.items():
    print(f"\nHash: {file_hash[:16]}...")
    for f in files:
        size = os.path.getsize(f)
        print(f"  - {f} ({size} bytes)")

# Optional: Remove duplicates (keep first)
for file_hash, files in duplicates.items():
    for dup_file in files[1:]:
        print(f"Would remove: {dup_file}")
        # os.remove(dup_file)  # Uncomment to actually delete
```

## Example 4: Secure Checksum Distribution

Create and distribute checksum files:

```python
skill = HashGeneratorSkill()

# Files to distribute
release_files = [
    "app-v1.0.exe",
    "app-v1.0.dmg",
    "app-v1.0.AppImage",
    "README.md",
    "LICENSE",
]

# Generate checksums
checksum_file = "SHA256SUMS"
skill.generate_checksum_file(release_files, checksum_file, "sha256")

print(f"Created {checksum_file}")
with open(checksum_file) as f:
    print(f.read())

# User verification
print("\n--- User Verification ---")
results = skill.verify_checksum_file(checksum_file)

all_valid = True
for filepath, valid in results.items():
    status = "✓" if valid else "✗ INVALID"
    if not valid:
        all_valid = False
    print(f"{status} {filepath}")

if all_valid:
    print("\nAll files verified successfully!")
else:
    print("\nWARNING: Some files failed verification!")
```

## Example 5: Password Hashing (Educational)

Note: Use proper KDF in production (bcrypt, Argon2):

```python
skill = HashGeneratorSkill()
import secrets

class SimplePasswordStore:
    """Educational example - use bcrypt/Argon2 in production!"""
    
    def __init__(self):
        self.skill = HashGeneratorSkill()
    
    def hash_password(self, password):
        """Hash password with salt"""
        # Generate random salt
        salt = secrets.token_hex(16)
        
        # Hash password + salt
        salted = password + salt
        password_hash = self.skill.hash_string(salted, "sha256")
        
        return f"{salt}${password_hash}"
    
    def verify_password(self, password, stored_hash):
        """Verify password against stored hash"""
        salt, original_hash = stored_hash.split('$')
        
        salted = password + salt
        computed_hash = self.skill.hash_string(salted, "sha256")
        
        return self.skill.compare_hashes(computed_hash, original_hash)

# Usage
store = SimplePasswordStore()

# Store password
user_password = "my_secure_password_123"
stored = store.hash_password(user_password)
print(f"Stored: {stored}")

# Verify
is_valid = store.verify_password("my_secure_password_123", stored)
print(f"Password valid: {is_valid}")

is_invalid = store.verify_password("wrong_password", stored)
print(f"Wrong password rejected: {not is_invalid}")
```

## Example 6: Build Verification

Verify build artifacts in CI/CD:

```python
skill = HashGeneratorSkill()
import sys

def verify_build(build_dir, expected_hashes_file):
    """Verify build artifacts match expected hashes"""
    
    # Load expected hashes
    import json
    with open(expected_hashes_file) as f:
        expected = json.load(f)
    
    # Verify each file
    all_passed = True
    for filepath, expected_hash in expected.items():
        full_path = os.path.join(build_dir, filepath)
        
        if not os.path.exists(full_path):
            print(f"✗ MISSING: {filepath}")
            all_passed = False
            continue
        
        if skill.verify_file(full_path, expected_hash, "sha256"):
            print(f"✓ {filepath}")
        else:
            print(f"✗ HASH MISMATCH: {filepath}")
            all_passed = False
    
    return all_passed

# CI/CD usage
if __name__ == "__main__":
    success = verify_build("./dist/", "expected_hashes.json")
    sys.exit(0 if success else 1)
```

## Example 7: Secure Data Comparison

Compare data without exposing it:

```python
skill = HashGeneratorSkill()

def compare_datasets(dataset1, dataset2):
    """Compare two datasets using hashes"""
    
    # Hash both datasets
    hash1 = skill.hash_string(dataset1, "sha256")
    hash2 = skill.hash_string(dataset2, "sha256")
    
    # Compare
    match = skill.compare_hashes(hash1, hash2)
    
    return {
        'match': match,
        'hash1': hash1[:16] + "...",
        'hash2': hash2[:16] + "...",
    }

# Compare configurations
prod_config = open("production.conf").read()
staging_config = open("staging.conf").read()

result = compare_datasets(prod_config, staging_config)

if result['match']:
    print("Configurations are identical")
else:
    print("Configurations differ:")
    print(f"  Production: {result['hash1']}")
    print(f"  Staging:    {result['hash2']}")
```
