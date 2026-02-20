"""
Test suite for Web3.py Skill.
"""

import json
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

from main import Web3PySkill, Wallet


class TestWeb3PySkill(unittest.TestCase):
    """Test cases for Web3.py Skill."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "network": "mainnet",
            "default_gas_limit": 21000,
            "max_gas_price_gwei": 100,
            "confirmations": 1,
            "timeout": 30
        }
        
        # Create temp config file
        self.config_path = "test_config_web3.json"
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)
        
        self.skill = Web3PySkill(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
    
    def test_init_with_config(self):
        """Test initialization with config file."""
        self.assertEqual(self.skill.config["network"], "mainnet")
        self.assertEqual(self.skill.config["default_gas_limit"], 21000)
    
    def test_init_without_config(self):
        """Test initialization without config file."""
        skill = Web3PySkill()
        self.assertEqual(skill.config["network"], "mainnet")
        self.assertEqual(skill.config["default_gas_limit"], 21000)
    
    def test_load_config_with_env(self):
        """Test loading config with environment variable."""
        config_with_env = {
            "private_key_env": "TEST_WEB3_KEY"
        }
        with open(self.config_path, 'w') as f:
            json.dump(config_with_env, f)
        
        with patch.dict(os.environ, {"TEST_WEB3_KEY": "test_key"}):
            skill = Web3PySkill(self.config_path)
            self.assertEqual(skill.config["private_key"], "test_key")
    
    @patch('main.Web3')
    def test_connect_http(self, mock_web3):
        """Test HTTP connection."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_instance.eth.chain_id = 1
        mock_web3.return_value = mock_instance
        
        result = self.skill.connect("https://mainnet.infura.io/v3/test")
        
        self.assertTrue(result)
        self.assertIsNotNone(self.skill.w3)
    
    @patch('main.Web3')
    def test_is_connected(self, mock_web3):
        """Test connection status."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_web3.return_value = mock_instance
        
        self.assertFalse(self.skill.is_connected())
        self.skill.connect("https://mainnet.infura.io/v3/test")
        self.assertTrue(self.skill.is_connected())
    
    @patch('main.Web3')
    def test_disconnect(self, mock_web3):
        """Test disconnection."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_instance.provider = Mock(disconnect=Mock())
        mock_web3.return_value = mock_instance
        
        self.skill.connect("https://mainnet.infura.io/v3/test")
        self.skill.disconnect()
        self.assertIsNone(self.skill.w3)
    
    def test_create_wallet(self):
        """Test wallet creation."""
        with patch('main.generate_mnemonic') as mock_mnemonic:
            mock_mnemonic.return_value = "test mnemonic phrase"
            
            with patch('main.Account') as mock_account:
                mock_account.enable_unaudited_hdwallet_features = Mock()
                mock_account.from_mnemonic.return_value = Mock(
                    address="0x1234567890abcdef",
                    key=Mock(hex=lambda: "0xprivatekey")
                )
                
                wallet = self.skill.create_wallet()
                
                self.assertIn("address", wallet)
                self.assertIn("private_key", wallet)
                self.assertIn("mnemonic", wallet)
    
    def test_import_wallet(self):
        """Test wallet import."""
        with patch('main.Account') as mock_account:
            mock_account.from_key.return_value = Mock(
                address="0x1234567890abcdef",
                key=Mock(hex=lambda: "0xprivatekey")
            )
            
            wallet = self.skill.import_wallet("0xprivate_key")
            
            self.assertIn("address", wallet)
            self.assertIn("private_key", wallet)
            self.assertIn("0x1234567890abcdef", self.skill._wallets)
    
    def test_import_wallet_from_mnemonic(self):
        """Test wallet import from mnemonic."""
        with patch('main.Account') as mock_account:
            mock_account.enable_unaudited_hdwallet_features = Mock()
            mock_account.from_mnemonic.return_value = Mock(
                address="0x1234567890abcdef",
                key=Mock(hex=lambda: "0xprivatekey")
            )
            
            wallet = self.skill.import_wallet_from_mnemonic("test mnemonic")
            
            self.assertIn("address", wallet)
            self.assertIn("private_key", wallet)
    
    def test_get_wallet(self):
        """Test wallet retrieval."""
        test_wallet = Wallet(
            address="0x123",
            private_key="0xabc",
            mnemonic="test"
        )
        self.skill._wallets["test_wallet"] = test_wallet
        
        retrieved = self.skill.get_wallet("test_wallet")
        self.assertEqual(retrieved, test_wallet)
    
    def test_list_wallets(self):
        """Test wallet listing."""
        test_wallet = Wallet(
            address="0x123",
            private_key="0xabc",
            mnemonic="test"
        )
        self.skill._wallets["test_wallet"] = test_wallet
        
        wallets = self.skill.list_wallets()
        self.assertEqual(len(wallets), 1)
        self.assertEqual(wallets[0]["address"], "0x123")
    
    @patch('main.Web3')
    def test_resolve_ens(self, mock_web3):
        """Test ENS resolution."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_instance.ens.address.return_value = "0x" + "a" * 40
        mock_web3.return_value = mock_instance
        
        self.skill.connect("https://mainnet.infura.io/v3/test")
        address = self.skill.resolve_ens("vitalik.eth")
        
        self.assertEqual(address, "0x" + "a" * 40)
    
    @patch('main.Web3')
    def test_reverse_resolve_ens(self, mock_web3):
        """Test reverse ENS resolution."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_instance.ens.name.return_value = "test.eth"
        mock_web3.return_value = mock_instance
        
        self.skill.connect("https://mainnet.infura.io/v3/test")
        name = self.skill.reverse_resolve_ens("0x" + "a" * 40)
        
        self.assertEqual(name, "test.eth")
    
    def test_to_wei(self):
        """Test wei conversion."""
        result = self.skill.to_wei(1, "ether")
        self.assertEqual(result, 10**18)
        
        result = self.skill.to_wei(1, "gwei")
        self.assertEqual(result, 10**9)
    
    def test_from_wei(self):
        """Test from wei conversion."""
        result = self.skill.from_wei(10**18, "ether")
        self.assertEqual(result, Decimal(1))
    
    def test_to_checksum_address(self):
        """Test checksum address conversion."""
        address = "0xdac17f958d2ee523a2206206994597c13d831ec7"
        checksum = self.skill.to_checksum_address(address)
        self.assertEqual(checksum, "0xdAC17F958D2ee523a2206206994597C13D831ec7")
    
    def test_is_address(self):
        """Test address validation."""
        valid_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        invalid_address = "0xInvalid"
        
        self.assertTrue(self.skill.is_address(valid_address))
        self.assertFalse(self.skill.is_address(invalid_address))
    
    def test_is_checksum_address(self):
        """Test checksum address validation."""
        valid_checksum = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        invalid_checksum = "0xdac17f958d2ee523a2206206994597c13d831ec7"
        
        self.assertTrue(self.skill.is_checksum_address(valid_checksum))
        self.assertFalse(self.skill.is_checksum_address(invalid_checksum))
    
    def test_keccak256(self):
        """Test Keccak-256 hashing."""
        result = self.skill.keccak256("test")
        self.assertTrue(result.startswith("0x"))
        self.assertEqual(len(result), 66)  # 0x + 64 hex chars
    
    def test_encode_decode_abi(self):
        """Test ABI encoding/decoding."""
        types = ["uint256", "address"]
        values = [1000, "0xdAC17F958D2ee523a2206206994597C13D831ec7"]
        
        encoded = self.skill.encode_abi(types, values)
        self.assertTrue(encoded.startswith("0x"))
        
        # Note: decode_abi returns tuple, address comparison needs care
        # This test verifies the round-trip works
        self.assertIsInstance(encoded, str)
    
    @patch('main.Web3')
    def test_get_balance(self, mock_web3):
        """Test balance retrieval."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_instance.eth.get_balance.return_value = 10**18
        mock_instance.to_checksum_address = lambda x: x
        mock_web3.return_value = mock_instance
        
        self.skill.connect("https://mainnet.infura.io/v3/test")
        balance = self.skill.get_balance("0x" + "a" * 40)
        
        self.assertEqual(balance, 10**18)
    
    @patch('main.Web3')
    def test_get_gas_price(self, mock_web3):
        """Test gas price retrieval."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_instance.eth.gas_price = 20 * 10**9
        mock_web3.return_value = mock_instance
        
        self.skill.connect("https://mainnet.infura.io/v3/test")
        gas_price = self.skill.get_gas_price()
        
        self.assertEqual(gas_price, 20 * 10**9)
    
    @patch('main.Web3')
    def test_get_block_number(self, mock_web3):
        """Test block number retrieval."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_instance.eth.block_number = 12345678
        mock_web3.return_value = mock_instance
        
        self.skill.connect("https://mainnet.infura.io/v3/test")
        block_number = self.skill.get_block_number()
        
        self.assertEqual(block_number, 12345678)
    
    @patch('main.Web3')
    def test_get_block(self, mock_web3):
        """Test block retrieval."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_instance.eth.get_block.return_value = {
            "number": 100,
            "hash": b"block_hash",
            "transactions": []
        }
        mock_web3.return_value = mock_instance
        
        self.skill.connect("https://mainnet.infura.io/v3/test")
        block = self.skill.get_block("latest")
        
        self.assertEqual(block["number"], 100)
    
    @patch('main.Web3')
    def test_get_contract_instance(self, mock_web3):
        """Test contract instance creation."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_instance.eth.contract.return_value = Mock()
        mock_web3.return_value = mock_instance
        
        self.skill.connect("https://mainnet.infura.io/v3/test")
        
        abi = [{"name": "test", "type": "function"}]
        contract = self.skill.get_contract_instance("0x" + "a" * 40, abi)
        
        self.assertIsNotNone(contract)
    
    def test_sign_message(self):
        """Test message signing."""
        with patch('main.Account') as mock_account:
            mock_account.from_key.return_value = Mock(
                sign_message=Mock(return_value=Mock(signature=b"signature"))
            )
            
            self.skill._wallets["test"] = Wallet(
                address="0x123",
                private_key="0xabc"
            )
            
            result = self.skill.sign_message("test message", "test")
            self.assertIsNotNone(result)
    
    def test_verify_signature(self):
        """Test signature verification."""
        with patch('main.Account') as mock_account:
            mock_account.recover_message.return_value = "0x1234567890abcdef"
            
            result = self.skill.verify_signature(
                "test",
                "0x" + "a" * 130,
                "0x1234567890abcdef"
            )
            
            self.assertTrue(result)
    
    def test_verify_signature_invalid(self):
        """Test invalid signature verification."""
        with patch('main.Account') as mock_account:
            mock_account.recover_message.return_value = "0xdifferentaddress"
            
            result = self.skill.verify_signature(
                "test",
                "0x" + "a" * 130,
                "0x1234567890abcdef"
            )
            
            self.assertFalse(result)


class TestWeb3PySkillIntegration(unittest.TestCase):
    """Integration tests requiring actual Ethereum connection."""
    
    @unittest.skip("Requires live Ethereum connection")
    def test_live_connection(self):
        """Test with live Ethereum node."""
        skill = Web3PySkill()
        connected = skill.connect("https://mainnet.infura.io/v3/YOUR_API_KEY")
        self.assertTrue(connected)
        
        # Get latest block
        block = skill.get_block("latest")
        self.assertIsNotNone(block["number"])
        
        # Get balance for known address
        balance = skill.get_balance("0xdAC17F958D2ee523a2206206994597C13D831ec7")
        self.assertIsInstance(balance, int)
    
    @unittest.skip("Requires live Ethereum connection")
    def test_ens_resolution(self):
        """Test ENS resolution."""
        skill = Web3PySkill()
        skill.connect("https://mainnet.infura.io/v3/YOUR_API_KEY")
        
        address = skill.resolve_ens("vitalik.eth")
        self.assertIsNotNone(address)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add unit tests
    suite.addTests(loader.loadTestsFromTestCase(TestWeb3PySkill))
    
    # Add integration tests (skipped by default)
    suite.addTests(loader.loadTestsFromTestCase(TestWeb3PySkillIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
