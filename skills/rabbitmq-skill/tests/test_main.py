"""
Unit tests for RabbitMQ Skill main module.

Tests cover:
- Configuration classes
- Connection management
- Queue operations
- Exchange operations
- Publishing and consuming
- RPC pattern
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, "D:/kimi/projects/godlike-kimi-skills/skills/rabbitmq-skill/src")

from main import (
    RabbitMQConfig, QueueConfig, ExchangeConfig,
    RabbitMQConnection, RabbitMQQueueManager, RabbitMQExchangeManager,
    RabbitMQPublisher, RabbitMQConsumer, RabbitMQRPC, RabbitMQSkill
)


class TestRabbitMQConfig(unittest.TestCase):
    """Test RabbitMQConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = RabbitMQConfig()
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 5672)
        self.assertEqual(config.username, "guest")
        self.assertEqual(config.password, "guest")
        self.assertEqual(config.virtual_host, "/")
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = RabbitMQConfig(
            host="rabbitmq.example.com",
            port=5673,
            username="admin",
            password="secret",
            virtual_host="/production"
        )
        self.assertEqual(config.host, "rabbitmq.example.com")
        self.assertEqual(config.port, 5673)
        self.assertEqual(config.username, "admin")
        self.assertEqual(config.virtual_host, "/production")
    
    def test_to_connection_params(self):
        """Test conversion to ConnectionParameters."""
        config = RabbitMQConfig(host="localhost", port=5672)
        params = config.to_connection_params()
        self.assertEqual(params.host, "localhost")
        self.assertEqual(params.port, 5672)


class TestQueueConfig(unittest.TestCase):
    """Test QueueConfig dataclass."""
    
    def test_default_config(self):
        """Test default queue configuration."""
        config = QueueConfig(name="test-queue")
        self.assertEqual(config.name, "test-queue")
        self.assertTrue(config.durable)
        self.assertFalse(config.exclusive)
        self.assertFalse(config.auto_delete)
    
    def test_build_arguments_empty(self):
        """Test building arguments with no special settings."""
        config = QueueConfig(name="test")
        args = config.build_arguments()
        self.assertEqual(args, {})
    
    def test_build_arguments_with_ttl(self):
        """Test building arguments with TTL."""
        config = QueueConfig(name="test", message_ttl=60000)
        args = config.build_arguments()
        self.assertEqual(args["x-message-ttl"], 60000)
    
    def test_build_arguments_with_dlq(self):
        """Test building arguments with dead letter settings."""
        config = QueueConfig(
            name="test",
            dead_letter_exchange="dlx",
            dead_letter_routing_key="dlq"
        )
        args = config.build_arguments()
        self.assertEqual(args["x-dead-letter-exchange"], "dlx")
        self.assertEqual(args["x-dead-letter-routing-key"], "dlq")
    
    def test_build_arguments_full(self):
        """Test building arguments with all settings."""
        config = QueueConfig(
            name="test",
            message_ttl=30000,
            max_length=1000,
            dead_letter_exchange="dlx",
            arguments={"x-max-priority": 10}
        )
        args = config.build_arguments()
        self.assertEqual(args["x-message-ttl"], 30000)
        self.assertEqual(args["x-max-length"], 1000)
        self.assertEqual(args["x-dead-letter-exchange"], "dlx")
        self.assertEqual(args["x-max-priority"], 10)


class TestExchangeConfig(unittest.TestCase):
    """Test ExchangeConfig dataclass."""
    
    def test_default_config(self):
        """Test default exchange configuration."""
        config = ExchangeConfig(name="test-ex")
        self.assertEqual(config.name, "test-ex")
        self.assertEqual(config.exchange_type, "direct")
        self.assertTrue(config.durable)
        self.assertFalse(config.auto_delete)
    
    def test_get_exchange_type_direct(self):
        """Test getting direct exchange type."""
        config = ExchangeConfig(name="ex", exchange_type="direct")
        from pika.exchange_type import ExchangeType
        self.assertEqual(config.get_exchange_type(), ExchangeType.direct)
    
    def test_get_exchange_type_fanout(self):
        """Test getting fanout exchange type."""
        config = ExchangeConfig(name="ex", exchange_type="fanout")
        from pika.exchange_type import ExchangeType
        self.assertEqual(config.get_exchange_type(), ExchangeType.fanout)
    
    def test_get_exchange_type_topic(self):
        """Test getting topic exchange type."""
        config = ExchangeConfig(name="ex", exchange_type="topic")
        from pika.exchange_type import ExchangeType
        self.assertEqual(config.get_exchange_type(), ExchangeType.topic)


