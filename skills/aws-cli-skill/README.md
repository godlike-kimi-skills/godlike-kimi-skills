# AWS CLI Skill

AWS云服务操作助手，支持EC2/S3/RDS/DynamoDB操作和资源查询。

## Description

功能描述：AWS云服务操作助手，支持EC2实例管理、S3存储操作、RDS数据库管理、DynamoDB表操作。Use when managing cloud resources, deploying infrastructure, or when user mentions 'AWS', 'EC2', 'S3', 'RDS', 'DynamoDB'

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Configure AWS credentials:

```bash
aws configure
```

Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

## Usage Examples

### EC2 Operations

```bash
# List instances
python main.py ec2 list

# Start/Stop instances
python main.py ec2 start --instance-id i-1234567890abcdef0
python main.py ec2 stop --instance-id i-1234567890abcdef0

# Create new instance
python main.py ec2 create --name my-vm --type t2.micro --ami ami-0c55b159cbfafe1f0

# Terminate instance
python main.py ec2 terminate --instance-id i-1234567890abcdef0
```

### S3 Operations

```bash
# List buckets
python main.py s3 list

# Create bucket
python main.py s3 create --bucket my-bucket --region us-east-1

# Upload/Download files
python main.py s3 upload --bucket my-bucket --file ./data.txt --key data.txt
python main.py s3 download --bucket my-bucket --key data.txt --file ./data.txt

# List objects
python main.py s3 objects --bucket my-bucket --prefix logs/

# Get presigned URL
python main.py s3 url --bucket my-bucket --key file.txt --expires 3600
```

### RDS Operations

```bash
# List databases
python main.py rds list

# Create database
python main.py rds create --name mydb --engine mysql --instance-class db.t3.micro --master-user admin --master-pass password123

# Create snapshot
python main.py rds snapshot --db-id mydb --snapshot-name mydb-backup

# List snapshots
python main.py rds snapshots --db-id mydb
```

### DynamoDB Operations

```bash
# List tables
python main.py dynamodb list

# Create table
python main.py dynamodb create --table mytable --key id --key-type S

# Describe table
python main.py dynamodb describe --table mytable

# Scan table
python main.py dynamodb scan --table mytable

# Delete table
python main.py dynamodb delete --table mytable
```

### Search Resources

```bash
# Search across all services
python main.py search my-resource-name
```

## Testing

Run the test suite:

```bash
python test.py
```

Run specific tests:

```bash
python test.py TestAWSResourceManager.test_ec2_list_instances
python test.py TestAWSResourceManager.test_s3_list_buckets
```

## Features

- ✅ EC2: List, start, stop, create, terminate instances
- ✅ S3: Bucket management, file operations, presigned URLs
- ✅ RDS: Database instances, snapshots management
- ✅ DynamoDB: Table operations, scan/query
- ✅ Cross-service resource search
- ✅ Multi-region support
- ✅ AWS profile support

## Requirements

- Python 3.8+
- boto3
- AWS credentials

## License

MIT
