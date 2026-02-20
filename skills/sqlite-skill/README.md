# SQLite Skill

A comprehensive SQLite local database management tool for Kimi Code CLI.

## Description

SQLite local database management tool. Supports database creation, SQL queries, data backup and maintenance.

**Use when working with SQLite, querying data, or when user mentions 'sqlite', 'sqlite3', 'local database'**

## Features

- ✅ Local database creation and management
- ✅ SQL query execution
- ✅ Data export to CSV/JSON/SQL
- ✅ Data import from CSV
- ✅ Database backup and optimization (VACUUM)
- ✅ Integrity checking
- ✅ PRAGMA command support
- ✅ In-memory database support

## Installation

No external dependencies required - uses Python's built-in sqlite3 module.

## Quick Start

```bash
# Query existing database
python main.py query "SELECT * FROM users" --database app.db

# List tables
python main.py tables --database app.db

# Export to CSV
python main.py export users --format csv --output users.csv --database app.db

# Import from CSV (auto-creates table)
python main.py import data.csv --table users --database app.db

# Backup database
python main.py backup app_backup.db --database app.db
```

## Configuration

No configuration required - SQLite is file-based.

## Commands

| Command | Description |
|---------|-------------|
| `query` | Execute SQL query |
| `tables` | List all tables |
| `schema` | Show table schema |
| `indexes` | Show table indexes |
| `ddl` | Show CREATE TABLE statement |
| `info` | Show database information |
| `export` | Export table/query |
| `import` | Import from CSV |
| `vacuum` | Optimize database |
| `check` | Check database integrity |
| `backup` | Backup database file |
| `pragma` | Execute PRAGMA command |

## Testing

```bash
python test.py
```

## License

MIT License - see LICENSE file

## Author

KbotGenesis
