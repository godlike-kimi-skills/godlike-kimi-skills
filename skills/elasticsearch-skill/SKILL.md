---
name: elasticsearch-skill
description: Elasticsearch search management with index operations, Query DSL, aggregations, and full-text search. Use when implementing search functionality, managing search indexes, building analytics dashboards, or querying large datasets. Supports complex queries, aggregations, and bulk operations.
---

# Elasticsearch Search Management Skill

## Use When
- Setting up search functionality for applications
- Managing search indexes and mappings
- Building analytics with aggregations
- Implementing full-text search
- Performing complex queries with Query DSL
- Bulk indexing documents
- Reindexing data between indexes

## Out of Scope
- Elasticsearch cluster setup and configuration
- Security and authentication setup
- Complex machine learning features
- Geo-spatial queries (basic support only)
- Cross-cluster search
- Snapshot and restore management
- ILM (Index Lifecycle Management) policies

## Quick Start

```python
from scripts.main import ElasticsearchManager, ESConfig, IndexMapping

# Initialize connection
config = ESConfig(
    hosts=["localhost:9200"],
    username="elastic",
    password="changeme"
)
es = ElasticsearchManager(config)

# Create index
mapping = IndexMapping(
    properties={
        "title": {"type": "text"},
        "price": {"type": "float"},
        "created_at": {"type": "date"}
    }
)
es.create_index("products", mapping)

# Index document
doc = {"title": "iPhone 15", "price": 999.99, "created_at": "2024-01-15"}
es.index_document("products", doc)

# Search
results = es.match_query("products", "title", "iPhone")
print(f"Found {results.total} results")
```

## Core Features

### Index Management
- Create/delete indexes
- Define mappings and settings
- Update mappings
- List and inspect indexes
- Refresh and reindex operations

### Query DSL Support
- Full-text match queries
- Term queries for exact matches
- Range queries for numbers/dates
- Boolean queries (must/should/must_not/filter)
- Multi-match across fields

### Aggregations
- Terms aggregations (group by field)
- Statistics aggregations (min/max/avg/sum)
- Histogram aggregations
- Date histogram for time series

### Document Operations
- Single document CRUD
- Bulk indexing
- Update by query
- Scroll API for large datasets

## CLI Usage

```bash
# Connection testing
python scripts/main.py --host localhost:9200 ping
python scripts/main.py --host localhost:9200 info
python scripts/main.py --host localhost:9200 health

# Index management
python scripts/main.py create-index products --shards 3 --replicas 1
python scripts/main.py list-indices
python scripts/main.py delete-index old_index

# Document operations
python scripts/main.py index-doc products --doc '{"title": "Test"}' --id doc1
python scripts/main.py get-doc products doc1

# Search
python scripts/main.py search products --query "iphone" --field title --size 20
python scripts/main.py search products  # Match all

# Aggregations
python scripts/main.py aggregate products --field category --type terms
python scripts/main.py aggregate products --field price --type stats
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| hosts | ["localhost:9200"] | Elasticsearch nodes |
| username | None | Authentication username |
| password | None | Authentication password |
| use_ssl | False | Enable HTTPS |
| verify_certs | False | Verify SSL certificates |
| timeout | 30 | Request timeout in seconds |
| max_retries | 3 | Retry failed requests |

## Query Examples

### Boolean Query
```python
results = es.bool_query(
    "products",
    must=[{"match": {"title": "iphone"}}],
    filter=[{"range": {"price": {"gte": 500, "lte": 1000}}}]
)
```

### Range Query
```python
results = es.range_query(
    "products",
    "price",
    gte=100,
    lte=500
)
```

### Aggregation Query
```python
results = es.aggregate_date_histogram(
    "logs",
    "timestamp",
    calendar_interval="day"
)
```
