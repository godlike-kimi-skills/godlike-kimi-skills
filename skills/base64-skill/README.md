# Base64 Skill

A Base64 encoding/decoding utility for Kimi CLI supporting text encoding, image conversion, and URL-safe variants.

## Features

- 📝 **Text Encoding/Decoding**: Standard Base64 operations
- 🖼️ **Image Conversion**: Convert images to/from Base64
- 🔗 **URL-Safe Base64**: RFC 4648 URL-safe encoding
- 📁 **File Support**: Encode/decode files of any type
- ✅ **Validation**: Validate Base64 strings

## Installation

```bash
# Copy skill to Kimi skills directory
cp -r base64-skill ~/.kimi/skills/

# Install dependencies
pip install -r ~/.kimi/skills/base64-skill/requirements.txt
```

## Quick Start

```python
from skills.base64_skill.main import Base64Skill

skill = Base64Skill()

# Encode text
encoded = skill.encode_text("Hello World")
print(f"Encoded: {encoded}")

# Decode text
decoded = skill.decode_text("SGVsbG8gV29ybGQ=")
print(f"Decoded: {decoded}")

# Image to Base64
img_b64 = skill.image_to_base64("photo.jpg")
print(f"Image Base64 (first 50 chars): {img_b64[:50]}...")

# Base64 to image
skill.base64_to_image(img_b64, "output.jpg")

# URL-safe encoding
url_safe = skill.encode_url_safe("Hello World!")
print(f"URL-safe: {url_safe}")
```

## Documentation

- [SKILL.md](./SKILL.md) - Detailed usage guide
- [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md) - Example use cases

## License

MIT License
