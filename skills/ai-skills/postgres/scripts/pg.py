#!/usr/bin/env python3
"""PostgreSQL Database Assistant"""

import argparse
import re
from pathlib import Path

class PostgresAssistant:
    def __init__(self):
        self.best_practices = {
            "indexes": [
                "CREATE INDEX CONCURRENTLY for production",
                "Use partial indexes for filtered queries",
                "Consider covering indexes for frequent queries"
            ],
            "queries": [
                "Avoid SELECT * in production",
                "Use EXPLAIN ANALYZE for query planning",
                "Prefer JOINs over subqueries when possible"
            ],
            "schema": [
                "Use appropriate data types (TIMESTAMPTZ, UUID, JSONB)",
                "Add constraints at database level",
                "Use schemas for multi-tenant applications"
            ]
        }
    
    def optimize_query(self, query):
        """Analyze and optimize SQL query"""
        print(f"\n[SEARCH] Query Analysis")
        print("=" * 60)
        print(f"Original: {query[:80]}...")
        
        issues = []
        suggestions = []
        optimized = query
        
        # Check for SELECT *
        if re.search(r'SELECT\s+\*', query, re.IGNORECASE):
            issues.append("SELECT * fetches unnecessary columns")
            suggestions.append("Specify only needed columns")
        
        # Check for LIKE with leading wildcard
        if re.search(r"LIKE\s+'%", query, re.IGNORECASE):
            issues.append("Leading wildcard in LIKE prevents index usage")
            suggestions.append("Consider full-text search (tsvector)")
        
        # Check for N+1 pattern
        if re.search(r'for.*in.*select', query, re.IGNORECASE):
            issues.append("Potential N+1 query pattern detected")
            suggestions.append("Use JOIN to fetch related data")
        
        # Check for missing LIMIT
        if not re.search(r'LIMIT', query, re.IGNORECASE) and not re.search(r'WHERE', query, re.IGNORECASE):
            issues.append("No LIMIT clause - may return excessive rows")
            suggestions.append("Add LIMIT for pagination")
        
        print("\n[WARNING] Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
        
        print("\n[TIP] Suggestions:")
        for suggestion in suggestions:
            print(f"  -> {suggestion}")
        
        print("\n[CLIPBOARD] Best Practices:")
        for practice in self.best_practices["queries"]:
            print(f"  [OK] {practice}")
        
        return issues, suggestions
    
    def generate_schema(self, entities):
        """Generate database schema for entities"""
        print(f"\n[LAYOUT] Schema Design for: {', '.join(entities)}")
        print("=" * 60)
        
        schema = []
        
        for entity in entities:
            table_sql = f"""
-- {entity.title()} table
CREATE TABLE {entity}s (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Add entity-specific fields here
    name VARCHAR(255) NOT NULL,
    metadata JSONB DEFAULT '{{}}',
    
    -- Constraints
    CONSTRAINT {entity}s_name_check CHECK (LENGTH(name) > 0)
);

-- Indexes
CREATE INDEX idx_{entity}s_created_at ON {entity}s(created_at);
CREATE INDEX idx_{entity}s_name ON {entity}s(name);

-- Trigger for updated_at
CREATE TRIGGER update_{entity}s_updated_at
    BEFORE UPDATE ON {entity}s
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""
            schema.append(table_sql)
            print(table_sql)
        
        # Relations
        if len(entities) > 1:
            print("\n-- Relationships")
            for i, entity in enumerate(entities):
                if i < len(entities) - 1:
                    next_entity = entities[i + 1]
                    print(f"-- {entity} has many {next_entity}s")
                    print(f"ALTER TABLE {next_entity}s ADD COLUMN {entity}_id UUID REFERENCES {entity}s(id);")
                    print(f"CREATE INDEX idx_{next_entity}s_{entity}_id ON {next_entity}s({entity}_id);\n")
        
        print("\n[OK] Schema generated with:")
        print("  - UUID primary keys")
        print("  - Automatic timestamp tracking")
        print("  - JSONB for flexible metadata")
        print("  - Appropriate indexes")
        
        return schema
    
    def generate_migration(self, from_version, to_version):
        """Generate migration script"""
        print(f"\n[MIGRATE] Migration: v{from_version} -> v{to_version}")
        print("=" * 60)
        
        migration = f"""-- Migration {from_version} -> {to_version}
-- Generated: {__import__('datetime').datetime.now().isoformat()}

BEGIN;

-- Add your migration steps here
-- Example:
-- ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
-- CREATE INDEX idx_users_email_verified ON users(email_verified) WHERE NOT email_verified;

COMMIT;

-- Rollback (for emergencies)
-- BEGIN;
-- ALTER TABLE users DROP COLUMN email_verified;
-- COMMIT;
"""
        print(migration)
        return migration
    
    def analyze_indexes(self, table_name):
        """Analyze index recommendations"""
        print(f"\n[CHART] Index Analysis for: {table_name}")
        print("=" * 60)
        
        print(f"""
-- Current index usage query
SELECT 
    indexname,
    indexdef,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_indexes
WHERE tablename = '{table_name}';

-- Missing index detection (run in production)
SELECT 
    schemaname,
    tablename,
    attname as column,
    n_tup_read,
    n_tup_fetch
FROM pg_stats
WHERE tablename = '{table_name}'
AND schemaname = 'public';

-- Recommended indexes for {table_name}:
""")
        
        recommendations = [
            f"CREATE INDEX idx_{table_name}_created_at ON {table_name}(created_at);",
            f"CREATE INDEX idx_{table_name}_updated_at ON {table_name}(updated_at);",
        ]
        
        for rec in recommendations:
            print(f"-- {rec}")
        
        print("\n[WARNING] Create indexes CONCURRENTLY in production:")
        print(f"-- CREATE INDEX CONCURRENTLY idx_{table_name}_new ON {table_name}(column);")

def main():
    parser = argparse.ArgumentParser(description='PostgreSQL Assistant')
    parser.add_argument('command', choices=['optimize', 'schema', 'migrate', 'index'])
    parser.add_argument('--query', '-q', help='SQL query to optimize')
    parser.add_argument('--entities', '-e', help='Comma-separated entity list')
    parser.add_argument('--from', dest='from_ver', help='From version')
    parser.add_argument('--to', dest='to_ver', help='To version')
    parser.add_argument('--table', '-t', help='Table name')
    
    args = parser.parse_args()
    
    pg = PostgresAssistant()
    
    if args.command == 'optimize':
        if not args.query:
            print("[X] Please provide --query")
            return
        pg.optimize_query(args.query)
    
    elif args.command == 'schema':
        entities = args.entities.split(',') if args.entities else ['user', 'post']
        pg.generate_schema(entities)
    
    elif args.command == 'migrate':
        pg.generate_migration(args.from_ver or '1', args.to_ver or '2')
    
    elif args.command == 'index':
        pg.analyze_indexes(args.table or 'users')

if __name__ == '__main__':
    main()
