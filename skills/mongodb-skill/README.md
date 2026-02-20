# MongoDB Skill

A comprehensive MongoDB document database management tool for Kimi Code CLI.

## Description

MongoDB document database management tool. Supports document queries, aggregation pipelines, data backup.

**Use when working with MongoDB, querying data, or when user mentions 'mongodb', 'mongo', 'nosql database'**

## Features

- ✅ Document CRUD operations
- ✅ Aggregation pipeline execution
- ✅ Data export to CSV/JSON
- ✅ Data import from JSON
- ✅ Index management
- ✅ Collection statistics
- ✅ MongoDB Atlas support
- ✅ Replica set and sharded cluster support

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
# Find documents
python main.py find users --database mydb --limit 10

# Query with filter
python main.py find users --database mydb --filter '{"age": {"$gte": 18}}'

# Aggregation
python main.py aggregate orders --database mydb --pipeline '[{"$group": {"_id": "$status", "count": {"$sum": 1}}}]'

# Export collection
python main.py export users --database mydb --output users.json
```

## Configuration

Set environment variables:

```bash
export MONGODB_URI=mongodb://localhost:27017
export MONGODB_DATABASE=mydb
```

Or use MongoDB Atlas:

```bash
export MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net
```

## Commands

| Command | Description |
|---------|-------------|
| `databases` | List all databases |
| `collections` | List collections |
| `find` | Find documents |
| `aggregate` | Run aggregation pipeline |
| `insert` | Insert document |
| `insert-many` | Insert multiple documents |
| `update` | Update document |
| `update-many` | Update multiple documents |
| `delete` | Delete document |
| `delete-many` | Delete multiple documents |
| `count` | Count documents |
| `stats` | Collection statistics |
| `export` | Export collection |
| `import` | Import documents |
| `create-index` | Create index |
| `indexes` | List indexes |
| `drop-index` | Drop index |

## Testing

```bash
python test.py
```

## License

MIT License - see LICENSE file

## Author

KbotGenesis
