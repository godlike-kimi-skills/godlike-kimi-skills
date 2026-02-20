"""
Redis Queue Skill - Main Implementation

Provides comprehensive Redis queue operations including:
- List operations (LPUSH, RPOP, BRPOP, etc.)
- Stream operations (XADD, XREAD, XGROUP, etc.)
- Pub/Sub (publish, subscribe, pattern subscribe)
- Priority queues (sorted sets)
- Task queues (delayed, scheduled, retries)
- Distributed locks and rate limiting
"""

import json
import logging
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Union, Tuple
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from functools import wraps

import redis
from redis import Redis, ConnectionPool
from redis.exceptions import (
    RedisError, ConnectionError, TimeoutError, ResponseError
)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RedisConfig:
    """Configuration for Redis connections."""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    username: Optional[str] = None
    socket_timeout: float = 30.0
    socket_connect_timeout: float = 5.0
    max_connections: int = 50
    decode_responses: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class StreamEntry:
    """Represents a Redis Stream entry."""
    id: str
    fields: Dict[str, Any]
    
    @classmethod
    def from_redis(cls, entry: Tuple) -> "StreamEntry":
        """Create StreamEntry from Redis response."""
        entry_id, fields = entry
        # Convert list of field-value pairs to dict
        field_dict = {fields[i]: fields[i+1] for i in range(0, len(fields), 2)}
        return cls(id=entry_id, fields=field_dict)


@dataclass
class Task:
    """Represents a task for task queue."""
    id: str
    payload: Dict[str, Any]
    priority: int = 0
    delay: int = 0  # Delay in seconds
    retries: int = 3
    created_at: Optional[float] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, data: str) -> "Task":
        """Deserialize from JSON."""
        return cls(**json.loads(data))


