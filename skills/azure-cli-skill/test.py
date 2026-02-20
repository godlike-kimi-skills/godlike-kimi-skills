#!/usr/bin/env python3
"""
Azure CLI Skill - Test Suite
Tests for VM, Storage, SQL Database, and Resource Group operations
"""

import unittest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Import the main module
import main as azure_cli


class TestAzureResourceManager(unittest.TestCase):
    """Test Azure Resource Manager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-subscription-id'
        with patch('main.DefaultAzureCredential'):
            with patch('azure.mgmt.compute.ComputeManagementClient'):
                with patch('azure.mgmt.storage.StorageManagementClient'):
                    with patch('azure.mgmt.sql.SqlManagementClient'):
                        with patch('azure.mgmt.resource.ResourceManagementClient'):
                            self.azure = azure_cli.AzureResourceManager()
    
    # ==================== VM Tests ====================
    
    @patch('main.DefaultAzureCredential')
    def test_vm_list(self, mock_credential):
        """Test listing VMs"""
        os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-sub-id'
        
        mock_compute = MagicMock()
        with patch('azure.mgmt.compute.ComputeManagementClient', return_value=mock_compute):
            with patch('azure.mgmt.storage.StorageManagementClient'):
                with patch('azure.mgmt.sql.SqlManagementClient'):
                    with patch('azure.mgmt.resource.ResourceManagementClient'):
                        azure = azure_cli.AzureResourceManager()
                        
                        mock_vm = MagicMock()
                        mock_vm.name = 'test-vm'
                        mock_vm.id = '/subscriptions/test/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/test-vm'
                        mock_vm.type = 'Microsoft.Compute/virtualMachines'
                        mock_vm.location = 'eastus'
                        mock_vm.hardware_profile.vm_size = 'Standard_B1s'
                        mock_vm.storage_profile.os_disk.os_type = 'Linux'
                        mock_vm.provisioning_state = 'Succeeded'
                        
                        mock_compute.virtual_machines.list_all.return_value = [mock_vm]
                        azure.compute_client = mock_compute
                        
                        vms = azure.vm_list()
                        
                        self.assertEqual(len(vms), 1)
                        self.assertEqual(vms[0]['name'], 'test-vm')
    
    @patch('main.DefaultAzureCredential')
    def test_vm_start(self, mock_credential):
        """Test starting VM"""
        os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-sub-id'
        
        mock_compute = MagicMock()
        mock_poller = MagicMock()
        mock_compute.virtual_machines.begin_start.return_value = mock_poller
        
        with patch('azure.mgmt.compute.ComputeManagementClient', return_value=mock_compute):
            with patch('azure.mgmt.storage.StorageManagementClient'):
                with patch('azure.mgmt.sql.SqlManagementClient'):
                    with patch('azure.mgmt.resource.ResourceManagementClient'):
                        azure = azure_cli.AzureResourceManager()
                        azure.compute_client = mock_compute
                        
                        result = azure.vm_start('test-rg', 'test-vm')
                        
                        self.assertTrue(result)
                        mock_compute.virtual_machines.begin_start.assert_called_once_with('test-rg', 'test-vm')
    
    @patch('main.DefaultAzureCredential')
    def test_vm_stop(self, mock_credential):
        """Test stopping VM"""
        os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-sub-id'
        
        mock_compute = MagicMock()
        mock_poller = MagicMock()
        mock_compute.virtual_machines.begin_deallocate.return_value = mock_poller
        
        with patch('azure.mgmt.compute.ComputeManagementClient', return_value=mock_compute):
            with patch('azure.mgmt.storage.StorageManagementClient'):
                with patch('azure.mgmt.sql.SqlManagementClient'):
                    with patch('azure.mgmt.resource.ResourceManagementClient'):
                        azure = azure_cli.AzureResourceManager()
                        azure.compute_client = mock_compute
                        
                        result = azure.vm_stop('test-rg', 'test-vm', deallocate=True)
                        
                        self.assertTrue(result)
                        mock_compute.virtual_machines.begin_deallocate.assert_called_once_with('test-rg', 'test-vm')
    
    @patch('main.DefaultAzureCredential')
    def test_vm_restart(self, mock_credential):
        """Test restarting VM"""
        os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-sub-id'
        
        mock_compute = MagicMock()
        mock_poller = MagicMock()
        mock_compute.virtual_machines.begin_restart.return_value = mock_poller
        
        with patch('azure.mgmt.compute.ComputeManagementClient', return_value=mock_compute):
            with patch('azure.mgmt.storage.StorageManagementClient'):
                with patch('azure.mgmt.sql.SqlManagementClient'):
                    with patch('azure.mgmt.resource.ResourceManagementClient'):
                        azure = azure_cli.AzureResourceManager()
                        azure.compute_client = mock_compute
                        
                        result = azure.vm_restart('test-rg', 'test-vm')
                        
                        self.assertTrue(result)
                        mock_compute.virtual_machines.begin_restart.assert_called_once_with('test-rg', 'test-vm')
    
    # ==================== Storage Tests ====================
    
    @patch('main.DefaultAzureCredential')
    def test_storage_list_accounts(self, mock_credential):
        """Test listing storage accounts"""
        os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-sub-id'
        
        mock_storage = MagicMock()
        mock_acct = MagicMock()
        mock_acct.name = 'teststorage'
        mock_acct.id = '/subscriptions/test/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/teststorage'
        mock_acct.location = 'eastus'
        mock_acct.sku.name = 'Standard_LRS'
        mock_acct.kind = 'StorageV2'
        mock_acct.primary_endpoints.blob = 'https://teststorage.blob.core.windows.net'
        
        mock_storage.storage_accounts.list.return_value = [mock_acct]
        
        with patch('azure.mgmt.compute.ComputeManagementClient'):
            with patch('azure.mgmt.storage.StorageManagementClient', return_value=mock_storage):
                with patch('azure.mgmt.sql.SqlManagementClient'):
                    with patch('azure.mgmt.resource.ResourceManagementClient'):
                        azure = azure_cli.AzureResourceManager()
                        azure.storage_client = mock_storage
                        
                        accounts = azure.storage_list_accounts()
                        
                        self.assertEqual(len(accounts), 1)
                        self.assertEqual(accounts[0]['name'], 'teststorage')
    
    @patch('main.DefaultAzureCredential')
    def test_storage_create_account(self, mock_credential):
        """Test creating storage account"""
        os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-sub-id'
        
        mock_storage = MagicMock()
        mock_poller = MagicMock()
        mock_storage.storage_accounts.begin_create.return_value = mock_poller
        
        with patch('azure.mgmt.compute.ComputeManagementClient'):
            with patch('azure.mgmt.storage.StorageManagementClient', return_value=mock_storage):
                with patch('azure.mgmt.sql.SqlManagementClient'):
                    with patch('azure.mgmt.resource.ResourceManagementClient'):
                        azure = azure_cli.AzureResourceManager()
                        azure.storage_client = mock_storage
                        
                        result = azure.storage_create_account('test-rg', 'newstorage', 'eastus')
                        
                        self.assertTrue(result)
                        mock_storage.storage_accounts.begin_create.assert_called_once()
    
    @patch('main.DefaultAzureCredential')
    def test_storage_delete_account(self, mock_credential):
        """Test deleting storage account"""
        os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-sub-id'
        
        mock_storage = MagicMock()
        
        with patch('azure.mgmt.compute.ComputeManagementClient'):
            with patch('azure.mgmt.storage.StorageManagementClient', return_value=mock_storage):
                with patch('azure.mgmt.sql.SqlManagementClient'):
                    with patch('azure.mgmt.resource.ResourceManagementClient'):
                        azure = azure_cli.AzureResourceManager()
                        azure.storage_client = mock_storage
                        
                        result = azure.storage_delete_account('test-rg', 'oldstorage')
                        
                        self.assertTrue(result)
                        mock_storage.storage_accounts.delete.assert_called_once_with('test-rg', 'oldstorage')
    
    # ==================== SQL Tests ====================
    
    @patch('main.DefaultAzureCredential')
    def test_sql_list_servers(self, mock_credential):
        """Test listing SQL servers"""
        os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-sub-id'
        
        mock_sql = MagicMock()
        mock_server = MagicMock()
        mock_server.name = 'test-server'
        mock_server.id = '/subscriptions/test/resourceGroups/rg/providers/Microsoft.Sql/servers/test-server'
        mock_server.location = 'eastus'
        mock_server.fully_qualified_domain_name = 'test-server.database.windows.net'
        mock_server.administrator_login = 'admin'
        mock_server.version = '12.0'
        
        mock_sql.servers.list.return_value = [mock_server]
        
        with patch('azure.mgmt.compute.ComputeManagementClient'):
            with patch('azure.mgmt.storage.StorageManagementClient'):
                with patch('azure.mgmt.sql.SqlManagementClient', return_value=mock_sql):
                    with patch('azure.mgmt.resource.ResourceManagementClient'):
                        azure = azure_cli.AzureResourceManager()
                        azure.sql_client = mock_sql
                        
                        servers = azure.sql_list_servers()
                        
                        self.assertEqual(len(servers), 1)
                        self.assertEqual(servers[0]['name'], 'test-server')
    
    @patch('main.DefaultAzureCredential')
    def test_sql_create_server(self, mock_credential):
        """Test creating SQL server"""
        os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-sub-id'
        
        mock_sql = MagicMock()
        mock_poller = MagicMock()
        mock_sql.servers.begin_create_or_update.return_value = mock_poller
        
        with patch('azure.mgmt.compute.ComputeManagementClient'):
            with patch('azure.mgmt.storage.StorageManagementClient'):
                with patch('azure.mgmt.sql.SqlManagementClient', return_value=mock_sql):
                    with patch('azure.mgmt.resource.ResourceManagementClient'):
                        azure = azure_cli.AzureResourceManager()
                        azure.sql_client = mock_sql
                        
                        result = azure.sql_create_server('test-rg', 'new-server', 'eastus', 'admin', 'password123')
                        
                        self.assertTrue(result)
                        mock_sql.servers.begin_create_or_update.assert_called_once()
    
    @patch('main.DefaultAzureCredential')
    def test_sql_list_databases(self, mock_credential):
        """Test listing databases"""
        os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-sub-id'
        
        mock_sql = MagicMock()
        mock_db = MagicMock()
        mock_db.name = 'test-db'
        mock_db.id = '/subscriptions/test/resourceGroups/rg/providers/Microsoft.Sql/servers/test-server/databases/test-db'
        mock_db.status = 'Online'
        mock_db.collation = 'SQL_Latin1_General_CP1_CI_AS'
        mock_db.max_size_gb = 2
        
        mock_sql.databases.list_by_server.return_value = [mock_db]
        
        with patch('azure.mgmt.compute.ComputeManagementClient'):
            with patch('azure.mgmt.storage.StorageManagementClient'):
                with patch('azure.mgmt.sql.SqlManagementClient', return_value=mock_sql):
                    with patch('azure.mgmt.resource.ResourceManagementClient'):
                        azure = azure_cli.AzureResourceManager()
                        azure.sql_client = mock_sql
                        
                        dbs = azure.sql_list_databases('test-rg', 'test-server')
                        
                        self.assertEqual(len(dbs), 1)
                        self.assertEqual(dbs[0]['name'], 'test-db')
    
    @patch('main.DefaultAzureCredential')
    def test_sql_create_database(self, mock_credential):
        """Test creating database"""
        os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-sub-id'
        
        mock_sql = MagicMock()
        mock_server = MagicMock()
        mock_server.location = 'eastus'
        mock_sql.servers.get.return_value = mock_server
        
        mock_poller = MagicMock()
        mock_sql.databases.begin_create_or_update.return_value = mock_poller
        
        with patch('azure.mgmt.compute.ComputeManagementClient'):
            with patch('azure.mgmt.storage.StorageManagementClient'):
                with patch('azure.mgmt.sql.SqlManagementClient', return_value=mock_sql):
                    with patch('azure.mgmt.resource.ResourceManagementClient'):
                        azure = azure_cli.AzureResourceManager()
                        azure.sql_client = mock_sql
                        
                        result = azure.sql_create_database('test-rg', 'test-server', 'new-db')
                        
                        self.assertTrue(result)
                        mock_sql.databases.begin_create_or_update.assert_called_once()
    
    # ==================== Resource Group Tests ====================
    
    @patch('main.DefaultAzureCredential')
    def test_group_list(self, mock_credential):
        """Test listing resource groups"""
        os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-sub-id'
        
        mock_resource = MagicMock()
        mock_group = MagicMock()
        mock_group.name = 'test-rg'
        mock_group.id = '/subscriptions/test/resourceGroups/test-rg'
        mock_group.location = 'eastus'
        mock_group.managed_by = None
        mock_group.properties.provisioning_state = 'Succeeded'
        
        mock_resource.resource_groups.list.return_value = [mock_group]
        
        with patch('azure.mgmt.compute.ComputeManagementClient'):
            with patch('azure.mgmt.storage.StorageManagementClient'):
                with patch('azure.mgmt.sql.SqlManagementClient'):
                    with patch('azure.mgmt.resource.ResourceManagementClient', return_value=mock_resource):
                        azure = azure_cli.AzureResourceManager()
                        azure.resource_client = mock_resource
                        
                        groups = azure.group_list()
                        
                        self.assertEqual(len(groups), 1)
                        self.assertEqual(groups[0]['name'], 'test-rg')
    
    @patch('main.DefaultAzureCredential')
    def test_group_create(self, mock_credential):
        """Test creating resource group"""
        os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-sub-id'
        
        mock_resource = MagicMock()
        
        with patch('azure.mgmt.compute.ComputeManagementClient'):
            with patch('azure.mgmt.storage.StorageManagementClient'):
                with patch('azure.mgmt.sql.SqlManagementClient'):
                    with patch('azure.mgmt.resource.ResourceManagementClient', return_value=mock_resource):
                        azure = azure_cli.AzureResourceManager()
                        azure.resource_client = mock_resource
                        
                        result = azure.group_create('new-rg', 'eastus')
                        
                        self.assertTrue(result)
                        mock_resource.resource_groups.create_or_update.assert_called_once()
    
    @patch('main.DefaultAzureCredential')
    def test_group_delete(self, mock_credential):
        """Test deleting resource group"""
        os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-sub-id'
        
        mock_resource = MagicMock()
        mock_poller = MagicMock()
        mock_resource.resource_groups.begin_delete.return_value = mock_poller
        
        with patch('azure.mgmt.compute.ComputeManagementClient'):
            with patch('azure.mgmt.storage.StorageManagementClient'):
                with patch('azure.mgmt.sql.SqlManagementClient'):
                    with patch('azure.mgmt.resource.ResourceManagementClient', return_value=mock_resource):
                        azure = azure_cli.AzureResourceManager()
                        azure.resource_client = mock_resource
                        
                        result = azure.group_delete('old-rg')
                        
                        self.assertTrue(result)
                        mock_resource.resource_groups.begin_delete.assert_called_once_with('old-rg')
    
    # ==================== Search Tests ====================
    
    @patch('main.DefaultAzureCredential')
    def test_search_resources(self, mock_credential):
        """Test searching resources"""
        os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-sub-id'
        
        with patch('azure.mgmt.compute.ComputeManagementClient'):
            with patch('azure.mgmt.storage.StorageManagementClient'):
                with patch('azure.mgmt.sql.SqlManagementClient'):
                    with patch('azure.mgmt.resource.ResourceManagementClient'):
                        azure = azure_cli.AzureResourceManager()
                        
                        # Mock the list methods
                        azure.vm_list = MagicMock(return_value=[{'name': 'test-vm'}])
                        azure.storage_list_accounts = MagicMock(return_value=[])
                        azure.sql_list_servers = MagicMock(return_value=[])
                        azure.group_list = MagicMock(return_value=[])
                        
                        results = azure.search_resources('test')
                        
                        self.assertIn('vm', results)
                        self.assertIn('storage', results)
                        self.assertIn('sql', results)
                        self.assertIn('groups', results)


class TestCLI(unittest.TestCase):
    """Test Command Line Interface"""
    
    @patch('main.AzureResourceManager')
    def test_cli_help(self, mock_azure):
        """Test CLI help output"""
        with patch('sys.argv', ['main.py', '--help']):
            with self.assertRaises(SystemExit) as cm:
                azure_cli.main()
            self.assertEqual(cm.exception.code, 0)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestAzureResourceManager))
    suite.addTests(loader.loadTestsFromTestCase(TestCLI))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
