# Terraform Skill

Terraform基础设施管理助手，支持Plan/Apply/State管理、模块操作。

## Description

功能描述：Terraform基础设施即代码(IaC)管理助手，支持资源编排、状态管理、模块操作。Use when managing cloud resources, deploying infrastructure, or when user mentions 'Terraform', 'IaC', 'Infrastructure as Code'

## Installation

```bash
pip install -r requirements.txt
```

Ensure Terraform CLI is installed:
```bash
terraform version
```

## Configuration

Set up your Terraform working directory with:
- `main.tf` - Main configuration
- `variables.tf` - Variable definitions
- `outputs.tf` - Output definitions
- `terraform.tfvars` - Variable values (optional)

Configure cloud provider credentials as needed:
```bash
# AWS
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx

# Azure
export ARM_CLIENT_ID=xxx
export ARM_CLIENT_SECRET=xxx

# GCP
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

## Usage Examples

### Initialize and Basic Operations

```bash
# Initialize Terraform
python main.py init

# Initialize with backend reconfiguration
python main.py init --upgrade --reconfigure

# Validate configuration
python main.py validate

# Format configuration files
python main.py fmt
python main.py fmt --recursive
python main.py fmt --check  # Check without modifying
```

### Plan and Apply

```bash
# Generate plan
python main.py plan

# Plan with variable file
python main.py plan --var-file=prod.tfvars

# Plan specific resource
python main.py plan --target=aws_instance.example

# Plan destruction
python main.py plan --destroy

# Apply changes
python main.py apply

# Apply with auto-approve
python main.py apply --auto-approve

# Apply specific plan file
python main.py apply --plan=tfplan

# Apply specific resource
python main.py apply --target=aws_instance.example
```

### Destroy

```bash
# Destroy resources
python main.py destroy

# Destroy with auto-approve
python main.py destroy --auto-approve

# Destroy specific resource
python main.py destroy --target=aws_instance.example
```

### State Management

```bash
# List resources in state
python main.py state list

# Show resource details
python main.py state show aws_instance.example

# Remove resource from state
python main.py state rm aws_instance.example

# Move resource in state
python main.py state mv aws_instance.old aws_instance.new

# Pull raw state
python main.py state pull > state.json

# Push state from file
python main.py state push state.json
```

### Workspace Management

```bash
# List workspaces
python main.py workspace list

# Create new workspace
python main.py workspace new prod

# Select workspace
python main.py workspace select prod

# Show current workspace
python main.py workspace show

# Delete workspace
python main.py workspace delete dev --force
```

### Import Resources

```bash
# Import existing resource
python main.py import aws_instance.example i-1234567890abcdef0

# Import with variable file
python main.py import aws_instance.example i-1234567890abcdef0 --var-file=prod.tfvars
```

### Module Operations

```bash
# List modules in configuration
python main.py modules list

# Download and update modules
python main.py modules get

# List providers
python main.py modules providers
```

### Output and Show

```bash
# Show all outputs
python main.py output

# Show specific output
python main.py output vpc_id

# Show state
python main.py show

# Show plan file
python main.py show tfplan
```

### Taint/Untaint

```bash
# Taint resource (force recreation)
python main.py taint aws_instance.example

# Untaint resource
python main.py untaint aws_instance.example
```

### Refresh

```bash
# Refresh state to match real resources
python main.py refresh
```

## Testing

Run the test suite:

```bash
python test.py
```

## Features

- ✅ **Initialization**: terraform init with backend configuration
- ✅ **Plan/Apply**: Preview and apply infrastructure changes
- ✅ **State Management**: List, show, move, remove, pull, push state
- ✅ **Workspace**: Multi-environment workspace management
- ✅ **Module Operations**: List modules, download, providers
- ✅ **Import**: Import existing resources
- ✅ **Format/Validate**: Format and validate configuration
- ✅ **Taint/Untaint**: Force resource recreation
- ✅ **Output**: Show output values
- ✅ **Destroy**: Clean up resources

## Requirements

- Python 3.8+
- Terraform CLI 1.0+
- Cloud provider credentials

## License

MIT
