# Ethereum Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Web3.py](https://img.shields.io/badge/web3.py-6.0+-orange.svg)](https://web3py.readthedocs.io/)

A comprehensive toolkit for Ethereum blockchain development. Use when developing blockchain applications, interacting with smart contracts, or when user mentions 'Ethereum', 'Web3', 'blockchain'.

## Features

- **Multi-Network Support**: Mainnet, Testnets (Goerli, Sepolia), Local networks
- **Smart Contract Interaction**: Read state and execute transactions
- **Transaction Management**: Send ETH and tokens with gas optimization
- **Event Listening**: Real-time event monitoring with callbacks
- **Account Management**: Secure key handling and multiple wallet support
- **Gas Optimization**: Automatic gas price estimation and limits
- **ENS Support**: Resolve Ethereum Name Service domains

## Installation

```bash
# Clone the skill
git clone https://github.com/your-repo/ethereum-skill.git
cd ethereum-skill

# Install dependencies
pip install -r requirements.txt

# Configure
cp config.example.json config.json
# Edit config.json with your settings
```

## Quick Start

```python
from main import EthereumSkill

# Initialize
skill = EthereumSkill("config.json")

# Connect to network
skill.connect("https://mainnet.infura.io/v3/YOUR_API_KEY")

# Check balance
balance = skill.get_balance("0xYourAddress")
print(f"Balance: {skill.from_wei(balance, 'ether')} ETH")

# Send transaction
tx_hash = skill.send_transaction(
    to="0xRecipientAddress",
    value=skill.to_wei(0.1, "ether")
)
print(f"Transaction: {tx_hash}")
```

## Documentation

See [SKILL.md](SKILL.md) for detailed API documentation.

## Testing

```bash
python test_skill.py
```

## Security

- Never commit private keys
- Use environment variables for sensitive data
- Validate all transaction parameters
- Test on testnets before mainnet

## License

MIT License - see LICENSE file for details.
