"""
Unit tests for Redis Queue Skill main module.

Tests cover:
- Configuration classes
- Connection management
- List queue operations
- Stream operations
- Pub/Sub operations
- Priority queues
- Task queues
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime

import sys
sys.path.insert(0, "D:/kimi/projects/godlike-kimi-skills/skills/redis-queue-skill/src")

from main import (
    RedisConfig, Task, StreamEntry,
    RedisConnection, RedisListQueue, RedisStream,
    RedisPubSub, RedisPriorityQueue, RedisTaskQueue, RedisQueueSkill
)


class TestRedisConfig(unittest.TestCase):
    """Test RedisConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = RedisConfig()
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 6379)
        self.assertEqual(config.db, 0)
        self.assertIsNone(config.password)
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = RedisConfig(
            host="redis.example.com",
            port=6380,
            db=1,
            password="secret",
            max_connections=100
        )
        self.assertEqual(config.host, "redis.example.com")
        self.assertEqual(config.port, 6380)
        self.assertEqual(config.db, 1)
        self.assertEqual(config.password, "secret")
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = RedisConfig(host="localhost", password="pass")
        config_dict = config.to_dict()
        self.assertEqual(config_dict["host"], "localhost")
        self.assertEqual(config_dict["password"], "pass")


class TestTask(unittest.TestCase):
    """Test Task dataclass."""
    
    def test_default_task(self):
        """Test default task creation."""
        task = Task(id="123", payload={"key": "value"})
        self.assertEqual(task.id, "123")
        self.assertEqual(task.payload, {"key": "value"})
        self.assertEqual(task.priority, 0)
        self.assertEqual(task.delay, 0)
        self.assertEqual(task.retries, 3)
        self.assertIsNotNone(task.created_at)
    
    def test_to_json(self):
        """Test task serialization."""
        task = Task(id="123", payload={"key": "value"}, priority=5)
        json_str = task.to_json()
        data = json.loads(json_str)
        self.assertEqual(data["id"], "123")
        self.assertEqual(data["priority"], 5)
    
    def test_from_json(self):
        """Test task deserialization."""
        json_str = '{"id": "123", "payload": {"key": "value"}, "priority": 5, "delay": 0, "retries": 3}'
        task = Task.from_json(json_str)
        self.assertEqual(task.id, "123")
        self.assertEqual(task.payload, {"key": "value"})
        self.assertEqual(task.priority, 5)


class TestStreamEntry(unittest.TestCase):
    """Test StreamEntry dataclass."""
    
    def test_from_redis(self):
        """Test creating StreamEntry from Redis response."""
        redis_entry = ("1234567890-0", ["field1", "value1", "field2", "value2"])
        entry = StreamEntry.from_redis(redis_entry)
        self.assertEqual(entry.id, "1234567890-0")
        self.assertEqual(entry.fields, {"field1": "value1", "field2": "value2"})


