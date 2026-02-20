#!/usr/bin/env python3
"""
SQLite Skill - Local database management tool
Supports database creation, SQL queries, data backup and maintenance
"""

import argparse
import csv
import json
import os
import shutil
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional


class SQLiteSkill:
    """SQLite database management skill"""
    
    def __init__(self, database_path: str = None, memory: bool = False):
        self.database_path = database_path
        self.memory = memory
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            import sqlite3
            
            if self.memory:
                self.conn = sqlite3.connect(":memory:")
            else:
                if not self.database_path:
                    raise ValueError("Database path required for file-based connection")
                self.conn = sqlite3.connect(self.database_path)
            
            # Enable dictionary access
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            
            # Enable foreign keys
            self.cursor.execute("PRAGMA foreign_keys = ON")
            
            return True
        except Exception as e:
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
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Query error: {e}")
            return []
    
    def execute_command(self, command: str, params: tuple = None) -> int:
        """Execute non-SELECT command, return affected rows"""
        try:
            if params:
                self.cursor.execute(command, params)
            else:
                self.cursor.execute(command)
            
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            print(f"Command error: {e}")
            self.conn.rollback()
            return 0
    
    def get_tables(self) -> List[str]:
        """Get list of all tables"""
        query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        result = self.execute_query(query)
        return [row['name'] for row in result]
    
    def get_schema(self, table_name: str) -> List[Dict]:
        """Get table schema"""
        query = f"PRAGMA table_info({table_name})"
        return self.execute_query(query)
    
    def get_indexes(self, table_name: str) -> List[Dict]:
        """Get table indexes"""
        query = f"PRAGMA index_list({table_name})"
        return self.execute_query(query)
    
    def get_ddl(self, table_name: str) -> str:
        """Get CREATE TABLE statement"""
        query = "SELECT sql FROM sqlite_master WHERE type='table' AND name=?"
        result = self.execute_query(query, (table_name,))
        return result[0]['sql'] if result else ''
    
    def get_database_info(self) -> Dict:
        """Get database information"""
        info = {}
        
        # Page size
        result = self.execute_query("PRAGMA page_size")
        info['page_size'] = result[0]['page_size'] if result else 0
        
        # Page count
        result = self.execute_query("PRAGMA page_count")
        info['page_count'] = result[0]['page_count'] if result else 0
        
        # File size
        info['size_bytes'] = info['page_size'] * info['page_count']
        
        # Table count
        tables = self.get_tables()
        info['table_count'] = len(tables)
        info['tables'] = tables
        
        # SQLite version
        result = self.execute_query("SELECT sqlite_version() as version")
        info['sqlite_version'] = result[0]['version'] if result else 'unknown'
        
        return info
    
    def vacuum(self):
        """Optimize database (VACUUM)"""
        try:
            self.cursor.execute("VACUUM")
            print("Database vacuumed successfully")
        except Exception as e:
            print(f"Vacuum error: {e}")
    
    def integrity_check(self) -> List[Dict]:
        """Check database integrity"""
        return self.execute_query("PRAGMA integrity_check")
    
    def export_to_csv(self, table_or_query: str, output_file: str, is_query: bool = False):
        """Export to CSV"""
        if is_query:
            results = self.execute_query(table_or_query)
        else:
            results = self.execute_query(f"SELECT * FROM {table_or_query}")
        
        if not results:
            print("No data to export")
            return
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"Exported {len(results)} rows to {output_file}")
    
    def export_to_json(self, table_or_query: str, output_file: str, is_query: bool = False):
        """Export to JSON"""
        if is_query:
            results = self.execute_query(table_or_query)
        else:
            results = self.execute_query(f"SELECT * FROM {table_or_query}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Exported {len(results)} rows to {output_file}")
    
    def export_to_sql(self, table_name: str, output_file: str):
        """Export to SQL INSERT statements"""
        ddl = self.get_ddl(table_name)
        data = self.execute_query(f"SELECT * FROM {table_name}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"-- Export of table {table_name}\n")
            f.write(f"-- Generated: {datetime.now()}\n\n")
            f.write(f"{ddl};\n\n")
            
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
        
        print(f"Exported to {output_file}")
    
    def import_from_csv(self, csv_file: str, table_name: str = None):
        """Import from CSV file"""
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if not rows:
            print("No data to import")
            return
        
        # Auto-create table if not exists
        if table_name:
            columns = list(rows[0].keys())
            col_defs = ', '.join([f'"{col}" TEXT' for col in columns])
            
            create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({col_defs})'
            self.execute_command(create_sql)
            
            # Insert data
            placeholders = ', '.join(['?' for _ in columns])
            insert_sql = f'INSERT INTO "{table_name}" ({', '.join(columns)}) VALUES ({placeholders})'
            
            for row in rows:
                self.cursor.execute(insert_sql, tuple(row.values()))
            self.conn.commit()
            
            print(f"Imported {len(rows)} rows into {table_name}")
    
    def backup(self, output_path: str):
        """Backup database file"""
        if self.memory:
            print("Cannot backup in-memory database")
            return
        
        try:
            shutil.copy2(self.database_path, output_path)
            print(f"Backup saved to {output_path}")
        except Exception as e:
            print(f"Backup error: {e}")
    
    def execute_pragma(self, pragma: str):
        """Execute PRAGMA command"""
        query = f"PRAGMA {pragma}"
        return self.execute_query(query)


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
    parser = argparse.ArgumentParser(description='SQLite Skill - Database management tool')
    parser.add_argument('--database', '-d', help='Database file path')
    parser.add_argument('--memory', action='store_true', help='Use in-memory database')
    parser.add_argument('--format', choices=['json', 'table'], default='table')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Execute SQL query')
    query_parser.add_argument('sql', help='SQL query')
    
    # Tables command
    subparsers.add_parser('tables', help='List all tables')
    
    # Schema command
    schema_parser = subparsers.add_parser('schema', help='Show table schema')
    schema_parser.add_argument('table', help='Table name')
    
    # Indexes command
    indexes_parser = subparsers.add_parser('indexes', help='Show table indexes')
    indexes_parser.add_argument('table', help='Table name')
    
    # DDL command
    ddl_parser = subparsers.add_parser('ddl', help='Show CREATE TABLE statement')
    ddl_parser.add_argument('table', help='Table name')
    
    # Info command
    subparsers.add_parser('info', help='Show database information')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export table/query')
    export_parser.add_argument('source', help='Table name or SQL query')
    export_parser.add_argument('--output', '-o', required=True, help='Output file')
    export_parser.add_argument('--format', choices=['csv', 'json', 'sql'], default='csv')
    export_parser.add_argument('--query', action='store_true', help='Source is SQL query')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import from CSV')
    import_parser.add_argument('file', help='CSV file path')
    import_parser.add_argument('--table', '-t', help='Target table name')
    
    # Vacuum command
    subparsers.add_parser('vacuum', help='Optimize database')
    
    # Check command
    subparsers.add_parser('check', help='Check database integrity')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup database')
    backup_parser.add_argument('output', help='Output file path')
    
    # Pragma command
    pragma_parser = subparsers.add_parser('pragma', help='Execute PRAGMA')
    pragma_parser.add_argument('command', help='PRAGMA command')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize skill
    skill = SQLiteSkill(
        database_path=args.database,
        memory=args.memory
    )
    
    if not skill.connect():
        sys.exit(1)
    
    try:
        if args.command == 'query':
            results = skill.execute_query(args.sql)
            if args.format == 'json':
                print(json.dumps(results, indent=2))
            else:
                print(format_table(results))
        
        elif args.command == 'tables':
            tables = skill.get_tables()
            for table in tables:
                print(table)
        
        elif args.command == 'schema':
            schema = skill.get_schema(args.table)
            print(format_table(schema))
        
        elif args.command == 'indexes':
            indexes = skill.get_indexes(args.table)
            print(format_table(indexes))
        
        elif args.command == 'ddl':
            ddl = skill.get_ddl(args.table)
            print(ddl)
        
        elif args.command == 'info':
            info = skill.get_database_info()
            print(json.dumps(info, indent=2))
        
        elif args.command == 'export':
            if args.format == 'csv':
                skill.export_to_csv(args.source, args.output, args.query)
            elif args.format == 'json':
                skill.export_to_json(args.source, args.output, args.query)
            else:  # sql
                if args.query:
                    print("SQL export only supports table names, not queries")
                else:
                    skill.export_to_sql(args.source, args.output)
        
        elif args.command == 'import':
            skill.import_from_csv(args.file, args.table)
        
        elif args.command == 'vacuum':
            skill.vacuum()
        
        elif args.command == 'check':
            result = skill.integrity_check()
            print(format_table(result))
        
        elif args.command == 'backup':
            skill.backup(args.output)
        
        elif args.command == 'pragma':
            result = skill.execute_pragma(args.command)
            print(format_table(result))
    
    finally:
        skill.close()



# =============================================================================
# Additional Utility Functions
# =============================================================================

def validate_database_path(path: str) -> bool:
    """Validate database file path"""
    if not path:
        print("Error: Database path is required")
        return False
    if not path.endswith('.db') and not path.endswith('.sqlite'):
        print("Warning: Database file should have .db or .sqlite extension")
    return True


def print_query_plan(skill: SQLiteSkill, query: str):
    """Display query execution plan"""
    try:
        result = skill.execute_query(f"EXPLAIN QUERY PLAN {query}")
        print("Query Plan:")
        for row in result:
            print(f"  {row.get('detail', '')}")
    except Exception as e:
        print(f"Could not get query plan: {e}")


def batch_execute(skill: SQLiteSkill, queries: List[str]) -> Dict[str, Any]:
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


def get_database_size(skill: SQLiteSkill) -> str:
    """Get database file size"""
    if skill.memory:
        return "In-memory database (no file size)"
    
    if skill.database_path and os.path.exists(skill.database_path):
        size_bytes = os.path.getsize(skill.database_path)
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.2f} MB"
    return 'Unknown'


