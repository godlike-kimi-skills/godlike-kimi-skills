#!/usr/bin/env python3
"""
PostgreSQL Skill - Database query and management tool
Supports SQL queries, table structure viewing, data import/export
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
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2 import sql
except ImportError:
    print("Error: psycopg2-binary is required. Install with: pip install psycopg2-binary")
    sys.exit(1)


class PostgresSkill:
    """PostgreSQL database management skill"""
    
    def __init__(self, connection_params: Dict[str, Any]):
        self.connection_params = connection_params
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            return True
        except psycopg2.Error as e:
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
        except psycopg2.Error as e:
            print(f"Query error: {e}")
            return []
    
    def execute_command(self, command: str, params: tuple = None) -> bool:
        """Execute non-SELECT command (INSERT/UPDATE/DELETE)"""
        try:
            self.cursor.execute(command, params)
            self.conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"Command error: {e}")
            self.conn.rollback()
            return False
    
    def get_tables(self) -> List[str]:
        """Get list of all tables"""
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        result = self.execute_query(query)
        return [row['table_name'] for row in result]
    
    def describe_table(self, table_name: str) -> List[Dict]:
        """Get table structure"""
        query = """
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = %s AND table_schema = 'public'
            ORDER BY ordinal_position
        """
        return self.execute_query(query, (table_name,))
    
    def get_indexes(self, table_name: str) -> List[Dict]:
        """Get table indexes"""
        query = """
            SELECT
                indexname,
                indexdef
            FROM pg_indexes
            WHERE tablename = %s AND schemaname = 'public'
        """
        return self.execute_query(query, (table_name,))
    
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
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
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
        except psycopg2.Error as e:
            print(f"Import error: {e}")
            self.conn.rollback()
    
    def backup_table(self, table_name: str, output_file: str):
        """Backup table to SQL file"""
        # Get table schema
        schema_query = f"""
            SELECT 'CREATE TABLE IF NOT EXISTS ' || tablename || ' (' ||
                string_agg(column_name || ' ' || data_type, ', ' ORDER BY ordinal_position) ||
            ');' as create_stmt
            FROM (
                SELECT tablename, column_name, data_type, ordinal_position
                FROM pg_catalog.pg_tables t
                JOIN information_schema.columns c ON c.table_name = t.tablename
                WHERE t.tablename = '{table_name}' AND t.schemaname = 'public'
            ) sub
            GROUP BY tablename
        """
        
        with open(output_file, 'w') as f:
            f.write(f"-- Backup of table {table_name}\n")
            f.write(f"-- Generated at: {datetime.now()}\n\n")
            
            # Export data as INSERT statements
            data = self.execute_query(f"SELECT * FROM {table_name}")
            for row in data:
                columns = ', '.join(row.keys())
                values = ', '.join([f"'{v}'" if v is not None else 'NULL' for v in row.values()])
                f.write(f"INSERT INTO {table_name} ({columns}) VALUES ({values});\n")
        
        print(f"Backup saved to {output_file}")


def parse_connection_string(conn_str: str) -> Dict[str, Any]:
    """Parse PostgreSQL connection string"""
    parsed = urlparse(conn_str)
    return {
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 5432,
        'database': parsed.path[1:] if parsed.path else None,
        'user': parsed.username,
        'password': parsed.password
    }


def get_connection_params(args) -> Dict[str, Any]:
    """Build connection parameters from args and environment"""
    if args.connection:
        return parse_connection_string(args.connection)
    
    return {
        'host': args.host or os.getenv('PGHOST', 'localhost'),
        'port': args.port or int(os.getenv('PGPORT', 5432)),
        'database': args.database or os.getenv('PGDATABASE'),
        'user': args.user or os.getenv('PGUSER', 'postgres'),
        'password': args.password or os.getenv('PGPASSWORD', '')
    }


def format_table(data: List[Dict]) -> str:
    """Format results as ASCII table"""
    if not data:
        return "No results"
    
    headers = list(data[0].keys())
    col_widths = {h: max(len(h), max(len(str(row.get(h, ''))) for row in data)) for h in headers}
    
    lines = []
    # Header
    header_line = ' | '.join(h.ljust(col_widths[h]) for h in headers)
    lines.append(header_line)
    lines.append('-' * len(header_line))
    
    # Data rows
    for row in data:
        lines.append(' | '.join(str(row.get(h, '')).ljust(col_widths[h]) for h in headers))
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='PostgreSQL Skill - Database management tool')
    parser.add_argument('--host', help='Database host')
    parser.add_argument('--port', type=int, help='Database port')
    parser.add_argument('--database', '-d', help='Database name')
    parser.add_argument('--user', '-u', help='Database user')
    parser.add_argument('--password', '-p', help='Database password')
    parser.add_argument('--connection', '-c', help='Connection string')
    parser.add_argument('--format', choices=['json', 'table'], default='table', help='Output format')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Execute SQL query')
    query_parser.add_argument('sql', help='SQL query')
    
    # Tables command
    subparsers.add_parser('tables', help='List all tables')
    
    # Describe command
    describe_parser = subparsers.add_parser('describe', help='Describe table structure')
    describe_parser.add_argument('table', help='Table name')
    
    # Indexes command
    indexes_parser = subparsers.add_parser('indexes', help='Show table indexes')
    indexes_parser.add_argument('table', help='Table name')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export query results')
    export_parser.add_argument('sql', help='SQL query')
    export_parser.add_argument('--output', '-o', required=True, help='Output file')
    export_parser.add_argument('--format', choices=['csv', 'json'], default='csv')
    
    # Export-table command
    export_table_parser = subparsers.add_parser('export-table', help='Export entire table')
    export_table_parser.add_argument('table', help='Table name')
    export_table_parser.add_argument('--output', '-o', required=True, help='Output file')
    export_table_parser.add_argument('--format', choices=['csv', 'json'], default='csv')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import data from file')
    import_parser.add_argument('table', help='Target table')
    import_parser.add_argument('--source', '-s', required=True, help='Source file')
    import_parser.add_argument('--format', choices=['csv', 'json'], default='csv')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup table or database')
    backup_parser.add_argument('--table', '-t', help='Table to backup (omit for full DB)')
    backup_parser.add_argument('--output', '-o', required=True, help='Output file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Get connection parameters
    conn_params = get_connection_params(args)
    
    # Initialize skill
    skill = PostgresSkill(conn_params)
    
    if not skill.connect():
        sys.exit(1)
    
    try:
        if args.command == 'query':
            results = skill.execute_query(args.sql)
            if args.format == 'json':
                print(json.dumps(results, indent=2, default=str))
            else:
                print(format_table(results))
        
        elif args.command == 'tables':
            tables = skill.get_tables()
            for table in tables:
                print(table)
        
        elif args.command == 'describe':
            structure = skill.describe_table(args.table)
            print(format_table(structure))
        
        elif args.command == 'indexes':
            indexes = skill.get_indexes(args.table)
            print(format_table(indexes))
        
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
                print("Full database backup requires pg_dump utility")
    
    finally:
        skill.close()



# =============================================================================
# Additional Utility Functions
# =============================================================================

def validate_connection_params(params: Dict[str, Any]) -> bool:
    """Validate connection parameters"""
    required = ['host', 'database', 'user']
    for field in required:
        if not params.get(field):
            print(f"Error: Missing required parameter '{field}'")
            return False
    return True


def print_query_plan(skill: PostgresSkill, query: str):
    """Display query execution plan"""
    try:
        skill.cursor.execute(f"EXPLAIN {query}")
        plan = skill.cursor.fetchall()
        print("Query Plan:")
        for row in plan:
            print(f"  {row[0]}")
    except Exception as e:
        print(f"Could not get query plan: {e}")


def batch_execute(skill: PostgresSkill, queries: List[str]) -> Dict[str, Any]:
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


def get_database_size(skill: PostgresSkill) -> str:
    """Get database size in human readable format"""
    query = """
        SELECT pg_size_pretty(pg_database_size(current_database())) as size
    """
    result = skill.execute_query(query)
    return result[0]['size'] if result else 'Unknown'


def get_table_stats(skill: PostgresSkill, table_name: str) -> Dict[str, Any]:
    """Get table statistics"""
    stats = {}
    
    # Row count
    count_query = f"SELECT COUNT(*) as count FROM {table_name}"
    result = skill.execute_query(count_query)
    stats['row_count'] = result[0]['count'] if result else 0
    
    # Table size
    size_query = """
        SELECT pg_size_pretty(pg_total_relation_size(%s)) as size
    """
    result = skill.execute_query(size_query, (table_name,))
    stats['size'] = result[0]['size'] if result else 'Unknown'
    
    return stats


def search_columns(skill: PostgresSkill, search_term: str) -> List[Dict]:
    """Search for columns across all tables"""
    query = """
        SELECT 
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
            AND column_name ILIKE %s
        ORDER BY table_name, column_name
    """
    return skill.execute_query(query, (f'%{search_term}%',))


def copy_table(skill: PostgresSkill, source_table: str, target_table: str):
    """Copy table structure and data"""
    # Copy structure
    skill.execute_command(f"CREATE TABLE {target_table} (LIKE {source_table} INCLUDING ALL)")
    
    # Copy data
    skill.execute_command(f"INSERT INTO {target_table} SELECT * FROM {source_table}")
    
    print(f"Table {source_table} copied to {target_table}")


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == '__main__':
    main()
