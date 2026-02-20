#!/usr/bin/env python3
"""
MySQL Skill - Test Suite
Tests all major functionality of the mysql-skill
"""

import json
import os
import sys
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import MySQLSkill, parse_connection_string, format_table


class TestMySQLSkill(unittest.TestCase):
    """Test cases for MySQL Skill"""
    
    @patch('main.pymysql.connect')
    def setUp(self, mock_connect):
        """Set up test fixtures"""
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        mock_connect.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor
        
        self.skill = MySQLSkill({
            'host': 'localhost',
            'port': 3306,
            'database': 'testdb',
            'user': 'root',
            'password': 'secret',
            'charset': 'utf8mb4'
        })
        self.skill.connect()
    
    def tearDown(self):
        """Clean up after tests"""
        if self.skill:
            self.skill.close()
    
    def test_connection_params(self):
        """Test connection parameters"""
        self.assertEqual(self.skill.connection_params['host'], 'localhost')
        self.assertEqual(self.skill.connection_params['port'], 3306)
        self.assertEqual(self.skill.connection_params['charset'], 'utf8mb4')
    
    @patch('main.pymysql.connect')
    def test_connect_success(self, mock_connect):
        """Test successful connection"""
        mock_connect.return_value = self.mock_conn
        result = self.skill.connect()
        self.assertTrue(result)
    
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
        self.mock_cursor.rowcount = 1
        result = self.skill.execute_command("UPDATE test SET name='X'")
        self.assertEqual(result, 1)
    
    def test_get_tables(self):
        """Test getting table list"""
        mock_result = [
            {'Tables_in_testdb': 'users'},
            {'Tables_in_testdb': 'orders'}
        ]
        self.mock_cursor.fetchall.return_value = mock_result
        
        tables = self.skill.get_tables()
        self.assertEqual(len(tables), 2)
        self.assertIn('users', tables)
    
    def test_describe_table(self):
        """Test describing table"""
        mock_result = [
            {'Field': 'id', 'Type': 'int', 'Null': 'NO', 'Key': 'PRI'},
            {'Field': 'name', 'Type': 'varchar(255)', 'Null': 'YES', 'Key': ''}
        ]
        self.mock_cursor.fetchall.return_value = mock_result
        
        result = self.skill.describe_table('users')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['Field'], 'id')
    
    def test_create_table(self):
        """Test table creation"""
        self.mock_cursor.rowcount = 0
        result = self.skill.create_table('new_table', 'id INT PRIMARY KEY, name VARCHAR(100)')
        self.assertEqual(result, 0)
    
    def test_drop_table(self):
        """Test table deletion"""
        self.mock_cursor.rowcount = 0
        result = self.skill.drop_table('old_table')
        self.assertEqual(result, 0)
    
    def test_get_users(self):
        """Test getting user list"""
        mock_result = [
            {'User': 'root', 'Host': 'localhost'},
            {'User': 'app_user', 'Host': '%'}
        ]
        self.mock_cursor.fetchall.return_value = mock_result
        
        result = self.skill.get_users()
        self.assertEqual(len(result), 2)


class TestConnectionString(unittest.TestCase):
    """Test connection string parsing"""
    
    def test_parse_mysql_connection_string(self):
        """Test parsing MySQL connection string"""
        conn_str = "mysql://root:pass@localhost:3306/mydb"
        result = parse_connection_string(conn_str)
        
        self.assertEqual(result['host'], 'localhost')
        self.assertEqual(result['port'], 3306)
        self.assertEqual(result['database'], 'mydb')
        self.assertEqual(result['user'], 'root')
        self.assertEqual(result['password'], 'pass')
        self.assertEqual(result['charset'], 'utf8mb4')
    
    def test_parse_minimal_connection_string(self):
        """Test parsing minimal connection string"""
        conn_str = "mysql://user@host/db"
        result = parse_connection_string(conn_str)
        
        self.assertEqual(result['host'], 'host')
        self.assertEqual(result['port'], 3306)


class TestFormatTable(unittest.TestCase):
    """Test table formatting"""
    
    def test_format_table(self):
        """Test table formatting"""
        data = [
            {'id': 1, 'status': 'active'},
            {'id': 2, 'status': 'inactive'}
        ]
        result = format_table(data)
        
        self.assertIn('id', result)
        self.assertIn('status', result)
        self.assertIn('active', result)
    
    def test_format_empty_table(self):
        """Test formatting empty result"""
        result = format_table([])
        self.assertEqual(result, "No results")


class TestIntegration(unittest.TestCase):
    """Integration tests (requires MySQL connection)"""
    
    @unittest.skipIf(not os.getenv('MYSQL_HOST'), "MySQL not configured")
    def test_real_connection(self):
        """Test with real MySQL connection"""
        skill = MySQLSkill({
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'database': os.getenv('MYSQL_DATABASE', 'mysql'),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', ''),
            'charset': 'utf8mb4'
        })
        
        if skill.connect():
            result = skill.execute_query("SELECT 1 as test")
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['test'], 1)
            skill.close()


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestMySQLSkill))
    suite.addTests(loader.loadTestsFromTestCase(TestConnectionString))
    suite.addTests(loader.loadTestsFromTestCase(TestFormatTable))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
