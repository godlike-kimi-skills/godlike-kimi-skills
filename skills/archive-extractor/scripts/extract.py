#!/usr/bin/env python3
"""
Archive extraction script supporting multiple formats.
Usage: extract.py <archive_path> [output_dir] [--list]
"""

import sys
import os
import zipfile
import tarfile
import argparse
from pathlib import Path


def detect_format(archive_path: str) -> str:
    """Detect archive format from file extension."""
    ext = Path(archive_path).suffix.lower()
    name = Path(archive_path).name.lower()
    
    if name.endswith('.tar.gz') or name.endswith('.tgz'):
        return 'tar.gz'
    elif name.endswith('.tar.bz2') or name.endswith('.tbz2'):
        return 'tar.bz2'
    elif name.endswith('.tar.xz') or name.endswith('.txz'):
        return 'tar.xz'
    elif ext == '.zip':
        return 'zip'
    elif ext == '.rar':
        return 'rar'
    elif ext == '.7z':
        return '7z'
    elif ext == '.tar':
        return 'tar'
    else:
        return None


def list_zip_contents(archive_path: str):
    """List contents of a ZIP archive."""
    with zipfile.ZipFile(archive_path, 'r') as zf:
        print(f"Contents of {archive_path}:")
        print("-" * 50)
        for info in zf.infolist():
            size = f"{info.file_size:,}" if info.file_size < 1024*1024 else f"{info.file_size/1024/1024:.2f} MB"
            print(f"  {info.filename:<50} {size:>15}")
        print(f"\nTotal files: {len(zf.namelist())}")


def extract_zip(archive_path: str, output_dir: str):
    """Extract a ZIP archive."""
    with zipfile.ZipFile(archive_path, 'r') as zf:
        zf.extractall(output_dir)
        print(f"Extracted {len(zf.namelist())} files to {output_dir}")


def list_tar_contents(archive_path: str, mode: str):
    """List contents of a tar archive."""
    with tarfile.open(archive_path, mode) as tf:
        print(f"Contents of {archive_path}:")
        print("-" * 50)
        members = tf.getmembers()
        for member in members:
            size = f"{member.size:,}" if member.size < 1024*1024 else f"{member.size/1024/1024:.2f} MB"
            type_char = 'D' if member.isdir() else 'F'
            print(f"  [{type_char}] {member.name:<50} {size:>15}")
        print(f"\nTotal entries: {len(members)}")


def extract_tar(archive_path: str, output_dir: str, mode: str):
    """Extract a tar archive."""
    with tarfile.open(archive_path, mode) as tf:
        tf.extractall(output_dir)
        print(f"Extracted {len(tf.getmembers())} entries to {output_dir}")


def extract_with_7z(archive_path: str, output_dir: str, list_only: bool = False):
    """Extract or list using 7z command line tool."""
    import subprocess
    
    # Try to find 7z executable
    seven_z_paths = [
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe",
    ]
    
    seven_z = None
    for path in seven_z_paths:
        if os.path.exists(path):
            seven_z = path
            break
    
    if not seven_z:
        # Try to find in PATH
        try:
            result = subprocess.run(['where', '7z'], capture_output=True, text=True)
            if result.returncode == 0:
                seven_z = result.stdout.strip().split('\n')[0]
        except:
            pass
    
    if not seven_z:
        raise RuntimeError("7-Zip not found. Please install 7-Zip or use Python-native formats (zip, tar.gz).")
    
    if list_only:
        result = subprocess.run([seven_z, 'l', archive_path], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    else:
        os.makedirs(output_dir, exist_ok=True)
        result = subprocess.run([seven_z, 'x', archive_path, f'-o{output_dir}', '-y'], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        print(f"Extracted to {output_dir}")


def main():
    parser = argparse.ArgumentParser(description='Extract archive files')
    parser.add_argument('archive', help='Path to archive file')
    parser.add_argument('output', nargs='?', help='Output directory (optional)')
    parser.add_argument('--list', '-l', action='store_true', help='List contents without extracting')
    
    args = parser.parse_args()
    
    archive_path = os.path.abspath(args.archive)
    
    if not os.path.exists(archive_path):
        print(f"Error: File not found: {archive_path}", file=sys.stderr)
        sys.exit(1)
    
    # Detect format
    fmt = detect_format(archive_path)
    if not fmt:
        print(f"Error: Unsupported archive format: {archive_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Detected format: {fmt}")
    
    # Determine output directory
    if args.output:
        output_dir = os.path.abspath(args.output)
    else:
        output_dir = os.path.splitext(archive_path)[0]
    
    # Process based on format
    try:
        if fmt == 'zip':
            if args.list:
                list_zip_contents(archive_path)
            else:
                os.makedirs(output_dir, exist_ok=True)
                extract_zip(archive_path, output_dir)
                
        elif fmt in ('tar.gz', 'tgz'):
            if args.list:
                list_tar_contents(archive_path, 'r:gz')
            else:
                os.makedirs(output_dir, exist_ok=True)
                extract_tar(archive_path, output_dir, 'r:gz')
                
        elif fmt in ('tar.bz2', 'tbz2'):
            if args.list:
                list_tar_contents(archive_path, 'r:bz2')
            else:
                os.makedirs(output_dir, exist_ok=True)
                extract_tar(archive_path, output_dir, 'r:bz2')
                
        elif fmt in ('tar.xz', 'txz'):
            if args.list:
                list_tar_contents(archive_path, 'r:xz')
            else:
                os.makedirs(output_dir, exist_ok=True)
                extract_tar(archive_path, output_dir, 'r:xz')
                
        elif fmt == 'tar':
            if args.list:
                list_tar_contents(archive_path, 'r')
            else:
                os.makedirs(output_dir, exist_ok=True)
                extract_tar(archive_path, output_dir, 'r')
                
        elif fmt in ('rar', '7z'):
            extract_with_7z(archive_path, output_dir, args.list)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
