#!/usr/bin/env python3
"""
PostgreSQL Skill - Test Suite
Tests all major functionality of the postgres-skill
"""

import json
import os
import sys
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import PostgresSkill, parse_connection_string, format_table


class TestPostgresSkill(unittest.TestCase):
    """Test cases for PostgreSQL Skill"""
    
    @patch('main.psycopg2.connect')
    def setUp(self, mock_connect):
        """Set up test fixtures"""
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        mock_connect.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor
        
        self.skill = PostgresSkill({
            'host': 'localhost',
            'port': 5432,
            'database': 'testdb',
            'user': 'postgres',
            'password': 'secret'
        })
        self.skill.connect()
    
    def tearDown(self):
        """Clean up after tests"""
        if self.skill:
            self.skill.close()
    
    def test_connection_params(self):
        """Test connection parameters are stored correctly"""
        self.assertEqual(self.skill.connection_params['host'], 'localhost')
        self.assertEqual(self.skill.connection_params['port'], 5432)
        self.assertEqual(self.skill.connection_params['database'], 'testdb')
    
    @patch('main.psycopg2.connect')
    def test_connect_success(self, mock_connect):
        """Test successful connection"""
        mock_connect.return_value = self.mock_conn
        result = self.skill.connect()
        self.assertTrue(result)
    
    @patch('main.psycopg2.connect')
    def test_connect_failure(self, mock_connect):
        """Test connection failure handling"""
        mock_connect.side_effect = Exception("Connection refused")
        result = self.skill.connect()
        self.assertFalse(result)
    
    def test_execute_query(self):
        """Test query execution"""
        mock_result = [
            {'id': 1, 'name': 'Test'},
            {'id': 2, 'name': 'Test2'}
        ]
        self.mock_cursor.fetchall.return_value = mock_result
        
        result = self.skill.execute_query("SELECT * FROM test")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Test')
    
    def test_execute_command(self):
        """Test command execution"""
        result = self.skill.execute_command("INSERT INTO test VALUES (1)")
        self.assertTrue(result)
        self.mock_conn.commit.assert_called_once()
    
    def test_get_tables(self):
        """Test getting table list"""
        mock_result = [
            {'table_name': 'users'},
            {'table_name': 'orders'}
        ]
        self.mock_cursor.fetchall.return_value = mock_result
        
        tables = self.skill.get_tables()
        self.assertEqual(len(tables), 2)
        self.assertIn('users', tables)
        self.assertIn('orders', tables)
    
    def test_describe_table(self):
        """Test describing table structure"""
        mock_result = [
            {'column_name': 'id', 'data_type': 'integer', 'is_nullable': 'NO', 'column_default': None},
            {'column_name': 'name', 'data_type': 'varchar', 'is_nullable': 'YES', 'column_default': None}
        ]
        self.mock_cursor.fetchall.return_value = mock_result
        
        result = self.skill.describe_table('users')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['column_name'], 'id')
    
    def test_get_indexes(self):
        """Test getting table indexes"""
        mock_result = [
            {'indexname': 'users_pkey', 'indexdef': 'CREATE UNIQUE INDEX users_pkey ON users USING btree (id)'}
        ]
        self.mock_cursor.fetchall.return_value = mock_result
        
        result = self.skill.get_indexes('users')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['indexname'], 'users_pkey')


class TestConnectionString(unittest.TestCase):
    """Test connection string parsing"""
    
    def test_parse_basic_connection_string(self):
        """Test parsing basic connection string"""
        conn_str = "postgresql://user:pass@localhost:5432/mydb"
        result = parse_connection_string(conn_str)
        
        self.assertEqual(result['host'], 'localhost')
        self.assertEqual(result['port'], 5432)
        self.assertEqual(result['database'], 'mydb')
        self.assertEqual(result['user'], 'user')
        self.assertEqual(result['password'], 'pass')
    
    def test_parse_connection_string_defaults(self):
        """Test parsing with default values"""
        conn_str = "postgresql://user@localhost/mydb"
        result = parse_connection_string(conn_str)
        
        self.assertEqual(result['host'], 'localhost')
        self.assertEqual(result['port'], 5432)
        self.assertIsNone(result['password'])


class TestFormatTable(unittest.TestCase):
    """Test table formatting"""
    
    def test_format_table_basic(self):
        """Test basic table formatting"""
        data = [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
        result = format_table(data)
        
        self.assertIn('id', result)
        self.assertIn('name', result)
        self.assertIn('Alice', result)
        self.assertIn('Bob', result)
    
    def test_format_table_empty(self):
        """Test formatting empty data"""
        result = format_table([])
        self.assertEqual(result, "No results")


class TestIntegration(unittest.TestCase):
    """Integration tests (requires PostgreSQL connection)"""
    
    @unittest.skipIf(not os.getenv('PGHOST'), "PostgreSQL not configured")
    def test_real_connection(self):
        """Test with real PostgreSQL connection"""
        skill = PostgresSkill({
            'host': os.getenv('PGHOST', 'localhost'),
            'port': int(os.getenv('PGPORT', 5432)),
            'database': os.getenv('PGDATABASE', 'postgres'),
            'user': os.getenv('PGUSER', 'postgres'),
            'password': os.getenv('PGPASSWORD', '')
        })
        
        if skill.connect():
            # Test basic query
            result = skill.execute_query("SELECT 1 as test")
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['test'], 1)
            skill.close()


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPostgresSkill))
    suite.addTests(loader.loadTestsFromTestCase(TestConnectionString))
    suite.addTests(loader.loadTestsFromTestCase(TestFormatTable))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
