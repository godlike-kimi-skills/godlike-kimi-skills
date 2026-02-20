---
name: redis-cache-skill
description: Redis cache management with caching strategies, TTL expiration, session management, and performance analysis. Use when implementing caching layers, managing sessions, optimizing database queries, or analyzing cache performance. Supports LRU/LFU eviction policies, batch operations, and detailed metrics.
---

# Redis Cache Management Skill

## Use When
- Implementing application caching layer
- Managing user sessions in Redis
- Setting up cache expiration policies
- Analyzing cache hit/miss rates
- Configuring cache eviction strategies (LRU/LFU)
- Running cache performance benchmarks
- Bulk cache operations

## Out of Scope
- Redis server installation and setup
- Redis Cluster configuration
- Redis Sentinel high availability
- Complex Lua scripting
- Pub/Sub messaging patterns
- Redis modules (RedisJSON, RediSearch, etc.)

## Quick Start

```python
from scripts.main import RedisCacheManager, CacheConfig

# Initialize with configuration
config = CacheConfig(host="localhost", port=6379, db=0)
cache = RedisCacheManager(config)

# Basic operations
cache.set("user:123", json.dumps({"name": "John"}), ttl=3600)
user = cache.get("user:123")

# Session management
session_id = "sess_abc123"
cache.create_session(session_id, {"user_id": 123}, ttl=3600)
session = cache.get_session(session_id)

# Cache decorator
@cache.cached(ttl=300)
def get_expensive_data(query):
    return expensive_database_query(query)
```

## Core Features

### Cache Strategies
- **LRU** (Least Recently Used): Default strategy for most use cases
- **LFU** (Least Frequently Used): Better for repeated access patterns
- **TTL**: Time-based expiration
- **FIFO**: First In First Out
- **Random**: Random eviction when memory is full

### Performance Metrics
- Hit/miss rates with percentages
- Memory usage statistics
- Operations per second
- Slow query log analysis
- Benchmarking tools

### Batch Operations
- Multi-get for retrieving multiple keys
- Multi-set for bulk inserts
- Pattern-based deletion
- Key scanning with cursors

## CLI Usage

```bash
# Connection
python scripts/main.py --host localhost --port 6379 ping

# Basic operations
python scripts/main.py --host localhost set mykey "myvalue" --ttl 3600
python scripts/main.py --host localhost get mykey
python scripts/main.py --host localhost delete mykey
python scripts/main.py --host localhost ttl mykey

# Batch operations
python scripts/main.py --host localhost scan --pattern "user:*"
python scripts/main.py --host localhost flush-pattern "temp:*"

# Performance analysis
python scripts/main.py --host localhost stats
python scripts/main.py --host localhost memory
python scripts/main.py --host localhost benchmark --requests 10000
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| host | localhost | Redis server hostname |
| port | 6379 | Redis server port |
| db | 0 | Database number |
| password | None | Authentication password |
| max_memory | 256mb | Maximum memory usage |
| max_memory_policy | allkeys-lru | Eviction policy |
| timeout | 5 | Connection timeout in seconds |

## Cache Decorator Pattern

```python
from scripts.main import RedisCacheManager, CacheConfig

config = CacheConfig(host="localhost", port=6379)
cache = RedisCacheManager(config)

# Cache function results
@cache.cached(ttl=300, key_prefix="api")
def fetch_user(user_id):
    return database.get_user(user_id)

# Cached automatically
user = fetch_user(123)  # Miss - queries DB
user = fetch_user(123)  # Hit - returns from cache
```