class TestRedisConnection(unittest.TestCase):
    """Test RedisConnection class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = RedisConfig(host="localhost", port=6379)
        self.connection = RedisConnection(self.config)
    
    @patch("main.ConnectionPool")
    @patch("main.Redis")
    def test_connect_success(self, mock_redis_class, mock_pool_class):
        """Test successful connection."""
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        mock_redis_class.return_value = mock_redis
        
        result = self.connection.connect()
        
        self.assertEqual(result, mock_redis)
        mock_redis.ping.assert_called_once()
    
    @patch("main.ConnectionPool")
    @patch("main.Redis")
    def test_get_redis_reuses(self, mock_redis_class, mock_pool_class):
        """Test Redis client reuse."""
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        mock_redis_class.return_value = mock_redis
        
        redis1 = self.connection.get_redis()
        redis2 = self.connection.get_redis()
        
        self.assertEqual(redis1, redis2)
    
    def test_close(self):
        """Test closing connection."""
        mock_pool = Mock()
        self.connection._pool = mock_pool
        self.connection._redis = Mock()
        
        self.connection.close()
        
        mock_pool.disconnect.assert_called_once()
        self.assertIsNone(self.connection._pool)
    
    @patch.object(RedisConnection, "get_redis")
    def test_health_check_healthy(self, mock_get_redis):
        """Test health check with healthy connection."""
        mock_redis = Mock()
        mock_redis.info.return_value = {
            "redis_version": "7.0.0",
            "used_memory_human": "1.5M",
            "connected_clients": 10
        }
        mock_get_redis.return_value = mock_redis
        
        health = self.connection.health_check()
        
        self.assertTrue(health["healthy"])
        self.assertEqual(health["version"], "7.0.0")
    
    @patch.object(RedisConnection, "get_redis")
    def test_health_check_unhealthy(self, mock_get_redis):
        """Test health check with failed connection."""
        mock_get_redis.side_effect = Exception("Connection refused")
        
        health = self.connection.health_check()
        
        self.assertFalse(health["healthy"])
        self.assertIn("error", health)


class TestRedisListQueue(unittest.TestCase):
    """Test RedisListQueue class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_redis = Mock()
        self.queue = RedisListQueue(self.mock_redis)
    
    def test_push_left(self):
        """Test LPUSH operation."""
        self.mock_redis.lpush.return_value = 1
        
        result = self.queue.push_left("my-queue", {"key": "value"})
        
        self.assertEqual(result, 1)
        self.mock_redis.lpush.assert_called_once()
    
    def test_push_right(self):
        """Test RPUSH operation."""
        self.mock_redis.rpush.return_value = 2
        
        result = self.queue.push_right("my-queue", "item1", "item2")
        
        self.assertEqual(result, 2)
    
    def test_pop_left(self):
        """Test LPOP operation."""
        self.mock_redis.lpop.return_value = '{"data": "value"}'
        
        result = self.queue.pop_left("my-queue")
        
        self.assertEqual(result, {"data": "value"})
    
    def test_pop_left_blocking(self):
        """Test BLPOP operation."""
        self.mock_redis.blpop.return_value = ("my-queue", "message")
        
        result = self.queue.pop_left("my-queue", timeout=5)
        
        self.assertEqual(result, "message")
    
    def test_pop_left_blocking_empty(self):
        """Test BLPOP with empty result."""
        self.mock_redis.blpop.return_value = None
        
        result = self.queue.pop_left("my-queue", timeout=1)
        
        self.assertIsNone(result)
    
    def test_length(self):
        """Test LLEN operation."""
        self.mock_redis.llen.return_value = 10
        
        result = self.queue.length("my-queue")
        
        self.assertEqual(result, 10)
    
    def test_range(self):
        """Test LRANGE operation."""
        self.mock_redis.lrange.return_value = ['"a"', '"b"', '"c"']
        
        result = self.queue.range("my-queue", 0, -1)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result, ["a", "b", "c"])
    
    def test_delete(self):
        """Test queue deletion."""
        self.mock_redis.delete.return_value = 1
        
        result = self.queue.delete("my-queue")
        
        self.assertEqual(result, 1)


