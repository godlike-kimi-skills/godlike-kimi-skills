"""
RabbitMQ Skill - Main Implementation

Provides comprehensive RabbitMQ operations including:
- Queue management (declare, delete, bind, purge)
- Exchange operations (declare, delete, bind)
- Publishing (persistent, mandatory, expiration)
- Consuming (basic, ack/nack, prefetch, qos)
- RPC patterns (request-reply)
- Dead letter handling
"""

import json
import logging
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Union
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime
from functools import wraps

import pika
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import (
    AMQPConnectionError, AMQPChannelError, ChannelClosed,
    ConnectionClosed, NackError, UnroutableError
)
from pika.exchange_type import ExchangeType
from tenacity import retry, stop_after_attempt, wait_exponential


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RabbitMQConfig:
    """Configuration for RabbitMQ connections."""
    host: str = "localhost"
    port: int = 5672
    username: str = "guest"
    password: str = "guest"
    virtual_host: str = "/"
    heartbeat: int = 600
    blocked_connection_timeout: int = 300
    connection_attempts: int = 3
    retry_delay: int = 5
    ssl_options: Optional[Dict] = None
    
    def to_connection_params(self) -> ConnectionParameters:
        """Convert config to pika ConnectionParameters."""
        credentials = PlainCredentials(self.username, self.password)
        return ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.virtual_host,
            credentials=credentials,
            heartbeat=self.heartbeat,
            blocked_connection_timeout=self.blocked_connection_timeout,
            connection_attempts=self.connection_attempts,
            retry_delay=self.retry_delay,
            ssl_options=self.ssl_options
        )


@dataclass
class QueueConfig:
    """Configuration for queue declaration."""
    name: str
    durable: bool = True
    exclusive: bool = False
    auto_delete: bool = False
    arguments: Optional[Dict[str, Any]] = None
    message_ttl: Optional[int] = None
    max_length: Optional[int] = None
    dead_letter_exchange: Optional[str] = None
    dead_letter_routing_key: Optional[str] = None
    
    def build_arguments(self) -> Dict[str, Any]:
        """Build queue arguments dict."""
        args = self.arguments or {}
        if self.message_ttl:
            args["x-message-ttl"] = self.message_ttl
        if self.max_length:
            args["x-max-length"] = self.max_length
        if self.dead_letter_exchange:
            args["x-dead-letter-exchange"] = self.dead_letter_exchange
        if self.dead_letter_routing_key:
            args["x-dead-letter-routing-key"] = self.dead_letter_routing_key
        return args


@dataclass
class ExchangeConfig:
    """Configuration for exchange declaration."""
    name: str
    exchange_type: str = "direct"  # direct, fanout, topic, headers
    durable: bool = True
    auto_delete: bool = False
    internal: bool = False
    arguments: Optional[Dict[str, Any]] = None
    
    def get_exchange_type(self) -> ExchangeType:
        """Get pika ExchangeType."""
        type_map = {
            "direct": ExchangeType.direct,
            "fanout": ExchangeType.fanout,
            "topic": ExchangeType.topic,
            "headers": ExchangeType.headers
        }
        return type_map.get(self.exchange_type, ExchangeType.direct)


