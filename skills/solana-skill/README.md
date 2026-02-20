# Solana Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Solana](https://img.shields.io/badge/Solana-Purple.svg)](https://solana.com/)

A comprehensive toolkit for Solana blockchain development. Use when developing blockchain applications, interacting with smart contracts, or when user mentions 'Ethereum', 'Web3', 'blockchain'.

## Features

- **Multi-Cluster Support**: Mainnet-beta, Devnet, Testnet, Localnet
- **Program Interaction**: Call on-chain programs and read accounts
- **Transaction Building**: Create complex transactions with multiple instructions
- **Account Management**: Create, fund, and manage accounts
- **SPL Token Support**: Full SPL token operations
- **RPC Operations**: Complete JSON RPC API coverage
- **Keypair Management**: Secure keypair generation and storage

## Installation

```bash
# Clone the skill
git clone https://github.com/your-repo/solana-skill.git
cd solana-skill

# Install dependencies
pip install -r requirements.txt

# Configure
cp config.example.json config.json
# Edit config.json with your settings
```

## Quick Start

```python
from main import SolanaSkill

# Initialize
skill = SolanaSkill("config.json")

# Connect to cluster
skill.connect("https://api.devnet.solana.com")

# Check balance
balance = skill.get_balance("YourPublicKey")
print(f"Balance: {balance} SOL")

# Send SOL
tx_signature = skill.transfer_sol(
    to="RecipientPublicKey",
    amount=0.1
)
print(f"Transaction: {tx_signature}")
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
- Test on devnet before mainnet
- Validate all transaction parameters

## License

MIT License - see LICENSE file for details.
