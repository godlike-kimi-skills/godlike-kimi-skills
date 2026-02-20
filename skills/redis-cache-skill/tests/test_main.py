#!/usr/bin/env python3
"""
Tests for Redis Cache Skill
"""

import unittest
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.main import (
    RedisCacheManager, CacheConfig, CacheStats, CacheEntry,
    CacheStrategy, ExpirationPolicy
)

class TestCacheConfig(unittest.TestCase):
    
    def test_default_values(self):
        """Test default configuration"""
        config = CacheConfig()
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 6379)
        self.assertEqual(config.db, 0)
        self.assertEqual(config.max_memory, "256mb")
        self.assertEqual(config.max_memory_policy, "allkeys-lru")
    
    def test_custom_values(self):
        """Test custom configuration"""
        config = CacheConfig(
            host="redis.example.com",
            port=6380,
            db=1,
            password="secret"
        )
        self.assertEqual(config.host, "redis.example.com")
        self.assertEqual(config.port, 6380)
        self.assertEqual(config.db, 1)
        self.assertEqual(config.password, "secret")

class TestCacheStats(unittest.TestCase):
    
    def test_hit_rate_calculation(self):
        """Test hit rate calculation"""
        stats = CacheStats(hits=80, misses=20)
        self.assertEqual(stats.hit_rate, 80.0)
        self.assertEqual(stats.miss_rate, 20.0)
    
    def test_zero_division(self):
        """Test with no operations"""
        stats = CacheStats()
        self.assertEqual(stats.hit_rate, 0.0)
        self.assertEqual(stats.miss_rate, 0.0)
    
    def test_all_hits(self):
        """Test with all hits"""
        stats = CacheStats(hits=100, misses=0)
        self.assertEqual(stats.hit_rate, 100.0)
        self.assertEqual(stats.miss_rate, 0.0)

class TestRedisCacheManager(unittest.TestCase):
    
    @patch('scripts.main.redis.Redis')
    def setUp(self, mock_redis_class):
        self.mock_redis = MagicMock()
        mock_redis_class.return_value = self.mock_redis
        
        self.config = CacheConfig(host="localhost", port=6379)
        self.cache = RedisCacheManager(self.config)
    
    def test_connect_success(self):
        """Test successful connection"""
        self.mock_redis.ping.return_value = True
        self.assertTrue(self.cache.connect())
    
    def test_connect_failure(self):
        """Test failed connection"""
        from redis import ConnectionError
        self.mock_redis.ping.side_effect = ConnectionError
        self.assertFalse(self.cache.connect())
    
    def test_get_existing_key(self):
        """Test getting existing key"""
        self.mock_redis.get.return_value = "value"
        result = self.cache.get("key")
        self.assertEqual(result, "value")
    
    def test_get_missing_key(self):
        """Test getting missing key"""
        self.mock_redis.get.return_value = None
        result = self.cache.get("key")
        self.assertIsNone(result)
    
    def test_set_with_ttl(self):
        """Test setting key with TTL"""
        self.mock_redis.set.return_value = True
        result = self.cache.set("key", "value", ttl=300)
        self.assertTrue(result)
        self.mock_redis.set.assert_called_with("key", "value", ex=300, nx=False, xx=False)
    
    def test_delete(self):
        """Test deleting key"""
        self.mock_redis.delete.return_value = 1
        result = self.cache.delete("key")
        self.assertTrue(result)
    
    def test_exists(self):
        """Test checking key existence"""
        self.mock_redis.exists.return_value = 1
        self.assertTrue(self.cache.exists("key"))
    
    def test_ttl(self):
        """Test getting TTL"""
        self.mock_redis.ttl.return_value = 300
        result = self.cache.ttl("key")
        self.assertEqual(result, 300)
    
    def test_expire(self):
        """Test setting expiration"""
        self.mock_redis.expire.return_value = True
        result = self.cache.expire("key", 600)
        self.assertTrue(result)
    
    def test_mget(self):
        """Test multi-get"""
        self.mock_redis.mget.return_value = ["val1", "val2", None]
        results = self.cache.mget(["key1", "key2", "key3"])
        self.assertEqual(results, {"key1": "val1", "key2": "val2"})
    
    def test_get_stats(self):
        """Test getting statistics"""
        self.mock_redis.info.return_value = {
            "keyspace_hits": 100,
            "keyspace_misses": 20,
            "evicted_keys": 5,
            "expired_keys": 10,
            "used_memory": 1048576,
            "used_memory_human": "1M",
            "connected_clients": 10,
            "total_commands_processed": 1000,
            "instantaneous_ops_per_sec": 50
        }
        
        stats = self.cache.get_stats()
        self.assertEqual(stats.hits, 100)
        self.assertEqual(stats.misses, 20)
        self.assertAlmostEqual(stats.hit_rate, 83.33, places=2)
    
    def test_set_strategy(self):
        """Test setting cache strategy"""
        self.cache.set_strategy(CacheStrategy.LRU)
        self.mock_redis.config_set.assert_called_with("maxmemory-policy", "allkeys-lru")
    
    def test_session_management(self):
        """Test session operations"""
        session_data = {"user_id": 123, "role": "admin"}
        
        # Create session
        self.mock_redis.set.return_value = True
        result = self.cache.create_session("sess123", session_data, ttl=3600)
        self.assertTrue(result)
        
        # Get session
        self.mock_redis.get.return_value = json.dumps(session_data)
        session = self.cache.get_session("sess123")
        self.assertEqual(session, session_data)

class TestCacheEntry(unittest.TestCase):
    
    def test_initialization(self):
        """Test cache entry initialization"""
        entry = CacheEntry(key="test", value="data", ttl=300)
        self.assertEqual(entry.key, "test")
        self.assertEqual(entry.value, "data")
        self.assertEqual(entry.ttl, 300)
        self.assertEqual(entry.access_count, 0)
        self.assertIsNotNone(entry.created_at)

class TestCacheStrategy(unittest.TestCase):
    
    def test_strategy_values(self):
        """Test strategy enum values"""
        self.assertEqual(CacheStrategy.LRU.value, "lru")
        self.assertEqual(CacheStrategy.LFU.value, "lfu")
        self.assertEqual(CacheStrategy.FIFO.value, "fifo")
        self.assertEqual(CacheStrategy.TTL.value, "ttl")
        self.assertEqual(CacheStrategy.RANDOM.value, "random")

if __name__ == "__main__":
    unittest.main()
