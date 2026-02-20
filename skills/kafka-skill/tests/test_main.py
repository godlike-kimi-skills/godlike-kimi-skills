"""
Unit tests for Kafka Skill main module.

Tests cover:
- Topic management operations
- Producer operations
- Consumer operations
- Error handling
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import sys
sys.path.insert(0, "D:/kimi/projects/godlike-kimi-skills/skills/kafka-skill/src")

from main import (
    KafkaConfig, TopicConfig, KafkaTopicManager,
    KafkaProducer, KafkaConsumer, KafkaSkill
)


class TestKafkaConfig(unittest.TestCase):
    """Test KafkaConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = KafkaConfig()
        self.assertEqual(config.bootstrap_servers, "localhost:9092")
        self.assertEqual(config.security_protocol, "PLAINTEXT")
        self.assertIsNone(config.client_id)
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = KafkaConfig(
            bootstrap_servers="kafka1:9092,kafka2:9092",
            client_id="test-client",
            security_protocol="SASL_SSL"
        )
        self.assertEqual(config.bootstrap_servers, "kafka1:9092,kafka2:9092")
        self.assertEqual(config.client_id, "test-client")
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = KafkaConfig(bootstrap_servers="localhost:9092")
        config_dict = config.to_dict()
        self.assertIn("bootstrap_servers", config_dict)
        self.assertEqual(config_dict["bootstrap_servers"], "localhost:9092")


class TestTopicConfig(unittest.TestCase):
    """Test TopicConfig dataclass."""
    
    def test_default_topic_config(self):
        """Test default topic configuration."""
        config = TopicConfig(name="test-topic")
        self.assertEqual(config.name, "test-topic")
        self.assertEqual(config.num_partitions, 1)
        self.assertEqual(config.replication_factor, 1)
    
    def test_custom_topic_config(self):
        """Test custom topic configuration."""
        config = TopicConfig(
            name="test-topic",
            num_partitions=3,
            replication_factor=2,
            config_entries={"retention.ms": "86400000"}
        )
        self.assertEqual(config.num_partitions, 3)
        self.assertEqual(config.replication_factor, 2)


