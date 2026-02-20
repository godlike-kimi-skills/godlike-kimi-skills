# Web3.py Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Web3.py](https://img.shields.io/badge/web3.py-6.0+-orange.svg)](https://web3py.readthedocs.io/)

A comprehensive Web3.py toolkit for Ethereum development. Use when developing blockchain applications, interacting with smart contracts, or when user mentions 'Ethereum', 'Web3', 'blockchain'.

## Features

- **Wallet Management**: HD wallet support, key derivation
- **Contract Deployment**: Compile and deploy Solidity contracts
- **ENS Integration**: Full ENS name resolution support
- **Multi-Provider**: HTTP, WebSocket, IPC connections
- **Signing & Verification**: Cryptographic operations
- **Gas Management**: Smart gas estimation and pricing

## Installation

```bash
# Clone the skill
git clone https://github.com/your-repo/web3-py-skill.git
cd web3-py-skill

# Install dependencies
pip install -r requirements.txt

# Configure
cp config.example.json config.json
# Edit config.json with your settings
```

## Quick Start

```python
from main import Web3PySkill

# Initialize
skill = Web3PySkill("config.json")

# Connect to network
skill.connect("https://mainnet.infura.io/v3/YOUR_API_KEY")

# Create wallet
wallet = skill.create_wallet()
print(f"Address: {wallet['address']}")
print(f"Mnemonic: {wallet['mnemonic']}")

# Resolve ENS
address = skill.resolve_ens("vitalik.eth")
print(f"vitalik.eth -> {address}")
```

## Documentation

See [SKILL.md](SKILL.md) for detailed API documentation.

## Testing

```bash
python test_skill.py
```

## Security

- Never store private keys in code
- Use hardware wallets for production
- Test thoroughly on testnets

## License

MIT License - see LICENSE file for details.
