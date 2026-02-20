#!/usr/bin/env python3
"""
Hash Generator Skill - Cryptographic hash generation utility
Supports MD5, SHA family, HMAC, and file hashing
"""

import hashlib
import hmac
import os
from typing import Union, List, Dict, Optional
from pathlib import Path


class HashGeneratorSkill:
    """
    A comprehensive hash generation utility supporting:
    - MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512
    - SHA3-224, SHA3-256, SHA3-384, SHA3-512
    - HMAC (Hash-based Message Authentication Code)
    - File hashing for large files
    - Batch file processing
    """
    
    # Supported hash algorithms
    SUPPORTED_ALGORITHMS = [
        'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
        'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
        'blake2b', 'blake2s', 'shake_128', 'shake_256'
    ]
    
    # Secure algorithms (recommended for cryptographic use)
    SECURE_ALGORITHMS = ['sha256', 'sha384', 'sha512', 'sha3_256', 'sha3_512', 'blake2b']
    
    # Insecure algorithms (for compatibility only)
    INSECURE_ALGORITHMS = ['md5', 'sha1']
    
    def __init__(self):
        """Initialize the HashGeneratorSkill"""
        self._chunk_size = 8192  # 8KB chunks for file hashing
    
    def hash_string(self, data: Union[str, bytes], algorithm: str = 'sha256') -> str:
        """
        Generate hash of a string
        
        Args:
            data: String or bytes to hash
            algorithm: Hash algorithm (md5, sha256, sha512, etc.)
            
        Returns:
            Hexadecimal hash string
            
        Raises:
            ValueError: If algorithm is not supported
        """
        algorithm = algorithm.lower().replace('-', '_')
        
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Supported: {', '.join(self.SUPPORTED_ALGORITHMS)}"
            )
        
        # Convert string to bytes
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Handle shake algorithms (variable length)
        if algorithm.startswith('shake_'):
            hasher = hashlib.new(algorithm)
            hasher.update(data)
            # Return 32 bytes (64 hex chars) for shake
            return hasher.hexdigest(32)
        
        hasher = hashlib.new(algorithm)
        hasher.update(data)
        return hasher.hexdigest()
    
    def hash_file(self, file_path: str, algorithm: str = 'sha256') -> str:
        """
        Generate hash of a file (memory-efficient for large files)
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm
            
        Returns:
            Hexadecimal hash string
            
        Raises:
            ValueError: If algorithm is not supported
            FileNotFoundError: If file does not exist
        """
        algorithm = algorithm.lower().replace('-', '_')
        
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Supported: {', '.join(self.SUPPORTED_ALGORITHMS)}"
            )
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Handle shake algorithms
        if algorithm.startswith('shake_'):
            hasher = hashlib.new(algorithm)
        else:
            hasher = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(self._chunk_size):
                hasher.update(chunk)
        
        if algorithm.startswith('shake_'):
            return hasher.hexdigest(32)
        return hasher.hexdigest()
    
    def hmac_string(
        self, 
        data: Union[str, bytes], 
        key: Union[str, bytes], 
        algorithm: str = 'sha256'
    ) -> str:
        """
        Generate HMAC of a string
        
        Args:
            data: String or bytes to hash
            key: Secret key for HMAC
            algorithm: Hash algorithm
            
        Returns:
            Hexadecimal HMAC string
        """
        algorithm = algorithm.lower().replace('-', '_')
        
        # Convert to bytes
        if isinstance(data, str):
            data = data.encode('utf-8')
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        # Map algorithm names
        algo_map = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha224': hashlib.sha224,
            'sha256': hashlib.sha256,
            'sha384': hashlib.sha384,
            'sha512': hashlib.sha512,
        }
        
        if algorithm not in algo_map:
            raise ValueError(f"HMAC only supports: {', '.join(algo_map.keys())}")
        
        h = hmac.new(key, data, algo_map[algorithm])
        return h.hexdigest()
    
    def hmac_file(
        self, 
        file_path: str, 
        key: Union[str, bytes], 
        algorithm: str = 'sha256'
    ) -> str:
        """
        Generate HMAC of a file
        
        Args:
            file_path: Path to file
            key: Secret key for HMAC
            algorithm: Hash algorithm
            
        Returns:
            Hexadecimal HMAC string
        """
        algorithm = algorithm.lower().replace('-', '_')
        
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        algo_map = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha224': hashlib.sha224,
            'sha256': hashlib.sha256,
            'sha384': hashlib.sha384,
            'sha512': hashlib.sha512,
        }
        
        if algorithm not in algo_map:
            raise ValueError(f"HMAC only supports: {', '.join(algo_map.keys())}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        h = hmac.new(key, digestmod=algo_map[algorithm])
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(self._chunk_size):
                h.update(chunk)
        
        return h.hexdigest()
    
    def hash_bytes(self, data: bytes, algorithm: str = 'sha256') -> bytes:
        """
        Generate hash and return raw bytes
        
        Args:
            data: Bytes to hash
            algorithm: Hash algorithm
            
        Returns:
            Raw hash bytes
        """
        algorithm = algorithm.lower().replace('-', '_')
        
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        if algorithm.startswith('shake_'):
            hasher = hashlib.new(algorithm)
            hasher.update(data)
            return hasher.digest(32)
        
        hasher = hashlib.new(algorithm)
        hasher.update(data)
        return hasher.digest()
    
    def compare_hashes(self, hash1: str, hash2: str) -> bool:
        """
        Compare two hashes securely (constant-time comparison)
        
        Args:
            hash1: First hash
            hash2: Second hash
            
        Returns:
            True if hashes match
        """
        return hmac.compare_digest(hash1.lower(), hash2.lower())
    
    def verify_string(
        self, 
        data: Union[str, bytes], 
        expected_hash: str, 
        algorithm: str = 'sha256'
    ) -> bool:
        """
        Verify data against expected hash
        
        Args:
            data: Data to verify
            expected_hash: Expected hash value
            algorithm: Hash algorithm
            
        Returns:
            True if hash matches
        """
        computed = self.hash_string(data, algorithm)
        return self.compare_hashes(computed, expected_hash)
    
    def verify_file(
        self, 
        file_path: str, 
        expected_hash: str, 
        algorithm: str = 'sha256'
    ) -> bool:
        """
        Verify file against expected hash
        
        Args:
            file_path: Path to file
            expected_hash: Expected hash value
            algorithm: Hash algorithm
            
        Returns:
            True if hash matches
        """
        computed = self.hash_file(file_path, algorithm)
        return self.compare_hashes(computed, expected_hash)
    
    def batch_hash_files(
        self, 
        file_paths: List[str], 
        algorithm: str = 'sha256'
    ) -> Dict[str, str]:
        """
        Generate hashes for multiple files
        
        Args:
            file_paths: List of file paths
            algorithm: Hash algorithm
            
        Returns:
            Dictionary mapping file paths to hashes
        """
        results = {}
        for file_path in file_paths:
            try:
                results[file_path] = self.hash_file(file_path, algorithm)
            except Exception as e:
                results[file_path] = f"Error: {e}"
        return results
    
    def hash_directory(
        self, 
        directory: str, 
        algorithm: str = 'sha256',
        pattern: str = '*'
    ) -> Dict[str, str]:
        """
        Hash all files in a directory
        
        Args:
            directory: Directory path
            algorithm: Hash algorithm
            pattern: File pattern to match
            
        Returns:
            Dictionary mapping file paths to hashes
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        results = {}
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                try:
                    results[str(file_path)] = self.hash_file(str(file_path), algorithm)
                except Exception as e:
                    results[str(file_path)] = f"Error: {e}"
        return results
    
    def generate_checksum_file(
        self, 
        file_paths: List[str], 
        output_path: str,
        algorithm: str = 'sha256'
    ) -> str:
        """
        Generate a checksum file (similar to shasum)
        
        Args:
            file_paths: List of files to hash
            output_path: Output checksum file path
            algorithm: Hash algorithm
            
        Returns:
            Path to checksum file
        """
        hashes = self.batch_hash_files(file_paths, algorithm)
        
        with open(output_path, 'w') as f:
            for file_path, hash_value in hashes.items():
                if not hash_value.startswith("Error:"):
                    f.write(f"{hash_value}  {file_path}\n")
        
        return output_path
    
    def verify_checksum_file(self, checksum_path: str) -> Dict[str, bool]:
        """
        Verify files against a checksum file
        
        Args:
            checksum_path: Path to checksum file
            
        Returns:
            Dictionary mapping file paths to verification results
        """
        results = {}
        
        with open(checksum_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Parse line (format: "HASH  filepath")
                parts = line.split('  ', 1)
                if len(parts) == 2:
                    expected_hash, file_path = parts
                    try:
                        results[file_path] = self.verify_file(file_path, expected_hash)
                    except Exception:
                        results[file_path] = False
        
        return results
    
    def get_algorithm_info(self, algorithm: str) -> Dict:
        """
        Get information about a hash algorithm
        
        Args:
            algorithm: Algorithm name
            
        Returns:
            Dictionary with algorithm information
        """
        algorithm = algorithm.lower().replace('-', '_')
        
        info = {
            'name': algorithm,
            'supported': algorithm in self.SUPPORTED_ALGORITHMS,
            'secure': algorithm in self.SECURE_ALGORITHMS,
            'insecure': algorithm in self.INSECURE_ALGORITHMS,
        }
        
        # Get digest size if available
        if info['supported'] and not algorithm.startswith('shake_'):
            try:
                hasher = hashlib.new(algorithm)
                info['digest_size'] = hasher.digest_size * 2  # hex chars
                info['block_size'] = hasher.block_size
            except Exception:
                pass
        
        return info
    
    def list_algorithms(self) -> List[str]:
        """List all supported algorithms"""
        return self.SUPPORTED_ALGORITHMS.copy()


# CLI interface
if __name__ == '__main__':
    import sys
    import json
    
    skill = HashGeneratorSkill()
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <command> [args...]")
        print("Commands: string, file, hmac, verify, compare, batch, checksum")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == 'string' and len(sys.argv) >= 3:
            algo = sys.argv[3] if len(sys.argv) > 3 else 'sha256'
            result = skill.hash_string(sys.argv[2], algo)
            print(result)
        
        elif command == 'file' and len(sys.argv) >= 3:
            algo = sys.argv[3] if len(sys.argv) > 3 else 'sha256'
            result = skill.hash_file(sys.argv[2], algo)
            print(result)
        
        elif command == 'hmac' and len(sys.argv) >= 4:
            algo = sys.argv[4] if len(sys.argv) > 4 else 'sha256'
            result = skill.hmac_string(sys.argv[2], sys.argv[3], algo)
            print(result)
        
        elif command == 'verify' and len(sys.argv) >= 4:
            algo = sys.argv[4] if len(sys.argv) > 4 else 'sha256'
            result = skill.verify_file(sys.argv[2], sys.argv[3], algo)
            print(f"Verification: {'PASSED' if result else 'FAILED'}")
        
        elif command == 'compare' and len(sys.argv) >= 4:
            result = skill.compare_hashes(sys.argv[2], sys.argv[3])
            print(f"Match: {'YES' if result else 'NO'}")
        
        elif command == 'batch' and len(sys.argv) >= 3:
            files = sys.argv[2:]
            algo = 'sha256'
            # Check if last arg is an algorithm
            if files[-1] in skill.SUPPORTED_ALGORITHMS:
                algo = files.pop()
            results = skill.batch_hash_files(files, algo)
            print(json.dumps(results, indent=2))
        
        elif command == 'checksum' and len(sys.argv) >= 4:
            files = sys.argv[3:]
            result = skill.generate_checksum_file(files, sys.argv[2])
            print(f"Checksum file created: {result}")
        
        elif command == 'info' and len(sys.argv) >= 3:
            info = skill.get_algorithm_info(sys.argv[2])
            print(json.dumps(info, indent=2))
        
        elif command == 'list':
            print("Supported algorithms:")
            for algo in skill.SUPPORTED_ALGORITHMS:
                secure = " [SECURE]" if algo in skill.SECURE_ALGORITHMS else ""
                print(f"  - {algo}{secure}")
        
        else:
            print("Invalid command or arguments")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
