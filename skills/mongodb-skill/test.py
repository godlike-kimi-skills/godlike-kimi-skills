#!/usr/bin/env python3
"""
MongoDB Skill - Test Suite
Tests all major functionality of the mongodb-skill
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import MongoDBSkill, parse_filter, parse_sort


class TestMongoDBSkill(unittest.TestCase):
    """Test cases for MongoDB Skill"""
    
    @patch('main.MongoClient')
    def setUp(self, mock_client_class):
        """Set up test fixtures"""
        self.mock_client = MagicMock()
        mock_client_class.return_value = self.mock_client
        
        self.mock_db = MagicMock()
        self.mock_client.__getitem__.return_value = self.mock_db
        
        self.skill = MongoDBSkill(uri='mongodb://localhost:27017', database='testdb')
        self.skill.client = self.mock_client
        self.skill.db = self.mock_db
    
    def tearDown(self):
        """Clean up after tests"""
        if self.skill:
            self.skill.close()
    
    def test_connection_params(self):
        """Test connection parameters"""
        self.assertEqual(self.skill.uri, 'mongodb://localhost:27017')
        self.assertEqual(self.skill.default_db, 'testdb')
    
    @patch('main.MongoClient')
    def test_connect_success(self, mock_client_class):
        """Test successful connection"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        skill = MongoDBSkill(uri='mongodb://localhost:27017')
        result = skill.connect()
        self.assertTrue(result)
        mock_client.admin.command.assert_called_once_with('ping')
    
    def test_list_databases(self):
        """Test listing databases"""
        self.mock_client.list_database_names.return_value = ['admin', 'testdb', 'local']
        result = self.skill.list_databases()
        self.assertEqual(len(result), 3)
        self.assertIn('testdb', result)
    
    def test_list_collections(self):
        """Test listing collections"""
        self.mock_db.list_collection_names.return_value = ['users', 'orders']
        result = self.skill.list_collections()
        self.assertEqual(len(result), 2)
        self.assertIn('users', result)
    
    def test_find(self):
        """Test find operation"""
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection
        
        mock_cursor = MagicMock()
        mock_collection.find.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.__iter__.return_value = iter([
            {'_id': '1', 'name': 'Alice'},
            {'_id': '2', 'name': 'Bob'}
        ])
        
        result = self.skill.find('users', {'active': True})
        self.assertEqual(len(result), 2)
        mock_collection.find.assert_called_once()
    
    def test_find_one(self):
        """Test find_one operation"""
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = {'_id': '1', 'name': 'Alice'}
        
        result = self.skill.find_one('users', {'_id': '1'})
        self.assertEqual(result['name'], 'Alice')
    
    def test_insert_one(self):
        """Test insert_one operation"""
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection
        mock_collection.insert_one.return_value.inserted_id = 'abc123'
        
        result = self.skill.insert_one('users', {'name': 'Charlie'})
        self.assertEqual(result, 'abc123')
    
    def test_insert_many(self):
        """Test insert_many operation"""
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection
        mock_collection.insert_many.return_value.inserted_ids = ['id1', 'id2']
        
        docs = [{'name': 'Alice'}, {'name': 'Bob'}]
        result = self.skill.insert_many('users', docs)
        self.assertEqual(len(result), 2)
    
    def test_update_one(self):
        """Test update_one operation"""
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection
        mock_collection.update_one.return_value.modified_count = 1
        
        result = self.skill.update_one('users', {'_id': '1'}, {'$set': {'name': 'New'}})
        self.assertEqual(result, 1)
    
    def test_update_many(self):
        """Test update_many operation"""
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection
        mock_collection.update_many.return_value.modified_count = 5
        
        result = self.skill.update_many('users', {'status': 'pending'}, {'$set': {'status': 'active'}})
        self.assertEqual(result, 5)
    
    def test_delete_one(self):
        """Test delete_one operation"""
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection
        mock_collection.delete_one.return_value.deleted_count = 1
        
        result = self.skill.delete_one('users', {'_id': '1'})
        self.assertEqual(result, 1)
    
    def test_delete_many(self):
        """Test delete_many operation"""
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection
        mock_collection.delete_many.return_value.deleted_count = 3
        
        result = self.skill.delete_many('users', {'inactive': True})
        self.assertEqual(result, 3)
    
    def test_aggregate(self):
        """Test aggregation pipeline"""
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection
        mock_collection.aggregate.return_value = [
            {'_id': 'A', 'count': 10},
            {'_id': 'B', 'count': 5}
        ]
        
        pipeline = [{'$group': {'_id': '$category', 'count': {'$sum': 1}}}]
        result = self.skill.aggregate('orders', pipeline)
        self.assertEqual(len(result), 2)
    
    def test_count(self):
        """Test count operation"""
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection
        mock_collection.count_documents.return_value = 100
        
        result = self.skill.count('users')
        self.assertEqual(result, 100)
    
    def test_create_index(self):
        """Test index creation"""
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection
        
        self.skill.create_index('users', 'email', unique=True)
        mock_collection.create_index.assert_called_once_with('email', unique=True)
    
    def test_list_indexes(self):
        """Test listing indexes"""
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection
        mock_collection.list_indexes.return_value = [
            {'name': '_id_', 'key': {'_id': 1}},
            {'name': 'email_1', 'key': {'email': 1}}
        ]
        
        result = self.skill.list_indexes('users')
        self.assertEqual(len(result), 2)
    
    def test_drop_index(self):
        """Test dropping index"""
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection
        
        self.skill.drop_index('users', 'email_1')
        mock_collection.drop_index.assert_called_once_with('email_1')


