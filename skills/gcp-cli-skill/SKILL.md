# GCP CLI Skill

Google Cloud Platform操作助手，提供Compute Engine、Cloud Storage、BigQuery等服务的便捷操作。

## Description

功能描述：GCP云服务操作助手，支持Compute Engine虚拟机管理、Cloud Storage操作、BigQuery查询。Use when managing cloud resources, deploying infrastructure, or when user mentions 'GCP', 'Google Cloud', 'Compute', 'Storage', 'BigQuery'

## Usage

```bash
# Compute Engine Operations
python main.py compute list
python main.py compute start --name my-vm --zone us-central1-a
python main.py compute stop --name my-vm --zone us-central1-a
python main.py compute create --name my-vm --zone us-central1-a --machine-type e2-medium
python main.py compute delete --name my-vm --zone us-central1-a

# Cloud Storage Operations
python main.py storage list
python main.py storage create --bucket my-bucket --location us-central1
python main.py storage upload --bucket my-bucket --file ./data.txt --destination data.txt
python main.py storage download --bucket my-bucket --source data.txt --file ./data.txt
python main.py storage delete-object --bucket my-bucket --object data.txt

# BigQuery Operations
python main.py bquery list-datasets
python main.py bquery list-tables --dataset my_dataset
python main.py bquery query --sql "SELECT * FROM project.dataset.table LIMIT 10"
python main.py bquery create-dataset --name new_dataset --location us-central1

# Search Resources
python main.py search my-resource-name
```

## Configuration

Set GCP credentials via service account:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

Or authenticate via gcloud:
```bash
gcloud auth application-default login
```

## Features

- **Compute Engine**: List, start, stop, create, delete VM instances
- **Cloud Storage**: Bucket management, file upload/download
- **BigQuery**: Dataset/table management, SQL query execution
- **Resource Discovery**: Cross-service resource search

## Requirements

- Python 3.8+
- google-cloud-compute, google-cloud-storage, google-cloud-bigquery
- GCP credentials configured
