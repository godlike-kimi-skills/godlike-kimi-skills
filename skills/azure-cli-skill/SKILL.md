# Azure CLI Skill

Azure云服务操作助手，提供VM、Storage、SQL Database等服务的便捷操作。

## Description

功能描述：Azure云服务操作助手，支持虚拟机管理、存储账户操作、SQL数据库管理。Use when managing cloud resources, deploying infrastructure, or when user mentions 'Azure', 'VM', 'Storage', 'SQL Database'

## Usage

```bash
# VM Operations
python main.py vm list
python main.py vm start --name my-vm --resource-group my-rg
python main.py vm stop --name my-vm --resource-group my-rg
python main.py vm create --name my-vm --resource-group my-rg --size Standard_B1s

# Storage Operations
python main.py storage list
python main.py storage create --name mystorage --resource-group my-rg --sku Standard_LRS
python main.py storage upload --account mystorage --container data --file ./data.txt
python main.py storage download --account mystorage --container data --blob data.txt

# SQL Database Operations
python main.py sql list-servers
python main.py sql create-server --name myserver --resource-group my-rg --admin-user admin --admin-pass password123
python main.py sql create-db --name mydb --server myserver --resource-group my-rg
python main.py sql list-dbs --server myserver --resource-group my-rg

# Resource Group Operations
python main.py group list
python main.py group create --name my-rg --location eastus

# Search Resources
python main.py search my-resource-name
```

## Configuration

Set Azure credentials via Azure CLI:
```bash
az login
az account set --subscription "My Subscription"
```

Or use service principal:
```bash
export AZURE_CLIENT_ID=your_client_id
export AZURE_CLIENT_SECRET=your_client_secret
export AZURE_TENANT_ID=your_tenant_id
export AZURE_SUBSCRIPTION_ID=your_subscription_id
```

## Features

- **VM Management**: List, start, stop, create, delete virtual machines
- **Storage Operations**: Account management, blob upload/download
- **SQL Database**: Server and database management
- **Resource Groups**: Group creation and management
- **Resource Discovery**: Cross-service resource search

## Requirements

- Python 3.8+
- azure-mgmt-compute, azure-mgmt-storage, azure-mgmt-sql, azure-mgmt-resource
- Azure CLI or service principal credentials