class RabbitMQConnection:
    """Manages RabbitMQ connection lifecycle."""
    
    def __init__(self, config: RabbitMQConfig):
        self.config = config
        self._connection: Optional[BlockingConnection] = None
        self._channel: Optional[BlockingChannel] = None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def connect(self) -> BlockingConnection:
        """Establish connection with retry logic."""
        try:
            params = self.config.to_connection_params()
            self._connection = BlockingConnection(params)
            logger.info(f"Connected to RabbitMQ at {self.config.host}:{self.config.port}")
            return self._connection
        except AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def get_connection(self) -> BlockingConnection:
        """Get existing or create new connection."""
        if self._connection is None or self._connection.is_closed:
            self.connect()
        return self._connection
    
    def get_channel(self) -> BlockingChannel:
        """Get channel from connection."""
        if self._channel is None or self._channel.is_closed:
            conn = self.get_connection()
            self._channel = conn.channel()
            # Enable publisher confirms for reliability
            self._channel.confirm_delivery()
            logger.debug("Channel created with publisher confirms enabled")
        return self._channel
    
    def close(self):
        """Close connection and channel."""
        if self._channel and not self._channel.is_closed:
            self._channel.close()
            self._channel = None
        if self._connection and not self._connection.is_closed:
            self._connection.close()
            self._connection = None
        logger.info("RabbitMQ connection closed")
    
    def __enter__(self):
        self.get_connection()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class RabbitMQQueueManager:
    """Manages RabbitMQ queues."""
    
    def __init__(self, connection: RabbitMQConnection):
        self.connection = connection
    
    def declare(self, config: QueueConfig) -> Dict[str, Any]:
        """Declare a queue with given configuration."""
        channel = self.connection.get_channel()
        
        try:
            result = channel.queue_declare(
                queue=config.name,
                durable=config.durable,
                exclusive=config.exclusive,
                auto_delete=config.auto_delete,
                arguments=config.build_arguments()
            )
            
            logger.info(f"Queue '{config.name}' declared with {result.method.message_count} messages")
            return {
                "success": True,
                "queue": config.name,
                "message_count": result.method.message_count,
                "consumer_count": result.method.consumer_count
            }
        except AMQPChannelError as e:
            logger.error(f"Failed to declare queue '{config.name}': {e}")
            return {"success": False, "error": str(e), "queue": config.name}
    
    def delete(self, queue_name: str, if_unused: bool = False, if_empty: bool = False) -> Dict[str, Any]:
        """Delete a queue."""
        channel = self.connection.get_channel()
        
        try:
            channel.queue_delete(
                queue=queue_name,
                if_unused=if_unused,
                if_empty=if_empty
            )
            logger.info(f"Queue '{queue_name}' deleted")
            return {"success": True, "queue": queue_name}
        except AMQPChannelError as e:
            logger.error(f"Failed to delete queue '{queue_name}': {e}")
            return {"success": False, "error": str(e), "queue": queue_name}
    
    def purge(self, queue_name: str) -> Dict[str, Any]:
        """Purge all messages from a queue."""
        channel = self.connection.get_channel()
        
        try:
            result = channel.queue_purge(queue=queue_name)
            logger.info(f"Queue '{queue_name}' purged, {result.method.message_count} messages removed")
            return {
                "success": True,
                "queue": queue_name,
                "messages_removed": result.method.message_count
            }
        except AMQPChannelError as e:
            logger.error(f"Failed to purge queue '{queue_name}': {e}")
            return {"success": False, "error": str(e), "queue": queue_name}
    
    def bind(
        self,
        queue_name: str,
        exchange_name: str,
        routing_key: str = "",
        arguments: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Bind a queue to an exchange."""
        channel = self.connection.get_channel()
        
        try:
            channel.queue_bind(
                queue=queue_name,
                exchange=exchange_name,
                routing_key=routing_key,
                arguments=arguments
            )
            logger.info(f"Queue '{queue_name}' bound to exchange '{exchange_name}' with key '{routing_key}'")
            return {
                "success": True,
                "queue": queue_name,
                "exchange": exchange_name,
                "routing_key": routing_key
            }
        except AMQPChannelError as e:
            logger.error(f"Failed to bind queue: {e}")
            return {"success": False, "error": str(e)}
    
    def unbind(
        self,
        queue_name: str,
        exchange_name: str,
        routing_key: str = ""
    ) -> Dict[str, Any]:
        """Unbind a queue from an exchange."""
        channel = self.connection.get_channel()
        
        try:
            channel.queue_unbind(
                queue=queue_name,
                exchange=exchange_name,
                routing_key=routing_key
            )
            logger.info(f"Queue '{queue_name}' unbound from exchange '{exchange_name}'")
            return {"success": True, "queue": queue_name, "exchange": exchange_name}
        except AMQPChannelError as e:
            return {"success": False, "error": str(e)}


class RabbitMQExchangeManager:
    """Manages RabbitMQ exchanges."""
    
    def __init__(self, connection: RabbitMQConnection):
        self.connection = connection
    
    def declare(self, config: ExchangeConfig) -> Dict[str, Any]:
        """Declare an exchange."""
        channel = self.connection.get_channel()
        
        try:
            channel.exchange_declare(
                exchange=config.name,
                exchange_type=config.get_exchange_type(),
                durable=config.durable,
                auto_delete=config.auto_delete,
                internal=config.internal,
                arguments=config.arguments
            )
            logger.info(f"Exchange '{config.name}' of type '{config.exchange_type}' declared")
            return {"success": True, "exchange": config.name, "type": config.exchange_type}
        except AMQPChannelError as e:
            logger.error(f"Failed to declare exchange '{config.name}': {e}")
            return {"success": False, "error": str(e), "exchange": config.name}
    
    def delete(self, exchange_name: str, if_unused: bool = False) -> Dict[str, Any]:
        """Delete an exchange."""
        channel = self.connection.get_channel()
        
        try:
            channel.exchange_delete(exchange=exchange_name, if_unused=if_unused)
            logger.info(f"Exchange '{exchange_name}' deleted")
            return {"success": True, "exchange": exchange_name}
        except AMQPChannelError as e:
            return {"success": False, "error": str(e), "exchange": exchange_name}


class RabbitMQPublisher:
    """Handles message publishing with reliability features."""
    
    def __init__(self, connection: RabbitMQConnection):
        self.connection = connection
    
    def publish(
        self,
        exchange: str,
        routing_key: str,
        body: Any,
        headers: Optional[Dict] = None,
        persistent: bool = True,
        mandatory: bool = False,
        expiration: Optional[int] = None,
        message_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        reply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """Publish a message to an exchange."""
        channel = self.connection.get_channel()
        
        # Serialize body
        if isinstance(body, dict) or isinstance(body, list):
            body = json.dumps(body).encode('utf-8')
        elif isinstance(body, str):
            body = body.encode('utf-8')
        elif not isinstance(body, bytes):
            body = str(body).encode('utf-8')
        
        # Build properties
        properties_kwargs = {"headers": headers or {}}
        if persistent:
            properties_kwargs["delivery_mode"] = 2  # Persistent
        if expiration:
            properties_kwargs["expiration"] = str(expiration)
        if message_id:
            properties_kwargs["message_id"] = message_id
        if correlation_id:
            properties_kwargs["correlation_id"] = correlation_id
        if reply_to:
            properties_kwargs["reply_to"] = reply_to
        
        properties = pika.BasicProperties(**properties_kwargs)
        
        try:
            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=body,
                properties=properties,
                mandatory=mandatory
            )
            logger.debug(f"Message published to '{exchange}' with key '{routing_key}'")
            return {
                "success": True,
                "exchange": exchange,
                "routing_key": routing_key,
                "message_id": message_id
            }
        except UnroutableError:
            logger.error(f"Message was returned: unroutable")
            return {"success": False, "error": "Message was returned (unroutable)"}
        except NackError:
            logger.error(f"Message was nack'd by broker")
            return {"success": False, "error": "Message was rejected by broker"}
        except AMQPChannelError as e:
            logger.error(f"Failed to publish message: {e}")
            return {"success": False, "error": str(e)}
    
    def send_to_queue(
        self,
        queue_name: str,
        body: Any,
        **kwargs
    ) -> Dict[str, Any]:
        """Convenience method to send directly to a queue (uses default exchange)."""
        return self.publish(
            exchange="",
            routing_key=queue_name,
            body=body,
            **kwargs
        )


class RabbitMQConsumer:
    """Handles message consumption with various patterns."""
    
    def __init__(
        self,
        connection: RabbitMQConnection,
        prefetch_count: int = 1,
        auto_ack: bool = False
    ):
        self.connection = connection
        self.prefetch_count = prefetch_count
        self.auto_ack = auto_ack
        self._consumer_tag: Optional[str] = None
    
    def _get_channel_with_qos(self) -> BlockingChannel:
        """Get channel with QoS settings."""
        channel = self.connection.get_channel()
        channel.basic_qos(prefetch_count=self.prefetch_count)
        return channel
    
    def consume_one(
        self,
        queue_name: str,
        auto_ack: Optional[bool] = None,
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Consume a single message from queue."""
        channel = self._get_channel_with_qos()
        auto_ack = auto_ack if auto_ack is not None else self.auto_ack
        
        method, properties, body = channel.basic_get(queue=queue_name, auto_ack=auto_ack)
        
        if method is None:
            return None
        
        message = self._build_message_dict(method, properties, body)
        message["channel"] = channel  # For manual ack
        return message
    
    def consume_batch(
        self,
        queue_name: str,
        batch_size: int = 10,
        timeout: int = 5
    ) -> List[Dict[str, Any]]:
        """Consume multiple messages from queue."""
        messages = []
        start_time = time.time()
        
        while len(messages) < batch_size:
            remaining = timeout - (time.time() - start_time)
            if remaining <= 0:
                break
            
            message = self.consume_one(queue_name, auto_ack=False)
            if message:
                messages.append(message)
            else:
                break
        
        return messages
    
    def start_consuming(
        self,
        queue_name: str,
        callback: Callable,
        auto_ack: Optional[bool] = None
    ):
        """Start continuous message consumption."""
        channel = self._get_channel_with_qos()
        auto_ack = auto_ack if auto_ack is not None else self.auto_ack
        
        def wrapped_callback(ch, method, properties, body):
            message = self._build_message_dict(method, properties, body)
            callback(ch, message)
        
        self._consumer_tag = channel.basic_consume(
            queue=queue_name,
            on_message_callback=wrapped_callback,
            auto_ack=auto_ack
        )
        
        logger.info(f"Started consuming from queue '{queue_name}'")
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
    
    def stop_consuming(self):
        """Stop continuous consumption."""
        channel = self.connection.get_channel()
        if self._consumer_tag:
            channel.basic_cancel(self._consumer_tag)
            self._consumer_tag = None
    
    def ack(self, channel: BlockingChannel, delivery_tag: int):
        """Manually acknowledge a message."""
        channel.basic_ack(delivery_tag=delivery_tag)
    
    def nack(
        self,
        channel: BlockingChannel,
        delivery_tag: int,
        requeue: bool = True
    ):
        """Negative acknowledge a message."""
        channel.basic_nack(delivery_tag=delivery_tag, requeue=requeue)
    
    def _build_message_dict(
        self,
        method,
        properties,
        body: bytes
    ) -> Dict[str, Any]:
        """Build message dictionary from delivery."""
        # Try to parse JSON
        try:
            decoded_body = json.loads(body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            decoded_body = body.decode('utf-8', errors='replace')
        
        return {
            "delivery_tag": method.delivery_tag,
            "exchange": method.exchange,
            "routing_key": method.routing_key,
            "redelivered": method.redelivered,
            "body": decoded_body,
            "raw_body": body,
            "message_id": properties.message_id,
            "correlation_id": properties.correlation_id,
            "reply_to": properties.reply_to,
            "headers": properties.headers,
            "timestamp": properties.timestamp,
            "content_type": properties.content_type
        }


class RabbitMQRPC:
    """Implements RPC pattern over RabbitMQ."""
    
    def __init__(self, connection: RabbitMQConnection):
        self.connection = connection
        self._pending_responses: Dict[str, Any] = {}
    
    def call(
        self,
        queue_name: str,
        payload: Any,
        timeout: int = 30
    ) -> Optional[Dict[str, Any]]:
        """Make an RPC call and wait for response."""
        channel = self.connection.get_channel()
        
        # Create exclusive callback queue
        result = channel.queue_declare(queue="", exclusive=True)
        callback_queue = result.method.queue
        
        correlation_id = str(uuid.uuid4())
        self._pending_responses[correlation_id] = None
        
        # Set up response consumer
        def on_response(ch, method, properties, body):
            if properties.correlation_id == correlation_id:
                self._pending_responses[correlation_id] = body
                ch.basic_ack(delivery_tag=method.delivery_tag)
        
        channel.basic_consume(
            queue=callback_queue,
            on_message_callback=on_response,
            auto_ack=False
        )
        
        # Send request
        body = json.dumps(payload).encode('utf-8')
        properties = pika.BasicProperties(
            reply_to=callback_queue,
            correlation_id=correlation_id,
            content_type="application/json"
        )
        
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            properties=properties,
            body=body
        )
        
        # Wait for response
        start_time = time.time()
        while self._pending_responses[correlation_id] is None:
            self.connection.get_connection().process_data_events(time_limit=0.1)
            if time.time() - start_time > timeout:
                del self._pending_responses[correlation_id]
                logger.warning(f"RPC call timeout after {timeout}s")
                return None
        
        response_body = self._pending_responses.pop(correlation_id)
        try:
            return json.loads(response_body.decode('utf-8'))
        except json.JSONDecodeError:
            return {"raw_response": response_body.decode('utf-8')}


class RabbitMQSkill:
    """Main entry point for RabbitMQ operations."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        virtual_host: str = "/"
    ):
        self.config = RabbitMQConfig(
            host=host,
            port=port,
            username=username,
            password=password,
            virtual_host=virtual_host
        )
        self.connection = RabbitMQConnection(self.config)
    
    def queue_manager(self) -> RabbitMQQueueManager:
        """Get queue manager."""
        return RabbitMQQueueManager(self.connection)
    
    def exchange_manager(self) -> RabbitMQExchangeManager:
        """Get exchange manager."""
        return RabbitMQExchangeManager(self.connection)
    
    def publisher(self) -> RabbitMQPublisher:
        """Get publisher."""
        return RabbitMQPublisher(self.connection)
    
    def consumer(self, prefetch_count: int = 1, auto_ack: bool = False) -> RabbitMQConsumer:
        """Get consumer."""
        return RabbitMQConsumer(self.connection, prefetch_count, auto_ack)
    
    def rpc(self) -> RabbitMQRPC:
        """Get RPC handler."""
        return RabbitMQRPC(self.connection)
    
    def health_check(self) -> Dict[str, Any]:
        """Check RabbitMQ connection health."""
        try:
            conn = self.connection.get_connection()
            is_open = conn.is_open
            return {
                "healthy": is_open,
                "host": self.config.host,
                "port": self.config.port,
                "virtual_host": self.config.virtual_host,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "host": self.config.host,
                "port": self.config.port,
                "timestamp": datetime.now().isoformat()
            }
    
    def close(self):
        """Close all connections."""
        self.connection.close()


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="RabbitMQ Skill")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5672)
    parser.add_argument("--action", required=True)
    parser.add_argument("--queue")
    parser.add_argument("--exchange")
    parser.add_argument("--message")
    parser.add_argument("--routing-key", default="")
    
    args = parser.parse_args()
    
    skill = RabbitMQSkill(host=args.host, port=args.port)
    
    try:
        if args.action == "declare_queue" and args.queue:
            config = QueueConfig(name=args.queue)
            result = skill.queue_manager().declare(config)
            print(json.dumps(result, indent=2))
            
        elif args.action == "delete_queue" and args.queue:
            result = skill.queue_manager().delete(args.queue)
            print(json.dumps(result, indent=2))
            
        elif args.action == "publish" and args.queue and args.message:
            result = skill.publisher().send_to_queue(args.queue, args.message)
            print(json.dumps(result, indent=2))
            
        elif args.action == "consume_one" and args.queue:
            result = skill.consumer().consume_one(args.queue)
            print(json.dumps(result, indent=2, default=str))
            
        elif args.action == "health":
            result = skill.health_check()
            print(json.dumps(result, indent=2))
            
    finally:
        skill.close()


if __name__ == "__main__":
    main()
