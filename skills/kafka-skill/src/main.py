"""
Apache Kafka Skill - Main Implementation

Provides comprehensive Kafka operations including:
- Topic management (create, delete, list, describe)
- Producer operations (sync/async, batching, compression)
- Consumer operations (simple, consumer groups, manual offset)
- Administrative operations (cluster info, config management)
"""

import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Union
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime

from kafka import KafkaProducer as BaseProducer
from kafka import KafkaConsumer as BaseConsumer
from kafka.admin import KafkaAdminClient, NewTopic, NewPartitions
from kafka.errors import (
    KafkaError, TopicAlreadyExistsError, UnknownTopicOrPartitionError,
    NoBrokersAvailable, KafkaConnectionError
)
from kafka.structs import TopicPartition, OffsetAndMetadata


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class KafkaConfig:
    """Configuration for Kafka connections."""
    bootstrap_servers: Union[str, List[str]] = "localhost:9092"
    client_id: Optional[str] = None
    security_protocol: str = "PLAINTEXT"
    ssl_cafile: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_keyfile: Optional[str] = None
    sasl_mechanism: Optional[str] = None
    sasl_plain_username: Optional[str] = None
    sasl_plain_password: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class TopicConfig:
    """Configuration for topic creation."""
    name: str
    num_partitions: int = 1
    replication_factor: int = 1
    config_entries: Optional[Dict[str, str]] = None


