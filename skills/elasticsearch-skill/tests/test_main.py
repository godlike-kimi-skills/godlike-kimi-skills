#!/usr/bin/env python3
"""
Tests for Elasticsearch Skill
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.main import (
    ElasticsearchManager, ESConfig, IndexMapping,
    QueryResult
)

class TestESConfig(unittest.TestCase):
    
    def test_default_values(self):
        """Test default configuration"""
        config = ESConfig()
        self.assertEqual(config.hosts, ["localhost:9200"])
        self.assertIsNone(config.username)
        self.assertIsNone(config.password)
        self.assertFalse(config.use_ssl)
        self.assertEqual(config.timeout, 30)
    
    def test_custom_values(self):
        """Test custom configuration"""
        config = ESConfig(
            hosts=["es1:9200", "es2:9200"],
            username="elastic",
            password="secret",
            use_ssl=True,
            timeout=60
        )
        self.assertEqual(config.hosts, ["es1:9200", "es2:9200"])
        self.assertEqual(config.username, "elastic")
        self.assertEqual(config.password, "secret")
        self.assertTrue(config.use_ssl)
        self.assertEqual(config.timeout, 60)

class TestIndexMapping(unittest.TestCase):
    
    def test_basic_mapping(self):
        """Test basic mapping creation"""
        mapping = IndexMapping(
            properties={
                "title": {"type": "text"},
                "price": {"type": "float"}
            }
        )
        
        result = mapping.to_dict()
        self.assertIn("mappings", result)
        self.assertIn("title", result["mappings"]["properties"])
        self.assertEqual(result["mappings"]["properties"]["title"]["type"], "text")
    
    def test_mapping_with_settings(self):
        """Test mapping with settings"""
        mapping = IndexMapping(
            properties={"name": {"type": "keyword"}},
            settings={"number_of_shards": 3}
        )
        
        result = mapping.to_dict()
        self.assertIn("settings", result)
        self.assertEqual(result["settings"]["number_of_shards"], 3)

class TestElasticsearchManager(unittest.TestCase):
    
    @patch('scripts.main.Elasticsearch')
    def setUp(self, mock_es_class):
        self.mock_es = MagicMock()
        mock_es_class.return_value = self.mock_es
        
        self.config = ESConfig(hosts=["localhost:9200"])
        self.es = ElasticsearchManager(self.config)
    
    def test_connect_success(self):
        """Test successful connection"""
        self.mock_es.ping.return_value = True
        self.assertTrue(self.es.connect())
    
    def test_connect_failure(self):
        """Test failed connection"""
        self.mock_es.ping.return_value = False
        self.assertFalse(self.es.connect())
    
    def test_create_index(self):
        """Test index creation"""
        mapping = IndexMapping(properties={"name": {"type": "text"}})
        result = self.es.create_index("test-index", mapping)
        
        self.assertTrue(result)
        self.mock_es.indices.create.assert_called_once()
    
    def test_delete_index(self):
        """Test index deletion"""
        result = self.es.delete_index("test-index")
        
        self.assertTrue(result)
        self.mock_es.indices.delete.assert_called_with(index="test-index")
    
    def test_index_exists(self):
        """Test index existence check"""
        self.mock_es.indices.exists.return_value = True
        self.assertTrue(self.es.index_exists("test-index"))
    
    def test_get_mapping(self):
        """Test getting index mapping"""
        self.mock_es.indices.get_mapping.return_value = {
            "test-index": {"mappings": {"properties": {}}}
        }
        result = self.es.get_mapping("test-index")
        self.assertIn("test-index", result)
    
    def test_index_document(self):
        """Test indexing a document"""
        doc = {"name": "Test"}
        self.es.index_document("test-index", doc, doc_id="1")
        
        self.mock_es.index.assert_called_with(
            index="test-index",
            id="1",
            body=doc
        )
    
    def test_get_document(self):
        """Test getting a document"""
        self.mock_es.get.return_value = {"_source": {"name": "Test"}}
        result = self.es.get_document("test-index", "1")
        
        self.assertEqual(result, {"name": "Test"})
    
    def test_delete_document(self):
        """Test deleting a document"""
        result = self.es.delete_document("test-index", "1")
        self.assertTrue(result)
    
    def test_update_document(self):
        """Test updating a document"""
        doc = {"price": 100}
        self.es.update_document("test-index", "1", doc)
        
        self.mock_es.update.assert_called_with(
            index="test-index",
            id="1",
            body={"doc": doc}
        )
    
    def test_list_indices(self):
        """Test listing indices"""
        self.mock_es.indices.get.return_value = {
            "index1": {},
            "index2": {}
        }
        result = self.es.list_indices("*")
        
        self.assertEqual(len(result), 2)
        self.assertIn("index1", result)
    
    def test_search(self):
        """Test search query"""
        self.mock_es.search.return_value = {
            "hits": {
                "total": {"value": 1},
                "hits": [{"_source": {"name": "Test"}}]
            },
            "took": 5
        }
        
        result = self.es.search("test-index", {"match_all": {}})
        
        self.assertEqual(result.total, 1)
        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result.took, 5)
    
    def test_match_query(self):
        """Test match query"""
        self.mock_es.search.return_value = {
            "hits": {"total": {"value": 2}, "hits": []},
            "took": 3
        }
        
        result = self.es.match_query("test-index", "title", "test")
        self.assertEqual(result.total, 2)
    
    def test_term_query(self):
        """Test term query"""
        self.mock_es.search.return_value = {
            "hits": {"total": {"value": 1}, "hits": []},
            "took": 2
        }
        
        result = self.es.term_query("test-index", "status", "active")
        self.assertEqual(result.total, 1)
    
    def test_range_query(self):
        """Test range query"""
        self.mock_es.search.return_value = {
            "hits": {"total": {"value": 5}, "hits": []},
            "took": 4
        }
        
        result = es.range_query("test-index", "price", gte=10, lte=100)
        self.assertEqual(result.total, 5)
    
    def test_bool_query(self):
        """Test boolean query"""
        self.mock_es.search.return_value = {
            "hits": {"total": {"value": 3}, "hits": []},
            "took": 3
        }
        
        result = self.es.bool_query(
            "test-index",
            must=[{"match": {"title": "test"}}],
            filter=[{"term": {"active": True}}]
        )
        self.assertEqual(result.total, 3)
    
    def test_refresh_index(self):
        """Test index refresh"""
        self.es.refresh_index("test-index")
        self.mock_es.indices.refresh.assert_called_with(index="test-index")

class TestQueryResult(unittest.TestCase):
    
    def test_query_result_creation(self):
        """Test QueryResult dataclass"""
        result = QueryResult(
            total=10,
            hits=[{"name": "Test"}],
            took=5,
            scroll_id="scroll123"
        )
        
        self.assertEqual(result.total, 10)
        self.assertEqual(len(result.hits), 1)
        self.assertEqual(result.took, 5)
        self.assertEqual(result.scroll_id, "scroll123")

if __name__ == "__main__":
    unittest.main()
