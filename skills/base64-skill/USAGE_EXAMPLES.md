# Base64 Skill - Usage Examples

## Example 1: Inline Images for HTML/CSS

Embed images directly in HTML without external files:

```python
from skills.base64_skill.main import Base64Skill

skill = Base64Skill()

# Convert logo to data URI
logo_data_uri = skill.image_to_base64("company_logo.png", format_data_uri=True)

# Create self-contained HTML email
html_email = f'''
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .logo {{ width: 200px; }}
    </style>
</head>
<body>
    <img src="{logo_data_uri}" alt="Company Logo" class="logo">
    <h1>Welcome to Our Service</h1>
    <p>Thank you for signing up!</p>
</body>
</html>
'''

with open("welcome_email.html", "w") as f:
    f.write(html_email)

print("Created self-contained HTML email")
print(f"Logo data URI length: {len(logo_data_uri)} chars")

# Also works for CSS background images
icon_data_uri = skill.image_to_base64("icon.png", format_data_uri=True)
css = f'''
.icon {{
    background-image: url("{icon_data_uri}");
    width: 16px;
    height: 16px;
}}
'''
```

## Example 2: API Data Transmission

Send binary data through JSON APIs:

```python
skill = Base64Skill()
import requests

class FileAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.skill = Base64Skill()
    
    def upload_file(self, filepath, metadata=None):
        """Upload file as Base64 in JSON"""
        import os
        
        # Encode file
        file_data = self.skill.encode_file(filepath)
        
        # Build payload
        payload = {
            "filename": os.path.basename(filepath),
            "content": file_data,
            "encoding": "base64",
            "metadata": metadata or {},
        }
        
        # Send
        response = requests.post(
            f"{self.base_url}/upload",
            json=payload,
            headers=self.headers
        )
        
        return response.json()
    
    def download_file(self, file_id, output_path):
        """Download and decode file"""
        response = requests.get(
            f"{self.base_url}/files/{file_id}",
            headers=self.headers
        )
        
        data = response.json()
        file_content = data["content"]
        
        # Decode and save
        self.skill.decode_file(file_content, output_path)
        return output_path

# Usage
api = FileAPI("https://api.example.com", "your_api_key")
result = api.upload_file("document.pdf", {"type": "contract"})
print(f"Uploaded with ID: {result['id']}")
```

## Example 3: JWT Token Processing

Decode and inspect JWT tokens:

```python
skill = Base64Skill()
import json

def decode_jwt(jwt_token):
    """Decode JWT payload without verification"""
    
    # Split JWT parts
    parts = jwt_token.split('.')
    if len(parts) != 3:
        raise ValueError("Invalid JWT format")
    
    header_b64, payload_b64, signature = parts
    
    # Decode header
    header_json = skill.decode_url_safe(header_b64)
    header = json.loads(header_json)
    
    # Decode payload
    payload_json = skill.decode_url_safe(payload_b64)
    payload = json.loads(payload_json)
    
    return {
        'header': header,
        'payload': payload,
        'signature': signature,
    }

# Example JWT (this is a dummy token)
jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

try:
    decoded = decode_jwt(jwt)
    
    print("Header:")
    print(json.dumps(decoded['header'], indent=2))
    
    print("\nPayload:")
    print(json.dumps(decoded['payload'], indent=2))
    
except Exception as e:
    print(f"Error: {e}")
```

## Example 4: URL-Safe Parameter Encoding

Encode data for URL parameters:

```python
skill = Base64Skill()
import json

def create_shareable_link(base_url, data):
    """Create a shareable link with encoded data"""
    
    # Convert data to JSON
    json_data = json.dumps(data)
    
    # URL-safe encode
    encoded = skill.encode_url_safe(json_data)
    
    # Build URL
    return f"{base_url}?data={encoded}"

def decode_shareable_data(url_or_param):
    """Decode data from URL parameter"""
    
    # Extract parameter if full URL
    if '?' in url_or_param:
        from urllib.parse import parse_qs, urlparse
        parsed = urlparse(url_or_param)
        params = parse_qs(parsed.query)
        encoded = params.get('data', [''])[0]
    else:
        encoded = url_or_param
    
    # Decode
    json_data = skill.decode_url_safe(encoded)
    return json.loads(json_data)

# Usage
data = {
    "filters": {"category": "electronics", "price_max": 500},
    "sort": "price_asc",
    "view": "grid"
}

share_url = create_shareable_link("https://shop.example.com/products", data)
print(f"Shareable URL: {share_url}")

# Decode
decoded = decode_shareable_data(share_url)
print(f"Decoded: {json.dumps(decoded, indent=2)}")
```