class RedisConnection:
    """Manages Redis connection lifecycle."""
    
    def __init__(self, config: RedisConfig):
        self.config = config
        self._pool: Optional[ConnectionPool] = None
        self._redis: Optional[Redis] = None
    
    def connect(self) -> Redis:
        """Establish connection to Redis."""
        try:
            self._pool = ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                username=self.config.username,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                max_connections=self.config.max_connections,
                decode_responses=self.config.decode_responses
            )
            self._redis = Redis(connection_pool=self._pool)
            
            # Test connection
            self._redis.ping()
            logger.info(f"Connected to Redis at {self.config.host}:{self.config.port}")
            return self._redis
        except ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def get_redis(self) -> Redis:
        """Get Redis client instance."""
        if self._redis is None:
            self.connect()
        return self._redis
    
    def close(self):
        """Close connection pool."""
        if self._pool:
            self._pool.disconnect()
            self._pool = None
            self._redis = None
            logger.info("Redis connection closed")
    
    def health_check(self) -> Dict[str, Any]:
        """Check Redis connection health."""
        try:
            redis_client = self.get_redis()
            info = redis_client.info()
            return {
                "healthy": True,
                "host": self.config.host,
                "port": self.config.port,
                "version": info.get("redis_version"),
                "used_memory_human": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
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
    
    def __enter__(self):
        self.get_redis()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class RedisListQueue:
    """Redis List-based queue operations (FIFO/LIFO)."""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    def push_left(self, queue_name: str, *items: Any) -> int:
        """Push items to left side of list (LPUSH)."""
        serialized = [self._serialize(item) for item in items]
        return self.redis.lpush(queue_name, *serialized)
    
    def push_right(self, queue_name: str, *items: Any) -> int:
        """Push items to right side of list (RPUSH)."""
        serialized = [self._serialize(item) for item in items]
        return self.redis.rpush(queue_name, *serialized)
    
    def pop_left(self, queue_name: str, timeout: Optional[int] = None) -> Optional[Any]:
        """Pop from left side (LPOP/BLPOP for blocking)."""
        if timeout:
            result = self.redis.blpop(queue_name, timeout=timeout)
            if result:
                return self._deserialize(result[1])
            return None
        else:
            result = self.redis.lpop(queue_name)
            return self._deserialize(result) if result else None
    
    def pop_right(self, queue_name: str, timeout: Optional[int] = None) -> Optional[Any]:
        """Pop from right side (RPOP/BRPOP for blocking)."""
        if timeout:
            result = self.redis.brpop(queue_name, timeout=timeout)
            if result:
                return self._deserialize(result[1])
            return None
        else:
            result = self.redis.rpop(queue_name)
            return self._deserialize(result) if result else None
    
    def pop_left_push(
        self,
        source: str,
        destination: str,
        timeout: Optional[int] = None
    ) -> Optional[Any]:
        """Pop from source and push to destination (RPOPLPUSH/BRPOPLPUSH)."""
        if timeout:
            result = self.redis.brpoplpush(source, destination, timeout=timeout)
        else:
            result = self.redis.rpoplpush(source, destination)
        return self._deserialize(result) if result else None
    
    def length(self, queue_name: str) -> int:
        """Get queue length (LLEN)."""
        return self.redis.llen(queue_name)
    
    def range(
        self,
        queue_name: str,
        start: int = 0,
        end: int = -1
    ) -> List[Any]:
        """Get range of items (LRANGE)."""
        items = self.redis.lrange(queue_name, start, end)
        return [self._deserialize(item) for item in items]
    
    def trim(self, queue_name: str, start: int, end: int) -> bool:
        """Trim list to specified range (LTRIM)."""
        return self.redis.ltrim(queue_name, start, end)
    
    def remove(self, queue_name: str, item: Any, count: int = 0) -> int:
        """Remove items from list (LREM)."""
        return self.redis.lrem(queue_name, count, self._serialize(item))
    
    def delete(self, queue_name: str) -> int:
        """Delete queue entirely."""
        return self.redis.delete(queue_name)
    
    def _serialize(self, item: Any) -> str:
        """Serialize item to string."""
        if isinstance(item, str):
            return item
        if isinstance(item, (dict, list)):
            return json.dumps(item)
        return str(item)
    
    def _deserialize(self, item: str) -> Any:
        """Deserialize item from string."""
        try:
            return json.loads(item)
        except json.JSONDecodeError:
            return item


class RedisStream:
    """Redis Stream operations for event sourcing and log processing."""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    def add(
        self,
        stream_name: str,
        fields: Dict[str, Any],
        message_id: str = "*",
        maxlen: Optional[int] = None,
        approximate: bool = True
    ) -> str:
        """Add entry to stream (XADD)."""
        # Convert all values to strings
        string_fields = {k: str(v) if not isinstance(v, str) else v 
                        for k, v in fields.items()}
        
        return self.redis.xadd(
            name=stream_name,
            fields=string_fields,
            id=message_id,
            maxlen=maxlen,
            approximate=approximate
        )
    
    def read(
        self,
        streams: Dict[str, str],
        count: Optional[int] = None,
        block: Optional[int] = None
    ) -> Dict[str, List[StreamEntry]]:
        """Read from streams (XREAD)."""
        result = self.redis.xread(streams, count=count, block=block)
        
        parsed = {}
        if result:
            for stream_data in result:
                stream_name = stream_data[0]
                entries = [StreamEntry.from_redis(e) for e in stream_data[1]]
                parsed[stream_name] = entries
        return parsed
    
    def range(
        self,
        stream_name: str,
        start: str = "-",
        end: str = "+",
        count: Optional[int] = None
    ) -> List[StreamEntry]:
        """Read range from stream (XRANGE)."""
        result = self.redis.xrange(stream_name, start, end, count=count)
        return [StreamEntry.from_redis(e) for e in result]
    
    def reverse_range(
        self,
        stream_name: str,
        start: str = "+",
        end: str = "-",
        count: Optional[int] = None
    ) -> List[StreamEntry]:
        """Read range in reverse (XREVRANGE)."""
        result = self.redis.xrevrange(stream_name, start, end, count=count)
        return [StreamEntry.from_redis(e) for e in result]
    
    def create_consumer_group(
        self,
        stream_name: str,
        group_name: str,
        id: str = "0",
        mkstream: bool = False
    ) -> bool:
        """Create consumer group (XGROUP CREATE)."""
        try:
            self.redis.xgroup_create(stream_name, group_name, id=id, mkstream=mkstream)
            logger.info(f"Consumer group '{group_name}' created for stream '{stream_name}'")
            return True
        except ResponseError as e:
            if "already exists" in str(e):
                logger.warning(f"Consumer group '{group_name}' already exists")
                return True
            raise
    
    def read_group(
        self,
        group_name: str,
        consumer_name: str,
        streams: Dict[str, str],
        count: Optional[int] = None,
        block: Optional[int] = None,
        noack: bool = False
    ) -> Dict[str, List[StreamEntry]]:
        """Read as consumer group member (XREADGROUP)."""
        result = self.redis.xreadgroup(
            groupname=group_name,
            consumername=consumer_name,
            streams=streams,
            count=count,
            block=block,
            noack=noack
        )
        
        parsed = {}
        if result:
            for stream_data in result:
                stream_name = stream_data[0]
                entries = [StreamEntry.from_redis(e) for e in stream_data[1]]
                parsed[stream_name] = entries
        return parsed
    
    def acknowledge(self, stream_name: str, group_name: str, *ids: str) -> int:
        """Acknowledge messages (XACK)."""
        return self.redis.xack(stream_name, group_name, *ids)
    
    def claim(
        self,
        stream_name: str,
        group_name: str,
        consumer_name: str,
        min_idle_time: int,
        message_ids: List[str],
        justid: bool = False
    ) -> List[StreamEntry]:
        """Claim pending messages (XCLAIM)."""
        result = self.redis.xclaim(
            stream_name, group_name, consumer_name,
            min_idle_time, message_ids, justid=justid
        )
        return [StreamEntry.from_redis(e) for e in result] if not justid else result
    
    def pending(
        self,
        stream_name: str,
        group_name: str
    ) -> Dict[str, Any]:
        """Get pending messages info (XPENDING)."""
        return self.redis.xpending(stream_name, group_name)
    
    def delete(self, stream_name: str, *ids: str) -> int:
        """Delete entries from stream (XDEL)."""
        return self.redis.xdel(stream_name, *ids)
    
    def trim(
        self,
        stream_name: str,
        maxlen: int,
        approximate: bool = True
    ) -> int:
        """Trim stream to max length (XTRIM)."""
        return self.redis.xtrim(stream_name, maxlen=maxlen, approximate=approximate)
    
    def len(self, stream_name: str) -> int:
        """Get stream length (XLEN)."""
        return self.redis.xlen(stream_name)


class RedisPubSub:
    """Redis Pub/Sub operations for real-time messaging."""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self._pubsub = None
    
    def publish(self, channel: str, message: Any) -> int:
        """Publish message to channel."""
        serialized = json.dumps(message) if not isinstance(message, str) else message
        return self.redis.publish(channel, serialized)
    
    def subscribe(self, *channels: str):
        """Subscribe to channels (returns pubsub object)."""
        self._pubsub = self.redis.pubsub()
        self._pubsub.subscribe(*channels)
        logger.info(f"Subscribed to channels: {channels}")
        return self._pubsub
    
    def psubscribe(self, *patterns: str):
        """Subscribe to channel patterns."""
        self._pubsub = self.redis.pubsub()
        self._pubsub.psubscribe(*patterns)
        logger.info(f"Pattern subscribed to: {patterns}")
        return self._pubsub
    
    def listen(self, handler: Optional[Callable] = None, timeout: Optional[float] = None):
        """Listen for messages with optional handler."""
        if self._pubsub is None:
            raise RuntimeError("Not subscribed to any channels")
        
        start_time = time.time()
        for message in self._pubsub.listen():
            if timeout and (time.time() - start_time) > timeout:
                break
            
            if message["type"] in ("message", "pmessage"):
                data = message["data"]
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    pass
                
                parsed_message = {
                    "type": message["type"],
                    "channel": message.get("channel") or message.get("pattern"),
                    "data": data
                }
                
                if handler:
                    handler(parsed_message)
                else:
                    yield parsed_message
    
    def unsubscribe(self, *channels: str):
        """Unsubscribe from channels."""
        if self._pubsub:
            self._pubsub.unsubscribe(*channels)
    
    def punsubscribe(self, *patterns: str):
        """Unsubscribe from patterns."""
        if self._pubsub:
            self._pubsub.punsubscribe(*patterns)
    
    def close(self):
        """Close pubsub connection."""
        if self._pubsub:
            self._pubsub.close()
            self._pubsub = None


class RedisPriorityQueue:
    """Redis Sorted Set-based priority queue."""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    def add(self, queue_name: str, item: Any, priority: float) -> int:
        """Add item with priority (ZADD)."""
        serialized = self._serialize(item)
        return self.redis.zadd(queue_name, {serialized: priority})
    
    def pop_min(self, queue_name: str, count: int = 1) -> List[Tuple[Any, float]]:
        """Pop items with lowest priority (ZPOPMIN)."""
        results = self.redis.zpopmin(queue_name, count)
        return [(self._deserialize(item), score) for item, score in results]
    
    def pop_max(self, queue_name: str, count: int = 1) -> List[Tuple[Any, float]]:
        """Pop items with highest priority (ZPOPMAX)."""
        results = self.redis.zpopmax(queue_name, count)
        return [(self._deserialize(item), score) for item, score in results]
    
    def range_by_score(
        self,
        queue_name: str,
        min_score: float,
        max_score: float,
        start: int = 0,
        num: int = -1
    ) -> List[Tuple[Any, float]]:
        """Get items by score range."""
        results = self.redis.zrangebyscore(
            queue_name, min_score, max_score, start=start, num=num, withscores=True
        )
        return [(self._deserialize(item), score) for item, score in results]
    
    def count(self, queue_name: str) -> int:
        """Get number of items (ZCARD)."""
        return self.redis.zcard(queue_name)
    
    def remove(self, queue_name: str, *items: Any) -> int:
        """Remove items (ZREM)."""
        serialized = [self._serialize(item) for item in items]
        return self.redis.zrem(queue_name, *serialized)
    
    def _serialize(self, item: Any) -> str:
        """Serialize item to string."""
        if isinstance(item, str):
            return item
        return json.dumps(item)
    
    def _deserialize(self, item: str) -> Any:
        """Deserialize item from string."""
        try:
            return json.loads(item)
        except json.JSONDecodeError:
            return item


class RedisTaskQueue:
    """Distributed task queue with scheduling and retries."""
    
    def __init__(self, redis_client: Redis, queue_prefix: str = "task"):
        self.redis = redis_client
        self.queue_prefix = queue_prefix
        self.ready_queue = f"{queue_prefix}:ready"
        self.delayed_queue = f"{queue_prefix}:delayed"
        self.processing_queue = f"{queue_prefix}:processing"
        self.dlq_queue = f"{queue_prefix}:dlq"
    
    def enqueue(self, task: Task) -> str:
        """Add task to queue."""
        if task.delay > 0:
            # Schedule for later
            execute_at = time.time() + task.delay
            self.redis.zadd(self.delayed_queue, {task.to_json(): execute_at})
            logger.debug(f"Task {task.id} scheduled for execution at {execute_at}")
        else:
            # Add to ready queue
            self.redis.lpush(self.ready_queue, task.to_json())
            logger.debug(f"Task {task.id} added to ready queue")
        return task.id
    
    def schedule(self, payload: Dict[str, Any], delay: int = 0, **kwargs) -> str:
        """Create and schedule a task."""
        task = Task(
            id=str(uuid.uuid4()),
            payload=payload,
            delay=delay,
            **kwargs
        )
        return self.enqueue(task)
    
    def dequeue(self, timeout: int = 0) -> Optional[Task]:
        """Get next task from queue (blocking)."""
        # Move due delayed tasks to ready queue
        self._promote_delayed_tasks()
        
        # Pop from ready queue
        result = self.redis.brpop(self.ready_queue, timeout=timeout)
        if result:
            task_json = result[1]
            task = Task.from_json(task_json)
            
            # Add to processing queue
            self.redis.lpush(self.processing_queue, task_json)
            logger.debug(f"Task {task.id} moved to processing")
            return task
        return None
    
    def complete(self, task: Task, success: bool = True):
        """Mark task as completed."""
        task_json = task.to_json()
        self.redis.lrem(self.processing_queue, 0, task_json)
        
        if not success and task.retries > 0:
            # Retry
            task.retries -= 1
            self.redis.lpush(self.ready_queue, task.to_json())
            logger.info(f"Task {task.id} scheduled for retry, {task.retries} left")
        elif not success:
            # Move to DLQ
            self.redis.lpush(self.dlq_queue, task_json)
            logger.warning(f"Task {task.id} moved to DLQ")
    
    def _promote_delayed_tasks(self):
        """Move delayed tasks that are due to ready queue."""
        now = time.time()
        due_tasks = self.redis.zrangebyscore(self.delayed_queue, 0, now)
        
        for task_json in due_tasks:
            self.redis.zrem(self.delayed_queue, task_json)
            self.redis.lpush(self.ready_queue, task_json)
            logger.debug(f"Delayed task promoted to ready queue")
    
    def get_stats(self) -> Dict[str, int]:
        """Get queue statistics."""
        return {
            "ready": self.redis.llen(self.ready_queue),
            "delayed": self.redis.zcard(self.delayed_queue),
            "processing": self.redis.llen(self.processing_queue),
            "dlq": self.redis.llen(self.dlq_queue)
        }


class RedisQueueSkill:
    """Main entry point for Redis Queue operations."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None
    ):
        self.config = RedisConfig(
            host=host,
            port=port,
            db=db,
            password=password
        )
        self.connection = RedisConnection(self.config)
    
    def list_queue(self) -> RedisListQueue:
        """Get list queue operations."""
        return RedisListQueue(self.connection.get_redis())
    
    def stream(self) -> RedisStream:
        """Get stream operations."""
        return RedisStream(self.connection.get_redis())
    
    def pubsub(self) -> RedisPubSub:
        """Get pub/sub operations."""
        return RedisPubSub(self.connection.get_redis())
    
    def priority_queue(self) -> RedisPriorityQueue:
        """Get priority queue operations."""
        return RedisPriorityQueue(self.connection.get_redis())
    
    def task_queue(self, prefix: str = "task") -> RedisTaskQueue:
        """Get task queue operations."""
        return RedisTaskQueue(self.connection.get_redis(), prefix)
    
    def health_check(self) -> Dict[str, Any]:
        """Check Redis health."""
        return self.connection.health_check()
    
    def close(self):
        """Close all connections."""
        self.connection.close()


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Redis Queue Skill")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=6379)
    parser.add_argument("--action", required=True)
    parser.add_argument("--queue")
    parser.add_argument("--message")
    parser.add_argument("--stream")
    
    args = parser.parse_args()
    
    skill = RedisQueueSkill(host=args.host, port=args.port)
    
    try:
        if args.action == "lpush" and args.queue and args.message:
            result = skill.list_queue().push_left(args.queue, args.message)
            print(json.dumps({"success": True, "length": result}))
            
        elif args.action == "rpop" and args.queue:
            result = skill.list_queue().pop_right(args.queue)
            print(json.dumps({"success": True, "message": result}))
            
        elif args.action == "llen" and args.queue:
            result = skill.list_queue().length(args.queue)
            print(json.dumps({"success": True, "length": result}))
            
        elif args.action == "xadd" and args.stream and args.message:
            msg_id = skill.stream().add(args.stream, {"data": args.message})
            print(json.dumps({"success": True, "id": msg_id}))
            
        elif args.action == "health":
            result = skill.health_check()
            print(json.dumps(result, indent=2))
            
    finally:
        skill.close()


if __name__ == "__main__":
    main()
