# AWS CLI Skill

AWS CLI操作助手，提供EC2、S3、RDS、DynamoDB等服务的便捷操作。

## Description

功能描述：AWS云服务操作助手，支持EC2实例管理、S3存储操作、RDS数据库管理、DynamoDB表操作。Use when managing cloud resources, deploying infrastructure, or when user mentions 'AWS', 'EC2', 'S3', 'RDS', 'DynamoDB'

## Usage

```bash
# EC2 Operations
python main.py ec2 list
python main.py ec2 start --instance-id i-1234567890abcdef0
python main.py ec2 stop --instance-id i-1234567890abcdef0
python main.py ec2 create --name my-instance --type t2.micro --ami ami-12345678

# S3 Operations
python main.py s3 list
python main.py s3 create --bucket my-bucket --region us-east-1
python main.py s3 upload --bucket my-bucket --file ./data.txt --key data.txt
python main.py s3 download --bucket my-bucket --key data.txt --file ./data.txt

# RDS Operations
python main.py rds list
python main.py rds create --name my-db --engine mysql --instance-class db.t3.micro
python main.py rds snapshot --db-id my-db --snapshot-name backup-2024

# DynamoDB Operations
python main.py dynamodb list
python main.py dynamodb create --table my-table --key id --key-type S
python main.py dynamodb put --table my-table --item '{"id": "1", "name": "test"}'
python main.py dynamodb query --table my-table --key id --value 1
```

## Configuration

Set AWS credentials via environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

Or use AWS CLI profile:
```bash
aws configure
```

## Features

- **EC2 Management**: List, start, stop, create, terminate instances
- **S3 Operations**: Bucket management, file upload/download
- **RDS Control**: Database instances, snapshots, parameter groups
- **DynamoDB**: Table operations, CRUD, query/scan
- **Resource Discovery**: Cross-service resource search

## Requirements

- Python 3.8+
- boto3 library
- AWS credentials configured
