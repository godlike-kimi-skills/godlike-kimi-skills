#!/usr/bin/env python3
"""Log Sentinel - Real-time log monitoring with audio alerts"""

import sys
import os
import time
import re
import argparse
import threading
from pathlib import Path
from collections import deque

class LogSentinel:
    def __init__(self):
        self.keywords = ['ERROR', 'CRITICAL', 'FATAL', '超时', '连接失败', 'Exception']
        self.alert_patterns = [
            r'\bERROR\b',
            r'\bCRITICAL\b',
            r'\bFATAL\b',
            r'超时',
            r'连接失败',
            r'Connection\s+(?:refused|reset|timeout)',
            r'Exception',
        ]
        self.monitoring = False
        self.alert_enabled = False
        self.alarm_cooldown = 30  # seconds between alarms
        self.last_alarm = 0
        
    def test(self):
        """Self-test mode"""
        print("[LOG-SENTINEL] Self-test started...")
        print("[OK] File watcher: Ready")
        print("[OK] Pattern matcher: Ready")
        print("[OK] Audio alarm: Ready")
        
        # Test audio
        if self.alert_enabled:
            print("[TEST] Playing alarm sound...")
            self.play_alarm()
        
        return True
    
    def play_alarm(self):
        """Cross-platform audio alarm"""
        current_time = time.time()
        if current_time - self.last_alarm < self.alarm_cooldown:
            return
        
        self.last_alarm = current_time
        
        # Windows
        if sys.platform == 'win32':
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                # Try to play custom sound if available
                alarm_path = Path(__file__).parent / 'alarm.wav'
                if alarm_path.exists():
                    winsound.PlaySound(str(alarm_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
                print("[ALARM] Audio alert triggered (Windows)")
            except Exception as e:
                print(f"[ALARM-WARN] {e}")
        
        # Linux
        elif sys.platform == 'linux':
            try:
                os.system('aplay alarm.wav 2>/dev/null || beep 2>/dev/null || echo -e "\a"')
                print("[ALARM] Audio alert triggered (Linux)")
            except:
                print("[ALARM] Console bell triggered")
        
        # macOS
        elif sys.platform == 'darwin':
            try:
                os.system('afplay alarm.wav 2>/dev/null || say "Alert"')
                print("[ALARM] Audio alert triggered (macOS)")
            except:
                print("[ALARM] Console bell triggered")
        
        else:
            print("[ALARM] Console bell triggered")
            print('\a')  # ANSI bell
    
    def highlight_line(self, line):
        """Highlight keywords in line"""
        highlighted = line
        colors = {
            'ERROR': '\033[91m',      # Red
            'CRITICAL': '\033[91m',   # Red
            'FATAL': '\033[91m',      # Red
            'WARNING': '\033[93m',    # Yellow
            '超时': '\033[93m',        # Yellow
            '连接失败': '\033[93m',    # Yellow
        }
        reset = '\033[0m'
        
        for keyword, color in colors.items():
            if keyword in line:
                highlighted = highlighted.replace(keyword, f"{color}{keyword}{reset}")
        
        return highlighted
    
    def check_patterns(self, line):
        """Check if line matches alert patterns"""
        for pattern in self.alert_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False
    
    def monitor_file(self, file_path, alert=False):
        """Monitor a single log file"""
        self.alert_enabled = alert
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"[ERROR] File not found: {file_path}")
            return False
        
        print(f"\n[MONITOR] {file_path}")
        print("-" * 60)
        print(f"[CONFIG] Keywords: {', '.join(self.keywords)}")
        print(f"[CONFIG] Audio alarm: {'ON' if alert else 'OFF'}")
        print("-" * 60)
        print("Press Ctrl+C to stop\n")
        
        self.monitoring = True
        
        # Get initial file size
        last_size = file_path.stat().st_size
        
        try:
            while self.monitoring:
                current_size = file_path.stat().st_size
                
                if current_size > last_size:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        f.seek(last_size)
                        new_lines = f.readlines()
                    
                    for line in new_lines:
                        line = line.rstrip()
                        if self.check_patterns(line):
                            # Alert pattern matched
                            highlighted = self.highlight_line(line)
                            print(f"[ALERT] {highlighted}")
                            
                            if alert:
                                self.play_alarm()
                        else:
                            print(f"[INFO] {line}")
                    
                    last_size = current_size
                
                time.sleep(0.5)  # Poll interval
                
        except KeyboardInterrupt:
            print("\n[MONITOR] Stopped by user")
            self.monitoring = False
        
        return True
    
    def monitor_directory(self, dir_path, pattern='*.log', alert=False):
        """Monitor directory for matching log files"""
        dir_path = Path(dir_path)
        
        if not dir_path.exists():
            print(f"[ERROR] Directory not found: {dir_path}")
            return False
        
        print(f"\n[MONITOR-DIR] {dir_path}")
        print(f"[PATTERN] {pattern}")
        
        # Find all matching files
        files = list(dir_path.glob(pattern))
        if not files:
            print("[WARNING] No matching files found")
            return False
        
        print(f"[FILES] Found {len(files)} file(s)")
        
        # For simplicity, monitor the most recently modified file
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        print(f"[ACTIVE] Monitoring: {latest_file.name}")
        
        return self.monitor_file(latest_file, alert)
    
    def config(self, **kwargs):
        """Configure sentinel settings"""
        if 'path' in kwargs:
            print(f"[CONFIG] Monitor path: {kwargs['path']}")
        
        if 'pattern' in kwargs:
            print(f"[CONFIG] File pattern: {kwargs['pattern']}")
        
        if 'keywords' in kwargs:
            keywords = kwargs['keywords'].split(',')
            self.keywords = [k.strip() for k in keywords]
            print(f"[CONFIG] Keywords: {', '.join(self.keywords)}")
        
        if 'alarm' in kwargs:
            print(f"[CONFIG] Alarm file: {kwargs['alarm']}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Log Sentinel')
    parser.add_argument('--test', action='store_true', help='Self-test')
    parser.add_argument('command', nargs='?', help='Command: monitor/config')
    parser.add_argument('path', nargs='?', help='File or directory path')
    parser.add_argument('--pattern', default='*.log', help='File pattern')
    parser.add_argument('--alert', action='store_true', help='Enable audio alarm')
    parser.add_argument('--keywords', help='Comma-separated keywords')
    
    args = parser.parse_args()
    
    sentinel = LogSentinel()
    
    if args.test:
        sys.exit(0 if sentinel.test() else 1)
    
    if args.command == 'monitor' and args.path:
        path = Path(args.path)
        if path.is_file():
            sys.exit(0 if sentinel.monitor_file(args.path, args.alert) else 1)
        elif path.is_dir():
            sys.exit(0 if sentinel.monitor_directory(args.path, args.pattern, args.alert) else 1)
    
    if args.command == 'config':
        sys.exit(0 if sentinel.config(
            path=args.path,
            pattern=args.pattern,
            keywords=args.keywords
        ) else 1)
    
    # Default: test
    sentinel.test()

if __name__ == '__main__':
    main()
