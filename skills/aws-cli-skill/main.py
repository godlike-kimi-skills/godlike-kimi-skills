#!/usr/bin/env python3
"""
AWS CLI Skill - AWS Cloud Operations Assistant
Supports EC2, S3, RDS, DynamoDB operations
"""

import argparse
import json
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print("Error: boto3 not installed. Run: pip install boto3")
    sys.exit(1)


class AWSResourceManager:
    """Unified AWS Resource Manager for multiple services"""
    
    def __init__(self, region: Optional[str] = None, profile: Optional[str] = None):
        self.region = region or 'us-east-1'
        self.profile = profile
        self.session = self._create_session()
        
    def _create_session(self):
        """Create AWS session with profile or default credentials"""
        try:
            if self.profile:
                return boto3.Session(profile_name=self.profile, region_name=self.region)
            return boto3.Session(region_name=self.region)
        except Exception as e:
            print(f"Error creating AWS session: {e}")
            sys.exit(1)
    
    # ==================== EC2 Operations ====================
    
    def ec2_list_instances(self, state: Optional[str] = None) -> List[Dict]:
        """List EC2 instances with optional state filter"""
        try:
            ec2 = self.session.client('ec2')
            filters = []
            if state:
                filters.append({'Name': 'instance-state-name', 'Values': [state]})
            
            response = ec2.describe_instances(Filters=filters) if filters else ec2.describe_instances()
            
            instances = []
            for reservation in response['Reservations']:
                for inst in reservation['Instances']:
                    instances.append({
                        'InstanceId': inst['InstanceId'],
                        'InstanceType': inst['InstanceType'],
                        'State': inst['State']['Name'],
                        'PublicIP': inst.get('PublicIpAddress', 'N/A'),
                        'PrivateIP': inst.get('PrivateIpAddress', 'N/A'),
                        'Name': next((t['Value'] for t in inst.get('Tags', []) if t['Key'] == 'Name'), 'N/A'),
                        'LaunchTime': inst['LaunchTime'].isoformat()
                    })
            return instances
        except ClientError as e:
            print(f"Error listing instances: {e}")
            return []
    
    def ec2_start_instance(self, instance_id: str) -> bool:
        """Start an EC2 instance"""
        try:
            ec2 = self.session.client('ec2')
            ec2.start_instances(InstanceIds=[instance_id])
            print(f"Started instance: {instance_id}")
            return True
        except ClientError as e:
            print(f"Error starting instance: {e}")
            return False
    
    def ec2_stop_instance(self, instance_id: str, force: bool = False) -> bool:
        """Stop an EC2 instance"""
        try:
            ec2 = self.session.client('ec2')
            ec2.stop_instances(InstanceIds=[instance_id], Force=force)
            print(f"Stopped instance: {instance_id}")
            return True
        except ClientError as e:
            print(f"Error stopping instance: {e}")
            return False
    
    def ec2_create_instance(self, name: str, instance_type: str, ami: str, 
                           key_name: Optional[str] = None, security_group: Optional[str] = None) -> Optional[str]:
        """Create a new EC2 instance"""
        try:
            ec2 = self.session.client('ec2')
            
            kwargs = {
                'ImageId': ami,
                'InstanceType': instance_type,
                'MinCount': 1,
                'MaxCount': 1,
                'TagSpecifications': [{
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': name}]
                }]
            }
            
            if key_name:
                kwargs['KeyName'] = key_name
            if security_group:
                kwargs['SecurityGroupIds'] = [security_group]
            
            response = ec2.run_instances(**kwargs)
            instance_id = response['Instances'][0]['InstanceId']
            print(f"Created instance: {instance_id}")
            return instance_id
        except ClientError as e:
            print(f"Error creating instance: {e}")
            return None
    
    def ec2_terminate_instance(self, instance_id: str) -> bool:
        """Terminate an EC2 instance"""
        try:
            ec2 = self.session.client('ec2')
            ec2.terminate_instances(InstanceIds=[instance_id])
            print(f"Terminated instance: {instance_id}")
            return True
        except ClientError as e:
            print(f"Error terminating instance: {e}")
            return False
    
    def ec2_describe_instance(self, instance_id: str) -> Optional[Dict]:
        """Get detailed instance information"""
        try:
            ec2 = self.session.client('ec2')
            response = ec2.describe_instances(InstanceIds=[instance_id])
            return response['Reservations'][0]['Instances'][0]
        except ClientError as e:
            print(f"Error describing instance: {e}")
            return None
    
    # ==================== S3 Operations ====================
    
    def s3_list_buckets(self) -> List[Dict]:
        """List all S3 buckets"""
        try:
            s3 = self.session.client('s3')
            response = s3.list_buckets()
            buckets = []
            for bucket in response['Buckets']:
                buckets.append({
                    'Name': bucket['Name'],
                    'CreationDate': bucket['CreationDate'].isoformat()
                })
            return buckets
        except ClientError as e:
            print(f"Error listing buckets: {e}")
            return []
    
    def s3_create_bucket(self, bucket_name: str, region: Optional[str] = None) -> bool:
        """Create a new S3 bucket"""
        try:
            s3 = self.session.client('s3')
            kwargs = {'Bucket': bucket_name}
            
            if region and region != 'us-east-1':
                kwargs['CreateBucketConfiguration'] = {'LocationConstraint': region}
            
            s3.create_bucket(**kwargs)
            print(f"Created bucket: {bucket_name}")
            return True
        except ClientError as e:
            print(f"Error creating bucket: {e}")
            return False
    
    def s3_list_objects(self, bucket: str, prefix: str = '') -> List[Dict]:
        """List objects in S3 bucket"""
        try:
            s3 = self.session.client('s3')
            kwargs = {'Bucket': bucket}
            if prefix:
                kwargs['Prefix'] = prefix
            
            response = s3.list_objects_v2(**kwargs)
            objects = []
            for obj in response.get('Contents', []):
                objects.append({
                    'Key': obj['Key'],
                    'Size': obj['Size'],
                    'LastModified': obj['LastModified'].isoformat()
                })
            return objects
        except ClientError as e:
            print(f"Error listing objects: {e}")
            return []
    
    def s3_upload_file(self, bucket: str, file_path: str, key: str) -> bool:
        """Upload file to S3"""
        try:
            s3 = self.session.client('s3')
            s3.upload_file(file_path, bucket, key)
            print(f"Uploaded {file_path} to s3://{bucket}/{key}")
            return True
        except ClientError as e:
            print(f"Error uploading file: {e}")
            return False
    
    def s3_download_file(self, bucket: str, key: str, file_path: str) -> bool:
        """Download file from S3"""
        try:
            s3 = self.session.client('s3')
            s3.download_file(bucket, key, file_path)
            print(f"Downloaded s3://{bucket}/{key} to {file_path}")
            return True
        except ClientError as e:
            print(f"Error downloading file: {e}")
            return False
    
    def s3_delete_object(self, bucket: str, key: str) -> bool:
        """Delete object from S3"""
        try:
            s3 = self.session.client('s3')
            s3.delete_object(Bucket=bucket, Key=key)
            print(f"Deleted s3://{bucket}/{key}")
            return True
        except ClientError as e:
            print(f"Error deleting object: {e}")
            return False
    
    def s3_get_presigned_url(self, bucket: str, key: str, expiration: int = 3600) -> Optional[str]:
        """Generate presigned URL for S3 object"""
        try:
            s3 = self.session.client('s3')
            url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None
    
    # ==================== RDS Operations ====================
    
    def rds_list_instances(self) -> List[Dict]:
        """List RDS instances"""
        try:
            rds = self.session.client('rds')
            response = rds.describe_db_instances()
            instances = []
            for db in response['DBInstances']:
                instances.append({
                    'DBInstanceIdentifier': db['DBInstanceIdentifier'],
                    'DBInstanceClass': db['DBInstanceClass'],
                    'Engine': db['Engine'],
                    'DBInstanceStatus': db['DBInstanceStatus'],
                    'Endpoint': db.get('Endpoint', {}).get('Address', 'N/A'),
                    'Port': db.get('Endpoint', {}).get('Port', 'N/A')
                })
            return instances
        except ClientError as e:
            print(f"Error listing RDS instances: {e}")
            return []
    
    def rds_create_instance(self, db_id: str, engine: str, instance_class: str,
                           master_user: str, master_pass: str, allocated_storage: int = 20) -> bool:
        """Create RDS instance"""
        try:
            rds = self.session.client('rds')
            rds.create_db_instance(
                DBInstanceIdentifier=db_id,
                DBInstanceClass=instance_class,
                Engine=engine,
                MasterUsername=master_user,
                MasterUserPassword=master_pass,
                AllocatedStorage=allocated_storage
            )
            print(f"Creating RDS instance: {db_id}")
            return True
        except ClientError as e:
            print(f"Error creating RDS instance: {e}")
            return False
    
    def rds_delete_instance(self, db_id: str, skip_snapshot: bool = False) -> bool:
        """Delete RDS instance"""
        try:
            rds = self.session.client('rds')
            kwargs = {'DBInstanceIdentifier': db_id}
            if skip_snapshot:
                kwargs['SkipFinalSnapshot'] = True
            else:
                kwargs['FinalDBSnapshotIdentifier'] = f"{db_id}-final-snapshot"
            
            rds.delete_db_instance(**kwargs)
            print(f"Deleting RDS instance: {db_id}")
            return True
        except ClientError as e:
            print(f"Error deleting RDS instance: {e}")
            return False
    
    def rds_create_snapshot(self, db_id: str, snapshot_id: str) -> bool:
        """Create RDS snapshot"""
        try:
            rds = self.session.client('rds')
            rds.create_db_snapshot(
                DBInstanceIdentifier=db_id,
                DBSnapshotIdentifier=snapshot_id
            )
            print(f"Creating snapshot: {snapshot_id}")
            return True
        except ClientError as e:
            print(f"Error creating snapshot: {e}")
            return False
    
    def rds_list_snapshots(self, db_id: Optional[str] = None) -> List[Dict]:
        """List RDS snapshots"""
        try:
            rds = self.session.client('rds')
            kwargs = {}
            if db_id:
                kwargs['DBInstanceIdentifier'] = db_id
            
            response = rds.describe_db_snapshots(**kwargs)
            snapshots = []
            for snap in response['DBSnapshots']:
                snapshots.append({
                    'DBSnapshotIdentifier': snap['DBSnapshotIdentifier'],
                    'DBInstanceIdentifier': snap['DBInstanceIdentifier'],
                    'SnapshotCreateTime': snap.get('SnapshotCreateTime', 'N/A'),
                    'Status': snap['Status']
                })
            return snapshots
        except ClientError as e:
            print(f"Error listing snapshots: {e}")
            return []
    
    # ==================== DynamoDB Operations ====================
    
    def dynamodb_list_tables(self) -> List[str]:
        """List DynamoDB tables"""
        try:
            dynamodb = self.session.client('dynamodb')
            response = dynamodb.list_tables()
            return response['TableNames']
        except ClientError as e:
            print(f"Error listing tables: {e}")
            return []
    
    def dynamodb_create_table(self, table_name: str, key_name: str, key_type: str = 'S',
                             read_capacity: int = 5, write_capacity: int = 5) -> bool:
        """Create DynamoDB table"""
        try:
            dynamodb = self.session.client('dynamodb')
            dynamodb.create_table(
                TableName=table_name,
                KeySchema=[{'AttributeName': key_name, 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': key_name, 'AttributeType': key_type}],
                ProvisionedThroughput={
                    'ReadCapacityUnits': read_capacity,
                    'WriteCapacityUnits': write_capacity
                }
            )
            print(f"Creating table: {table_name}")
            return True
        except ClientError as e:
            print(f"Error creating table: {e}")
            return False
    
    def dynamodb_describe_table(self, table_name: str) -> Optional[Dict]:
        """Get DynamoDB table details"""
        try:
            dynamodb = self.session.client('dynamodb')
            response = dynamodb.describe_table(TableName=table_name)
            return response['Table']
        except ClientError as e:
            print(f"Error describing table: {e}")
            return None
    
    def dynamodb_put_item(self, table_name: str, item: Dict) -> bool:
        """Put item into DynamoDB table"""
        try:
            dynamodb = self.session.client('dynamodb')
            dynamodb.put_item(TableName=table_name, Item=item)
            print(f"Put item into {table_name}")
            return True
        except ClientError as e:
            print(f"Error putting item: {e}")
            return False
    
    def dynamodb_get_item(self, table_name: str, key: Dict) -> Optional[Dict]:
        """Get item from DynamoDB table"""
        try:
            dynamodb = self.session.client('dynamodb')
            response = dynamodb.get_item(TableName=table_name, Key=key)
            return response.get('Item')
        except ClientError as e:
            print(f"Error getting item: {e}")
            return None
    
    def dynamodb_query(self, table_name: str, key_name: str, key_value: Any) -> List[Dict]:
        """Query DynamoDB table"""
        try:
            dynamodb = self.session.client('dynamodb')
            response = dynamodb.query(
                TableName=table_name,
                KeyConditionExpression=f"{key_name} = :v",
                ExpressionAttributeValues={':v': key_value}
            )
            return response.get('Items', [])
        except ClientError as e:
            print(f"Error querying table: {e}")
            return []
    
    def dynamodb_scan(self, table_name: str) -> List[Dict]:
        """Scan DynamoDB table"""
        try:
            dynamodb = self.session.client('dynamodb')
            response = dynamodb.scan(TableName=table_name)
            return response.get('Items', [])
        except ClientError as e:
            print(f"Error scanning table: {e}")
            return []
    
    def dynamodb_delete_table(self, table_name: str) -> bool:
        """Delete DynamoDB table"""
        try:
            dynamodb = self.session.client('dynamodb')
            dynamodb.delete_table(TableName=table_name)
            print(f"Deleting table: {table_name}")
            return True
        except ClientError as e:
            print(f"Error deleting table: {e}")
            return False
    
    # ==================== Resource Discovery ====================
    
    def search_resources(self, query: str) -> Dict[str, List]:
        """Search resources across services"""
        results = {
            'ec2': [],
            's3': [],
            'rds': [],
            'dynamodb': []
        }
        
        # Search EC2 instances
        try:
            ec2 = self.session.client('ec2')
            response = ec2.describe_instances()
            for reservation in response['Reservations']:
                for inst in reservation['Instances']:
                    name = next((t['Value'] for t in inst.get('Tags', []) if t['Key'] == 'Name'), '')
                    if query.lower() in name.lower() or query.lower() in inst['InstanceId'].lower():
                        results['ec2'].append(inst)
        except:
            pass
        
        # Search S3 buckets
        try:
            s3 = self.session.client('s3')
            response = s3.list_buckets()
            for bucket in response['Buckets']:
                if query.lower() in bucket['Name'].lower():
                    results['s3'].append(bucket)
        except:
            pass
        
        # Search RDS instances
        try:
            rds = self.session.client('rds')
            response = rds.describe_db_instances()
            for db in response['DBInstances']:
                if query.lower() in db['DBInstanceIdentifier'].lower():
                    results['rds'].append(db)
        except:
            pass
        
        # Search DynamoDB tables
        try:
            dynamodb = self.session.client('dynamodb')
            response = dynamodb.list_tables()
            for table in response['TableNames']:
                if query.lower() in table.lower():
                    results['dynamodb'].append(table)
        except:
            pass
        
        return results


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='AWS CLI Skill - Cloud Operations Assistant',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--region', '-r', help='AWS region')
    parser.add_argument('--profile', '-p', help='AWS profile name')
    parser.add_argument('--output', '-o', choices=['json', 'table'], default='json', help='Output format')
    
    subparsers = parser.add_subparsers(dest='service', help='AWS Service')
    
    # EC2 subcommands
    ec2_parser = subparsers.add_parser('ec2', help='EC2 operations')
    ec2_subparsers = ec2_parser.add_subparsers(dest='action')
    
    ec2_list = ec2_subparsers.add_parser('list', help='List instances')
    ec2_list.add_argument('--state', choices=['running', 'stopped', 'pending', 'terminated'])
    
    ec2_start = ec2_subparsers.add_parser('start', help='Start instance')
    ec2_start.add_argument('--instance-id', '-i', required=True)
    
    ec2_stop = ec2_subparsers.add_parser('stop', help='Stop instance')
    ec2_stop.add_argument('--instance-id', '-i', required=True)
    ec2_stop.add_argument('--force', action='store_true')
    
    ec2_create = ec2_subparsers.add_parser('create', help='Create instance')
    ec2_create.add_argument('--name', '-n', required=True)
    ec2_create.add_argument('--type', '-t', default='t2.micro')
    ec2_create.add_argument('--ami', '-a', required=True)
    ec2_create.add_argument('--key-name', '-k')
    ec2_create.add_argument('--security-group', '-s')
    
    ec2_terminate = ec2_subparsers.add_parser('terminate', help='Terminate instance')
    ec2_terminate.add_argument('--instance-id', '-i', required=True)
    
    # S3 subcommands
    s3_parser = subparsers.add_parser('s3', help='S3 operations')
    s3_subparsers = s3_parser.add_subparsers(dest='action')
    
    s3_list = s3_subparsers.add_parser('list', help='List buckets')
    
    s3_create = s3_subparsers.add_parser('create', help='Create bucket')
    s3_create.add_argument('--bucket', '-b', required=True)
    s3_create.add_argument('--region', '-r')
    
    s3_objects = s3_subparsers.add_parser('objects', help='List objects')
    s3_objects.add_argument('--bucket', '-b', required=True)
    s3_objects.add_argument('--prefix', '-p', default='')
    
    s3_upload = s3_subparsers.add_parser('upload', help='Upload file')
    s3_upload.add_argument('--bucket', '-b', required=True)
    s3_upload.add_argument('--file', '-f', required=True)
    s3_upload.add_argument('--key', '-k', required=True)
    
    s3_download = s3_subparsers.add_parser('download', help='Download file')
    s3_download.add_argument('--bucket', '-b', required=True)
    s3_download.add_argument('--key', '-k', required=True)
    s3_download.add_argument('--file', '-f', required=True)
    
    s3_delete = s3_subparsers.add_parser('delete', help='Delete object')
    s3_delete.add_argument('--bucket', '-b', required=True)
    s3_delete.add_argument('--key', '-k', required=True)
    
    s3_url = s3_subparsers.add_parser('url', help='Get presigned URL')
    s3_url.add_argument('--bucket', '-b', required=True)
    s3_url.add_argument('--key', '-k', required=True)
    s3_url.add_argument('--expires', '-e', type=int, default=3600)
    
    # RDS subcommands
    rds_parser = subparsers.add_parser('rds', help='RDS operations')
    rds_subparsers = rds_parser.add_subparsers(dest='action')
    
    rds_list = rds_subparsers.add_parser('list', help='List instances')
    
    rds_create = rds_subparsers.add_parser('create', help='Create instance')
    rds_create.add_argument('--name', '-n', required=True)
    rds_create.add_argument('--engine', '-e', required=True)
    rds_create.add_argument('--instance-class', '-c', default='db.t3.micro')
    rds_create.add_argument('--master-user', '-u', required=True)
    rds_create.add_argument('--master-pass', '-p', required=True)
    rds_create.add_argument('--storage', '-s', type=int, default=20)
    
    rds_delete = rds_subparsers.add_parser('delete', help='Delete instance')
    rds_delete.add_argument('--db-id', '-d', required=True)
    rds_delete.add_argument('--skip-snapshot', action='store_true')
    
    rds_snapshot = rds_subparsers.add_parser('snapshot', help='Create snapshot')
    rds_snapshot.add_argument('--db-id', '-d', required=True)
    rds_snapshot.add_argument('--snapshot-name', '-s', required=True)
    
    rds_snapshots = rds_subparsers.add_parser('snapshots', help='List snapshots')
    rds_snapshots.add_argument('--db-id', '-d')
    
    # DynamoDB subcommands
    dynamodb_parser = subparsers.add_parser('dynamodb', help='DynamoDB operations')
    dynamodb_subparsers = dynamodb_parser.add_subparsers(dest='action')
    
    dynamodb_list = dynamodb_subparsers.add_parser('list', help='List tables')
    
    dynamodb_create = dynamodb_subparsers.add_parser('create', help='Create table')
    dynamodb_create.add_argument('--table', '-t', required=True)
    dynamodb_create.add_argument('--key', '-k', required=True)
    dynamodb_create.add_argument('--key-type', choices=['S', 'N', 'B'], default='S')
    dynamodb_create.add_argument('--read-capacity', type=int, default=5)
    dynamodb_create.add_argument('--write-capacity', type=int, default=5)
    
    dynamodb_describe = dynamodb_subparsers.add_parser('describe', help='Describe table')
    dynamodb_describe.add_argument('--table', '-t', required=True)
    
    dynamodb_delete = dynamodb_subparsers.add_parser('delete', help='Delete table')
    dynamodb_delete.add_argument('--table', '-t', required=True)
    
    dynamodb_scan = dynamodb_subparsers.add_parser('scan', help='Scan table')
    dynamodb_scan.add_argument('--table', '-t', required=True)
    
    # Search subcommand
    search_parser = subparsers.add_parser('search', help='Search resources')
    search_parser.add_argument('query', help='Search query')
    
    args = parser.parse_args()
    
    if not args.service:
        parser.print_help()
        return
    
    # Initialize AWS manager
    aws = AWSResourceManager(region=args.region, profile=args.profile)
    
    # Execute commands
    if args.service == 'ec2':
        if args.action == 'list':
            instances = aws.ec2_list_instances(state=args.state)
            print(json.dumps(instances, indent=2))
        elif args.action == 'start':
            aws.ec2_start_instance(args.instance_id)
        elif args.action == 'stop':
            aws.ec2_stop_instance(args.instance_id, force=args.force)
        elif args.action == 'create':
            aws.ec2_create_instance(
                name=args.name,
                instance_type=args.type,
                ami=args.ami,
                key_name=args.key_name,
                security_group=args.security_group
            )
        elif args.action == 'terminate':
            aws.ec2_terminate_instance(args.instance_id)
    
    elif args.service == 's3':
        if args.action == 'list':
            buckets = aws.s3_list_buckets()
            print(json.dumps(buckets, indent=2))
        elif args.action == 'create':
            aws.s3_create_bucket(args.bucket, region=args.region)
        elif args.action == 'objects':
            objects = aws.s3_list_objects(args.bucket, prefix=args.prefix)
            print(json.dumps(objects, indent=2))
        elif args.action == 'upload':
            aws.s3_upload_file(args.bucket, args.file, args.key)
        elif args.action == 'download':
            aws.s3_download_file(args.bucket, args.key, args.file)
        elif args.action == 'delete':
            aws.s3_delete_object(args.bucket, args.key)
        elif args.action == 'url':
            url = aws.s3_get_presigned_url(args.bucket, args.key, args.expires)
            print(url)
    
    elif args.service == 'rds':
        if args.action == 'list':
            instances = aws.rds_list_instances()
            print(json.dumps(instances, indent=2))
        elif args.action == 'create':
            aws.rds_create_instance(
                db_id=args.name,
                engine=args.engine,
                instance_class=args.instance_class,
                master_user=args.master_user,
                master_pass=args.master_pass,
                allocated_storage=args.storage
            )
        elif args.action == 'delete':
            aws.rds_delete_instance(args.db_id, skip_snapshot=args.skip_snapshot)
        elif args.action == 'snapshot':
            aws.rds_create_snapshot(args.db_id, args.snapshot_name)
        elif args.action == 'snapshots':
            snapshots = aws.rds_list_snapshots(db_id=args.db_id)
            print(json.dumps(snapshots, indent=2))
    
    elif args.service == 'dynamodb':
        if args.action == 'list':
            tables = aws.dynamodb_list_tables()
            print(json.dumps(tables, indent=2))
        elif args.action == 'create':
            aws.dynamodb_create_table(
                table_name=args.table,
                key_name=args.key,
                key_type=args.key_type,
                read_capacity=args.read_capacity,
                write_capacity=args.write_capacity
            )
        elif args.action == 'describe':
            table = aws.dynamodb_describe_table(args.table)
            print(json.dumps(table, indent=2, default=str))
        elif args.action == 'delete':
            aws.dynamodb_delete_table(args.table)
        elif args.action == 'scan':
            items = aws.dynamodb_scan(args.table)
            print(json.dumps(items, indent=2, default=str))
    
    elif args.service == 'search':
        results = aws.search_resources(args.query)
        print(json.dumps(results, indent=2, default=str))


if __name__ == '__main__':
    main()
