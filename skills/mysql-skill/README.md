# MySQL Skill

A comprehensive MySQL/MariaDB database management tool for Kimi Code CLI.

## Description

MySQL/MariaDB database query and management tool. Supports SQL queries, table management, data import/export.

**Use when working with MySQL, querying data, or when user mentions 'mysql', 'mariadb', 'mysql database'**

## Features

- ✅ SQL query execution
- ✅ Table management (create, alter, describe)
- ✅ Data export to CSV/JSON
- ✅ Data import from CSV
- ✅ User and privileges listing
- ✅ Database backup
- ✅ Environment variable configuration

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
# Query data
python main.py query "SELECT * FROM users LIMIT 10" --database mydb --user root

# List tables
python main.py tables --database mydb

# Create table
python main.py create-table --name products --columns "id INT PRIMARY KEY, name VARCHAR(100)"

# Export to CSV
python main.py export "SELECT * FROM orders" --format csv --output orders.csv
```

## Configuration

Set environment variables:

```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_DATABASE=mydb
export MYSQL_USER=root
export MYSQL_PASSWORD=secret
```

## Commands

| Command | Description |
|---------|-------------|
| `query` | Execute SQL query |
| `execute` | Execute SQL file |
| `tables` | List all tables |
| `describe` | Describe table |
| `create-table` | Create new table |
| `drop-table` | Drop table (with confirmation) |
| `export` | Export query results |
| `export-table` | Export entire table |
| `import` | Import data |
| `backup` | Backup table |
| `users` | List database users |
| `grants` | Show user privileges |

## Testing

```bash
python test.py
```

## License

MIT License - see LICENSE file

## Author

KbotGenesis
