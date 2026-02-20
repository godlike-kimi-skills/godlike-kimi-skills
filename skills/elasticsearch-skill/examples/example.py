#!/usr/bin/env python3
"""
Elasticsearch Skill Usage Examples
"""

import sys
import json
from datetime import datetime, timedelta

sys.path.insert(0, '..')

from scripts.main import (
    ElasticsearchManager, ESConfig, IndexMapping,
    QueryResult
)

def example_basic_connection():
    """Demonstrate basic connection and info"""
    config = ESConfig(hosts=["localhost:9200"])
    es = ElasticsearchManager(config)
    
    # Test connection
    if es.connect():
        print("Connected to Elasticsearch")
        
        # Get cluster info
        info = es.info()
        print(f"Cluster: {info.get('cluster_name')}")
        print(f"Version: {info.get('version', {}).get('number')}")
        
        # Get health status
        health = es.health()
        print(f"Status: {health.get('status')}")
        print(f"Nodes: {health.get('number_of_nodes')}")
    else:
        print("Failed to connect")

def example_index_management():
    """Demonstrate index operations"""
    config = ESConfig(hosts=["localhost:9200"])
    es = ElasticsearchManager(config)
    
    index_name = "products"
    
    # Delete if exists
    if es.index_exists(index_name):
        es.delete_index(index_name)
        print(f"Deleted existing index: {index_name}")
    
    # Create index with mapping
    mapping = IndexMapping(
        properties={
            "name": {"type": "text", "analyzer": "standard"},
            "description": {"type": "text"},
            "price": {"type": "float"},
            "category": {"type": "keyword"},
            "in_stock": {"type": "boolean"},
            "created_at": {"type": "date"},
            "tags": {"type": "keyword"}
        },
        settings={
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    )
    
    if es.create_index(index_name, mapping):
        print(f"Created index: {index_name}")
    
    # List indices
    indices = es.list_indices("*")
    print(f"Available indices: {indices}")

def example_document_operations():
    """Demonstrate document CRUD operations"""
    config = ESConfig(hosts=["localhost:9200"])
    es = ElasticsearchManager(config)
    
    index_name = "products"
    
    # Index single document
    doc1 = {
        "name": "iPhone 15 Pro",
        "description": "Latest iPhone with titanium design",
        "price": 999.99,
        "category": "electronics",
        "in_stock": True,
        "created_at": datetime.now().isoformat(),
        "tags": ["phone", "apple", "smartphone"]
    }
    
    result = es.index_document(index_name, doc1, doc_id="iphone-15-pro")
    print(f"Indexed document: {result.get('_id')}")
    
    # Index another document
    doc2 = {
        "name": "MacBook Pro 16",
        "description": "Professional laptop with M3 chip",
        "price": 2499.99,
        "category": "electronics",
        "in_stock": True,
        "created_at": datetime.now().isoformat(),
        "tags": ["laptop", "apple", "computer"]
    }
    
    result = es.index_document(index_name, doc2, doc_id="macbook-pro-16")
    print(f"Indexed document: {result.get('_id')}")
    
    # Get document
    retrieved = es.get_document(index_name, "iphone-15-pro")
    print(f"Retrieved: {retrieved.get('name')}")
    
    # Update document
    es.update_document(index_name, "iphone-15-pro", {"price": 899.99})
    print("Updated document price")
    
    # Bulk index
    bulk_docs = [
        {
            "name": f"Product {i}",
            "price": i * 10.0,
            "category": "general",
            "created_at": datetime.now().isoformat()
        }
        for i in range(10)
    ]
    success, errors = es.bulk_index(index_name, bulk_docs)
    print(f"Bulk indexed: {success} success, {len(errors)} errors")

def example_search_queries():
    """Demonstrate various search queries"""
    config = ESConfig(hosts=["localhost:9200"])
    es = ElasticsearchManager(config)
    
    index_name = "products"
    
    # Match all
    results = es.match_all(index_name, size=5)
    print(f"\nMatch all: {results.total} total")
    
    # Match query
    results = es.match_query(index_name, "name", "iPhone")
    print(f"\nMatch 'iPhone': {results.total} results")
    for hit in results.hits:
        print(f"  - {hit.get('name')}: ${hit.get('price')}")
    
    # Term query
    results = es.term_query(index_name, "category", "electronics")
    print(f"\nCategory 'electronics': {results.total} results")
    
    # Range query
    results = es.range_query(
        index_name,
        "price",
        gte=500,
        lte=2000
    )
    print(f"\nPrice $500-$2000: {results.total} results")
    
    # Boolean query
    results = es.bool_query(
        index_name,
        must=[{"match": {"description": "design"}}],
        filter=[{"term": {"in_stock": True}}]
    )
    print(f"\nBoolean query: {results.total} results")
    
    # Multi-match query
    results = es.multi_match(
        index_name,
        "apple",
        ["name", "description", "tags"]
    )
    print(f"\nMulti-match 'apple': {results.total} results")

def example_aggregations():
    """Demonstrate aggregation queries"""
    config = ESConfig(hosts=["localhost:9200"])
    es = ElasticsearchManager(config)
    
    index_name = "products"
    
    # Terms aggregation
    print("\n=== Category Distribution ===")
    result = es.aggregate_terms(index_name, "category", size=10)
    buckets = result.get("terms_agg", {}).get("buckets", [])
    for bucket in buckets:
        print(f"  {bucket['key']}: {bucket['doc_count']} products")
    
    # Statistics aggregation
    print("\n=== Price Statistics ===")
    result = es.aggregate_stats(index_name, "price")
    stats = result.get("stats_agg", {})
    print(f"  Count: {stats.get('count')}")
    print(f"  Min: ${stats.get('min', 0):.2f}")
    print(f"  Max: ${stats.get('max', 0):.2f}")
    print(f"  Avg: ${stats.get('avg', 0):.2f}")
    print(f"  Sum: ${stats.get('sum', 0):.2f}")
    
    # Date histogram (if date field exists)
    print("\n=== Products by Day ===")
    result = es.aggregate_date_histogram(
        index_name,
        "created_at",
        calendar_interval="day"
    )
    buckets = result.get("date_histogram_agg", {}).get("buckets", [])
    for bucket in buckets:
        print(f"  {bucket['key_as_string']}: {bucket['doc_count']} products")

def example_scroll_search():
    """Demonstrate scroll search for large datasets"""
    config = ESConfig(hosts=["localhost:9200"])
    es = ElasticsearchManager(config)
    
    index_name = "products"
    
    # Use scroll for large result sets
    results = es.scroll_search(
        index_name,
        {"match_all": {}},
        scroll_time="1m",
        batch_size=100
    )
    
    print(f"\nScrolled through {len(results)} documents")
    
    # Process in batches
    for i, doc in enumerate(results[:5]):  # Show first 5
        print(f"  {i+1}. {doc.get('name', 'N/A')}")

def example_reindexing():
    """Demonstrate reindexing data"""
    config = ESConfig(hosts=["localhost:9200"])
    es = ElasticsearchManager(config)
    
    source_index = "products"
    dest_index = "products_v2"
    
    # Create new index
    if not es.index_exists(dest_index):
        mapping = IndexMapping(
            properties={
                "name": {"type": "text"},
                "price": {"type": "float"}
            }
        )
        es.create_index(dest_index, mapping)
    
    # Reindex with filter
    query = {"range": {"price": {"gte": 100}}}
    result = es.reindex_data(source_index, dest_index, query)
    
    print(f"Reindexed: {result.get('total')} documents")
    print(f"Failures: {result.get('failures', [])}")

if __name__ == "__main__":
    print("=" * 60)
    print("Elasticsearch Skill Examples")
    print("=" * 60)
    
    # Note: These examples require a running Elasticsearch instance
    print("\nNote: Ensure Elasticsearch is running on localhost:9200")
    print("-" * 60)
    
    try:
        print("\n1. Basic Connection:")
        example_basic_connection()
    except Exception as e:
        print(f"Skipped: {e}")
    
    try:
        print("\n2. Index Management:")
        example_index_management()
    except Exception as e:
        print(f"Skipped: {e}")
    
    try:
        print("\n3. Document Operations:")
        example_document_operations()
    except Exception as e:
        print(f"Skipped: {e}")
    
    try:
        print("\n4. Search Queries:")
        example_search_queries()
    except Exception as e:
        print(f"Skipped: {e}")
    
    try:
        print("\n5. Aggregations:")
        example_aggregations()
    except Exception as e:
        print(f"Skipped: {e}")
    
    try:
        print("\n6. Scroll Search:")
        example_scroll_search()
    except Exception as e:
        print(f"Skipped: {e}")
