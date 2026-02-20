# Regex Skill Examples

## Basic Matching

### Find All Numbers
```python
from main import RegexSkill

skill = RegexSkill()

# Extract all numbers from text
text = "Prices: $50, $120, and $25"
matches = skill.match(r'\d+', text)

for m in matches:
    print(f"Found: {m.text} at position {m.start}-{m.end}")
# Output:
# Found: 50 at position 9-11
# Found: 120 at position 14-17
# Found: 25 at position 23-25
```

### Extract Email Addresses
```python
skill = RegexSkill()

text = "Contact us at support@example.com or sales@company.org"
matches = skill.match(r'[\w.-]+@[\w.-]+\.\w+', text)

emails = [m.text for m in matches]
print(emails)  # ['support@example.com', 'sales@company.org']
```

### Match with Groups
```python
# Extract domain from URLs
text = "Visit https://example.com or http://test.org"
matches = skill.match(r'https?://([^/]+)', text)

for m in matches:
    print(f"Full: {m.text}")
    print(f"Domain: {m.groups[0]}")
# Output:
# Full: https://example.com
# Domain: example.com
```

## Validation

### Email Validation
```python
skill = RegexSkill()

emails = [
    "user@example.com",
    "invalid.email",
    "test@domain.org"
]

for email in emails:
    is_valid = skill.validate(r'^[\w.-]+@[\w.-]+\.\w+$', email)
    print(f"{email}: {'✓ Valid' if is_valid else '✗ Invalid'}")
# Output:
# user@example.com: ✓ Valid
# invalid.email: ✗ Invalid
# test@domain.org: ✓ Valid
```

### Using Built-in Patterns
```python
skill = RegexSkill()

# Use built-in email pattern
pattern = skill.generate('email')
print(pattern['pattern'])

is_valid = skill.validate(pattern['pattern'], "admin@company.com")
print(f"Valid: {is_valid}")
```

### Password Strength Validation
```python
# Strong password: 8+ chars, upper, lower, digit, special
strong_pattern = skill.generate('password_strong')

test_passwords = ['weak', 'Password1', 'Pass123!']
for pwd in test_passwords:
    is_strong = skill.validate(strong_pattern['pattern'], pwd)
    print(f"'{pwd}': {'Strong' if is_strong else 'Weak'}")
```

## Text Replacement

### Simple Replacement
```python
skill = RegexSkill()

# Replace all digits with X
text = "ID: 12345, Code: 67890"
new_text, count = skill.replace(r'\d+', 'XXXXX', text)
print(new_text)  # ID: XXXXX, Code: XXXXX
print(f"Replaced {count} occurrences")
```

### Using Backreferences
```python
# Swap first and last names
text = "Doe, John"
new_text, _ = skill.replace(r'(\w+),\s*(\w+)', r'\2 \1', text)
print(new_text)  # John Doe
```

### Format Phone Numbers
```python
# Normalize phone numbers
text = "Call 5551234567 or 555-987-6543"
new_text, _ = skill.replace(
    r'(\d{3})-?(\d{3})-?(\d{4})',
    r'(\1) \2-\3',
    text
)
print(new_text)  # Call (555) 123-4567 or (555) 987-6543
```

## Text Splitting

### Split by Whitespace
```python
skill = RegexSkill()

text = "apple    banana\tcherry   date"
parts = skill.split(r'\s+', text)
print(parts)  # ['apple', 'banana', 'cherry', 'date']
```

### Split by Multiple Delimiters
```python
# Split by comma or semicolon
text = "a,b;c,d"
parts = skill.split(r'[,;]', text)
print(parts)  # ['a', 'b', 'c', 'd']
```

### CSV Parsing
```python
csv_line = 'John Doe,30,"New York, NY",Engineer'
# Split by comma, but not inside quotes
parts = skill.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', csv_line)
print(parts)
# ['John Doe', '30', '"New York, NY"', 'Engineer']
```

## Testing Patterns

### Batch Testing
```python
skill = RegexSkill()

# Test IPv4 pattern
test_cases = [
    TestCase('192.168.1.1', True, 'Valid private IP'),
    TestCase('255.255.255.255', True, 'Valid broadcast'),
    TestCase('256.1.1.1', False, 'Invalid - 256 > 255'),
    TestCase('192.168.1', False, 'Invalid - missing octet'),
]

results = skill.test(
    r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
    test_cases
)

print(f"Success rate: {results['success_rate']:.0%}")
for r in results['results']:
    icon = "✓" if r['status'] == 'PASS' else "✗"
    print(f"{icon} {r['input']} - {r['description']}")
```

