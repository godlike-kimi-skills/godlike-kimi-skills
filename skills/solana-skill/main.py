"""
Solana Skill - Comprehensive Solana blockchain development toolkit.
Use when developing blockchain applications, interacting with smart contracts, 
or when user mentions 'Ethereum', 'Web3', 'blockchain'.
"""

import json
import os
import base64
import struct
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

from solana.rpc.api import Client
from solana.rpc.types import TxOpts, TokenAccountOpts
from solana.rpc.commitment import Commitment, Confirmed
from solana.transaction import Transaction, TransactionInstruction, AccountMeta
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.system_program import TransferParams, transfer, create_account, CreateAccountParams
from solana.sysvar import CLOCK, RENT
from solana.spl.token.client import Token
from solana.spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
import solders
from solders.system_program import transfer as solders_transfer
from solders.transaction import Transaction as SoldersTx
from solders.message import Message
from solders.instruction import Instruction as SoldersInstruction
from solders.account_meta import AccountMeta as SoldersAccountMeta
from solders.pubkey import Pubkey
from solders.keypair import Keypair as SoldersKeypair
from solders.signature import Signature
import base58


@dataclass
class InstructionData:
    """Represents instruction data for Solana programs."""
    name: str
    args: List[Any]
    
    def serialize(self) -> bytes:
        """Serialize instruction data to bytes."""
        # Simple serialization - can be extended with proper Borsh encoding
        data = struct.pack(f"<{len(self.args)}Q", *self.args) if self.args else b""
        return data


