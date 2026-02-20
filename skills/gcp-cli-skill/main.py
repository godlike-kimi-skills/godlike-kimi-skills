#!/usr/bin/env python3
"""
GCP CLI Skill - Google Cloud Platform Operations Assistant
Supports Compute Engine, Cloud Storage, BigQuery operations
"""

import argparse
import json
import sys
import os
from typing import Optional, List, Dict, Any

try:
    from google.cloud import compute_v1, storage, bigquery
    from google.api_core.extended_operation import ExtendedOperation
    from google.api_core.exceptions import NotFound, GoogleAPICallError
except ImportError as e:
    print(f"Error: Google Cloud SDK not installed. Run: pip install google-cloud-compute google-cloud-storage google-cloud-bigquery")
    sys.exit(1)


class GCPResourceManager:
    """Unified GCP Resource Manager for multiple services"""
    
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.environ.get('GOOGLE_CLOUD_PROJECT') or os.environ.get('GCP_PROJECT_ID')
        if not self.project_id:
            print("Error: GCP project ID required. Set GOOGLE_CLOUD_PROJECT or GCP_PROJECT_ID environment variable.")
            sys.exit(1)
        
        self._init_clients()
    
    def _init_clients(self):
        """Initialize GCP service clients"""
        try:
            self.compute_client = compute_v1.InstancesClient()
            self.zones_client = compute_v1.ZonesClient()
            self.machine_types_client = compute_v1.MachineTypesClient()
            self.images_client = compute_v1.ImagesClient()
            self.storage_client = storage.Client()
            self.bigquery_client = bigquery.Client()
        except Exception as e:
            print(f"Error initializing GCP clients: {e}")
            sys.exit(1)
    
    # ==================== Compute Engine Operations ====================
    
    def compute_list_instances(self, zone: Optional[str] = None) -> List[Dict]:
        """List Compute Engine instances"""
        try:
            instances = []
            
            if zone:
                request = compute_v1.ListInstancesRequest(project=self.project_id, zone=zone)
                response = self.compute_client.list(request=request)
                for instance in response:
                    instances.append(self._format_instance(instance, zone))
            else:
                # List from all zones
                zones_request = compute_v1.ListZonesRequest(project=self.project_id)
                zones = self.zones_client.list(request=zones_request)
                
                for zone_obj in zones:
                    request = compute_v1.ListInstancesRequest(
                        project=self.project_id, zone=zone_obj.name
                    )
                    response = self.compute_client.list(request=request)
                    for instance in response:
                        instances.append(self._format_instance(instance, zone_obj.name))
            
            return instances
        except GoogleAPICallError as e:
            print(f"Error listing instances: {e}")
            return []
    
    def _format_instance(self, instance, zone: str) -> Dict:
        """Format instance data for output"""
        network_ip = ''
        external_ip = ''
        
        if instance.network_interfaces:
            network_ip = instance.network_interfaces[0].network_i_p
            if instance.network_interfaces[0].access_configs:
                external_ip = instance.network_interfaces[0].access_configs[0].nat_i_p
        
        return {
            'name': instance.name,
            'id': str(instance.id),
            'zone': zone,
            'machine_type': instance.machine_type.split('/')[-1] if instance.machine_type else 'N/A',
            'status': instance.status,
            'internal_ip': network_ip,
            'external_ip': external_ip,
            'cpu_platform': instance.cpu_platform,
            'creation_timestamp': instance.creation_timestamp
        }
    
    def compute_get_instance(self, name: str, zone: str) -> Optional[Dict]:
        """Get Compute Engine instance details"""
        try:
            request = compute_v1.GetInstanceRequest(
                project=self.project_id, zone=zone, instance=name
            )
            instance = self.compute_client.get(request=request)
            return self._format_instance(instance, zone)
        except NotFound:
            print(f"Instance not found: {name}")
            return None
        except GoogleAPICallError as e:
            print(f"Error getting instance: {e}")
            return None
    
    def compute_start_instance(self, name: str, zone: str) -> bool:
        """Start a Compute Engine instance"""
        try:
            print(f"Starting instance: {name}...")
            request = compute_v1.StartInstanceRequest(
                project=self.project_id, zone=zone, instance=name
            )
            operation = self.compute_client.start(request=request)
            self._wait_for_zone_operation(operation, zone)
            print(f"Instance {name} started successfully")
            return True
        except GoogleAPICallError as e:
            print(f"Error starting instance: {e}")
            return False
    
    def compute_stop_instance(self, name: str, zone: str) -> bool:
        """Stop a Compute Engine instance"""
        try:
            print(f"Stopping instance: {name}...")
            request = compute_v1.StopInstanceRequest(
                project=self.project_id, zone=zone, instance=name
            )
            operation = self.compute_client.stop(request=request)
            self._wait_for_zone_operation(operation, zone)
            print(f"Instance {name} stopped successfully")
            return True
        except GoogleAPICallError as e:
            print(f"Error stopping instance: {e}")
            return False
    
    def compute_reset_instance(self, name: str, zone: str) -> bool:
        """Reset a Compute Engine instance"""
        try:
            print(f"Resetting instance: {name}...")
            request = compute_v1.ResetInstanceRequest(
                project=self.project_id, zone=zone, instance=name
            )
            operation = self.compute_client.reset(request=request)
            self._wait_for_zone_operation(operation, zone)
            print(f"Instance {name} reset successfully")
            return True
        except GoogleAPICallError as e:
            print(f"Error resetting instance: {e}")
            return False
    
    def compute_delete_instance(self, name: str, zone: str) -> bool:
        """Delete a Compute Engine instance"""
        try:
            print(f"Deleting instance: {name}...")
            request = compute_v1.DeleteInstanceRequest(
                project=self.project_id, zone=zone, instance=name
            )
            operation = self.compute_client.delete(request=request)
            self._wait_for_zone_operation(operation, zone)
            print(f"Instance {name} deleted successfully")
            return True
        except GoogleAPICallError as e:
            print(f"Error deleting instance: {e}")
            return False
    
    def compute_create_instance(self, name: str, zone: str, machine_type: str = 'e2-medium',
                               source_image: str = 'projects/debian-cloud/global/images/family/debian-11',
                               network: str = 'global/networks/default', 
                               startup_script: Optional[str] = None) -> bool:
        """Create a new Compute Engine instance"""
        try:
            print(f"Creating instance: {name}...")
            
            # Get machine type
            machine_type_url = f"zones/{zone}/machineTypes/{machine_type}"
            
            # Configure the boot disk
            boot_disk = compute_v1.AttachedDisk(
                boot=True,
                auto_delete=True,
                initialize_params=compute_v1.AttachedDiskInitializeParams(
                    source_image=source_image
                )
            )
            
            # Configure the network interface
            network_interface = compute_v1.NetworkInterface(
                name=network.split('/')[-1]
            )
            
            # Configure instance metadata
            metadata = None
            if startup_script:
                metadata = compute_v1.Metadata(
                    items=[compute_v1.Items(key='startup-script', value=startup_script)]
                )
            
            # Create instance
            instance = compute_v1.Instance(
                name=name,
                machine_type=machine_type_url,
                disks=[boot_disk],
                network_interfaces=[network_interface],
                metadata=metadata
            )
            
            request = compute_v1.InsertInstanceRequest(
                project=self.project_id, zone=zone, instance_resource=instance
            )
            operation = self.compute_client.insert(request=request)
            self._wait_for_zone_operation(operation, zone)
            
            print(f"Instance {name} created successfully")
            return True
        except GoogleAPICallError as e:
            print(f"Error creating instance: {e}")
            return False
    
    def compute_list_zones(self) -> List[Dict]:
        """List available zones"""
        try:
            request = compute_v1.ListZonesRequest(project=self.project_id)
            zones = self.zones_client.list(request=request)
            
            return [{
                'name': zone.name,
                'region': zone.region.split('/')[-1],
                'status': zone.status,
                'available_machine_types': [mt.split('/')[-1] for mt in zone.available_machine_types[:10]]
            } for zone in zones]
        except GoogleAPICallError as e:
            print(f"Error listing zones: {e}")
            return []
    
    def compute_list_machine_types(self, zone: str) -> List[Dict]:
        """List available machine types"""
        try:
            request = compute_v1.ListMachineTypesRequest(
                project=self.project_id, zone=zone
            )
            types = self.machine_types_client.list(request=request)
            
            return [{
                'name': mt.name,
                'guest_cpus': mt.guest_cpus,
                'memory_mb': mt.memory_mb,
                'description': mt.description
            } for mt in types]
        except GoogleAPICallError as e:
            print(f"Error listing machine types: {e}")
            return []
    
    def _wait_for_zone_operation(self, operation, zone: str):
        """Wait for zone operation to complete"""
        from google.cloud.compute_v1.services.zone_operations import ZoneOperationsClient
        
        op_client = ZoneOperationsClient()
        while operation.status != compute_v1.Operation.Status.DONE:
            request = compute_v1.GetZoneOperationRequest(
                project=self.project_id, zone=zone, operation=operation.name
            )
            operation = op_client.get(request=request)
    
    # ==================== Cloud Storage Operations ====================
    
    def storage_list_buckets(self) -> List[Dict]:
        """List Cloud Storage buckets"""
        try:
            buckets = []
            for bucket in self.storage_client.list_buckets():
                buckets.append({
                    'name': bucket.name,
                    'id': bucket.id,
                    'location': bucket.location,
                    'storage_class': bucket.storage_class,
                    'created': bucket.time_created.isoformat() if bucket.time_created else None,
                    'versioning_enabled': bucket.versioning_enabled
                })
            return buckets
        except GoogleAPICallError as e:
            print(f"Error listing buckets: {e}")
            return []
    
    def storage_get_bucket(self, name: str) -> Optional[Dict]:
        """Get bucket details"""
        try:
            bucket = self.storage_client.get_bucket(name)
            return {
                'name': bucket.name,
                'id': bucket.id,
                'location': bucket.location,
                'storage_class': bucket.storage_class,
                'created': bucket.time_created.isoformat() if bucket.time_created else None,
                'versioning_enabled': bucket.versioning_enabled,
                'labels': bucket.labels,
                'lifecycle_rules': [str(rule) for rule in bucket.lifecycle_rules]
            }
        except NotFound:
            print(f"Bucket not found: {name}")
            return None
        except GoogleAPICallError as e:
            print(f"Error getting bucket: {e}")
            return None
    
    def storage_create_bucket(self, name: str, location: str = 'US', 
                             storage_class: str = 'STANDARD') -> bool:
        """Create Cloud Storage bucket"""
        try:
            print(f"Creating bucket: {name}...")
            bucket = self.storage_client.bucket(name)
            bucket.storage_class = storage_class
            new_bucket = self.storage_client.create_bucket(bucket, location=location)
            print(f"Bucket created: {new_bucket.name}")
            return True
        except GoogleAPICallError as e:
            print(f"Error creating bucket: {e}")
            return False
    
    def storage_delete_bucket(self, name: str, force: bool = False) -> bool:
        """Delete Cloud Storage bucket"""
        try:
            print(f"Deleting bucket: {name}...")
            bucket = self.storage_client.bucket(name)
            bucket.delete(force=force)
            print(f"Bucket {name} deleted")
            return True
        except GoogleAPICallError as e:
            print(f"Error deleting bucket: {e}")
            return False
    
    def storage_list_objects(self, bucket_name: str, prefix: str = '', 
                            max_results: int = 1000) -> List[Dict]:
        """List objects in bucket"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blobs = bucket.list_blobs(prefix=prefix, max_results=max_results)
            
            return [{
                'name': blob.name,
                'size': blob.size,
                'content_type': blob.content_type,
                'updated': blob.updated.isoformat() if blob.updated else None,
                'storage_class': blob.storage_class,
                'md5_hash': blob.md5_hash
            } for blob in blobs]
        except GoogleAPICallError as e:
            print(f"Error listing objects: {e}")
            return []
    
    def storage_upload_file(self, bucket_name: str, file_path: str, 
                           destination: Optional[str] = None) -> bool:
        """Upload file to bucket"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob_name = destination or os.path.basename(file_path)
            blob = bucket.blob(blob_name)
            
            print(f"Uploading {file_path} to gs://{bucket_name}/{blob_name}...")
            blob.upload_from_filename(file_path)
            print(f"Upload complete")
            return True
        except GoogleAPICallError as e:
            print(f"Error uploading file: {e}")
            return False
    
    def storage_download_file(self, bucket_name: str, source: str, 
                             file_path: str) -> bool:
        """Download file from bucket"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(source)
            
            print(f"Downloading gs://{bucket_name}/{source} to {file_path}...")
            blob.download_to_filename(file_path)
            print(f"Download complete")
            return True
        except GoogleAPICallError as e:
            print(f"Error downloading file: {e}")
            return False
    
    def storage_delete_object(self, bucket_name: str, object_name: str) -> bool:
        """Delete object from bucket"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(object_name)
            blob.delete()
            print(f"Deleted gs://{bucket_name}/{object_name}")
            return True
        except GoogleAPICallError as e:
            print(f"Error deleting object: {e}")
            return False
    
    def storage_get_signed_url(self, bucket_name: str, object_name: str, 
                               expiration: int = 3600) -> Optional[str]:
        """Generate signed URL for object"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(object_name)
            from datetime import timedelta
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(seconds=expiration),
                method="GET"
            )
            return url
        except GoogleAPICallError as e:
            print(f"Error generating signed URL: {e}")
            return None
    
    # ==================== BigQuery Operations ====================
    
    def bquery_list_datasets(self) -> List[Dict]:
        """List BigQuery datasets"""
        try:
            datasets = []
            for dataset in self.bigquery_client.list_datasets():
                datasets.append({
                    'dataset_id': dataset.dataset_id,
                    'project': dataset.project,
                    'location': dataset.location,
                    'created': dataset.created.isoformat() if dataset.created else None,
                    'modified': dataset.modified.isoformat() if dataset.modified else None,
                    'description': dataset.description
                })
            return datasets
        except GoogleAPICallError as e:
            print(f"Error listing datasets: {e}")
            return []
    
    def bquery_get_dataset(self, dataset_id: str) -> Optional[Dict]:
        """Get dataset details"""
        try:
            dataset = self.bigquery_client.get_dataset(dataset_id)
            return {
                'dataset_id': dataset.dataset_id,
                'project': dataset.project,
                'location': dataset.location,
                'created': dataset.created.isoformat() if dataset.created else None,
                'modified': dataset.modified.isoformat() if dataset.modified else None,
                'description': dataset.description,
                'labels': dataset.labels,
                'access_entries': [str(entry) for entry in dataset.access_entries]
            }
        except NotFound:
            print(f"Dataset not found: {dataset_id}")
            return None
        except GoogleAPICallError as e:
            print(f"Error getting dataset: {e}")
            return None
    
    def bquery_create_dataset(self, dataset_id: str, location: str = 'US',
                             description: Optional[str] = None) -> bool:
        """Create BigQuery dataset"""
        try:
            print(f"Creating dataset: {dataset_id}...")
            
            dataset = bigquery.Dataset(f"{self.project_id}.{dataset_id}")
            dataset.location = location
            if description:
                dataset.description = description
            
            dataset = self.bigquery_client.create_dataset(dataset)
            print(f"Dataset created: {dataset.dataset_id}")
            return True
        except GoogleAPICallError as e:
            print(f"Error creating dataset: {e}")
            return False
    
    def bquery_delete_dataset(self, dataset_id: str, delete_contents: bool = False) -> bool:
        """Delete BigQuery dataset"""
        try:
            print(f"Deleting dataset: {dataset_id}...")
            self.bigquery_client.delete_dataset(
                dataset_id, delete_contents=delete_contents, not_found_ok=True
            )
            print(f"Dataset {dataset_id} deleted")
            return True
        except GoogleAPICallError as e:
            print(f"Error deleting dataset: {e}")
            return False
    
    def bquery_list_tables(self, dataset_id: str) -> List[Dict]:
        """List tables in dataset"""
        try:
            tables = []
            for table in self.bigquery_client.list_tables(dataset_id):
                tables.append({
                    'table_id': table.table_id,
                    'dataset_id': table.dataset_id,
                    'project': table.project,
                    'table_type': table.table_type,
                    'created': table.created.isoformat() if table.created else None,
                    'expires': table.expires.isoformat() if table.expires else None,
                    'num_rows': table.num_rows,
                    'num_bytes': table.num_bytes
                })
            return tables
        except GoogleAPICallError as e:
            print(f"Error listing tables: {e}")
            return []
    
    def bquery_query(self, sql: str, max_results: int = 1000) -> List[Dict]:
        """Execute BigQuery SQL query"""
        try:
            print(f"Executing query...")
            query_job = self.bigquery_client.query(sql)
            results = query_job.result()
            
            rows = []
            for row in results:
                row_dict = {}
                for key in row.keys():
                    value = row[key]
                    # Handle datetime objects
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    row_dict[key] = value
                rows.append(row_dict)
            
            print(f"Query returned {len(rows)} rows")
            return rows
        except GoogleAPICallError as e:
            print(f"Error executing query: {e}")
            return []
    
    def bquery_create_table(self, dataset_id: str, table_id: str, 
                           schema: List[Dict]) -> bool:
        """Create BigQuery table"""
        try:
            print(f"Creating table: {dataset_id}.{table_id}...")
            
            table_ref = f"{self.project_id}.{dataset_id}.{table_id}"
            table = bigquery.Table(table_ref, schema=schema)
            table = self.bigquery_client.create_table(table)
            
            print(f"Table created: {table.table_id}")
            return True
        except GoogleAPICallError as e:
            print(f"Error creating table: {e}")
            return False
    
    def bquery_delete_table(self, dataset_id: str, table_id: str) -> bool:
        """Delete BigQuery table"""
        try:
            print(f"Deleting table: {dataset_id}.{table_id}...")
            self.bigquery_client.delete_table(f"{dataset_id}.{table_id}")
            print(f"Table deleted")
            return True
        except GoogleAPICallError as e:
            print(f"Error deleting table: {e}")
            return False
    
    # ==================== Search Operations ====================
    
    def search_resources(self, query: str) -> Dict[str, List]:
        """Search resources across services"""
        results = {'compute': [], 'storage': [], 'bigquery': []}
        query_lower = query.lower()
        
        # Search Compute instances
        try:
            for instance in self.compute_list_instances():
                if query_lower in instance['name'].lower():
                    results['compute'].append(instance)
        except:
            pass
        
        # Search Storage buckets
        try:
            for bucket in self.storage_list_buckets():
                if query_lower in bucket['name'].lower():
                    results['storage'].append(bucket)
        except:
            pass
        
        # Search BigQuery datasets
        try:
            for dataset in self.bquery_list_datasets():
                if query_lower in dataset['dataset_id'].lower():
                    results['bigquery'].append(dataset)
        except:
            pass
        
        return results


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='GCP CLI Skill - Google Cloud Operations Assistant',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--project', '-p', help='GCP project ID')
    parser.add_argument('--output', '-o', choices=['json', 'table'], default='json', help='Output format')
    
    subparsers = parser.add_subparsers(dest='service', help='GCP Service')
    
    # Compute subcommands
    compute_parser = subparsers.add_parser('compute', help='Compute Engine operations')
    compute_subparsers = compute_parser.add_subparsers(dest='action')
    
    compute_list = compute_subparsers.add_parser('list', help='List instances')
    compute_list.add_argument('--zone', '-z')
    
    compute_get = compute_subparsers.add_parser('get', help='Get instance details')
    compute_get.add_argument('--name', '-n', required=True)
    compute_get.add_argument('--zone', '-z', required=True)
    
    compute_start = compute_subparsers.add_parser('start', help='Start instance')
    compute_start.add_argument('--name', '-n', required=True)
    compute_start.add_argument('--zone', '-z', required=True)
    
    compute_stop = compute_subparsers.add_parser('stop', help='Stop instance')
    compute_stop.add_argument('--name', '-n', required=True)
    compute_stop.add_argument('--zone', '-z', required=True)
    
    compute_reset = compute_subparsers.add_parser('reset', help='Reset instance')
    compute_reset.add_argument('--name', '-n', required=True)
    compute_reset.add_argument('--zone', '-z', required=True)
    
    compute_create = compute_subparsers.add_parser('create', help='Create instance')
    compute_create.add_argument('--name', '-n', required=True)
    compute_create.add_argument('--zone', '-z', required=True)
    compute_create.add_argument('--machine-type', '-t', default='e2-medium')
    compute_create.add_argument('--image', '-i', default='projects/debian-cloud/global/images/family/debian-11')
    
    compute_delete = compute_subparsers.add_parser('delete', help='Delete instance')
    compute_delete.add_argument('--name', '-n', required=True)
    compute_delete.add_argument('--zone', '-z', required=True)
    
    compute_zones = compute_subparsers.add_parser('zones', help='List zones')
    compute_types = compute_subparsers.add_parser('types', help='List machine types')
    compute_types.add_argument('--zone', '-z', required=True)
    
    # Storage subcommands
    storage_parser = subparsers.add_parser('storage', help='Cloud Storage operations')
    storage_subparsers = storage_parser.add_subparsers(dest='action')
    
    storage_list = storage_subparsers.add_parser('list', help='List buckets')
    
    storage_get = storage_subparsers.add_parser('get', help='Get bucket details')
    storage_get.add_argument('--bucket', '-b', required=True)
    
    storage_create = storage_subparsers.add_parser('create', help='Create bucket')
    storage_create.add_argument('--bucket', '-b', required=True)
    storage_create.add_argument('--location', '-l', default='US')
    storage_create.add_argument('--storage-class', '-c', default='STANDARD')
    
    storage_delete = storage_subparsers.add_parser('delete', help='Delete bucket')
    storage_delete.add_argument('--bucket', '-b', required=True)
    storage_delete.add_argument('--force', action='store_true')
    
    storage_objects = storage_subparsers.add_parser('objects', help='List objects')
    storage_objects.add_argument('--bucket', '-b', required=True)
    storage_objects.add_argument('--prefix', '-p', default='')
    
    storage_upload = storage_subparsers.add_parser('upload', help='Upload file')
    storage_upload.add_argument('--bucket', '-b', required=True)
    storage_upload.add_argument('--file', '-f', required=True)
    storage_upload.add_argument('--destination', '-d')
    
    storage_download = storage_subparsers.add_parser('download', help='Download file')
    storage_download.add_argument('--bucket', '-b', required=True)
    storage_download.add_argument('--source', '-s', required=True)
    storage_download.add_argument('--file', '-f', required=True)
    
    storage_delete_obj = storage_subparsers.add_parser('delete-object', help='Delete object')
    storage_delete_obj.add_argument('--bucket', '-b', required=True)
    storage_delete_obj.add_argument('--object', '-o', required=True)
    
    storage_url = storage_subparsers.add_parser('url', help='Get signed URL')
    storage_url.add_argument('--bucket', '-b', required=True)
    storage_url.add_argument('--object', '-o', required=True)
    storage_url.add_argument('--expires', '-e', type=int, default=3600)
    
    # BigQuery subcommands
    bquery_parser = subparsers.add_parser('bquery', help='BigQuery operations')
    bquery_subparsers = bquery_parser.add_subparsers(dest='action')
    
    bquery_list_ds = bquery_subparsers.add_parser('list-datasets', help='List datasets')
    
    bquery_get_ds = bquery_subparsers.add_parser('get-dataset', help='Get dataset')
    bquery_get_ds.add_argument('--dataset', '-d', required=True)
    
    bquery_create_ds = bquery_subparsers.add_parser('create-dataset', help='Create dataset')
    bquery_create_ds.add_argument('--name', '-n', required=True)
    bquery_create_ds.add_argument('--location', '-l', default='US')
    bquery_create_ds.add_argument('--description', '-desc')
    
    bquery_delete_ds = bquery_subparsers.add_parser('delete-dataset', help='Delete dataset')
    bquery_delete_ds.add_argument('--dataset', '-d', required=True)
    bquery_delete_ds.add_argument('--delete-contents', action='store_true')
    
    bquery_list_tbl = bquery_subparsers.add_parser('list-tables', help='List tables')
    bquery_list_tbl.add_argument('--dataset', '-d', required=True)
    
    bquery_query = bquery_subparsers.add_parser('query', help='Execute query')
    bquery_query.add_argument('--sql', '-s', required=True)
    bquery_query.add_argument('--max-results', '-m', type=int, default=1000)
    
    bquery_delete_tbl = bquery_subparsers.add_parser('delete-table', help='Delete table')
    bquery_delete_tbl.add_argument('--dataset', '-d', required=True)
    bquery_delete_tbl.add_argument('--table', '-t', required=True)
    
    # Search subcommand
    search_parser = subparsers.add_parser('search', help='Search resources')
    search_parser.add_argument('query', help='Search query')
    
    args = parser.parse_args()
    
    if not args.service:
        parser.print_help()
        return
    
    # Initialize GCP manager
    gcp = GCPResourceManager(project_id=args.project)
    
    # Execute commands
    if args.service == 'compute':
        if args.action == 'list':
            instances = gcp.compute_list_instances(zone=args.zone)
            print(json.dumps(instances, indent=2))
        elif args.action == 'get':
            instance = gcp.compute_get_instance(args.name, args.zone)
            print(json.dumps(instance, indent=2))
        elif args.action == 'start':
            gcp.compute_start_instance(args.name, args.zone)
        elif args.action == 'stop':
            gcp.compute_stop_instance(args.name, args.zone)
        elif args.action == 'reset':
            gcp.compute_reset_instance(args.name, args.zone)
        elif args.action == 'create':
            gcp.compute_create_instance(args.name, args.zone, args.machine_type, args.image)
        elif args.action == 'delete':
            gcp.compute_delete_instance(args.name, args.zone)
        elif args.action == 'zones':
            zones = gcp.compute_list_zones()
            print(json.dumps(zones, indent=2))
        elif args.action == 'types':
            types = gcp.compute_list_machine_types(args.zone)
            print(json.dumps(types, indent=2))
    
    elif args.service == 'storage':
        if args.action == 'list':
            buckets = gcp.storage_list_buckets()
            print(json.dumps(buckets, indent=2))
        elif args.action == 'get':
            bucket = gcp.storage_get_bucket(args.bucket)
            print(json.dumps(bucket, indent=2))
        elif args.action == 'create':
            gcp.storage_create_bucket(args.bucket, args.location, args.storage_class)
        elif args.action == 'delete':
            gcp.storage_delete_bucket(args.bucket, args.force)
        elif args.action == 'objects':
            objects = gcp.storage_list_objects(args.bucket, args.prefix)
            print(json.dumps(objects, indent=2))
        elif args.action == 'upload':
            gcp.storage_upload_file(args.bucket, args.file, args.destination)
        elif args.action == 'download':
            gcp.storage_download_file(args.bucket, args.source, args.file)
        elif args.action == 'delete-object':
            gcp.storage_delete_object(args.bucket, args.object)
        elif args.action == 'url':
            url = gcp.storage_get_signed_url(args.bucket, args.object, args.expires)
            print(url)
    
    elif args.service == 'bquery':
        if args.action == 'list-datasets':
            datasets = gcp.bquery_list_datasets()
            print(json.dumps(datasets, indent=2))
        elif args.action == 'get-dataset':
            dataset = gcp.bquery_get_dataset(args.dataset)
            print(json.dumps(dataset, indent=2))
        elif args.action == 'create-dataset':
            gcp.bquery_create_dataset(args.name, args.location, args.description)
        elif args.action == 'delete-dataset':
            gcp.bquery_delete_dataset(args.dataset, args.delete_contents)
        elif args.action == 'list-tables':
            tables = gcp.bquery_list_tables(args.dataset)
            print(json.dumps(tables, indent=2))
        elif args.action == 'query':
            results = gcp.bquery_query(args.sql, args.max_results)
            print(json.dumps(results, indent=2, default=str))
        elif args.action == 'delete-table':
            gcp.bquery_delete_table(args.dataset, args.table)
    
    elif args.service == 'search':
        results = gcp.search_resources(args.query)
        print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