class TestRabbitMQConnection(unittest.TestCase):
    """Test RabbitMQConnection class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = RabbitMQConfig(host="localhost", port=5672)
        self.connection = RabbitMQConnection(self.config)
    
    @patch("main.BlockingConnection")
    def test_connect_success(self, mock_conn_class):
        """Test successful connection."""
        mock_conn = Mock()
        mock_conn_class.return_value = mock_conn
        
        result = self.connection.connect()
        
        self.assertEqual(result, mock_conn)
        mock_conn_class.assert_called_once()
    
    @patch("main.BlockingConnection")
    def test_get_connection_reuses(self, mock_conn_class):
        """Test connection reuse."""
        mock_conn = Mock()
        mock_conn.is_open = True
        mock_conn_class.return_value = mock_conn
        
        conn1 = self.connection.get_connection()
        conn2 = self.connection.get_connection()
        
        self.assertEqual(conn1, conn2)
        mock_conn_class.assert_called_once()
    
    @patch("main.BlockingConnection")
    def test_get_connection_reconnects(self, mock_conn_class):
        """Test reconnection when connection closed."""
        mock_conn = Mock()
        mock_conn.is_open = False
        mock_conn_class.return_value = mock_conn
        
        self.connection._connection = mock_conn
        self.connection.get_connection()
        
        self.assertEqual(mock_conn_class.call_count, 1)
    
    def test_context_manager(self):
        """Test connection as context manager."""
        with patch("main.BlockingConnection") as mock_conn_class:
            mock_conn = Mock()
            mock_conn_class.return_value = mock_conn
            
            with RabbitMQConnection(self.config) as conn:
                self.assertIsInstance(conn, RabbitMQConnection)
    
    def test_close(self):
        """Test closing connection."""
        mock_conn = Mock()
        mock_conn.is_closed = False
        mock_channel = Mock()
        mock_channel.is_closed = False
        
        self.connection._connection = mock_conn
        self.connection._channel = mock_channel
        
        self.connection.close()
        
        mock_channel.close.assert_called_once()
        mock_conn.close.assert_called_once()


class TestRabbitMQQueueManager(unittest.TestCase):
    """Test RabbitMQQueueManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_connection = Mock()
        self.mock_channel = Mock()
        self.mock_connection.get_channel.return_value = self.mock_channel
        self.manager = RabbitMQQueueManager(self.mock_connection)
    
    def test_declare_success(self):
        """Test successful queue declaration."""
        mock_result = Mock()
        mock_result.method.message_count = 10
        mock_result.method.consumer_count = 2
        self.mock_channel.queue_declare.return_value = mock_result
        
        config = QueueConfig(name="test-queue")
        result = self.manager.declare(config)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["queue"], "test-queue")
        self.assertEqual(result["message_count"], 10)
        self.mock_channel.queue_declare.assert_called_once()
    
    def test_declare_failure(self):
        """Test failed queue declaration."""
        from pika.exceptions import AMQPChannelError
        self.mock_channel.queue_declare.side_effect = AMQPChannelError("Access refused")
        
        config = QueueConfig(name="test-queue")
        result = self.manager.declare(config)
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_delete_success(self):
        """Test successful queue deletion."""
        result = self.manager.delete("test-queue")
        
        self.assertTrue(result["success"])
        self.mock_channel.queue_delete.assert_called_with(
            queue="test-queue", if_unused=False, if_empty=False
        )
    
    def test_purge(self):
        """Test queue purge."""
        mock_result = Mock()
        mock_result.method.message_count = 5
        self.mock_channel.queue_purge.return_value = mock_result
        
        result = self.manager.purge("test-queue")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["messages_removed"], 5)
    
    def test_bind(self):
        """Test queue binding."""
        result = self.manager.bind("queue1", "ex1", "routing.key")
        
        self.assertTrue(result["success"])
        self.mock_channel.queue_bind.assert_called_with(
            queue="queue1", exchange="ex1", routing_key="routing.key", arguments=None
        )
    
    def test_unbind(self):
        """Test queue unbinding."""
        result = self.manager.unbind("queue1", "ex1", "routing.key")
        
        self.assertTrue(result["success"])
        self.mock_channel.queue_unbind.assert_called_with(
            queue="queue1", exchange="ex1", routing_key="routing.key"
        )


