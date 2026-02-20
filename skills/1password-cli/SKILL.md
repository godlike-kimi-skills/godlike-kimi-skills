---
name: 1password-cli
version: 1.0.0
description: 1Password CLI integration for secure secret management
requires_setup: true
---

# 1Password CLI Skill

Secure password and secret management using 1Password CLI (`op`).

## Installation Status

- [x] 1Password CLI installed via winget
- [ ] User sign-in required (manual step)
- [ ] Wallet secrets imported (ready to configure)

## Setup Instructions

### Step 1: Sign in to 1Password

Open a new PowerShell window (to refresh PATH) and run:

```powershell
# Sign in to your 1Password account
op signin

# Or with biometric unlock (if enabled)
op signin --biometric
```

### Step 2: Verify Installation

```powershell
# Check version
op --version

# List vaults
op vault list
```

### Step 3: Import Kbot Wallets (CRITICAL)

After sign-in, securely import your wallet private keys:

```powershell
# Read wallet data and create secure items
$walletData = Get-Content D:\kimi\memory\state\kbot_wallets.json | ConvertFrom-Json

# Create Base wallet item
op item create `
    --category="Secure Note" `
    --title="Kbot Base Wallet" `
    --vault="Private" `
    "address=$($walletData.wallets.base.address)" `
    "private_key=$($walletData.wallets.base.private_key)" `
    "network=Base Mainnet"

# Create Solana wallet item  
op item create `
    --category="Secure Note" `
    --title="Kbot Solana Wallet" `
    --vault="Private" `
    "address=$($walletData.wallets.solana.address)" `
    "private_key=$($walletData.wallets.solana.private_key)` `
    "network=Solana Mainnet"
```

## Usage

### Retrieve Wallet Address (for payments)

```powershell
# Get Base address (safe to share)
op item get "Kbot Base Wallet" --fields=address

# Get Solana address (safe to share)
op item get "Kbot Solana Wallet" --fields=address
```

### Retrieve Private Key (for transactions)

```powershell
# Get Base private key (KEEP SECRET)
op item get "Kbot Base Wallet" --fields=private_key

# Get Solana private key (KEEP SECRET)
op item get "Kbot Solana Wallet" --fields=private_key
```

### Generate Payment Instructions

```powershell
# Create public payment info (no secrets)
python D:\kimi\skills\1password-cli\scripts\generate_payment_info.py
```

## Security Best Practices

1. **NEVER commit secrets to Git**
   - 1Password vaults are the single source of truth
   - Keep `kbot_wallets.json` backups encrypted

2. **Use biometric unlock when possible**
   - Faster and more secure than typing master password

3. **Rotate secrets if compromised**
   - Create new wallets and transfer funds
   - Update 1Password items immediately

4. **Regular backups**
   - 1Password cloud is primary backup
   - Keep offline emergency kit in safe place

## CLI Commands Reference

| Command | Description |
|---------|-------------|
| `op signin` | Sign in to 1Password |
| `op vault list` | List available vaults |
| `op item list` | List items in vault |
| `op item get <name>` | Retrieve item |
| `op item create` | Create new item |
| `op item edit <name>` | Edit existing item |
| `op signout` | Sign out |

## Troubleshooting

**"op not recognized"**
- Solution: Restart PowerShell or run `refreshenv`

**"Not signed in"**
- Solution: Run `op signin` first

**"Vault not found"**
- Solution: Check vault name with `op vault list`
