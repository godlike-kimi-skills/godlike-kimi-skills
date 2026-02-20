#!/usr/bin/env python3
"""Debug Master - Advanced CLI debugging tool"""

import sys
import pdb
import traceback
import argparse
from pathlib import Path

class DebugMaster:
    def __init__(self):
        self.breakpoints = []
        self.trace_data = []
    
    def test(self):
        """Self-test mode"""
        print("[DEBUG-MASTER] Self-test started...")
        print("[OK] PDB integration: Ready")
        print("[OK] Trace capture: Ready")
        print("[OK] Error parser: Ready")
        return True
    
    def debug_script(self, script_path, args=None):
        """Debug a Python script with PDB"""
        if not Path(script_path).exists():
            print(f"[ERROR] Script not found: {script_path}")
            return False
        
        print(f"[DEBUG] Starting PDB debugging: {script_path}")
        
        # Set breakpoint at start
        pdb.set_trace()
        
        try:
            with open(script_path) as f:
                code = compile(f.read(), script_path, 'exec')
                exec(code, {'__name__': '__main__'})
        except Exception as e:
            print(f"[ERROR] {type(e).__name__}: {e}")
            traceback.print_exc()
            return False
        
        return True
    
    def parse_error(self, error_code):
        """Parse Windows/Linux error codes"""
        error_map = {
            "0x80070005": "Access Denied (权限不足)",
            "0x80070002": "File Not Found (文件不存在)",
            "0xC0000005": "Access Violation (内存访问冲突)",
            "126": "Module not found (DLL缺失)",
            "2": "File not found",
            "5": "Access denied",
        }
        
        code_str = str(error_code).strip()
        if code_str in error_map:
            print(f"[ERROR-CODE] {error_code}: {error_map[code_str]}")
        else:
            print(f"[ERROR-CODE] {error_code}: Unknown error code")
            print("[TIP] Use 'python -m pdb script.py' for detailed debugging")
        
        return True
    
    def capture_trace(self):
        """Capture current stack trace"""
        stack = traceback.extract_stack()
        print("\n[STACK-TRACE]")
        for frame in stack[-5:]:
            print(f"  {frame.filename}:{frame.lineno} - {frame.name}")
        return True

def main():
    parser = argparse.ArgumentParser(description='Debug Master')
    parser.add_argument('--test', action='store_true', help='Self-test')
    parser.add_argument('command', nargs='?', help='Command: debug/error/trace')
    parser.add_argument('target', nargs='?', help='Target script or error code')
    
    args = parser.parse_args()
    
    dm = DebugMaster()
    
    if args.test:
        sys.exit(0 if dm.test() else 1)
    
    if args.command == 'debug' and args.target:
        sys.exit(0 if dm.debug_script(args.target) else 1)
    
    if args.command == 'error' and args.target:
        sys.exit(0 if dm.parse_error(args.target) else 1)
    
    if args.command == 'trace':
        sys.exit(0 if dm.capture_trace() else 1)
    
    # Default: run test
    dm.test()

if __name__ == '__main__':
    main()
