# UUID Generator Skill Examples

## Basic UUID Generation

### Generate UUID v4 (Random)
```python
from main import UUIDGeneratorSkill

skill = UUIDGeneratorSkill()

# Single UUID v4
uuid_v4 = skill.uuid_v4()
print(uuid_v4)  # e.g., "550e8400-e29b-41d4-a716-446655440000"

# Multiple UUIDs
for _ in range(3):
    print(skill.uuid_v4())
```

### Generate UUID v1 (Timestamp + MAC)
```python
# UUID v1 includes timestamp and MAC address
uuid_v1 = skill.uuid_v1()
print(uuid_v1)

# Parse to see timestamp
info = skill.parse(uuid_v1)
print(f"Generated at: {info.time}")
```

### Generate UUID v7 (Time-sortable)
```python
# UUID v7 is time-ordered and sortable
uuid_v7_first = skill.uuid_v7()
time.sleep(0.001)  # Small delay
uuid_v7_second = skill.uuid_v7()

# UUIDs are naturally sorted by time
assert uuid_v7_first < uuid_v7_second
print(f"First:  {uuid_v7_first}")
print(f"Second: {uuid_v7_second}")
```

## Short IDs

### Generate URL-friendly Short IDs
```python
# Short ID for URLs
short_id = skill.short_id(8)
print(short_id)  # e.g., "aB3xK9pQ"

# Different lengths
for length in [6, 8, 10, 12]:
    print(f"Length {length}: {skill.short_id(length)}")
```

### Use Case: URL Shortener
```python
def create_short_url(long_url):
    """Create a short URL"""
    short_code = skill.short_id(7)
    return f"https://short.link/{short_code}"

# Example
urls = [
    "https://example.com/very/long/path/to/resource",
    "https://another-site.com/some/deeply/nested/page"
]

for url in urls:
    short = create_short_url(url)
    print(f"{url[:40]}... -> {short}")
```

## Random Strings

### Generate API Keys
```python
# Secure API key (alphanumeric only)
api_key = skill.alphanumeric(32)
print(f"API Key: {api_key}")

# API key with special characters
secure_key = skill.random_string(
    length=48,
    use_uppercase=True,
    use_lowercase=True,
    use_digits=True,
    use_special=True
)
print(f"Secure Key: {secure_key}")
```

### Generate Passwords
```python
def generate_password(length=16, include_special=True):
    """Generate a secure password"""
    return skill.random_string(
        length=length,
        use_uppercase=True,
        use_lowercase=True,
        use_digits=True,
        use_special=include_special
    )

# Generate different types of passwords
print(f"Standard:   {generate_password(12)}")
print(f"Strong:     {generate_password(20, True)}")
print(f"Simple:     {generate_password(16, False)}")
```

### Generate Hex Strings
```python
# Hex string for colors, keys, etc.
color_code = skill.hex_string(6)
print(f"Color: #{color_code}")

# Longer hex for cryptographic use
hex_key = skill.hex_string(64)
print(f"Hex Key: {hex_key}")
```

## NanoID

### Generate NanoIDs
```python
# Default NanoID (21 chars, URL-safe)
nanoid = skill.nanoid()
print(nanoid)  # e.g., "V1StGXR8_Z5jdHi6B-myT"

# Custom size
short_nanoid = skill.nanoid(10)
long_nanoid = skill.nanoid(32)

print(f"Short:  {short_nanoid}")
print(f"Long:   {long_nanoid}")
```

### Use Case: Session Tokens
```python
def create_session():
    """Create a new session with NanoID"""
    return {
        'session_id': skill.nanoid(32),
        'csrf_token': skill.nanoid(21),
        'created_at': datetime.now()
    }

session = create_session()
print(f"Session ID: {session['session_id']}")
print(f"CSRF Token: {session['csrf_token']}")
```

## CUID

### Generate CUIDs
```python
# CUIDs are collision-resistant
cuid1 = skill.cuid()
cuid2 = skill.cuid()

print(f"CUID 1: {cuid1}")
print(f"CUID 2: {cuid2}")

# CUIDs are naturally sortable
assert cuid1 < cuid2 or cuid1 > cuid2  # One should be less than the other
```

