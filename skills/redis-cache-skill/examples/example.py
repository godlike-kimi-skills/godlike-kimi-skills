#!/usr/bin/env python3
"""
Redis Cache Skill Usage Examples
"""

import sys
import json
sys.path.insert(0, '..')

from scripts.main import RedisCacheManager, CacheConfig, CacheStrategy

def example_basic_operations():
    """Demonstrate basic cache operations"""
    config = CacheConfig(host="localhost", port=6379, db=0)
    cache = RedisCacheManager(config)
    
    if not cache.connect():
        print("Could not connect to Redis")
        return
    
    # Set values with TTL
    cache.set("name", "John Doe", ttl=300)
    cache.set("email", "john@example.com", ttl=300)
    cache.set("counter", "1")
    
    # Get values
    print(f"Name: {cache.get('name')}")
    print(f"Email: {cache.get('email')}")
    print(f"Counter: {cache.get('counter')}")
    
    # Check existence and TTL
    print(f"Exists: {cache.exists('name')}")
    print(f"TTL: {cache.ttl('name')} seconds")
    
    # Delete
    cache.delete("counter")
    print(f"Counter exists after delete: {cache.exists('counter')}")

def example_batch_operations():
    """Demonstrate batch operations"""
    config = CacheConfig(host="localhost", port=6379)
    cache = RedisCacheManager(config)
    
    # Multi-set
    data = {
        "user:1": json.dumps({"name": "Alice", "age": 30}),
        "user:2": json.dumps({"name": "Bob", "age": 25}),
        "user:3": json.dumps({"name": "Carol", "age": 35})
    }
    cache.mset(data, ttl=600)
    print("Batch insert completed")
    
    # Multi-get
    keys = ["user:1", "user:2", "user:3"]
    results = cache.mget(keys)
    for key, value in results.items():
        print(f"{key}: {value}")
    
    # Scan keys by pattern
    users = cache.scan_keys("user:*")
    print(f"Found {len(users)} user keys")

def example_session_management():
    """Demonstrate session management"""
    config = CacheConfig(host="localhost", port=6379)
    cache = RedisCacheManager(config)
    
    # Create session
    session_id = "sess_abc123xyz"
    session_data = {
        "user_id": 123,
        "username": "john_doe",
        "role": "admin",
        "login_time": "2024-01-15T10:30:00Z"
    }
    
    cache.create_session(session_id, session_data, ttl=3600)
    print(f"Created session: {session_id}")
    
    # Retrieve session
    session = cache.get_session(session_id)
    print(f"Session data: {session}")
    
    # Update session
    session_data["last_activity"] = "2024-01-15T11:00:00Z"
    cache.update_session(session_id, session_data, ttl=3600)
    
    # Delete session
    cache.delete_session(session_id)
    print(f"Session deleted")

def example_cache_strategies():
    """Demonstrate different cache strategies"""
    config = CacheConfig(host="localhost", port=6379)
    cache = RedisCacheManager(config)
    
    strategies = [
        CacheStrategy.LRU,
        CacheStrategy.LFU,
        CacheStrategy.RANDOM,
        CacheStrategy.TTL
    ]
    
    for strategy in strategies:
        cache.set_strategy(strategy)
        current = cache.get_strategy()
        print(f"Set strategy to: {current.value}")

def example_performance_analysis():
    """Demonstrate performance analysis"""
    config = CacheConfig(host="localhost", port=6379)
    cache = RedisCacheManager(config)
    
    # Get statistics
    stats = cache.get_stats()
    print("\n=== Cache Statistics ===")
    print(f"Hit Rate: {stats.hit_rate:.2f}%")
    print(f"Miss Rate: {stats.miss_rate:.2f}%")
    print(f"Used Memory: {stats.used_memory_human}")
    print(f"Connected Clients: {stats.connected_clients}")
    print(f"Ops/sec: {stats.instantaneous_ops_per_sec}")
    
    # Memory info
    print("\n=== Memory Info ===")
    mem_info = cache.get_memory_info()
    for key, value in mem_info.items():
        print(f"{key}: {value}")
    
    # Slow log
    print("\n=== Slow Queries ===")
    slowlog = cache.get_slowlog(5)
    for entry in slowlog:
        print(f"{entry['command']}: {entry['duration']}μs")

def example_benchmark():
    """Run cache benchmark"""
    config = CacheConfig(host="localhost", port=6379)
    cache = RedisCacheManager(config)
    
    print("\n=== Running Benchmark ===")
    results = cache.benchmark(num_requests=1000, data_size=100)
    
    print(f"Write ops/sec: {results['write_ops_per_sec']:.2f}")
    print(f"Read ops/sec: {results['read_ops_per_sec']:.2f}")
    print(f"Write latency: {results['write_latency_ms']:.3f}ms")
    print(f"Read latency: {results['read_latency_ms']:.3f}ms")

def example_cache_decorator():
    """Demonstrate cache decorator usage"""
    config = CacheConfig(host="localhost", port=6379)
    cache = RedisCacheManager(config)
    
    call_count = 0
    
    @cache.cached(ttl=60, key_prefix="expensive")
    def expensive_function(query):
        nonlocal call_count
        call_count += 1
        # Simulate expensive operation
        return f"Result for: {query}"
    
    # First call - executes function
    result1 = expensive_function("test_query")
    print(f"First call: {result1} (executions: {call_count})")
    
    # Second call - returns from cache
    result2 = expensive_function("test_query")
    print(f"Second call: {result2} (executions: {call_count})")
    
    print(f"Cache saved {call_count - 1} executions")

if __name__ == "__main__":
    print("=" * 60)
    print("Redis Cache Skill Examples")
    print("=" * 60)
    
    print("\n1. Basic Operations:")
    example_basic_operations()
    
    print("\n2. Batch Operations:")
    example_batch_operations()
    
    print("\n3. Session Management:")
    example_session_management()
    
    print("\n4. Cache Strategies:")
    example_cache_strategies()
    
    print("\n5. Performance Analysis:")
    example_performance_analysis()
    
    print("\n6. Benchmark:")
    example_benchmark()
    
    print("\n7. Cache Decorator:")
    example_cache_decorator()