class TestParseFunctions(unittest.TestCase):
    """Test helper parsing functions"""
    
    def test_parse_filter_valid(self):
        """Test parsing valid filter JSON"""
        filter_str = '{"status": "active", "age": {"$gte": 18}}'
        result = parse_filter(filter_str)
        self.assertEqual(result['status'], 'active')
        self.assertIn('$gte', result['age'])
    
    def test_parse_filter_empty(self):
        """Test parsing empty filter"""
        result = parse_filter('')
        self.assertEqual(result, {})
    
    def test_parse_filter_invalid(self):
        """Test parsing invalid JSON"""
        result = parse_filter('invalid json')
        self.assertEqual(result, {})
    
    def test_parse_sort_valid(self):
        """Test parsing valid sort JSON"""
        sort_str = '{"created_at": -1, "name": 1}'
        result = parse_sort(sort_str)
        self.assertEqual(len(result), 2)
    
    def test_parse_sort_empty(self):
        """Test parsing empty sort"""
        result = parse_sort('')
        self.assertIsNone(result)


class TestExportImport(unittest.TestCase):
    """Test export/import functionality"""
    
    @patch('main.MongoClient')
    def setUp(self, mock_client_class):
        self.mock_client = MagicMock()
        mock_client_class.return_value = self.mock_client
        
        self.skill = MongoDBSkill(uri='mongodb://localhost:27017', database='testdb')
        self.skill.client = self.mock_client
    
    def test_export_collection_json(self):
        """Test JSON export"""
        mock_db = MagicMock()
        mock_collection = MagicMock()
        self.mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        
        mock_cursor = MagicMock()
        mock_collection.find.return_value = mock_cursor
        mock_cursor.__iter__.return_value = iter([
            {'_id': '1', 'name': 'Alice'},
            {'_id': '2', 'name': 'Bob'}
        ])
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            self.skill.export_collection('users', temp_path, 'json')
            with open(temp_path, 'r') as f:
                data = json.load(f)
            self.assertEqual(len(data), 2)
        finally:
            os.unlink(temp_path)


class TestIntegration(unittest.TestCase):
    """Integration tests (requires MongoDB connection)"""
    
    @unittest.skipIf(not os.getenv('MONGODB_URI'), "MongoDB not configured")
    def test_real_connection(self):
        """Test with real MongoDB connection"""
        skill = MongoDBSkill(
            uri=os.getenv('MONGODB_URI', 'mongodb://localhost:27017'),
            database=os.getenv('MONGODB_DATABASE', 'test')
        )
        
        if skill.connect():
            # Test basic operations
            db_list = skill.list_databases()
            self.assertIsInstance(db_list, list)
            skill.close()


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestMongoDBSkill))
    suite.addTests(loader.loadTestsFromTestCase(TestParseFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestExportImport))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
