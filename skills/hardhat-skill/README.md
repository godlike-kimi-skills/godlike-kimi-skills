# Hardhat Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Hardhat](https://img.shields.io/badge/Hardhat-2.10+-blue.svg)](https://hardhat.org/)

A comprehensive skill for Hardhat Ethereum development. Use when developing blockchain applications, interacting with smart contracts, or when user mentions 'Ethereum', 'Web3', 'blockchain'.

## Features

- **Project Scaffolding**: Initialize projects with templates
- **Contract Compilation**: Automated Solidity compilation
- **Test Runner**: Execute Hardhat tests with reporting
- **Deployment Manager**: Manage multi-environment deployments
- **Network Configuration**: Configure multiple networks
- **Etherscan Integration**: Automatic contract verification

## Prerequisites

- Node.js 16+
- npm or yarn
- Python 3.8+

## Installation

```bash
# Clone the skill
git clone https://github.com/your-repo/hardhat-skill.git
cd hardhat-skill

# Install Python dependencies
pip install -r requirements.txt

# Install Hardhat globally
npm install -g hardhat
```

## Quick Start

```python
from main import HardhatSkill

# Initialize skill
skill = HardhatSkill("config.json")

# Create new project
skill.init_project("my-dapp")

# Compile contracts
skill.compile_contracts()

# Run tests
skill.test()

# Deploy to local network
skill.node_start()
skill.deploy(network="localhost", script="deploy.js")
```

## Documentation

See [SKILL.md](SKILL.md) for detailed API documentation.

## Testing

```bash
python test_skill.py
```

## License

MIT License - see LICENSE file for details.
