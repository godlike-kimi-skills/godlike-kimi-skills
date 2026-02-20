#!/usr/bin/env python3
"""
AWS CLI Skill - Test Suite
Tests for EC2, S3, RDS, and DynamoDB operations
"""

import unittest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Import the main module
import main as aws_cli


class TestAWSResourceManager(unittest.TestCase):
    """Test AWS Resource Manager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        with patch('main.boto3.Session'):
            self.aws = aws_cli.AWSResourceManager(region='us-east-1')
    
    # ==================== EC2 Tests ====================
    
    @patch('main.boto3.Session')
    def test_ec2_list_instances(self, mock_session):
        """Test listing EC2 instances"""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        mock_client.describe_instances.return_value = {
            'Reservations': [{
                'Instances': [{
                    'InstanceId': 'i-1234567890abcdef0',
                    'InstanceType': 't2.micro',
                    'State': {'Name': 'running'},
                    'PublicIpAddress': '1.2.3.4',
                    'PrivateIpAddress': '10.0.0.1',
                    'Tags': [{'Key': 'Name', 'Value': 'test-instance'}],
                    'LaunchTime': MagicMock(isoformat=lambda: '2024-01-01T00:00:00')
                }]
            }]
        }
        
        aws = aws_cli.AWSResourceManager(region='us-east-1')
        instances = aws.ec2_list_instances()
        
        self.assertEqual(len(instances), 1)
        self.assertEqual(instances[0]['InstanceId'], 'i-1234567890abcdef0')
        self.assertEqual(instances[0]['State'], 'running')
    
    @patch('main.boto3.Session')
    def test_ec2_start_instance(self, mock_session):
        """Test starting EC2 instance"""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        aws = aws_cli.AWSResourceManager(region='us-east-1')
        result = aws.ec2_start_instance('i-1234567890abcdef0')
        
        self.assertTrue(result)
        mock_client.start_instances.assert_called_once_with(
            InstanceIds=['i-1234567890abcdef0']
        )
    
    @patch('main.boto3.Session')
    def test_ec2_create_instance(self, mock_session):
        """Test creating EC2 instance"""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        mock_client.run_instances.return_value = {
            'Instances': [{'InstanceId': 'i-newinstance123'}]
        }
        
        aws = aws_cli.AWSResourceManager(region='us-east-1')
        instance_id = aws.ec2_create_instance(
            name='test-vm',
            instance_type='t2.micro',
            ami='ami-12345678'
        )
        
        self.assertEqual(instance_id, 'i-newinstance123')
    
    # ==================== S3 Tests ====================
    
    @patch('main.boto3.Session')
    def test_s3_list_buckets(self, mock_session):
        """Test listing S3 buckets"""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        from datetime import datetime
        mock_client.list_buckets.return_value = {
            'Buckets': [
                {'Name': 'bucket1', 'CreationDate': datetime(2024, 1, 1)},
                {'Name': 'bucket2', 'CreationDate': datetime(2024, 1, 2)}
            ]
        }
        
        aws = aws_cli.AWSResourceManager(region='us-east-1')
        buckets = aws.s3_list_buckets()
        
        self.assertEqual(len(buckets), 2)
        self.assertEqual(buckets[0]['Name'], 'bucket1')
    
    @patch('main.boto3.Session')
    def test_s3_create_bucket(self, mock_session):
        """Test creating S3 bucket"""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        aws = aws_cli.AWSResourceManager(region='us-east-1')
        result = aws.s3_create_bucket('my-new-bucket')
        
        self.assertTrue(result)
        mock_client.create_bucket.assert_called_once_with(Bucket='my-new-bucket')
    
    @patch('main.boto3.Session')
    def test_s3_upload_file(self, mock_session):
        """Test uploading file to S3"""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        aws = aws_cli.AWSResourceManager(region='us-east-1')
        result = aws.s3_upload_file('my-bucket', '/path/to/file.txt', 'file.txt')
        
        self.assertTrue(result)
        mock_client.upload_file.assert_called_once_with(
            '/path/to/file.txt', 'my-bucket', 'file.txt'
        )
    
    @patch('main.boto3.Session')
    def test_s3_get_presigned_url(self, mock_session):
        """Test generating presigned URL"""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        mock_client.generate_presigned_url.return_value = 'https://s3.amazonaws.com/bucket/key?token=xxx'
        
        aws = aws_cli.AWSResourceManager(region='us-east-1')
        url = aws.s3_get_presigned_url('my-bucket', 'file.txt', 3600)
        
        self.assertIsNotNone(url)
        self.assertIn('https://', url)
    
    # ==================== RDS Tests ====================
    
    @patch('main.boto3.Session')
    def test_rds_list_instances(self, mock_session):
        """Test listing RDS instances"""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        mock_client.describe_db_instances.return_value = {
            'DBInstances': [{
                'DBInstanceIdentifier': 'my-db',
                'DBInstanceClass': 'db.t3.micro',
                'Engine': 'mysql',
                'DBInstanceStatus': 'available',
                'Endpoint': {'Address': 'my-db.xxx.us-east-1.rds.amazonaws.com', 'Port': 3306}
            }]
        }
        
        aws = aws_cli.AWSResourceManager(region='us-east-1')
        instances = aws.rds_list_instances()
        
        self.assertEqual(len(instances), 1)
        self.assertEqual(instances[0]['DBInstanceIdentifier'], 'my-db')
    
    @patch('main.boto3.Session')
    def test_rds_create_instance(self, mock_session):
        """Test creating RDS instance"""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        aws = aws_cli.AWSResourceManager(region='us-east-1')
        result = aws.rds_create_instance(
            db_id='new-db',
            engine='mysql',
            instance_class='db.t3.micro',
            master_user='admin',
            master_pass='password123'
        )
        
        self.assertTrue(result)
        mock_client.create_db_instance.assert_called_once()
    
    @patch('main.boto3.Session')
    def test_rds_create_snapshot(self, mock_session):
        """Test creating RDS snapshot"""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        aws = aws_cli.AWSResourceManager(region='us-east-1')
        result = aws.rds_create_snapshot('my-db', 'my-snapshot')
        
        self.assertTrue(result)
        mock_client.create_db_snapshot.assert_called_once_with(
            DBInstanceIdentifier='my-db',
            DBSnapshotIdentifier='my-snapshot'
        )
    
    # ==================== DynamoDB Tests ====================
    
    @patch('main.boto3.Session')
    def test_dynamodb_list_tables(self, mock_session):
        """Test listing DynamoDB tables"""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        mock_client.list_tables.return_value = {
            'TableNames': ['table1', 'table2', 'table3']
        }
        
        aws = aws_cli.AWSResourceManager(region='us-east-1')
        tables = aws.dynamodb_list_tables()
        
        self.assertEqual(len(tables), 3)
        self.assertIn('table1', tables)
    
    @patch('main.boto3.Session')
    def test_dynamodb_create_table(self, mock_session):
        """Test creating DynamoDB table"""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        aws = aws_cli.AWSResourceManager(region='us-east-1')
        result = aws.dynamodb_create_table('my-table', 'id', 'S', 5, 5)
        
        self.assertTrue(result)
        mock_client.create_table.assert_called_once()
    
    @patch('main.boto3.Session')
    def test_dynamodb_describe_table(self, mock_session):
        """Test describing DynamoDB table"""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        mock_client.describe_table.return_value = {
            'Table': {
                'TableName': 'my-table',
                'TableStatus': 'ACTIVE',
                'ItemCount': 100
            }
        }
        
        aws = aws_cli.AWSResourceManager(region='us-east-1')
        table = aws.dynamodb_describe_table('my-table')
        
        self.assertIsNotNone(table)
        self.assertEqual(table['TableName'], 'my-table')
    
    @patch('main.boto3.Session')
    def test_dynamodb_scan(self, mock_session):
        """Test scanning DynamoDB table"""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        mock_client.scan.return_value = {
            'Items': [{'id': {'S': '1'}, 'name': {'S': 'test'}}]
        }
        
        aws = aws_cli.AWSResourceManager(region='us-east-1')
        items = aws.dynamodb_scan('my-table')
        
        self.assertEqual(len(items), 1)
    
    # ==================== Error Handling Tests ====================
    
    @patch('main.boto3.Session')
    def test_ec2_list_instances_error(self, mock_session):
        """Test EC2 list with client error"""
        from botocore.exceptions import ClientError
        
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.describe_instances.side_effect = ClientError(
            {'Error': {'Code': 'UnauthorizedOperation', 'Message': 'Access denied'}},
            'DescribeInstances'
        )
        
        aws = aws_cli.AWSResourceManager(region='us-east-1')
        instances = aws.ec2_list_instances()
        
        self.assertEqual(instances, [])
    
    @patch('main.boto3.Session')
    def test_s3_list_buckets_error(self, mock_session):
        """Test S3 list with client error"""
        from botocore.exceptions import ClientError
        
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.list_buckets.side_effect = ClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
            'ListBuckets'
        )
        
        aws = aws_cli.AWSResourceManager(region='us-east-1')
        buckets = aws.s3_list_buckets()
        
        self.assertEqual(buckets, [])
    
    # ==================== Search Tests ====================
    
    @patch('main.boto3.Session')
    def test_search_resources(self, mock_session):
        """Test searching resources across services"""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        mock_client.describe_instances.return_value = {'Reservations': []}
        mock_client.list_buckets.return_value = {'Buckets': []}
        mock_client.describe_db_instances.return_value = {'DBInstances': []}
        mock_client.list_tables.return_value = {'TableNames': []}
        
        aws = aws_cli.AWSResourceManager(region='us-east-1')
        results = aws.search_resources('test')
        
        self.assertIn('ec2', results)
        self.assertIn('s3', results)
        self.assertIn('rds', results)
        self.assertIn('dynamodb', results)


class TestCLI(unittest.TestCase):
    """Test Command Line Interface"""
    
    @patch('main.AWSResourceManager')
    def test_cli_help(self, mock_aws):
        """Test CLI help output"""
        with patch('sys.argv', ['main.py', '--help']):
            with self.assertRaises(SystemExit) as cm:
                aws_cli.main()
            self.assertEqual(cm.exception.code, 0)
    
    @patch('main.AWSResourceManager')
    def test_ec2_list_command(self, mock_aws_class):
        """Test EC2 list command"""
        mock_aws = MagicMock()
        mock_aws_class.return_value = mock_aws
        mock_aws.ec2_list_instances.return_value = [
            {'InstanceId': 'i-123', 'State': 'running'}
        ]
        
        with patch('sys.argv', ['main.py', 'ec2', 'list', '--region', 'us-east-1']):
            aws_cli.main()
            mock_aws.ec2_list_instances.assert_called_once()


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestAWSResourceManager))
    suite.addTests(loader.loadTestsFromTestCase(TestCLI))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
