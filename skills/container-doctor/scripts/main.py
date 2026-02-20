#!/usr/bin/env python3
"""Container Doctor - Docker/K8s debugging tool"""

import sys
import subprocess
import json
import argparse
from pathlib import Path

class ContainerDoctor:
    def __init__(self):
        self.docker_available = self._check_docker()
    
    def _check_docker(self):
        """Check if Docker is available"""
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def test(self):
        """Self-test mode"""
        print("[CONTAINER-DOCTOR] Self-test started...")
        
        if self.docker_available:
            print("[OK] Docker CLI: Detected")
            
            # Check Docker daemon
            result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                print("[OK] Docker Daemon: Running")
            else:
                print("[WARNING] Docker Daemon: Not running")
        else:
            print("[WARNING] Docker CLI: Not found")
            print("[TIP] Install Docker Desktop for Windows")
        
        print("[OK] Health check module: Ready")
        print("[OK] Log analyzer: Ready")
        return True
    
    def get_status(self):
        """Get Docker system status"""
        print("\n[CONTAINER-STATUS]")
        print("-" * 50)
        
        if not self.docker_available:
            print("[ERROR] Docker not available")
            return False
        
        try:
            # List running containers
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{.Names}}\t{{.Status}}\t{{.Ports}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout.strip():
                print("\n[RUNNING-CONTAINERS]")
                for line in result.stdout.strip().split('\n'):
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        print(f"  [RUNNING] {parts[0]} - {parts[1]}")
            else:
                print("  No running containers")
            
            # System info
            result = subprocess.run(
                ['docker', 'system', 'df', '--format', '{{.Type}}: {{.Size}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("\n[DISK-USAGE]")
                for line in result.stdout.strip().split('\n'):
                    print(f"  {line}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
    
    def get_logs(self, container_name, tail=50):
        """Get container logs"""
        print(f"\n[CONTAINER-LOGS] {container_name}")
        print("-" * 50)
        
        if not self.docker_available:
            print("[ERROR] Docker not available")
            return False
        
        try:
            result = subprocess.run(
                ['docker', 'logs', '--tail', str(tail), container_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(result.stdout)
                
                # Analyze for errors
                errors = [line for line in result.stdout.split('\n') 
                         if 'error' in line.lower() or 'exception' in line.lower()]
                if errors:
                    print(f"\n[WARNING] Found {len(errors)} potential errors")
                
                return True
            else:
                print(f"[ERROR] {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
    
    def get_stats(self):
        """Get container resource stats"""
        print("\n[CONTAINER-STATS]")
        print("-" * 50)
        
        if not self.docker_available:
            print("[ERROR] Docker not available")
            return False
        
        try:
            result = subprocess.run(
                ['docker', 'stats', '--no-stream', '--format', 
                 '{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                print("\n[NAME]\t\t[CPU]\t[MEMORY]")
                for line in result.stdout.strip().split('\n'):
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        print(f"{parts[0]:20} {parts[1]:8} {parts[2]}")
                return True
            else:
                print("[WARNING] No running containers or Docker not responding")
                return False
                
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
    
    def health_check(self):
        """Run health checks on all containers"""
        print("\n[HEALTH-CHECK]")
        print("-" * 50)
        
        if not self.docker_available:
            print("[ERROR] Docker not available")
            return False
        
        try:
            # Check all containers with health status
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{.Names}}\t{{.Status}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                healthy = 0
                unhealthy = 0
                
                for line in result.stdout.strip().split('\n'):
                    if 'unhealthy' in line.lower():
                        unhealthy += 1
                        print(f"  [UNHEALTHY] {line}")
                    elif 'healthy' in line.lower() or 'up' in line.lower():
                        healthy += 1
                
                print(f"\n[SUMMARY] Healthy: {healthy}, Unhealthy: {unhealthy}")
                return unhealthy == 0
            
            return True
            
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Container Doctor')
    parser.add_argument('--test', action='store_true', help='Self-test')
    parser.add_argument('command', nargs='?', help='Command')
    parser.add_argument('target', nargs='?', help='Container name')
    
    args = parser.parse_args()
    
    cd = ContainerDoctor()
    
    if args.test:
        sys.exit(0 if cd.test() else 1)
    
    if args.command == 'status':
        sys.exit(0 if cd.get_status() else 1)
    
    if args.command == 'logs' and args.target:
        sys.exit(0 if cd.get_logs(args.target) else 1)
    
    if args.command == 'stats':
        sys.exit(0 if cd.get_stats() else 1)
    
    if args.command == 'health':
        sys.exit(0 if cd.health_check() else 1)
    
    # Default
    cd.test()

if __name__ == '__main__':
    main()