## Example 5: Configuration File with Binary Data

Store binary data in config files:

```python
skill = Base64Skill()
import yaml

class ConfigWithBinary:
    """Configuration that can include binary data"""
    
    def __init__(self):
        self.skill = Base64Skill()
    
    def load_config(self, filepath):
        """Load config with binary data"""
        with open(filepath, 'r') as f:
            config = yaml.safe_load(f)
        
        # Decode any binary fields
        if 'icon' in config and config['icon'].get('base64'):
            icon_path = config['icon'].get('cache_path', '/tmp/icon.png')
            self.skill.base64_to_image(config['icon']['base64'], icon_path)
            config['icon']['path'] = icon_path
        
        return config
    
    def save_config(self, config, filepath):
        """Save config with binary data encoded"""
        config_copy = config.copy()
        
        # Encode binary files
        if 'icon_path' in config:
            config_copy['icon'] = {
                'base64': self.skill.image_to_base64(config['icon_path']),
                'format': 'png'
            }
            del config_copy['icon_path']
        
        with open(filepath, 'w') as f:
            yaml.dump(config_copy, f)

# Usage
config_manager = ConfigWithBinary()

# Save config with icon
config = {
    "app_name": "My App",
    "version": "1.0",
    "icon_path": "app_icon.png",
    "settings": {"theme": "dark"}
}
config_manager.save_config(config, "app_config.yaml")

# Load config
loaded = config_manager.load_config("app_config.yaml")
print(f"Loaded config for: {loaded['app_name']}")
```

## Example 6: Email Attachment Handling

Prepare email attachments:

```python
skill = Base64Skill()
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def create_email_with_attachment(
    sender, recipient, subject, body, attachment_path
):
    """Create email with Base64 encoded attachment"""
    
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    
    # Add body
    msg.attach(MIMEText(body, 'plain'))
    
    # Add attachment
    with open(attachment_path, 'rb') as f:
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(f.read())
    
    encoders.encode_base64(attachment)
    
    filename = attachment_path.split('/')[-1]
    attachment.add_header(
        'Content-Disposition',
        f'attachment; filename= {filename}'
    )
    
    msg.attach(attachment)
    
    return msg

# Alternative: Manual Base64 attachment
skill = Base64Skill()

def encode_attachment_for_api(filepath):
    """Encode attachment for API upload"""
    import os
    
    file_b64 = skill.encode_file(filepath)
    mime_type = "application/pdf" if filepath.endswith('.pdf') else "application/octet-stream"
    
    return {
        "filename": os.path.basename(filepath),
        "content": file_b64,
        "content_type": mime_type,
        "encoding": "base64",
    }

# Usage
attachment_info = encode_attachment_for_api("report.pdf")
print(f"Encoded {attachment_info['filename']} ({len(attachment_info['content'])} chars)")
```

## Example 7: Data Validation

Validate Base64 data before processing:

```python
skill = Base64Skill()

def safe_decode_image(b64_data, output_path):
    """Safely decode image with validation"""
    
    # Validate first
    is_valid, error = skill.is_valid(b64_data)
    
    if not is_valid:
        print(f"Invalid Base64: {error}")
        return None
    
    # Get info
    info = skill.get_info(b64_data)
    print(f"Valid Base64: {info['length_chars']} chars, ~{info['length_bytes']} bytes")
    
    # Check if it's a data URI
    if info['is_data_uri']:
        print("Detected data URI format")
        from_uri = True
    else:
        from_uri = False
    
    # Decode
    try:
        skill.base64_to_image(b64_data, output_path, from_data_uri=from_uri)
        print(f"Image saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Decode error: {e}")
        return None

# Test with various inputs
test_cases = [
    "SGVsbG8gV29ybGQ=",  # Valid: "Hello World"
    "not_valid!!!",       # Invalid
    "data:image/png;base64,iVBORw0KGgo=",  # Data URI
]

for test in test_cases:
    print(f"\nTesting: {test[:30]}...")
    is_valid = skill.validate(test)
    print(f"Valid: {is_valid}")
```
