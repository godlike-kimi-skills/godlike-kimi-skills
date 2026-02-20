"""
Test suite for Hardhat Skill.
"""

import json
import os
import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path

from main import HardhatSkill, CompileResult, TestResult


class TestHardhatSkill(unittest.TestCase):
    """Test cases for Hardhat Skill."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "project_path": "./test-hardhat-project",
            "default_network": "hardhat",
            "solidity_version": "0.8.19",
            "optimizer": {
                "enabled": True,
                "runs": 200
            }
        }
        
        # Create temp config file
        self.config_path = "test_config_hardhat.json"
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)
        
        self.skill = HardhatSkill(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
    
    def test_init_with_config(self):
        """Test initialization with config file."""
        self.assertEqual(self.skill.config["default_network"], "hardhat")
        self.assertEqual(self.skill.config["solidity_version"], "0.8.19")
    
    def test_init_without_config(self):
        """Test initialization without config file."""
        skill = HardhatSkill()
        self.assertEqual(skill.config["default_network"], "hardhat")
        self.assertEqual(skill.config["solidity_version"], "0.8.19")
    
    def test_check_hardhat_installed(self):
        """Test Hardhat installation check."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            self.assertTrue(self.skill.check_hardhat_installed())
    
    def test_check_hardhat_not_installed(self):
        """Test Hardhat not installed."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False
            self.assertFalse(self.skill.check_hardhat_installed())
    
    @patch('subprocess.run')
    def test_install_hardhat(self, mock_run):
        """Test Hardhat installation."""
        mock_run.return_value = Mock(returncode=0)
        result = self.skill.install_hardhat()
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_install_hardhat_failure(self, mock_run):
        """Test Hardhat installation failure."""
        mock_run.side_effect = FileNotFoundError()
        result = self.skill.install_hardhat()
        self.assertFalse(result)
    
    @patch('pathlib.Path.mkdir')
    @patch('subprocess.run')
    @patch.object(HardhatSkill, 'install_hardhat')
    @patch.object(HardhatSkill, '_create_hardhat_config')
    @patch.object(HardhatSkill, '_create_directories')
    @patch.object(HardhatSkill, '_create_template_files')
    @patch.object(HardhatSkill, '_install_template_dependencies')
    def test_init_project(self, mock_deps, mock_files, mock_dirs, mock_config, mock_install, mock_run, mock_mkdir):
        """Test project initialization."""
        mock_install.return_value = True
        mock_run.return_value = Mock(returncode=0)
        
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False
            result = self.skill.init_project("test-project")
            self.assertTrue(result)
    
    def test_init_project_exists(self):
        """Test project initialization when directory exists."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            result = self.skill.init_project("test-project")
            self.assertFalse(result)
    
    @patch.object(HardhatSkill, '_run_npx_command')
    @patch.object(HardhatSkill, 'check_hardhat_installed')
    def test_compile_contracts(self, mock_check, mock_run):
        """Test contract compilation."""
        mock_check.return_value = True
        mock_run.return_value = (0, "Compiled successfully", "")
        
        result = self.skill.compile_contracts()
        self.assertIsInstance(result, CompileResult)
        self.assertTrue(result.success)
    
    @patch.object(HardhatSkill, 'check_hardhat_installed')
    def test_compile_contracts_not_installed(self, mock_check):
        """Test compilation without Hardhat."""
        mock_check.return_value = False
        result = self.skill.compile_contracts()
        self.assertFalse(result.success)
        self.assertIn("Hardhat not installed", result.errors)
    
    @patch.object(HardhatSkill, '_run_npx_command')
    @patch.object(HardhatSkill, 'check_hardhat_installed')
    def test_compile_with_force(self, mock_check, mock_run):
        """Test compilation with force flag."""
        mock_check.return_value = True
        mock_run.return_value = (0, "", "")
        
        self.skill.compile_contracts(force=True)
        mock_run.assert_called_once()
    
    @patch.object(HardhatSkill, '_run_npx_command')
    @patch.object(HardhatSkill, 'check_hardhat_installed')
    def test_test(self, mock_check, mock_run):
        """Test execution."""
        mock_check.return_value = True
        mock_run.return_value = (0, "5 passing", "")
        
        result = self.skill.test()
        self.assertIsInstance(result, TestResult)
        self.assertTrue(result.success)
        self.assertEqual(result.passed, 5)
    
    @patch.object(HardhatSkill, 'check_hardhat_installed')
    def test_test_not_installed(self, mock_check):
        """Test execution without Hardhat."""
        mock_check.return_value = False
        result = self.skill.test()
        self.assertFalse(result.success)
    
    @patch.object(HardhatSkill, '_run_npx_command')
    @patch.object(HardhatSkill, 'check_hardhat_installed')
    def test_test_with_grep(self, mock_check, mock_run):
        """Test with grep pattern."""
        mock_check.return_value = True
        mock_run.return_value = (0, "1 passing", "")
        
        result = self.skill.test(grep="MyContract")
        self.assertTrue(result.success)
    
    @patch.object(HardhatSkill, '_run_npx_command')
    @patch.object(HardhatSkill, 'check_hardhat_installed')
    def test_deploy(self, mock_check, mock_run):
        """Test deployment."""
        mock_check.return_value = True
        mock_run.return_value = (0, "Contract deployed to 0x123...", "")
        
        success, output = self.skill.deploy("sepolia", "deploy.js")
        self.assertTrue(success)
    
    @patch.object(HardhatSkill, 'check_hardhat_installed')
    def test_deploy_not_installed(self, mock_check):
        """Test deployment without Hardhat."""
        mock_check.return_value = False
        success, output = self.skill.deploy()
        self.assertFalse(success)
    
    @patch('pathlib.Path.exists')
    @patch.object(HardhatSkill, '_run_npx_command')
    @patch.object(HardhatSkill, 'check_hardhat_installed')
    def test_deploy_script_not_found(self, mock_check, mock_run, mock_exists):
        """Test deployment with missing script."""
        mock_check.return_value = True
        mock_exists.return_value = False
        
        success, output = self.skill.deploy(script="nonexistent.js")
        self.assertFalse(success)
    
    @patch.object(HardhatSkill, '_run_npx_command')
    @patch.object(HardhatSkill, 'check_hardhat_installed')
    def test_run_task(self, mock_check, mock_run):
        """Test task execution."""
        mock_check.return_value = True
        mock_run.return_value = (0, "Task output", "")
        
        success, output = self.skill.run_task("compile")
        self.assertTrue(success)
    
    @patch.object(HardhatSkill, '_run_npx_command')
    @patch.object(HardhatSkill, 'check_hardhat_installed')
    def test_verify_contract(self, mock_check, mock_run):
        """Test contract verification."""
        mock_check.return_value = True
        mock_run.return_value = (0, "Verified successfully", "")
        
        success, output = self.skill.verify_contract(
            "0x123...",
            "contracts/MyToken.sol:MyToken",
            "mainnet"
        )
        self.assertTrue(success)
    
    @patch.object(HardhatSkill, '_run_npx_command')
    @patch.object(HardhatSkill, 'check_hardhat_installed')
    def test_clean(self, mock_check, mock_run):
        """Test clean command."""
        mock_check.return_value = True
        mock_run.return_value = (0, "", "")
        
        result = self.skill.clean()
        self.assertTrue(result)
    
    @patch('subprocess.Popen')
    @patch.object(HardhatSkill, 'check_hardhat_installed')
    def test_node_start(self, mock_check, mock_popen):
        """Test node start."""
        mock_check.return_value = True
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        result = self.skill.node_start()
        self.assertTrue(result)
    
    @patch('subprocess.Popen')
    @patch.object(HardhatSkill, 'check_hardhat_installed')
    def test_node_start_with_fork(self, mock_check, mock_popen):
        """Test node start with fork."""
        mock_check.return_value = True
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        result = self.skill.node_start(fork="https://mainnet.infura.io/v3/key")
        self.assertTrue(result)
    
    def test_node_stop(self):
        """Test node stop."""
        mock_process = Mock()
        mock_process.wait.return_value = None
        self.skill._node_process = mock_process
        
        result = self.skill.node_stop()
        self.assertTrue(result)
    
    def test_node_stop_no_process(self):
        """Test node stop when no process."""
        self.skill._node_process = None
        result = self.skill.node_stop()
        self.assertFalse(result)
    
    @patch.object(HardhatSkill, '_run_npx_command')
    @patch.object(HardhatSkill, 'check_hardhat_installed')
    def test_get_accounts(self, mock_check, mock_run):
        """Test get accounts."""
        mock_check.return_value = True
        mock_run.return_value = (0, "0x123...\\n0x456...", "")
        
        accounts = self.skill.get_accounts()
        self.assertEqual(len(accounts), 2)
    
    @patch.object(HardhatSkill, '_run_npx_command')
    @patch.object(HardhatSkill, 'check_hardhat_installed')
    def test_get_balance(self, mock_check, mock_run):
        """Test get balance."""
        mock_check.return_value = True
        mock_run.return_value = (0, "1.5", "")
        
        balance = self.skill.get_balance("0x123...")
        self.assertEqual(balance, "1.5")
    
    @patch.object(HardhatSkill, '_run_npx_command')
    @patch.object(HardhatSkill, 'check_hardhat_installed')
    def test_flatten_contract(self, mock_check, mock_run):
        """Test contract flattening."""
        mock_check.return_value = True
        mock_run.return_value = (0, "flattened source code", "")
        
        with patch('builtins.open', mock_open()) as mock_file:
            success, output = self.skill.flatten_contract("contracts/Test.sol")
            self.assertTrue(success)
    
    @patch.object(HardhatSkill, '_run_npx_command')
    @patch.object(HardhatSkill, 'check_hardhat_installed')
    def test_flatten_contract_failure(self, mock_check, mock_run):
        """Test contract flattening failure."""
        mock_check.return_value = True
        mock_run.return_value = (1, "", "Error")
        
        success, output = self.skill.flatten_contract("contracts/Test.sol")
        self.assertFalse(success)
    
    def test_templates(self):
        """Test template definitions."""
        self.assertIn("basic", self.skill.TEMPLATES)
        self.assertIn("advanced", self.skill.TEMPLATES)
        self.assertIn("erc20", self.skill.TEMPLATES)
        self.assertIn("erc721", self.skill.TEMPLATES)
    
    def test_parse_test_results(self):
        """Test result parsing."""
        output = "5 passing (2s)\\n2 failing"
        passed, failed = self.skill._parse_test_results(output)
        self.assertEqual(passed, 5)
        self.assertEqual(failed, 2)
    
    def test_parse_test_results_no_failing(self):
        """Test result parsing with no failures."""
        output = "10 passing (5s)"
        passed, failed = self.skill._parse_test_results(output)
        self.assertEqual(passed, 10)
        self.assertEqual(failed, 0)
    
    def test_parse_errors(self):
        """Test error parsing."""
        output = "Error: Some error\\nAnother error line"
        errors = self.skill._parse_errors(output)
        self.assertGreater(len(errors), 0)
    
    @patch('builtins.open', mock_open(read_data='{"abi": [], "bytecode": "0x"}'))
    @patch('pathlib.Path.glob')
    @patch('pathlib.Path.exists')
    def test_parse_compilation_output(self, mock_exists, mock_glob):
        """Test compilation output parsing."""
        mock_exists.return_value = True
        mock_glob.return_value = [Path("Test.sol")]
        
        contracts = self.skill._parse_compilation_output("")
        self.assertIn("Test", contracts)


class TestCompileResult(unittest.TestCase):
    """Test CompileResult dataclass."""
    
    def test_compile_result_creation(self):
        """Test CompileResult creation."""
        result = CompileResult(
            success=True,
            contracts={"Test": {"abi": []}},
            errors=[],
            warnings=[]
        )
        self.assertTrue(result.success)
        self.assertEqual(result.contracts["Test"]["abi"], [])


class TestTestResult(unittest.TestCase):
    """Test TestResult dataclass."""
    
    def test_test_result_creation(self):
        """Test TestResult creation."""
        result = TestResult(
            success=True,
            passed=10,
            failed=0,
            duration=5.0,
            output="All tests passed"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.passed, 10)
        self.assertEqual(result.failed, 0)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestHardhatSkill))
    suite.addTests(loader.loadTestsFromTestCase(TestCompileResult))
    suite.addTests(loader.loadTestsFromTestCase(TestTestResult))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
