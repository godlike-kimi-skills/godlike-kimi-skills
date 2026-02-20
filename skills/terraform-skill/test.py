#!/usr/bin/env python3
"""
Terraform Skill - Test Suite
Tests for Plan/Apply/State management, Module operations
"""

import unittest
import json
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock, call
from io import StringIO

# Import the main module
import main as tf_cli


class TestTerraformManager(unittest.TestCase):
    """Test Terraform Manager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)
    
    @patch('subprocess.run')
    def test_validate_terraform(self, mock_run):
        """Test Terraform validation"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Terraform v1.5.0')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        
        mock_run.assert_called_once()
        self.assertEqual(tf.working_dir, self.temp_dir)
    
    @patch('subprocess.run')
    def test_validate_terraform_not_found(self, mock_run):
        """Test Terraform not found error"""
        mock_run.side_effect = FileNotFoundError()
        
        with self.assertRaises(SystemExit):
            tf_cli.TerraformManager(working_dir=self.temp_dir)
    
    @patch('subprocess.run')
    def test_init(self, mock_run):
        """Test terraform init"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Initialized!')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.init()
        
        self.assertTrue(result)
        mock_run.assert_called_with(
            ['terraform', 'init', '-no-color'],
            capture_output=True,
            text=True,
            cwd=self.temp_dir,
            timeout=300,
            env={**os.environ, 'TF_IN_AUTOMATION': 'true'}
        )
    
    @patch('subprocess.run')
    def test_init_with_upgrade(self, mock_run):
        """Test terraform init with upgrade"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Upgraded!')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.init(upgrade=True, reconfigure=True)
        
        self.assertTrue(result)
        cmd = mock_run.call_args[0][0]
        self.assertIn('-upgrade', cmd)
        self.assertIn('-reconfigure', cmd)
    
    @patch('subprocess.run')
    def test_validate(self, mock_run):
        """Test terraform validate"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"valid": true, "diagnostics": []}'
        )
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        is_valid, diagnostics = tf.validate()
        
        self.assertTrue(is_valid)
        self.assertEqual(diagnostics, [])
    
    @patch('subprocess.run')
    def test_validate_invalid(self, mock_run):
        """Test terraform validate with errors"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='{"valid": false, "diagnostics": [{"severity": "error", "summary": "Bad config"}]}'
        )
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        is_valid, diagnostics = tf.validate()
        
        self.assertFalse(is_valid)
        self.assertEqual(len(diagnostics), 1)
    
    @patch('subprocess.run')
    def test_plan(self, mock_run):
        """Test terraform plan"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Plan generated')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        success, plan_file = tf.plan()
        
        self.assertTrue(success)
        self.assertEqual(plan_file, 'tfplan')
    
    @patch('subprocess.run')
    def test_plan_with_options(self, mock_run):
        """Test terraform plan with options"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Plan generated')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        success, _ = tf.plan(
            var_file='prod.tfvars',
            target='aws_instance.example',
            destroy=True
        )
        
        self.assertTrue(success)
        cmd = mock_run.call_args[0][0]
        self.assertIn('-destroy', cmd)
        self.assertIn('-target', cmd)
        self.assertIn('aws_instance.example', cmd)
    
    @patch('subprocess.run')
    def test_apply(self, mock_run):
        """Test terraform apply"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Applied!')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.apply()
        
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_apply_auto_approve(self, mock_run):
        """Test terraform apply with auto-approve"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Applied!')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.apply(auto_approve=True)
        
        self.assertTrue(result)
        cmd = mock_run.call_args[0][0]
        self.assertIn('-auto-approve', cmd)
    
    @patch('subprocess.run')
    def test_destroy(self, mock_run):
        """Test terraform destroy"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Destroyed!')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.destroy()
        
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_destroy_auto_approve(self, mock_run):
        """Test terraform destroy with auto-approve"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Destroyed!')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.destroy(auto_approve=True, target='aws_instance.example')
        
        self.assertTrue(result)
        cmd = mock_run.call_args[0][0]
        self.assertIn('-auto-approve', cmd)
        self.assertIn('-target', cmd)
    
    # ==================== State Management Tests ====================
    
    @patch('subprocess.run')
    def test_state_list(self, mock_run):
        """Test state list"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='aws_instance.example\naws_s3_bucket.mybucket\n'
        )
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        resources = tf.state_list()
        
        self.assertEqual(len(resources), 2)
        self.assertIn('aws_instance.example', resources)
    
    @patch('subprocess.run')
    def test_state_show(self, mock_run):
        """Test state show"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='id = i-123456\ninstance_type = t2.micro\n'
        )
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        resource = tf.state_show('aws_instance.example')
        
        self.assertIsNotNone(resource)
        self.assertIn('attributes', resource)
    
    @patch('subprocess.run')
    def test_state_rm(self, mock_run):
        """Test state rm"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Removed!')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.state_rm('aws_instance.example')
        
        self.assertTrue(result)
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[2:4], ['state', 'rm'])
    
    @patch('subprocess.run')
    def test_state_mv(self, mock_run):
        """Test state mv"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Moved!')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.state_mv('aws_instance.old', 'aws_instance.new')
        
        self.assertTrue(result)
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[2:5], ['state', 'mv', 'aws_instance.old'])
    
    @patch('subprocess.run')
    def test_state_pull(self, mock_run):
        """Test state pull"""
        mock_state = {'version': 4, 'resources': []}
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(mock_state)
        )
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        state = tf.state_pull()
        
        self.assertIsNotNone(state)
        self.assertEqual(state['version'], 4)
    
    @patch('subprocess.run')
    def test_state_push(self, mock_run):
        """Test state push"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Pushed!')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.state_push('state.json')
        
        self.assertTrue(result)
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[-2:], ['state', 'push'])
    
    # ==================== Import Tests ====================
    
    @patch('subprocess.run')
    def test_import_resource(self, mock_run):
        """Test terraform import"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Imported!')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.import_resource('aws_instance.example', 'i-1234567890abcdef0')
        
        self.assertTrue(result)
        cmd = mock_run.call_args[0][0]
        self.assertIn('import', cmd)
        self.assertIn('aws_instance.example', cmd)
        self.assertIn('i-1234567890abcdef0', cmd)
    
    # ==================== Workspace Tests ====================
    
    @patch('subprocess.run')
    def test_workspace_list(self, mock_run):
        """Test workspace list"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='  default\n* prod\n  dev\n'
        )
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        current, workspaces = tf.workspace_list()
        
        self.assertEqual(current, 'prod')
        self.assertEqual(len(workspaces), 3)
        self.assertIn('prod', workspaces)
    
    @patch('subprocess.run')
    def test_workspace_new(self, mock_run):
        """Test workspace new"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Created!')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.workspace_new('staging')
        
        self.assertTrue(result)
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[2:4], ['workspace', 'new'])
    
    @patch('subprocess.run')
    def test_workspace_select(self, mock_run):
        """Test workspace select"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Selected!')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.workspace_select('dev')
        
        self.assertTrue(result)
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[2:4], ['workspace', 'select'])
    
    @patch('subprocess.run')
    def test_workspace_delete(self, mock_run):
        """Test workspace delete"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Deleted!')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.workspace_delete('old-workspace', force=True)
        
        self.assertTrue(result)
        cmd = mock_run.call_args[0][0]
        self.assertIn('-force', cmd)
    
    @patch('subprocess.run')
    def test_workspace_show(self, mock_run):
        """Test workspace show"""
        mock_run.return_value = MagicMock(returncode=0, stdout='prod')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        current = tf.workspace_show()
        
        self.assertEqual(current, 'prod')
    
    # ==================== Module Tests ====================
    
    def test_modules_list(self):
        """Test modules list"""
        # Create a test .tf file
        tf_content = '''
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "3.0.0"
}

module "eks" {
  source = "terraform-aws-modules/eks/aws"
}
'''
        with open(os.path.join(self.temp_dir, 'main.tf'), 'w') as f:
            f.write(tf_content)
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        modules = tf.modules_list()
        
        self.assertEqual(len(modules), 2)
        module_names = [m['name'] for m in modules]
        self.assertIn('vpc', module_names)
        self.assertIn('eks', module_names)
    
    @patch('subprocess.run')
    def test_get_modules(self, mock_run):
        """Test terraform get"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Downloaded!')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.get_modules()
        
        self.assertTrue(result)
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[1], 'get')
    
    @patch('subprocess.run')
    def test_providers_list(self, mock_run):
        """Test providers list"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='Providers required by configuration:\nprovider[registry.terraform.io/hashicorp/aws]'
        )
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        providers = tf.providers_list()
        
        self.assertIsInstance(providers, list)
    
    # ==================== Format Tests ====================
    
    @patch('subprocess.run')
    def test_fmt(self, mock_run):
        """Test terraform fmt"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Formatted!')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.fmt()
        
        self.assertTrue(result)
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[1], 'fmt')
    
    @patch('subprocess.run')
    def test_fmt_check(self, mock_run):
        """Test terraform fmt --check"""
        mock_run.return_value = MagicMock(returncode=0, stdout='')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.fmt(check=True)
        
        self.assertTrue(result)
        cmd = mock_run.call_args[0][0]
        self.assertIn('-check', cmd)
    
    # ==================== Output Tests ====================
    
    @patch('subprocess.run')
    def test_output(self, mock_run):
        """Test terraform output"""
        mock_output = {'vpc_id': {'value': 'vpc-123456', 'type': 'string'}}
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(mock_output)
        )
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        output = tf.output()
        
        self.assertIsNotNone(output)
        self.assertEqual(output['vpc_id']['value'], 'vpc-123456')
    
    @patch('subprocess.run')
    def test_show(self, mock_run):
        """Test terraform show"""
        mock_state = {'format_version': '1.0', 'values': {}}
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(mock_state)
        )
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.show()
        
        self.assertIsNotNone(result)
    
    # ==================== Taint Tests ====================
    
    @patch('subprocess.run')
    def test_taint(self, mock_run):
        """Test terraform taint"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Tainted!')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.taint('aws_instance.example')
        
        self.assertTrue(result)
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[1], 'taint')
    
    @patch('subprocess.run')
    def test_untaint(self, mock_run):
        """Test terraform untaint"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Untainted!')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.untaint('aws_instance.example')
        
        self.assertTrue(result)
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[1], 'untaint')
    
    # ==================== Refresh Tests ====================
    
    @patch('subprocess.run')
    def test_refresh(self, mock_run):
        """Test terraform refresh"""
        mock_run.return_value = MagicMock(returncode=0, stdout='Refreshed!')
        
        tf = tf_cli.TerraformManager(working_dir=self.temp_dir)
        result = tf.refresh()
        
        self.assertTrue(result)
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[1], 'refresh')


class TestCLI(unittest.TestCase):
    """Test Command Line Interface"""
    
    @patch('main.TerraformManager')
    def test_cli_help(self, mock_tf):
        """Test CLI help output"""
        with patch('sys.argv', ['main.py', '--help']):
            with self.assertRaises(SystemExit) as cm:
                tf_cli.main()
            self.assertEqual(cm.exception.code, 0)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestTerraformManager))
    suite.addTests(loader.loadTestsFromTestCase(TestCLI))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
