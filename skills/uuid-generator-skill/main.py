#!/usr/bin/env python3
"""
UUID Generator Skill - ID and UUID Generation Tool
Supports: UUID v1/v4/v7, short IDs, random strings, NanoID, CUID
"""

import uuid
import secrets
import string
import re
import time
import argparse
import sys
from typing import List, Optional, Tuple, Dict, Any, Union
from datetime import datetime
from dataclasses import dataclass


@dataclass
class UUIDInfo:
    """Information about a UUID"""
    version: int
    variant: str
    hex: str
    int: int
    bytes: bytes
    time: Optional[datetime]
    is_valid: bool


class UUIDGeneratorSkill:
    """Main skill class for ID generation"""
    
    # Alphabet for short IDs (Base62)
    BASE62_ALPHABET = string.ascii_letters + string.digits
    # Alphabet for NanoID (URL-safe)
    NANOID_ALPHABET = '_-' + string.ascii_letters + string.digits
    # Alphabet for CUID (Base36)
    CUID_ALPHABET = string.ascii_lowercase + string.digits
    
    def __init__(self):
        self.name = "uuid-generator-skill"
        self.version = "1.0.0"
        # Counter for CUID generation
        self._cuid_counter = 0
        self._cuid_last_time = 0
    
    def uuid_v4(self) -> str:
        """
        Generate UUID version 4 (random)
        
        Returns:
            UUID v4 string
        """
        return str(uuid.uuid4())
    
    def uuid_v1(self) -> str:
        """
        Generate UUID version 1 (timestamp + MAC address)
        
        Returns:
            UUID v1 string
        """
        return str(uuid.uuid1())
    
    def uuid_v7(self) -> str:
        """
        Generate UUID version 7 (Unix timestamp + random)
        Time-ordered, sortable UUID
        
        Returns:
            UUID v7 string
        """
        # UUID v7: 48-bit timestamp + 74 random bits + version/variant
        timestamp_ms = int(time.time() * 1000)
        
        # 48-bit timestamp (6 bytes)
        timestamp_bytes = timestamp_ms.to_bytes(6, byteorder='big')
        
        # 74 random bits (10 bytes, but we'll use 10 and mask)
        random_bytes = secrets.token_bytes(10)
        
        # Combine: 6 bytes timestamp + 10 bytes random
        all_bytes = timestamp_bytes + random_bytes
        
        # Set version (0111 = 7) in bits 48-51
        # Byte 6: high nibble is version
        version_byte = all_bytes[6] & 0x0F | 0x70
        
        # Set variant (10) in bits 64-65
        # Byte 8: high 2 bits are variant
        variant_byte = all_bytes[8] & 0x3F | 0x80
        
        # Create final byte array
        final_bytes = (
            all_bytes[0:6] +
            bytes([version_byte]) +
            bytes([all_bytes[7]]) +
            bytes([variant_byte]) +
            all_bytes[9:16]
        )
        
        # Convert to UUID string
        return str(uuid.UUID(bytes=final_bytes))
    
    def uuid(self, version: int = 4) -> str:
        """
        Generate UUID with specified version
        
        Args:
            version: UUID version (1, 4, or 7)
            
        Returns:
            UUID string
        """
        if version == 1:
            return self.uuid_v1()
        elif version == 4:
            return self.uuid_v4()
        elif version == 7:
            return self.uuid_v7()
        else:
            raise ValueError(f"Unsupported UUID version: {version}. Use 1, 4, or 7.")
    
    def batch_uuid(self, count: int = 10, version: int = 4) -> List[str]:
        """
        Generate multiple UUIDs
        
        Args:
            count: Number of UUIDs to generate
            version: UUID version (1, 4, or 7)
            
        Returns:
            List of UUID strings
        """
        return [self.uuid(version) for _ in range(count)]
    
    def batch_uuid_v4(self, count: int = 10) -> List[str]:
        """Generate multiple UUID v4"""
        return self.batch_uuid(count, version=4)
    
    def batch_uuid_v1(self, count: int = 10) -> List[str]:
        """Generate multiple UUID v1"""
        return self.batch_uuid(count, version=1)
    
    def batch_uuid_v7(self, count: int = 10) -> List[str]:
        """Generate multiple UUID v7"""
        return self.batch_uuid(count, version=7)
    
    def short_id(self, length: int = 8) -> str:
        """
        Generate a short URL-safe ID
        
        Args:
            length: Length of the ID (default: 8)
            
        Returns:
            Short ID string
        """
        return ''.join(secrets.choice(self.BASE62_ALPHABET) for _ in range(length))
    
    def nanoid(self, size: int = 21) -> str:
        """
        Generate a NanoID
        NanoID is a small, fast, URL-friendly unique ID
        
        Args:
            size: Size of the ID (default: 21 for ~149 billion years needed for 1% collision)
            
        Returns:
            NanoID string
        """
        return ''.join(secrets.choice(self.NANOID_ALPHABET) for _ in range(size))
    
    def cuid(self) -> str:
        """
        Generate a CUID (Collision-resistant Unique Identifier)
        Format: c + timestamp(32) + counter(4) + fingerprint(2) + random(8)
        
        Returns:
            CUID string
        """
        # Base36 alphabet for CUID
        base36 = string.ascii_lowercase + string.digits
        
        # Timestamp (current time in base36)
        timestamp = int(time.time() * 1000)
        timestamp_str = ''
        while timestamp > 0:
            timestamp_str = base36[timestamp % 36] + timestamp_str
            timestamp //= 36
        timestamp_str = timestamp_str.zfill(8)
        
        # Counter (increments for same-millisecond requests)
        current_time = int(time.time() * 1000)
        if current_time > self._cuid_last_time:
            self._cuid_counter = 0
            self._cuid_last_time = current_time
        else:
            self._cuid_counter = (self._cuid_counter + 1) % 1296  # 36^2
        
        counter_str = ''
        counter = self._cuid_counter
        while counter > 0:
            counter_str = base36[counter % 36] + counter_str
            counter //= 36
        counter_str = counter_str.zfill(2)
        
        # Fingerprint (process identifier + random)
        fingerprint = ''.join(secrets.choice(base36) for _ in range(2))
        
        # Random suffix
        random_suffix = ''.join(secrets.choice(base36) for _ in range(8))
        
        # Combine: c + timestamp + counter + fingerprint + random
        return 'c' + timestamp_str + counter_str + fingerprint + random_suffix
    
    def random_string(self, length: int = 32, 
                     use_uppercase: bool = True,
                     use_lowercase: bool = True,
                     use_digits: bool = True,
                     use_special: bool = False) -> str:
        """
        Generate a random string
        
        Args:
            length: Length of the string
            use_uppercase: Include uppercase letters
            use_lowercase: Include lowercase letters
            use_digits: Include digits
            use_special: Include special characters
            
        Returns:
            Random string
        """
        alphabet = ''
        if use_uppercase:
            alphabet += string.ascii_uppercase
        if use_lowercase:
            alphabet += string.ascii_lowercase
        if use_digits:
            alphabet += string.digits
        if use_special:
            alphabet += '!@#$%^&*()-_=+[]{}|;:,.<>?'
        
        if not alphabet:
            raise ValueError("At least one character type must be selected")
        
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def alphanumeric(self, length: int = 32) -> str:
        """
        Generate alphanumeric random string
        
        Args:
            length: Length of the string
            
        Returns:
            Alphanumeric string
        """
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def hex_string(self, length: int = 32) -> str:
        """
        Generate hexadecimal string
        
        Args:
            length: Length of the string
            
        Returns:
            Hexadecimal string
        """
        return secrets.token_hex(length // 2 + length % 2)[:length]
    
    def base64_string(self, length: int = 32) -> str:
        """
        Generate base64 string
        
        Args:
            length: Length of the string
            
        Returns:
            Base64 string
        """
        import base64
        # Generate enough random bytes
        num_bytes = (length * 3 + 3) // 4
        random_bytes = secrets.token_bytes(num_bytes)
        encoded = base64.urlsafe_b64encode(random_bytes).decode('ascii')
        return encoded[:length]
    
    def validate(self, uuid_str: str) -> bool:
        """
        Validate UUID format
        
        Args:
            uuid_str: UUID string to validate
            
        Returns:
            True if valid UUID format
        """
        if not uuid_str:
            return False
        
        # UUID pattern: 8-4-4-4-12 hex digits
        pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
        return bool(re.match(pattern, uuid_str))
    
    def parse(self, uuid_str: str) -> Optional[UUIDInfo]:
        """
        Parse UUID and extract information
        
        Args:
            uuid_str: UUID string
            
        Returns:
            UUIDInfo object or None if invalid
        """
        if not self.validate(uuid_str):
            return None
        
        try:
            u = uuid.UUID(uuid_str)
            
            # Determine version
            version = u.version
            
            # Determine variant
            # UUID variant is in the first 2-3 bits of the 9th byte
            variant_bits = (u.bytes[8] >> 5) & 0x07
            if variant_bits == 0:
                variant = "NCS (reserved)"
            elif variant_bits == 4 or variant_bits == 5:
                variant = "RFC 4122"
            elif variant_bits == 6:
                variant = "Microsoft (reserved)"
            else:
                variant = "Future/Reserved"
            
            # Extract time for v1 and v7
            time_val = None
            if version == 1:
                time_val = datetime.fromtimestamp((u.time - 0x01b21dd213814000) / 10000000)
            elif version == 7:
                # v7: first 48 bits are timestamp in ms
                timestamp_ms = int.from_bytes(u.bytes[:6], byteorder='big')
                time_val = datetime.fromtimestamp(timestamp_ms / 1000)
            
            return UUIDInfo(
                version=version,
                variant=variant,
                hex=u.hex,
                int=u.int,
                bytes=u.bytes,
                time=time_val,
                is_valid=True
            )
        except Exception:
            return None
    
    def slug(self, uuid_str: str = None) -> str:
        """
        Convert UUID to URL-friendly slug (base62)
        
        Args:
            uuid_str: UUID string (if None, generates new UUID v4)
            
        Returns:
            Short slug string
        """
        if uuid_str is None:
            uuid_str = self.uuid_v4()
        
        if not self.validate(uuid_str):
            raise ValueError("Invalid UUID format")
        
        # Remove dashes and convert to int
        hex_str = uuid_str.replace('-', '')
        num = int(hex_str, 16)
        
        # Convert to base62
        if num == 0:
            return '0'
        
        slug = ''
        while num > 0:
            num, remainder = divmod(num, 62)
            slug = self.BASE62_ALPHABET[remainder] + slug
        
        return slug


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='UUID and ID Generator Tool')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # UUID command
    uuid_parser = subparsers.add_parser('uuid', help='Generate UUID')
    uuid_parser.add_argument('--version', '-v', type=int, choices=[1, 4, 7], default=4,
                            help='UUID version (default: 4)')
    uuid_parser.add_argument('--count', '-n', type=int, default=1,
                            help='Number of UUIDs to generate')
    uuid_parser.add_argument('--uppercase', '-u', action='store_true',
                            help='Output in uppercase')
    
    # Short ID command
    short_parser = subparsers.add_parser('short', help='Generate short ID')
    short_parser.add_argument('--length', '-l', type=int, default=8,
                             help='Length of ID (default: 8)')
    short_parser.add_argument('--count', '-n', type=int, default=1,
                             help='Number of IDs to generate')
    
    # Random string command
    random_parser = subparsers.add_parser('random', help='Generate random string')
    random_parser.add_argument('--length', '-l', type=int, default=32,
                              help='Length of string (default: 32)')
    random_parser.add_argument('--count', '-n', type=int, default=1,
                              help='Number of strings to generate')
    random_parser.add_argument('--no-upper', action='store_true',
                              help='Exclude uppercase letters')
    random_parser.add_argument('--no-lower', action='store_true',
                              help='Exclude lowercase letters')
    random_parser.add_argument('--no-digits', action='store_true',
                              help='Exclude digits')
    random_parser.add_argument('--special', action='store_true',
                              help='Include special characters')
    
    # NanoID command
    nanoid_parser = subparsers.add_parser('nanoid', help='Generate NanoID')
    nanoid_parser.add_argument('--size', '-s', type=int, default=21,
                              help='Size of NanoID (default: 21)')
    nanoid_parser.add_argument('--count', '-n', type=int, default=1,
                              help='Number of IDs to generate')
    
    # CUID command
    cuid_parser = subparsers.add_parser('cuid', help='Generate CUID')
    cuid_parser.add_argument('--count', '-n', type=int, default=1,
                            help='Number of CUIDs to generate')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate UUID')
    validate_parser.add_argument('uuid', help='UUID string to validate')
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse UUID')
    parse_parser.add_argument('uuid', help='UUID string to parse')
    
    # Slug command
    slug_parser = subparsers.add_parser('slug', help='Convert UUID to slug')
    slug_parser.add_argument('--uuid', help='UUID to convert (default: generate new)')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Generate batch of IDs')
    batch_parser.add_argument('--type', choices=['uuid', 'short', 'nanoid', 'cuid', 'random'],
                             default='uuid', help='Type of ID')
    batch_parser.add_argument('--count', '-n', type=int, default=10,
                             help='Number of IDs (default: 10)')
    batch_parser.add_argument('--output', '-o', help='Output file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    skill = UUIDGeneratorSkill()
    
    if args.command == 'uuid':
        for _ in range(args.count):
            u = skill.uuid(args.version)
            if args.uppercase:
                u = u.upper()
            print(u)
    
    elif args.command == 'short':
        for _ in range(args.count):
            print(skill.short_id(args.length))
    
    elif args.command == 'random':
        for _ in range(args.count):
            s = skill.random_string(
                length=args.length,
                use_uppercase=not args.no_upper,
                use_lowercase=not args.no_lower,
                use_digits=not args.no_digits,
                use_special=args.special
            )
            print(s)
    
    elif args.command == 'nanoid':
        for _ in range(args.count):
            print(skill.nanoid(args.size))
    
    elif args.command == 'cuid':
        for _ in range(args.count):
            print(skill.cuid())
    
    elif args.command == 'validate':
        is_valid = skill.validate(args.uuid)
        print("Valid" if is_valid else "Invalid")
        sys.exit(0 if is_valid else 1)
    
    elif args.command == 'parse':
        info = skill.parse(args.uuid)
        if info:
            print(f"UUID: {args.uuid}")
            print(f"Version: {info.version}")
            print(f"Variant: {info.variant}")
            print(f"Hex: {info.hex}")
            print(f"Integer: {info.int}")
            print(f"Bytes: {info.bytes.hex()}")
            if info.time:
                print(f"Timestamp: {info.time.isoformat()}")
        else:
            print(f"Invalid UUID: {args.uuid}")
            sys.exit(1)
    
    elif args.command == 'slug':
        slug = skill.slug(args.uuid if args.uuid else None)
        print(slug)
    
    elif args.command == 'batch':
        ids = []
        if args.type == 'uuid':
            ids = skill.batch_uuid(args.count)
        elif args.type == 'short':
            ids = [skill.short_id() for _ in range(args.count)]
        elif args.type == 'nanoid':
            ids = [skill.nanoid() for _ in range(args.count)]
        elif args.type == 'cuid':
            ids = [skill.cuid() for _ in range(args.count)]
        elif args.type == 'random':
            ids = [skill.alphanumeric() for _ in range(args.count)]
        
        if args.output:
            with open(args.output, 'w') as f:
                for id_str in ids:
                    f.write(id_str + '\n')
            print(f"Generated {args.count} {args.type} IDs to {args.output}")
        else:
            for id_str in ids:
                print(id_str)


if __name__ == '__main__':
    main()
