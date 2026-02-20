# Terraform Skill

Terraform基础设施管理助手，支持Plan/Apply/State管理、模块操作。

## Description

功能描述：Terraform基础设施即代码(IaC)管理助手，支持资源编排、状态管理、模块操作。Use when managing cloud resources, deploying infrastructure, or when user mentions 'Terraform', 'IaC', 'Infrastructure as Code'

## Usage

```bash
# Initialize and Plan
python main.py init
python main.py plan
python main.py plan --var-file=prod.tfvars

# Apply Changes
python main.py apply
python main.py apply --auto-approve
python main.py apply --target=aws_instance.example

# Destroy Resources
python main.py destroy
python main.py destroy --auto-approve

# State Management
python main.py state list
python main.py state show aws_instance.example
python main.py state rm aws_instance.example
python main.py state mv aws_instance.old aws_instance.new
python main.py state pull > state.json

# Workspace Management
python main.py workspace list
python main.py workspace new prod
python main.py workspace select prod
python main.py workspace delete dev

# Module Operations
python main.py modules list
python main.py modules validate
python main.py modules providers

# Format and Validate
python main.py fmt
python main.py validate

# Import Resources
python main.py import aws_instance.example i-1234567890abcdef0
```

## Configuration

Requires Terraform CLI installed:
```bash
terraform version
```

Configure cloud provider credentials as needed (AWS, Azure, GCP).

## Features

- **Initialization**: terraform init with backend configuration
- **Plan/Apply**: Preview and apply infrastructure changes
- **State Management**: List, show, move, remove state resources
- **Workspace**: Multi-environment workspace management
- **Modules**: Module listing and validation
- **Import**: Import existing resources

## Requirements

- Python 3.8+
- Terraform CLI 1.0+
- Cloud provider credentials
