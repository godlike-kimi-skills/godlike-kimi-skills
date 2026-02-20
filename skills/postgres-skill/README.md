# PostgreSQL Skill

A comprehensive PostgreSQL database management tool for Kimi Code CLI.

## Description

PostgreSQL database query and management tool. Supports SQL queries, table structure viewing, data import/export.

**Use when working with PostgreSQL, querying data, or when user mentions 'postgres', 'psql', 'postgresql database'**

## Features

- ✅ SQL query execution
- ✅ Table structure viewing
- ✅ Data export to CSV/JSON
- ✅ Data import from CSV
- ✅ Table backup
- ✅ Connection string support
- ✅ Environment variable configuration

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
# Query data
python main.py query "SELECT * FROM users LIMIT 10" --database mydb --user postgres

# List tables
python main.py tables --database mydb

# Describe table
python main.py describe users --database mydb

# Export to CSV
python main.py export "SELECT * FROM orders" --format csv --output orders.csv
```

## Configuration

Set environment variables:

```bash
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=mydb
export PGUSER=postgres
export PGPASSWORD=secret
```

## Commands

| Command | Description |
|---------|-------------|
| `query` | Execute SQL query |
| `tables` | List all tables |
| `describe` | Show table structure |
| `indexes` | Show table indexes |
| `export` | Export query results |
| `export-table` | Export entire table |
| `import` | Import data from CSV |
| `backup` | Backup table |

## Testing

```bash
python test.py
```

## License

MIT License - see LICENSE file

## Author

KbotGenesis
