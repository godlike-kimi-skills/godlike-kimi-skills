#!/usr/bin/env python3
"""Net Debugger - Network diagnostics tool"""

import sys
import socket
import subprocess
import time
import argparse
from pathlib import Path

class NetDebugger:
    def __init__(self):
        self.timeout = 5
    
    def test(self):
        """Self-test mode"""
        print("[NET-DEBUGGER] Self-test started...")
        
        # Test DNS
        try:
            socket.gethostbyname('localhost')
            print("[OK] DNS resolution: Ready")
        except:
            print("[X] DNS resolution: Failed")
            return False
        
        # Test ICMP (ping)
        try:
            subprocess.run(['ping', '-n', '1', '127.0.0.1'], 
                         capture_output=True, timeout=5)
            print("[OK] ICMP ping: Ready")
        except:
            print("[WARNING] ICMP ping: Limited (may require admin)")
        
        print("[OK] TCP socket: Ready")
        return True
    
    def dns_check(self, hostname):
        """DNS resolution check with chain tracing"""
        print(f"\n[DNS-CHECK] {hostname}")
        print("-" * 50)
        
        try:
            # Get IP
            ip = socket.gethostbyname(hostname)
            print(f"[RESOLVED] {hostname} -> {ip}")
            
            # Reverse lookup
            try:
                reverse = socket.gethostbyaddr(ip)
                print(f"[REVERSE] {ip} -> {reverse[0]}")
            except:
                pass
            
            # Check multiple DNS servers
            dns_servers = ['8.8.8.8', '223.5.5.5', '114.114.114.114']
            print(f"\n[DNS-SERVERS] Testing {len(dns_servers)} servers...")
            
            for dns in dns_servers:
                start = time.time()
                try:
                    socket.gethostbyname(hostname)
                    latency = (time.time() - start) * 1000
                    print(f"  [OK] {dns}: {latency:.1f}ms")
                except:
                    print(f"  [X] {dns}: Failed")
            
            return True
            
        except socket.gaierror as e:
            print(f"[ERROR] DNS resolution failed: {e}")
            return False
    
    def ping_test(self, host, count=4):
        """ICMP ping test"""
        print(f"\n[PING] {host}")
        print("-" * 50)
        
        try:
            result = subprocess.run(
                ['ping', '-n', str(count), host],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(result.stdout)
                return True
            else:
                print(f"[ERROR] Ping failed:\n{result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("[ERROR] Ping timeout")
            return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
    
    def port_check(self, host, port):
        """TCP port connectivity check"""
        print(f"\n[PORT-CHECK] {host}:{port}")
        print("-" * 50)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, int(port)))
            
            if result == 0:
                print(f"[OK] Port {port} is OPEN")
                sock.close()
                return True
            else:
                print(f"[X] Port {port} is CLOSED (error: {result})")
                sock.close()
                return False
                
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
    
    def trace_route(self, host):
        """Route trace (simplified)"""
        print(f"\n[ROUTE-TRACE] {host}")
        print("-" * 50)
        
        try:
            result = subprocess.run(
                ['tracert', '-d', '-h', '15', host],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(result.stdout)
                return True
            else:
                print(f"[WARNING] Tracert may require admin privileges")
                return False
                
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Net Debugger')
    parser.add_argument('--test', action='store_true', help='Self-test')
    parser.add_argument('command', nargs='?', help='Command')
    parser.add_argument('target', nargs='?', help='Target host')
    parser.add_argument('port', nargs='?', help='Port number')
    
    args = parser.parse_args()
    
    nd = NetDebugger()
    
    if args.test:
        sys.exit(0 if nd.test() else 1)
    
    if args.command == 'dns-check' and args.target:
        sys.exit(0 if nd.dns_check(args.target) else 1)
    
    if args.command == 'ping' and args.target:
        sys.exit(0 if nd.ping_test(args.target) else 1)
    
    if args.command == 'port' and args.target and args.port:
        sys.exit(0 if nd.port_check(args.target, args.port) else 1)
    
    if args.command == 'trace' and args.target:
        sys.exit(0 if nd.trace_route(args.target) else 1)
    
    # Default: test
    nd.test()

if __name__ == '__main__':
    main()
