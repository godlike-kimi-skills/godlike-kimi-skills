#!/usr/bin/env python3
"""
Elasticsearch Search Management Skill
Supports: index management, Query DSL, aggregations, full-text search
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, scan, reindex
import urllib3

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ESConfig:
    """Elasticsearch connection configuration"""
    hosts: List[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    use_ssl: bool = False
    verify_certs: bool = False
    ca_certs: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    
    def __post_init__(self):
        if self.hosts is None:
            self.hosts = ["localhost:9200"]

@dataclass
class IndexMapping:
    """Index mapping definition"""
    properties: Dict[str, Any]
    settings: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"mappings": {"properties": self.properties}}
        if self.settings:
            result["settings"] = self.settings
        return result

@dataclass
class QueryResult:
    """Search query result"""
    total: int
    hits: List[Dict[str, Any]]
    took: int
    scroll_id: Optional[str] = None
    aggregations: Optional[Dict[str, Any]] = None

# ============================================================================
# Elasticsearch Manager
# ============================================================================

class ElasticsearchManager:
    """Main class for managing Elasticsearch"""
    
    def __init__(self, config: ESConfig = None):
        self.config = config or ESConfig()
        self._client: Optional[Elasticsearch] = None
    
    @property
    def client(self) -> Elasticsearch:
        """Get or create Elasticsearch client"""
        if self._client is None:
            conn_params = {
                "hosts": self.config.hosts,
                "timeout": self.config.timeout,
                "max_retries": self.config.max_retries,
                "retry_on_timeout": True
            }
            
            if self.config.use_ssl:
                conn_params["use_ssl"] = True
                conn_params["verify_certs"] = self.config.verify_certs
                if self.config.ca_certs:
                    conn_params["ca_certs"] = self.config.ca_certs
            
            if self.config.username and self.config.password:
                conn_params["basic_auth"] = (self.config.username, self.config.password)
            elif self.config.api_key:
                conn_params["api_key"] = self.config.api_key
            
            self._client = Elasticsearch(**conn_params)
        return self._client
    
    def connect(self) -> bool:
        """Test connection to Elasticsearch"""
        try:
            return self.client.ping()
        except Exception:
            return False
    
    def info(self) -> Dict[str, Any]:
        """Get cluster information"""
        return self.client.info()
    
    def health(self) -> Dict[str, Any]:
        """Get cluster health status"""
        return self.client.cluster.health()
    
    # ========================================================================
    # Index Management
    # ========================================================================
    
    def create_index(self, index_name: str, mapping: IndexMapping = None,
                     settings: Dict[str, Any] = None) -> bool:
        """Create a new index"""
        try:
            body = {}
            if mapping:
                body.update(mapping.to_dict())
            if settings:
                body.setdefault("settings", {}).update(settings)
            
            self.client.indices.create(index=index_name, body=body if body else None)
            return True
        except Exception as e:
            print(f"Error creating index: {e}")
            return False
    
    def delete_index(self, index_name: str) -> bool:
        """Delete an index"""
        try:
            self.client.indices.delete(index=index_name)
            return True
        except Exception:
            return False
    
    def index_exists(self, index_name: str) -> bool:
        """Check if index exists"""
        return self.client.indices.exists(index=index_name)
    
    def get_mapping(self, index_name: str) -> Dict[str, Any]:
        """Get index mapping"""
        return self.client.indices.get_mapping(index=index_name)
    
    def update_mapping(self, index_name: str, properties: Dict[str, Any]) -> bool:
        """Update index mapping"""
        try:
            self.client.indices.put_mapping(
                index=index_name,
                body={"properties": properties}
            )
            return True
        except Exception:
            return False
    
    def list_indices(self, pattern: str = "*") -> List[str]:
        """List all indices matching pattern"""
        indices = self.client.indices.get(index=pattern)
        return list(indices.keys())
    
    def get_index_stats(self, index_name: str) -> Dict[str, Any]:
        """Get index statistics"""
        return self.client.indices.stats(index=index_name)
    
    def refresh_index(self, index_name: str) -> None:
        """Refresh an index"""
        self.client.indices.refresh(index=index_name)
    
    def reindex_data(self, source_index: str, dest_index: str,
                     query: Dict[str, Any] = None) -> Dict[str, Any]:
        """Reindex data from source to destination"""
        body = {
            "source": {"index": source_index},
            "dest": {"index": dest_index}
        }
        if query:
            body["source"]["query"] = query
        
        return self.client.reindex(body=body, wait_for_completion=True)
    
    # ========================================================================
    # Document Operations
    # ========================================================================
    
    def index_document(self, index_name: str, document: Dict[str, Any],
                       doc_id: Optional[str] = None) -> Dict[str, Any]:
        """Index a single document"""
        return self.client.index(index=index_name, id=doc_id, body=document)
    
    def get_document(self, index_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        try:
            result = self.client.get(index=index_name, id=doc_id)
            return result.get("_source")
        except Exception:
            return None
    
    def update_document(self, index_name: str, doc_id: str,
                        document: Dict[str, Any]) -> Dict[str, Any]:
        """Update a document"""
        return self.client.update(
            index=index_name,
            id=doc_id,
            body={"doc": document}
        )
    
    def delete_document(self, index_name: str, doc_id: str) -> bool:
        """Delete a document"""
        try:
            self.client.delete(index=index_name, id=doc_id)
            return True
        except Exception:
            return False
    
    def bulk_index(self, index_name: str, documents: List[Dict[str, Any]],
                   doc_id_field: Optional[str] = None) -> Tuple[int, List]:
        """Bulk index documents"""
        actions = []
        for doc in documents:
            action = {
                "_index": index_name,
                "_source": doc
            }
            if doc_id_field and doc_id_field in doc:
                action["_id"] = doc[doc_id_field]
            actions.append(action)
        
        success, errors = bulk(self.client, actions)
        return success, errors
    
    # ========================================================================
    # Query DSL
    # ========================================================================
    
    def search(self, index_name: str, query: Dict[str, Any],
               size: int = 10, from_offset: int = 0,
               sort: List[Dict[str, Any]] = None,
               aggs: Dict[str, Any] = None) -> QueryResult:
        """Execute a search query"""
        body = {"query": query}
        
        if sort:
            body["sort"] = sort
        if aggs:
            body["aggs"] = aggs
        
        result = self.client.search(
            index=index_name,
            body=body,
            size=size,
            from_=from_offset
        )
        
        return QueryResult(
            total=result["hits"]["total"]["value"] if isinstance(result["hits"]["total"], dict) else result["hits"]["total"],
            hits=[hit["_source"] for hit in result["hits"]["hits"]],
            took=result["took"],
            aggregations=result.get("aggregations")
        )
    
    def match_all(self, index_name: str, size: int = 10) -> QueryResult:
        """Match all documents"""
        return self.search(index_name, {"match_all": {}}, size=size)
    
    def match_query(self, index_name: str, field: str, query: str,
                    size: int = 10) -> QueryResult:
        """Simple match query"""
        return self.search(index_name, {"match": {field: query}}, size=size)
    
    def term_query(self, index_name: str, field: str, value: Any,
                   size: int = 10) -> QueryResult:
        """Term query for exact matching"""
        return self.search(index_name, {"term": {field: value}}, size=size)
    
    def range_query(self, index_name: str, field: str,
                    gte: Any = None, lte: Any = None,
                    gt: Any = None, lt: Any = None,
                    size: int = 10) -> QueryResult:
        """Range query"""
        range_params = {}
        if gte is not None:
            range_params["gte"] = gte
        if lte is not None:
            range_params["lte"] = lte
        if gt is not None:
            range_params["gt"] = gt
        if lt is not None:
            range_params["lt"] = lt
        
        return self.search(index_name, {"range": {field: range_params}}, size=size)
    
    def bool_query(self, index_name: str,
                   must: List[Dict] = None,
                   should: List[Dict] = None,
                   must_not: List[Dict] = None,
                   filter_: List[Dict] = None,
                   size: int = 10) -> QueryResult:
        """Boolean query with multiple conditions"""
        bool_body = {}
        if must:
            bool_body["must"] = must
        if should:
            bool_body["should"] = should
        if must_not:
            bool_body["must_not"] = must_not
        if filter_:
            bool_body["filter"] = filter_
        
        return self.search(index_name, {"bool": bool_body}, size=size)
    
    def multi_match(self, index_name: str, query: str, fields: List[str],
                    size: int = 10) -> QueryResult:
        """Multi-field match query"""
        return self.search(index_name, {
            "multi_match": {
                "query": query,
                "fields": fields
            }
        }, size=size)
    
    # ========================================================================
    # Aggregations
    # ========================================================================
    
    def aggregate_terms(self, index_name: str, field: str, size: int = 10,
                        query: Dict[str, Any] = None) -> Dict[str, Any]:
        """Terms aggregation"""
        aggs = {
            "terms_agg": {
                "terms": {"field": field, "size": size}
            }
        }
        result = self.search(index_name, query or {"match_all": {}}, size=0, aggs=aggs)
        return result.aggregations
    
    def aggregate_stats(self, index_name: str, field: str,
                        query: Dict[str, Any] = None) -> Dict[str, Any]:
        """Statistics aggregation"""
        aggs = {
            "stats_agg": {
                "stats": {"field": field}
            }
        }
        result = self.search(index_name, query or {"match_all": {}}, size=0, aggs=aggs)
        return result.aggregations
    
    def aggregate_histogram(self, index_name: str, field: str, interval: int,
                            query: Dict[str, Any] = None) -> Dict[str, Any]:
        """Histogram aggregation"""
        aggs = {
            "histogram_agg": {
                "histogram": {"field": field, "interval": interval}
            }
        }
        result = self.search(index_name, query or {"match_all": {}}, size=0, aggs=aggs)
        return result.aggregations
    
    def aggregate_date_histogram(self, index_name: str, field: str,
                                 calendar_interval: str = "day",
                                 query: Dict[str, Any] = None) -> Dict[str, Any]:
        """Date histogram aggregation"""
        aggs = {
            "date_histogram_agg": {
                "date_histogram": {
                    "field": field,
                    "calendar_interval": calendar_interval
                }
            }
        }
        result = self.search(index_name, query or {"match_all": {}}, size=0, aggs=aggs)
        return result.aggregations
    
    # ========================================================================
    # Scroll API
    # ========================================================================
    
    def scroll_search(self, index_name: str, query: Dict[str, Any],
                      scroll_time: str = "1m", batch_size: int = 1000) -> List[Dict]:
        """Search using scroll API for large result sets"""
        results = []
        
        # Initial search
        result = self.client.search(
            index=index_name,
            body={"query": query},
            scroll=scroll_time,
            size=batch_size
        )
        
        scroll_id = result.get("_scroll_id")
        hits = result["hits"]["hits"]
        results.extend([h["_source"] for h in hits])
        
        # Continue scrolling
        while hits:
            result = self.client.scroll(scroll_id=scroll_id, scroll=scroll_time)
            scroll_id = result.get("_scroll_id")
            hits = result["hits"]["hits"]
            results.extend([h["_source"] for h in hits])
        
        # Clear scroll
        self.client.clear_scroll(scroll_id=scroll_id)
        
        return results

# ============================================================================
# CLI Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Elasticsearch Manager")
    parser.add_argument("--host", default="localhost:9200", help="ES host")
    parser.add_argument("--username", help="Username")
    parser.add_argument("--password", help="Password")
    parser.add_argument("--ssl", action="store_true", help="Use SSL")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Connection
    subparsers.add_parser("ping", help="Test connection")
    subparsers.add_parser("info", help="Cluster info")
    subparsers.add_parser("health", help="Cluster health")
    
    # Index management
    create_parser = subparsers.add_parser("create-index", help="Create index")
    create_parser.add_argument("index", help="Index name")
    create_parser.add_argument("--shards", type=int, default=1, help="Number of shards")
    create_parser.add_argument("--replicas", type=int, default=0, help="Number of replicas")
    
    delete_parser = subparsers.add_parser("delete-index", help="Delete index")
    delete_parser.add_argument("index", help="Index name")
    
    subparsers.add_parser("list-indices", help="List all indices")
    
    # Document operations
    index_parser = subparsers.add_parser("index-doc", help="Index document")
    index_parser.add_argument("index", help="Index name")
    index_parser.add_argument("--doc", required=True, help="JSON document")
    index_parser.add_argument("--id", help="Document ID")
    
    get_parser = subparsers.add_parser("get-doc", help="Get document")
    get_parser.add_argument("index", help="Index name")
    get_parser.add_argument("id", help="Document ID")
    
    # Search
    search_parser = subparsers.add_parser("search", help="Search documents")
    search_parser.add_argument("index", help="Index name")
    search_parser.add_argument("--query", default="*", help="Search query")
    search_parser.add_argument("--field", help="Search field")
    search_parser.add_argument("--size", type=int, default=10, help="Result size")
    
    # Aggregation
    agg_parser = subparsers.add_parser("aggregate", help="Run aggregation")
    agg_parser.add_argument("index", help="Index name")
    agg_parser.add_argument("--field", required=True, help="Field to aggregate")
    agg_parser.add_argument("--type", default="terms", 
                            choices=["terms", "stats", "histogram"],
                            help="Aggregation type")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    config = ESConfig(
        hosts=[args.host],
        username=args.username,
        password=args.password,
        use_ssl=args.ssl
    )
    
    manager = ElasticsearchManager(config)
    
    if args.command == "ping":
        print("Connected" if manager.connect() else "Failed")
    
    elif args.command == "info":
        print(json.dumps(manager.info(), indent=2))
    
    elif args.command == "health":
        print(json.dumps(manager.health(), indent=2))
    
    elif args.command == "create-index":
        settings = {
            "number_of_shards": args.shards,
            "number_of_replicas": args.replicas
        }
        if manager.create_index(args.index, settings=settings):
            print(f"Created index: {args.index}")
    
    elif args.command == "delete-index":
        if manager.delete_index(args.index):
            print(f"Deleted index: {args.index}")
    
    elif args.command == "list-indices":
        indices = manager.list_indices()
        for idx in indices:
            print(idx)
    
    elif args.command == "index-doc":
        doc = json.loads(args.doc)
        result = manager.index_document(args.index, doc, args.id)
        print(json.dumps(result, indent=2))
    
    elif args.command == "get-doc":
        doc = manager.get_document(args.index, args.id)
        if doc:
            print(json.dumps(doc, indent=2))
        else:
            print("Document not found")
    
    elif args.command == "search":
        if args.field:
            result = manager.match_query(args.index, args.field, args.query, args.size)
        else:
            result = manager.match_all(args.index, args.size)
        print(json.dumps(result.hits, indent=2))
    
    elif args.command == "aggregate":
        if args.type == "terms":
            result = manager.aggregate_terms(args.index, args.field)
        elif args.type == "stats":
            result = manager.aggregate_stats(args.index, args.field)
        else:
            result = manager.aggregate_histogram(args.index, args.field, 10)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
