"""
Test suite for Ethereum Skill.
"""

import json
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

from main import EthereumSkill


class TestEthereumSkill(unittest.TestCase):
    """Test cases for Ethereum Skill."""
    
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
        self.config_path = "test_config.json"
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)
        
        self.skill = EthereumSkill(self.config_path)
    
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
        skill = EthereumSkill()
        self.assertEqual(skill.config["network"], "mainnet")
        self.assertEqual(skill.config["default_gas_limit"], 21000)
    
    def test_load_config_with_env(self):
        """Test loading config with environment variable."""
        config_with_env = {
            "private_key_env": "TEST_PRIVATE_KEY"
        }
        with open(self.config_path, 'w') as f:
            json.dump(config_with_env, f)
        
        with patch.dict(os.environ, {"TEST_PRIVATE_KEY": "test_key"}):
            skill = EthereumSkill(self.config_path)
            self.assertEqual(skill.config["private_key"], "test_key")
    
    @patch('main.Web3')
    def test_connect(self, mock_web3):
        """Test connection to Ethereum node."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_instance.eth.chain_id = 1
        mock_web3.return_value = mock_instance
        
        result = self.skill.connect("https://mainnet.infura.io/v3/test")
        
        self.assertTrue(result)
        self.assertIsNotNone(self.skill.w3)
        mock_web3.assert_called_once()
    
    @patch('main.Web3')
    def test_is_connected(self, mock_web3):
        """Test connection status check."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_web3.return_value = mock_instance
        
        self.assertFalse(self.skill.is_connected())
        self.skill.connect("https://mainnet.infura.io/v3/test")
        self.assertTrue(self.skill.is_connected())
    
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
        
        result = self.skill.from_wei(10**9, "gwei")
        self.assertEqual(result, Decimal(1))
    
    def test_is_address(self):
        """Test address validation."""
        valid_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        invalid_address = "0xInvalid"
        
        self.assertTrue(self.skill.is_address(valid_address))
        self.assertFalse(self.skill.is_address(invalid_address))
    
    def test_to_checksum_address(self):
        """Test checksum address conversion."""
        address = "0xdac17f958d2ee523a2206206994597c13d831ec7"
        checksum = self.skill.to_checksum_address(address)
        self.assertEqual(checksum, "0xdAC17F958D2ee523a2206206994597C13D831ec7")
    
    @patch('main.Account')
    def test_load_account(self, mock_account):
        """Test account loading."""
        mock_account.from_key.return_value = Mock(address="0xTestAddress")
        
        self.skill._load_account("0x" + "a" * 64)
        mock_account.from_key.assert_called_once()
    
    @patch('main.Web3')
    def test_get_balance(self, mock_web3):
        """Test balance retrieval."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_instance.eth.get_balance.return_value = 10**18
        mock_instance.to_checksum_address = lambda x: x
        mock_web3.return_value = mock_instance
        
        self.skill.connect("https://mainnet.infura.io/v3/test")
        self.skill.account = Mock(address="0xTest")
        
        balance = self.skill.get_balance()
        self.assertEqual(balance, 10**18)
    
    @patch('main.Web3')
    def test_get_gas_price(self, mock_web3):
        """Test gas price retrieval."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_instance.eth.gas_price = 20 * 10**9  # 20 gwei
        mock_web3.return_value = mock_instance
        
        self.skill.connect("https://mainnet.infura.io/v3/test")
        gas_price = self.skill.get_gas_price()
        
        self.assertLessEqual(gas_price, 100 * 10**9)  # Max 100 gwei
    
    @patch('main.Web3')
    def test_get_transaction_count(self, mock_web3):
        """Test transaction count retrieval."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_instance.eth.get_transaction_count.return_value = 5
        mock_web3.return_value = mock_instance
        
        self.skill.connect("https://mainnet.infura.io/v3/test")
        self.skill.account = Mock(address="0xTest")
        
        count = self.skill.get_transaction_count()
        self.assertEqual(count, 5)
    
    @patch('main.Web3')
    def test_estimate_gas(self, mock_web3):
        """Test gas estimation."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_instance.eth.estimate_gas.return_value = 21000
        mock_web3.return_value = mock_instance
        
        self.skill.connect("https://mainnet.infura.io/v3/test")
        
        tx = {"to": "0x" + "a" * 40, "value": 0}
        gas = self.skill.estimate_gas(tx)
        self.assertEqual(gas, 21000)
    
    @patch('main.Web3')
    def test_load_contract(self, mock_web3):
        """Test contract loading."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_instance.eth.contract.return_value = Mock()
        mock_instance.to_checksum_address = lambda x: x
        mock_web3.return_value = mock_instance
        
        self.skill.connect("https://mainnet.infura.io/v3/test")
        
        abi = [{"name": "test", "type": "function"}]
        contract = self.skill.load_contract("0x" + "a" * 40, abi, "test_contract")
        
        self.assertIn("test_contract", self.skill.contracts)
    
    @patch('main.Web3')
    def test_call_contract_method(self, mock_web3):
        """Test contract method calling."""
        mock_contract = Mock()
        mock_function = Mock()
        mock_function.return_value = Mock(call=Mock(return_value=100))
        mock_contract.functions = Mock(balanceOf=mock_function)
        
        self.skill.w3 = Mock()
        self.skill.contracts["test"] = mock_contract
        
        result = self.skill.call_contract_method("test", "balanceOf", "0xAddress")
        self.assertEqual(result, 100)
    
    @patch('main.Web3')
    def test_send_transaction(self, mock_web3):
        """Test transaction sending."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_instance.eth.chain_id = 1
        mock_instance.eth.get_transaction_count.return_value = 0
        mock_instance.eth.gas_price = 20 * 10**9
        mock_instance.eth.estimate_gas.return_value = 21000
        mock_instance.eth.send_raw_transaction.return_value = b"tx_hash"
        mock_instance.eth.wait_for_transaction_receipt.return_value = {"blockNumber": 1}
        mock_instance.to_checksum_address = lambda x: x
        mock_web3.return_value = mock_instance
        
        self.skill.connect("https://mainnet.infura.io/v3/test")
        self.skill.account = Mock(
            address="0xTest",
            sign_transaction=Mock(return_value=Mock(rawTransaction=b"signed"))
        )
        
        tx_hash = self.skill.send_transaction("0x" + "b" * 40, 10**18)
        self.assertIsNotNone(tx_hash)
    
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
    def test_wait_for_confirmation(self, mock_web3):
        """Test transaction confirmation waiting."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_instance.eth.wait_for_transaction_receipt.return_value = {
            "blockNumber": 100,
            "status": 1
        }
        mock_instance.eth.block_number = 105
        mock_web3.return_value = mock_instance
        
        self.skill.connect("https://mainnet.infura.io/v3/test")
        
        receipt = self.skill.wait_for_confirmation(b"tx_hash")
        self.assertEqual(receipt["blockNumber"], 100)
    
    def test_event_listener_management(self):
        """Test event listener start and stop."""
        self.skill.w3 = Mock()
        
        # Mock contract and filter
        mock_contract = Mock()
        mock_filter = Mock()
        mock_contract.events = {"Transfer": Mock(create_filter=Mock(return_value=mock_filter))}
        self.skill.w3.eth.contract.return_value = mock_contract
        
        listener_id = self.skill.listen_events(
            "0x" + "a" * 40,
            "Transfer",
            callback=lambda x: x
        )
        
        self.assertIn(listener_id, self.skill._event_listeners)
        
        result = self.skill.stop_listening(listener_id)
        self.assertTrue(result)
        self.assertNotIn(listener_id, self.skill._event_listeners)
    
    def test_stop_nonexistent_listener(self):
        """Test stopping non-existent listener."""
        result = self.skill.stop_listening("nonexistent")
        self.assertFalse(result)
    
    @patch('main.Web3')
    def test_transfer_token(self, mock_web3):
        """Test ERC20 token transfer."""
        mock_instance = Mock()
        mock_instance.is_connected.return_value = True
        mock_instance.eth.chain_id = 1
        mock_instance.eth.get_transaction_count.return_value = 0
        mock_instance.eth.gas_price = 20 * 10**9
        mock_instance.to_checksum_address = lambda x: x
        mock_web3.return_value = mock_instance
        
        self.skill.connect("https://mainnet.infura.io/v3/test")
        self.skill.account = Mock(
            address="0xTest",
            sign_transaction=Mock(return_value=Mock(rawTransaction=b"signed"))
        )
        self.skill.send_raw_transaction = Mock(return_value=b"tx_hash")
        self.skill.wait_for_confirmation = Mock(return_value={"status": 1})
        
        tx_hash = self.skill.transfer_token("0x" + "c" * 40, "0x" + "d" * 40, 1000)
        self.assertIsNotNone(tx_hash)


class TestEthereumSkillIntegration(unittest.TestCase):
    """Integration tests requiring actual Ethereum connection."""
    
    @unittest.skip("Requires live Ethereum connection")
    def test_live_connection(self):
        """Test with live Ethereum node."""
        skill = EthereumSkill()
        connected = skill.connect("https://mainnet.infura.io/v3/YOUR_API_KEY")
        self.assertTrue(connected)
        
        # Get latest block
        block = skill.get_block("latest")
        self.assertIsNotNone(block["number"])
        
        # Get balance for known address
        balance = skill.get_balance("0xdAC17F958D2ee523a2206206994597C13D831ec7")
        self.assertIsInstance(balance, int)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add unit tests
    suite.addTests(loader.loadTestsFromTestCase(TestEthereumSkill))
    
    # Add integration tests (skipped by default)
    suite.addTests(loader.loadTestsFromTestCase(TestEthereumSkillIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
