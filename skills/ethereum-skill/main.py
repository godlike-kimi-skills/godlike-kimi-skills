"""
Ethereum Skill - Comprehensive Ethereum blockchain development toolkit.
Use when developing blockchain applications, interacting with smart contracts, 
or when user mentions 'Ethereum', 'Web3', 'blockchain'.
"""

import json
import os
import time
from typing import Any, Callable, Dict, List, Optional, Union
from decimal import Decimal

from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.types import TxParams, Wei
from eth_account import Account
from eth_account.datastructures import SignedTransaction
from eth_utils import to_checksum_address, is_address, is_checksum_address
from hexbytes import HexBytes


class EthereumSkill:
    """
    Ethereum blockchain development skill with smart contract interaction,
    transaction management, and event listening capabilities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Ethereum Skill with configuration.
        
        Args:
            config_path: Path to configuration JSON file
        """
        self.config = self._load_config(config_path)
        self.w3: Optional[Web3] = None
        self.account: Optional[Account] = None
        self.contracts: Dict[str, Any] = {}
        self._event_listeners: Dict[str, Any] = {}
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from JSON file."""
        default_config = {
            "network": "mainnet",
            "default_gas_limit": 21000,
            "max_gas_price_gwei": 100,
            "confirmations": 1,
            "timeout": 120
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
    
    def connect(self, rpc_url: Optional[str] = None, **kwargs) -> bool:
        """
        Connect to Ethereum node.
        
        Args:
            rpc_url: RPC endpoint URL (overrides config)
            **kwargs: Additional Web3 connection options
            
        Returns:
            bool: True if connection successful
        """
        url = rpc_url or self.config.get("rpc_url")
        if not url:
            raise ValueError("RPC URL not provided in config or arguments")
        
        self.w3 = Web3(Web3.HTTPProvider(url, **kwargs))
        
        # Add middleware for POA chains
        if "geth_poa" in self.config.get("middlewares", []):
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Load account if private key available
        if self.config.get("private_key"):
            self._load_account(self.config["private_key"])
        
        return self.is_connected()
    
    def connect_websocket(self, ws_url: str, **kwargs) -> bool:
        """
        Connect via WebSocket for real-time updates.
        
        Args:
            ws_url: WebSocket endpoint URL
            **kwargs: Additional Web3 connection options
            
        Returns:
            bool: True if connection successful
        """
        self.w3 = Web3(Web3.WebsocketProvider(ws_url, **kwargs))
        
        if "geth_poa" in self.config.get("middlewares", []):
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        if self.config.get("private_key"):
            self._load_account(self.config["private_key"])
            
        return self.is_connected()
    
    def is_connected(self) -> bool:
        """Check if connected to Ethereum node."""
        return self.w3 is not None and self.w3.is_connected()
    
    def _load_account(self, private_key: str) -> None:
        """Load account from private key."""
        # Remove 0x prefix if present
        private_key = private_key.strip()
        if private_key.startswith("0x"):
            private_key = private_key[2:]
        
        self.account = Account.from_key(private_key)
    
    def get_address(self) -> Optional[str]:
        """Get loaded account address."""
        return self.account.address if self.account else None
    
    def load_contract(self, address: str, abi: Union[str, List, Dict], 
                      name: Optional[str] = None) -> Any:
        """
        Load smart contract instance.
        
        Args:
            address: Contract address
            abi: Contract ABI (JSON string, dict, or list)
            name: Optional name to reference the contract later
            
        Returns:
            Contract instance
        """
        if not self.w3:
            raise ConnectionError("Not connected to Ethereum node")
        
        # Parse ABI if string
        if isinstance(abi, str):
            abi = json.loads(abi)
        
        contract_address = to_checksum_address(address)
        contract = self.w3.eth.contract(address=contract_address, abi=abi)
        
        if name:
            self.contracts[name] = contract
            
        return contract
    
    def load_contract_from_file(self, address: str, abi_path: str,
                                name: Optional[str] = None) -> Any:
        """Load contract ABI from file."""
        with open(abi_path, 'r') as f:
            abi = json.load(f)
        return self.load_contract(address, abi, name)
    
    def call_contract_method(self, contract: Any, method: str, 
                             *args, **kwargs) -> Any:
        """
        Call contract read method.
        
        Args:
            contract: Contract instance or name
            method: Method name
            *args: Method arguments
            **kwargs: Additional call options
            
        Returns:
            Method return value
        """
        if not self.w3:
            raise ConnectionError("Not connected to Ethereum node")
        
        # Resolve contract by name if string
        if isinstance(contract, str):
            contract = self.contracts.get(contract)
            if not contract:
                raise ValueError(f"Contract '{contract}' not found")
        
        contract_fn = getattr(contract.functions, method)
        result = contract_fn(*args).call(kwargs)
        return result
    
    def build_transaction(self, contract: Any, method: str, *args,
                         tx_params: Optional[Dict] = None, **kwargs) -> Dict:
        """
        Build contract transaction.
        
        Args:
            contract: Contract instance
            method: Method name
            *args: Method arguments
            tx_params: Transaction parameters
            **kwargs: Additional build options
            
        Returns:
            Transaction dictionary
        """
        if not self.w3:
            raise ConnectionError("Not connected to Ethereum node")
        
        if isinstance(contract, str):
            contract = self.contracts.get(contract)
        
        contract_fn = getattr(contract.functions, method)
        transaction = contract_fn(*args).build_transaction({
            'from': self.get_address(),
            'nonce': self.get_transaction_count(),
            **(tx_params or {})
        })
        
        return transaction
    
    def send_contract_transaction(self, contract: Any, method: str, *args,
                                   value: int = 0, gas: Optional[int] = None,
                                   gas_price: Optional[int] = None,
                                   wait: bool = True) -> str:
        """
        Execute contract write method.
        
        Args:
            contract: Contract instance or name
            method: Method name
            *args: Method arguments
            value: ETH value to send
            gas: Gas limit (auto-estimated if None)
            gas_price: Gas price in wei (auto if None)
            wait: Whether to wait for confirmation
            
        Returns:
            Transaction hash
        """
        if not self.account:
            raise ValueError("No account loaded for signing")
        
        tx_params = {
            'value': value,
            'from': self.get_address()
        }
        
        if gas:
            tx_params['gas'] = gas
        if gas_price:
            tx_params['gasPrice'] = gas_price
        
        transaction = self.build_transaction(contract, method, *args, tx_params)
        
        # Estimate gas if not provided
        if 'gas' not in transaction:
            transaction['gas'] = self.estimate_gas(transaction)
        
        # Set gas price if not provided
        if 'gasPrice' not in transaction:
            transaction['gasPrice'] = self.get_gas_price()
        
        signed_tx = self.sign_transaction(transaction)
        tx_hash = self.send_raw_transaction(signed_tx.rawTransaction)
        
        if wait:
            self.wait_for_confirmation(tx_hash)
        
        return tx_hash.hex()
    
    def send_transaction(self, to: str, value: int = 0, 
                         data: str = "0x", gas: Optional[int] = None,
                         gas_price: Optional[int] = None,
                         wait: bool = True) -> str:
        """
        Send ETH transaction.
        
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
        if not self.account:
            raise ValueError("No account loaded for signing")
        
        transaction: TxParams = {
            'to': to_checksum_address(to),
            'value': value,
            'data': data,
            'nonce': self.get_transaction_count(),
            'chainId': self.w3.eth.chain_id
        }
        
        if gas:
            transaction['gas'] = gas
        else:
            transaction['gas'] = self.estimate_gas(transaction)
        
        if gas_price:
            transaction['gasPrice'] = gas_price
        else:
            transaction['gasPrice'] = self.get_gas_price()
        
        signed_tx = self.sign_transaction(transaction)
        tx_hash = self.send_raw_transaction(signed_tx.rawTransaction)
        
        if wait:
            self.wait_for_confirmation(tx_hash)
        
        return tx_hash.hex()
    
    def sign_transaction(self, transaction: Dict) -> SignedTransaction:
        """Sign transaction with loaded account."""
        if not self.account:
            raise ValueError("No account loaded")
        return self.account.sign_transaction(transaction)
    
    def send_raw_transaction(self, signed_tx: bytes) -> HexBytes:
        """Send signed raw transaction."""
        if not self.w3:
            raise ConnectionError("Not connected")
        return self.w3.eth.send_raw_transaction(signed_tx)
    
    def wait_for_confirmation(self, tx_hash: HexBytes, 
                              timeout: Optional[int] = None) -> Dict:
        """
        Wait for transaction confirmation.
        
        Args:
            tx_hash: Transaction hash
            timeout: Timeout in seconds
            
        Returns:
            Transaction receipt
        """
        if not self.w3:
            raise ConnectionError("Not connected")
        
        timeout = timeout or self.config.get("timeout", 120)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
        
        # Wait for confirmations
        confirmations = self.config.get("confirmations", 1)
        if confirmations > 1:
            start_block = receipt['blockNumber']
            while True:
                current_block = self.w3.eth.block_number
                if current_block - start_block >= confirmations - 1:
                    break
                time.sleep(1)
        
        return receipt
    
    def get_transaction_count(self, address: Optional[str] = None) -> int:
        """Get transaction nonce for address."""
        if not self.w3:
            raise ConnectionError("Not connected")
        addr = address or self.get_address()
        return self.w3.eth.get_transaction_count(addr, 'pending')
    
    def get_balance(self, address: Optional[str] = None) -> int:
        """Get ETH balance in wei."""
        if not self.w3:
            raise ConnectionError("Not connected")
        addr = address or self.get_address()
        return self.w3.eth.get_balance(to_checksum_address(addr))
    
    def get_gas_price(self) -> int:
        """Get current gas price in wei."""
        if not self.w3:
            raise ConnectionError("Not connected")
        
        gas_price = self.w3.eth.gas_price
        max_gwei = self.config.get("max_gas_price_gwei", 100)
        max_wei = self.to_wei(max_gwei, "gwei")
        
        return min(gas_price, max_wei)
    
    def estimate_gas(self, transaction: Dict) -> int:
        """Estimate gas for transaction."""
        if not self.w3:
            raise ConnectionError("Not connected")
        
        try:
            return self.w3.eth.estimate_gas(transaction)
        except Exception as e:
            # Return default if estimation fails
            return self.config.get("default_gas_limit", 21000)
    
    def listen_events(self, contract_address: str, event_name: str,
                      from_block: Union[int, str] = "latest",
                      to_block: Union[int, str] = "latest",
                      filters: Optional[Dict] = None,
                      callback: Optional[Callable] = None,
                      poll_interval: int = 2) -> str:
        """
        Listen to contract events.
        
        Args:
            contract_address: Contract address
            event_name: Event name to listen for
            from_block: Starting block number or "latest"
            to_block: Ending block number or "latest"
            filters: Event filters
            callback: Callback function for events
            poll_interval: Polling interval in seconds
            
        Returns:
            Listener ID
        """
        if not self.w3:
            raise ConnectionError("Not connected")
        
        listener_id = f"{contract_address}_{event_name}_{int(time.time())}"
        
        contract = self.w3.eth.contract(
            address=to_checksum_address(contract_address),
            abi=[]  # Minimal ABI for event listening
        )
        
        event_filter = contract.events[event_name].create_filter(
            fromBlock=from_block,
            toBlock=to_block,
            argument_filters=filters or {}
        )
        
        self._event_listeners[listener_id] = {
            'filter': event_filter,
            'callback': callback,
            'running': True
        }
        
        # Start polling in background
        import threading
        def poll_events():
            while self._event_listeners[listener_id]['running']:
                try:
                    events = event_filter.get_new_entries()
                    for event in events:
                        if callback:
                            callback(event)
                except Exception as e:
                    print(f"Event polling error: {e}")
                time.sleep(poll_interval)
        
        thread = threading.Thread(target=poll_events, daemon=True)
        thread.start()
        
        return listener_id
    
    def stop_listening(self, listener_id: str) -> bool:
        """Stop event listener."""
        if listener_id in self._event_listeners:
            self._event_listeners[listener_id]['running'] = False
            del self._event_listeners[listener_id]
            return True
        return False
    
    def resolve_ens(self, name: str) -> Optional[str]:
        """Resolve ENS name to address."""
        if not self.w3:
            raise ConnectionError("Not connected")
        try:
            return self.w3.ens.address(name)
        except Exception:
            return None
    
    def reverse_resolve_ens(self, address: str) -> Optional[str]:
        """Reverse resolve address to ENS name."""
        if not self.w3:
            raise ConnectionError("Not connected")
        try:
            return self.w3.ens.name(to_checksum_address(address))
        except Exception:
            return None
    
    @staticmethod
    def to_wei(value: Union[int, float, str, Decimal], unit: str) -> int:
        """Convert value to wei."""
        return Web3.to_wei(value, unit)
    
    @staticmethod
    def from_wei(value: int, unit: str) -> Decimal:
        """Convert wei to unit."""
        return Web3.from_wei(value, unit)
    
    @staticmethod
    def is_address(address: str) -> bool:
        """Check if string is valid Ethereum address."""
        return is_address(address)
    
    @staticmethod
    def is_checksum_address(address: str) -> bool:
        """Check if address is valid checksum address."""
        return is_checksum_address(address)
    
    @staticmethod
    def to_checksum_address(address: str) -> str:
        """Convert address to checksum format."""
        return to_checksum_address(address)
    
    def get_block(self, block_identifier: Union[int, str]) -> Dict:
        """Get block by number or hash."""
        if not self.w3:
            raise ConnectionError("Not connected")
        return dict(self.w3.eth.get_block(block_identifier, full_transactions=True))
    
    def get_transaction(self, tx_hash: str) -> Dict:
        """Get transaction by hash."""
        if not self.w3:
            raise ConnectionError("Not connected")
        return dict(self.w3.eth.get_transaction(tx_hash))
    
    def get_transaction_receipt(self, tx_hash: str) -> Dict:
        """Get transaction receipt."""
        if not self.w3:
            raise ConnectionError("Not connected")
        return dict(self.w3.eth.get_transaction_receipt(tx_hash))
    
    def deploy_contract(self, bytecode: str, abi: List, *constructor_args,
                        gas: Optional[int] = None, wait: bool = True) -> str:
        """
        Deploy smart contract.
        
        Args:
            bytecode: Contract bytecode
            abi: Contract ABI
            *constructor_args: Constructor arguments
            gas: Gas limit
            wait: Wait for confirmation
            
        Returns:
            Contract address
        """
        if not self.account:
            raise ValueError("No account loaded")
        
        Contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)
        transaction = Contract.constructor(*constructor_args).build_transaction({
            'from': self.get_address(),
            'nonce': self.get_transaction_count(),
            'gas': gas or self.config.get("default_gas_limit", 3000000),
            'gasPrice': self.get_gas_price()
        })
        
        signed_tx = self.sign_transaction(transaction)
        tx_hash = self.send_raw_transaction(signed_tx.rawTransaction)
        
        if wait:
            receipt = self.wait_for_confirmation(tx_hash)
            return receipt['contractAddress']
        
        return tx_hash.hex()
    
    def transfer_token(self, token_address: str, to: str, amount: int,
                       wait: bool = True) -> str:
        """
        Transfer ERC20 tokens.
        
        Args:
            token_address: Token contract address
            to: Recipient address
            amount: Token amount (in smallest unit)
            wait: Wait for confirmation
            
        Returns:
            Transaction hash
        """
        erc20_abi = [
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            }
        ]
        
        return self.send_contract_transaction(
            self.load_contract(token_address, erc20_abi),
            "transfer",
            to_checksum_address(to),
            amount,
            wait=wait
        )


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ethereum Skill CLI")
    parser.add_argument("--config", default="config.json", help="Config file path")
    parser.add_argument("--rpc", help="RPC URL")
    parser.add_argument("command", choices=["balance", "send", "call"], help="Command")
    parser.add_argument("--address", help="Address")
    parser.add_argument("--to", help="Recipient")
    parser.add_argument("--value", type=float, help="ETH value")
    parser.add_argument("--contract", help="Contract address")
    parser.add_argument("--method", help="Contract method")
    
    args = parser.parse_args()
    
    skill = EthereumSkill(args.config)
    skill.connect(args.rpc)
    
    if args.command == "balance":
        balance = skill.get_balance(args.address)
        print(f"Balance: {skill.from_wei(balance, 'ether')} ETH")
    elif args.command == "send":
        tx_hash = skill.send_transaction(args.to, skill.to_wei(args.value, "ether"))
        print(f"Transaction sent: {tx_hash}")
    elif args.command == "call":
        contract = skill.load_contract(args.contract, "[]")
        result = skill.call_contract_method(contract, args.method)
        print(f"Result: {result}")
