# GCP CLI Skill

Google Cloud Platform操作助手，支持Compute/Storage/BigQuery操作。

## Description

功能描述：GCP云服务操作助手，支持Compute Engine虚拟机管理、Cloud Storage操作、BigQuery查询。Use when managing cloud resources, deploying infrastructure, or when user mentions 'GCP', 'Google Cloud', 'Compute', 'Storage', 'BigQuery'

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Configure GCP credentials:

```bash
# Using service account
gcloud auth activate-service-account --key-file=/path/to/key.json

# Or application default credentials
gcloud auth application-default login
```

Set environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
export GOOGLE_CLOUD_PROJECT=your-project-id
```

## Usage Examples

### Compute Engine Operations

```bash
# List instances
python main.py compute list
python main.py compute list --zone us-central1-a

# Get instance details
python main.py compute get --name my-vm --zone us-central1-a

# Start/Stop/Reset instances
python main.py compute start --name my-vm --zone us-central1-a
python main.py compute stop --name my-vm --zone us-central1-a
python main.py compute reset --name my-vm --zone us-central1-a

# Create VM
python main.py compute create --name new-vm --zone us-central1-a \
  --machine-type e2-medium --image projects/debian-cloud/global/images/family/debian-11

# Delete VM
python main.py compute delete --name old-vm --zone us-central1-a

# List zones and machine types
python main.py compute zones
python main.py compute types --zone us-central1-a
```

### Cloud Storage Operations

```bash
# List buckets
python main.py storage list

# Get bucket details
python main.py storage get --bucket my-bucket

# Create bucket
python main.py storage create --bucket new-bucket --location US --storage-class STANDARD

# Delete bucket
python main.py storage delete --bucket old-bucket --force

# List objects
python main.py storage objects --bucket my-bucket --prefix logs/

# Upload file
python main.py storage upload --bucket my-bucket --file ./document.pdf --destination docs/document.pdf

# Download file
python main.py storage download --bucket my-bucket --source docs/document.pdf --file ./downloaded.pdf

# Delete object
python main.py storage delete-object --bucket my-bucket --object old-file.txt

# Get signed URL
python main.py storage url --bucket my-bucket --object private-file.pdf --expires 3600
```

### BigQuery Operations

```bash
# List datasets
python main.py bquery list-datasets

# Get dataset details
python main.py bquery get-dataset --dataset my_dataset

# Create dataset
python main.py bquery create-dataset --name new_dataset --location US --description "My dataset"

# Delete dataset
python main.py bquery delete-dataset --dataset old_dataset --delete-contents

# List tables
python main.py bquery list-tables --dataset my_dataset

# Execute query
python main.py bquery query --sql "SELECT * FROM project.dataset.table LIMIT 10"

# Delete table
python main.py bquery delete-table --dataset my_dataset --table old_table
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

## Features

- ✅ Compute Engine: List, start, stop, reset, create, delete VMs
- ✅ Cloud Storage: Bucket management, file operations, signed URLs
- ✅ BigQuery: Dataset/table management, SQL query execution
- ✅ Cross-service resource search
- ✅ Multi-zone support

## Requirements

- Python 3.8+
- Google Cloud SDK for Python
- GCP service account or user credentials
- GCP project with appropriate APIs enabled

## License

MIT
