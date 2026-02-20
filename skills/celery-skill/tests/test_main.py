"""
Unit tests for Celery Skill main module.

Tests cover:
- Configuration classes
- App management
- Task operations
- Worker management
- Workflows
- Scheduling
"""

import json
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, PropertyMock

import sys
sys.path.insert(0, "D:/kimi/projects/godlike-kimi-skills/skills/celery-skill/src")

from main import (
    CeleryConfig, TaskResult, WorkerInfo,
    CeleryAppManager, CeleryTaskManager, CeleryWorkerManager,
    CeleryWorkflow, CeleryBeatScheduler, CelerySkill
)


class TestCeleryConfig(unittest.TestCase):
    """Test CeleryConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = CeleryConfig()
        self.assertEqual(config.broker_url, "redis://localhost:6379/0")
        self.assertIsNone(config.result_backend)
        self.assertEqual(config.task_serializer, "json")
        self.assertTrue(config.enable_utc)
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = CeleryConfig(
            broker_url="amqp://guest:guest@localhost:5672//",
            result_backend="redis://localhost:6379/1",
            worker_concurrency=8
        )
        self.assertEqual(config.broker_url, "amqp://guest:guest@localhost:5672//")
        self.assertEqual(config.result_backend, "redis://localhost:6379/1")
        self.assertEqual(config.worker_concurrency, 8)
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = CeleryConfig(broker_url="redis://localhost:6379/0")
        config_dict = config.to_dict()
        self.assertIn("broker_url", config_dict)
        self.assertEqual(config_dict["broker_url"], "redis://localhost:6379/0")


class TestTaskResult(unittest.TestCase):
    """Test TaskResult dataclass."""
    
    def test_creation(self):
        """Test TaskResult creation."""
        result = TaskResult(
            task_id="abc-123",
            status="SUCCESS",
            result={"data": "value"}
        )
        self.assertEqual(result.task_id, "abc-123")
        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(result.result, {"data": "value"})
    
    @patch("main.AsyncResult")
    def test_from_async_result(self, mock_async_class):
        """Test creating from AsyncResult."""
        mock_async = Mock()
        mock_async.id = "abc-123"
        mock_async.status = "SUCCESS"
        mock_async.ready.return_value = True
        mock_async.result = {"data": "value"}
        mock_async.failed.return_value = False
        mock_async.traceback = None
        mock_async.date_done = datetime.now()
        
        result = TaskResult.from_async_result(mock_async)
        
        self.assertEqual(result.task_id, "abc-123")
        self.assertEqual(result.status, "SUCCESS")


class TestWorkerInfo(unittest.TestCase):
    """Test WorkerInfo dataclass."""
    
    def test_from_stats(self):
        """Test creating from worker stats."""
        stats = {
            "active": [{"id": "task-1"}],
            "total": {"tasks": 100},
            "queues": {"high": {}, "default": {}},
            "pool": {"max-concurrency": 4}
        }
        
        info = WorkerInfo.from_stats("worker1@host", stats)
        
        self.assertEqual(info.hostname, "worker1@host")
        self.assertEqual(info.status, "active")
        self.assertEqual(info.processed, 100)
        self.assertEqual(info.pool_size, 4)


class TestCeleryAppManager(unittest.TestCase):
    """Test CeleryAppManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = CeleryConfig(broker_url="redis://localhost:6379/0")
        self.manager = CeleryAppManager(self.config, "test-app")
    
    @patch("main.Celery")
    def test_get_app(self, mock_celery_class):
        """Test getting Celery app."""
        mock_app = Mock()
        mock_celery_class.return_value = mock_app
        
        app = self.manager.get_app()
        
        self.assertEqual(app, mock_app)
        mock_celery_class.assert_called_once_with("test-app")
    
    @patch("main.Celery")
    def test_get_app_caches(self, mock_celery_class):
        """Test app caching."""
        mock_app = Mock()
        mock_celery_class.return_value = mock_app
        
        app1 = self.manager.get_app()
        app2 = self.manager.get_app()
        
        self.assertEqual(app1, app2)
        mock_celery_class.assert_called_once()
    
    def test_register_task(self):
        """Test task registration."""
        def test_func(x):
            return x * 2
        
        with patch.object(self.manager, "get_app") as mock_get_app:
            mock_app = Mock()
            mock_get_app.return_value = mock_app
            
            self.manager.register_task(test_func, name="tasks.double")
            
            self.assertIn("tasks.double", self.manager._tasks)


