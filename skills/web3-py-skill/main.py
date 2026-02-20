"""
Web3.py Skill - Comprehensive Ethereum development toolkit using Web3.py.
Use when developing blockchain applications, interacting with smart contracts, 
or when user mentions 'Ethereum', 'Web3', 'blockchain'.
"""

import json
import os
import time
import secrets
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from decimal import Decimal
from dataclasses import dataclass
from pathlib import Path

from web3 import Web3, HTTPProvider, WebsocketProvider, IPCProvider
from web3.middleware import geth_poa_middleware
from web3.types import TxParams, Wei, ENS
from web3.contract import Contract
from eth_account import Account
from eth_account.hdaccount import generate_mnemonic, seed_from_mnemonic
from eth_account.datastructures import SignedMessage, SignedTransaction
from eth_utils import to_checksum_address, is_address, is_checksum_address, keccak
from eth_utils.address import to_normalized_address
from eth_abi import encode, decode
from hexbytes import HexBytes


@dataclass
class Wallet:
    """Represents an Ethereum wallet."""
    address: str
    private_key: str
    mnemonic: Optional[str] = None
    path: Optional[str] = None


class Web3PySkill:
    """
    Web3.py-based Ethereum development skill with wallet management,
    contract deployment, and ENS resolution capabilities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Web3.py Skill with configuration.
        
        Args:
            config_path: Path to configuration JSON file
        """
        self.config = self._load_config(config_path)
        self.w3: Optional[Web3] = None
        self.account: Optional[Account] = None
        self._wallets: Dict[str, Wallet] = {}
        self._contracts: Dict[str, Contract] = {}
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from JSON file."""
        default_config = {
            "network": "mainnet",
            "default_gas_limit": 21000,
            "max_gas_price_gwei": 100,
            "confirmations": 1,
            "timeout": 120,
            "provider_type": "http"
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                default_config.update(config)
        
        # Load private key from environment if specified
        if default_config.get("private_key_env"):
            default_config["private_key"] = os.getenv(
                default_config["private_key_env"], 
                default_config.get("private_key", "")
            )
            
        return default_config
    
    def connect(self, rpc_url: Optional[str] = None, 
                provider_type: Optional[str] = None, **kwargs) -> bool:
        """
        Connect to Ethereum network.
        
        Args:
            rpc_url: RPC endpoint URL
            provider_type: 'http', 'websocket', or 'ipc'
            **kwargs: Additional provider options
            
        Returns:
            bool: True if connection successful
        """
        url = rpc_url or self.config.get("rpc_url")
        provider = provider_type or self.config.get("provider_type", "http")
        
        if not url and provider != "ipc":
            raise ValueError("RPC URL required for HTTP/WebSocket providers")
        
        # Create provider
        if provider == "http":
            self.w3 = Web3(HTTPProvider(url, **kwargs))
        elif provider == "websocket":
            self.w3 = Web3(WebsocketProvider(url, **kwargs))
        elif provider == "ipc":
            ipc_path = url or kwargs.get("ipc_path", "~/.ethereum/geth.ipc")
            self.w3 = Web3(IPCProvider(ipc_path))
        else:
            raise ValueError(f"Unknown provider type: {provider}")
        
        # Add middleware for POA chains (Polygon, BSC, etc.)
        if "geth_poa" in self.config.get("middlewares", []):
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Load account if private key available
        if self.config.get("private_key"):
            self.import_wallet(self.config["private_key"])
        
        return self.is_connected()
    
    def is_connected(self) -> bool:
        """Check if connected to Ethereum node."""
        return self.w3 is not None and self.w3.is_connected()
    
    def disconnect(self) -> None:
        """Disconnect from Ethereum node."""
        if self.w3:
            if hasattr(self.w3.provider, 'disconnect'):
                self.w3.provider.disconnect()
            self.w3 = None
    
    # Wallet Management
    
    def create_wallet(self, password: Optional[str] = None,
                      num_words: int = 12) -> Dict[str, str]:
        """
        Create new Ethereum wallet.
        
        Args:
            password: Optional password for encryption
            num_words: Mnemonic word count (12 or 24)
            
        Returns:
            Dictionary with address, private_key, mnemonic
        """
        # Generate mnemonic
        mnemonic = generate_mnemonic(num_words=num_words, lang="english")
        
        # Create account from mnemonic
        Account.enable_unaudited_hdwallet_features()
        account = Account.from_mnemonic(mnemonic)
        
        wallet = Wallet(
            address=account.address,
            private_key=account.key.hex(),
            mnemonic=mnemonic,
            path="m/44'/60'/0'/0/0"
        )
        
        self._wallets[account.address] = wallet
        
        return {
            "address": wallet.address,
            "private_key": wallet.private_key,
            "mnemonic": wallet.mnemonic,
            "path": wallet.path
        }
    
    def import_wallet(self, private_key: str, name: Optional[str] = None) -> Dict[str, str]:
        """
        Import wallet from private key.
        
        Args:
            private_key: Private key (with or without 0x prefix)
            name: Optional name for the wallet
            
        Returns:
            Dictionary with address and private_key
        """
        # Remove 0x prefix if present
        private_key = private_key.strip()
        if private_key.startswith("0x"):
            private_key = private_key[2:]
        
        account = Account.from_key(private_key)
        
        wallet = Wallet(
            address=account.address,
            private_key=private_key
        )
        
        wallet_key = name or account.address
        self._wallets[wallet_key] = wallet
        
        # Set as active account
        self.account = account
        
        return {
            "address": account.address,
            "private_key": private_key
        }
    
    def import_wallet_from_mnemonic(self, mnemonic: str, 
                                    path: str = "m/44'/60'/0'/0/0",
                                    name: Optional[str] = None) -> Dict[str, str]:
        """
        Import wallet from mnemonic phrase.
        
        Args:
            mnemonic: BIP39 mnemonic phrase
            path: Derivation path
            name: Optional wallet name
            
        Returns:
            Dictionary with address and private_key
        """
        Account.enable_unaudited_hdwallet_features()
        account = Account.from_mnemonic(mnemonic, account_path=path)
        
        wallet = Wallet(
            address=account.address,
            private_key=account.key.hex(),
            mnemonic=mnemonic,
            path=path
        )
        
        wallet_key = name or account.address
        self._wallets[wallet_key] = wallet
        self.account = account
        
        return {
            "address": wallet.address,
            "private_key": account.key.hex()
        }
    
    def get_wallet(self, name_or_address: Optional[str] = None) -> Optional[Wallet]:
        """
        Get wallet by name or address.
        
        Args:
            name_or_address: Wallet name or address (uses active if None)
            
        Returns:
            Wallet object or None
        """
        if name_or_address:
            return self._wallets.get(name_or_address)
        
        if self.account:
            return self._wallets.get(self.account.address)
        
        return None
    
    def list_wallets(self) -> List[Dict[str, str]]:
        """List all imported wallets."""
        return [
            {
                "address": w.address,
                "has_mnemonic": w.mnemonic is not None,
                "path": w.path
            }
            for w in self._wallets.values()
        ]
    
    # ENS Resolution
    
    def resolve_ens(self, name: str) -> Optional[str]:
        """
        Resolve ENS name to Ethereum address.
        
        Args:
            name: ENS name (e.g., 'vitalik.eth')
            
        Returns:
            Ethereum address or None
        """
        if not self.w3:
            raise ConnectionError("Not connected to Ethereum node")
        
        try:
            address = self.w3.ens.address(name)
            return address
        except Exception:
            return None
    
    def reverse_resolve_ens(self, address: str) -> Optional[str]:
        """
        Reverse resolve Ethereum address to ENS name.
        
        Args:
            address: Ethereum address
            
        Returns:
            ENS name or None
        """
        if not self.w3:
            raise ConnectionError("Not connected to Ethereum node")
        
        try:
            name = self.w3.ens.name(to_checksum_address(address))
            return name
        except Exception:
            return None
    
    def setup_ens(self, ens_address: Optional[str] = None) -> None:
        """
        Configure ENS with custom resolver.
        
        Args:
            ens_address: Custom ENS registry address
        """
        if not self.w3:
            raise ConnectionError("Not connected")
        
        if ens_address:
            self.w3.ens = ENS.from_web3(self.w3, addr=to_checksum_address(ens_address))
    
    # Contract Operations
    
    def get_contract_instance(self, address: str, 
                              abi: Union[str, List, Dict]) -> Contract:
        """
        Get contract instance.
        
        Args:
            address: Contract address
            abi: Contract ABI
            
        Returns:
            Contract instance
        """
        if not self.w3:
            raise ConnectionError("Not connected")
        
        if isinstance(abi, str):
            abi = json.loads(abi)
        
        contract = self.w3.eth.contract(
            address=to_checksum_address(address),
            abi=abi
        )
        
        return contract
    
    def deploy_contract(self, abi: Union[str, List, Dict],
                        bytecode: str,
                        constructor_args: Optional[List] = None,
                        gas: Optional[int] = None,
                        gas_price: Optional[int] = None,
                        wait: bool = True) -> str:
        """
        Deploy smart contract.
        
        Args:
            abi: Contract ABI
            bytecode: Contract bytecode
            constructor_args: Constructor arguments
            gas: Gas limit
            gas_price: Gas price in wei
            wait: Wait for confirmation
            
        Returns:
            Contract address
        """
        if not self.w3:
            raise ConnectionError("Not connected")
        
        if not self.account:
            raise ValueError("No account loaded for deployment")
        
        if isinstance(abi, str):
            abi = json.loads(abi)
        
        Contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)
        
        # Build constructor transaction
        constructor = Contract.constructor(*(constructor_args or []))
        
        tx_params = {
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': gas or self.config.get("contracts", {}).get("deployment_gas_limit", 5000000),
            'gasPrice': gas_price or self.w3.eth.gas_price
        }
        
        transaction = constructor.build_transaction(tx_params)
        
        # Sign and send
        signed = self.account.sign_transaction(transaction)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        
        if wait:
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt['contractAddress']
        
        return tx_hash.hex()
    
    def estimate_deployment_gas(self, abi: Union[str, List, Dict],
                                 bytecode: str,
                                 constructor_args: Optional[List] = None) -> int:
        """
        Estimate gas for contract deployment.
        
        Args:
            abi: Contract ABI
            bytecode: Contract bytecode
            constructor_args: Constructor arguments
            
        Returns:
            Estimated gas amount
        """
        if not self.w3:
            raise ConnectionError("Not connected")
        
        if not self.account:
            raise ValueError("No account loaded")
        
        if isinstance(abi, str):
            abi = json.loads(abi)
        
        Contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)
        constructor = Contract.constructor(*(constructor_args or []))
        
        gas_estimate = constructor.estimate_gas({'from': self.account.address})
        return gas_estimate
    
    # Cryptographic Operations
    
    def sign_message(self, message: Union[str, bytes],
                     wallet_name: Optional[str] = None) -> SignedMessage:
        """
        Sign message with wallet.
        
        Args:
            message: Message to sign
            wallet_name: Wallet to use (active wallet if None)
            
        Returns:
            SignedMessage object
        """
        wallet = self.get_wallet(wallet_name) if wallet_name else None
        
        if wallet:
            account = Account.from_key(wallet.private_key)
        elif self.account:
            account = self.account
        else:
            raise ValueError("No wallet available for signing")
        
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        return account.sign_message(message)
    
    def sign_typed_data(self, domain: Dict, types: Dict, 
                        value: Dict,
                        wallet_name: Optional[str] = None) -> SignedMessage:
        """
        Sign typed data (EIP-712).
        
        Args:
            domain: EIP-712 domain
            types: Type definitions
            value: Data to sign
            wallet_name: Wallet to use
            
        Returns:
            SignedMessage object
        """
        wallet = self.get_wallet(wallet_name) if wallet_name else None
        
        if wallet:
            account = Account.from_key(wallet.private_key)
        elif self.account:
            account = self.account
        else:
            raise ValueError("No wallet available for signing")
        
        return account.sign_typed_data(domain, types, value)
    
    @staticmethod
    def verify_signature(message: Union[str, bytes], 
                         signature: Union[str, bytes],
                         address: str) -> bool:
        """
        Verify message signature.
        
        Args:
            message: Original message
            signature: Signature
            address: Signer address
            
        Returns:
            True if signature is valid
        """
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        if isinstance(signature, str):
            if signature.startswith("0x"):
                signature = signature[2:]
            signature = bytes.fromhex(signature)
        
        try:
            recovered = Account.recover_message(message, signature=signature)
            return recovered.lower() == address.lower()
        except Exception:
            return False
    
    # Transaction Operations
    
    def send_transaction(self, to: str, value: int = 0,
                         data: str = "0x", gas: Optional[int] = None,
                         gas_price: Optional[int] = None,
                         wait: bool = True) -> str:
        """
        Send transaction.
        
        Args:
            to: Recipient address
            value: Amount in wei
            data: Transaction data
            gas: Gas limit
            gas_price: Gas price in wei
            wait: Wait for confirmation
            
        Returns:
            Transaction hash
        """
        if not self.w3:
            raise ConnectionError("Not connected")
        
        if not self.account:
            raise ValueError("No account loaded")
        
        transaction: TxParams = {
            'to': to_checksum_address(to),
            'value': value,
            'data': data,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'chainId': self.w3.eth.chain_id
        }
        
        if gas:
            transaction['gas'] = gas
        else:
            transaction['gas'] = self.w3.eth.estimate_gas(transaction)
        
        if gas_price:
            transaction['gasPrice'] = gas_price
        else:
            transaction['gasPrice'] = self.w3.eth.gas_price
        
        signed = self.account.sign_transaction(transaction)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        
        if wait:
            self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return tx_hash.hex()
    
    def estimate_gas(self, transaction: Dict) -> int:
        """Estimate gas for transaction."""
        if not self.w3:
            raise ConnectionError("Not connected")
        return self.w3.eth.estimate_gas(transaction)
    
    def get_transaction_receipt(self, tx_hash: str) -> Dict:
        """Get transaction receipt."""
        if not self.w3:
            raise ConnectionError("Not connected")
        return dict(self.w3.eth.get_transaction_receipt(tx_hash))
    
    # Utility Methods
    
    @staticmethod
    def to_wei(value: Union[int, float, str, Decimal], unit: str) -> int:
        """Convert value to wei."""
        return Web3.to_wei(value, unit)
    
    @staticmethod
    def from_wei(value: int, unit: str) -> Decimal:
        """Convert wei to unit."""
        return Web3.from_wei(value, unit)
    
    @staticmethod
    def to_checksum_address(address: str) -> str:
        """Convert address to checksum format."""
        return to_checksum_address(address)
    
    @staticmethod
    def is_address(address: str) -> bool:
        """Check if string is valid Ethereum address."""
        return is_address(address)
    
    @staticmethod
    def is_checksum_address(address: str) -> bool:
        """Check if address is valid checksum address."""
        return is_checksum_address(address)
    
    @staticmethod
    def keccak256(data: Union[str, bytes]) -> str:
        """Compute Keccak-256 hash."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return '0x' + keccak(data).hex()
    
    @staticmethod
    def encode_abi(types: List[str], values: List[Any]) -> str:
        """Encode ABI values."""
        return '0x' + encode(types, values).hex()
    
    @staticmethod
    def decode_abi(types: List[str], data: str) -> Tuple[Any, ...]:
        """Decode ABI data."""
        if data.startswith("0x"):
            data = data[2:]
        return decode(types, bytes.fromhex(data))
    
    def get_balance(self, address: Optional[str] = None) -> int:
        """Get ETH balance in wei."""
        if not self.w3:
            raise ConnectionError("Not connected")
        
        addr = address or (self.account.address if self.account else None)
        if not addr:
            raise ValueError("No address provided")
        
        return self.w3.eth.get_balance(to_checksum_address(addr))
    
    def get_gas_price(self) -> int:
        """Get current gas price."""
        if not self.w3:
            raise ConnectionError("Not connected")
        return self.w3.eth.gas_price
    
    def get_block_number(self) -> int:
        """Get current block number."""
        if not self.w3:
            raise ConnectionError("Not connected")
        return self.w3.eth.block_number
    
    def get_block(self, block_identifier: Union[int, str], 
                  full_transactions: bool = True) -> Dict:
        """Get block by number or hash."""
        if not self.w3:
            raise ConnectionError("Not connected")
        return dict(self.w3.eth.get_block(block_identifier, full_transactions))
    
    # Compilation (requires py-solc-x)
    
    def compile_solidity(self, source_code: str, 
                         output_format: str = "combined") -> Dict:
        """
        Compile Solidity source code.
        
        Args:
            source_code: Solidity source code
            output_format: Output format
            
        Returns:
            Compilation output
        """
        try:
            from solcx import compile_source
            
            compiled = compile_source(source_code, output_values=['abi', 'bin'])
            return compiled
        except ImportError:
            raise ImportError("py-solc-x not installed. Install with: pip install py-solc-x")
    
    def compile_solidity_file(self, file_path: str) -> Dict:
        """
        Compile Solidity file.
        
        Args:
            file_path: Path to .sol file
            
        Returns:
            Compilation output
        """
        try:
            from solcx import compile_files
            
            compiled = compile_files([file_path], output_values=['abi', 'bin'])
            return compiled
        except ImportError:
            raise ImportError("py-solc-x not installed")


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Web3.py Skill CLI")
    parser.add_argument("--config", default="config.json", help="Config file path")
    parser.add_argument("--rpc", help="RPC URL")
    parser.add_argument("command", choices=["create-wallet", "balance", "resolve", "sign"], help="Command")
    parser.add_argument("--address", help="Address")
    parser.add_argument("--message", help="Message to sign")
    parser.add_argument("--ens", help="ENS name")
    
    args = parser.parse_args()
    
    skill = Web3PySkill(args.config)
    skill.connect(args.rpc)
    
    if args.command == "create-wallet":
        wallet = skill.create_wallet()
        print(f"Address: {wallet['address']}")
        print(f"Private Key: {wallet['private_key']}")
        print(f"Mnemonic: {wallet['mnemonic']}")
    elif args.command == "balance":
        balance = skill.get_balance(args.address)
        print(f"Balance: {skill.from_wei(balance, 'ether')} ETH")
    elif args.command == "resolve":
        address = skill.resolve_ens(args.ens)
        print(f"{args.ens} -> {address}")
    elif args.command == "sign":
        signed = skill.sign_message(args.message)
        print(f"Signature: {signed.signature.hex()}")
