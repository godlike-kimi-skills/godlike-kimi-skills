"""
Celery Skill - Main Implementation

Provides comprehensive Celery operations including:
- Task management (send, revoke, result tracking)
- Worker management (inspect, control, stats)
- Workflow patterns (chains, groups, chords, maps)
- Periodic tasks (scheduling, crontab)
- Result backends (Redis, RPC, Database)
"""

import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Union, Tuple
from contextlib import contextmanager
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from functools import wraps

from celery import Celery, chain, group, chord, signature
from celery.result import AsyncResult, GroupResult
from celery.exceptions import CeleryError, TimeoutError, TaskRevokedError
from celery.task import Task as CeleryTask
from celery.schedules import crontab, schedule
from celery.events import EventReceiver
from celery.backends.base import DisabledBackend


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CeleryConfig:
    """Configuration for Celery application."""
    broker_url: str = "redis://localhost:6379/0"
    result_backend: Optional[str] = None
    task_serializer: str = "json"
    accept_content: List[str] = field(default_factory=lambda: ["json"])
    result_serializer: str = "json"
    timezone: str = "UTC"
    enable_utc: bool = True
    task_track_started: bool = True
    task_time_limit: int = 3600
    task_soft_time_limit: int = 3000
    worker_prefetch_multiplier: int = 1
    worker_concurrency: int = 4
    task_acks_late: bool = True
    task_reject_on_worker_lost: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to Celery configuration dict."""
        return {
            "broker_url": self.broker_url,
            "result_backend": self.result_backend or self.broker_url,
            "task_serializer": self.task_serializer,
            "accept_content": self.accept_content,
            "result_serializer": self.result_serializer,
            "timezone": self.timezone,
            "enable_utc": self.enable_utc,
            "task_track_started": self.task_track_started,
            "task_time_limit": self.task_time_limit,
            "task_soft_time_limit": self.task_soft_time_limit,
            "worker_prefetch_multiplier": self.worker_prefetch_multiplier,
            "worker_concurrency": self.worker_concurrency,
            "task_acks_late": self.task_acks_late,
            "task_reject_on_worker_lost": self.task_reject_on_worker_lost,
        }


@dataclass
class TaskResult:
    """Represents a task result."""
    task_id: str
    status: str
    result: Any = None
    traceback: Optional[str] = None
    date_done: Optional[str] = None
    
    @classmethod
    def from_async_result(cls, async_result: AsyncResult) -> "TaskResult":
        """Create TaskResult from Celery AsyncResult."""
        return cls(
            task_id=async_result.id,
            status=async_result.status,
            result=async_result.result if async_result.ready() else None,
            traceback=async_result.traceback if async_result.failed() else None,
            date_done=str(async_result.date_done) if async_result.ready() else None
        )


@dataclass
class WorkerInfo:
    """Information about a worker."""
    hostname: str
    status: str
    active_tasks: List[Dict[str, Any]]
    processed: int
    queues: List[str]
    pool_size: int
    
    @classmethod
    def from_stats(cls, hostname: str, stats: Dict) -> "WorkerInfo":]
        """Create WorkerInfo from Celery stats."""
        return cls(
            hostname=hostname,
            status="active" if stats else "offline",
            active_tasks=stats.get("active", []) if stats else [],
            processed=stats.get("total", {}).get("tasks", 0) if stats else 0,
            queues=list(stats.get("queues", {}).keys()) if stats else [],
            pool_size=stats.get("pool", {}).get("max-concurrency", 0) if stats else 0
        )


class CeleryAppManager:
    """Manages Celery application lifecycle."""
    
    def __init__(self, config: CeleryConfig, app_name: str = "celery-skill"):
        self.config = config
        self.app_name = app_name
        self._app: Optional[Celery] = None
        self._tasks: Dict[str, Callable] = {}
    
    def get_app(self) -> Celery:
        """Get or create Celery application."""
        if self._app is None:
            self._app = Celery(self.app_name)
            self._app.conf.update(self.config.to_dict())
            
            # Register tasks
            for name, func in self._tasks.items():
                self._app.task(name=name)(func)
            
            logger.info(f"Celery app '{self.app_name}' initialized")
        return self._app
    
    def register_task(self, func: Callable, name: Optional[str] = None) -> CeleryTask:
        """Register a function as a Celery task."""
        task_name = name or f"{self.app_name}.{func.__name__}"
        self._tasks[task_name] = func
        
        if self._app:
            task = self._app.task(name=task_name)(func)
            return task
        return None
    
    def close(self):
        """Close Celery connections."""
        if self._app:
            self._app.close()
            self._app = None
            logger.info("Celery app closed")


class CeleryTaskManager:
    """Manages Celery task operations."""
    
    def __init__(self, app_manager: CeleryAppManager):
        self.app_manager = app_manager
    
    def send_task(
        self,
        task_name: str,
        args: Optional[tuple] = None,
        kwargs: Optional[Dict] = None,
        countdown: Optional[int] = None,
        eta: Optional[datetime] = None,
        expires: Optional[Union[int, datetime]] = None,
        queue: Optional[str] = None,
        priority: Optional[int] = None,
        retries: int = 0,
        retry_delay: int = 0,
        routing_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a task to the queue with advanced options."""
        app = self.app_manager.get_app()
        
        try:
            result = app.send_task(
                task_name,
                args=args or (),
                kwargs=kwargs or {},
                countdown=countdown,
                eta=eta,
                expires=expires,
                queue=queue,
                priority=priority,
                retries=retries,
                retry_delay=retry_delay,
                routing_key=routing_key
            )
            
            logger.info(f"Task '{task_name}' sent with ID: {result.id}")
            return {
                "success": True,
                "task_id": result.id,
                "task_name": task_name,
                "status": result.status
            }
        except CeleryError as e:
            logger.error(f"Failed to send task '{task_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "task_name": task_name
            }
    
    def get_result(
        self,
        task_id: str,
        timeout: Optional[float] = None,
        propagate: bool = False
    ) -> Dict[str, Any]:
        """Get task result with optional waiting."""
        app = self.app_manager.get_app()
        
        try:
            async_result = AsyncResult(task_id, app=app)
            
            if timeout:
                result = async_result.get(timeout=timeout, propagate=propagate)
                return {
                    "success": True,
                    "task_id": task_id,
                    "status": async_result.status,
                    "result": result,
                    "ready": True
                }
            else:
                task_result = TaskResult.from_async_result(async_result)
                return {
                    "success": True,
                    **asdict(task_result),
                    "ready": async_result.ready()
                }
        except TimeoutError:
            return {
                "success": False,
                "error": "Timeout waiting for result",
                "task_id": task_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id
            }
    
    def revoke(
        self,
        task_id: str,
        terminate: bool = False,
        signal: Optional[str] = None,
        wait: bool = False,
        timeout: float = 1.0
    ) -> Dict[str, Any]:
        """Revoke a task by ID."""
        app = self.app_manager.get_app()
        
        try:
            async_result = AsyncResult(task_id, app=app)
            async_result.revoke(
                terminate=terminate,
                signal=signal,
                wait=wait,
                timeout=timeout
            )
            logger.info(f"Task {task_id} revoked")
            return {
                "success": True,
                "task_id": task_id,
                "revoked": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id
            }
    
    def retry(
        self,
        task_id: str,
        countdown: Optional[int] = None
    ) -> Dict[str, Any]:
        """Retry a failed task."""
        app = self.app_manager.get_app()
        
        try:
            async_result = AsyncResult(task_id, app=app)
            if async_result.failed():
                # Get task info and resend
                task = app.tasks.get(async_result.task_name)
                if task:
                    new_result = task.retry(
                        args=async_result.args,
                        kwargs=async_result.kwargs,
                        countdown=countdown
                    )
                    return {
                        "success": True,
                        "original_task_id": task_id,
                        "new_task_id": new_result.id
                    }
            return {
                "success": False,
                "error": "Task cannot be retried",
                "task_id": task_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id
            }
    
    def get_status(self, task_id: str) -> Dict[str, Any]:
        """Get current task status."""
        app = self.app_manager.get_app()
        
        async_result = AsyncResult(task_id, app=app)
        return {
            "task_id": task_id,
            "status": async_result.status,
            "ready": async_result.ready(),
            "successful": async_result.successful() if async_result.ready() else None,
            "failed": async_result.failed() if async_result.ready() else None
        }