class TestRabbitMQExchangeManager(unittest.TestCase):
    """Test RabbitMQExchangeManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_connection = Mock()
        self.mock_channel = Mock()
        self.mock_connection.get_channel.return_value = self.mock_channel
        self.manager = RabbitMQExchangeManager(self.mock_connection)
    
    def test_declare_success(self):
        """Test successful exchange declaration."""
        config = ExchangeConfig(name="test-ex", exchange_type="topic")
        result = self.manager.declare(config)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["exchange"], "test-ex")
        self.assertEqual(result["type"], "topic")
    
    def test_delete(self):
        """Test exchange deletion."""
        result = self.manager.delete("test-ex")
        
        self.assertTrue(result["success"])
        self.mock_channel.exchange_delete.assert_called_with(
            exchange="test-ex", if_unused=False
        )


class TestRabbitMQPublisher(unittest.TestCase):
    """Test RabbitMQPublisher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_connection = Mock()
        self.mock_channel = Mock()
        self.mock_connection.get_channel.return_value = self.mock_channel
        self.publisher = RabbitMQPublisher(self.mock_connection)
    
    def test_publish_dict(self):
        """Test publishing dictionary."""
        result = self.publisher.publish(
            exchange="",
            routing_key="test-queue",
            body={"key": "value"}
        )
        
        self.assertTrue(result["success"])
        call_args = self.mock_channel.basic_publish.call_args
        self.assertEqual(call_args[1]["exchange"], "")
        self.assertEqual(call_args[1]["routing_key"], "test-queue")
    
    def test_publish_string(self):
        """Test publishing string."""
        result = self.publisher.publish(
            exchange="",
            routing_key="test-queue",
            body="Hello World"
        )
        
        self.assertTrue(result["success"])
        call_args = self.mock_channel.basic_publish.call_args
        self.assertEqual(call_args[1]["body"], b"Hello World")
    
    def test_publish_with_headers(self):
        """Test publishing with headers."""
        result = self.publisher.publish(
            exchange="ex",
            routing_key="key",
            body="msg",
            headers={"source": "test"},
            message_id="msg-001"
        )
        
        self.assertTrue(result["success"])
        call_kwargs = self.mock_channel.basic_publish.call_args[1]
        self.assertIn("properties", call_kwargs)
    
    def test_send_to_queue(self):
        """Test convenience method to send to queue."""
        result = self.publisher.send_to_queue("my-queue", {"data": "value"})
        
        self.assertTrue(result["success"])
        call_args = self.mock_channel.basic_publish.call_args
        self.assertEqual(call_args[1]["exchange"], "")
        self.assertEqual(call_args[1]["routing_key"], "my-queue")


