# Web3.py Skill

A comprehensive skill for Web3.py-based Ethereum development with wallet management, contract deployment, and ENS resolution. Use when developing blockchain applications, interacting with smart contracts, or when user mentions 'Ethereum', 'Web3', 'blockchain'.

## Description

The Web3.py Skill provides a Python-native toolkit for Ethereum blockchain operations including wallet management, contract deployment, ENS resolution, and transaction handling.

## Features

- **Wallet Management**: Create, import, and manage Ethereum wallets
- **Contract Deployment**: Deploy smart contracts with compilation support
- **ENS Resolution**: Resolve and reverse-resolve ENS names
- **Multi-Provider Support**: HTTP, WebSocket, and IPC providers
- **Transaction Utilities**: Sign, send, and monitor transactions
- **ABI Encoding**: Automatic ABI encoding/decoding

## Installation

```bash
pip install -r requirements.txt
```

Copy `config.example.json` to `config.json` and configure your settings.

## Usage

```python
from main import Web3PySkill

# Initialize skill
skill = Web3PySkill("config.json")

# Connect to Ethereum
skill.connect("https://mainnet.infura.io/v3/YOUR_API_KEY")

# Create new wallet
wallet = skill.create_wallet()
print(f"Address: {wallet['address']}")

# Import wallet from private key
wallet = skill.import_wallet("0xprivate_key_here")

# Deploy contract
contract_address = skill.deploy_contract(
    abi=abi_json,
    bytecode=bytecode,
    constructor_args=[arg1, arg2]
)

# Resolve ENS
address = skill.resolve_ens("vitalik.eth")
ens_name = skill.reverse_resolve_ens("0xAddress")
```

## Configuration

```json
{
    "network": "mainnet",
    "rpc_url": "https://mainnet.infura.io/v3/YOUR_API_KEY",
    "private_key": "YOUR_PRIVATE_KEY",
    "default_gas_limit": 21000
}
```

## Methods

- `connect(rpc_url, provider_type)`: Connect to Ethereum
- `create_wallet()`: Generate new wallet
- `import_wallet(private_key)`: Import existing wallet
- `deploy_contract(abi, bytecode, args)`: Deploy smart contract
- `resolve_ens(name)`: Resolve ENS to address
- `reverse_resolve_ens(address)`: Reverse resolve address
- `sign_message(message)`: Sign message with wallet
- `verify_signature(message, signature, address)`: Verify signature
- `estimate_gas(transaction)`: Estimate gas cost
- `get_contract_instance(address, abi)`: Get contract instance

## Testing

```bash
python test_skill.py
```

## Requirements

- Python 3.8+
- web3 >= 6.0.0
- eth-account >= 0.8.0
- eth-ens >= 0.8.0

## License

MIT
