#!/usr/bin/env python3
"""
Base64 Skill - Base64 encoding/decoding utility
Supports text encoding, image conversion, URL-safe variant, and file operations
"""

import base64
import io
import os
from typing import Union, Optional, Tuple
from pathlib import Path


class Base64Skill:
    """
    A comprehensive Base64 encoding/decoding utility supporting:
    - Standard Base64 encoding/decoding
    - URL-safe Base64 (RFC 4648)
    - Image to/from Base64 conversion
    - File encoding/decoding
    - Base64 validation
    """
    
    def __init__(self):
        """Initialize the Base64Skill"""
        self._supported_image_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', 
            '.webp', '.svg', '.ico', '.tiff', '.tif'
        }
    
    def encode_text(self, text: Union[str, bytes], encoding: str = 'utf-8') -> str:
        """
        Encode text to Base64
        
        Args:
            text: String or bytes to encode
            encoding: Text encoding for string input
            
        Returns:
            Base64 encoded string
        """
        if isinstance(text, str):
            text = text.encode(encoding)
        
        return base64.b64encode(text).decode('ascii')
    
    def decode_text(
        self, 
        b64_string: str, 
        encoding: str = 'utf-8',
        errors: str = 'strict'
    ) -> str:
        """
        Decode Base64 to text
        
        Args:
            b64_string: Base64 encoded string
            encoding: Text encoding for output
            errors: Error handling strategy
            
        Returns:
            Decoded text string
            
        Raises:
            ValueError: If input is not valid Base64
        """
        try:
            decoded = base64.b64decode(b64_string, validate=True)
            return decoded.decode(encoding, errors=errors)
        except Exception as e:
            raise ValueError(f"Invalid Base64 string: {e}")
    
    def encode_bytes(self, data: bytes) -> bytes:
        """
        Encode bytes to Base64 bytes
        
        Args:
            data: Raw bytes to encode
            
        Returns:
            Base64 encoded bytes
        """
        return base64.b64encode(data)
    
    def decode_bytes(self, b64_bytes: Union[str, bytes]) -> bytes:
        """
        Decode Base64 to raw bytes
        
        Args:
            b64_bytes: Base64 encoded data
            
        Returns:
            Decoded raw bytes
        """
        if isinstance(b64_bytes, str):
            b64_bytes = b64_bytes.encode('ascii')
        return base64.b64decode(b64_bytes, validate=True)
    
    def encode_url_safe(self, text: Union[str, bytes], encoding: str = 'utf-8') -> str:
        """
        Encode to URL-safe Base64 (RFC 4648)
        Replaces + with - and / with _
        
        Args:
            text: String or bytes to encode
            encoding: Text encoding for string input
            
        Returns:
            URL-safe Base64 encoded string
        """
        if isinstance(text, str):
            text = text.encode(encoding)
        
        return base64.urlsafe_b64encode(text).decode('ascii').rstrip('=')
    
    def decode_url_safe(
        self, 
        b64_string: str, 
        encoding: str = 'utf-8',
        errors: str = 'strict'
    ) -> str:
        """
        Decode URL-safe Base64 to text
        
        Args:
            b64_string: URL-safe Base64 encoded string
            encoding: Text encoding for output
            errors: Error handling strategy
            
        Returns:
            Decoded text string
        """
        # Add padding if needed
        padding = 4 - len(b64_string) % 4
        if padding != 4:
            b64_string += '=' * padding
        
        try:
            decoded = base64.urlsafe_b64decode(b64_string)
            return decoded.decode(encoding, errors=errors)
        except Exception as e:
            raise ValueError(f"Invalid URL-safe Base64 string: {e}")
    
    def image_to_base64(
        self, 
        image_path: str, 
        format_data_uri: bool = False
    ) -> str:
        """
        Convert image file to Base64
        
        Args:
            image_path: Path to image file
            format_data_uri: If True, return as data URI (data:image/...)
            
        Returns:
            Base64 encoded image string
            
        Raises:
            FileNotFoundError: If image file doesn't exist
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        ext = Path(image_path).suffix.lower()
        if ext not in self._supported_image_extensions:
            raise ValueError(f"Unsupported image format: {ext}")
        
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        b64_string = base64.b64encode(image_data).decode('ascii')
        
        if format_data_uri:
            mime_type = self._get_mime_type(ext)
            return f"data:{mime_type};base64,{b64_string}"
        
        return b64_string
    
    def base64_to_image(
        self, 
        b64_string: str, 
        output_path: str,
        from_data_uri: bool = False
    ) -> str:
        """
        Convert Base64 to image file
        
        Args:
            b64_string: Base64 encoded image
            output_path: Path for output image
            from_data_uri: If True, parse as data URI
            
        Returns:
            Path to saved image
        """
        if from_data_uri:
            b64_string = self._extract_from_data_uri(b64_string)
        
        # Clean the string
        b64_string = b64_string.strip()
        
        try:
            image_data = base64.b64decode(b64_string, validate=True)
        except Exception as e:
            raise ValueError(f"Invalid Base64 image data: {e}")
        
        with open(output_path, 'wb') as f:
            f.write(image_data)
        
        return output_path
    
    def encode_file(self, file_path: str) -> str:
        """
        Encode any file to Base64
        
        Args:
            file_path: Path to file
            
        Returns:
            Base64 encoded string
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        return base64.b64encode(file_data).decode('ascii')
    
    def decode_file(self, b64_string: str, output_path: str) -> str:
        """
        Decode Base64 to file
        
        Args:
            b64_string: Base64 encoded file data
            output_path: Path for output file
            
        Returns:
            Path to saved file
        """
        # Clean the string
        b64_string = b64_string.strip()
        
        try:
            file_data = base64.b64decode(b64_string, validate=True)
        except Exception as e:
            raise ValueError(f"Invalid Base64 data: {e}")
        
        with open(output_path, 'wb') as f:
            f.write(file_data)
        
        return output_path
    
    def validate(self, b64_string: str) -> bool:
        """
        Validate if string is valid Base64
        
        Args:
            b64_string: String to validate
            
        Returns:
            True if valid Base64, False otherwise
        """
        try:
            # Remove whitespace and common formatting characters
            cleaned = b64_string.strip().replace('\n', '').replace('\r', '')
            base64.b64decode(cleaned, validate=True)
            return True
        except Exception:
            return False
    
    def is_valid(self, b64_string: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Base64 with detailed error message
        
        Args:
            b64_string: String to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            cleaned = b64_string.strip().replace('\n', '').replace('\r', '')
            base64.b64decode(cleaned, validate=True)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def get_info(self, b64_string: str) -> dict:
        """
        Get information about a Base64 string
        
        Args:
            b64_string: Base64 string to analyze
            
        Returns:
            Dictionary with information
        """
        cleaned = b64_string.strip().replace('\n', '').replace('\r', '')
        
        info = {
            'valid': False,
            'length_chars': len(cleaned),
            'length_bytes': 0,
            'has_padding': '=' in cleaned,
            'is_url_safe': '-' in cleaned or '_' in cleaned,
            'is_data_uri': cleaned.startswith('data:'),
        }
        
        try:
            decoded = base64.b64decode(cleaned, validate=True)
            info['valid'] = True
            info['length_bytes'] = len(decoded)
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def encode_with_line_breaks(
        self, 
        data: Union[str, bytes], 
        line_length: int = 76,
        encoding: str = 'utf-8'
    ) -> str:
        """
        Encode with line breaks (MIME style)
        
        Args:
            data: Data to encode
            line_length: Characters per line (default 76 for MIME)
            encoding: Text encoding for string input
            
        Returns:
            Base64 with line breaks
        """
        if isinstance(data, str):
            data = data.encode(encoding)
        
        encoded = base64.b64encode(data).decode('ascii')
        
        # Add line breaks
        lines = []
        for i in range(0, len(encoded), line_length):
            lines.append(encoded[i:i + line_length])
        
        return '\n'.join(lines)
    
    def strip_padding(self, b64_string: str) -> str:
        """
        Remove Base64 padding characters
        
        Args:
            b64_string: Base64 string
            
        Returns:
            Base64 without padding
        """
        return b64_string.rstrip('=')
    
    def add_padding(self, b64_string: str) -> str:
        """
        Add Base64 padding if missing
        
        Args:
            b64_string: Base64 string without padding
            
        Returns:
            Properly padded Base64 string
        """
        padding = 4 - len(b64_string) % 4
        if padding != 4:
            return b64_string + '=' * padding
        return b64_string
    
    def _get_mime_type(self, ext: str) -> str:
        """Get MIME type for image extension"""
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff',
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def _extract_from_data_uri(self, data_uri: str) -> str:
        """Extract Base64 data from data URI"""
        if not data_uri.startswith('data:'):
            raise ValueError("Not a valid data URI")
        
        # Format: data:[<mediatype>][;base64],<data>
        if ',' not in data_uri:
            raise ValueError("Invalid data URI format")
        
        header, data = data_uri.split(',', 1)
        
        if ';base64' not in header:
            raise ValueError("Data URI is not Base64 encoded")
        
        return data


# CLI interface
if __name__ == '__main__':
    import sys
    import json
    
    skill = Base64Skill()
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <command> [args...]")
        print("Commands: encode, decode, url-encode, url-decode, image-encode, image-decode, file-encode, file-decode, validate, info")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == 'encode':
            if len(sys.argv) < 3:
                # Read from stdin
                text = sys.stdin.read()
            else:
                text = sys.argv[2]
            result = skill.encode_text(text)
            print(result)
        
        elif command == 'decode':
            if len(sys.argv) < 3:
                b64 = sys.stdin.read()
            else:
                b64 = sys.argv[2]
            result = skill.decode_text(b64)
            print(result)
        
        elif command == 'url-encode':
            text = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
            result = skill.encode_url_safe(text)
            print(result)
        
        elif command == 'url-decode':
            b64 = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
            result = skill.decode_url_safe(b64)
            print(result)
        
        elif command == 'image-encode' and len(sys.argv) >= 3:
            data_uri = '--data-uri' in sys.argv
            result = skill.image_to_base64(sys.argv[2], format_data_uri=data_uri)
            print(result)
        
        elif command == 'image-decode' and len(sys.argv) >= 4:
            from_uri = '--from-uri' in sys.argv
            result = skill.base64_to_image(sys.argv[2], sys.argv[3], from_data_uri=from_uri)
            print(f"Image saved to: {result}")
        
        elif command == 'file-encode' and len(sys.argv) >= 3:
            result = skill.encode_file(sys.argv[2])
            print(result)
        
        elif command == 'file-decode' and len(sys.argv) >= 4:
            result = skill.decode_file(sys.argv[2], sys.argv[3])
            print(f"File saved to: {result}")
        
        elif command == 'validate':
            b64 = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
            result = skill.validate(b64)
            print(f"Valid: {'YES' if result else 'NO'}")
        
        elif command == 'info':
            b64 = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
            info = skill.get_info(b64)
            print(json.dumps(info, indent=2))
        
        else:
            print("Invalid command or arguments")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