class TestRedisStream(unittest.TestCase):
    """Test RedisStream class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_redis = Mock()
        self.stream = RedisStream(self.mock_redis)
    
    def test_add(self):
        """Test XADD operation."""
        self.mock_redis.xadd.return_value = "1234567890-0"
        
        result = self.stream.add("my-stream", {"field": "value"})
        
        self.assertEqual(result, "1234567890-0")
        self.mock_redis.xadd.assert_called_once()
    
    def test_read(self):
        """Test XREAD operation."""
        mock_result = [
            ("my-stream", [("1234567890-0", ["field", "value"])])
        ]
        self.mock_redis.xread.return_value = mock_result
        
        result = self.stream.read(streams={"my-stream": "0"})
        
        self.assertIn("my-stream", result)
        self.assertEqual(len(result["my-stream"]), 1)
        self.assertEqual(result["my-stream"][0].id, "1234567890-0")
    
    def test_range(self):
        """Test XRANGE operation."""
        mock_result = [
            ("1234567890-0", ["field", "value"])
        ]
        self.mock_redis.xrange.return_value = mock_result
        
        result = self.stream.range("my-stream")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "1234567890-0")
    
    def test_create_consumer_group(self):
        """Test XGROUP CREATE."""
        self.mock_redis.xgroup_create.return_value = True
        
        result = self.stream.create_consumer_group("stream", "group")
        
        self.assertTrue(result)
    
    def test_acknowledge(self):
        """Test XACK operation."""
        self.mock_redis.xack.return_value = 2
        
        result = self.stream.acknowledge("stream", "group", "id1", "id2")
        
        self.assertEqual(result, 2)
    
    def test_trim(self):
        """Test XTRIM operation."""
        self.mock_redis.xtrim.return_value = 100
        
        result = self.stream.trim("my-stream", maxlen=1000)
        
        self.assertEqual(result, 100)


class TestRedisPubSub(unittest.TestCase):
    """Test RedisPubSub class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_redis = Mock()
        self.pubsub = RedisPubSub(self.mock_redis)
    
    def test_publish(self):
        """Test PUBLISH operation."""
        self.mock_redis.publish.return_value = 2
        
        result = self.pubsub.publish("channel", {"msg": "hello"})
        
        self.assertEqual(result, 2)
        self.mock_redis.publish.assert_called_once_with("channel", '{"msg": "hello"}')
    
    def test_subscribe(self):
        """Test SUBSCRIBE operation."""
        mock_pubsub = Mock()
        self.mock_redis.pubsub.return_value = mock_pubsub
        
        result = self.pubsub.subscribe("channel1", "channel2")
        
        self.assertEqual(result, mock_pubsub)
        mock_pubsub.subscribe.assert_called_with("channel1", "channel2")
    
    def test_psubscribe(self):
        """Test PSUBSCRIBE operation."""
        mock_pubsub = Mock()
        self.mock_redis.pubsub.return_value = mock_pubsub
        
        result = self.pubsub.psubscribe("user.*", "order.*")
        
        self.assertEqual(result, mock_pubsub)
        mock_pubsub.psubscribe.assert_called_with("user.*", "order.*")


class TestRedisPriorityQueue(unittest.TestCase):
    """Test RedisPriorityQueue class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_redis = Mock()
        self.queue = RedisPriorityQueue(self.mock_redis)
    
    def test_add(self):
        """Test ZADD operation."""
        self.mock_redis.zadd.return_value = 1
        
        result = self.queue.add("priority-queue", "task1", priority=10)
        
        self.assertEqual(result, 1)
    
    def test_pop_min(self):
        """Test ZPOPMIN operation."""
        self.mock_redis.zpopmin.return_value = [("task1", 5.0), ("task2", 10.0)]
        
        result = self.queue.pop_min("priority-queue", count=2)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][1], 5.0)
    
    def test_range_by_score(self):
        """Test ZRANGEBYSCORE operation."""
        self.mock_redis.zrangebyscore.return_value = [("task1", 5.0)]
        
        result = self.queue.range_by_score("queue", 0, 10)
        
        self.assertEqual(len(result), 1)
    
    def test_count(self):
        """Test ZCARD operation."""
        self.mock_redis.zcard.return_value = 5
        
        result = self.queue.count("priority-queue")
        
        self.assertEqual(result, 5)


class TestRedisTaskQueue(unittest.TestCase):
    """Test RedisTaskQueue class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_redis = Mock()
        self.task_queue = RedisTaskQueue(self.mock_redis, prefix="test")
    
    def test_enqueue_immediate(self):
        """Test enqueue immediate task."""
        task = Task(id="123", payload={"job": "send_email"}, delay=0)
        
        result = self.task_queue.enqueue(task)
        
        self.assertEqual(result, "123")
        self.mock_redis.lpush.assert_called_once()
    
    def test_enqueue_delayed(self):
        """Test enqueue delayed task."""
        task = Task(id="456", payload={"job": "reminder"}, delay=3600)
        
        result = self.task_queue.enqueue(task)
        
        self.assertEqual(result, "456")
        self.mock_redis.zadd.assert_called_once()
    
    def test_schedule(self):
        """Test schedule convenience method."""
        self.mock_redis.zadd.return_value = 1
        
        task_id = self.task_queue.schedule(
            payload={"job": "cleanup"},
            delay=60,
            priority=5
        )
        
        self.assertIsNotNone(task_id)
    
    def test_dequeue(self):
        """Test dequeue operation."""
        task_json = '{"id": "123", "payload": {"job": "test"}, "priority": 0, "delay": 0, "retries": 3}'
        self.mock_redis.brpop.return_value = ("test:ready", task_json)
        self.mock_redis.zrangebyscore.return_value = []
        
        task = self.task_queue.dequeue(timeout=5)
        
        self.assertIsNotNone(task)
        self.assertEqual(task.id, "123")
    
    def test_complete_success(self):
        """Test completing task successfully."""
        task = Task(id="123", payload={"job": "test"})
        
        self.task_queue.complete(task, success=True)
        
        self.mock_redis.lrem.assert_called_once()
    
    def test_complete_with_retry(self):
        """Test completing failed task with retry."""
        task = Task(id="123", payload={"job": "test"}, retries=2)
        
        self.task_queue.complete(task, success=False)
        
        # Should push back to ready queue
        self.assertTrue(self.mock_redis.lpush.called)
    
    def test_get_stats(self):
        """Test getting queue statistics."""
        self.mock_redis.llen.side_effect = [5, 2]  # ready, processing
        self.mock_redis.zcard.return_value = 3  # delayed
        
        stats = self.task_queue.get_stats()
        
        self.assertEqual(stats["ready"], 5)
        self.assertEqual(stats["delayed"], 3)
        self.assertEqual(stats["processing"], 2)


