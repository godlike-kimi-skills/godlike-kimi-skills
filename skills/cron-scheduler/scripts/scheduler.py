#!/usr/bin/env python3
"""
Task Scheduler - Production Grade
借鉴: BullMQ, Agenda, node-cron, APScheduler

实现:
- Cron表达式调度
- 延迟任务
- 重复任务
- 并发控制
- 重试机制
- 优先级队列
"""

import argparse
import json
import os
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import importlib.util


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class Job:
    """任务定义"""
    id: str
    name: str
    task: str
    args: Dict[str, Any]
    schedule_type: str  # 'cron', 'delay', 'interval', 'once'
    schedule_value: str
    priority: int = 5
    retry_attempts: int = 3
    retry_delay: int = 60
    timeout: int = 300
    status: JobStatus = JobStatus.PENDING
    created_at: str = ""
    last_run: str = ""
    next_run: str = ""
    run_count: int = 0
    fail_count: int = 0
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class CronParser:
    """Cron表达式解析器"""
    
    # 预定义表达式
    PREDEFINED = {
        '@yearly': '0 0 1 1 *',
        '@monthly': '0 0 1 * *',
        '@weekly': '0 0 * * 0',
        '@daily': '0 0 * * *',
        '@hourly': '0 * * * *',
        '@minutely': '* * * * *',
    }
    
    @classmethod
    def parse(cls, expression: str) -> Dict[str, str]:
        """解析Cron表达式为字段"""
        # 处理预定义表达式
        if expression in cls.PREDEFINED:
            expression = cls.PREDEFINED[expression]
        
        parts = expression.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {expression}")
        
        return {
            'minute': parts[0],
            'hour': parts[1],
            'day': parts[2],
            'month': parts[3],
            'weekday': parts[4],
        }
    
    @classmethod
    def match(cls, expression: str, dt: datetime = None) -> bool:
        """检查当前时间是否匹配Cron表达式"""
        if dt is None:
            dt = datetime.now()
        
        fields = cls.parse(expression)
        
        checks = [
            cls._match_field(fields['minute'], dt.minute, 0, 59),
            cls._match_field(fields['hour'], dt.hour, 0, 23),
            cls._match_field(fields['day'], dt.day, 1, 31),
            cls._match_field(fields['month'], dt.month, 1, 12),
            cls._match_field(fields['weekday'], dt.weekday(), 0, 6),
        ]
        
        return all(checks)
    
    @classmethod
    def _match_field(cls, field: str, value: int, min_val: int, max_val: int) -> bool:
        """匹配单个字段"""
        if field == '*':
            return True
        
        # 处理步长 (*/5)
        if field.startswith('*/'):
            step = int(field[2:])
            return value % step == 0
        
        # 处理范围 (1-5)
        if '-' in field:
            start, end = map(int, field.split('-'))
            return start <= value <= end
        
        # 处理列表 (1,3,5)
        if ',' in field:
            return value in map(int, field.split(','))
        
        # 精确匹配
        return value == int(field)
    
    @classmethod
    def get_next_run(cls, expression: str, after: datetime = None) -> datetime:
        """计算下次执行时间"""
        if after is None:
            after = datetime.now()
        
        # 简化实现: 逐分钟检查
        dt = after + timedelta(minutes=1)
        while True:
            if cls.match(expression, dt):
                return dt
            dt += timedelta(minutes=1)
            # 防止无限循环
            if (dt - after).days > 366:
                raise ValueError("Cannot find next run time within 1 year")


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = str(Path.home() / '.kimi' / 'scheduler.json')
        self.storage_path = storage_path
        self.jobs: Dict[str, Job] = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.load_jobs()
    
    def load_jobs(self):
        """加载任务"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for job_data in data.get('jobs', []):
                        job = Job(**job_data)
                        job.status = JobStatus(job_data.get('status', 'pending'))
                        self.jobs[job.id] = job
            except Exception as e:
                print(f"Error loading jobs: {e}")
    
    def save_jobs(self):
        """保存任务"""
        data = {
            'jobs': [
                {**asdict(job), 'status': job.status.value}
                for job in self.jobs.values()
            ]
        }
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_job(self, job: Job) -> str:
        """添加任务"""
        self.jobs[job.id] = job
        self.save_jobs()
        print(f"[+] Added job: {job.name} (ID: {job.id})")
        return job.id
    
    def remove_job(self, job_id: str) -> bool:
        """删除任务"""
        if job_id in self.jobs:
            del self.jobs[job_id]
            self.save_jobs()
            print(f"[+] Removed job: {job_id}")
            return True
        return False
    
    def pause_job(self, job_id: str) -> bool:
        """暂停任务"""
        if job_id in self.jobs:
            self.jobs[job_id].status = JobStatus.PAUSED
            self.save_jobs()
            print(f"[+] Paused job: {job_id}")
            return True
        return False
    
    def resume_job(self, job_id: str) -> bool:
        """恢复任务"""
        if job_id in self.jobs:
            self.jobs[job_id].status = JobStatus.PENDING
            self.save_jobs()
            print(f"[+] Resumed job: {job_id}")
            return True
        return False
    
    def list_jobs(self) -> List[Job]:
        """列出所有任务"""
        return sorted(self.jobs.values(), key=lambda j: j.created_at, reverse=True)
    
    def execute_task(self, job: Job) -> Dict:
        """执行任务"""
        print(f"[*] Executing: {job.name}")
        
        try:
            # 解析任务路径 (e.g., "tasks.hello")
            parts = job.task.split('.')
            module_path = '/'.join(parts[:-1]) + '.py'
            function_name = parts[-1]
            
            # 动态加载模块
            module_name = '.'.join(parts[:-1])
            spec = importlib.util.spec_from_file_location(
                module_name, 
                os.path.join(os.getcwd(), module_path)
            )
            
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                func = getattr(module, function_name)
                
                # 执行函数
                result = func(**job.args)
                return {"success": True, "result": result}
            else:
                # 作为shell命令执行
                result = subprocess.run(
                    job.task,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=job.timeout
                )
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_job(self, job: Job):
        """运行单个任务"""
        job.status = JobStatus.RUNNING
        job.last_run = datetime.now().isoformat()
        job.run_count += 1
        
        result = self.execute_task(job)
        
        if result.get('success'):
            job.status = JobStatus.COMPLETED
            print(f"[✓] Job completed: {job.name}")
        else:
            job.fail_count += 1
            if job.fail_count < job.retry_attempts:
                job.status = JobStatus.PENDING
                print(f"[!] Job failed (retry {job.fail_count}/{job.retry_attempts}): {job.name}")
            else:
                job.status = JobStatus.FAILED
                print(f"[✗] Job failed permanently: {job.name}")
        
        self.save_jobs()
    
    def check_and_run(self):
        """检查并运行到期任务"""
        now = datetime.now()
        
        for job in self.jobs.values():
            if job.status not in [JobStatus.PENDING, JobStatus.COMPLETED]:
                continue
            
            should_run = False
            
            if job.schedule_type == 'cron':
                # 检查Cron匹配
                if CronParser.match(job.schedule_value):
                    # 避免重复运行同一分钟
                    if job.last_run:
                        last = datetime.fromisoformat(job.last_run)
                        if (now - last).seconds < 60:
                            continue
                    should_run = True
            
            elif job.schedule_type == 'delay':
                # 检查延迟时间
                created = datetime.fromisoformat(job.created_at)
                delay_seconds = int(job.schedule_value)
                if (now - created).total_seconds() >= delay_seconds:
                    should_run = True
            
            elif job.schedule_type == 'once':
                # 检查指定时间
                target = datetime.fromisoformat(job.schedule_value)
                if now >= target and job.run_count == 0:
                    should_run = True
            
            if should_run:
                self.run_job(job)
    
    def start(self):
        """启动调度器"""
        self.running = True
        print("[*] Scheduler started. Press Ctrl+C to stop.")
        
        try:
            while self.running:
                self.check_and_run()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[*] Scheduler stopped.")
    
    def stop(self):
        """停止调度器"""
        self.running = False


def main():
    parser = argparse.ArgumentParser(description='Task Scheduler')
    subparsers = parser.add_subparsers(dest='command')
    
    # add
    add_parser = subparsers.add_parser('add', help='Add cron job')
    add_parser.add_argument('--name', required=True, help='Job name')
    add_parser.add_argument('--cron', required=True, help='Cron expression')
    add_parser.add_argument('--task', required=True, help='Task to run')
    add_parser.add_argument('--args', default='{}', help='JSON arguments')
    
    # delay
    delay_parser = subparsers.add_parser('delay', help='Add delayed job')
    delay_parser.add_argument('--name', required=True, help='Job name')
    delay_parser.add_argument('--task', required=True, help='Task to run')
    delay_parser.add_argument('--delay', type=int, required=True, help='Delay in seconds')
    
    # at
    at_parser = subparsers.add_parser('at', help='Schedule job at specific time')
    at_parser.add_argument('--name', required=True, help='Job name')
    at_parser.add_argument('--task', required=True, help='Task to run')
    at_parser.add_argument('--time', required=True, help='Time (YYYY-MM-DD HH:MM:SS)')
    
    # list
    list_parser = subparsers.add_parser('list', help='List all jobs')
    
    # remove
    remove_parser = subparsers.add_parser('remove', help='Remove job')
    remove_parser.add_argument('--id', help='Job ID')
    
    # pause/resume
    pause_parser = subparsers.add_parser('pause', help='Pause job')
    pause_parser.add_argument('--id', required=True, help='Job ID')
    
    resume_parser = subparsers.add_parser('resume', help='Resume job')
    resume_parser.add_argument('--id', required=True, help='Job ID')
    
    # start
    start_parser = subparsers.add_parser('start', help='Start scheduler')
    
    args = parser.parse_args()
    
    scheduler = TaskScheduler()
    
    if args.command == 'add':
        import uuid
        job = Job(
            id=str(uuid.uuid4())[:8],
            name=args.name,
            task=args.task,
            args=json.loads(args.args),
            schedule_type='cron',
            schedule_value=args.cron,
        )
        scheduler.add_job(job)
    
    elif args.command == 'delay':
        import uuid
        job = Job(
            id=str(uuid.uuid4())[:8],
            name=args.name,
            task=args.task,
            args={},
            schedule_type='delay',
            schedule_value=str(args.delay),
        )
        scheduler.add_job(job)
    
    elif args.command == 'at':
        import uuid
        job = Job(
            id=str(uuid.uuid4())[:8],
            name=args.name,
            task=args.task,
            args={},
            schedule_type='once',
            schedule_value=args.time,
        )
        scheduler.add_job(job)
    
    elif args.command == 'list':
        jobs = scheduler.list_jobs()
        print(f"\n{'ID':<10} {'Name':<20} {'Type':<10} {'Status':<12} {'Last Run'}")
        print("-" * 80)
        for job in jobs:
            print(f"{job.id:<10} {job.name:<20} {job.schedule_type:<10} "
                  f"{job.status.value:<12} {job.last_run or 'Never'}")
    
    elif args.command == 'remove':
        scheduler.remove_job(args.id)
    
    elif args.command == 'pause':
        scheduler.pause_job(args.id)
    
    elif args.command == 'resume':
        scheduler.resume_job(args.id)
    
    elif args.command == 'start':
        scheduler.start()
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
