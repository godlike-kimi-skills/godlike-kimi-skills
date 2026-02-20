#!/usr/bin/env python3
"""
System resource monitor v2.0 for Kbot.
Features: Resource monitoring, Circuit Breaker, Health Checks, Agent Management
Usage: monitor.py <command> [options]
"""

import sys
import psutil
import argparse
import time
import json
import os
from datetime import datetime
from collections import deque
from pathlib import Path

# System Resource Reservation (硬性约束 - 必须预留 25% 给 Windows 系统)
SYSTEM_RESERVE = {
    "cpu_cores": 4,           # 预留 4 核
    "memory_gb": 8,           # 预留 8 GB
    "reserve_percent": 25     # 预留 25%
}

# Resource thresholds (基于系统总容量，不是可用容量)
THRESHOLDS = {
    "healthy": 25,     # < 25% - 系统预留充足
    "normal": 50,      # 25-50% - 正常
    "warning": 75,     # 50-75% - 接近红线
    "danger": 87,      # > 75% - 超过系统预留
    "critical": 95     # > 87% - 紧急
}

MAX_AGENTS_PER_CORE = 1
MAX_CONCURRENT_AGENTS = 12  # 16核 - 4核预留 = 12核可用
HISTORY_LENGTH = 100  # Keep last 100 readings

# Per-agent resource limit
MAX_AGENT_MEMORY_GB = 2  # 每个 Agent 最多 2GB

# State files
STATE_DIR = Path("D:/kimi/memory/system-monitor")
STATE_DIR.mkdir(parents=True, exist_ok=True)
CIRCUIT_FILE = STATE_DIR / "circuit_breaker.json"
HEALTH_FILE = STATE_DIR / "health_status.json"
HISTORY_FILE = STATE_DIR / "resource_history.json"


class CircuitBreaker:
    """Circuit Breaker pattern implementation for fault tolerance."""
    
    STATES = ["CLOSED", "OPEN", "HALF_OPEN"]
    
    def __init__(self, failure_threshold=5, recovery_timeout=60, half_open_max_calls=3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.load()
    
    def load(self):
        """Load circuit breaker state from file."""
        if CIRCUIT_FILE.exists():
            try:
                data = json.loads(CIRCUIT_FILE.read_text())
                self.state = data.get("state", "CLOSED")
                self.failure_count = data.get("failure_count", 0)
                self.last_failure_time = data.get("last_failure_time")
                self.success_count = data.get("success_count", 0)
            except:
                self.reset()
        else:
            self.reset()
    
    def save(self):
        """Save circuit breaker state to file."""
        data = {
            "state": self.state,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "success_count": self.success_count,
            "updated_at": datetime.now().isoformat()
        }
        CIRCUIT_FILE.write_text(json.dumps(data, indent=2))
    
    def reset(self):
        """Reset circuit breaker to CLOSED state."""
        self.state = "CLOSED"
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
        self.save()
    
    def can_execute(self):
        """Check if execution is allowed."""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed > self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    self.success_count = 0
                    self.save()
                    return True
            return False
        elif self.state == "HALF_OPEN":
            return self.success_count < self.half_open_max_calls
        return False
    
    def record_success(self):
        """Record successful execution."""
        if self.state == "HALF_OPEN":
            self.success_count += 1
            if self.success_count >= self.half_open_max_calls:
                self.reset()
        else:
            self.failure_count = max(0, self.failure_count - 1)
        self.save()
    
    def record_failure(self):
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == "HALF_OPEN":
            self.state = "OPEN"
        elif self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
        
        self.save()
    
    def get_status(self):
        """Get circuit breaker status."""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "can_execute": self.can_execute()
        }