### Use Case: Database IDs
```python
def create_record(data):
    """Create a database record with CUID"""
    return {
        'id': skill.cuid(),
        'data': data,
        'created_at': datetime.now()
    }

records = [create_record(f"Item {i}") for i in range(5)]
for record in records:
    print(f"ID: {record['id']}, Data: {record['data']}")
```

## UUID Validation and Parsing

### Validate UUIDs
```python
# Valid UUIDs
print(skill.validate('550e8400-e29b-41d4-a716-446655440000'))  # True
print(skill.validate('550E8400-E29B-41D4-A716-446655440000'))  # True (uppercase)

# Invalid UUIDs
print(skill.validate('not-a-uuid'))      # False
print(skill.validate('550e8400'))        # False (too short)
print(skill.validate(''))                # False
```

### Parse UUID Information
```python
# Parse UUID v4
uuid_v4 = skill.uuid_v4()
info = skill.parse(uuid_v4)

print(f"UUID: {uuid_v4}")
print(f"Version: {info.version}")
print(f"Variant: {info.variant}")
print(f"Hex: {info.hex}")
print(f"Integer: {info.int}")

# Parse UUID v1 (with timestamp)
uuid_v1 = skill.uuid_v1()
info_v1 = skill.parse(uuid_v1)
print(f"\nUUID v1 Timestamp: {info_v1.time}")

# Parse UUID v7 (with timestamp)
uuid_v7 = skill.uuid_v7()
info_v7 = skill.parse(uuid_v7)
print(f"UUID v7 Timestamp: {info_v7.time}")
```

## UUID Slugs

### Convert UUID to Short Slug
```python
# Convert UUID to URL-friendly slug
uuid = skill.uuid_v4()
slug = skill.slug(uuid)

print(f"UUID:  {uuid}")   # 36 chars
print(f"Slug:  {slug}")   # ~22 chars

# Generate slug from new UUID
new_slug = skill.slug()
print(f"New Slug: {new_slug}")
```

## Batch Generation

### Generate Multiple IDs
```python
# Batch UUID v4
uuids = skill.batch_uuid_v4(count=5)
print("UUIDs:")
for u in uuids:
    print(f"  {u}")

# Batch UUID v7 (time-ordered)
sorted_uuids = skill.batch_uuid_v7(count=5)
print("\nUUID v7s (sorted):")
for u in sorted_uuids:
    print(f"  {u}")
```

### Generate IDs for Bulk Operations
```python
def generate_bulk_ids(count, id_type='uuid'):
    """Generate IDs for bulk database operations"""
    if id_type == 'uuid':
        return skill.batch_uuid_v4(count)
    elif id_type == 'short':
        return [skill.short_id(8) for _ in range(count)]
    elif id_type == 'nanoid':
        return [skill.nanoid() for _ in range(count)]
    elif id_type == 'cuid':
        return [skill.cuid() for _ in range(count)]
    else:
        raise ValueError(f"Unknown ID type: {id_type}")

# Generate for different use cases
product_ids = generate_bulk_ids(10, 'short')
user_ids = generate_bulk_ids(10, 'uuid')
order_ids = generate_bulk_ids(10, 'cuid')

print("Product IDs:", product_ids[:3], "...")
print("User IDs:", user_ids[:3], "...")
print("Order IDs:", order_ids[:3], "...")
```

## Practical Workflows