class CeleryWorkerManager:
    """Manages Celery worker operations."""
    
    def __init__(self, app_manager: CeleryAppManager):
        self.app_manager = app_manager
    
    def inspect_workers(self) -> Dict[str, Any]:
        """Get information about all workers."""
        app = self.app_manager.get_app()
        
        try:
            inspect = app.control.inspect()
            stats = inspect.stats()
            active = inspect.active()
            scheduled = inspect.scheduled()
            reserved = inspect.reserved()
            
            workers = []
            if stats:
                for hostname, worker_stats in stats.items():
                    worker_info = {
                        "hostname": hostname,
                        "stats": worker_stats,
                        "active_tasks": active.get(hostname, []) if active else [],
                        "scheduled_tasks": scheduled.get(hostname, []) if scheduled else [],
                        "reserved_tasks": reserved.get(hostname, []) if reserved else []
                    }
                    workers.append(worker_info)
            
            return {
                "success": True,
                "workers": workers,
                "count": len(workers)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def ping_workers(self) -> Dict[str, Any]:
        """Ping all workers to check availability."""
        app = self.app_manager.get_app()
        
        try:
            inspect = app.control.inspect()
            ping_result = inspect.ping()
            
            return {
                "success": True,
                "responses": ping_result or {},
                "active_workers": list(ping_result.keys()) if ping_result else []
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_active_tasks(self) -> Dict[str, Any]:
        """Get all currently running tasks."""
        app = self.app_manager.get_app()
        
        try:
            inspect = app.control.inspect()
            active = inspect.active()
            
            all_active = []
            if active:
                for hostname, tasks in active.items():
                    for task in tasks:
                        task["worker"] = hostname
                        all_active.append(task)
            
            return {
                "success": True,
                "tasks": all_active,
                "count": len(all_active)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_registered_tasks(self) -> Dict[str, Any]:
        """Get all registered tasks."""
        app = self.app_manager.get_app()
        
        try:
            inspect = app.control.inspect()
            registered = inspect.registered()
            
            all_tasks = set()
            if registered:
                for tasks in registered.values():
                    all_tasks.update(tasks)
            
            return {
                "success": True,
                "tasks": sorted(list(all_tasks))
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def pool_restart(self, destination: Optional[List[str]] = None) -> Dict[str, Any]:
        """Restart worker pool."""
        app = self.app_manager.get_app()
        
        try:
            result = app.control.pool_restart(destination=destination)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def shutdown_workers(self, destination: Optional[List[str]] = None) -> Dict[str, Any]:
        """Shutdown workers gracefully."""
        app = self.app_manager.get_app()
        
        try:
            app.control.shutdown(destination=destination)
            return {
                "success": True,
                "message": "Shutdown signal sent to workers"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class CeleryWorkflow:
    """Manages complex task workflows."""
    
    def __init__(self, app_manager: CeleryAppManager):
        self.app_manager = app_manager
    
    def chain_tasks(
        self,
        *task_signatures: Union[str, tuple, Dict]
    ) -> Any:
        """Create a task chain (sequential execution)."""
        signatures = []
        for sig in task_signatures:
            if isinstance(sig, str):
                signatures.append(signature(sig))
            elif isinstance(sig, tuple):
                task_name, args = sig[0], sig[1] if len(sig) > 1 else ()
                kwargs = sig[2] if len(sig) > 2 else {}
                signatures.append(signature(task_name, args=args, kwargs=kwargs))
            elif isinstance(sig, dict):
                signatures.append(signature(
                    sig["task"],
                    args=sig.get("args", ()),
                    kwargs=sig.get("kwargs", {})
                ))
        
        workflow = chain(*signatures)
        return workflow.delay()
    
    def group_tasks(
        self,
        *task_signatures: Union[str, tuple, Dict]
    ) -> GroupResult:
        """Create a task group (parallel execution)."""
        signatures = []
        for sig in task_signatures:
            if isinstance(sig, str):
                signatures.append(signature(sig))
            elif isinstance(sig, tuple):
                task_name, args = sig[0], sig[1] if len(sig) > 1 else ()
                kwargs = sig[2] if len(sig) > 2 else {}
                signatures.append(signature(task_name, args=args, kwargs=kwargs))
            elif isinstance(sig, dict):
                signatures.append(signature(
                    sig["task"],
                    args=sig.get("args", ()),
                    kwargs=sig.get("kwargs", {})
                ))
        
        workflow = group(*signatures)
        return workflow.delay()
    
    def chord_workflow(
        self,
        header_tasks: List[Union[str, tuple, Dict]],
        callback_task: Union[str, tuple, Dict]
    ) -> Any:
        """Create a chord (parallel + callback)."""
        # Build header signatures
        header_sigs = []
        for sig in header_tasks:
            if isinstance(sig, str):
                header_sigs.append(signature(sig))
            elif isinstance(sig, tuple):
                task_name, args = sig[0], sig[1] if len(sig) > 1 else ()
                kwargs = sig[2] if len(sig) > 2 else {}
                header_sigs.append(signature(task_name, args=args, kwargs=kwargs))
            elif isinstance(sig, dict):
                header_sigs.append(signature(
                    sig["task"],
                    args=sig.get("args", ()),
                    kwargs=sig.get("kwargs", {})
                ))
        
        # Build callback signature
        if isinstance(callback_task, str):
            callback_sig = signature(callback_task)
        elif isinstance(callback_task, tuple):
            task_name, args = callback_task[0], callback_task[1] if len(callback_task) > 1 else ()
            kwargs = callback_task[2] if len(callback_task) > 2 else {}
            callback_sig = signature(task_name, args=args, kwargs=kwargs)
        else:
            callback_sig = signature(
                callback_task["task"],
                args=callback_task.get("args", ()),
                kwargs=callback_task.get("kwargs", {})
            )
        
        workflow = chord(group(*header_sigs), callback_sig)
        return workflow.delay()
    
    def map_task(
        self,
        task_name: str,
        items: List[tuple],
        chord_callback: Optional[str] = None
    ) -> Any:
        """Map a task over a list of arguments."""
        sigs = [signature(task_name, args=args) for args in items]
        
        if chord_callback:
            workflow = chord(group(*sigs), signature(chord_callback))
            return workflow.delay()
        else:
            workflow = group(*sigs)
            return workflow.delay()


class CeleryBeatScheduler:
    """Manages periodic tasks scheduling."""
    
    def __init__(self, app_manager: CeleryAppManager):
        self.app_manager = app_manager
    
    def add_periodic_task(
        self,
        task_name: str,
        schedule: Union[int, float, timedelta, crontab],
        args: Optional[tuple] = None,
        kwargs: Optional[Dict] = None,
        name: Optional[str] = None,
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Add a periodic task."""
        app = self.app_manager.get_app()
        task_display_name = name or f"periodic-{task_name}"
        
        try:
            app.add_periodic_task(
                schedule,
                signature(task_name, args=args, kwargs=kwargs, options=options),
                name=task_display_name
            )
            logger.info(f"Periodic task '{task_display_name}' added")
            return {
                "success": True,
                "task_name": task_display_name,
                "schedule": str(schedule)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def crontab(
        self,
        minute: str = "*",
        hour: str = "*",
        day_of_week: str = "*",
        day_of_month: str = "*",
        month_of_year: str = "*"
    ) -> crontab:
        """Create a crontab schedule."""
        return crontab(
            minute=minute,
            hour=hour,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            month_of_year=month_of_year
        )


class CelerySkill:
    """Main entry point for Celery operations."""
    
    def __init__(
        self,
        broker_url: str = "redis://localhost:6379/0",
        result_backend: Optional[str] = None,
        app_name: str = "celery-skill"
    ):
        self.config = CeleryConfig(
            broker_url=broker_url,
            result_backend=result_backend
        )
        self.app_manager = CeleryAppManager(self.config, app_name)
    
    def task_manager(self) -> CeleryTaskManager:
        """Get task manager."""
        return CeleryTaskManager(self.app_manager)
    
    def worker_manager(self) -> CeleryWorkerManager:
        """Get worker manager."""
        return CeleryWorkerManager(self.app_manager)
    
    def workflow(self) -> CeleryWorkflow:
        """Get workflow manager."""
        return CeleryWorkflow(self.app_manager)
    
    def scheduler(self) -> CeleryBeatScheduler:
        """Get scheduler."""
        return CeleryBeatScheduler(self.app_manager)
    
    def register_task(self, func: Callable, name: Optional[str] = None) -> CeleryTask:
        """Register a task function."""
        return self.app_manager.register_task(func, name)
    
    def health_check(self) -> Dict[str, Any]:
        """Check Celery health."""
        try:
            ping_result = self.worker_manager().ping_workers()
            return {
                "healthy": ping_result["success"],
                "broker_url": self.config.broker_url,
                "active_workers": ping_result.get("active_workers", []),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "broker_url": self.config.broker_url,
                "timestamp": datetime.now().isoformat()
            }
    
    def close(self):
        """Close all connections."""
        self.app_manager.close()


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Celery Skill")
    parser.add_argument("--broker-url", default="redis://localhost:6379/0")
    parser.add_argument("--action", required=True)
    parser.add_argument("--task-name")
    parser.add_argument("--task-id")
    parser.add_argument("--args", default="[]")
    
    args = parser.parse_args()
    
    skill = CelerySkill(broker_url=args.broker_url)
    
    try:
        if args.action == "send_task" and args.task_name:
            task_args = json.loads(args.args)
            result = skill.task_manager().send_task(args.task_name, args=task_args)
            print(json.dumps(result, indent=2))
            
        elif args.action == "get_result" and args.task_id:
            result = skill.task_manager().get_result(args.task_id)
            print(json.dumps(result, indent=2, default=str))
            
        elif args.action == "inspect_workers":
            result = skill.worker_manager().inspect_workers()
            print(json.dumps(result, indent=2, default=str))
            
        elif args.action == "ping":
            result = skill.worker_manager().ping_workers()
            print(json.dumps(result, indent=2))
            
        elif args.action == "health":
            result = skill.health_check()
            print(json.dumps(result, indent=2))
            
    finally:
        skill.close()


if __name__ == "__main__":
    main()
