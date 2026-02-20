#!/usr/bin/env python3
"""
Azure CLI Skill - Azure Cloud Operations Assistant
Supports VM, Storage, SQL Database operations
"""

import argparse
import json
import sys
from typing import Optional, List, Dict, Any

try:
    from azure.identity import DefaultAzureCredential, ClientSecretCredential
    from azure.mgmt.compute import ComputeManagementClient
    from azure.mgmt.storage import StorageManagementClient
    from azure.mgmt.sql import SqlManagementClient
    from azure.mgmt.resource import ResourceManagementClient
    from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
except ImportError as e:
    print(f"Error: Azure SDK not installed. Run: pip install azure-identity azure-mgmt-compute azure-mgmt-storage azure-mgmt-sql azure-mgmt-resource")
    sys.exit(1)

import os


class AzureResourceManager:
    """Unified Azure Resource Manager for multiple services"""
    
    def __init__(self, subscription_id: Optional[str] = None):
        self.subscription_id = subscription_id or os.environ.get('AZURE_SUBSCRIPTION_ID')
        if not self.subscription_id:
            print("Error: Azure subscription ID required. Set AZURE_SUBSCRIPTION_ID environment variable.")
            sys.exit(1)
        
        self.credential = self._get_credential()
        self._init_clients()
    
    def _get_credential(self):
        """Get Azure credentials from environment or default chain"""
        try:
            # Try service principal first
            client_id = os.environ.get('AZURE_CLIENT_ID')
            client_secret = os.environ.get('AZURE_CLIENT_SECRET')
            tenant_id = os.environ.get('AZURE_TENANT_ID')
            
            if client_id and client_secret and tenant_id:
                return ClientSecretCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client_secret=client_secret
                )
            
            # Fall back to default credential chain
            return DefaultAzureCredential()
        except Exception as e:
            print(f"Error getting Azure credentials: {e}")
            sys.exit(1)
    
    def _init_clients(self):
        """Initialize Azure management clients"""
        self.compute_client = ComputeManagementClient(self.credential, self.subscription_id)
        self.storage_client = StorageManagementClient(self.credential, self.subscription_id)
        self.sql_client = SqlManagementClient(self.credential, self.subscription_id)
        self.resource_client = ResourceManagementClient(self.credential, self.subscription_id)
    
    # ==================== VM Operations ====================
    
    def vm_list(self, resource_group: Optional[str] = None) -> List[Dict]:
        """List virtual machines"""
        try:
            vms = []
            if resource_group:
                vm_list = self.compute_client.virtual_machines.list(resource_group)
            else:
                vm_list = self.compute_client.virtual_machines.list_all()
            
            for vm in vm_list:
                vm_info = {
                    'name': vm.name,
                    'id': vm.id,
                    'type': vm.type,
                    'location': vm.location,
                    'resource_group': vm.id.split('/')[4] if vm.id else 'N/A',
                    'vm_size': vm.hardware_profile.vm_size if vm.hardware_profile else 'N/A',
                    'os_type': vm.storage_profile.os_disk.os_type if vm.storage_profile and vm.storage_profile.os_disk else 'N/A',
                    'provisioning_state': vm.provisioning_state
                }
                vms.append(vm_info)
            return vms
        except Exception as e:
            print(f"Error listing VMs: {e}")
            return []
    
    def vm_get(self, resource_group: str, name: str) -> Optional[Dict]:
        """Get VM details"""
        try:
            vm = self.compute_client.virtual_machines.get(resource_group, name)
            instance_view = self.compute_client.virtual_machines.instance_view(resource_group, name)
            
            power_state = 'Unknown'
            for status in instance_view.statuses or []:
                if status.code and status.code.startswith('PowerState/'):
                    power_state = status.code.split('/')[-1]
            
            return {
                'name': vm.name,
                'id': vm.id,
                'location': vm.location,
                'vm_size': vm.hardware_profile.vm_size,
                'os_type': vm.storage_profile.os_disk.os_type,
                'power_state': power_state,
                'provisioning_state': vm.provisioning_state,
                'network_interfaces': [nic.id for nic in vm.network_profile.network_interfaces] if vm.network_profile else []
            }
        except ResourceNotFoundError:
            print(f"VM not found: {name}")
            return None
        except Exception as e:
            print(f"Error getting VM: {e}")
            return None
    
    def vm_start(self, resource_group: str, name: str) -> bool:
        """Start a virtual machine"""
        try:
            print(f"Starting VM: {name}...")
            poller = self.compute_client.virtual_machines.begin_start(resource_group, name)
            poller.result()
            print(f"VM {name} started successfully")
            return True
        except Exception as e:
            print(f"Error starting VM: {e}")
            return False
    
    def vm_stop(self, resource_group: str, name: str, deallocate: bool = True) -> bool:
        """Stop a virtual machine"""
        try:
            if deallocate:
                print(f"Deallocating VM: {name}...")
                poller = self.compute_client.virtual_machines.begin_deallocate(resource_group, name)
            else:
                print(f"Stopping VM: {name}...")
                poller = self.compute_client.virtual_machines.begin_power_off(resource_group, name)
            poller.result()
            print(f"VM {name} stopped successfully")
            return True
        except Exception as e:
            print(f"Error stopping VM: {e}")
            return False
    
    def vm_restart(self, resource_group: str, name: str) -> bool:
        """Restart a virtual machine"""
        try:
            print(f"Restarting VM: {name}...")
            poller = self.compute_client.virtual_machines.begin_restart(resource_group, name)
            poller.result()
            print(f"VM {name} restarted successfully")
            return True
        except Exception as e:
            print(f"Error restarting VM: {e}")
            return False
    
    def vm_create(self, resource_group: str, name: str, location: str, vm_size: str,
                  admin_username: str, admin_password: str, image: str = 'UbuntuLTS') -> bool:
        """Create a new virtual machine"""
        try:
            from azure.mgmt.compute.models import (
                HardwareProfile, StorageProfile, OSProfile, NetworkProfile,
                NetworkInterfaceReference, OSDisk, ManagedDiskParameters, DiskCreateOptionTypes
            )
            
            print(f"Creating VM: {name}...")
            
            # VM parameters
            vm_params = {
                'location': location,
                'hardware_profile': HardwareProfile(vm_size=vm_size),
                'storage_profile': StorageProfile(
                    image_reference=self._get_image_reference(image),
                    os_disk=OSDisk(
                        create_option=DiskCreateOptionTypes.from_image,
                        managed_disk=ManagedDiskParameters(storage_account_type='Standard_LRS')
                    )
                ),
                'os_profile': OSProfile(
                    computer_name=name,
                    admin_username=admin_username,
                    admin_password=admin_password
                )
            }
            
            poller = self.compute_client.virtual_machines.begin_create_or_update(
                resource_group, name, vm_params
            )
            vm = poller.result()
            print(f"VM created: {vm.id}")
            return True
        except Exception as e:
            print(f"Error creating VM: {e}")
            return False
    
    def vm_delete(self, resource_group: str, name: str) -> bool:
        """Delete a virtual machine"""
        try:
            print(f"Deleting VM: {name}...")
            poller = self.compute_client.virtual_machines.begin_delete(resource_group, name)
            poller.result()
            print(f"VM {name} deleted successfully")
            return True
        except Exception as e:
            print(f"Error deleting VM: {e}")
            return False
    
    def _get_image_reference(self, image: str):
        """Get image reference for common images"""
        from azure.mgmt.compute.models import ImageReference
        
        images = {
            'UbuntuLTS': ImageReference(
                publisher='Canonical',
                offer='UbuntuServer',
                sku='18.04-LTS',
                version='latest'
            ),
            'WindowsServer': ImageReference(
                publisher='MicrosoftWindowsServer',
                offer='WindowsServer',
                sku='2019-Datacenter',
                version='latest'
            ),
            'Debian': ImageReference(
                publisher='Debian',
                offer='debian-10',
                sku='10',
                version='latest'
            )
        }
        return images.get(image, images['UbuntuLTS'])
    
    # ==================== Storage Operations ====================
    
    def storage_list_accounts(self) -> List[Dict]:
        """List storage accounts"""
        try:
            accounts = []
            for acct in self.storage_client.storage_accounts.list():
                accounts.append({
                    'name': acct.name,
                    'id': acct.id,
                    'location': acct.location,
                    'resource_group': acct.id.split('/')[4] if acct.id else 'N/A',
                    'sku': acct.sku.name if acct.sku else 'N/A',
                    'kind': acct.kind,
                    'primary_endpoint': acct.primary_endpoints.blob if acct.primary_endpoints else None
                })
            return accounts
        except Exception as e:
            print(f"Error listing storage accounts: {e}")
            return []
    
    def storage_create_account(self, resource_group: str, name: str, location: str,
                               sku: str = 'Standard_LRS', kind: str = 'StorageV2') -> bool:
        """Create storage account"""
        try:
            from azure.mgmt.storage.models import StorageAccountCreateParameters, Sku
            
            print(f"Creating storage account: {name}...")
            
            params = StorageAccountCreateParameters(
                location=location,
                sku=Sku(name=sku),
                kind=kind
            )
            
            poller = self.storage_client.storage_accounts.begin_create(
                resource_group, name, params
            )
            account = poller.result()
            print(f"Storage account created: {account.id}")
            return True
        except Exception as e:
            print(f"Error creating storage account: {e}")
            return False
    
    def storage_delete_account(self, resource_group: str, name: str) -> bool:
        """Delete storage account"""
        try:
            print(f"Deleting storage account: {name}...")
            self.storage_client.storage_accounts.delete(resource_group, name)
            print(f"Storage account {name} deleted")
            return True
        except Exception as e:
            print(f"Error deleting storage account: {e}")
            return False
    
    def storage_list_containers(self, resource_group: str, account_name: str) -> List[Dict]:
        """List storage containers"""
        try:
            containers = []
            for container in self.storage_client.blob_containers.list(resource_group, account_name):
                containers.append({
                    'name': container.name,
                    'last_modified': container.last_modified_time.isoformat() if container.last_modified_time else None,
                    'lease_status': container.lease_status
                })
            return containers
        except Exception as e:
            print(f"Error listing containers: {e}")
            return []
    
    def storage_create_container(self, resource_group: str, account_name: str, 
                                 container_name: str, public_access: str = 'None') -> bool:
        """Create storage container"""
        try:
            from azure.mgmt.storage.models import BlobContainer
            
            self.storage_client.blob_containers.create(
                resource_group, account_name, container_name, BlobContainer()
            )
            print(f"Container created: {container_name}")
            return True
        except Exception as e:
            print(f"Error creating container: {e}")
            return False
    
    def storage_upload_blob(self, connection_string: str, container: str, 
                           file_path: str, blob_name: Optional[str] = None) -> bool:
        """Upload file to blob storage"""
        try:
            from azure.storage.blob import BlobServiceClient
            
            blob_service = BlobServiceClient.from_connection_string(connection_string)
            blob_client = blob_service.get_blob_client(container=container, blob=blob_name or os.path.basename(file_path))
            
            with open(file_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True)
            
            print(f"Uploaded {file_path} to {container}/{blob_name}")
            return True
        except Exception as e:
            print(f"Error uploading blob: {e}")
            return False
    
    def storage_download_blob(self, connection_string: str, container: str,
                             blob_name: str, file_path: str) -> bool:
        """Download blob from storage"""
        try:
            from azure.storage.blob import BlobServiceClient
            
            blob_service = BlobServiceClient.from_connection_string(connection_string)
            blob_client = blob_service.get_blob_client(container=container, blob=blob_name)
            
            with open(file_path, 'wb') as download_file:
                download_file.write(blob_client.download_blob().readall())
            
            print(f"Downloaded {container}/{blob_name} to {file_path}")
            return True
        except Exception as e:
            print(f"Error downloading blob: {e}")
            return False
    
    # ==================== SQL Database Operations ====================
    
    def sql_list_servers(self, resource_group: Optional[str] = None) -> List[Dict]:
        """List SQL servers"""
        try:
            servers = []
            if resource_group:
                server_list = self.sql_client.servers.list_by_resource_group(resource_group)
            else:
                server_list = self.sql_client.servers.list()
            
            for server in server_list:
                servers.append({
                    'name': server.name,
                    'id': server.id,
                    'location': server.location,
                    'resource_group': server.id.split('/')[4] if server.id else 'N/A',
                    'fully_qualified_domain_name': server.fully_qualified_domain_name,
                    'administrator_login': server.administrator_login,
                    'version': server.version
                })
            return servers
        except Exception as e:
            print(f"Error listing SQL servers: {e}")
            return []
    
    def sql_create_server(self, resource_group: str, name: str, location: str,
                         admin_user: str, admin_pass: str, version: str = '12.0') -> bool:
        """Create SQL server"""
        try:
            from azure.mgmt.sql.models import Server
            
            print(f"Creating SQL server: {name}...")
            
            server_params = Server(
                location=location,
                administrator_login=admin_user,
                administrator_login_password=admin_pass,
                version=version
            )
            
            poller = self.sql_client.servers.begin_create_or_update(
                resource_group, name, server_params
            )
            server = poller.result()
            print(f"SQL server created: {server.fully_qualified_domain_name}")
            return True
        except Exception as e:
            print(f"Error creating SQL server: {e}")
            return False
    
    def sql_delete_server(self, resource_group: str, name: str) -> bool:
        """Delete SQL server"""
        try:
            print(f"Deleting SQL server: {name}...")
            self.sql_client.servers.delete(resource_group, name)
            print(f"SQL server {name} deleted")
            return True
        except Exception as e:
            print(f"Error deleting SQL server: {e}")
            return False
    
    def sql_list_databases(self, resource_group: str, server_name: str) -> List[Dict]:
        """List databases in a SQL server"""
        try:
            databases = []
            for db in self.sql_client.databases.list_by_server(resource_group, server_name):
                databases.append({
                    'name': db.name,
                    'id': db.id,
                    'status': db.status,
                    'collation': db.collation,
                    'max_size_gb': db.max_size_gb
                })
            return databases
        except Exception as e:
            print(f"Error listing databases: {e}")
            return []
    
    def sql_create_database(self, resource_group: str, server_name: str, name: str,
                           sku_name: str = 'Basic', max_size_gb: int = 2) -> bool:
        """Create SQL database"""
        try:
            from azure.mgmt.sql.models import Database, Sku as SqlSku
            
            print(f"Creating database: {name}...")
            
            db_params = Database(
                location=self.sql_client.servers.get(resource_group, server_name).location,
                sku=SqlSku(name=sku_name),
                max_size_gb=max_size_gb
            )
            
            poller = self.sql_client.databases.begin_create_or_update(
                resource_group, server_name, name, db_params
            )
            db = poller.result()
            print(f"Database created: {db.name}")
            return True
        except Exception as e:
            print(f"Error creating database: {e}")
            return False
    
    def sql_delete_database(self, resource_group: str, server_name: str, name: str) -> bool:
        """Delete SQL database"""
        try:
            print(f"Deleting database: {name}...")
            self.sql_client.databases.delete(resource_group, server_name, name)
            print(f"Database {name} deleted")
            return True
        except Exception as e:
            print(f"Error deleting database: {e}")
            return False
    
    # ==================== Resource Group Operations ====================
    
    def group_list(self) -> List[Dict]:
        """List resource groups"""
        try:
            groups = []
            for group in self.resource_client.resource_groups.list():
                groups.append({
                    'name': group.name,
                    'id': group.id,
                    'location': group.location,
                    'managed_by': group.managed_by,
                    'provisioning_state': group.properties.provisioning_state if group.properties else None
                })
            return groups
        except Exception as e:
            print(f"Error listing resource groups: {e}")
            return []
    
    def group_create(self, name: str, location: str, tags: Optional[Dict] = None) -> bool:
        """Create resource group"""
        try:
            from azure.mgmt.resource.resources.models import ResourceGroup
            
            print(f"Creating resource group: {name}...")
            group = self.resource_client.resource_groups.create_or_update(
                name, ResourceGroup(location=location, tags=tags or {})
            )
            print(f"Resource group created: {group.id}")
            return True
        except Exception as e:
            print(f"Error creating resource group: {e}")
            return False
    
    def group_delete(self, name: str) -> bool:
        """Delete resource group"""
        try:
            print(f"Deleting resource group: {name}...")
            poller = self.resource_client.resource_groups.begin_delete(name)
            poller.result()
            print(f"Resource group {name} deleted")
            return True
        except Exception as e:
            print(f"Error deleting resource group: {e}")
            return False
    
    def group_get_resources(self, name: str) -> List[Dict]:
        """Get resources in a resource group"""
        try:
            resources = []
            for res in self.resource_client.resources.list_by_resource_group(name):
                resources.append({
                    'name': res.name,
                    'id': res.id,
                    'type': res.type,
                    'location': res.location,
                    'kind': res.kind
                })
            return resources
        except Exception as e:
            print(f"Error listing resources: {e}")
            return []
    
    # ==================== Search Operations ====================
    
    def search_resources(self, query: str) -> Dict[str, List]:
        """Search resources across services"""
        results = {'vm': [], 'storage': [], 'sql': [], 'groups': []}
        query_lower = query.lower()
        
        # Search VMs
        try:
            for vm in self.vm_list():
                if query_lower in vm['name'].lower():
                    results['vm'].append(vm)
        except:
            pass
        
        # Search storage accounts
        try:
            for acct in self.storage_list_accounts():
                if query_lower in acct['name'].lower():
                    results['storage'].append(acct)
        except:
            pass
        
        # Search SQL servers
        try:
            for server in self.sql_list_servers():
                if query_lower in server['name'].lower():
                    results['sql'].append(server)
        except:
            pass
        
        # Search resource groups
        try:
            for group in self.group_list():
                if query_lower in group['name'].lower():
                    results['groups'].append(group)
        except:
            pass
        
        return results


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Azure CLI Skill - Cloud Operations Assistant',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--subscription', '-s', help='Azure subscription ID')
    parser.add_argument('--output', '-o', choices=['json', 'table'], default='json', help='Output format')
    
    subparsers = parser.add_subparsers(dest='service', help='Azure Service')
    
    # VM subcommands
    vm_parser = subparsers.add_parser('vm', help='VM operations')
    vm_subparsers = vm_parser.add_subparsers(dest='action')
    
    vm_list = vm_subparsers.add_parser('list', help='List VMs')
    vm_list.add_argument('--resource-group', '-g')
    
    vm_get = vm_subparsers.add_parser('get', help='Get VM details')
    vm_get.add_argument('--name', '-n', required=True)
    vm_get.add_argument('--resource-group', '-g', required=True)
    
    vm_start = vm_subparsers.add_parser('start', help='Start VM')
    vm_start.add_argument('--name', '-n', required=True)
    vm_start.add_argument('--resource-group', '-g', required=True)
    
    vm_stop = vm_subparsers.add_parser('stop', help='Stop VM')
    vm_stop.add_argument('--name', '-n', required=True)
    vm_stop.add_argument('--resource-group', '-g', required=True)
    vm_stop.add_argument('--deallocate', action='store_true', help='Deallocate VM')
    
    vm_restart = vm_subparsers.add_parser('restart', help='Restart VM')
    vm_restart.add_argument('--name', '-n', required=True)
    vm_restart.add_argument('--resource-group', '-g', required=True)
    
    vm_create = vm_subparsers.add_parser('create', help='Create VM')
    vm_create.add_argument('--name', '-n', required=True)
    vm_create.add_argument('--resource-group', '-g', required=True)
    vm_create.add_argument('--location', '-l', required=True)
    vm_create.add_argument('--size', default='Standard_B1s')
    vm_create.add_argument('--admin-user', '-u', required=True)
    vm_create.add_argument('--admin-pass', '-p', required=True)
    vm_create.add_argument('--image', '-i', default='UbuntuLTS', choices=['UbuntuLTS', 'WindowsServer', 'Debian'])
    
    vm_delete = vm_subparsers.add_parser('delete', help='Delete VM')
    vm_delete.add_argument('--name', '-n', required=True)
    vm_delete.add_argument('--resource-group', '-g', required=True)
    
    # Storage subcommands
    storage_parser = subparsers.add_parser('storage', help='Storage operations')
    storage_subparsers = storage_parser.add_subparsers(dest='action')
    
    storage_list = storage_subparsers.add_parser('list', help='List storage accounts')
    
    storage_create = storage_subparsers.add_parser('create', help='Create storage account')
    storage_create.add_argument('--name', '-n', required=True)
    storage_create.add_argument('--resource-group', '-g', required=True)
    storage_create.add_argument('--location', '-l', required=True)
    storage_create.add_argument('--sku', default='Standard_LRS', choices=['Standard_LRS', 'Standard_GRS', 'Premium_LRS'])
    
    storage_delete = storage_subparsers.add_parser('delete', help='Delete storage account')
    storage_delete.add_argument('--name', '-n', required=True)
    storage_delete.add_argument('--resource-group', '-g', required=True)
    
    storage_containers = storage_subparsers.add_parser('containers', help='List containers')
    storage_containers.add_argument('--account', '-a', required=True)
    storage_containers.add_argument('--resource-group', '-g', required=True)
    
    storage_upload = storage_subparsers.add_parser('upload', help='Upload blob')
    storage_upload.add_argument('--connection-string', '-c', required=True)
    storage_upload.add_argument('--container', required=True)
    storage_upload.add_argument('--file', '-f', required=True)
    storage_upload.add_argument('--blob', '-b')
    
    storage_download = storage_subparsers.add_parser('download', help='Download blob')
    storage_download.add_argument('--connection-string', '-c', required=True)
    storage_download.add_argument('--container', required=True)
    storage_download.add_argument('--blob', '-b', required=True)
    storage_download.add_argument('--file', '-f', required=True)
    
    # SQL subcommands
    sql_parser = subparsers.add_parser('sql', help='SQL Database operations')
    sql_subparsers = sql_parser.add_subparsers(dest='action')
    
    sql_list_servers = sql_subparsers.add_parser('list-servers', help='List SQL servers')
    sql_list_servers.add_argument('--resource-group', '-g')
    
    sql_create_server = sql_subparsers.add_parser('create-server', help='Create SQL server')
    sql_create_server.add_argument('--name', '-n', required=True)
    sql_create_server.add_argument('--resource-group', '-g', required=True)
    sql_create_server.add_argument('--location', '-l', required=True)
    sql_create_server.add_argument('--admin-user', '-u', required=True)
    sql_create_server.add_argument('--admin-pass', '-p', required=True)
    
    sql_delete_server = sql_subparsers.add_parser('delete-server', help='Delete SQL server')
    sql_delete_server.add_argument('--name', '-n', required=True)
    sql_delete_server.add_argument('--resource-group', '-g', required=True)
    
    sql_list_dbs = sql_subparsers.add_parser('list-dbs', help='List databases')
    sql_list_dbs.add_argument('--server', '-s', required=True)
    sql_list_dbs.add_argument('--resource-group', '-g', required=True)
    
    sql_create_db = sql_subparsers.add_parser('create-db', help='Create database')
    sql_create_db.add_argument('--name', '-n', required=True)
    sql_create_db.add_argument('--server', '-s', required=True)
    sql_create_db.add_argument('--resource-group', '-g', required=True)
    sql_create_db.add_argument('--sku', default='Basic')
    
    sql_delete_db = sql_subparsers.add_parser('delete-db', help='Delete database')
    sql_delete_db.add_argument('--name', '-n', required=True)
    sql_delete_db.add_argument('--server', '-s', required=True)
    sql_delete_db.add_argument('--resource-group', '-g', required=True)
    
    # Resource Group subcommands
    group_parser = subparsers.add_parser('group', help='Resource Group operations')
    group_subparsers = group_parser.add_subparsers(dest='action')
    
    group_list = group_subparsers.add_parser('list', help='List resource groups')
    
    group_create = group_subparsers.add_parser('create', help='Create resource group')
    group_create.add_argument('--name', '-n', required=True)
    group_create.add_argument('--location', '-l', required=True)
    
    group_delete = group_subparsers.add_parser('delete', help='Delete resource group')
    group_delete.add_argument('--name', '-n', required=True)
    
    group_resources = group_subparsers.add_parser('resources', help='List group resources')
    group_resources.add_argument('--name', '-n', required=True)
    
    # Search subcommand
    search_parser = subparsers.add_parser('search', help='Search resources')
    search_parser.add_argument('query', help='Search query')
    
    args = parser.parse_args()
    
    if not args.service:
        parser.print_help()
        return
    
    # Initialize Azure manager
    azure = AzureResourceManager(subscription_id=args.subscription)
    
    # Execute commands
    if args.service == 'vm':
        if args.action == 'list':
            vms = azure.vm_list(args.resource_group)
            print(json.dumps(vms, indent=2))
        elif args.action == 'get':
            vm = azure.vm_get(args.resource_group, args.name)
            print(json.dumps(vm, indent=2))
        elif args.action == 'start':
            azure.vm_start(args.resource_group, args.name)
        elif args.action == 'stop':
            azure.vm_stop(args.resource_group, args.name, deallocate=args.deallocate)
        elif args.action == 'restart':
            azure.vm_restart(args.resource_group, args.name)
        elif args.action == 'create':
            azure.vm_create(args.resource_group, args.name, args.location, args.size,
                          args.admin_user, args.admin_pass, args.image)
        elif args.action == 'delete':
            azure.vm_delete(args.resource_group, args.name)
    
    elif args.service == 'storage':
        if args.action == 'list':
            accounts = azure.storage_list_accounts()
            print(json.dumps(accounts, indent=2))
        elif args.action == 'create':
            azure.storage_create_account(args.resource_group, args.name, args.location, args.sku)
        elif args.action == 'delete':
            azure.storage_delete_account(args.resource_group, args.name)
        elif args.action == 'containers':
            containers = azure.storage_list_containers(args.resource_group, args.account)
            print(json.dumps(containers, indent=2))
        elif args.action == 'upload':
            azure.storage_upload_blob(args.connection_string, args.container, args.file, args.blob)
        elif args.action == 'download':
            azure.storage_download_blob(args.connection_string, args.container, args.blob, args.file)
    
    elif args.service == 'sql':
        if args.action == 'list-servers':
            servers = azure.sql_list_servers(args.resource_group)
            print(json.dumps(servers, indent=2))
        elif args.action == 'create-server':
            azure.sql_create_server(args.resource_group, args.name, args.location, 
                                   args.admin_user, args.admin_pass)
        elif args.action == 'delete-server':
            azure.sql_delete_server(args.resource_group, args.name)
        elif args.action == 'list-dbs':
            dbs = azure.sql_list_databases(args.resource_group, args.server)
            print(json.dumps(dbs, indent=2))
        elif args.action == 'create-db':
            azure.sql_create_database(args.resource_group, args.server, args.name, args.sku)
        elif args.action == 'delete-db':
            azure.sql_delete_database(args.resource_group, args.server, args.name)
    
    elif args.service == 'group':
        if args.action == 'list':
            groups = azure.group_list()
            print(json.dumps(groups, indent=2))
        elif args.action == 'create':
            azure.group_create(args.name, args.location)
        elif args.action == 'delete':
            azure.group_delete(args.name)
        elif args.action == 'resources':
            resources = azure.group_get_resources(args.name)
            print(json.dumps(resources, indent=2))
    
    elif args.service == 'search':
        results = azure.search_resources(args.query)
        print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