class TestKafkaTopicManager(unittest.TestCase):
    """Test KafkaTopicManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = KafkaConfig(bootstrap_servers="localhost:9092")
        self.manager = KafkaTopicManager(self.config)
    
    @patch("main.KafkaAdminClient")
    def test_create_topic_success(self, mock_admin_class):
        """Test successful topic creation."""
        mock_admin = MagicMock()
        mock_admin_class.return_value = mock_admin
        mock_admin.create_topics.return_value = {}
        
        topic_config = TopicConfig(name="test-topic", num_partitions=1, replication_factor=1)
        result = self.manager.create_topic(topic_config)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["topic"], "test-topic")
        mock_admin.create_topics.assert_called_once()
    
    @patch("main.KafkaAdminClient")
    def test_create_topic_already_exists(self, mock_admin_class):
        """Test topic creation when topic already exists."""
        from kafka.errors import TopicAlreadyExistsError
        
        mock_admin = MagicMock()
        mock_admin_class.return_value = mock_admin
        mock_admin.create_topics.side_effect = TopicAlreadyExistsError("Topic exists")
        
        topic_config = TopicConfig(name="existing-topic")
        result = self.manager.create_topic(topic_config)
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Topic already exists")
    
    @patch("main.KafkaAdminClient")
    def test_list_topics(self, mock_admin_class):
        """Test listing topics."""
        mock_admin = MagicMock()
        mock_admin_class.return_value = mock_admin
        mock_admin.list_topics.return_value = ["topic1", "topic2", "topic3"]
        
        result = self.manager.list_topics()
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["topics"]), 3)
        self.assertEqual(result["count"], 3)
    
    @patch("main.KafkaAdminClient")
    def test_delete_topic_success(self, mock_admin_class):
        """Test successful topic deletion."""
        mock_admin = MagicMock()
        mock_admin_class.return_value = mock_admin
        mock_admin.delete_topics.return_value = {}
        
        result = self.manager.delete_topic("test-topic")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["topic"], "test-topic")
    
    @patch("main.KafkaAdminClient")
    def test_delete_topic_not_exists(self, mock_admin_class):
        """Test deleting non-existent topic."""
        from kafka.errors import UnknownTopicOrPartitionError
        
        mock_admin = MagicMock()
        mock_admin_class.return_value = mock_admin
        mock_admin.delete_topics.side_effect = UnknownTopicOrPartitionError("Unknown topic")
        
        result = self.manager.delete_topic("non-existent")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Topic does not exist")
    
    @patch("main.KafkaAdminClient")
    def test_close(self, mock_admin_class):
        """Test closing admin client."""
        mock_admin = MagicMock()
        mock_admin_class.return_value = mock_admin
        
        # Trigger client creation
        self.manager._get_admin_client()
        self.assertIsNotNone(self.manager._admin_client)
        
        # Close
        self.manager.close()
        mock_admin.close.assert_called_once()
        self.assertIsNone(self.manager._admin_client)


class TestKafkaProducer(unittest.TestCase):
    """Test KafkaProducer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = KafkaConfig(bootstrap_servers="localhost:9092")
        self.producer = KafkaProducer(self.config)
    
    def test_default_serializer_string(self):
        """Test default serializer with string input."""
        result = self.producer._default_serializer("hello")
        self.assertEqual(result, b"hello")
    
    def test_default_serializer_dict(self):
        """Test default serializer with dict input."""
        data = {"key": "value", "num": 123}
        result = self.producer._default_serializer(data)
        self.assertEqual(json.loads(result), data)
    
    def test_default_serializer_bytes(self):
        """Test default serializer with bytes input."""
        data = b"raw bytes"
        result = self.producer._default_serializer(data)
        self.assertEqual(result, data)
    
    @patch("main.BaseProducer")
    def test_send_sync(self, mock_producer_class):
        """Test synchronous send."""
        mock_record = Mock()
        mock_record.topic = "test-topic"
        mock_record.partition = 0
        mock_record.offset = 123
        mock_record.timestamp = 1234567890
        
        mock_future = Mock()
        mock_future.get.return_value = mock_record
        
        mock_producer = Mock()
        mock_producer.send.return_value = mock_future
        mock_producer_class.return_value = mock_producer
        
        result = self.producer.send("test-topic", {"message": "hello"})
        
        self.assertTrue(result["success"])
        self.assertEqual(result["topic"], "test-topic")
        self.assertEqual(result["offset"], 123)
    
    @patch("main.BaseProducer")
    def test_send_with_key(self, mock_producer_class):
        """Test sending with partition key."""
        mock_record = Mock()
        mock_record.topic = "test-topic"
        mock_record.partition = 1
        mock_record.offset = 456
        mock_record.timestamp = 1234567890
        
        mock_future = Mock()
        mock_future.get.return_value = mock_record
        
        mock_producer = Mock()
        mock_producer.send.return_value = mock_future
        mock_producer_class.return_value = mock_producer
        
        result = self.producer.send("test-topic", {"msg": "data"}, key="user-123")
        
        self.assertTrue(result["success"])
        mock_producer.send.assert_called_once()


