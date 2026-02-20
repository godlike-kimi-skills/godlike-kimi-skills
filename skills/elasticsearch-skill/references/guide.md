# Elasticsearch Guide

## Table of Contents
1. [Query DSL](#query-dsl)
2. [Mappings](#mappings)
3. [Aggregations](#aggregations)
4. [Performance](#performance)
5. [Best Practices](#best-practices)

## Query DSL <a name="query-dsl"></a>

### Match Query
Full-text search with relevance scoring:
```json
{
  "query": {
    "match": {
      "title": {
        "query": "quick brown fox",
        "operator": "and"
      }
    }
  }
}
```

### Term Query
Exact value matching (no analysis):
```json
{
  "query": {
    "term": {
      "status": "published"
    }
  }
}
```

### Range Query
Numeric/date ranges:
```json
{
  "query": {
    "range": {
      "price": {
        "gte": 10,
        "lte": 100
      }
    }
  }
}
```

### Bool Query
Combine multiple conditions:
```json
{
  "query": {
    "bool": {
      "must": [
        { "match": { "title": "search" } }
      ],
      "filter": [
        { "term": { "status": "active" } },
        { "range": { "created_at": { "gte": "2024-01-01" } } }
      ],
      "must_not": [
        { "match": { "hidden": true } }
      ],
      "should": [
        { "match": { "featured": true } }
      ]
    }
  }
}
```

## Mappings <a name="mappings"></a>

### Field Types
| Type | Use Case |
|------|----------|
| text | Full-text search, analyzed |
| keyword | Exact matching, sorting, aggregations |
| integer | Whole numbers |
| float | Decimal numbers |
| date | Dates and times |
| boolean | true/false values |
| object | Nested JSON objects |
| nested | Arrays of objects (separate indexing) |

### Dynamic Templates
```json
{
  "mappings": {
    "dynamic_templates": [
      {
        "strings_as_keywords": {
          "match_mapping_type": "string",
          "mapping": {
            "type": "keyword"
          }
        }
      }
    ]
  }
}
```

## Aggregations <a name="aggregations"></a>

### Terms Aggregation
```json
{
  "aggs": {
    "by_category": {
      "terms": {
        "field": "category",
        "size": 10
      }
    }
  }
}
```

### Date Histogram
```json
{
  "aggs": {
    "over_time": {
      "date_histogram": {
        "field": "created_at",
        "calendar_interval": "day"
      }
    }
  }
}
```

### Stats Aggregation
```json
{
  "aggs": {
    "price_stats": {
      "stats": {
        "field": "price"
      }
    }
  }
}
```

### Sub-aggregations
```json
{
  "aggs": {
    "by_category": {
      "terms": {
        "field": "category"
      },
      "aggs": {
        "avg_price": {
          "avg": {
            "field": "price"
          }
        }
      }
    }
  }
}
```

## Performance <a name="performance"></a>

### Index Settings
```json
{
  "settings": {
    "number_of_shards": 5,
    "number_of_replicas": 1,
    "refresh_interval": "30s",
    "index.store.preload": ["nvd", "dvd"]
  }
}
```

### Search Optimization
- Use `filter` context for caching
- Limit result size
- Use `_source` filtering
- Implement pagination with `search_after`

### Bulk Operations
```python
# Use bulk API for indexing
from elasticsearch.helpers import bulk

actions = [
    {"_index": "products", "_source": doc}
    for doc in documents
]
bulk(es.client, actions)
```

## Best Practices <a name="best-practices"></a>

### Index Naming
```
logs-2024.01.15          # Time-based
products-v2              # Versioned
user-events-prod         # Environment
```

### Document Design
- Keep documents under 1MB
- Avoid deeply nested objects
- Use `_source` filtering
- Consider denormalization for search

### Query Patterns
1. **Filter First**: Use filters before queries
2. **Pagination**: Use `search_after` not `from`
3. **Caching**: Enable request cache for repeated queries
4. **Routing**: Use custom routing for related data

### Monitoring
Check these metrics regularly:
- Indexing rate
- Search latency
- JVM heap usage
- Disk usage
- Circuit breaker trips