class TestCeleryTaskManager(unittest.TestCase):
    """Test CeleryTaskManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_app_manager = Mock()
        self.mock_app = Mock()
        self.mock_app_manager.get_app.return_value = self.mock_app
        self.manager = CeleryTaskManager(self.mock_app_manager)
    
    def test_send_task_success(self):
        """Test successful task sending."""
        mock_result = Mock()
        mock_result.id = "task-123"
        mock_result.status = "PENDING"
        self.mock_app.send_task.return_value = mock_result
        
        result = self.manager.send_task(
            task_name="tasks.process",
            args=("data",),
            queue="default"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["task_id"], "task-123")
    
    def test_send_task_with_countdown(self):
        """Test sending task with countdown."""
        mock_result = Mock()
        mock_result.id = "task-456"
        mock_result.status = "PENDING"
        self.mock_app.send_task.return_value = mock_result
        
        result = self.manager.send_task(
            task_name="tasks.delayed",
            countdown=3600
        )
        
        self.assertTrue(result["success"])
        call_kwargs = self.mock_app.send_task.call_args[1]
        self.assertEqual(call_kwargs["countdown"], 3600)
    
    @patch("main.AsyncResult")
    def test_get_result_ready(self, mock_async_class):
        """Test getting result for ready task."""
        mock_async = Mock()
        mock_async.status = "SUCCESS"
        mock_async.ready.return_value = True
        mock_async.successful.return_value = True
        mock_async.failed.return_value = False
        mock_async.result = {"output": "data"}
        mock_async.traceback = None
        mock_async.date_done = datetime.now()
        mock_async_class.return_value = mock_async
        
        result = self.manager.get_result("task-123")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], {"output": "data"})
    
    @patch("main.AsyncResult")
    def test_get_result_with_timeout(self, mock_async_class):
        """Test getting result with timeout."""
        mock_async = Mock()
        mock_async.get.return_value = {"output": "data"}
        mock_async_class.return_value = mock_async
        
        result = self.manager.get_result("task-123", timeout=30)
        
        self.assertTrue(result["success"])
        mock_async.get.assert_called_with(timeout=30, propagate=False)
    
    @patch("main.AsyncResult")
    def test_revoke_task(self, mock_async_class):
        """Test task revocation."""
        mock_async = Mock()
        mock_async_class.return_value = mock_async
        
        result = self.manager.revoke("task-123", terminate=True)
        
        self.assertTrue(result["success"])
        self.assertTrue(result["revoked"])
        mock_async.revoke.assert_called_with(
            terminate=True, signal=None, wait=False, timeout=1.0
        )
    
    @patch("main.AsyncResult")
    def test_get_status(self, mock_async_class):
        """Test getting task status."""
        mock_async = Mock()
        mock_async.status = "STARTED"
        mock_async.ready.return_value = False
        mock_async_class.return_value = mock_async
        
        result = self.manager.get_status("task-123")
        
        self.assertEqual(result["status"], "STARTED")
        self.assertFalse(result["ready"])


class TestCeleryWorkerManager(unittest.TestCase):
    """Test CeleryWorkerManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_app_manager = Mock()
        self.mock_app = Mock()
        self.mock_app_manager.get_app.return_value = self.mock_app
        self.manager = CeleryWorkerManager(self.mock_app_manager)
    
    def test_inspect_workers(self):
        """Test inspecting workers."""
        mock_inspect = Mock()
        mock_inspect.stats.return_value = {
            "worker1@host": {"total": {"tasks": 100}}
        }
        mock_inspect.active.return_value = {"worker1@host": []}
        mock_inspect.scheduled.return_value = {}
        mock_inspect.reserved.return_value = {}
        self.mock_app.control.inspect.return_value = mock_inspect
        
        result = self.manager.inspect_workers()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 1)
    
    def test_ping_workers(self):
        """Test pinging workers."""
        mock_inspect = Mock()
        mock_inspect.ping.return_value = {
            "worker1@host": {"ok": "pong"},
            "worker2@host": {"ok": "pong"}
        }
        self.mock_app.control.inspect.return_value = mock_inspect
        
        result = self.manager.ping_workers()
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["active_workers"]), 2)
    
    def test_get_active_tasks(self):
        """Test getting active tasks."""
        mock_inspect = Mock()
        mock_inspect.active.return_value = {
            "worker1@host": [
                {"id": "task-1", "name": "tasks.process"}
            ]
        }
        self.mock_app.control.inspect.return_value = mock_inspect
        
        result = self.manager.get_active_tasks()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["tasks"][0]["worker"], "worker1@host")
    
    def test_get_registered_tasks(self):
        """Test getting registered tasks."""
        mock_inspect = Mock()
        mock_inspect.registered.return_value = {
            "worker1@host": ["tasks.email", "tasks.process"]
        }
        self.mock_app.control.inspect.return_value = mock_inspect
        
        result = self.manager.get_registered_tasks()
        
        self.assertTrue(result["success"])
        self.assertIn("tasks.email", result["tasks"])
    
    def test_pool_restart(self):
        """Test pool restart."""
        self.mock_app.control.pool_restart.return_value = {"ok": "restarted"}
        
        result = self.manager.pool_restart()
        
        self.assertTrue(result["success"])
    
    def test_shutdown_workers(self):
        """Test shutting down workers."""
        result = self.manager.shutdown_workers()
        
        self.assertTrue(result["success"])
        self.mock_app.control.shutdown.assert_called_once()


