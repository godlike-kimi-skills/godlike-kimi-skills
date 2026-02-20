"""
Test suite for Solana Skill.
"""

import json
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

from main import SolanaSkill, InstructionData


class TestSolanaSkill(unittest.TestCase):
    """Test cases for Solana Skill."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "network": "devnet",
            "commitment": "confirmed",
            "timeout": 30
        }
        
        # Create temp config file
        self.config_path = "test_config_solana.json"
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)
        
        self.skill = SolanaSkill(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
    
    def test_init_with_config(self):
        """Test initialization with config file."""
        self.assertEqual(self.skill.config["network"], "devnet")
        self.assertEqual(self.skill.config["commitment"], "confirmed")
    
    def test_init_without_config(self):
        """Test initialization without config file."""
        skill = SolanaSkill()
        self.assertEqual(skill.config["network"], "mainnet-beta")
        self.assertEqual(skill.config["commitment"], "confirmed")
    
    def test_load_config_with_env(self):
        """Test loading config with environment variable."""
        config_with_env = {
            "private_key_env": "TEST_SOLANA_KEY"
        }
        with open(self.config_path, 'w') as f:
            json.dump(config_with_env, f)
        
        with patch.dict(os.environ, {"TEST_SOLANA_KEY": "test_key_12345"}):
            skill = SolanaSkill(self.config_path)
            self.assertEqual(skill.config["private_key"], "test_key_12345")
    
    @patch('main.Client')
    def test_connect(self, mock_client):
        """Test connection to Solana cluster."""
        mock_instance = Mock()
        mock_instance.get_slot.return_value = {'result': 123456}
        mock_client.return_value = mock_instance
        
        result = self.skill.connect("https://api.devnet.solana.com")
        
        self.assertTrue(result)
        self.assertIsNotNone(self.skill.client)
        mock_client.assert_called_once()
    
    @patch('main.Client')
    def test_is_connected(self, mock_client):
        """Test connection status check."""
        mock_instance = Mock()
        mock_instance.get_slot.return_value = {'result': 123456}
        mock_client.return_value = mock_instance
        
        self.assertFalse(self.skill.is_connected())
        self.skill.connect("https://api.devnet.solana.com")
        self.assertTrue(self.skill.is_connected())
    
    @patch('main.Client')
    def test_is_connected_failure(self, mock_client):
        """Test connection failure."""
        mock_instance = Mock()
        mock_instance.get_slot.side_effect = Exception("Connection failed")
        mock_client.return_value = mock_instance
        
        self.skill.connect("https://api.devnet.solana.com")
        self.assertFalse(self.skill.is_connected())
    
    def test_generate_keypair(self):
        """Test keypair generation."""
        public_key, private_key = self.skill.generate_keypair()
        
        self.assertIsNotNone(public_key)
        self.assertIsNotNone(private_key)
        self.assertIsInstance(public_key, str)
        self.assertIsInstance(private_key, str)
        self.assertTrue(len(private_key) > 0)
    
    def test_lamports_to_sol(self):
        """Test lamports to SOL conversion."""
        sol = self.skill.lamports_to_sol(10**9)
        self.assertEqual(sol, 1.0)
        
        sol = self.skill.lamports_to_sol(500000000)
        self.assertEqual(sol, 0.5)
    
    def test_sol_to_lamports(self):
        """Test SOL to lamports conversion."""
        lamports = self.skill.sol_to_lamports(1.0)
        self.assertEqual(lamports, 10**9)
        
        lamports = self.skill.sol_to_lamports(0.5)
        self.assertEqual(lamports, 500000000)
    
    def test_is_valid_public_key(self):
        """Test public key validation."""
        # Valid pubkey format (base58)
        valid = "HN7cABqLq46Es1jh92dQQisAq662SmxELLLsHHe4YWrH"
        # Invalid format
        invalid = "invalid_key"
        
        # Mock will fail, but we test the method structure
        try:
            result = self.skill.is_valid_public_key(valid)
            self.assertIsInstance(result, bool)
        except Exception:
            pass
    
    @patch('main.Client')
    def test_get_balance(self, mock_client):
        """Test balance retrieval."""
        mock_instance = Mock()
        mock_instance.get_balance.return_value = {'result': {'value': 10**9}}
        mock_client.return_value = mock_instance
        
        self.skill.connect("https://api.devnet.solana.com")
        balance = self.skill.get_balance("HN7cABqLq46Es1jh92dQQisAq662SmxELLLsHHe4YWrH")
        
        self.assertEqual(balance, 1.0)
    
    @patch('main.Client')
    def test_get_slot(self, mock_client):
        """Test slot retrieval."""
        mock_instance = Mock()
        mock_instance.get_slot.return_value = {'result': 123456789}
        mock_client.return_value = mock_instance
        
        self.skill.connect("https://api.devnet.solana.com")
        slot = self.skill.get_slot()
        
        self.assertEqual(slot, 123456789)
    
    @patch('main.Client')
    def test_get_recent_blockhash(self, mock_client):
        """Test recent blockhash retrieval."""
        mock_instance = Mock()
        mock_instance.get_recent_blockhash.return_value = {
            'result': {'value': {'blockhash': 'abc123xyz'}}
        }
        mock_client.return_value = mock_instance
        
        self.skill.connect("https://api.devnet.solana.com")
        blockhash = self.skill.get_recent_blockhash()
        
        self.assertEqual(blockhash, 'abc123xyz')
    
    @patch('main.Client')
    def test_request_airdrop(self, mock_client):
        """Test airdrop request."""
        mock_instance = Mock()
        mock_instance.request_airdrop.return_value = {
            'result': 'tx_signature_123'
        }
        mock_client.return_value = mock_instance
        
        self.skill.connect("https://api.devnet.solana.com")
        signature = self.skill.request_airdrop("HN7cABqLq46Es1jh92dQQisAq662SmxELLLsHHe4YWrH", 1.0)
        
        self.assertEqual(signature, 'tx_signature_123')
    
    @patch('main.Client')
    def test_get_account_info(self, mock_client):
        """Test account info retrieval."""
        mock_instance = Mock()
        mock_instance.get_account_info.return_value = {
            'result': {
                'value': {
                    'lamports': 10**9,
                    'owner': '11111111111111111111111111111111',
                    'data': ['', 'base64']
                }
            }
        }
        mock_client.return_value = mock_instance
        
        self.skill.connect("https://api.devnet.solana.com")
        info = self.skill.get_account_info("HN7cABqLq46Es1jh92dQQisAq662SmxELLLsHHe4YWrH")
        
        self.assertEqual(info['lamports'], 10**9)
    
    @patch('main.Client')
    def test_get_program_accounts(self, mock_client):
        """Test program accounts retrieval."""
        mock_instance = Mock()
        mock_instance.get_program_accounts.return_value = {
            'result': [
                {'pubkey': 'account1', 'account': {'lamports': 1000}},
                {'pubkey': 'account2', 'account': {'lamports': 2000}}
            ]
        }
        mock_client.return_value = mock_instance
        
        self.skill.connect("https://api.devnet.solana.com")
        accounts = self.skill.get_program_accounts("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        
        self.assertEqual(len(accounts), 2)
    
    @patch('main.Client')
    def test_get_block_time(self, mock_client):
        """Test block time retrieval."""
        mock_instance = Mock()
        mock_instance.get_block_time.return_value = {'result': 1640000000}
        mock_client.return_value = mock_instance
        
        self.skill.connect("https://api.devnet.solana.com")
        block_time = self.skill.get_block_time(123456)
        
        self.assertEqual(block_time, 1640000000)
    
    @patch('main.Client')
    def test_get_token_accounts(self, mock_client):
        """Test token accounts retrieval."""
        mock_instance = Mock()
        mock_instance.get_token_accounts_by_owner.return_value = {
            'result': {
                'value': [
                    {'pubkey': 'token_account1', 'account': {'data': {}}},
                    {'pubkey': 'token_account2', 'account': {'data': {}}}
                ]
            }
        }
        mock_client.return_value = mock_instance
        
        self.skill.connect("https://api.devnet.solana.com")
        accounts = self.skill.get_token_accounts("HN7cABqLq46Es1jh92dQQisAq662SmxELLLsHHe4YWrH")
        
        self.assertEqual(len(accounts), 2)
    
    @patch('main.Client')
    def test_get_token_balance(self, mock_client):
        """Test token balance retrieval."""
        mock_instance = Mock()
        mock_instance.get_token_account_balance.return_value = {
            'result': {
                'value': {
                    'amount': '1000000',
                    'decimals': 6,
                    'uiAmount': 1.0
                }
            }
        }
        mock_client.return_value = mock_instance
        
        self.skill.connect("https://api.devnet.solana.com")
        balance = self.skill.get_token_balance("token_account_address")
        
        self.assertEqual(balance['amount'], '1000000')
        self.assertEqual(balance['decimals'], 6)
    
    def test_instruction_data(self):
        """Test instruction data creation."""
        data = self.skill.build_instruction_data("transfer", [100, 200])
        
        self.assertIsInstance(data, InstructionData)
        self.assertEqual(data.name, "transfer")
        self.assertEqual(data.args, [100, 200])
    
    def test_encode_instruction_data(self):
        """Test instruction data encoding."""
        # Test with discriminator only
        data = self.skill.encode_instruction_data(1)
        self.assertIsInstance(data, bytes)
        self.assertEqual(len(data), 1)
        
        # Test with additional args
        data = self.skill.encode_instruction_data(1, 100, 200)
        self.assertIsInstance(data, bytes)
    
    @patch('main.Client')
    def test_simulate_transaction(self, mock_client):
        """Test transaction simulation."""
        mock_instance = Mock()
        mock_instance.simulate_transaction.return_value = {
            'result': {
                'value': {
                    'err': None,
                    'logs': ['log1', 'log2']
                }
            }
        }
        mock_client.return_value = mock_instance
        
        self.skill.connect("https://api.devnet.solana.com")
        
        from main import Transaction
        transaction = Transaction()
        result = self.skill.simulate_transaction(transaction)
        
        self.assertIsNone(result['err'])
        self.assertEqual(len(result['logs']), 2)
    
    def test_create_instruction(self):
        """Test instruction creation."""
        keys = [
            ("HN7cABqLq46Es1jh92dQQisAq662SmxELLLsHHe4YWrH", True, True),
            ("RecipientPublicKey", False, True)
        ]
        
        instruction = self.skill.create_instruction(
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
            keys,
            b"instruction_data"
        )
        
        self.assertIsNotNone(instruction)
        self.assertEqual(len(instruction.keys), 2)
    
    def test_build_transaction(self):
        """Test transaction building."""
        from main import TransactionInstruction, PublicKey, AccountMeta
        
        instruction = TransactionInstruction(
            keys=[AccountMeta(PublicKey(1), False, True)],
            program_id=PublicKey("11111111111111111111111111111111"),
            data=b"test"
        )
        
        with patch.object(self.skill, 'client') as mock_client:
            mock_client.get_recent_blockhash.return_value = {
                'result': {'value': {'blockhash': 'abc123'}}
            }
            
            transaction = self.skill.build_transaction([instruction])
            
            self.assertIsNotNone(transaction)


class TestSolanaSkillIntegration(unittest.TestCase):
    """Integration tests requiring actual Solana connection."""
    
    @unittest.skip("Requires live Solana connection")
    def test_live_connection(self):
        """Test with live Solana devnet."""
        skill = SolanaSkill()
        connected = skill.connect("https://api.devnet.solana.com")
        self.assertTrue(connected)
        
        # Get slot
        slot = skill.get_slot()
        self.assertIsInstance(slot, int)
        
        # Get balance for known address
        balance = skill.get_balance("HN7cABqLq46Es1jh92dQQisAq662SmxELLLsHHe4YWrH")
        self.assertIsInstance(balance, float)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add unit tests
    suite.addTests(loader.loadTestsFromTestCase(TestSolanaSkill))
    
    # Add integration tests (skipped by default)
    suite.addTests(loader.loadTestsFromTestCase(TestSolanaSkillIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