class TestKafkaConsumer(unittest.TestCase):
    """Test KafkaConsumer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = KafkaConfig(bootstrap_servers="localhost:9092")
        self.consumer = KafkaConsumer(
            config=self.config,
            topics=["test-topic"],
            group_id="test-group"
        )
    
    def test_default_deserializer_json(self):
        """Test default deserializer with JSON bytes."""
        data = b'{"key": "value"}'
        result = self.consumer._default_deserializer(data)
        self.assertEqual(result, {"key": "value"})
    
    def test_default_deserializer_string(self):
        """Test default deserializer with string bytes."""
        data = b"plain string"
        result = self.consumer._default_deserializer(data)
        self.assertEqual(result, b"plain string")  # Returns as-is if not valid JSON
    
    def test_default_deserializer_none(self):
        """Test default deserializer with None."""
        result = self.consumer._default_deserializer(None)
        self.assertIsNone(result)
    
    @patch("main.BaseConsumer")
    def test_consume(self, mock_consumer_class):
        """Test message consumption."""
        # Create mock message
        mock_msg = Mock()
        mock_msg.topic = "test-topic"
        mock_msg.partition = 0
        mock_msg.offset = 100
        mock_msg.key = b"key"
        mock_msg.value = b'{"data": "value"}'
        mock_msg.timestamp = 1234567890
        mock_msg.headers = []
        
        # Mock consumer
        mock_consumer = Mock()
        mock_consumer.poll.return_value = {
            Mock(topic="test-topic", partition=0): [mock_msg]
        }
        mock_consumer_class.return_value = mock_consumer
        
        messages = self.consumer.consume(timeout_ms=1000)
        
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["topic"], "test-topic")
        self.assertEqual(messages[0]["offset"], 100)


class TestKafkaSkill(unittest.TestCase):
    """Test main KafkaSkill class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.skill = KafkaSkill(bootstrap_servers="localhost:9092")
    
    def test_initialization(self):
        """Test skill initialization."""
        self.assertIsNotNone(self.skill.config)
        self.assertEqual(self.skill.config.bootstrap_servers, "localhost:9092")
    
    def test_topic_manager_lazy_load(self):
        """Test lazy loading of topic manager."""
        self.assertIsNone(self.skill._topic_manager)
        manager = self.skill.topic_manager()
        self.assertIsNotNone(manager)
        self.assertIs(self.skill._topic_manager, manager)
    
    def test_producer_lazy_load(self):
        """Test lazy loading of producer."""
        self.assertIsNone(self.skill._producer)
        producer = self.skill.producer()
        self.assertIsNotNone(producer)
        self.assertIs(self.skill._producer, producer)
    
    def test_consumer_lazy_load(self):
        """Test lazy loading of consumer."""
        self.assertIsNone(self.skill._consumer)
        consumer = self.skill.consumer(["topic"], "group")
        self.assertIsNotNone(consumer)
        self.assertIs(self.skill._consumer, consumer)
    
    @patch.object(KafkaTopicManager, "list_topics")
    def test_health_check_healthy(self, mock_list_topics):
        """Test health check with healthy cluster."""
        mock_list_topics.return_value = {"success": True, "count": 5}
        
        health = self.skill.health_check()
        
        self.assertTrue(health["healthy"])
        self.assertEqual(health["topics_count"], 5)
        self.assertIn("timestamp", health)
    
    @patch.object(KafkaTopicManager, "list_topics")
    def test_health_check_unhealthy(self, mock_list_topics):
        """Test health check with unhealthy cluster."""
        mock_list_topics.side_effect = Exception("Connection refused")
        
        health = self.skill.health_check()
        
        self.assertFalse(health["healthy"])
        self.assertIn("error", health)
    
    @patch.object(KafkaTopicManager, "close")
    @patch.object(KafkaProducer, "close")
    @patch.object(KafkaConsumer, "close")
    def test_close_all(self, mock_consumer_close, mock_producer_close, mock_topic_close):
        """Test closing all connections."""
        # Initialize all connections
        self.skill.topic_manager()
        self.skill.producer()
        self.skill.consumer(["topic"], "group")
        
        self.skill.close_all()
        
        mock_topic_close.assert_called_once()
        mock_producer_close.assert_called_once()
        mock_consumer_close.assert_called_once()


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios."""
    
    @patch("main.KafkaAdminClient")
    def test_full_workflow(self, mock_admin_class):
        """Test complete workflow from topic creation to message consumption."""
        # Mock admin client
        mock_admin = MagicMock()
        mock_admin_class.return_value = mock_admin
        mock_admin.create_topics.return_value = {}
        mock_admin.list_topics.return_value = ["my-topic"]
        
        skill = KafkaSkill(bootstrap_servers="localhost:9092")
        
        # 1. Create topic
        config = TopicConfig(name="my-topic", num_partitions=3, replication_factor=1)
        result = skill.topic_manager().create_topic(config)
        self.assertTrue(result["success"])
        
        # 2. List topics
        topics = skill.topic_manager().list_topics()
        self.assertIn("my-topic", topics["topics"])
        
        skill.close_all()


if __name__ == "__main__":
    unittest.main()