class TestCeleryWorkflow(unittest.TestCase):
    """Test CeleryWorkflow class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_app_manager = Mock()
        self.mock_app = Mock()
        self.mock_app_manager.get_app.return_value = self.mock_app
        self.workflow = CeleryWorkflow(self.mock_app_manager)
    
    @patch("main.chain")
    @patch("main.signature")
    def test_chain_tasks(self, mock_signature, mock_chain):
        """Test creating task chain."""
        mock_workflow = Mock()
        mock_chain.return_value = mock_workflow
        mock_workflow.delay.return_value = Mock(id="chain-123")
        
        result = self.workflow.chain_tasks(
            ("tasks.step1", ("arg1",)),
            ("tasks.step2",)
        )
        
        self.assertIsNotNone(result)
        mock_chain.assert_called_once()
    
    @patch("main.group")
    @patch("main.signature")
    def test_group_tasks(self, mock_signature, mock_group):
        """Test creating task group."""
        mock_workflow = Mock()
        mock_group.return_value = mock_workflow
        mock_workflow.delay.return_value = Mock(id="group-123")
        
        result = self.workflow.group_tasks(
            ("tasks.task1",),
            ("tasks.task2",)
        )
        
        self.assertIsNotNone(result)
        mock_group.assert_called_once()
    
    @patch("main.chord")
    @patch("main.group")
    @patch("main.signature")
    def test_chord_workflow(self, mock_sig, mock_group, mock_chord):
        """Test creating chord workflow."""
        mock_header = Mock()
        mock_group.return_value = mock_header
        mock_workflow = Mock()
        mock_chord.return_value = mock_workflow
        mock_workflow.delay.return_value = Mock(id="chord-123")
        
        result = self.workflow.chord_workflow(
            header_tasks=[("tasks.t1",), ("tasks.t2",)],
            callback_task=("tasks.callback",)
        )
        
        self.assertIsNotNone(result)
        mock_chord.assert_called_once()


class TestCeleryBeatScheduler(unittest.TestCase):
    """Test CeleryBeatScheduler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_app_manager = Mock()
        self.mock_app = Mock()
        self.mock_app_manager.get_app.return_value = self.mock_app
        self.scheduler = CeleryBeatScheduler(self.mock_app_manager)
    
    @patch("main.signature")
    def test_add_periodic_task(self, mock_signature):
        """Test adding periodic task."""
        mock_sig = Mock()
        mock_signature.return_value = mock_sig
        
        result = self.scheduler.add_periodic_task(
            task_name="tasks.cleanup",
            schedule=3600,
            name="hourly-cleanup"
        )
        
        self.assertTrue(result["success"])
        self.mock_app.add_periodic_task.assert_called_once()
    
    def test_crontab(self):
        """Test creating crontab schedule."""
        with patch("main.crontab") as mock_crontab:
            mock_cron = Mock()
            mock_crontab.return_value = mock_cron
            
            result = self.scheduler.crontab(
                minute="0",
                hour="2",
                day_of_week="*"
            )
            
            mock_crontab.assert_called_with(
                minute="0", hour="2", day_of_week="*",
                day_of_month="*", month_of_year="*"
            )


