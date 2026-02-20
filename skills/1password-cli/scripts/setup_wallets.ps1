#!/usr/bin/env pwsh
# Setup 1Password and import Kbot wallets
# Run this after installing 1Password CLI

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "1Password Wallet Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if op is available (may need fresh shell)
Write-Host "[Step 1] Checking 1Password CLI..." -ForegroundColor Yellow

try {
    $version = op --version 2>$null
    Write-Host "  [OK] 1Password CLI installed: $version" -ForegroundColor Green
} catch {
    Write-Host "  [WARNING] op command not found in PATH" -ForegroundColor Yellow
    Write-Host "  Please restart PowerShell or run: refreshenv" -ForegroundColor Yellow
    Write-Host ""
}

# Step 2: Check if user is signed in
Write-Host "[Step 2] Checking sign-in status..." -ForegroundColor Yellow

$signedIn = $false
try {
    $vaults = op vault list 2>$null
    if ($vaults) {
        Write-Host "  [OK] Already signed in!" -ForegroundColor Green
        $signedIn = $true
    }
} catch {
    Write-Host "  [INFO] Not signed in yet" -ForegroundColor Cyan
}

if (-not $signedIn) {
    Write-Host ""
    Write-Host "  To sign in, run one of these commands:" -ForegroundColor Cyan
    Write-Host "    op signin                    # Standard sign-in" -ForegroundColor White
    Write-Host "    op signin --biometric       # With fingerprint/face" -ForegroundColor White
    Write-Host ""
    Write-Host "  Then run this script again." -ForegroundColor Yellow
    exit
}

# Step 3: Import wallets
Write-Host "[Step 3] Importing wallet secrets to 1Password..." -ForegroundColor Yellow

$walletFile = "D:\kimi\memory\state\kbot_wallets.json"
if (-not (Test-Path $walletFile)) {
    Write-Host "  [ERROR] Wallet file not found!" -ForegroundColor Red
    exit 1
}

$walletData = Get-Content $walletFile | ConvertFrom-Json

Write-Host ""
Write-Host "  Found wallets:" -ForegroundColor Cyan
Write-Host "    Base:    $($walletData.wallets.base.address)" -ForegroundColor Gray
Write-Host "    Solana:  $($walletData.wallets.solana.address)" -ForegroundColor Gray
Write-Host ""

Write-Host "  This will create secure items in 1Password:" -ForegroundColor Yellow
Write-Host "    - Kbot Base Wallet (with private key)" -ForegroundColor White
Write-Host "    - Kbot Solana Wallet (with private key)" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "  Continue? (yes/no)"

if ($confirm -ne "yes") {
    Write-Host "  Cancelled." -ForegroundColor Yellow
    exit
}

# Create Base wallet item
Write-Host ""
Write-Host "  Creating Base wallet item..." -ForegroundColor Yellow
try {
    op item create `
        --category="Secure Note" `
        --title="Kbot Base Wallet" `
        --vault="Private" `
        "address=$($walletData.wallets.base.address)" `
        "private_key=$($walletData.wallets.base.private_key)" `
        "network=Base Mainnet" `
        "chain_id=8453" `
        2>$null
    
    Write-Host "    [OK] Base wallet imported" -ForegroundColor Green
} catch {
    Write-Host "    [ERROR] Failed to import Base wallet" -ForegroundColor Red
}

# Create Solana wallet item
Write-Host ""
Write-Host "  Creating Solana wallet item..." -ForegroundColor Yellow
try {
    op item create `
        --category="Secure Note" `
        --title="Kbot Solana Wallet" `
        --vault="Private" `
        "address=$($walletData.wallets.solana.address)" `
        "private_key=$($walletData.wallets.solana.private_key)" `
        "network=Solana Mainnet" `
        2>$null
    
    Write-Host "    [OK] Solana wallet imported" -ForegroundColor Green
} catch {
    Write-Host "    [ERROR] Failed to import Solana wallet" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Verify items in 1Password app" -ForegroundColor White
Write-Host "  2. Delete plaintext backup (optional):" -ForegroundColor White
Write-Host "     Remove-Item D:\kimi\memory\state\kbot_wallets.json" -ForegroundColor Gray
Write-Host "  3. Generate payment info:" -ForegroundColor White
Write-Host "     python D:\kimi\skills\1password-cli\scripts\generate_payment_info.py" -ForegroundColor Gray
Write-Host ""
Write-Host "[WARNING] Keep your 1Password master password safe!" -ForegroundColor Yellow
Write-Host ""
