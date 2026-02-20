# Base64 Skill

**Category:** Utility  
**Version:** 1.0.0  
**Author:** godlike-kimi-skills

---

## Use When

- Encoding binary data as text for transmission or storage
- Embedding images directly in HTML/CSS (data URIs)
- Encoding/decoding JWT tokens or API keys
- Converting file attachments for email transmission
- URL-safe encoding for web parameters
- Working with Base64-encoded data from APIs
- Validating Base64-encoded strings
- Decoding configuration files with embedded binary data

---

## Out of Scope

- Encryption/decryption (Base64 is encoding, not encryption)
- Compression/decompression
- URL percent-encoding (use urllib for this)
- HTML entity encoding
- Hexadecimal encoding/decoding
- Binary protocol implementation
- Steganography
- QR code generation
- Barcode encoding

---

## Quick Reference

### Core Methods

```python
from skills.base64_skill.main import Base64Skill

skill = Base64Skill()

# Text encoding/decoding
encoded = skill.encode_text("Hello World")
decoded = skill.decode_text("SGVsbG8gV29ybGQ=")

# URL-safe encoding (RFC 4648)
url_safe = skill.encode_url_safe("Hello World!")
decoded = skill.decode_url_safe(url_safe)

# Image to Base64
img_b64 = skill.image_to_base64("photo.jpg", format_data_uri=True)
# Returns: data:image/jpeg;base64,/9j/4AAQSkZJRg...

# Base64 to image
skill.base64_to_image(img_b64, "output.jpg")

# File encoding/decoding
file_b64 = skill.encode_file("document.pdf")
skill.decode_file(file_b64, "document_copy.pdf")

# Validation
is_valid = skill.validate("SGVsbG8gV29ybGQ=")
```

---

## Base64 Variants

### Standard Base64
- Characters: `A-Z`, `a-z`, `0-9`, `+`, `/`
- Padding: `=`
- Use: Email, MIME, general encoding

### URL-Safe Base64 (RFC 4648)
- Characters: `A-Z`, `a-z`, `0-9`, `-`, `_`
- Padding: None (usually stripped)
- Use: URLs, filenames, JWT tokens

### MIME Style
- Line breaks every 76 characters
- Use: Email attachments

---

## Data URI Format

```
data:[<mediatype>][;base64],<data>
```

Examples:
- `data:text/plain;base64,SGVsbG8=`
- `data:image/png;base64,iVBORw0KGgo...`
- `data:application/pdf;base64,JVBERi0xLjQ...`

---

## CLI Usage

```bash
# Encode text
echo "Hello World" | python main.py encode
python main.py encode "Hello World"

# Decode text
echo "SGVsbG8gV29ybGQ=" | python main.py decode
python main.py decode "SGVsbG8gV29ybGQ="

# URL-safe encode
python main.py url-encode "Hello World!"

# URL-safe decode
python main.py url-decode "SGVsbG8gV29ybGQ"

# Image to Base64
python main.py image-encode photo.jpg
python main.py image-encode photo.jpg --data-uri

# Base64 to image
python main.py image-decode <base64_string> output.jpg
python main.py image-decode <data_uri> output.jpg --from-uri

# File encoding
python main.py file-encode document.pdf

# File decoding
python main.py file-decode <base64_string> output.pdf

# Validation
echo "SGVsbG8=" | python main.py validate
python main.py validate "SGVsbG8="

# Get info
python main.py info "SGVsbG8gV29ybGQ="
```

---

## Method Reference

### Text Encoding

- `encode_text(text, encoding='utf-8')` - Encode string to Base64
- `decode_text(b64_string, encoding='utf-8', errors='strict')` - Decode Base64 to string
- `encode_bytes(data)` - Encode bytes to Base64 bytes
- `decode_bytes(b64_bytes)` - Decode Base64 to raw bytes

### URL-Safe Encoding

- `encode_url_safe(text, encoding='utf-8')` - URL-safe encode
- `decode_url_safe(b64_string, encoding='utf-8')` - URL-safe decode

### Image Operations

- `image_to_base64(image_path, format_data_uri=False)` - Image to Base64
- `base64_to_image(b64_string, output_path, from_data_uri=False)` - Base64 to image

### File Operations

- `encode_file(file_path)` - Encode any file
- `decode_file(b64_string, output_path)` - Decode to file

### Validation & Info

- `validate(b64_string)` - Quick validation
- `is_valid(b64_string)` - Validation with error details
- `get_info(b64_string)` - Get detailed information

### Utilities

- `encode_with_line_breaks(data, line_length=76)` - MIME style encoding
- `strip_padding(b64_string)` - Remove padding
- `add_padding(b64_string)` - Add missing padding

---

## Dependencies

```
pillow>=10.0.0  # For image processing
```

---

## Supported Image Formats

- `.png` - PNG images
- `.jpg`, `.jpeg` - JPEG images
- `.gif` - GIF images
- `.bmp` - BMP images
- `.webp` - WebP images
- `.svg` - SVG images
- `.ico` - Icon files
- `.tiff`, `.tif` - TIFF images

---

## Examples

### Embedded Images in HTML

```python
skill = Base64Skill()

# Convert logo to data URI for inline HTML
logo_data_uri = skill.image_to_base64("logo.png", format_data_uri=True)

html = f'''
<!DOCTYPE html>
<html>
<head><title>My Page</title></head>
<body>
    <img src="{logo_data_uri}" alt="Logo">
</body>
</html>
'''

with open("page.html", "w") as f:
    f.write(html)
```

### API Data Encoding

```python
skill = Base64Skill()

# Prepare binary data for JSON API
data = {
    "filename": "report.pdf",
    "content": skill.encode_file("report.pdf"),
    "metadata": {
        "title": skill.encode_url_safe("Q4 Financial Report 2026"),
    }
}

# Send to API
import json
response = requests.post(
    "https://api.example.com/upload",
    json=data
)
```

### Processing JWT Token

```python
skill = Base64Skill()

# JWT: header.payload.signature
jwt_token = "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiYWxpY2UifQ.signature"

# Split and decode payload
header_b64, payload_b64, signature = jwt_token.split('.')

# Decode payload (URL-safe Base64)
payload_json = skill.decode_url_safe(payload_b64)
payload = json.loads(payload_json)

print(f"User: {payload['user']}")
```

### CSS with Embedded Font

```python
skill = Base64Skill()

# Embed font in CSS
font_base64 = skill.encode_file("custom-font.woff2")

css = f'''
@font-face {{
    font-family: 'CustomFont';
    src: url(data:font/woff2;base64,{font_base64}) format('woff2');
}}
'''

with open("styles.css", "w") as f:
    f.write(css)
```
