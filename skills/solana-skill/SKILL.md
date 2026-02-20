# Solana Skill

A comprehensive skill for Solana blockchain development, program interaction, and transaction management. Use when developing blockchain applications, interacting with smart contracts, or when user mentions 'Ethereum', 'Web3', 'blockchain'.

## Description

The Solana Skill provides a complete toolkit for Solana development including program (smart contract) interaction, transaction building, account management, and SPL token operations.

## Features

- **Program Interaction**: Call Solana programs and read account data
- **Transaction Building**: Build, sign, and send transactions
- **Account Management**: Create and manage Solana accounts
- **SPL Token Support**: Transfer and manage SPL tokens
- **RPC Operations**: Query blockchain state via JSON RPC
- **Keypair Management**: Secure keypair handling

## Installation

```bash
pip install -r requirements.txt
```

Copy `config.example.json` to `config.json` and configure your settings.

## Usage

```python
from main import SolanaSkill

# Initialize skill
skill = SolanaSkill("config.json")

# Connect to Solana cluster
skill.connect("https://api.mainnet-beta.solana.com")

# Get account balance
balance = skill.get_balance("YourPublicKey")

# Send SOL
tx_signature = skill.transfer_sol(
    to="RecipientPublicKey",
    amount=0.1  # In SOL
)

# Interact with program
instruction_data = skill.build_instruction_data("instruction_name", [arg1, arg2])
tx = skill.build_transaction([
    skill.create_instruction(program_id, keys, instruction_data)
])
signature = skill.send_transaction(tx)

# SPL Token transfer
token_signature = skill.transfer_token(
    mint="TokenMintAddress",
    to="RecipientPublicKey",
    amount=100
)
```

## Configuration

```json
{
    "network": "mainnet-beta",
    "rpc_url": "https://api.mainnet-beta.solana.com",
    "private_key": "YOUR_BASE58_PRIVATE_KEY",
    "commitment": "confirmed",
    "timeout": 30
}
```

## Methods

- `connect(rpc_url)`: Connect to Solana cluster
- `get_balance(public_key)`: Get SOL balance
- `transfer_sol(to, amount)`: Send SOL
- `build_instruction_data(name, args)`: Build instruction data
- `create_instruction(program_id, keys, data)`: Create instruction
- `build_transaction(instructions)`: Build transaction
- `send_transaction(transaction)`: Send signed transaction
- `create_account(lamports, space, owner)`: Create new account
- `get_account_info(public_key)`: Get account data
- `transfer_token(mint, to, amount)`: Transfer SPL tokens

## Testing

```bash
python test_skill.py
```

## Requirements

- Python 3.8+
- solana-py >= 0.30.0
- solders >= 0.18.0
- base58 >= 2.1.0

## License

MIT
