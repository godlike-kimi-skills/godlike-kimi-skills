#!/usr/bin/env python3
"""
MySQL Skill - Database query and management tool
Supports SQL queries, table management, data import/export
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

try:
    import pymysql
    from pymysql.cursors import DictCursor
except ImportError:
    print("Error: PyMySQL is required. Install with: pip install PyMySQL")
    sys.exit(1)


class MySQLSkill:
    """MySQL database management skill"""
    
    def __init__(self, connection_params: Dict[str, Any]):
        self.connection_params = connection_params
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = pymysql.connect(**self.connection_params)
            self.cursor = self.conn.cursor(DictCursor)
            return True
        except pymysql.Error as e:
            print(f"Connection error: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute SELECT query and return results"""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except pymysql.Error as e:
            print(f"Query error: {e}")
            return []
    
    def execute_command(self, command: str, params: tuple = None) -> int:
        """Execute non-SELECT command, return affected rows"""
        try:
            self.cursor.execute(command, params)
            self.conn.commit()
            return self.cursor.rowcount
        except pymysql.Error as e:
            print(f"Command error: {e}")
            self.conn.rollback()
            return 0
    
    def get_tables(self) -> List[str]:
        """Get list of all tables"""
        query = "SHOW TABLES"
        result = self.execute_query(query)
        if result:
            key = list(result[0].keys())[0]
            return [row[key] for row in result]
        return []
    
    def describe_table(self, table_name: str) -> List[Dict]:
        """Get table structure"""
        query = f"DESCRIBE {table_name}"
        return self.execute_query(query)
    
    def show_indexes(self, table_name: str) -> List[Dict]:
        """Get table indexes"""
        query = f"SHOW INDEX FROM {table_name}"
        return self.execute_query(query)
    
    def show_create_table(self, table_name: str) -> str:
        """Get CREATE TABLE statement"""
        query = f"SHOW CREATE TABLE {table_name}"
        result = self.execute_query(query)
        if result:
            return result[0].get('Create Table', '')
        return ''
    
    def create_table(self, name: str, columns_def: str):
        """Create new table"""
        query = f"CREATE TABLE IF NOT EXISTS {name} ({columns_def})"
        return self.execute_command(query)
    
    def drop_table(self, name: str):
        """Drop table"""
        query = f"DROP TABLE IF EXISTS {name}"
        return self.execute_command(query)
    
    def export_to_csv(self, query: str, output_file: str):
        """Export query results to CSV"""
        results = self.execute_query(query)
        if not results:
            print("No data to export")
            return
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"Exported {len(results)} rows to {output_file}")
    
    def export_to_json(self, query: str, output_file: str):
        """Export query results to JSON"""
        results = self.execute_query(query)
        # Convert datetime objects to string
        for row in results:
            for key, value in row.items():
                if isinstance(value, datetime):
                    row[key] = value.isoformat()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Exported {len(results)} rows to {output_file}")
    
    def import_from_csv(self, table_name: str, csv_file: str):
        """Import data from CSV file"""
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if not rows:
            print("No data to import")
            return
        
        columns = list(rows[0].keys())
        placeholders = ', '.join(['%s'] * len(columns))
        column_names = ', '.join(columns)
        
        query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
        
        try:
            for row in rows:
                self.cursor.execute(query, tuple(row.values()))
            self.conn.commit()
            print(f"Imported {len(rows)} rows into {table_name}")
        except pymysql.Error as e:
            print(f"Import error: {e}")
            self.conn.rollback()
    
    def get_users(self) -> List[Dict]:
        """Get all database users"""
        query = "SELECT User, Host FROM mysql.user"
        return self.execute_query(query)
    
    def get_grants(self, user: str) -> List[Dict]:
        """Get user privileges"""
        query = f"SHOW GRANTS FOR '{user}'"
        return self.execute_query(query)
    
    def backup_table(self, table_name: str, output_file: str):
        """Backup table to SQL file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"-- Backup of table {table_name}\n")
            f.write(f"-- Generated at: {datetime.now()}\n\n")
            
            # Write CREATE TABLE
            create_stmt = self.show_create_table(table_name)
            f.write(f"{create_stmt};\n\n")
            
            # Write INSERT statements
            data = self.execute_query(f"SELECT * FROM {table_name}")
            for row in data:
                columns = ', '.join(row.keys())
                values = []
                for v in row.values():
                    if v is None:
                        values.append('NULL')
                    elif isinstance(v, (int, float)):
                        values.append(str(v))
                    else:
                        values.append(f"'{str(v).replace(\"'\", \"''\")}'")
                
                f.write(f"INSERT INTO {table_name} ({columns}) VALUES ({', '.join(values)});\n")
        
        print(f"Backup saved to {output_file}")


def parse_connection_string(conn_str: str) -> Dict[str, Any]:
    """Parse MySQL connection string"""
    parsed = urlparse(conn_str)
    return {
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 3306,
        'database': parsed.path[1:] if parsed.path else None,
        'user': parsed.username,
        'password': parsed.password,
        'charset': 'utf8mb4'
    }


def get_connection_params(args) -> Dict[str, Any]:
    """Build connection parameters from args and environment"""
    if args.connection:
        return parse_connection_string(args.connection)
    
    return {
        'host': args.host or os.getenv('MYSQL_HOST', 'localhost'),
        'port': args.port or int(os.getenv('MYSQL_PORT', 3306)),
        'database': args.database or os.getenv('MYSQL_DATABASE'),
        'user': args.user or os.getenv('MYSQL_USER', 'root'),
        'password': args.password or os.getenv('MYSQL_PASSWORD', ''),
        'charset': 'utf8mb4'
    }


def format_table(data: List[Dict]) -> str:
    """Format results as ASCII table"""
    if not data:
        return "No results"
    
    headers = list(data[0].keys())
    col_widths = {h: max(len(h), max(len(str(row.get(h, ''))) for row in data)) for h in headers}
    
    lines = []
    header_line = ' | '.join(h.ljust(col_widths[h]) for h in headers)
    lines.append(header_line)
    lines.append('-' * len(header_line))
    
    for row in data:
        lines.append(' | '.join(str(row.get(h, '')).ljust(col_widths[h]) for h in headers))
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='MySQL Skill - Database management tool')
    parser.add_argument('--host', help='Database host')
    parser.add_argument('--port', type=int, help='Database port')
    parser.add_argument('--database', '-d', help='Database name')
    parser.add_argument('--user', '-u', help='Database user')
    parser.add_argument('--password', '-p', help='Database password')
    parser.add_argument('--connection', '-c', help='Connection string')
    parser.add_argument('--format', choices=['json', 'table'], default='table')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Execute SQL query')
    query_parser.add_argument('sql', help='SQL query')
    
    # Execute file command
    exec_parser = subparsers.add_parser('execute', help='Execute SQL file')
    exec_parser.add_argument('--file', '-f', required=True, help='SQL file path')
    
    # Tables command
    subparsers.add_parser('tables', help='List all tables')
    
    # Describe command
    describe_parser = subparsers.add_parser('describe', help='Describe table')
    describe_parser.add_argument('table', help='Table name')
    
    # Create table command
    create_parser = subparsers.add_parser('create-table', help='Create new table')
    create_parser.add_argument('--name', required=True, help='Table name')
    create_parser.add_argument('--columns', required=True, help='Column definitions')
    
    # Drop table command
    drop_parser = subparsers.add_parser('drop-table', help='Drop table')
    drop_parser.add_argument('table', help='Table name')
    drop_parser.add_argument('--confirm', action='store_true', help='Confirm deletion')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export query results')
    export_parser.add_argument('sql', help='SQL query')
    export_parser.add_argument('--output', '-o', required=True, help='Output file')
    export_parser.add_argument('--format', choices=['csv', 'json'], default='csv')
    
    # Export table command
    export_table_parser = subparsers.add_parser('export-table', help='Export entire table')
    export_table_parser.add_argument('table', help='Table name')
    export_table_parser.add_argument('--output', '-o', required=True, help='Output file')
    export_table_parser.add_argument('--format', choices=['csv', 'json'], default='csv')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import data')
    import_parser.add_argument('table', help='Target table')
    import_parser.add_argument('--source', '-s', required=True, help='Source file')
    import_parser.add_argument('--format', choices=['csv', 'json'], default='csv')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup table/database')
    backup_parser.add_argument('--table', '-t', help='Table to backup')
    backup_parser.add_argument('--output', '-o', required=True, help='Output file')
    
    # Users command
    subparsers.add_parser('users', help='List database users')
    
    # Grants command
    grants_parser = subparsers.add_parser('grants', help='Show user privileges')
    grants_parser.add_argument('user', help='Username')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    conn_params = get_connection_params(args)
    skill = MySQLSkill(conn_params)
    
    if not skill.connect():
        sys.exit(1)
    
    try:
        if args.command == 'query':
            results = skill.execute_query(args.sql)
            if args.format == 'json':
                print(json.dumps(results, indent=2, default=str))
            else:
                print(format_table(results))
        
        elif args.command == 'execute':
            with open(args.file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            for statement in sql_content.split(';'):
                statement = statement.strip()
                if statement:
                    skill.execute_command(statement)
            print("SQL file executed successfully")
        
        elif args.command == 'tables':
            tables = skill.get_tables()
            for table in tables:
                print(table)
        
        elif args.command == 'describe':
            structure = skill.describe_table(args.table)
            print(format_table(structure))
        
        elif args.command == 'create-table':
            skill.create_table(args.name, args.columns)
            print(f"Table {args.name} created successfully")
        
        elif args.command == 'drop-table':
            if args.confirm:
                skill.drop_table(args.table)
                print(f"Table {args.table} dropped")
            else:
                print("Use --confirm to drop table")
        
        elif args.command == 'export':
            if args.format == 'csv':
                skill.export_to_csv(args.sql, args.output)
            else:
                skill.export_to_json(args.sql, args.output)
        
        elif args.command == 'export-table':
            sql_query = f"SELECT * FROM {args.table}"
            if args.format == 'csv':
                skill.export_to_csv(sql_query, args.output)
            else:
                skill.export_to_json(sql_query, args.output)
        
        elif args.command == 'import':
            if args.format == 'csv':
                skill.import_from_csv(args.table, args.source)
            else:
                print("JSON import not implemented in this version")
        
        elif args.command == 'backup':
            if args.table:
                skill.backup_table(args.table, args.output)
            else:
                print("Full database backup requires mysqldump utility")
        
        elif args.command == 'users':
            users = skill.get_users()
            print(format_table(users))
        
        elif args.command == 'grants':
            grants = skill.get_grants(args.user)
            for grant in grants:
                print(list(grant.values())[0])
    
    finally:
        skill.close()



# =============================================================================
# Additional Utility Functions
# =============================================================================

def validate_connection_params(params: Dict[str, Any]) -> bool:
    """Validate connection parameters"""
    required = ['host', 'user']
    for field in required:
        if not params.get(field):
            print(f"Error: Missing required parameter '{field}'")
            return False
    return True


def print_query_plan(skill: MySQLSkill, query: str):
    """Display query execution plan"""
    try:
        result = skill.execute_query(f"EXPLAIN {query}")
        print("Query Plan:")
        print(format_table(result))
    except Exception as e:
        print(f"Could not get query plan: {e}")


def batch_execute(skill: MySQLSkill, queries: List[str]) -> Dict[str, Any]:
    """Execute multiple queries in batch"""
    results = {
        'success': [],
        'failed': [],
        'total': len(queries)
    }
    
    for i, query in enumerate(queries):
        query = query.strip()
        if not query:
            continue
        try:
            skill.execute_command(query)
            results['success'].append(i)
        except Exception as e:
            results['failed'].append({'index': i, 'error': str(e)})
    
    return results


def get_database_size(skill: MySQLSkill) -> str:
    """Get database size information"""
    query = """
        SELECT 
            table_schema as db_name,
            SUM(data_length + index_length) / 1024 / 1024 as size_mb
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
        GROUP BY table_schema
    """
    result = skill.execute_query(query)
    if result:
        return f"{result[0]['size_mb']:.2f} MB"
    return 'Unknown'


def get_table_stats(skill: MySQLSkill, table_name: str) -> Dict[str, Any]:
    """Get table statistics"""
    stats = {}
    
    # Row count and size
    query = """
        SELECT 
            table_rows as row_count,
            ROUND(data_length / 1024 / 1024, 2) as data_size_mb,
            ROUND(index_length / 1024 / 1024, 2) as index_size_mb
        FROM information_schema.tables
        WHERE table_schema = DATABASE() AND table_name = %s
    """
    result = skill.execute_query(query, (table_name,))
    if result:
        stats = result[0]
    
    return stats


def search_columns(skill: MySQLSkill, search_term: str) -> List[Dict]:
    """Search for columns across all tables"""
    query = """
        SELECT 
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
            AND column_name LIKE %s
        ORDER BY table_name, column_name
    """
    return skill.execute_query(query, (f'%{search_term}%',))


def copy_table(skill: MySQLSkill, source_table: str, target_table: str):
    """Copy table structure and data"""
    # Get create statement
    ddl = skill.show_create_table(source_table)
    new_ddl = ddl.replace(f'CREATE TABLE `{source_table}`', 
                          f'CREATE TABLE `{target_table}`')
    
    skill.execute_command(new_ddl)
    skill.execute_command(f"INSERT INTO {target_table} SELECT * FROM {source_table}")
    
    print(f"Table {source_table} copied to {target_table}")


def compare_tables(skill: MySQLSkill, table1: str, table2: str) -> List[Dict]:
    """Compare structure of two tables"""
    cols1 = {col['Field']: col for col in skill.describe_table(table1)}
    cols2 = {col['Field']: col for col in skill.describe_table(table2)}
    
    differences = []
    all_cols = set(cols1.keys()) | set(cols2.keys())
    
    for col in all_cols:
        if col not in cols1:
            differences.append({'column': col, 'status': f'only in {table2}'})
        elif col not in cols2:
            differences.append({'column': col, 'status': f'only in {table1}'})
        elif cols1[col]['Type'] != cols2[col]['Type']:
            differences.append({
                'column': col,
                'status': 'type mismatch',
                table1: cols1[col]['Type'],
                table2: cols2[col]['Type']
            })
    
    return differences


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == '__main__':
    main()
