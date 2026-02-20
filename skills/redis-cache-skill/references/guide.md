# Redis Cache Management Guide

## Table of Contents
1. [Cache Strategies](#strategies)
2. [Configuration](#configuration)
3. [Performance Tuning](#performance)
4. [Common Patterns](#patterns)
5. [Troubleshooting](#troubleshooting)

## Cache Strategies <a name="strategies"></a>

### LRU (Least Recently Used)
Best for: General-purpose caching with temporal locality
```python
cache.set_strategy(CacheStrategy.LRU)
```
Use when recently accessed items are likely to be accessed again.

### LFU (Least Frequently Used)
Best for: Caching items with consistent access patterns
```python
cache.set_strategy(CacheStrategy.LFU)
```
Use when popular items should remain cached regardless of recency.

### TTL-Based
Best for: Time-sensitive data like sessions
```python
cache.set_strategy(CacheStrategy.TTL)
```
Items with shorter TTLs are evicted first.

### Random
Best for: When eviction order doesn't matter
```python
cache.set_strategy(CacheStrategy.RANDOM)
```
Simple and fast, minimal overhead.

## Configuration <a name="configuration"></a>

### Memory Policies
| Policy | Description |
|--------|-------------|
| allkeys-lru | Evict any key using LRU |
| allkeys-lfu | Evict any key using LFU |
| allkeys-random | Evict random keys |
| volatile-lru | Evict LRU from keys with TTL |
| volatile-lfu | Evict LFU from keys with TTL |
| volatile-ttl | Evict shortest TTL first |
| volatile-random | Evict random from keys with TTL |
| noeviction | Return errors on memory limit |

### Connection Pool Settings
```python
config = CacheConfig(
    host="localhost",
    port=6379,
    max_connections=50,
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True
)
```

## Performance Tuning <a name="performance"></a>

### Pipelining
Use pipelines for bulk operations:
```python
pipe = cache.client.pipeline()
for key in keys:
    pipe.get(key)
results = pipe.execute()
```

### Batch Operations
```python
# Instead of multiple gets
data = cache.mget(["key1", "key2", "key3"])

# Instead of multiple sets
cache.mset({"key1": "val1", "key2": "val2"}, ttl=3600)
```

### Key Naming Conventions
```
user:123:profile
user:123:settings
session:abc123:data
cache:query:hash_of_query
```

## Common Patterns <a name="patterns"></a>

### Cache-Aside Pattern
```python
def get_data(key):
    # Try cache first
    data = cache.get(key)
    if data:
        return data
    
    # Load from database
    data = database.get(key)
    
    # Store in cache
    cache.set(key, data, ttl=300)
    return data
```

### Session Store
```python
# Create session
session_id = generate_session_id()
cache.create_session(session_id, user_data, ttl=3600)

# Validate session
session = cache.get_session(session_id)
if not session:
    raise Unauthorized()

# Extend session
cache.expire(f"session:{session_id}", 3600)
```

### Rate Limiting
```python
def check_rate_limit(key, limit, window):
    current = cache.client.get(key)
    if current and int(current) >= limit:
        return False
    
    pipe = cache.client.pipeline()
    pipe.incr(key)
    pipe.expire(key, window)
    pipe.execute()
    return True
```

## Troubleshooting <a name="troubleshooting"></a>

### High Memory Usage
1. Check `maxmemory` setting
2. Review eviction policy
3. Analyze key sizes: `redis-cli --bigkeys`
4. Check TTL on keys

### Low Hit Rate
1. Increase cache size
2. Review TTL values
3. Analyze access patterns
4. Consider different eviction policy

### Connection Issues
```python
# Test connection
if not cache.connect():
    logger.error("Redis connection failed")
    # Fallback to database
```

### Slow Queries
```python
# Check slow log
slowlog = cache.get_slowlog(10)
for entry in slowlog:
    print(f"{entry['command']}: {entry['duration']}μs")
```