### String Test Cases
```python
# Simple string test cases
results = skill.test(r'^\d{5}$', ['12345', '1234', '123456'])
print(f"Passed: {results['passed']}/{results['total']}")
```

## Pattern Explanation

### Understanding Complex Patterns
```python
skill = RegexSkill()

# Explain a password validation pattern
explanations = skill.explain(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$')

print("Password Pattern Breakdown:")
print("-" * 50)
for exp in explanations:
    print(f"{exp['char']:<15} [{exp['type']:<12}] {exp['meaning']}")
```

**Output:**
```
Password Pattern Breakdown:
--------------------------------------------------
^               [anchor      ] Start of string
(               [group       ] Start of capturing group
?:              [group       ] Non-capturing group
=               [literal     ] Literal: =
.               [character_cl] Any character (except newline)
*               [quantifier  ] Zero or more of preceding
[               [character_cl] Character class: [a-z]
...
```

## Extracting Groups

### Named Groups
```python
skill = RegexSkill()

log_line = '2024-01-15 10:30:45 [ERROR] Connection failed'
pattern = r'(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) \[(?P<level>\w+)\] (?P<message>.+)'

results = skill.extract_groups(pattern, log_line)
for result in results:
    print(f"Full match: {result['full_match']}")
    print(f"Named groups: {result['named_groups']}")
# {'date': '2024-01-15', 'time': '10:30:45', 'level': 'ERROR', 'message': 'Connection failed'}
```

### Multiple Matches with Groups
```python
text = "Prices: $10.99, $25.50, $100.00"
pattern = r'\$(?P<dollars>\d+)\.(?P<cents>\d{2})'

results = skill.extract_groups(pattern, text)
for result in results:
    print(f"${result['named_groups']['dollars']}.{result['named_groups']['cents']}")
# $10.99
# $25.50
# $100.00
```

## Practical Workflows

### Log Analysis
```python
#!/usr/bin/env python3
"""Analyze web server logs"""

from main import RegexSkill

skill = RegexSkill()

# Common log pattern
log_pattern = r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<request>[^"]+)" (?P<status>\d+) (?P<size>\d+)'

log_line = '192.168.1.1 - - [20/Feb/2024:10:30:45 +0000] "GET /api/users HTTP/1.1" 200 1024'

results = skill.extract_groups(log_pattern, log_line)
if results:
    data = results[0]['named_groups']
    print(f"IP: {data['ip']}")
    print(f"Time: {data['time']}")
    print(f"Request: {data['request']}")
    print(f"Status: {data['status']}")
```

### Data Extraction Pipeline
```python
# Extract structured data from unstructured text
def extract_contacts(text):
    skill = RegexSkill()
    
    # Extract emails
    emails = skill.match(r'[\w.-]+@[\w.-]+\.\w+', text)
    
    # Extract phone numbers
    phones = skill.match(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}', text)
    
    # Extract URLs
    urls = skill.match(r'https?://[^\s<>"{}|\\^`\[\]]+', text)
    
    return {
        'emails': [m.text for m in emails],
        'phones': [m.text for m in phones],
        'urls': [m.text for m in urls]
    }

text = """
Contact John at john.doe@example.com or call +1-555-123-4567.
Visit our website: https://company.com/contact
"""
print(extract_contacts(text))
```

## CLI Examples

### Match Command
```bash
# Find all email addresses in text
python main.py match "[\w.-]+@[\w.-]+\.\w+" "Contact: support@example.com"

# Find with flags (case-insensitive)
python main.py match "hello" "HELLO Hello" -f ignorecase

# Read from file
python main.py match "\d+" --file numbers.txt
```

### Validate Command
```bash
# Validate email
python main.py validate "^[\w.-]+@[\w.-]+\.\w+$" "user@example.com"

# Validate with built-in pattern
python main.py validate "$(python main.py generate email -q pattern)" "test@test.com"
```

### Replace Command
```bash
# Simple replacement
python main.py replace "\d+" "XXX" "Code: 12345"

# Limited replacements
python main.py replace "\s+" " " "a    b    c    d" --count 2

# Read from file and write to file
python main.py replace "OLD" "NEW" --file input.txt > output.txt
```

### Test Command
```bash
# Create test file
cat > tests.txt << EOF
valid@example.com
invalid
another@valid.org
EOF

# Run tests
python main.py test "^[\w.-]+@[\w.-]+\.\w+$" --file tests.txt
```

### Generate Command
```bash
# List all patterns
python main.py generate list

# Get specific pattern
python main.py generate email

# Use in validation
python main.py validate "$(python main.py generate email | head -1)" "user@example.com"
```

### Explain Command
```bash
# Explain complex pattern
python main.py explain "^(?=.*[a-z])(?=.*[A-Z]).{8,}$"
```
