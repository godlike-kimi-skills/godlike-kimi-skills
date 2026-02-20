# Azure CLI Skill

Azure云服务操作助手，支持VM/Storage/SQL服务管理。

## Description

功能描述：Azure云服务操作助手，支持虚拟机管理、存储账户操作、SQL数据库管理。Use when managing cloud resources, deploying infrastructure, or when user mentions 'Azure', 'VM', 'Storage', 'SQL Database'

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Configure Azure credentials:

```bash
# Login via Azure CLI
az login
az account set --subscription "Your Subscription Name"
```

Or use service principal:
```bash
export AZURE_CLIENT_ID=your_client_id
export AZURE_CLIENT_SECRET=your_client_secret
export AZURE_TENANT_ID=your_tenant_id
export AZURE_SUBSCRIPTION_ID=your_subscription_id
```

## Usage Examples

### VM Operations

```bash
# List VMs
python main.py vm list
python main.py vm list --resource-group my-rg

# Start/Stop VMs
python main.py vm start --name my-vm --resource-group my-rg
python main.py vm stop --name my-vm --resource-group my-rg
python main.py vm stop --name my-vm --resource-group my-rg --deallocate

# Restart VM
python main.py vm restart --name my-vm --resource-group my-rg

# Create VM
python main.py vm create --name new-vm --resource-group my-rg --location eastus \
  --size Standard_B1s --admin-user adminuser --admin-pass SecurePassword123 \
  --image UbuntuLTS

# Delete VM
python main.py vm delete --name old-vm --resource-group my-rg
```

### Storage Operations

```bash
# List storage accounts
python main.py storage list

# Create storage account
python main.py storage create --name mystorage --resource-group my-rg --location eastus --sku Standard_LRS

# Delete storage account
python main.py storage delete --name oldstorage --resource-group my-rg

# List containers
python main.py storage containers --account mystorage --resource-group my-rg

# Upload file
python main.py storage upload --connection-string "DefaultEndpointsProtocol=https;..." \
  --container data --file ./document.pdf --blob document.pdf

# Download file
python main.py storage download --connection-string "DefaultEndpointsProtocol=https;..." \
  --container data --blob document.pdf --file ./downloaded.pdf
```

### SQL Database Operations

```bash
# List SQL servers
python main.py sql list-servers
python main.py sql list-servers --resource-group my-rg

# Create SQL server
python main.py sql create-server --name myserver --resource-group my-rg --location eastus \
  --admin-user sqladmin --admin-pass SecurePassword123

# Delete SQL server
python main.py sql delete-server --name oldserver --resource-group my-rg

# List databases
python main.py sql list-dbs --server myserver --resource-group my-rg

# Create database
python main.py sql create-db --name mydb --server myserver --resource-group my-rg --sku Basic

# Delete database
python main.py sql delete-db --name olddb --server myserver --resource-group my-rg
```

### Resource Group Operations

```bash
# List resource groups
python main.py group list

# Create resource group
python main.py group create --name new-rg --location eastus

# Delete resource group
python main.py group delete --name old-rg

# List resources in group
python main.py group resources --name my-rg
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

- ✅ VM: List, start, stop, restart, create, delete virtual machines
- ✅ Storage: Account management, blob upload/download, container management
- ✅ SQL Database: Server and database lifecycle management
- ✅ Resource Groups: Group creation, deletion, resource listing
- ✅ Cross-service resource search
- ✅ Multi-region support
- ✅ Service principal authentication

## Requirements

- Python 3.8+
- Azure SDK for Python
- Azure CLI (optional, for interactive login)
- Azure subscription

## License

MIT