def get_table_stats(skill: SQLiteSkill, table_name: str) -> Dict[str, Any]:
    """Get table statistics"""
    stats = {}
    
    # Row count
    result = skill.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
    stats['row_count'] = result[0]['count'] if result else 0
    
    # Page count
    result = skill.execute_query("PRAGMA page_count")
    stats['pages'] = result[0]['page_count'] if result else 0
    
    return stats


def search_columns(skill: SQLiteSkill, search_term: str) -> List[Dict]:
    """Search for columns across all tables"""
    tables = skill.get_tables()
    matches = []
    
    for table in tables:
        schema = skill.get_schema(table)
        for col in schema:
            if search_term.lower() in col['name'].lower():
                matches.append({
                    'table': table,
                    'column': col['name'],
                    'type': col['type']
                })
    
    return matches


def copy_table(skill: SQLiteSkill, source_table: str, target_table: str):
    """Copy table structure and data"""
    ddl = skill.get_ddl(source_table)
    new_ddl = ddl.replace(source_table, target_table, 1)
    
    skill.execute_command(new_ddl)
    skill.execute_command(f"INSERT INTO {target_table} SELECT * FROM {source_table}")
    
    # Copy indexes
    indexes = skill.get_indexes(source_table)
    for idx in indexes:
        idx_name = idx['name']
        new_idx_name = idx_name.replace(source_table, target_table)
        idx_sql = skill.execute_query(
            f"SELECT sql FROM sqlite_master WHERE type='index' AND name=?",
            (idx_name,)
        )
        if idx_sql and idx_sql[0]['sql']:
            new_idx_sql = idx_sql[0]['sql'].replace(source_table, target_table)
            new_idx_sql = new_idx_sql.replace(idx_name, new_idx_name)
            skill.execute_command(new_idx_sql)
    
    print(f"Table {source_table} copied to {target_table}")


def merge_databases(source_db: str, target_db: str, tables: List[str] = None):
    """Merge tables from source database into target"""
    source_skill = SQLiteSkill(database_path=source_db)
    target_skill = SQLiteSkill(database_path=target_db)
    
    if not source_skill.connect() or not target_skill.connect():
        print("Failed to connect to databases")
        return
    
    try:
        tables_to_merge = tables or source_skill.get_tables()
        
        for table in tables_to_merge:
            # Check if table exists in target
            if table in target_skill.get_tables():
                print(f"Table {table} already exists in target, skipping")
                continue
            
            # Copy table
            ddl = source_skill.get_ddl(table)
            target_skill.execute_command(ddl)
            
            # Copy data
            data = source_skill.execute_query(f"SELECT * FROM {table}")
            if data:
                columns = ', '.join(data[0].keys())
                placeholders = ', '.join(['?' for _ in data[0].keys()])
                insert_sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                
                for row in data:
                    target_skill.cursor.execute(insert_sql, tuple(row.values()))
                target_skill.conn.commit()
            
            print(f"Copied table {table} ({len(data)} rows)")
    
    finally:
        source_skill.close()
        target_skill.close()


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == '__main__':
    main()