class SolanaSkill:
    """
    Solana blockchain development skill with program interaction,
    transaction building, and account management capabilities.
    """
    
    # Token Program IDs
    TOKEN_PROGRAM_ID = PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    ASSOCIATED_TOKEN_PROGRAM_ID = PublicKey("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
    SYSTEM_PROGRAM_ID = PublicKey("11111111111111111111111111111111")
    RENT_SYSVAR = PublicKey("SysvarRent111111111111111111111111111111111")
    CLOCK_SYSVAR = PublicKey("SysvarC1ock11111111111111111111111111111111")
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Solana Skill with configuration.
        
        Args:
            config_path: Path to configuration JSON file
        """
        self.config = self._load_config(config_path)
        self.client: Optional[Client] = None
        self.keypair: Optional[Keypair] = None
        self.solders_keypair: Optional[SoldersKeypair] = None
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from JSON file."""
        default_config = {
            "network": "mainnet-beta",
            "commitment": "confirmed",
            "timeout": 30,
            "skip_preflight": False
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
        Connect to Solana cluster.
        
        Args:
            rpc_url: RPC endpoint URL (overrides config)
            **kwargs: Additional client options
            
        Returns:
            bool: True if connection successful
        """
        url = rpc_url or self.config.get("rpc_url")
        if not url:
            raise ValueError("RPC URL not provided in config or arguments")
        
        commitment = self.config.get("commitment", "confirmed")
        timeout = self.config.get("timeout", 30)
        
        self.client = Client(
            url, 
            commitment=Commitment(commitment),
            timeout=timeout
        )
        
        # Load keypair if available
        if self.config.get("private_key"):
            self._load_keypair(self.config["private_key"])
        
        return self.is_connected()
    
    def is_connected(self) -> bool:
        """Check if connected to Solana cluster."""
        if not self.client:
            return False
        try:
            # Test connection by getting slot
            self.client.get_slot()
            return True
        except Exception:
            return False
    
    def _load_keypair(self, private_key: str) -> None:
        """Load keypair from private key."""
        try:
            # Try base58 encoded key
            secret_key = base58.b58decode(private_key)
            self.keypair = Keypair.from_secret_key(secret_key)
            self.solders_keypair = SoldersKeypair.from_bytes(secret_key)
        except Exception:
            # Try base64 encoded key
            try:
                secret_key = base64.b64decode(private_key)
                self.keypair = Keypair.from_secret_key(secret_key)
                self.solders_keypair = SoldersKeypair.from_bytes(secret_key)
            except Exception as e:
                raise ValueError(f"Invalid private key format: {e}")
    
    def generate_keypair(self) -> Tuple[str, str]:
        """
        Generate new keypair.
        
        Returns:
            Tuple of (public_key, private_key)
        """
        new_keypair = Keypair()
        public_key = str(new_keypair.public_key)
        private_key = base58.b58encode(new_keypair.secret_key).decode('utf-8')
        return public_key, private_key
    
    def get_public_key(self) -> Optional[str]:
        """Get loaded keypair public key."""
        if self.keypair:
            return str(self.keypair.public_key)
        return None
    
    def get_balance(self, public_key: Optional[str] = None) -> float:
        """
        Get SOL balance.
        
        Args:
            public_key: Public key to check (uses loaded keypair if None)
            
        Returns:
            Balance in SOL
        """
        if not self.client:
            raise ConnectionError("Not connected to Solana cluster")
        
        pubkey = public_key or self.get_public_key()
        if not pubkey:
            raise ValueError("No public key provided")
        
        response = self.client.get_balance(PublicKey(pubkey))
        lamports = response['result']['value']
        return lamports / 10**9  # Convert to SOL
    
    def transfer_sol(self, to: str, amount: float, 
                     skip_preflight: Optional[bool] = None) -> str:
        """
        Send SOL to address.
        
        Args:
            to: Recipient public key
            amount: Amount in SOL
            skip_preflight: Skip transaction preflight
            
        Returns:
            Transaction signature
        """
        if not self.keypair:
            raise ValueError("No keypair loaded for signing")
        
        if not self.client:
            raise ConnectionError("Not connected")
        
        lamports = int(amount * 10**9)  # Convert to lamports
        
        # Create transfer instruction
        transfer_params = TransferParams(
            from_pubkey=self.keypair.public_key,
            to_pubkey=PublicKey(to),
            lamports=lamports
        )
        instruction = transfer(transfer_params)
        
        # Build and send transaction
        transaction = Transaction()
        transaction.add(instruction)
        
        opts = TxOpts(
            skip_preflight=skip_preflight if skip_preflight is not None 
                          else self.config.get("skip_preflight", False)
        )
        
        response = self.client.send_transaction(
            transaction, 
            self.keypair,
            opts=opts
        )
        
        return response['result']
    
    def build_instruction_data(self, instruction_name: str, 
                               args: List[Any]) -> InstructionData:
        """
        Build instruction data.
        
        Args:
            instruction_name: Name of the instruction
            args: Instruction arguments
            
        Returns:
            InstructionData object
        """
        return InstructionData(name=instruction_name, args=args)
    
    def create_instruction(self, program_id: Union[str, PublicKey],
                          keys: List[Tuple[str, bool, bool]],
                          data: Union[bytes, InstructionData]) -> TransactionInstruction:
        """
        Create transaction instruction.
        
        Args:
            program_id: Program public key
            keys: List of (pubkey, is_signer, is_writable) tuples
            data: Instruction data
            
        Returns:
            TransactionInstruction
        """
        if isinstance(program_id, str):
            program_id = PublicKey(program_id)
        
        account_metas = []
        for pubkey, is_signer, is_writable in keys:
            account_metas.append(AccountMeta(
                pubkey=PublicKey(pubkey),
                is_signer=is_signer,
                is_writable=is_writable
            ))
        
        if isinstance(data, InstructionData):
            data = data.serialize()
        
        return TransactionInstruction(
            keys=account_metas,
            program_id=program_id,
            data=data
        )
    
    def build_transaction(self, instructions: List[TransactionInstruction],
                         fee_payer: Optional[str] = None,
                         recent_blockhash: Optional[str] = None) -> Transaction:
        """
        Build transaction from instructions.
        
        Args:
            instructions: List of instructions
            fee_payer: Fee payer public key
            recent_blockhash: Recent blockhash
            
        Returns:
            Transaction object
        """
        transaction = Transaction()
        
        for instruction in instructions:
            transaction.add(instruction)
        
        if fee_payer:
            transaction.fee_payer = PublicKey(fee_payer)
        elif self.keypair:
            transaction.fee_payer = self.keypair.public_key
        
        if recent_blockhash:
            transaction.recent_blockhash = recent_blockhash
        else:
            # Fetch recent blockhash
            if self.client:
                response = self.client.get_recent_blockhash()
                transaction.recent_blockhash = response['result']['value']['blockhash']
        
        return transaction
    
    def sign_transaction(self, transaction: Transaction,
                         keypairs: Optional[List[Keypair]] = None) -> Transaction:
        """
        Sign transaction.
        
        Args:
            transaction: Transaction to sign
            keypairs: List of keypairs to sign with
            
        Returns:
            Signed transaction
        """
        signers = keypairs or [self.keypair] if self.keypair else []
        
        if not signers:
            raise ValueError("No signers available")
        
        transaction.sign(*signers)
        return transaction
    
    def send_transaction(self, transaction: Transaction,
                         signers: Optional[List[Keypair]] = None,
                         wait_confirmation: bool = True) -> str:
        """
        Send transaction.
        
        Args:
            transaction: Transaction to send
            signers: Signer keypairs
            wait_confirmation: Wait for confirmation
            
        Returns:
            Transaction signature
        """
        if not self.client:
            raise ConnectionError("Not connected")
        
        # Sign transaction
        if not transaction.signatures:
            transaction = self.sign_transaction(transaction, signers)
        
        opts = TxOpts(
            skip_preflight=self.config.get("skip_preflight", False),
            preflight_commitment=self.config.get("preflight_commitment", "confirmed")
        )
        
        response = self.client.send_transaction(
            transaction,
            *(signers or [self.keypair]),
            opts=opts
        )
        
        signature = response['result']
        
        if wait_confirmation:
            self.wait_for_confirmation(signature)
        
        return signature
    
    def wait_for_confirmation(self, signature: str, 
                              timeout: Optional[int] = None) -> Dict:
        """
        Wait for transaction confirmation.
        
        Args:
            signature: Transaction signature
            timeout: Timeout in seconds
            
        Returns:
            Transaction status
        """
        if not self.client:
            raise ConnectionError("Not connected")
        
        import time
        start_time = time.time()
        timeout = timeout or self.config.get("timeout", 30)
        
        while time.time() - start_time < timeout:
            try:
                response = self.client.get_signature_statuses([signature])
                status = response['result']['value'][0]
                
                if status:
                    if status.get('err'):
                        raise Exception(f"Transaction failed: {status['err']}")
                    if status.get('confirmationStatus') in ['confirmed', 'finalized']:
                        return status
            except Exception:
                pass
            
            time.sleep(0.5)
        
        raise TimeoutError(f"Transaction confirmation timeout after {timeout}s")
    
    def create_account(self, from_keypair: Optional[Keypair] = None,
                       new_account_keypair: Optional[Keypair] = None,
                       lamports: int = 10**9,  # 1 SOL default
                       space: int = 0,
                       owner: Optional[str] = None) -> Tuple[str, str]:
        """
        Create new account.
        
        Args:
            from_keypair: Payer keypair
            new_account_keypair: New account keypair
            lamports: Initial lamports
            space: Account space in bytes
            owner: Owner program ID
            
        Returns:
            Tuple of (transaction_signature, new_public_key)
        """
        if not self.client:
            raise ConnectionError("Not connected")
        
        payer = from_keypair or self.keypair
        if not payer:
            raise ValueError("No payer keypair available")
        
        new_account = new_account_keypair or Keypair()
        owner_program = PublicKey(owner) if owner else self.SYSTEM_PROGRAM_ID
        
        create_params = CreateAccountParams(
            from_pubkey=payer.public_key,
            new_account_pubkey=new_account.public_key,
            lamports=lamports,
            space=space,
            program_id=owner_program
        )
        
        instruction = create_account(create_params)
        
        transaction = Transaction()
        transaction.add(instruction)
        
        response = self.client.send_transaction(transaction, payer, new_account)
        
        return response['result'], str(new_account.public_key)
    
    def get_account_info(self, public_key: str) -> Dict:
        """
        Get account information.
        
        Args:
            public_key: Account public key
            
        Returns:
            Account info dictionary
        """
        if not self.client:
            raise ConnectionError("Not connected")
        
        response = self.client.get_account_info(PublicKey(public_key))
        return response['result']['value']
    
    def get_token_accounts(self, owner: str, 
                          mint: Optional[str] = None) -> List[Dict]:
        """
        Get SPL token accounts for owner.
        
        Args:
            owner: Owner public key
            mint: Token mint (optional)
            
        Returns:
            List of token account info
        """
        if not self.client:
            raise ConnectionError("Not connected")
        
        opts = TokenAccountOpts(
            mint=PublicKey(mint) if mint else None
        )
        
        response = self.client.get_token_accounts_by_owner(
            PublicKey(owner),
            opts
        )
        
        return response['result']['value']
    
    def get_token_balance(self, token_account: str) -> Dict:
        """
        Get SPL token balance.
        
        Args:
            token_account: Token account public key
            
        Returns:
            Token balance info
        """
        if not self.client:
            raise ConnectionError("Not connected")
        
        response = self.client.get_token_account_balance(PublicKey(token_account))
        return response['result']['value']
    
    def transfer_token(self, mint: str, to: str, amount: int,
                       from_token_account: Optional[str] = None,
                       decimals: int = 9) -> str:
        """
        Transfer SPL tokens.
        
        Args:
            mint: Token mint address
            to: Recipient public key
            amount: Amount to transfer
            from_token_account: Source token account
            decimals: Token decimals
            
        Returns:
            Transaction signature
        """
        if not self.keypair:
            raise ValueError("No keypair loaded")
        
        if not self.client:
            raise ConnectionError("Not connected")
        
        token = Token(
            self.client,
            PublicKey(mint),
            self.TOKEN_PROGRAM_ID,
            self.keypair
        )
        
        # Get or create associated token accounts
        sender_ata = from_token_account or token.get_associated_token_address(
            self.keypair.public_key
        )
        
        recipient_ata = token.get_associated_token_address(PublicKey(to))
        
        # Create recipient ATA if needed
        create_ata_ix = None
        try:
            self.client.get_account_info(recipient_ata)
        except Exception:
            # Create associated token account
            create_ata_ix = token.create_associated_token_account(
                self.keypair.public_key,
                PublicKey(to)
            )
        
        # Transfer tokens
        transfer_ix = token.transfer(
            source=PublicKey(sender_ata),
            dest=PublicKey(recipient_ata),
            owner=self.keypair.public_key,
            amount=amount,
            opts=TxOpts(skip_confirmation=False)
        )
        
        # Build transaction
        transaction = Transaction()
        if create_ata_ix:
            transaction.add(create_ata_ix)
        transaction.add(transfer_ix)
        
        response = self.client.send_transaction(transaction, self.keypair)
        return response['result']
    
    def request_airdrop(self, public_key: str, amount: float = 1.0) -> str:
        """
        Request SOL airdrop (devnet/testnet only).
        
        Args:
            public_key: Public key to receive airdrop
            amount: Amount in SOL
            
        Returns:
            Transaction signature
        """
        if not self.client:
            raise ConnectionError("Not connected")
        
        lamports = int(amount * 10**9)
        response = self.client.request_airdrop(PublicKey(public_key), lamports)
        return response['result']
    
    def get_slot(self) -> int:
        """Get current slot."""
        if not self.client:
            raise ConnectionError("Not connected")
        
        response = self.client.get_slot()
        return response['result']
    
    def get_block_time(self, slot: int) -> Optional[int]:
        """Get block time for slot."""
        if not self.client:
            raise ConnectionError("Not connected")
        
        response = self.client.get_block_time(slot)
        return response['result']
    
    def get_recent_blockhash(self) -> str:
        """Get recent blockhash."""
        if not self.client:
            raise ConnectionError("Not connected")
        
        response = self.client.get_recent_blockhash()
        return response['result']['value']['blockhash']
    
    def get_program_accounts(self, program_id: str,
                            filters: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Get accounts owned by program.
        
        Args:
            program_id: Program public key
            filters: Optional filters
            
        Returns:
            List of account info
        """
        if not self.client:
            raise ConnectionError("Not connected")
        
        response = self.client.get_program_accounts(
            PublicKey(program_id),
            filters=filters
        )
        return response['result']
    
    def simulate_transaction(self, transaction: Transaction) -> Dict:
        """
        Simulate transaction without sending.
        
        Args:
            transaction: Transaction to simulate
            
        Returns:
            Simulation result
        """
        if not self.client:
            raise ConnectionError("Not connected")
        
        response = self.client.simulate_transaction(transaction)
        return response['result']['value']
    
    @staticmethod
    def lamports_to_sol(lamports: int) -> float:
        """Convert lamports to SOL."""
        return lamports / 10**9
    
    @staticmethod
    def sol_to_lamports(sol: float) -> int:
        """Convert SOL to lamports."""
        return int(sol * 10**9)
    
    @staticmethod
    def is_valid_public_key(key: str) -> bool:
        """Check if string is valid Solana public key."""
        try:
            PublicKey(key)
            return True
        except Exception:
            return False
    
    @staticmethod
    def encode_instruction_data(discriminator: int, *args) -> bytes:
        """
        Encode instruction data with discriminator.
        
        Args:
            discriminator: Instruction discriminator (u8 or u64)
            *args: Additional arguments to encode
            
        Returns:
            Encoded bytes
        """
        data = struct.pack("<B", discriminator)
        for arg in args:
            if isinstance(arg, int):
                data += struct.pack("<Q", arg)
            elif isinstance(arg, bytes):
                data += arg
        return data
    
    def close(self):
        """Close connection."""
        if self.client:
            self.client.close()
            self.client = None


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Solana Skill CLI")
    parser.add_argument("--config", default="config.json", help="Config file path")
    parser.add_argument("--rpc", help="RPC URL")
    parser.add_argument("command", choices=["balance", "transfer", "airdrop"], help="Command")
    parser.add_argument("--address", help="Address")
    parser.add_argument("--to", help="Recipient")
    parser.add_argument("--amount", type=float, help="Amount in SOL")
    
    args = parser.parse_args()
    
    skill = SolanaSkill(args.config)
    skill.connect(args.rpc)
    
    if args.command == "balance":
        balance = skill.get_balance(args.address)
        print(f"Balance: {balance} SOL")
    elif args.command == "transfer":
        signature = skill.transfer_sol(args.to, args.amount)
        print(f"Transaction sent: {signature}")
    elif args.command == "airdrop":
        signature = skill.request_airdrop(args.address, args.amount)
        print(f"Airdrop requested: {signature}")