class KafkaTopicManager:
    """Manages Kafka topics with administrative operations."""
    
    def __init__(self, config: KafkaConfig):
        self.config = config
        self._admin_client: Optional[KafkaAdminClient] = None
        
    def _get_admin_client(self) -> KafkaAdminClient:
        """Get or create admin client with connection retry."""
        if self._admin_client is None:
            try:
                self._admin_client = KafkaAdminClient(
                    bootstrap_servers=self.config.bootstrap_servers,
                    client_id=self.config.client_id or "kafka-topic-manager",
                    security_protocol=self.config.security_protocol,
                    ssl_cafile=self.config.ssl_cafile,
                    ssl_certfile=self.config.ssl_certfile,
                    ssl_keyfile=self.config.ssl_keyfile,
                    sasl_mechanism=self.config.sasl_mechanism,
                    sasl_plain_username=self.config.sasl_plain_username,
                    sasl_plain_password=self.config.sasl_plain_password,
                )
                logger.info("Kafka admin client connected successfully")
            except NoBrokersAvailable as e:
                logger.error(f"No Kafka brokers available: {e}")
                raise KafkaConnectionError(f"Failed to connect to Kafka: {e}")
        return self._admin_client
    
    def create_topic(
        self,
        topic_config: TopicConfig,
        validate_only: bool = False,
        timeout_ms: int = 30000
    ) -> Dict[str, Any]:
        """Create a new Kafka topic."""
        admin = self._get_admin_client()
        
        new_topic = NewTopic(
            name=topic_config.name,
            num_partitions=topic_config.num_partitions,
            replication_factor=topic_config.replication_factor,
            topic_configs=topic_config.config_entries or {}
        )
        
        try:
            result = admin.create_topics(
                new_topics=[new_topic],
                validate_only=validate_only,
                timeout_ms=timeout_ms
            )
            logger.info(f"Topic '{topic_config.name}' created successfully")
            return {
                "success": True,
                "topic": topic_config.name,
                "partitions": topic_config.num_partitions,
                "replication_factor": topic_config.replication_factor,
                "result": result
            }
        except TopicAlreadyExistsError:
            logger.warning(f"Topic '{topic_config.name}' already exists")
            return {
                "success": False,
                "error": "Topic already exists",
                "topic": topic_config.name
            }
        except KafkaError as e:
            logger.error(f"Failed to create topic '{topic_config.name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic_config.name
            }
    
    def delete_topic(self, topic_name: str, timeout_ms: int = 30000) -> Dict[str, Any]:
        """Delete a Kafka topic."""
        admin = self._get_admin_client()
        
        try:
            result = admin.delete_topics(
                topics=[topic_name],
                timeout_ms=timeout_ms
            )
            logger.info(f"Topic '{topic_name}' deleted successfully")
            return {
                "success": True,
                "topic": topic_name,
                "result": result
            }
        except UnknownTopicOrPartitionError:
            logger.warning(f"Topic '{topic_name}' does not exist")
            return {
                "success": False,
                "error": "Topic does not exist",
                "topic": topic_name
            }
        except KafkaError as e:
            logger.error(f"Failed to delete topic '{topic_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic_name
            }
    
    def list_topics(self) -> Dict[str, Any]:
        """List all topics in the cluster."""
        admin = self._get_admin_client()
        
        try:
            topics = admin.list_topics()
            logger.info(f"Found {len(topics)} topics")
            return {
                "success": True,
                "topics": topics,
                "count": len(topics)
            }
        except KafkaError as e:
            logger.error(f"Failed to list topics: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def describe_topic(self, topic_name: str) -> Dict[str, Any]:
        """Get detailed information about a topic."""
        admin = self._get_admin_client()
        
        try:
            # Get topic metadata
            cluster_metadata = admin.describe_cluster()
            
            # Try to get configs
            configs = admin.describe_configs(
                config_resources=[("topic", topic_name)]
            )
            
            return {
                "success": True,
                "topic": topic_name,
                "cluster_id": cluster_metadata.get("cluster_id"),
                "configs": configs
            }
        except KafkaError as e:
            logger.error(f"Failed to describe topic '{topic_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic_name
            }
    
    def increase_partitions(
        self,
        topic_name: str,
        total_partitions: int
    ) -> Dict[str, Any]:
        """Increase the number of partitions for a topic."""
        admin = self._get_admin_client()
        
        try:
            new_partitions = NewPartitions(topic_name, total_partitions)
            result = admin.create_partitions([new_partitions])
            logger.info(f"Partitions increased for topic '{topic_name}' to {total_partitions}")
            return {
                "success": True,
                "topic": topic_name,
                "total_partitions": total_partitions,
                "result": result
            }
        except KafkaError as e:
            logger.error(f"Failed to increase partitions for '{topic_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic_name
            }
    
    def close(self):
        """Close the admin client connection."""
        if self._admin_client:
            self._admin_client.close()
            self._admin_client = None
            logger.info("Kafka admin client closed")


class KafkaProducer:
    """High-level Kafka producer with advanced features."""
    
    def __init__(
        self,
        config: KafkaConfig,
        value_serializer: Optional[Callable] = None,
        key_serializer: Optional[Callable] = None,
        acks: str = "all",
        retries: int = 3,
        batch_size: int = 16384,
        linger_ms: int = 0,
        compression_type: Optional[str] = None
    ):
        self.config = config
        self.value_serializer = value_serializer or self._default_serializer
        self.key_serializer = key_serializer
        self.acks = acks
        self.retries = retries
        self.batch_size = batch_size
        self.linger_ms = linger_ms
        self.compression_type = compression_type
        self._producer: Optional[BaseProducer] = None
        
    @staticmethod
    def _default_serializer(value: Any) -> bytes:
        """Default JSON serializer."""
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            return value.encode('utf-8')
        return json.dumps(value, default=str).encode('utf-8')
    
    def _get_producer(self) -> BaseProducer:
        """Get or create producer instance."""
        if self._producer is None:
            config = {
                "bootstrap_servers": self.config.bootstrap_servers,
                "value_serializer": self.value_serializer,
                "acks": self.acks,
                "retries": self.retries,
                "batch_size": self.batch_size,
                "linger_ms": self.linger_ms,
            }
            
            if self.key_serializer:
                config["key_serializer"] = self.key_serializer
            if self.compression_type:
                config["compression_type"] = self.compression_type
            if self.config.client_id:
                config["client_id"] = self.config.client_id
                
            self._producer = BaseProducer(**config)
            logger.info("Kafka producer initialized")
        return self._producer
    
    def send(
        self,
        topic: str,
        value: Any,
        key: Optional[Any] = None,
        headers: Optional[Dict[str, bytes]] = None,
        partition: Optional[int] = None,
        timestamp_ms: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send a message to Kafka topic synchronously."""
        producer = self._get_producer()
        
        try:
            future = producer.send(
                topic=topic,
                value=value,
                key=key,
                headers=headers,
                partition=partition,
                timestamp_ms=timestamp_ms
            )
            
            # Wait for send to complete
            record_metadata = future.get(timeout=30)
            
            return {
                "success": True,
                "topic": record_metadata.topic,
                "partition": record_metadata.partition,
                "offset": record_metadata.offset,
                "timestamp": record_metadata.timestamp
            }
        except Exception as e:
            logger.error(f"Failed to send message to '{topic}': {e}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic
            }
    
    def send_async(
        self,
        topic: str,
        value: Any,
        key: Optional[Any] = None,
        headers: Optional[Dict[str, bytes]] = None,
        callback: Optional[Callable] = None
    ) -> None:
        """Send a message asynchronously with optional callback."""
        producer = self._get_producer()
        
        def on_send_success(record_metadata):
            logger.debug(f"Message sent to {record_metadata.topic}")
            if callback:
                callback(None, record_metadata)
        
        def on_send_error(exception):
            logger.error(f"Failed to send message: {exception}")
            if callback:
                callback(exception, None)
        
        producer.send(
            topic=topic,
            value=value,
            key=key,
            headers=headers
        ).add_callback(on_send_success).add_errback(on_send_error)
    
    def flush(self, timeout: int = 30):
        """Flush all pending messages."""
        if self._producer:
            self._producer.flush(timeout=timeout)
    
    def close(self):
        """Close the producer connection."""
        if self._producer:
            self._producer.close()
            self._producer = None
            logger.info("Kafka producer closed")


class KafkaConsumer:
    """High-level Kafka consumer with consumer group support."""
    
    def __init__(
        self,
        config: KafkaConfig,
        topics: List[str],
        group_id: str,
        value_deserializer: Optional[Callable] = None,
        key_deserializer: Optional[Callable] = None,
        auto_offset_reset: str = "latest",
        enable_auto_commit: bool = True,
        auto_commit_interval_ms: int = 5000,
        max_poll_records: int = 500
    ):
        self.config = config
        self.topics = topics
        self.group_id = group_id
        self.value_deserializer = value_deserializer or self._default_deserializer
        self.key_deserializer = key_deserializer
        self.auto_offset_reset = auto_offset_reset
        self.enable_auto_commit = enable_auto_commit
        self.auto_commit_interval_ms = auto_commit_interval_ms
        self.max_poll_records = max_poll_records
        self._consumer: Optional[BaseConsumer] = None
        self._running = False
        
    @staticmethod
    def _default_deserializer(value: bytes) -> Any:
        """Default JSON deserializer."""
        if value is None:
            return None
        try:
            return json.loads(value.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return value
    
    def _get_consumer(self) -> BaseConsumer:
        """Get or create consumer instance."""
        if self._consumer is None:
            config = {
                "bootstrap_servers": self.config.bootstrap_servers,
                "group_id": self.group_id,
                "value_deserializer": self.value_deserializer,
                "auto_offset_reset": self.auto_offset_reset,
                "enable_auto_commit": self.enable_auto_commit,
                "auto_commit_interval_ms": self.auto_commit_interval_ms,
                "max_poll_records": self.max_poll_records
            }
            
            if self.key_deserializer:
                config["key_deserializer"] = self.key_deserializer
            if self.config.client_id:
                config["client_id"] = self.config.client_id
                
            self._consumer = BaseConsumer(**config)
            self._consumer.subscribe(self.topics)
            logger.info(f"Kafka consumer subscribed to topics: {self.topics}")
        return self._consumer
    
    def consume(
        self,
        timeout_ms: int = 1000,
        max_records: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Consume messages from subscribed topics."""
        consumer = self._get_consumer()
        messages = []
        
        try:
            records = consumer.poll(timeout_ms=timeout_ms)
            
            for topic_partition, msgs in records.items():
                for msg in msgs:
                    message_data = {
                        "topic": msg.topic,
                        "partition": msg.partition,
                        "offset": msg.offset,
                        "key": msg.key,
                        "value": msg.value,
                        "timestamp": msg.timestamp,
                        "headers": msg.headers
                    }
                    messages.append(message_data)
                    
                    if max_records and len(messages) >= max_records:
                        return messages
                        
            return messages
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
            return []
    
    def consume_iter(self, timeout_ms: int = 1000):
        """Iterate over messages from subscribed topics."""
        consumer = self._get_consumer()
        self._running = True
        
        try:
            while self._running:
                records = consumer.poll(timeout_ms=timeout_ms)
                
                for topic_partition, msgs in records.items():
                    for msg in msgs:
                        yield {
                            "topic": msg.topic,
                            "partition": msg.partition,
                            "offset": msg.offset,
                            "key": msg.key,
                            "value": msg.value,
                            "timestamp": msg.timestamp,
                            "headers": msg.headers
                        }
        except Exception as e:
            logger.error(f"Error in consume iterator: {e}")
        finally:
            self._running = False
    
    def commit(self, offsets: Optional[Dict] = None):
        """Manually commit offsets."""
        consumer = self._get_consumer()
        if offsets:
            consumer.commit(offsets)
        else:
            consumer.commit()
    
    def pause(self, partitions: List[TopicPartition]):
        """Pause consumption from specified partitions."""
        consumer = self._get_consumer()
        consumer.pause(*partitions)
    
    def resume(self, partitions: List[TopicPartition]):
        """Resume consumption from specified partitions."""
        consumer = self._get_consumer()
        consumer.resume(*partitions)
    
    def seek(self, partition: TopicPartition, offset: int):
        """Seek to a specific offset."""
        consumer = self._get_consumer()
        consumer.seek(partition, offset)
    
    def stop(self):
        """Stop the consumer."""
        self._running = False
    
    def close(self):
        """Close the consumer connection."""
        self.stop()
        if self._consumer:
            self._consumer.close()
            self._consumer = None
            logger.info("Kafka consumer closed")


class KafkaSkill:
    """Main entry point for Kafka Skill operations."""
    
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.config = KafkaConfig(bootstrap_servers=bootstrap_servers)
        self._topic_manager: Optional[KafkaTopicManager] = None
        self._producer: Optional[KafkaProducer] = None
        self._consumer: Optional[KafkaConsumer] = None
    
    def topic_manager(self) -> KafkaTopicManager:
        """Get topic manager instance."""
        if self._topic_manager is None:
            self._topic_manager = KafkaTopicManager(self.config)
        return self._topic_manager
    
    def producer(
        self,
        value_serializer: Optional[Callable] = None,
        acks: str = "all",
        retries: int = 3
    ) -> KafkaProducer:
        """Get producer instance."""
        if self._producer is None:
            self._producer = KafkaProducer(
                config=self.config,
                value_serializer=value_serializer,
                acks=acks,
                retries=retries
            )
        return self._producer
    
    def consumer(
        self,
        topics: List[str],
        group_id: str,
        auto_offset_reset: str = "latest"
    ) -> KafkaConsumer:
        """Get consumer instance."""
        if self._consumer is None:
            self._consumer = KafkaConsumer(
                config=self.config,
                topics=topics,
                group_id=group_id,
                auto_offset_reset=auto_offset_reset
            )
        return self._consumer
    
    def health_check(self) -> Dict[str, Any]:
        """Check Kafka cluster health."""
        try:
            admin = self.topic_manager()
            topics_result = admin.list_topics()
            
            return {
                "healthy": topics_result["success"],
                "bootstrap_servers": self.config.bootstrap_servers,
                "topics_count": topics_result.get("count", 0),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "bootstrap_servers": self.config.bootstrap_servers,
                "timestamp": datetime.now().isoformat()
            }
    
    def close_all(self):
        """Close all connections."""
        if self._topic_manager:
            self._topic_manager.close()
        if self._producer:
            self._producer.close()
        if self._consumer:
            self._consumer.close()


def main():
    """CLI entry point for Kafka Skill."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Apache Kafka Skill")
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--action", required=True, choices=[
        "create_topic", "delete_topic", "list_topics", "produce", "consume"
    ])
    parser.add_argument("--topic")
    parser.add_argument("--message")
    parser.add_argument("--group-id", default="kafka-skill-group")
    
    args = parser.parse_args()
    
    skill = KafkaSkill(bootstrap_servers=args.bootstrap_servers)
    
    try:
        if args.action == "list_topics":
            result = skill.topic_manager().list_topics()
            print(json.dumps(result, indent=2))
            
        elif args.action == "create_topic" and args.topic:
            config = TopicConfig(name=args.topic, num_partitions=1, replication_factor=1)
            result = skill.topic_manager().create_topic(config)
            print(json.dumps(result, indent=2))
            
        elif args.action == "delete_topic" and args.topic:
            result = skill.topic_manager().delete_topic(args.topic)
            print(json.dumps(result, indent=2))
            
        elif args.action == "produce" and args.topic and args.message:
            result = skill.producer().send(args.topic, args.message)
            print(json.dumps(result, indent=2))
            skill.producer().flush()
            
        elif args.action == "consume" and args.topic:
            consumer = skill.consumer([args.topic], args.group_id)
            messages = consumer.consume(timeout_ms=5000, max_records=10)
            print(json.dumps(messages, indent=2, default=str))
            
    finally:
        skill.close_all()


if __name__ == "__main__":
    main()