class TestRedisQueueSkill(unittest.TestCase):
    """Test main RedisQueueSkill class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.skill = RedisQueueSkill(
            host="localhost",
            port=6379,
            db=0
        )
    
    def test_initialization(self):
        """Test skill initialization."""
        self.assertIsNotNone(self.skill.config)
        self.assertEqual(self.skill.config.host, "localhost")
        self.assertEqual(self.skill.config.port, 6379)
    
    def test_list_queue(self):
        """Test getting list queue operations."""
        with patch.object(self.skill.connection, "get_redis", return_value=Mock()):
            queue = self.skill.list_queue()
            self.assertIsInstance(queue, RedisListQueue)
    
    def test_stream(self):
        """Test getting stream operations."""
        with patch.object(self.skill.connection, "get_redis", return_value=Mock()):
            stream = self.skill.stream()
            self.assertIsInstance(stream, RedisStream)
    
    def test_pubsub(self):
        """Test getting pubsub operations."""
        with patch.object(self.skill.connection, "get_redis", return_value=Mock()):
            pubsub = self.skill.pubsub()
            self.assertIsInstance(pubsub, RedisPubSub)
    
    def test_priority_queue(self):
        """Test getting priority queue operations."""
        with patch.object(self.skill.connection, "get_redis", return_value=Mock()):
            queue = self.skill.priority_queue()
            self.assertIsInstance(queue, RedisPriorityQueue)
    
    def test_task_queue(self):
        """Test getting task queue operations."""
        with patch.object(self.skill.connection, "get_redis", return_value=Mock()):
            queue = self.skill.task_queue(prefix="my-tasks")
            self.assertIsInstance(queue, RedisTaskQueue)
    
    @patch.object(RedisConnection, "health_check")
    def test_health_check(self, mock_health):
        """Test health check."""
        mock_health.return_value = {"healthy": True}
        
        result = self.skill.health_check()
        
        self.assertTrue(result["healthy"])


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios."""
    
    @patch("main.ConnectionPool")
    @patch("main.Redis")
    def test_full_workflow(self, mock_redis_class, mock_pool_class):
        """Test complete workflow."""
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        mock_redis_class.return_value = mock_redis
        
        skill = RedisQueueSkill(host="localhost")
        
        # 1. Add to list queue
        skill.list_queue().push_right("tasks", {"job": "email"})
        
        # 2. Add to stream
        skill.stream().add("events", {"type": "user_action"})
        
        # 3. Publish message
        skill.pubsub().publish("updates", {"msg": "hello"})
        
        # Verify all operations called
        self.assertTrue(mock_redis.rpush.called or mock_redis.lpush.called)
        self.assertTrue(mock_redis.xadd.called)
        self.assertTrue(mock_redis.publish.called)


if __name__ == "__main__":
    unittest.main()