class TestRabbitMQConsumer(unittest.TestCase):
    """Test RabbitMQConsumer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_connection = Mock()
        self.mock_channel = Mock()
        self.mock_connection.get_channel.return_value = self.mock_channel
        self.consumer = RabbitMQConsumer(self.mock_connection, prefetch_count=5)
    
    def test_consume_one_with_message(self):
        """Test consuming single message."""
        mock_method = Mock()
        mock_method.delivery_tag = 123
        mock_method.exchange = ""
        mock_method.routing_key = "test-queue"
        mock_method.redelivered = False
        
        mock_props = Mock()
        mock_props.message_id = "msg-001"
        mock_props.headers = {}
        mock_props.timestamp = None
        mock_props.content_type = None
        mock_props.correlation_id = None
        mock_props.reply_to = None
        
        self.mock_channel.basic_get.return_value = (mock_method, mock_props, b'{"test": "data"}')
        
        message = self.consumer.consume_one("test-queue")
        
        self.assertIsNotNone(message)
        self.assertEqual(message["delivery_tag"], 123)
        self.assertEqual(message["body"], {"test": "data"})
    
    def test_consume_one_empty(self):
        """Test consuming when queue is empty."""
        self.mock_channel.basic_get.return_value = (None, None, None)
        
        message = self.consumer.consume_one("test-queue")
        
        self.assertIsNone(message)
    
    def test_consume_batch(self):
        """Test batch consumption."""
        mock_method = Mock()
        mock_method.delivery_tag = 1
        mock_method.exchange = ""
        mock_method.routing_key = "queue"
        mock_method.redelivered = False
        
        mock_props = Mock()
        mock_props.message_id = None
        mock_props.headers = {}
        mock_props.timestamp = None
        mock_props.content_type = None
        mock_props.correlation_id = None
        mock_props.reply_to = None
        
        # Return message first time, empty second time
        self.mock_channel.basic_get.side_effect = [
            (mock_method, mock_props, b'{"i": 1}'),
            (None, None, None)
        ]
        
        messages = self.consumer.consume_batch("queue", batch_size=5, timeout=1)
        
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["body"], {"i": 1})
    
    def test_ack(self):
        """Test message acknowledgment."""
        self.consumer.ack(self.mock_channel, 123)
        self.mock_channel.basic_ack.assert_called_with(delivery_tag=123)
    
    def test_nack_requeue(self):
        """Test negative acknowledgment with requeue."""
        self.consumer.nack(self.mock_channel, 456, requeue=True)
        self.mock_channel.basic_nack.assert_called_with(delivery_tag=456, requeue=True)


class TestRabbitMQSkill(unittest.TestCase):
    """Test main RabbitMQSkill class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.skill = RabbitMQSkill(
            host="localhost",
            port=5672,
            username="guest",
            password="guest"
        )
    
    def test_initialization(self):
        """Test skill initialization."""
        self.assertIsNotNone(self.skill.config)
        self.assertEqual(self.skill.config.host, "localhost")
        self.assertEqual(self.skill.config.port, 5672)
    
    def test_queue_manager(self):
        """Test getting queue manager."""
        manager = self.skill.queue_manager()
        self.assertIsInstance(manager, RabbitMQQueueManager)
        # Should return same instance
        self.assertIs(self.skill.queue_manager(), manager)
    
    def test_exchange_manager(self):
        """Test getting exchange manager."""
        manager = self.skill.exchange_manager()
        self.assertIsInstance(manager, RabbitMQExchangeManager)
    
    def test_publisher(self):
        """Test getting publisher."""
        publisher = self.skill.publisher()
        self.assertIsInstance(publisher, RabbitMQPublisher)
    
    def test_consumer(self):
        """Test getting consumer."""
        consumer = self.skill.consumer(prefetch_count=10)
        self.assertIsInstance(consumer, RabbitMQConsumer)
        self.assertEqual(consumer.prefetch_count, 10)
    
    def test_rpc(self):
        """Test getting RPC handler."""
        rpc = self.skill.rpc()
        self.assertIsInstance(rpc, RabbitMQRPC)
    
    @patch.object(RabbitMQConnection, "get_connection")
    def test_health_check_healthy(self, mock_get_conn):
        """Test health check with healthy connection."""
        mock_conn = Mock()
        mock_conn.is_open = True
        mock_get_conn.return_value = mock_conn
        
        health = self.skill.health_check()
        
        self.assertTrue(health["healthy"])
        self.assertEqual(health["host"], "localhost")
        self.assertIn("timestamp", health)
    
    @patch.object(RabbitMQConnection, "get_connection")
    def test_health_check_unhealthy(self, mock_get_conn):
        """Test health check with failed connection."""
        mock_get_conn.side_effect = Exception("Connection refused")
        
        health = self.skill.health_check()
        
        self.assertFalse(health["healthy"])
        self.assertIn("error", health)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios."""
    
    @patch("main.BlockingConnection")
    def test_full_workflow(self, mock_conn_class):
        """Test complete workflow."""
        mock_conn = Mock()
        mock_channel = Mock()
        mock_conn.channel.return_value = mock_channel
        mock_conn_class.return_value = mock_conn
        
        skill = RabbitMQSkill(host="localhost")
        
        # 1. Declare exchange
        skill.exchange_manager().declare(
            ExchangeConfig(name="events", exchange_type="topic")
        )
        
        # 2. Declare queue
        skill.queue_manager().declare(
            QueueConfig(name="event-queue", durable=True)
        )
        
        # 3. Bind queue
        skill.queue_manager().bind("event-queue", "events", "user.*")
        
        # 4. Publish message
        skill.publisher().publish("events", "user.login", {"user": "alice"})
        
        # Verify all operations
        self.assertTrue(mock_channel.exchange_declare.called)
        self.assertTrue(mock_channel.queue_declare.called)
        self.assertTrue(mock_channel.queue_bind.called)
        self.assertTrue(mock_channel.basic_publish.called)


if __name__ == "__main__":
    unittest.main()
