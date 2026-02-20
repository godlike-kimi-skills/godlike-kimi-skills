# JSON/YAML Skill Examples

## Basic Usage

### 1. Format Conversion

#### JSON to YAML
```python
from main import JsonYamlSkill

skill = JsonYamlSkill()

json_data = '''
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "credentials": {
      "username": "admin",
      "password": "secret"
    }
  },
  "features": ["auth", "api", "logging"]
}
'''

yaml_output, error = skill.json_to_yaml(json_data)
print(yaml_output)
```

**Output:**
```yaml
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
    password: secret
features:
  - auth
  - api
  - logging
```

#### YAML to JSON
```python
yaml_data = '''
server:
  host: 0.0.0.0
  port: 8080
routes:
  - path: /api/v1
    method: GET
  - path: /api/v2
    method: POST
'''

json_output, error = skill.yaml_to_json(yaml_data, indent=2)
print(json_output)
```

### 2. Data Validation

```python
# Validate JSON
is_valid, error = skill.validate_json('{"key": "value"}')
if is_valid:
    print("✓ Valid JSON")
else:
    print(f"✗ Invalid: {error}")

# Validate YAML
is_valid, error = skill.validate_yaml('''
name: test
items:
  - one
  - two
''')
```

### 3. JSONPath Queries

```python
sample_data = {
    "store": {
        "book": [
            {"category": "fiction", "price": 8.99, "title": "Book A"},
            {"category": "fiction", "price": 12.99, "title": "Book B"},
            {"category": "reference", "price": 4.99, "title": "Book C"}
        ],
        "bicycle": {"color": "red", "price": 19.95}
    }
}

# Get all book titles
titles, error = skill.query_json(sample_data, '$.store.book[*].title')
print(titles)  # ['Book A', 'Book B', 'Book C']

# Get books with price > 10
expensive, error = skill.query_json(sample_data, '$.store.book[?(@.price > 10)]')
print(expensive)

# Get all prices recursively
all_prices, error = skill.query_json(sample_data, '$..price')
print(all_prices)  # [8.99, 12.99, 4.99, 19.95]
```

### 4. Beautification

```python
# Minified JSON
ugly_json = '{"users":[{"name":"Alice","age":30},{"name":"Bob","age":25}]}'

# Beautify
pretty, _ = skill.beautify_json(ugly_json, indent=2)
print(pretty)
```

**Output:**
```json
{
  "users": [
    {
      "name": "Alice",
      "age": 30
    },
    {
      "name": "Bob",
      "age": 25
    }
  ]
}
```

### 5. File Merging

```python
# Merge multiple configuration files
files = ['config/base.json', 'config/dev.json', 'config/local.json']
merged, error = skill.merge_json(files, merge_strategy='deep')

# Save merged result
with open('config/merged.json', 'w') as f:
    json.dump(merged, f, indent=2)
```

### 6. File Comparison

```python
diff, error = skill.diff_files('config/old.json', 'config/new.json')
print(diff)
```

**Output:**
```diff
--- config/old.json
+++ config/new.json
@@ -3,5 +3,6 @@
   "database": {
     "host": "localhost",
-    "port": 5432
+    "port": 3306,
+    "ssl": true
   }
 }
```

## CLI Examples

### Convert Files
```bash
# JSON to YAML
python main.py convert config.json config.yaml

# YAML to JSON
python main.py convert config.yaml config.json
```

### Validate Files
```bash
# Auto-detect format
python main.py validate data.json

# Explicit format
python main.py validate data.yaml --format yaml
```

### Query Data
```bash
# Extract specific fields
python main.py query users.json '$.users[*].email'

# Complex query
python main.py query store.json '$.store.book[?(@.price < 10)].title'
```

### Beautify Files
```bash
# Pretty print with custom indent
python main.py beautify minified.json --indent 4 -o pretty.json
```

### Minify Files
```bash
# Remove whitespace
python main.py minify pretty.json -o minified.json
```

### Merge Files
```bash
# Deep merge (default)
python main.py merge base.json dev.json local.json -o merged.json

# Shallow merge
python main.py merge file1.json file2.json -o merged.json --strategy shallow
```

### Compare Files
```bash
# Show differences
python main.py diff version1.json version2.json
```

## Advanced Examples

### Configuration Management Pipeline

```python
#!/usr/bin/env python3
"""Configuration management workflow"""

from main import JsonYamlSkill
import sys

skill = JsonYamlSkill()

def process_config(input_file, output_file, overrides=None):
    """Process configuration with validation and merging"""
    
    # 1. Validate input
    is_valid, error = skill.validate_json(input_file)
    if not is_valid:
        print(f"Validation failed: {error}")
        sys.exit(1)
    
    # 2. Load base config
    with open(input_file) as f:
        content = f.read()
    
    # 3. Apply overrides if provided
    if overrides:
        base, _ = skill.parse_json(content)
        override_data, _ = skill.parse_json(overrides)
        merged = skill._deep_merge(base, override_data)
        content = json.dumps(merged)
    
    # 4. Convert format if needed
    if output_file.endswith('.yaml') or output_file.endswith('.yml'):
        result, error = skill.json_to_yaml(content)
    else:
        result, error = skill.beautify_json(content)
    
    if error:
        print(f"Processing error: {error}")
        sys.exit(1)
    
    # 5. Write output
    with open(output_file, 'w') as f:
        f.write(result)
    
    print(f"Config processed: {input_file} -> {output_file}")

# Usage
process_config('config.json', 'config.yaml', 'overrides.json')
```

### Bulk File Processing

```python
from pathlib import Path
from main import JsonYamlSkill

skill = JsonYamlSkill()

# Convert all JSON files to YAML
for json_file in Path('configs/').glob('*.json'):
    yaml_file = json_file.with_suffix('.yaml')
    yaml_content, error = skill.json_to_yaml(json_file)
    if not error:
        yaml_file.write_text(yaml_content)
        print(f"Converted: {json_file} -> {yaml_file}")
```

### Data Migration Script

```python
"""Migrate data from old format to new format"""

skill = JsonYamlSkill()

# Read old format
old_data, error = skill.parse_yaml('legacy_data.yaml')

# Transform data
new_data = {
    'version': '2.0',
    'migrated_at': '2024-01-01',
    'data': {
        'users': old_data.get('user_list', []),
        'settings': {
            'theme': old_data.get('ui_theme', 'default'),
            'language': old_data.get('lang', 'en')
        }
    }
}

# Write new format
json_output, _ = skill.beautify_json(new_data, indent=2)
Path('migrated_data.json').write_text(json_output)
```
