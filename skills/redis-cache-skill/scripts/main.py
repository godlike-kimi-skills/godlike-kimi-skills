#!/usr/bin/env python3
"""
Redis Cache Management Skill
Supports: cache strategies, expiration management, performance analysis
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import redis
from redis.sentinel import Sentinel

# ============================================================================
# Cache Strategy Enums
# ============================================================================

class CacheStrategy(Enum):
    """Cache strategies"""
    LRU = "lru"           # Least Recently Used
    LFU = "lfu"           # Least Frequently Used
    FIFO = "fifo"         # First In First Out
    TTL = "ttl"           # Time To Live
    RANDOM = "random"     # Random eviction

class ExpirationPolicy(Enum):
    """Expiration policies"""
    LAZY = "lazy"         # Check on access
    ACTIVE = "active"     # Background cleanup
    MIXED = "mixed"       # Combination

# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class CacheConfig:
    """Redis cache configuration"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_memory: str = "256mb"
    max_memory_policy: str = "allkeys-lru"
    timeout: int = 5
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    evicted_keys: int = 0
    expired_keys: int = 0
    used_memory: int = 0
    used_memory_human: str = "0B"
    connected_clients: int = 0
    total_commands_processed: int = 0
    instantaneous_ops_per_sec: int = 0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total * 100 if total > 0 else 0
    
    @property
    def miss_rate(self) -> float:
        total = self.hits + self.misses
        return self.misses / total * 100 if total > 0 else 0

@dataclass
class CacheEntry:
    """Cache entry metadata"""
    key: str
    value: Any
    ttl: Optional[int] = None
    created_at: Optional[datetime] = None
    accessed_at: Optional[datetime] = None
    access_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.accessed_at is None:
            self.accessed_at = datetime.now()

# ============================================================================
# Redis Cache Manager
# ============================================================================

