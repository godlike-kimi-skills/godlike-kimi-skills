#!/usr/bin/env python3
"""
GCP CLI Skill - Test Suite
Tests for Compute Engine, Cloud Storage, and BigQuery operations
"""

import unittest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Import the main module
import main as gcp_cli


class TestGCPResourceManager(unittest.TestCase):
    """Test GCP Resource Manager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
    
    # ==================== Compute Tests ====================
    
    @patch('main.compute_v1.InstancesClient')
    @patch('main.compute_v1.ZonesClient')
    @patch('main.storage.Client')
    @patch('main.bigquery.Client')
    def test_compute_list_instances(self, mock_bq, mock_storage, mock_zones, mock_compute):
        """Test listing Compute instances"""
        mock_client = MagicMock()
        mock_instance = MagicMock()
        mock_instance.name = 'test-instance'
        mock_instance.id = 12345
        mock_instance.machine_type = 'zones/us-central1-a/machineTypes/e2-medium'
        mock_instance.status = 'RUNNING'
        mock_instance.cpu_platform = 'Intel Skylake'
        mock_instance.creation_timestamp = '2024-01-01T00:00:00'
        mock_instance.network_interfaces = []
        
        mock_client.list.return_value = [mock_instance]
        mock_compute.return_value = mock_client
        mock_zones.return_value = MagicMock()
        mock_storage.return_value = MagicMock()
        mock_bq.return_value = MagicMock()
        
        gcp = gcp_cli.GCPResourceManager()
        gcp.compute_client = mock_client
        
        instances = gcp.compute_list_instances(zone='us-central1-a')
        
        self.assertEqual(len(instances), 1)
        self.assertEqual(instances[0]['name'], 'test-instance')
    
    @patch('main.compute_v1.InstancesClient')
    @patch('main.compute_v1.ZonesClient')
    @patch('main.storage.Client')
    @patch('main.bigquery.Client')
    def test_compute_get_instance(self, mock_bq, mock_storage, mock_zones, mock_compute):
        """Test getting Compute instance"""
        mock_client = MagicMock()
        mock_instance = MagicMock()
        mock_instance.name = 'test-instance'
        mock_instance.id = 12345
        mock_instance.machine_type = 'zones/us-central1-a/machineTypes/e2-medium'
        mock_instance.status = 'RUNNING'
        mock_instance.cpu_platform = 'Intel Skylake'
        mock_instance.creation_timestamp = '2024-01-01T00:00:00'
        mock_instance.network_interfaces = []
        
        mock_client.get.return_value = mock_instance
        mock_compute.return_value = mock_client
        mock_zones.return_value = MagicMock()
        mock_storage.return_value = MagicMock()
        mock_bq.return_value = MagicMock()
        
        gcp = gcp_cli.GCPResourceManager()
        gcp.compute_client = mock_client
        
        instance = gcp.compute_get_instance('test-instance', 'us-central1-a')
        
        self.assertIsNotNone(instance)
        self.assertEqual(instance['name'], 'test-instance')
    
    @patch('main.compute_v1.InstancesClient')
    @patch('main.compute_v1.ZonesClient')
    @patch('main.storage.Client')
    @patch('main.bigquery.Client')
    def test_compute_start_instance(self, mock_bq, mock_storage, mock_zones, mock_compute):
        """Test starting Compute instance"""
        mock_client = MagicMock()
        mock_operation = MagicMock()
        mock_client.start.return_value = mock_operation
        mock_compute.return_value = mock_client
        mock_zones.return_value = MagicMock()
        mock_storage.return_value = MagicMock()
        mock_bq.return_value = MagicMock()
        
        gcp = gcp_cli.GCPResourceManager()
        gcp.compute_client = mock_client
        gcp._wait_for_zone_operation = MagicMock()
        
        result = gcp.compute_start_instance('test-instance', 'us-central1-a')
        
        self.assertTrue(result)
        mock_client.start.assert_called_once()
    
    @patch('main.compute_v1.InstancesClient')
    @patch('main.compute_v1.ZonesClient')
    @patch('main.storage.Client')
    @patch('main.bigquery.Client')
    def test_compute_stop_instance(self, mock_bq, mock_storage, mock_zones, mock_compute):
        """Test stopping Compute instance"""
        mock_client = MagicMock()
        mock_operation = MagicMock()
        mock_client.stop.return_value = mock_operation
        mock_compute.return_value = mock_client
        mock_zones.return_value = MagicMock()
        mock_storage.return_value = MagicMock()
        mock_bq.return_value = MagicMock()
        
        gcp = gcp_cli.GCPResourceManager()
        gcp.compute_client = mock_client
        gcp._wait_for_zone_operation = MagicMock()
        
        result = gcp.compute_stop_instance('test-instance', 'us-central1-a')
        
        self.assertTrue(result)
        mock_client.stop.assert_called_once()
    
    @patch('main.compute_v1.InstancesClient')
    @patch('main.compute_v1.ZonesClient')
    @patch('main.storage.Client')
    @patch('main.bigquery.Client')
    def test_compute_delete_instance(self, mock_bq, mock_storage, mock_zones, mock_compute):
        """Test deleting Compute instance"""
        mock_client = MagicMock()
        mock_operation = MagicMock()
        mock_client.delete.return_value = mock_operation
        mock_compute.return_value = mock_client
        mock_zones.return_value = MagicMock()
        mock_storage.return_value = MagicMock()
        mock_bq.return_value = MagicMock()
        
        gcp = gcp_cli.GCPResourceManager()
        gcp.compute_client = mock_client
        gcp._wait_for_zone_operation = MagicMock()
        
        result = gcp.compute_delete_instance('test-instance', 'us-central1-a')
        
        self.assertTrue(result)
        mock_client.delete.assert_called_once()
    
    # ==================== Storage Tests ====================
    
    @patch('main.compute_v1.InstancesClient')
    @patch('main.compute_v1.ZonesClient')
    @patch('main.storage.Client')
    @patch('main.bigquery.Client')
    def test_storage_list_buckets(self, mock_bq, mock_storage, mock_zones, mock_compute):
        """Test listing Storage buckets"""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.name = 'test-bucket'
        mock_bucket.id = 'test-bucket-id'
        mock_bucket.location = 'US'
        mock_bucket.storage_class = 'STANDARD'
        mock_bucket.time_created = MagicMock(isoformat=lambda: '2024-01-01T00:00:00')
        mock_bucket.versioning_enabled = False
        
        mock_client.list_buckets.return_value = [mock_bucket]
        mock_storage.return_value = mock_client
        mock_compute.return_value = MagicMock()
        mock_zones.return_value = MagicMock()
        mock_bq.return_value = MagicMock()
        
        gcp = gcp_cli.GCPResourceManager()
        gcp.storage_client = mock_client
        
        buckets = gcp.storage_list_buckets()
        
        self.assertEqual(len(buckets), 1)
        self.assertEqual(buckets[0]['name'], 'test-bucket')
    
    @patch('main.compute_v1.InstancesClient')
    @patch('main.compute_v1.ZonesClient')
    @patch('main.storage.Client')
    @patch('main.bigquery.Client')
    def test_storage_get_bucket(self, mock_bq, mock_storage, mock_zones, mock_compute):
        """Test getting Storage bucket"""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.name = 'test-bucket'
        mock_bucket.id = 'test-bucket-id'
        mock_bucket.location = 'US'
        mock_bucket.storage_class = 'STANDARD'
        mock_bucket.time_created = MagicMock(isoformat=lambda: '2024-01-01T00:00:00')
        mock_bucket.versioning_enabled = False
        mock_bucket.labels = {}
        mock_bucket.lifecycle_rules = []
        
        mock_client.get_bucket.return_value = mock_bucket
        mock_storage.return_value = mock_client
        mock_compute.return_value = MagicMock()
        mock_zones.return_value = MagicMock()
        mock_bq.return_value = MagicMock()
        
        gcp = gcp_cli.GCPResourceManager()
        gcp.storage_client = mock_client
        
        bucket = gcp.storage_get_bucket('test-bucket')
        
        self.assertIsNotNone(bucket)
        self.assertEqual(bucket['name'], 'test-bucket')
    
    @patch('main.compute_v1.InstancesClient')
    @patch('main.compute_v1.ZonesClient')
    @patch('main.storage.Client')
    @patch('main.bigquery.Client')
    def test_storage_create_bucket(self, mock_bq, mock_storage, mock_zones, mock_compute):
        """Test creating Storage bucket"""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.name = 'new-bucket'
        mock_client.bucket.return_value = mock_bucket
        mock_client.create_bucket.return_value = mock_bucket
        mock_storage.return_value = mock_client
        mock_compute.return_value = MagicMock()
        mock_zones.return_value = MagicMock()
        mock_bq.return_value = MagicMock()
        
        gcp = gcp_cli.GCPResourceManager()
        gcp.storage_client = mock_client
        
        result = gcp.storage_create_bucket('new-bucket', 'US', 'STANDARD')
        
        self.assertTrue(result)
        mock_client.create_bucket.assert_called_once()
    
    @patch('main.compute_v1.InstancesClient')
    @patch('main.compute_v1.ZonesClient')
    @patch('main.storage.Client')
    @patch('main.bigquery.Client')
    def test_storage_delete_bucket(self, mock_bq, mock_storage, mock_zones, mock_compute):
        """Test deleting Storage bucket"""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_storage.return_value = mock_client
        mock_compute.return_value = MagicMock()
        mock_zones.return_value = MagicMock()
        mock_bq.return_value = MagicMock()
        
        gcp = gcp_cli.GCPResourceManager()
        gcp.storage_client = mock_client
        
        result = gcp.storage_delete_bucket('old-bucket')
        
        self.assertTrue(result)
        mock_bucket.delete.assert_called_once()
    
    @patch('main.compute_v1.InstancesClient')
    @patch('main.compute_v1.ZonesClient')
    @patch('main.storage.Client')
    @patch('main.bigquery.Client')
    def test_storage_list_objects(self, mock_bq, mock_storage, mock_zones, mock_compute):
        """Test listing Storage objects"""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.name = 'test-file.txt'
        mock_blob.size = 1024
        mock_blob.content_type = 'text/plain'
        mock_blob.updated = MagicMock(isoformat=lambda: '2024-01-01T00:00:00')
        mock_blob.storage_class = 'STANDARD'
        mock_blob.md5_hash = 'abc123'
        
        mock_bucket.list_blobs.return_value = [mock_blob]
        mock_client.bucket.return_value = mock_bucket
        mock_storage.return_value = mock_client
        mock_compute.return_value = MagicMock()
        mock_zones.return_value = MagicMock()
        mock_bq.return_value = MagicMock()
        
        gcp = gcp_cli.GCPResourceManager()
        gcp.storage_client = mock_client
        
        objects = gcp.storage_list_objects('test-bucket')
        
        self.assertEqual(len(objects), 1)
        self.assertEqual(objects[0]['name'], 'test-file.txt')
    
    # ==================== BigQuery Tests ====================
    
    @patch('main.compute_v1.InstancesClient')
    @patch('main.compute_v1.ZonesClient')
    @patch('main.storage.Client')
    @patch('main.bigquery.Client')
    def test_bquery_list_datasets(self, mock_bq, mock_storage, mock_zones, mock_compute):
        """Test listing BigQuery datasets"""
        mock_client = MagicMock()
        mock_dataset = MagicMock()
        mock_dataset.dataset_id = 'test_dataset'
        mock_dataset.project = 'test-project'
        mock_dataset.location = 'US'
        mock_dataset.created = MagicMock(isoformat=lambda: '2024-01-01T00:00:00')
        mock_dataset.modified = MagicMock(isoformat=lambda: '2024-01-02T00:00:00')
        mock_dataset.description = 'Test dataset'
        
        mock_client.list_datasets.return_value = [mock_dataset]
        mock_bq.return_value = mock_client
        mock_compute.return_value = MagicMock()
        mock_zones.return_value = MagicMock()
        mock_storage.return_value = MagicMock()
        
        gcp = gcp_cli.GCPResourceManager()
        gcp.bigquery_client = mock_client
        
        datasets = gcp.bquery_list_datasets()
        
        self.assertEqual(len(datasets), 1)
        self.assertEqual(datasets[0]['dataset_id'], 'test_dataset')
    
    @patch('main.compute_v1.InstancesClient')
    @patch('main.compute_v1.ZonesClient')
    @patch('main.storage.Client')
    @patch('main.bigquery.Client')
    def test_bquery_get_dataset(self, mock_bq, mock_storage, mock_zones, mock_compute):
        """Test getting BigQuery dataset"""
        mock_client = MagicMock()
        mock_dataset = MagicMock()
        mock_dataset.dataset_id = 'test_dataset'
        mock_dataset.project = 'test-project'
        mock_dataset.location = 'US'
        mock_dataset.created = MagicMock(isoformat=lambda: '2024-01-01T00:00:00')
        mock_dataset.modified = MagicMock(isoformat=lambda: '2024-01-02T00:00:00')
        mock_dataset.description = 'Test dataset'
        mock_dataset.labels = {}
        mock_dataset.access_entries = []
        
        mock_client.get_dataset.return_value = mock_dataset
        mock_bq.return_value = mock_client
        mock_compute.return_value = MagicMock()
        mock_zones.return_value = MagicMock()
        mock_storage.return_value = MagicMock()
        
        gcp = gcp_cli.GCPResourceManager()
        gcp.bigquery_client = mock_client
        
        dataset = gcp.bquery_get_dataset('test_dataset')
        
        self.assertIsNotNone(dataset)
        self.assertEqual(dataset['dataset_id'], 'test_dataset')
    
    @patch('main.compute_v1.InstancesClient')
    @patch('main.compute_v1.ZonesClient')
    @patch('main.storage.Client')
    @patch('main.bigquery.Client')
    def test_bquery_create_dataset(self, mock_bq, mock_storage, mock_zones, mock_compute):
        """Test creating BigQuery dataset"""
        mock_client = MagicMock()
        mock_dataset = MagicMock()
        mock_dataset.dataset_id = 'new_dataset'
        mock_client.create_dataset.return_value = mock_dataset
        mock_bq.return_value = mock_client
        mock_compute.return_value = MagicMock()
        mock_zones.return_value = MagicMock()
        mock_storage.return_value = MagicMock()
        
        gcp = gcp_cli.GCPResourceManager()
        gcp.bigquery_client = mock_client
        
        result = gcp.bquery_create_dataset('new_dataset', 'US', 'New dataset description')
        
        self.assertTrue(result)
        mock_client.create_dataset.assert_called_once()
    
    @patch('main.compute_v1.InstancesClient')
    @patch('main.compute_v1.ZonesClient')
    @patch('main.storage.Client')
    @patch('main.bigquery.Client')
    def test_bquery_list_tables(self, mock_bq, mock_storage, mock_zones, mock_compute):
        """Test listing BigQuery tables"""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_table.table_id = 'test_table'
        mock_table.dataset_id = 'test_dataset'
        mock_table.project = 'test-project'
        mock_table.table_type = 'TABLE'
        mock_table.created = MagicMock(isoformat=lambda: '2024-01-01T00:00:00')
        mock_table.expires = None
        mock_table.num_rows = 100
        mock_table.num_bytes = 1024
        
        mock_client.list_tables.return_value = [mock_table]
        mock_bq.return_value = mock_client
        mock_compute.return_value = MagicMock()
        mock_zones.return_value = MagicMock()
        mock_storage.return_value = MagicMock()
        
        gcp = gcp_cli.GCPResourceManager()
        gcp.bigquery_client = mock_client
        
        tables = gcp.bquery_list_tables('test_dataset')
        
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]['table_id'], 'test_table')
    
    @patch('main.compute_v1.InstancesClient')
    @patch('main.compute_v1.ZonesClient')
    @patch('main.storage.Client')
    @patch('main.bigquery.Client')
    def test_bquery_delete_table(self, mock_bq, mock_storage, mock_zones, mock_compute):
        """Test deleting BigQuery table"""
        mock_client = MagicMock()
        mock_bq.return_value = mock_client
        mock_compute.return_value = MagicMock()
        mock_zones.return_value = MagicMock()
        mock_storage.return_value = MagicMock()
        
        gcp = gcp_cli.GCPResourceManager()
        gcp.bigquery_client = mock_client
        
        result = gcp.bquery_delete_table('test_dataset', 'old_table')
        
        self.assertTrue(result)
        mock_client.delete_table.assert_called_once_with('test_dataset.old_table')
    
    # ==================== Search Tests ====================
    
    @patch('main.compute_v1.InstancesClient')
    @patch('main.compute_v1.ZonesClient')
    @patch('main.storage.Client')
    @patch('main.bigquery.Client')
    def test_search_resources(self, mock_bq, mock_storage, mock_zones, mock_compute):
        """Test searching resources"""
        mock_compute.return_value = MagicMock()
        mock_zones.return_value = MagicMock()
        mock_storage.return_value = MagicMock()
        mock_bq.return_value = MagicMock()
        
        gcp = gcp_cli.GCPResourceManager()
        
        # Mock the list methods
        gcp.compute_list_instances = MagicMock(return_value=[{'name': 'test-vm'}])
        gcp.storage_list_buckets = MagicMock(return_value=[{'name': 'test-bucket'}])
        gcp.bquery_list_datasets = MagicMock(return_value=[{'dataset_id': 'test_dataset'}])
        
        results = gcp.search_resources('test')
        
        self.assertIn('compute', results)
        self.assertIn('storage', results)
        self.assertIn('bigquery', results)
        self.assertEqual(len(results['compute']), 1)


class TestCLI(unittest.TestCase):
    """Test Command Line Interface"""
    
    @patch('main.GCPResourceManager')
    def test_cli_help(self, mock_gcp):
        """Test CLI help output"""
        with patch('sys.argv', ['main.py', '--help']):
            with self.assertRaises(SystemExit) as cm:
                gcp_cli.main()
            self.assertEqual(cm.exception.code, 0)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestGCPResourceManager))
    suite.addTests(loader.loadTestsFromTestCase(TestCLI))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
