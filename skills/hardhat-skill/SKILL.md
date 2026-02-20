# Hardhat Skill

A comprehensive skill for Hardhat Ethereum development environment with project initialization, contract compilation, and testing. Use when developing blockchain applications, interacting with smart contracts, or when user mentions 'Ethereum', 'Web3', 'blockchain'.

## Description

The Hardhat Skill provides tools for managing Hardhat projects including project initialization, smart contract compilation, automated testing, and deployment scripts.

## Features

- **Project Initialization**: Create new Hardhat projects from templates
- **Contract Compilation**: Compile Solidity contracts with optimization
- **Testing Framework**: Run and debug Hardhat tests
- **Deployment Scripts**: Manage deployment configurations
- **Network Management**: Configure local, testnet, and mainnet networks
- **Task Automation**: Run Hardhat tasks and custom scripts

## Installation

```bash
pip install -r requirements.txt
```

Requires Node.js and npm installed.

## Usage

```python
from main import HardhatSkill

# Initialize skill
skill = HardhatSkill("config.json")

# Create new Hardhat project
skill.init_project("my-dapp", template="basic")

# Compile contracts
skill.compile_contracts(optimizer=True, runs=200)

# Run tests
skill.test(verbose=True, grep="MyContract")

# Deploy to network
skill.deploy(network="sepolia", script="deploy.js")

# Run custom task
skill.run_task("accounts")

# Verify contract on Etherscan
skill.verify_contract(
    address="0x...",
    contract="contracts/MyToken.sol:MyToken",
    network="mainnet"
)
```

## Configuration

```json
{
    "project_path": "./hardhat-project",
    "default_network": "hardhat",
    "networks": {
        "sepolia": {
            "url": "https://sepolia.infura.io/v3/YOUR_KEY",
            "accounts": ["PRIVATE_KEY"]
        }
    },
    "etherscan_api_key": "YOUR_ETHERSCAN_KEY"
}
```

## Methods

- `init_project(name, template)`: Initialize new Hardhat project
- `compile_contracts(optimizer, runs)`: Compile Solidity contracts
- `test(grep, verbose)`: Run test suite
- `deploy(network, script)`: Deploy contracts
- `run_task(task_name)`: Run Hardhat task
- `verify_contract(address, contract, network)`: Verify on Etherscan
- `clean()`: Clean build artifacts
- `node_start()`: Start local Hardhat node
- `run_script(script, network)`: Run deployment/script

## Testing

```bash
python test_skill.py
```

## Requirements

- Python 3.8+
- Node.js 16+
- Hardhat 2.10+
- npm or yarn

## License

MIT
