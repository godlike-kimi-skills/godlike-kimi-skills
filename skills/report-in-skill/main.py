#!/usr/bin/env python3
"""
Report-In Skill - System Status Reporter
Generates comprehensive reports on tasks, agents, memory, and ports.
"""

import os
import sys
import io

# Fix encoding issues on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import json
import time
import socket
import argparse
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Try to import psutil for system metrics
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Warning: psutil not installed. Some features will be limited.")


@dataclass
class TaskInfo:
    """Represents a task with its metadata."""
    name: str
    status: str  # 'completed', 'running', 'failed'
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress: float = 0.0  # 0-100
    duration_minutes: float = 0.0
    category: str = "general"
    agent_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'progress': self.progress,
            'duration_minutes': self.duration_minutes,
            'category': self.category,
            'agent_id': self.agent_id
        }


@dataclass
class AgentInfo:
    """Represents an active agent."""
    agent_id: str
    pid: int
    status: str
    current_task: Optional[str] = None
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    start_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'agent_id': self.agent_id,
            'pid': self.pid,
            'status': self.status,
            'current_task': self.current_task,
            'cpu_percent': self.cpu_percent,
            'memory_mb': self.memory_mb,
            'start_time': self.start_time.isoformat() if self.start_time else None
        }


@dataclass
class MemoryInfo:
    """System memory information."""
    total_gb: float
    used_gb: float
    available_gb: float
    percent_used: float
    cached_gb: float = 0.0
    buffers_gb: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PortInfo:
    """Network port information."""
    port: int
    protocol: str
    status: str  # 'listening', 'established', 'closed'
    service: Optional[str] = None
    pid: Optional[int] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class DiskInfo:
    """Disk usage information."""
    device: str
    mountpoint: str
    total_gb: float
    used_gb: float
    free_gb: float
    percent_used: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ReportInSkill:
    """Main skill class for generating system reports."""
    
    def __init__(self):
        self.config = self._load_config()
        self.report_time = datetime.now()
        
    def _load_config(self) -> Dict:
        """Load configuration from environment variables."""
        return {
            'log_path': os.getenv('REPORTIN_LOG_PATH', str(Path.home() / '.kimi' / 'logs')),
            'task_log': os.getenv('REPORTIN_TASK_LOG', 'tasks.log'),
            'format': os.getenv('REPORTIN_FORMAT', 'text'),
            'time_range_hours': int(os.getenv('REPORTIN_TIME_RANGE', '24')),
        }
    
    def get_completed_tasks(self, hours: int = 24) -> List[TaskInfo]:
        """Get tasks completed in the last N hours."""
        tasks = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Try to read from task log file
        log_file = Path(self.config['log_path']) / self.config['task_log']
        
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Try to parse as JSON first
                        try:
                            data = json.loads(line)
                            task = self._parse_task_from_json(data)
                            if task and task.end_time and task.end_time > cutoff_time:
                                tasks.append(task)
                        except json.JSONDecodeError:
                            # Fall back to simple parsing
                            task = self._parse_task_from_line(line)
                            if task and task.end_time and task.end_time > cutoff_time:
                                tasks.append(task)
            except Exception as e:
                print(f"Warning: Could not read task log: {e}")
        
        # If no log file, try to infer from recent file modifications
        if not tasks:
            tasks = self._infer_tasks_from_files(cutoff_time)
        
        # Sort by end time, most recent first
        tasks.sort(key=lambda x: x.end_time or datetime.min, reverse=True)
        return tasks
    
    def _parse_task_from_json(self, data: Dict) -> Optional[TaskInfo]:
        """Parse task info from JSON data."""
        try:
            end_time = None
            if 'end_time' in data:
                end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
            
            start_time = None
            if 'start_time' in data:
                start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
            
            return TaskInfo(
                name=data.get('name', 'Unknown'),
                status=data.get('status', 'completed'),
                start_time=start_time,
                end_time=end_time,
                progress=data.get('progress', 100.0),
                duration_minutes=data.get('duration_minutes', 0.0),
                category=data.get('category', 'general'),
                agent_id=data.get('agent_id')
            )
        except Exception:
            return None
    
    def _parse_task_from_line(self, line: str) -> Optional[TaskInfo]:
        """Parse task info from a log line."""
        # Simple parsing: "[TIMESTAMP] STATUS: Task Name"
        try:
            if '[' in line and ']' in line:
                timestamp_str = line[line.find('[')+1:line.find(']')]
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                
                if 'COMPLETED:' in line:
                    name = line.split('COMPLETED:')[1].strip()
                    return TaskInfo(name=name, status='completed', end_time=timestamp)
                elif 'FAILED:' in line:
                    name = line.split('FAILED:')[1].strip()
                    return TaskInfo(name=name, status='failed', end_time=timestamp)
        except Exception:
            pass
        return None
    
    def _infer_tasks_from_files(self, cutoff_time: datetime) -> List[TaskInfo]:
        """Infer recent tasks by checking modified files."""
        tasks = []
        skills_dir = Path('D:/kimi/projects/godlike-kimi-skills/skills')
        
        if skills_dir.exists():
            for skill_dir in skills_dir.iterdir():
                if skill_dir.is_dir():
                    # Check the most recently modified file in the skill
                    try:
                        latest_mtime = max(
                            (f.stat().st_mtime for f in skill_dir.rglob('*') if f.is_file()),
                            default=0
                        )
                        if latest_mtime > 0:
                            mtime = datetime.fromtimestamp(latest_mtime)
                            if mtime > cutoff_time:
                                tasks.append(TaskInfo(
                                    name=f"Updated {skill_dir.name}",
                                    status='completed',
                                    end_time=mtime,
                                    category='skill-development'
                                ))
                    except Exception:
                        pass
        
        return tasks
    
    def get_running_tasks(self) -> List[TaskInfo]:
        """Get currently running tasks."""
        running_tasks = []
        
        # Check for processes that look like agents or tasks
        if HAS_PSUTIL:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'cpu_percent', 'memory_info']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    
                    # Look for agent or kimi-related processes
                    if any(keyword in cmdline.lower() for keyword in ['agent', 'kimi', 'skill', 'task']):
                        if proc.info['create_time']:
                            start_time = datetime.fromtimestamp(proc.info['create_time'])
                            running_tasks.append(TaskInfo(
                                name=f"Process: {proc.info['name']}",
                                status='running',
                                start_time=start_time,
                                progress=self._estimate_progress(start_time),
                                agent_id=str(proc.info['pid'])
                            ))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        
        # Also check for any .lock files or progress indicators
        running_tasks.extend(self._check_progress_files())
        
        return running_tasks
    
    def _estimate_progress(self, start_time: datetime) -> float:
        """Estimate task progress based on duration."""
        duration = datetime.now() - start_time
        minutes = duration.total_seconds() / 60
        
        # Simple heuristic: tasks under 5 min = 25%, 5-30 min = 50%, 30-60 min = 75%, >60 min = 90%
        if minutes < 5:
            return 25.0
        elif minutes < 30:
            return 50.0
        elif minutes < 60:
            return 75.0
        else:
            return 90.0
    
    def _check_progress_files(self) -> List[TaskInfo]:
        """Check for progress indicator files."""
        tasks = []
        progress_dir = Path(self.config['log_path']) / 'progress'
        
        if progress_dir.exists():
            for progress_file in progress_dir.glob('*.progress'):
                try:
                    with open(progress_file, 'r') as f:
                        data = json.load(f)
                        tasks.append(TaskInfo(
                            name=data.get('task_name', progress_file.stem),
                            status='running',
                            progress=data.get('progress', 0.0),
                            start_time=datetime.fromisoformat(data['start_time']) if 'start_time' in data else None
                        ))
                except Exception:
                    pass
        
        return tasks
    
    def get_active_agents(self) -> List[AgentInfo]:
        """Get information about active agents."""
        agents = []
        
        if HAS_PSUTIL:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'cpu_percent', 'memory_info']):
                try:
                    pinfo = proc.info
                    cmdline = ' '.join(pinfo['cmdline'] or [])
                    
                    # Detect agent processes
                    is_agent = False
                    agent_keywords = ['agent', 'kimi', 'claude', 'skill', 'worker', 'bot']
                    
                    if any(kw in cmdline.lower() for kw in agent_keywords):
                        is_agent = True
                    
                    if is_agent:
                        start_time = None
                        if pinfo['create_time']:
                            start_time = datetime.fromtimestamp(pinfo['create_time'])
                        
                        memory_mb = 0.0
                        if pinfo['memory_info']:
                            memory_mb = pinfo['memory_info'].rss / (1024 * 1024)
                        
                        agents.append(AgentInfo(
                            agent_id=f"agent-{pinfo['pid']}",
                            pid=pinfo['pid'],
                            status='active',
                            current_task=self._get_agent_task(pinfo['pid']),
                            cpu_percent=pinfo['cpu_percent'] or 0.0,
                            memory_mb=memory_mb,
                            start_time=start_time
                        ))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        
        return agents
    
    def _get_agent_task(self, pid: int) -> Optional[str]:
        """Try to determine what task an agent is working on."""
        try:
            if HAS_PSUTIL:
                proc = psutil.Process(pid)
                cmdline = ' '.join(proc.cmdline() or [])
                # Extract task name from command line if possible
                if 'skill' in cmdline.lower():
                    parts = cmdline.split()
                    for i, part in enumerate(parts):
                        if 'skill' in part.lower() and i + 1 < len(parts):
                            return parts[i + 1]
                return f"Working on: {proc.name()}"
        except Exception:
            pass
        return None
    
    def get_memory_info(self) -> MemoryInfo:
        """Get system memory information."""
        if HAS_PSUTIL:
            mem = psutil.virtual_memory()
            return MemoryInfo(
                total_gb=mem.total / (1024**3),
                used_gb=mem.used / (1024**3),
                available_gb=mem.available / (1024**3),
                percent_used=mem.percent,
                cached_gb=getattr(mem, 'cached', 0) / (1024**3),
                buffers_gb=getattr(mem, 'buffers', 0) / (1024**3)
            )
        else:
            # Fallback: try to parse /proc/meminfo on Linux
            return self._get_memory_from_proc()
    
    def _get_memory_from_proc(self) -> MemoryInfo:
        """Fallback method to get memory info from /proc."""
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
            
            mem_data = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    mem_data[key.strip()] = int(value.split()[0]) * 1024  # Convert KB to bytes
            
            total = mem_data.get('MemTotal', 0)
            free = mem_data.get('MemFree', 0)
            available = mem_data.get('MemAvailable', free)
            buffers = mem_data.get('Buffers', 0)
            cached = mem_data.get('Cached', 0)
            
            used = total - available
            
            return MemoryInfo(
                total_gb=total / (1024**3),
                used_gb=used / (1024**3),
                available_gb=available / (1024**3),
                percent_used=(used / total * 100) if total > 0 else 0,
                cached_gb=cached / (1024**3),
                buffers_gb=buffers / (1024**3)
            )
        except Exception:
            return MemoryInfo(total_gb=0, used_gb=0, available_gb=0, percent_used=0)
    
    def get_disk_info(self) -> List[DiskInfo]:
        """Get disk usage information."""
        disks = []
        
        if HAS_PSUTIL:
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append(DiskInfo(
                        device=partition.device,
                        mountpoint=partition.mountpoint,
                        total_gb=usage.total / (1024**3),
                        used_gb=usage.used / (1024**3),
                        free_gb=usage.free / (1024**3),
                        percent_used=usage.percent
                    ))
                except (PermissionError, OSError):
                    pass
        
        return disks
    
    def get_port_status(self) -> List[PortInfo]:
        """Get network port status."""
        ports = []
        
        if HAS_PSUTIL:
            # Get listening ports
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'LISTEN' and conn.laddr:
                    service = self._identify_service(conn.laddr.port)
                    ports.append(PortInfo(
                        port=conn.laddr.port,
                        protocol='tcp',
                        status='listening',
                        service=service,
                        pid=conn.pid
                    ))
        else:
            # Fallback: use netstat command
            ports = self._get_ports_from_netstat()
        
        # Sort by port number
        ports.sort(key=lambda x: x.port)
        return ports
    
    def _identify_service(self, port: int) -> Optional[str]:
        """Identify service name by port number."""
        common_ports = {
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            110: 'POP3',
            143: 'IMAP',
            443: 'HTTPS',
            3306: 'MySQL',
            3389: 'RDP',
            5432: 'PostgreSQL',
            6379: 'Redis',
            8080: 'HTTP-Alt',
            8443: 'HTTPS-Alt',
            9200: 'Elasticsearch',
            27017: 'MongoDB',
        }
        return common_ports.get(port, 'Unknown')
    
    def _get_ports_from_netstat(self) -> List[PortInfo]:
        """Fallback to get ports using netstat command."""
        ports = []
        
        try:
            # Try different commands based on OS
            if sys.platform == 'win32':
                result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            else:
                result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if 'LISTEN' in line:
                    # Parse netstat output
                    parts = line.split()
                    for part in parts:
                        if ':' in part:
                            try:
                                port = int(part.split(':')[-1])
                                service = self._identify_service(port)
                                ports.append(PortInfo(
                                    port=port,
                                    protocol='tcp',
                                    status='listening',
                                    service=service
                                ))
                            except ValueError:
                                pass
        except Exception:
            pass
        
        return ports
    
    def generate_full_report(self) -> str:
        """Generate a complete text report."""
        lines = []
        
        # Header
        lines.extend([
            "╔═══════════════════════════════════════════════════════════╗",
            "║                    SYSTEM STATUS REPORT                    ║",
            f"║                    Generated: {self.report_time.strftime('%Y-%m-%d %H:%M:%S')}         ║",
            "╚═══════════════════════════════════════════════════════════╝",
            ""
        ])
        
        # Task Summary
        completed_tasks = self.get_completed_tasks(self.config['time_range_hours'])
        running_tasks = self.get_running_tasks()
        
        lines.extend([
            "📊 TASK SUMMARY (Last 24 Hours)",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"✅ Completed Tasks: {len(completed_tasks)}",
            f"⏳ Running Tasks: {len(running_tasks)}",
            ""
        ])
        
        if completed_tasks:
            lines.append("Completed Tasks:")
            for task in completed_tasks[:10]:  # Show top 10
                time_ago = self._format_time_ago(task.end_time)
                lines.append(f"  ✓ {task.name[:40]:40} {time_ago}")
            if len(completed_tasks) > 10:
                lines.append(f"  ... and {len(completed_tasks) - 10} more")
            lines.append("")
        
        if running_tasks:
            lines.append("Running Tasks:")
            for task in running_tasks:
                progress_bar = self._format_progress_bar(task.progress)
                lines.append(f"  ⏳ {task.name[:35]:35} {progress_bar} {task.progress:.0f}%")
            lines.append("")
        
        # Agent Activities
        agents = self.get_active_agents()
        lines.extend([
            "🤖 AGENT ACTIVITIES",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"Active Agents: {len(agents)}",
            ""
        ])
        
        for agent in agents:
            lines.extend([
                f"  🤖 {agent.agent_id} (PID: {agent.pid})",
                f"     Status: {agent.status}",
            ])
            if agent.current_task:
                lines.append(f"     Task: {agent.current_task}")
            lines.append(f"     CPU: {agent.cpu_percent:.1f}% | Memory: {agent.memory_mb:.1f}MB")
            if agent.start_time:
                uptime = self._format_time_ago(agent.start_time)
                lines.append(f"     Uptime: {uptime}")
            lines.append("")
        
        # System Resources
        memory = self.get_memory_info()
        disks = self.get_disk_info()
        
        lines.extend([
            "💾 SYSTEM RESOURCES",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "Memory:",
            f"  Total: {memory.total_gb:.1f}GB",
            f"  Used: {memory.used_gb:.1f}GB ({memory.percent_used:.1f}%)",
            f"  Available: {memory.available_gb:.1f}GB",
        ])
        
        if memory.cached_gb > 0:
            lines.append(f"  Cached: {memory.cached_gb:.1f}GB")
        
        lines.append("")
        
        if disks:
            lines.append("Disk Usage:")
            for disk in disks:
                status_icon = "✓" if disk.percent_used < 80 else "⚠"
                lines.append(f"  {status_icon} {disk.mountpoint}: {disk.percent_used:.0f}% used ({disk.used_gb:.0f}GB/{disk.total_gb:.0f}GB)")
            lines.append("")
        
        if HAS_PSUTIL:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            lines.append(f"CPU: {cpu_percent:.1f}% ({cpu_count} cores)")
            lines.append("")
        
        # Port Status
        ports = self.get_port_status()
        lines.extend([
            "🌐 PORT STATUS",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"Active Services: {len(ports)}",
            ""
        ])
        
        for port in ports[:20]:  # Show top 20
            service_name = port.service or 'Unknown'
            lines.append(f"  ✓ {port.port:5}/tcp   {service_name:20} {port.status}")
        
        if len(ports) > 20:
            lines.append(f"  ... and {len(ports) - 20} more ports")
        
        lines.append("")
        lines.append("═" * 59)
        lines.append("Report generated by report-in-skill")
        lines.append("═" * 59)
        
        return '\n'.join(lines)
    
    def generate_json_report(self) -> Dict:
        """Generate a JSON report."""
        return {
            'generated_at': self.report_time.isoformat(),
            'tasks': {
                'completed_24h': [t.to_dict() for t in self.get_completed_tasks(24)],
                'running': [t.to_dict() for t in self.get_running_tasks()]
            },
            'agents': [a.to_dict() for a in self.get_active_agents()],
            'system': {
                'memory': self.get_memory_info().to_dict(),
                'disks': [d.to_dict() for d in self.get_disk_info()],
                'cpu_cores': psutil.cpu_count() if HAS_PSUTIL else None,
                'cpu_percent': psutil.cpu_percent(interval=1) if HAS_PSUTIL else None
            },
            'network': {
                'ports': [p.to_dict() for p in self.get_port_status()]
            }
        }
    
    def _format_time_ago(self, dt: Optional[datetime]) -> str:
        """Format datetime as 'X hours ago' etc."""
        if not dt:
            return "unknown"
        
        diff = datetime.now() - dt
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return f"{int(seconds)}s ago"
        elif seconds < 3600:
            return f"{int(seconds/60)}m ago"
        elif seconds < 86400:
            return f"{int(seconds/3600)}h ago"
        else:
            return f"{int(seconds/86400)}d ago"
    
    def _format_progress_bar(self, percent: float, width: int = 20) -> str:
        """Format a text progress bar."""
        filled = int(width * percent / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}]"


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Report-In Skill - System Status Reporter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s report          Generate full status report
  %(prog)s tasks           Show task summary
  %(prog)s agents          Show agent activities
  %(prog)s ports           Show port status
  %(prog)s memory          Show memory usage
  %(prog)s --json          Generate JSON output
        """
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        default='report',
        choices=['report', 'tasks', 'agents', 'ports', 'memory', 'full'],
        help='Command to execute (default: report)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Time range for completed tasks in hours (default: 24)'
    )
    
    args = parser.parse_args()
    
    skill = ReportInSkill()
    
    if args.json:
        report = skill.generate_json_report()
        print(json.dumps(report, indent=2, default=str))
    else:
        if args.command == 'report' or args.command == 'full':
            print(skill.generate_full_report())
        elif args.command == 'tasks':
            completed = skill.get_completed_tasks(args.hours)
            running = skill.get_running_tasks()
            
            print("📊 TASK SUMMARY")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"✅ Completed (last {args.hours}h): {len(completed)}")
            print(f"⏳ Running: {len(running)}")
            print()
            
            if completed:
                print("Recent Completed:")
                for t in completed[:5]:
                    print(f"  ✓ {t.name}")
                print()
            
            if running:
                print("Running Tasks:")
                for t in running:
                    print(f"  ⏳ {t.name} ({t.progress:.0f}%)")
                    
        elif args.command == 'agents':
            agents = skill.get_active_agents()
            print("🤖 AGENT ACTIVITIES")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"Active Agents: {len(agents)}")
            print()
            
            for agent in agents:
                print(f"  🤖 {agent.agent_id} (PID: {agent.pid})")
                print(f"     CPU: {agent.cpu_percent:.1f}% | Memory: {agent.memory_mb:.1f}MB")
                if agent.current_task:
                    print(f"     Task: {agent.current_task}")
                print()
                
        elif args.command == 'ports':
            ports = skill.get_port_status()
            print("🌐 PORT STATUS")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"Listening Services: {len(ports)}")
            print()
            
            for port in ports:
                service = port.service or 'Unknown'
                print(f"  ✓ {port.port:5}/tcp  {service}")
                
        elif args.command == 'memory':
            mem = skill.get_memory_info()
            disks = skill.get_disk_info()
            
            print("💾 MEMORY & DISK")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("Memory:")
            print(f"  Total: {mem.total_gb:.1f}GB")
            print(f"  Used: {mem.used_gb:.1f}GB ({mem.percent_used:.1f}%)")
            print(f"  Available: {mem.available_gb:.1f}GB")
            print()
            
            if disks:
                print("Disk Usage:")
                for d in disks:
                    print(f"  {d.mountpoint}: {d.percent_used:.0f}% used")


if __name__ == '__main__':
    main()