class RedisCacheManager:
    """Main class for managing Redis cache"""
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self._client: Optional[redis.Redis] = None
        self._pipeline = None
        self._local_cache: Dict[str, CacheEntry] = {}
        self._strategy = CacheStrategy.LRU
    
    @property
    def client(self) -> redis.Redis:
        """Get or create Redis client"""
        if self._client is None:
            self._client = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                socket_timeout=self.config.timeout,
                decode_responses=True
            )
        return self._client
    
    def connect(self) -> bool:
        """Test connection to Redis"""
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False
    
    def disconnect(self) -> None:
        """Close Redis connection"""
        if self._client:
            self._client.close()
            self._client = None
    
    # ========================================================================
    # Basic Cache Operations
    # ========================================================================
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with local tracking"""
        value = self.client.get(key)
        
        if value is not None:
            # Update local tracking for strategy
            if key in self._local_cache:
                entry = self._local_cache[key]
                entry.accessed_at = datetime.now()
                entry.access_count += 1
            return value
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None,
            nx: bool = False, xx: bool = False) -> bool:
        """Set value in cache with optional TTL"""
        try:
            result = self.client.set(key, value, ex=ttl, nx=nx, xx=xx)
            
            if result:
                # Track in local cache
                self._local_cache[key] = CacheEntry(
                    key=key,
                    value=value,
                    ttl=ttl
                )
            return bool(result)
        except redis.RedisError:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        result = self.client.delete(key)
        self._local_cache.pop(key, None)
        return result > 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self.client.exists(key) > 0
    
    def ttl(self, key: str) -> int:
        """Get remaining TTL for key"""
        return self.client.ttl(key)
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key"""
        return self.client.expire(key, seconds)
    
    def persist(self, key: str) -> bool:
        """Remove expiration from key"""
        return self.client.persist(key)
    
    # ========================================================================
    # Cache Strategies
    # ========================================================================
    
    def set_strategy(self, strategy: CacheStrategy) -> None:
        """Set cache eviction strategy"""
        self._strategy = strategy
        policy_map = {
            CacheStrategy.LRU: "allkeys-lru",
            CacheStrategy.LFU: "allkeys-lfu",
            CacheStrategy.RANDOM: "allkeys-random",
            CacheStrategy.TTL: "volatile-ttl",
            CacheStrategy.FIFO: "volatile-lru"
        }
        
        policy = policy_map.get(strategy, "allkeys-lru")
        self.client.config_set("maxmemory-policy", policy)
    
    def get_strategy(self) -> CacheStrategy:
        """Get current cache strategy"""
        return self._strategy
    
    # ========================================================================
    # Batch Operations
    # ========================================================================
    
    def mget(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple keys at once"""
        values = self.client.mget(keys)
        return {k: v for k, v in zip(keys, values) if v is not None}
    
    def mset(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple keys at once"""
        pipe = self.client.pipeline()
        pipe.mset(mapping)
        
        if ttl:
            for key in mapping.keys():
                pipe.expire(key, ttl)
        
        results = pipe.execute()
        return all(results)
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        keys = self.client.keys(pattern)
        if keys:
            return self.client.delete(*keys)
        return 0
    
    def scan_keys(self, pattern: str = "*", count: int = 100) -> List[str]:
        """Scan keys matching pattern"""
        keys = []
        cursor = 0
        
        while True:
            cursor, batch = self.client.scan(cursor, match=pattern, count=count)
            keys.extend(batch)
            if cursor == 0:
                break
        
        return keys
    
    # ========================================================================
    # Performance Analysis
    # ========================================================================
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        info = self.client.info()
        
        return CacheStats(
            hits=info.get("keyspace_hits", 0),
            misses=info.get("keyspace_misses", 0),
            evicted_keys=info.get("evicted_keys", 0),
            expired_keys=info.get("expired_keys", 0),
            used_memory=info.get("used_memory", 0),
            used_memory_human=info.get("used_memory_human", "0B"),
            connected_clients=info.get("connected_clients", 0),
            total_commands_processed=info.get("total_commands_processed", 0),
            instantaneous_ops_per_sec=info.get("instantaneous_ops_per_sec", 0)
        )
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get detailed memory information"""
        info = self.client.info("memory")
        return {
            "used_memory": info.get("used_memory"),
            "used_memory_human": info.get("used_memory_human"),
            "used_memory_rss": info.get("used_memory_rss"),
            "used_memory_peak": info.get("used_memory_peak"),
            "total_system_memory": info.get("total_system_memory"),
            "maxmemory": info.get("maxmemory"),
            "maxmemory_policy": info.get("maxmemory_policy")
        }
    
    def get_slowlog(self, entries: int = 10) -> List[Dict]:
        """Get slow query log"""
        slowlog = self.client.slowlog_get(entries)
        return [
            {
                "id": entry["id"],
                "duration": entry["duration"],
                "command": " ".join(str(c) for c in entry["command"]),
                "timestamp": datetime.fromtimestamp(entry["time"]).isoformat()
            }
            for entry in slowlog
        ]
    
    def benchmark(self, num_requests: int = 10000, 
                  data_size: int = 100) -> Dict[str, float]:
        """Run simple benchmark"""
        import random
        import string
        
        test_data = ''.join(random.choices(string.ascii_letters, k=data_size))
        
        # Write benchmark
        start = time.time()
        for i in range(num_requests):
            self.set(f"bench:{i}", test_data)
        write_time = time.time() - start
        
        # Read benchmark
        start = time.time()
        for i in range(num_requests):
            self.get(f"bench:{i}")
        read_time = time.time() - start
        
        # Cleanup
        self.delete_pattern("bench:*")
        
        return {
            "write_ops_per_sec": num_requests / write_time,
            "read_ops_per_sec": num_requests / read_time,
            "write_latency_ms": (write_time / num_requests) * 1000,
            "read_latency_ms": (read_time / num_requests) * 1000
        }
    
    # ========================================================================
    # Cache Decorator
    # ========================================================================
    
    def cached(self, ttl: Optional[int] = None, key_prefix: str = ""):
        """Decorator for caching function results"""
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{key_prefix}:{func.__name__}:{hash(args + tuple(kwargs.items()))}"
                
                # Try to get from cache
                result = self.get(cache_key)
                if result is not None:
                    return json.loads(result)
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Store in cache
                self.set(cache_key, json.dumps(result), ttl)
                
                return result
            return wrapper
        return decorator
    
    # ========================================================================
    # Session Management
    # ========================================================================
    
    def create_session(self, session_id: str, data: Dict, ttl: int = 3600) -> bool:
        """Create session data"""
        return self.set(f"session:{session_id}", json.dumps(data), ttl)
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        data = self.get(f"session:{session_id}")
        return json.loads(data) if data else None
    
    def update_session(self, session_id: str, data: Dict, ttl: int = 3600) -> bool:
        """Update session data"""
        return self.create_session(session_id, data, ttl)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        return self.delete(f"session:{session_id}")

# ============================================================================
# CLI Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Redis Cache Manager")
    parser.add_argument("--host", default="localhost", help="Redis host")
    parser.add_argument("--port", type=int, default=6379, help="Redis port")
    parser.add_argument("--db", type=int, default=0, help="Redis database")
    parser.add_argument("--password", help="Redis password")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Basic commands
    get_parser = subparsers.add_parser("get", help="Get key")
    get_parser.add_argument("key", help="Key to get")
    
    set_parser = subparsers.add_parser("set", help="Set key")
    set_parser.add_argument("key", help="Key to set")
    set_parser.add_argument("value", help="Value to set")
    set_parser.add_argument("--ttl", type=int, help="TTL in seconds")
    
    subparsers.add_parser("ping", help="Test connection")
    subparsers.add_parser("stats", help="Get statistics")
    subparsers.add_parser("memory", help="Get memory info")
    
    delete_parser = subparsers.add_parser("delete", help="Delete key")
    delete_parser.add_argument("key", help="Key to delete")
    
    # Pattern commands
    scan_parser = subparsers.add_parser("scan", help="Scan keys")
    scan_parser.add_argument("--pattern", default="*", help="Pattern to match")
    
    flush_parser = subparsers.add_parser("flush-pattern", help="Delete keys by pattern")
    flush_parser.add_argument("pattern", help="Pattern to match")
    
    # Benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Run benchmark")
    bench_parser.add_argument("--requests", type=int, default=1000, help="Number of requests")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    config = CacheConfig(
        host=args.host,
        port=args.port,
        db=args.db,
        password=args.password
    )
    
    manager = RedisCacheManager(config)
    
    if args.command == "ping":
        print("Connected" if manager.connect() else "Failed to connect")
    
    elif args.command == "get":
        value = manager.get(args.key)
        print(value if value else "(nil)")
    
    elif args.command == "set":
        if manager.set(args.key, args.value, args.ttl):
            print("OK")
    
    elif args.command == "delete":
        print("Deleted" if manager.delete(args.key) else "Not found")
    
    elif args.command == "stats":
        stats = manager.get_stats()
        print(f"Hit Rate: {stats.hit_rate:.2f}%")
        print(f"Miss Rate: {stats.miss_rate:.2f}%")
        print(f"Used Memory: {stats.used_memory_human}")
        print(f"Connected Clients: {stats.connected_clients}")
        print(f"Ops/sec: {stats.instantaneous_ops_per_sec}")
    
    elif args.command == "memory":
        info = manager.get_memory_info()
        for k, v in info.items():
            print(f"{k}: {v}")
    
    elif args.command == "scan":
        keys = manager.scan_keys(args.pattern)
        for key in keys:
            print(key)
    
    elif args.command == "flush-pattern":
        count = manager.delete_pattern(args.pattern)
        print(f"Deleted {count} keys")
    
    elif args.command == "benchmark":
        results = manager.benchmark(args.requests)
        print(f"Write ops/sec: {results['write_ops_per_sec']:.2f}")
        print(f"Read ops/sec: {results['read_ops_per_sec']:.2f}")

if __name__ == "__main__":
    main()
