#!/usr/bin/env python3
"""
SQLite Skill - Test Suite
Tests all major functionality of the sqlite-skill
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import SQLiteSkill, format_table


class TestSQLiteSkill(unittest.TestCase):
    """Test cases for SQLite Skill"""
    
    def setUp(self):
        """Set up in-memory database for each test"""
        self.skill = SQLiteSkill(memory=True)
        self.assertTrue(self.skill.connect())
        
        # Create test table
        self.skill.execute_command('''
            CREATE TABLE test_users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                age INTEGER
            )
        ''')
        
        # Insert test data
        self.skill.execute_command("INSERT INTO test_users VALUES (1, 'Alice', 'alice@test.com', 30)")
        self.skill.execute_command("INSERT INTO test_users VALUES (2, 'Bob', 'bob@test.com', 25)")
    
    def tearDown(self):
        """Clean up after tests"""
        if self.skill:
            self.skill.close()
    
    def test_connection(self):
        """Test database connection"""
        self.assertIsNotNone(self.skill.conn)
        self.assertIsNotNone(self.skill.cursor)
    
    def test_execute_query(self):
        """Test query execution"""
        result = self.skill.execute_query("SELECT * FROM test_users")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Alice')
    
    def test_execute_query_with_params(self):
        """Test parameterized query"""
        result = self.skill.execute_query("SELECT * FROM test_users WHERE id = ?", (1,))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Alice')
    
    def test_execute_command(self):
        """Test command execution"""
        count = self.skill.execute_command("INSERT INTO test_users VALUES (3, 'Charlie', 'charlie@test.com', 35)")
        self.assertEqual(count, 1)
    
    def test_get_tables(self):
        """Test getting table list"""
        tables = self.skill.get_tables()
        self.assertIn('test_users', tables)
    
    def test_get_schema(self):
        """Test getting table schema"""
        schema = self.skill.get_schema('test_users')
        self.assertEqual(len(schema), 4)
        column_names = [col['name'] for col in schema]
        self.assertIn('id', column_names)
        self.assertIn('name', column_names)
    
    def test_get_ddl(self):
        """Test getting CREATE TABLE statement"""
        ddl = self.skill.get_ddl('test_users')
        self.assertIn('CREATE TABLE', ddl)
        self.assertIn('test_users', ddl)
    
    def test_get_database_info(self):
        """Test getting database info"""
        info = self.skill.get_database_info()
        self.assertIn('table_count', info)
        self.assertIn('tables', info)
        self.assertIn('sqlite_version', info)
        self.assertGreaterEqual(info['table_count'], 1)
    
    def test_vacuum(self):
        """Test vacuum operation"""
        # Should not raise exception
        self.skill.vacuum()
    
    def test_integrity_check(self):
        """Test integrity check"""
        result = self.skill.integrity_check()
        self.assertTrue(len(result) > 0)
        self.assertEqual(result[0]['integrity_check'], 'ok')
    
    def test_export_to_json(self):
        """Test JSON export"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            self.skill.export_to_json('test_users', temp_path)
            with open(temp_path, 'r') as f:
                data = json.load(f)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]['name'], 'Alice')
        finally:
            os.unlink(temp_path)
    
    def test_export_to_csv(self):
        """Test CSV export"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            self.skill.export_to_csv('test_users', temp_path)
            with open(temp_path, 'r') as f:
                content = f.read()
            self.assertIn('Alice', content)
            self.assertIn('Bob', content)
        finally:
            os.unlink(temp_path)
    
    def test_import_from_csv(self):
        """Test CSV import"""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('id,name,email,age\n')
            f.write('10,David,david@test.com,40\n')
            f.write('11,Eve,eve@test.com,28\n')
            temp_path = f.name
        
        try:
            self.skill.import_from_csv(temp_path, 'imported_users')
            result = self.skill.execute_query("SELECT * FROM imported_users")
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['name'], 'David')
        finally:
            os.unlink(temp_path)
    
    def test_pragma(self):
        """Test PRAGMA commands"""
        result = self.skill.execute_pragma('user_version')
        self.assertIsInstance(result, list)
        
        result = self.skill.execute_pragma('table_info(test_users)')
        self.assertEqual(len(result), 4)


class TestFileDatabase(unittest.TestCase):
    """Tests with file-based database"""
    
    def setUp(self):
        """Create temporary database file"""
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_file.close()
        self.db_path = self.temp_file.name
    
    def tearDown(self):
        """Remove temporary database"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_file_database(self):
        """Test file-based database operations"""
        skill = SQLiteSkill(database_path=self.db_path)
        self.assertTrue(skill.connect())
        
        skill.execute_command("CREATE TABLE test (id INTEGER)")
        skill.execute_command("INSERT INTO test VALUES (1)")
        
        result = skill.execute_query("SELECT * FROM test")
        self.assertEqual(len(result), 1)
        
        skill.close()
    
    def test_backup(self):
        """Test database backup"""
        skill = SQLiteSkill(database_path=self.db_path)
        skill.connect()
        skill.execute_command("CREATE TABLE test (id INTEGER)")
        skill.execute_command("INSERT INTO test VALUES (1)")
        skill.close()
        
        # Backup
        backup_path = self.db_path + '.backup'
        skill2 = SQLiteSkill(database_path=self.db_path)
        skill2.connect()
        skill2.backup(backup_path)
        skill2.close()
        
        # Verify backup exists and works
        self.assertTrue(os.path.exists(backup_path))
        skill3 = SQLiteSkill(database_path=backup_path)
        skill3.connect()
        result = skill3.execute_query("SELECT * FROM test")
        self.assertEqual(len(result), 1)
        skill3.close()
        
        os.unlink(backup_path)


class TestFormatTable(unittest.TestCase):
    """Test table formatting"""
    
    def test_format_table(self):
        """Test table formatting"""
        data = [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
        result = format_table(data)
        self.assertIn('id', result)
        self.assertIn('name', result)
        self.assertIn('Alice', result)
    
    def test_format_empty(self):
        """Test formatting empty data"""
        result = format_table([])
        self.assertEqual(result, "No results")
    
    def test_format_long_values(self):
        """Test formatting with long values"""
        data = [{'id': 1, 'description': 'This is a very long description'}]
        result = format_table(data)
        self.assertIn('description', result)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestSQLiteSkill))
    suite.addTests(loader.loadTestsFromTestCase(TestFileDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestFormatTable))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