### API Key Management System
```python
#!/usr/bin/env python3
"""Simple API key management system"""

from main import UUIDGeneratorSkill
from datetime import datetime, timedelta

skill = UUIDGeneratorSkill()

class APIKeyManager:
    def __init__(self):
        self.keys = {}
    
    def generate_key(self, name, permissions=None):
        """Generate a new API key"""
        key_id = skill.short_id(8)
        secret = skill.random_string(48, use_special=False)
        
        self.keys[key_id] = {
            'id': key_id,
            'secret': secret,
            'name': name,
            'permissions': permissions or [],
            'created_at': datetime.now(),
            'last_used': None,
            'active': True
        }
        
        return {
            'id': key_id,
            'secret': secret,  # Only shown once
            'name': name
        }
    
    def revoke_key(self, key_id):
        """Revoke an API key"""
        if key_id in self.keys:
            self.keys[key_id]['active'] = False
            return True
        return False
    
    def list_keys(self):
        """List all keys (without secrets)"""
        return [
            {
                'id': k['id'],
                'name': k['name'],
                'created_at': k['created_at'],
                'active': k['active']
            }
            for k in self.keys.values()
        ]

# Example usage
manager = APIKeyManager()

# Generate keys
prod_key = manager.generate_key('Production App', ['read', 'write'])
print(f"Production Key ID: {prod_key['id']}")
print(f"Production Secret: {prod_key['secret'][:10]}...")

dev_key = manager.generate_key('Development', ['read'])
print(f"\nDevelopment Key ID: {dev_key['id']}")

# List keys
print("\nAll Keys:")
for key in manager.list_keys():
    print(f"  {key['id']}: {key['name']} ({'active' if key['active'] else 'revoked'})")
```

### Order ID Generator
```python
#!/usr/bin/env python3
"""Order ID generator with different formats"""

from main import UUIDGeneratorSkill

skill = UUIDGeneratorSkill()

class OrderIDGenerator:
    """Generate order IDs in different formats"""
    
    @staticmethod
    def short_format():
        """Short 8-character ID"""
        return skill.short_id(8).upper()
    
    @staticmethod
    def date_format():
        """Date-based ID: ORD-YYYYMMDD-XXXX"""
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m%d')
        random_suffix = skill.short_id(4).upper()
        return f"ORD-{date_str}-{random_suffix}"
    
    @staticmethod
    def uuid_format():
        """Full UUID format"""
        return skill.uuid_v7()
    
    @staticmethod
    def cuid_format():
        """CUID format"""
        return skill.cuid()

# Generate order IDs
generator = OrderIDGenerator()

print("Order ID Formats:")
print(f"Short:  {generator.short_format()}")
print(f"Date:   {generator.date_format()}")
print(f"UUID:   {generator.uuid_format()}")
print(f"CUID:   {generator.cuid_format()}")
```

## CLI Examples

### Generate UUIDs
```bash
# Single UUID v4
python main.py uuid

# UUID v1 (timestamp-based)
python main.py uuid --version 1

# UUID v7 (time-sortable)
python main.py uuid --version 7

# Multiple UUIDs
python main.py uuid --count 5

# Uppercase
python main.py uuid --uppercase
```

### Generate Short IDs
```bash
# Short ID (8 chars)
python main.py short

# Custom length
python main.py short --length 10

# Multiple IDs
python main.py short --count 5
```

### Generate Random Strings
```bash
# Default (alphanumeric)
python main.py random

# Custom length
python main.py random --length 64

# Only lowercase
python main.py random --no-upper --no-digits

# With special characters
python main.py random --special
```

### Generate NanoIDs
```bash
# Default (21 chars)
python main.py nanoid

# Custom size
python main.py nanoid --size 16
```

### Generate CUIDs
```bash
# Single CUID
python main.py cuid

# Multiple CUIDs
python main.py cuid --count 3
```

### Validate UUID
```bash
# Valid UUID
python main.py validate 550e8400-e29b-41d4-a716-446655440000

# Invalid UUID
python main.py validate invalid-uuid
```

### Parse UUID
```bash
# Parse and show info
python main.py parse 550e8400-e29b-41d4-a716-446655440000
```

### Batch Generation
```bash
# Generate 100 UUIDs to file
python main.py batch --type uuid --count 100 --output uuids.txt

# Generate short IDs
python main.py batch --type short --count 50 --output ids.txt
```

### Create Slug
```bash
# Slug from existing UUID
python main.py slug --uuid 550e8400-e29b-41d4-a716-446655440000

# Slug from new UUID
python main.py slug
```
