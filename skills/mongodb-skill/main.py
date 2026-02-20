#!/usr/bin/env python3
"""
MongoDB Skill - Document database management tool
Supports document queries, aggregation pipelines, data backup
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from pymongo import MongoClient, ASCENDING, DESCENDING
    from pymongo.errors import PyMongoError, DuplicateKeyError
    from bson import ObjectId, json_util
except ImportError:
    print("Error: pymongo is required. Install with: pip install pymongo")
    sys.exit(1)


class MongoDBSkill:
    """MongoDB database management skill"""
    
    def __init__(self, uri: str = None, database: str = None):
        self.uri = uri or os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        self.default_db = database or os.getenv('MONGODB_DATABASE')
        self.client = None
        self.db = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            if self.default_db:
                self.db = self.client[self.default_db]
            return True
        except PyMongoError as e:
            print(f"Connection error: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
    
    def get_database(self, name: str = None):
        """Get database instance"""
        db_name = name or self.default_db
        if not db_name:
            raise ValueError("Database name required")
        return self.client[db_name]
    
    def list_databases(self) -> List[str]:
        """List all databases"""
        return self.client.list_database_names()
    
    def list_collections(self, database: str = None) -> List[str]:
        """List all collections"""
        db = self.get_database(database)
        return db.list_collection_names()
    
    def find(self, collection: str, filter_dict: Dict = None, projection: Dict = None,
             sort: List = None, skip: int = 0, limit: int = 0, database: str = None) -> List[Dict]:
        """Execute find query"""
        db = self.get_database(database)
        coll = db[collection]
        
        cursor = coll.find(filter_dict or {}, projection)
        
        if sort:
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        return list(cursor)
    
    def find_one(self, collection: str, filter_dict: Dict, database: str = None) -> Optional[Dict]:
        """Find single document"""
        db = self.get_database(database)
        return db[collection].find_one(filter_dict)
    
    def insert_one(self, collection: str, document: Dict, database: str = None) -> str:
        """Insert single document"""
        db = self.get_database(database)
        result = db[collection].insert_one(document)
        return str(result.inserted_id)
    
    def insert_many(self, collection: str, documents: List[Dict], database: str = None) -> List[str]:
        """Insert multiple documents"""
        db = self.get_database(database)
        result = db[collection].insert_many(documents)
        return [str(id) for id in result.inserted_ids]
    
    def update_one(self, collection: str, filter_dict: Dict, update_dict: Dict, 
                   database: str = None) -> int:
        """Update single document"""
        db = self.get_database(database)
        result = db[collection].update_one(filter_dict, update_dict)
        return result.modified_count
    
    def update_many(self, collection: str, filter_dict: Dict, update_dict: Dict,
                    database: str = None) -> int:
        """Update multiple documents"""
        db = self.get_database(database)
        result = db[collection].update_many(filter_dict, update_dict)
        return result.modified_count
    
    def delete_one(self, collection: str, filter_dict: Dict, database: str = None) -> int:
        """Delete single document"""
        db = self.get_database(database)
        result = db[collection].delete_one(filter_dict)
        return result.deleted_count
    
    def delete_many(self, collection: str, filter_dict: Dict, database: str = None) -> int:
        """Delete multiple documents"""
        db = self.get_database(database)
        result = db[collection].delete_many(filter_dict)
        return result.deleted_count
    
    def aggregate(self, collection: str, pipeline: List[Dict], database: str = None) -> List[Dict]:
        """Execute aggregation pipeline"""
        db = self.get_database(database)
        return list(db[collection].aggregate(pipeline))
    
    def count(self, collection: str, filter_dict: Dict = None, database: str = None) -> int:
        """Count documents"""
        db = self.get_database(database)
        return db[collection].count_documents(filter_dict or {})
    
    def get_stats(self, collection: str, database: str = None) -> Dict:
        """Get collection statistics"""
        db = self.get_database(database)
        return db.command('collstats', collection)
    
    def create_index(self, collection: str, field: str, unique: bool = False,
                     database: str = None):
        """Create index"""
        db = self.get_database(database)
        db[collection].create_index(field, unique=unique)
        print(f"Index created on {field}")
    
    def list_indexes(self, collection: str, database: str = None) -> List[Dict]:
        """List collection indexes"""
        db = self.get_database(database)
        return list(db[collection].list_indexes())
    
    def drop_index(self, collection: str, index_name: str, database: str = None):
        """Drop index"""
        db = self.get_database(database)
        db[collection].drop_index(index_name)
        print(f"Index {index_name} dropped")
    
    def export_collection(self, collection: str, output_file: str, 
                          format_type: str = 'json', database: str = None):
        """Export collection to file"""
        documents = self.find(collection, database=database)
        
        if format_type == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(documents, f, indent=2, default=json_util.default)
        
        elif format_type == 'csv':
            if not documents:
                print("No documents to export")
                return
            
            # Flatten documents for CSV
            flat_docs = []
            for doc in documents:
                flat_doc = {}
                for key, value in doc.items():
                    if isinstance(value, dict):
                        flat_doc[key] = json.dumps(value)
                    else:
                        flat_doc[key] = value
                flat_docs.append(flat_doc)
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=flat_docs[0].keys())
                writer.writeheader()
                writer.writerows(flat_docs)
        
        print(f"Exported {len(documents)} documents to {output_file}")
    
    def import_collection(self, collection: str, input_file: str, 
                          database: str = None):
        """Import documents from JSON file"""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            ids = self.insert_many(collection, data, database)
            print(f"Imported {len(ids)} documents")
        else:
            id = self.insert_one(collection, data, database)
            print(f"Imported 1 document with id {id}")
    
    def export_query(self, collection: str, filter_dict: Dict, output_file: str,
                     database: str = None):
        """Export filtered documents"""
        documents = self.find(collection, filter_dict, database=database)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, default=json_util.default)
        print(f"Exported {len(documents)} documents to {output_file}")


def parse_filter(filter_str: str) -> Dict:
    """Parse filter JSON string"""
    if not filter_str:
        return {}
    try:
        return json.loads(filter_str)
    except json.JSONDecodeError as e:
        print(f"Invalid filter JSON: {e}")
        return {}


def parse_sort(sort_str: str) -> List:
    """Parse sort specification"""
    if not sort_str:
        return None
    try:
        sort_dict = json.loads(sort_str)
        result = []
        for field, direction in sort_dict.items():
            result.append((field, ASCENDING if direction == 1 else DESCENDING))
        return result
    except json.JSONDecodeError:
        return None


def format_document(doc: Dict) -> str:
    """Format document for display"""
    return json.dumps(doc, indent=2, default=json_util.default)


def main():
    parser = argparse.ArgumentParser(description='MongoDB Skill - Database management tool')
    parser.add_argument('--uri', help='MongoDB connection URI')
    parser.add_argument('--database', '-d', help='Database name')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Databases command
    subparsers.add_parser('databases', help='List all databases')
    
    # Collections command
    collections_parser = subparsers.add_parser('collections', help='List collections')
    collections_parser.add_argument('--database', '-d', help='Database name')
    
    # Find command
    find_parser = subparsers.add_parser('find', help='Find documents')
    find_parser.add_argument('collection', help='Collection name')
    find_parser.add_argument('--filter', '-f', help='Filter JSON')
    find_parser.add_argument('--fields', help='Projection fields JSON')
    find_parser.add_argument('--sort', help='Sort specification JSON')
    find_parser.add_argument('--skip', type=int, default=0)
    find_parser.add_argument('--limit', type=int, default=0)
    find_parser.add_argument('--database', '-d', help='Database name')
    
    # Aggregate command
    agg_parser = subparsers.add_parser('aggregate', help='Run aggregation pipeline')
    agg_parser.add_argument('collection', help='Collection name')
    agg_parser.add_argument('--pipeline', '-p', required=True, help='Pipeline JSON array')
    agg_parser.add_argument('--database', '-d', help='Database name')
    agg_parser.add_argument('--out', help='Output collection')
    
    # Insert command
    insert_parser = subparsers.add_parser('insert', help='Insert document')
    insert_parser.add_argument('collection', help='Collection name')
    insert_parser.add_argument('--doc', required=True, help='Document JSON')
    insert_parser.add_argument('--database', '-d', help='Database name')
    
    # Insert-many command
    insert_many_parser = subparsers.add_parser('insert-many', help='Insert multiple documents')
    insert_many_parser.add_argument('collection', help='Collection name')
    insert_many_parser.add_argument('--file', required=True, help='JSON file path')
    insert_many_parser.add_argument('--database', '-d', help='Database name')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update document')
    update_parser.add_argument('collection', help='Collection name')
    update_parser.add_argument('--filter', required=True, help='Filter JSON')
    update_parser.add_argument('--update', required=True, help='Update JSON')
    update_parser.add_argument('--database', '-d', help='Database name')
    
    # Update-many command
    update_many_parser = subparsers.add_parser('update-many', help='Update multiple documents')
    update_many_parser.add_argument('collection', help='Collection name')
    update_many_parser.add_argument('--filter', required=True, help='Filter JSON')
    update_many_parser.add_argument('--update', required=True, help='Update JSON')
    update_many_parser.add_argument('--database', '-d', help='Database name')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete document')
    delete_parser.add_argument('collection', help='Collection name')
    delete_parser.add_argument('--filter', required=True, help='Filter JSON')
    delete_parser.add_argument('--database', '-d', help='Database name')
    
    # Delete-many command
    delete_many_parser = subparsers.add_parser('delete-many', help='Delete multiple documents')
    delete_many_parser.add_argument('collection', help='Collection name')
    delete_many_parser.add_argument('--filter', required=True, help='Filter JSON')
    delete_many_parser.add_argument('--database', '-d', help='Database name')
    
    # Count command
    count_parser = subparsers.add_parser('count', help='Count documents')
    count_parser.add_argument('collection', help='Collection name')
    count_parser.add_argument('--filter', help='Filter JSON')
    count_parser.add_argument('--database', '-d', help='Database name')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Collection statistics')
    stats_parser.add_argument('collection', help='Collection name')
    stats_parser.add_argument('--database', '-d', help='Database name')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export collection')
    export_parser.add_argument('collection', help='Collection name')
    export_parser.add_argument('--output', '-o', required=True, help='Output file')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json')
    export_parser.add_argument('--database', '-d', help='Database name')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import documents')
    import_parser.add_argument('collection', help='Collection name')
    import_parser.add_argument('--file', required=True, help='JSON file path')
    import_parser.add_argument('--database', '-d', help='Database name')
    
    # Create-index command
    index_parser = subparsers.add_parser('create-index', help='Create index')
    index_parser.add_argument('collection', help='Collection name')
    index_parser.add_argument('--field', required=True, help='Field name')
    index_parser.add_argument('--unique', action='store_true', help='Unique index')
    index_parser.add_argument('--database', '-d', help='Database name')
    
    # Indexes command
    indexes_parser = subparsers.add_parser('indexes', help='List indexes')
    indexes_parser.add_argument('collection', help='Collection name')
    indexes_parser.add_argument('--database', '-d', help='Database name')
    
    # Drop-index command
    drop_index_parser = subparsers.add_parser('drop-index', help='Drop index')
    drop_index_parser.add_argument('collection', help='Collection name')
    drop_index_parser.add_argument('--name', required=True, help='Index name')
    drop_index_parser.add_argument('--database', '-d', help='Database name')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize skill
    skill = MongoDBSkill(uri=args.uri, database=args.database)
    
    if not skill.connect():
        sys.exit(1)
    
    try:
        if args.command == 'databases':
            for db in skill.list_databases():
                print(db)
        
        elif args.command == 'collections':
            db_name = args.database or skill.default_db
            for coll in skill.list_collections(db_name):
                print(coll)
        
        elif args.command == 'find':
            filter_dict = parse_filter(getattr(args, 'filter', None))
            projection = parse_filter(getattr(args, 'fields', None))
            sort = parse_sort(getattr(args, 'sort', None))
            
            results = skill.find(
                args.collection, 
                filter_dict, 
                projection,
                sort,
                args.skip,
                args.limit,
                args.database
            )
            for doc in results:
                print(format_document(doc))
                print('---')
        
        elif args.command == 'aggregate':
            pipeline = json.loads(args.pipeline)
            results = skill.aggregate(args.collection, pipeline, args.database)
            if args.out:
                # Save to collection
                db = skill.get_database(args.database)
                db[args.out].insert_many(results)
                print(f"Results saved to collection {args.out}")
            else:
                for doc in results:
                    print(format_document(doc))
        
        elif args.command == 'insert':
            doc = json.loads(args.doc)
            id = skill.insert_one(args.collection, doc, args.database)
            print(f"Inserted document with id: {id}")
        
        elif args.command == 'insert-many':
            with open(args.file, 'r') as f:
                docs = json.load(f)
            ids = skill.insert_many(args.collection, docs, args.database)
            print(f"Inserted {len(ids)} documents")
        
        elif args.command == 'update':
            filter_dict = json.loads(args.filter)
            update_dict = json.loads(args.update)
            count = skill.update_one(args.collection, filter_dict, update_dict, args.database)
            print(f"Updated {count} document(s)")
        
        elif args.command == 'update-many':
            filter_dict = json.loads(args.filter)
            update_dict = json.loads(args.update)
            count = skill.update_many(args.collection, filter_dict, update_dict, args.database)
            print(f"Updated {count} document(s)")
        
        elif args.command == 'delete':
            filter_dict = json.loads(args.filter)
            count = skill.delete_one(args.collection, filter_dict, args.database)
            print(f"Deleted {count} document(s)")
        
        elif args.command == 'delete-many':
            filter_dict = json.loads(args.filter)
            count = skill.delete_many(args.collection, filter_dict, args.database)
            print(f"Deleted {count} document(s)")
        
        elif args.command == 'count':
            filter_dict = parse_filter(getattr(args, 'filter', None))
            count = skill.count(args.collection, filter_dict, args.database)
            print(count)
        
        elif args.command == 'stats':
            stats = skill.get_stats(args.collection, args.database)
            print(json.dumps(stats, indent=2, default=json_util.default))
        
        elif args.command == 'export':
            skill.export_collection(args.collection, args.output, args.format, args.database)
        
        elif args.command == 'import':
            skill.import_collection(args.collection, args.file, args.database)
        
        elif args.command == 'create-index':
            skill.create_index(args.collection, args.field, args.unique, args.database)
        
        elif args.command == 'indexes':
            indexes = skill.list_indexes(args.collection, args.database)
            for idx in indexes:
                print(f"{idx['name']}: {idx['key']}")
        
        elif args.command == 'drop-index':
            skill.drop_index(args.collection, args.name, args.database)
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        skill.close()



# =============================================================================
# Additional Utility Functions
# =============================================================================

def validate_connection_uri(uri: str) -> bool:
    """Validate MongoDB connection URI"""
    if not uri:
        print("Error: MongoDB URI is required")
        return False
    if not uri.startswith('mongodb://') and not uri.startswith('mongodb+srv://'):
        print("Error: Invalid MongoDB URI format")
        return False
    return True


def format_aggregation_pipeline(pipeline: List[Dict]) -> str:
    """Pretty print aggregation pipeline"""
    lines = ['Aggregation Pipeline:']
    for i, stage in enumerate(pipeline):
        stage_name = list(stage.keys())[0]
        lines.append(f"  Stage {i+1}: {stage_name}")
        lines.append(f"    {json.dumps(stage[stage_name], indent=4)}")
    return '\n'.join(lines)


def batch_insert(skill: MongoDBSkill, collection: str, documents: List[Dict], 
                 batch_size: int = 1000, database: str = None) -> Dict[str, Any]:
    """Insert documents in batches"""
    results = {'inserted': 0, 'batches': 0, 'errors': []}
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        try:
            ids = skill.insert_many(collection, batch, database)
            results['inserted'] += len(ids)
            results['batches'] += 1
        except Exception as e:
            results['errors'].append({'batch': i // batch_size, 'error': str(e)})
    
    return results


def get_collection_stats_detailed(skill: MongoDBSkill, collection: str, 
                                   database: str = None) -> Dict[str, Any]:
    """Get detailed collection statistics"""
    stats = skill.get_stats(collection, database)
    
    # Add additional computed metrics
    if 'size' in stats and 'count' in stats:
        doc_count = stats['count']
        total_size = stats['size']
        if doc_count > 0:
            stats['avg_doc_size'] = total_size / doc_count
    
    return stats


def search_fields(skill: MongoDBSkill, collection: str, field_pattern: str,
                  database: str = None) -> List[str]:
    """Search for fields matching pattern in collection documents"""
    db = skill.get_database(database)
    coll = db[collection]
    
    # Sample documents to find field names
    sample = coll.find_one()
    if not sample:
        return []
    
    matching_fields = []
    pattern_lower = field_pattern.lower()
    
    def search_nested(doc, prefix=''):
        for key, value in doc.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if pattern_lower in key.lower():
                matching_fields.append(full_key)
            if isinstance(value, dict):
                search_nested(value, full_key)
    
    search_nested(sample)
    return matching_fields


def validate_documents(documents: List[Dict]) -> List[Dict]:
    """Validate documents before insertion"""
    errors = []
    
    for i, doc in enumerate(documents):
        # Check for _id conflicts would require DB access
        # Here we just validate structure
        if not isinstance(doc, dict):
            errors.append({'index': i, 'error': 'Document is not a dictionary'})
        elif len(doc) == 0:
            errors.append({'index': i, 'error': 'Document is empty'})
    
    return errors


def compare_collections(skill: MongoDBSkill, coll1: str, coll2: str,
                        database: str = None) -> Dict[str, Any]:
    """Compare two collections"""
    db = skill.get_database(database)
    
    stats1 = db.command('collstats', coll1)
    stats2 = db.command('collstats', coll2)
    
    comparison = {
        'collection1': {
            'name': coll1,
            'count': stats1.get('count', 0),
            'size': stats1.get('size', 0)
        },
        'collection2': {
            'name': coll2,
            'count': stats2.get('count', 0),
            'size': stats2.get('size', 0)
        },
        'differences': {
            'count_diff': stats1.get('count', 0) - stats2.get('count', 0),
            'size_diff': stats1.get('size', 0) - stats2.get('size', 0)
        }
    }
    
    return comparison


def create_text_index(skill: MongoDBSkill, collection: str, fields: List[str],
                      database: str = None):
    """Create text index on multiple fields"""
    db = skill.get_database(database)
    coll = db[collection]
    
    index_spec = [(field, 'text') for field in fields]
    coll.create_index(index_spec, name='text_search_idx')
    print(f"Text index created on {', '.join(fields)}")


def text_search(skill: MongoDBSkill, collection: str, search_text: str,
                database: str = None) -> List[Dict]:
    """Perform text search"""
    db = skill.get_database(database)
    coll = db[collection]
    
    return list(coll.find({'$text': {'$search': search_text}}))


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == '__main__':
    main()