class ResourceHistory:
    """Track resource usage history for trend analysis."""
    
    def __init__(self, max_length=HISTORY_LENGTH):
        self.max_length = max_length
        self.cpu_history = deque(maxlen=max_length)
        self.memory_history = deque(maxlen=max_length)
        self.load()
    
    def load(self):
        """Load history from file."""
        if HISTORY_FILE.exists():
            try:
                data = json.loads(HISTORY_FILE.read_text())
                self.cpu_history = deque(data.get("cpu", []), maxlen=self.max_length)
                self.memory_history = deque(data.get("memory", []), maxlen=self.max_length)
            except:
                pass
    
    def save(self):
        """Save history to file."""
        data = {
            "cpu": list(self.cpu_history),
            "memory": list(self.memory_history),
            "updated_at": datetime.now().isoformat()
        }
        HISTORY_FILE.write_text(json.dumps(data, indent=2))
    
    def record(self, cpu_percent, memory_percent):
        """Record a new reading."""
        timestamp = datetime.now().isoformat()
        self.cpu_history.append({"time": timestamp, "value": cpu_percent})
        self.memory_history.append({"time": timestamp, "value": memory_percent})
        self.save()
    
    def get_trend(self, window=10):
        """Get resource usage trend (increasing/decreasing/stable)."""
        if len(self.memory_history) < window:
            return "INSUFFICIENT_DATA"
        
        recent = list(self.memory_history)[-window:]
        values = [r["value"] for r in recent]
        
        # Simple linear trend
        first_half = sum(values[:window//2]) / (window//2)
        second_half = sum(values[window//2:]) / (window - window//2)
        
        diff = second_half - first_half
        if diff > 5:
            return "INCREASING"
        elif diff < -5:
            return "DECREASING"
        return "STABLE"
    
    def predict_critical(self):
        """Predict if system will hit critical memory soon."""
        if len(self.memory_history) < 20:
            return False, "insufficient_data"
        
        recent = list(self.memory_history)[-20:]
        values = [r["value"] for r in recent]
        
        # Check if consistently increasing
        trend = self.get_trend(10)
        current = values[-1]
        
        if trend == "INCREASING" and current > 70:
            return True, f"trending_up (current: {current:.1f}%)"
        return False, trend


class HealthChecker:
    """Health check management for agents."""
    
    def __init__(self):
        self.checks = {}
        self.load()
    
    def load(self):
        """Load health status from file."""
        if HEALTH_FILE.exists():
            try:
                self.checks = json.loads(HEALTH_FILE.read_text())
            except:
                self.checks = {}
    
    def save(self):
        """Save health status to file."""
        HEALTH_FILE.write_text(json.dumps(self.checks, indent=2))
    
    def register(self, agent_id, check_type="heartbeat", interval=60):
        """Register a new health check."""
        self.checks[agent_id] = {
            "type": check_type,
            "interval": interval,
            "last_check": datetime.now().isoformat(),
            "status": "HEALTHY",
            "consecutive_failures": 0
        }
        self.save()
    
    def update(self, agent_id, status="HEALTHY"):
        """Update health check status."""
        if agent_id not in self.checks:
            self.register(agent_id)
        
        self.checks[agent_id]["last_check"] = datetime.now().isoformat()
        
        if status == "HEALTHY":
            self.checks[agent_id]["consecutive_failures"] = 0
            self.checks[agent_id]["status"] = "HEALTHY"
        else:
            self.checks[agent_id]["consecutive_failures"] += 1
            if self.checks[agent_id]["consecutive_failures"] >= 3:
                self.checks[agent_id]["status"] = "UNHEALTHY"
        
        self.save()
    
    def check_all(self):
        """Run health checks on all registered agents."""
        results = []
        now = datetime.now()
        
        for agent_id, check in self.checks.items():
            last_check = datetime.fromisoformat(check["last_check"])
            elapsed = (now - last_check).total_seconds()
            
            if elapsed > check["interval"] * 2:
                status = "STALE"
            else:
                status = check["status"]
            
            results.append({
                "agent_id": agent_id,
                "status": status,
                "last_check": check["last_check"],
                "elapsed_seconds": int(elapsed)
            })
        
        return results


# Global instances
circuit_breaker = CircuitBreaker()
resource_history = ResourceHistory()
health_checker = HealthChecker()


def get_system_info():
    """Get current system resource usage with system reservation info."""
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    memory_used_gb = memory.used / (1024**3)
    memory_total_gb = memory.total / (1024**3)
    memory_available_gb = memory.available / (1024**3)
    
    disk = psutil.disk_usage('D:\\')
    disk_percent = disk.percent
    
    # Calculate available resources for agents (total - system reserve)
    available_cores = max(1, cpu_count - SYSTEM_RESERVE["cpu_cores"])
    available_memory_gb = max(4, memory_total_gb - SYSTEM_RESERVE["memory_gb"])
    
    # Record in history
    resource_history.record(cpu_percent, memory_percent)
    
    return {
        "cpu": {
            "percent": cpu_percent,
            "cores": cpu_count,
            "cores_reserved": SYSTEM_RESERVE["cpu_cores"],
            "cores_available": available_cores,
            "max_agents": min(available_cores, MAX_CONCURRENT_AGENTS)
        },
        "memory": {
            "percent": memory_percent,
            "used_gb": round(memory_used_gb, 2),
            "total_gb": round(memory_total_gb, 2),
            "available_gb": round(memory_available_gb, 2),
            "reserved_gb": SYSTEM_RESERVE["memory_gb"],
            "available_for_agents_gb": round(available_memory_gb, 2),
            "status": get_memory_status(memory_percent)
        },
        "disk": {
            "percent": disk_percent
        },
        "system_reserve": SYSTEM_RESERVE
    }


def get_memory_status(percent):
    """Get memory status based on percentage with system reserve consideration.
    
    Thresholds based on total system memory:
    - < 25% (8GB): Healthy, plenty of system reserve
    - 25-50% (8-16GB): Normal operation
    - 50-75% (16-24GB): Approaching system reserve limit
    - > 75% (>24GB): Danger, exceeded system reserve
    - > 87% (>28GB): Critical, system may become unresponsive
    """
    if percent < THRESHOLDS["healthy"]:
        return ("healthy", "[OK]", "System reserve healthy, OK to spawn")
    elif percent < THRESHOLDS["normal"]:
        return ("normal", "[OK]", "Normal operation, system reserve OK")
    elif percent < THRESHOLDS["warning"]:
        return ("warning", "[!]", "Approaching system reserve limit, caution")
    elif percent < THRESHOLDS["danger"]:
        return ("danger", "[DANGER]", "STOP: Exceeded system reserve!")
    else:
        return ("critical", "[EMERGENCY]", "EMERGENCY: System becoming unresponsive!")


def get_current_agent_count():
    """Get current number of running agents."""
    count = 0
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'kimi' in cmdline.lower() or 'python' in cmdline.lower():
                count += 1
        except:
            pass
    return max(1, count)


def show_status():
    """Show comprehensive system status with system reserve info."""
    info = get_system_info()
    memory_status = info["memory"]["status"]
    current_agents = get_current_agent_count()
    max_agents = info["cpu"]["max_agents"]
    reserve = info['system_reserve']
    
    # Get trend
    trend = resource_history.get_trend()
    will_be_critical, prediction_reason = resource_history.predict_critical()
    
    # Get circuit breaker status
    cb_status = circuit_breaker.get_status()
    
    # Calculate system reserve status
    mem_reserve_used = (info['memory']['used_gb'] / info['memory']['total_gb'] * 100) if info['memory']['total_gb'] > 0 else 0
    reserve_status = "OK" if mem_reserve_used < 75 else "WARNING" if mem_reserve_used < 87 else "CRITICAL"
    
    print(f"\n[STATS] Kbot System Monitor v2.0")
    print(f"=================================")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"")
    print(f"[SYSTEM RESERVE - PROTECTED]")
    print(f"   CPU:  {reserve['cpu_cores']} cores reserved for Windows")
    print(f"   Mem:  {reserve['memory_gb']} GB reserved for Windows")
    print(f"   Rule: Always keep {reserve['reserve_percent']}% free for system stability")
    print(f"")
    print(f"[CPU]")
    print(f"   Usage:   {info['cpu']['percent']}%")
    print(f"   Total:   {info['cpu']['cores']} cores")
    print(f"   Reserve: {reserve['cpu_cores']} cores (for Windows)")
    print(f"   Agents:  {info['cpu']['cores_available']} cores available")
    print(f"   Max:     {max_agents} concurrent agents")
    print(f"")
    print(f"[MEMORY]")
    print(f"   Usage:    {info['memory']['percent']}% {memory_status[1]}")
    print(f"   Total:    {info['memory']['total_gb']} GB")
    print(f"   Used:     {info['memory']['used_gb']} GB")
    print(f"   Reserve:  {reserve['memory_gb']} GB (for Windows)")
    print(f"   Agents:   {info['memory']['available_for_agents_gb']} GB available")
    print(f"   Status:   {memory_status[0].upper()}")
    print(f"   Trend:    {trend}")
    if will_be_critical:
        print(f"   [!] WARNING: May hit critical soon ({prediction_reason})")
    print(f"")
    print(f"[DISK] (D:)")
    print(f"   Usage: {info['disk']['percent']}%")
    print(f"")
    print(f"[AGENTS]")
    print(f"   Running: {current_agents}/{max_agents}")
    print(f"   Slots:   {max(max_agents - current_agents, 0)} available")
    print(f"")
    print(f"[CIRCUIT BREAKER]")
    print(f"   State: {cb_status['state']}")
    print(f"   Failures: {cb_status['failure_count']}")
    print(f"   Can Execute: {cb_status['can_execute']}")
    print(f"=================================")
    print(f"System Reserve Status: {reserve_status}")
    print(f"=================================\n")


def check_can_spawn():
    """Check if it's safe to spawn a new subagent with system reserve consideration."""
    # Check circuit breaker first
    if not circuit_breaker.can_execute():
        print(f"\n[CIRCUIT BREAKER] Blocking spawn request")
        print(f"State: {circuit_breaker.state}")
        print(f"Please wait or reset circuit breaker\n")
        return False
    
    info = get_system_info()
    memory_status = info["memory"]["status"]
    current_agents = get_current_agent_count()
    max_agents = info["cpu"]["max_agents"]
    
    # System reserve info
    reserve = info['system_reserve']
    cpu_available = info['cpu']['cores_available']
    mem_available = info['memory']['available_for_agents_gb']
    
    print(f"\n[CHECK] Spawn Check (with System Reserve)")
    print(f"========================")
    print(f"CPU: {info['cpu']['percent']}% ({info['cpu']['cores']} total cores)")
    print(f"     Reserved: {reserve['cpu_cores']} cores | Available for Agents: {cpu_available} cores")
    print(f"Memory: {info['memory']['percent']}% ({info['memory']['used_gb']}/{info['memory']['total_gb']} GB)")
    print(f"        Reserved: {reserve['memory_gb']} GB | Available for Agents: {mem_available} GB")
    print(f"Status: {memory_status[1]} {memory_status[0].upper()}")
    print(f"Agents: {current_agents}/{max_agents} (max based on available cores)")
    print(f"========================\n")
    
    # Check memory - CRITICAL: Must not exceed system reserve
    if memory_status[0] in ["danger", "critical"]:
        print(f"[X] CANNOT SPAWN: System memory usage too high ({info['memory']['percent']}%)")
        print(f"   System reserve ({reserve['memory_gb']} GB) may be compromised!")
        print(f"   Windows system may become unresponsive!")
        circuit_breaker.record_failure()
        return False
    
    if memory_status[0] == "warning":
        print(f"[!] WARNING: Memory at {info['memory']['percent']}%")
        print(f"    Approaching system reserve limit. Spawn with caution.")
    
    # Check CPU/concurrency
    if current_agents >= max_agents:
        print(f"[X] CANNOT SPAWN: Max agents reached ({current_agents}/{max_agents})")
        print(f"   All available CPU cores ({cpu_available}) are in use.")
        print(f"   System reserve: {reserve['cpu_cores']} cores must remain free.")
        return False
    
    # Additional safety check - ensure we're not close to per-agent memory limit
    if mem_available / max(1, (max_agents - current_agents)) < MAX_AGENT_MEMORY_GB:
        print(f"[!] WARNING: Limited memory per agent")
        print(f"    Each agent may have less than {MAX_AGENT_MEMORY_GB}GB available")
    
    print(f"[OK] OK TO SPAWN")
    print(f"   Can spawn {max_agents - current_agents} more agent(s)")
    print(f"   System reserve protected: {reserve['cpu_cores']} cores, {reserve['memory_gb']} GB")
    circuit_breaker.record_success()
    return True


def watch_resources(interval=5):
    """Continuously watch system resources."""
    print(f"\n[WATCH] Monitoring (every {interval}s)...")
    print(f"Press Ctrl+C to stop\n")
    
    try:
        while True:
            info = get_system_info()
            memory_status = info["memory"]["status"]
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            # Prediction
            will_be_critical, _ = resource_history.predict_critical()
            
            print(f"[{timestamp}] CPU: {info['cpu']['percent']:5.1f}% | "
                  f"Mem: {info['memory']['percent']:5.1f}% {memory_status[1]} | "
                  f"Agents: {get_current_agent_count()}/{info['cpu']['max_agents']}", end="")
            
            if will_be_critical:
                print(" [!] TRENDING TO CRITICAL")
            elif memory_status[0] in ["danger", "critical"]:
                print(f" [!] {memory_status[0].upper()}")
            else:
                print()
            
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\n[STOP] Monitoring stopped.")


def main():
    parser = argparse.ArgumentParser(description='System resource monitor v2.0 for Kbot')
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Basic commands
    subparsers.add_parser('status', help='Show system status')
    subparsers.add_parser('can-spawn', help='Check if safe to spawn subagent')
    
    watch_parser = subparsers.add_parser('watch', help='Continuous monitoring')
    watch_parser.add_argument('--interval', '-i', type=int, default=5)
    
    # Circuit breaker commands
    subparsers.add_parser('circuit-status', help='Show circuit breaker status')
    subparsers.add_parser('circuit-reset', help='Reset circuit breaker')
    subparsers.add_parser('circuit-trip', help='Manually trip circuit breaker')
    
    # Health check commands
    health_parser = subparsers.add_parser('health-check', help='Run health checks')
    health_parser.add_argument('--agent', help='Check specific agent')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        show_status()
    elif args.command == 'can-spawn':
        can_spawn = check_can_spawn()
        sys.exit(0 if can_spawn else 1)
    elif args.command == 'watch':
        watch_resources(args.interval)
    elif args.command == 'circuit-status':
        status = circuit_breaker.get_status()
        print(f"\n[CIRCUIT BREAKER]")
        print(f"State: {status['state']}")
        print(f"Failures: {status['failure_count']}")
        print(f"Success: {status['success_count']}")
        print(f"Can Execute: {status['can_execute']}\n")
    elif args.command == 'circuit-reset':
        circuit_breaker.reset()
        print("[OK] Circuit breaker reset to CLOSED")
    elif args.command == 'circuit-trip':
        circuit_breaker.record_failure()
        print(f"[!] Circuit breaker tripped. State: {circuit_breaker.state}")
    elif args.command == 'health-check':
        if args.agent:
            health_checker.update(args.agent)
            print(f"[OK] Health check updated for {args.agent}")
        else:
            results = health_checker.check_all()
            print(f"\n[HEALTH CHECK] {len(results)} agents")
            for r in results:
                print(f"  {r['agent_id']}: {r['status']} ({r['elapsed_seconds']}s ago)")
            print()
    else:
        show_status()


if __name__ == '__main__':
    main()
