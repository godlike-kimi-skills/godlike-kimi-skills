# Ethereum Skill

A comprehensive skill for Ethereum blockchain development, smart contract interaction, and transaction management. Use when developing blockchain applications, interacting with smart contracts, or when user mentions 'Ethereum', 'Web3', 'blockchain'.

## Description

The Ethereum Skill provides a complete toolkit for Ethereum development including smart contract interaction, transaction sending, event listening, and account management.

## Features

- **Smart Contract Interaction**: Call contract methods and read state
- **Transaction Management**: Send transactions with gas optimization
- **Event Listening**: Monitor contract events in real-time
- **Account Management**: Handle multiple accounts and wallet operations
- **Gas Estimation**: Automatic gas price and limit calculation
- **ENS Resolution**: Support for Ethereum Name Service

## Installation

```bash
pip install -r requirements.txt
```

Copy `config.example.json` to `config.json` and configure your settings.

## Usage

```python
from main import EthereumSkill

# Initialize skill
skill = EthereumSkill("config.json")

# Connect to Ethereum node
skill.connect("https://mainnet.infura.io/v3/YOUR_API_KEY")

# Interact with smart contract
contract = skill.load_contract("0xContractAddress", abi_json)
result = skill.call_contract_method(contract, "balanceOf", "0xAddress")

# Send transaction
tx_hash = skill.send_transaction(
    to="0xRecipientAddress",
    value=skill.to_wei(0.1, "ether"),
    gas_price=skill.get_gas_price()
)

# Listen to events
skill.listen_events(
    contract_address="0xContractAddress",
    event_name="Transfer",
    from_block="latest",
    callback=lambda event: print(event)
)
```

## Configuration

```json
{
    "network": "mainnet",
    "rpc_url": "https://mainnet.infura.io/v3/YOUR_API_KEY",
    "private_key": "YOUR_PRIVATE_KEY",
    "default_gas_limit": 21000,
    "max_gas_price_gwei": 100
}
```

## Methods

- `connect(rpc_url)`: Connect to Ethereum node
- `load_contract(address, abi)`: Load smart contract instance
- `call_contract_method(contract, method, *args)`: Call contract method
- `send_transaction(to, value, **kwargs)`: Send transaction
- `listen_events(**kwargs)`: Listen to contract events
- `to_wei(value, unit)`: Convert to wei
- `from_wei(value, unit)`: Convert from wei
- `get_gas_price()`: Get current gas price
- `get_balance(address)`: Get account balance
- `estimate_gas(transaction)`: Estimate gas for transaction

## Testing

```bash
python test_skill.py
```

## Requirements

- Python 3.8+
- web3.py >= 6.0.0
- eth-account >= 0.8.0
- eth-utils >= 2.0.0

## License

MIT