class TestCelerySkill(unittest.TestCase):
    """Test main CelerySkill class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.skill = CelerySkill(
            broker_url="redis://localhost:6379/0",
            result_backend="redis://localhost:6379/1"
        )
    
    def test_initialization(self):
        """Test skill initialization."""
        self.assertIsNotNone(self.skill.config)
        self.assertEqual(self.skill.config.broker_url, "redis://localhost:6379/0")
        self.assertEqual(self.skill.config.result_backend, "redis://localhost:6379/1")
    
    def test_task_manager(self):
        """Test getting task manager."""
        manager = self.skill.task_manager()
        self.assertIsInstance(manager, CeleryTaskManager)
    
    def test_worker_manager(self):
        """Test getting worker manager."""
        manager = self.skill.worker_manager()
        self.assertIsInstance(manager, CeleryWorkerManager)
    
    def test_workflow(self):
        """Test getting workflow manager."""
        workflow = self.skill.workflow()
        self.assertIsInstance(workflow, CeleryWorkflow)
    
    def test_scheduler(self):
        """Test getting scheduler."""
        scheduler = self.skill.scheduler()
        self.assertIsInstance(scheduler, CeleryBeatScheduler)
    
    @patch.object(CeleryWorkerManager, "ping_workers")
    def test_health_check_healthy(self, mock_ping):
        """Test health check with healthy cluster."""
        mock_ping.return_value = {
            "success": True,
            "active_workers": ["worker1@host"]
        }
        
        health = self.skill.health_check()
        
        self.assertTrue(health["healthy"])
        self.assertEqual(health["active_workers"], ["worker1@host"])
    
    @patch.object(CeleryWorkerManager, "ping_workers")
    def test_health_check_unhealthy(self, mock_ping):
        """Test health check with failed connection."""
        mock_ping.side_effect = Exception("Connection refused")
        
        health = self.skill.health_check()
        
        self.assertFalse(health["healthy"])
        self.assertIn("error", health)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios."""
    
    @patch("main.Celery")
    def test_full_workflow(self, mock_celery_class):
        """Test complete workflow."""
        mock_app = Mock()
        mock_celery_class.return_value = mock_app
        
        skill = CelerySkill(broker_url="redis://localhost:6379/0")
        
        # 1. Send task
        mock_result = Mock()
        mock_result.id = "task-123"
        mock_app.send_task.return_value = mock_result
        
        result = skill.task_manager().send_task("tasks.process", args=("data",))
        self.assertEqual(result["task_id"], "task-123")
        
        # 2. Check status
        mock_async = Mock()
        mock_async.status = "SUCCESS"
        mock_async.ready.return_value = True
        
        with patch("main.AsyncResult", return_value=mock_async):
            status = skill.task_manager().get_status("task-123")
            self.assertEqual(status["status"], "SUCCESS")


if __name__ == "__main__":
    unittest.main()
