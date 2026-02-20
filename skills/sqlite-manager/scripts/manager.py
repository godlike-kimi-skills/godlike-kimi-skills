#!/usr/bin/env python3
"""SQLite Manager - Database management tool"""

import argparse
import csv
import json
import sqlite3
from pathlib import Path
from typing import Dict, List


def open_db(db_path: str) -> Dict:
    """Open and inspect database"""
    path = Path(db_path)
    if not path.exists():
        return {'error': f'Database not found: {db_path}'}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get schema
        schema = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [{'name': row[1], 'type': row[2]} for row in cursor.fetchall()]
            schema[table] = columns
        
        conn.close()
        
        return {
            'database': db_path,
            'tables': tables,
            'schema': schema,
            'size_bytes': path.stat().st_size
        }
    except sqlite3.Error as e:
        return {'error': str(e)}


def execute_query(db_path: str, query: str) -> Dict:
    """Execute SQL query"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            return {
                'query': query,
                'row_count': len(results),
                'results': results[:100]  # Limit results
            }
        else:
            conn.commit()
            return {
                'query': query,
                'rows_affected': cursor.rowcount
            }
    except sqlite3.Error as e:
        return {'error': str(e)}
    finally:
        conn.close()


def export_table(db_path: str, table: str, format_type: str, output: str):
    """Export table data"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        if format_type == 'csv':
            with open(output, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(rows)
        elif format_type == 'json':
            data = [dict(zip(columns, row)) for row in rows]
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        
        print(f"Exported {len(rows)} rows to {output}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description='SQLite Manager')
    subparsers = parser.add_subparsers(dest='command')
    
    open_parser = subparsers.add_parser('open')
    open_parser.add_argument('db_path')
    
    query_parser = subparsers.add_parser('query')
    query_parser.add_argument('sql')
    query_parser.add_argument('--db', required=True)
    
    export_parser = subparsers.add_parser('export')
    export_parser.add_argument('--table', required=True)
    export_parser.add_argument('--format', choices=['csv', 'json'], required=True)
    export_parser.add_argument('--output', required=True)
    export_parser.add_argument('--db', required=True)
    
    args = parser.parse_args()
    
    if args.command == 'open':
        result = open_db(args.db_path)
        print(json.dumps(result, indent=2))
    elif args.command == 'query':
        result = execute_query(args.db, args.sql)
        print(json.dumps(result, indent=2))
    elif args.command == 'export':
        export_table(args.db, args.table, args.format, args.output)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
