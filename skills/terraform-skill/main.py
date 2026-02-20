#!/usr/bin/env python3
"""
Terraform Skill - Infrastructure as Code Management Assistant
Supports Plan/Apply/State management, Module operations
"""

import argparse
import json
import sys
import os
import subprocess
import re
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime


class TerraformManager:
    """Terraform Infrastructure Manager"""
    
    def __init__(self, working_dir: str = '.', terraform_path: str = 'terraform'):
        self.working_dir = working_dir
        self.terraform_path = terraform_path
        self._validate_terraform()
    
    def _validate_terraform(self):
        """Check if Terraform is installed"""
        try:
            result = subprocess.run(
                [self.terraform_path, 'version'],
                capture_output=True,
                text=True,
                cwd=self.working_dir
            )
            if result.returncode != 0:
                print("Error: Terraform is not installed or not in PATH")
                sys.exit(1)
        except FileNotFoundError:
            print("Error: Terraform executable not found. Please install Terraform.")
            sys.exit(1)
    
    def _run_command(self, args: List[str], capture_output: bool = True, 
                     timeout: int = 300) -> Tuple[int, str, str]:
        """Run terraform command"""
        cmd = [self.terraform_path] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                cwd=self.working_dir,
                timeout=timeout,
                env={**os.environ, 'TF_IN_AUTOMATION': 'true'}
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, '', f"Command timed out after {timeout} seconds"
        except Exception as e:
            return -1, '', str(e)
    
    # ==================== Core Operations ====================
    
    def init(self, backend_config: Optional[Dict] = None, 
             upgrade: bool = False, reconfigure: bool = False) -> bool:
        """Initialize Terraform working directory"""
        args = ['init', '-no-color']
        
        if upgrade:
            args.append('-upgrade')
        if reconfigure:
            args.append('-reconfigure')
        
        if backend_config:
            for key, value in backend_config.items():
                args.extend(['-backend-config', f'{key}={value}'])
        
        print("Initializing Terraform...")
        rc, stdout, stderr = self._run_command(args)
        
        if rc == 0:
            print("Initialization successful")
            return True
        else:
            print(f"Initialization failed:\n{stderr}")
            return False
    
    def validate(self) -> Tuple[bool, List[Dict]]:
        """Validate Terraform configuration"""
        args = ['validate', '-no-color', '-json']
        
        rc, stdout, stderr = self._run_command(args)
        
        try:
            result = json.loads(stdout) if stdout else {'valid': False, 'diagnostics': []}
            is_valid = result.get('valid', False)
            diagnostics = result.get('diagnostics', [])
            
            if is_valid:
                print("Configuration is valid")
            else:
                print("Configuration is invalid:")
                for diag in diagnostics:
                    severity = diag.get('severity', 'error')
                    summary = diag.get('summary', 'Unknown error')
                    detail = diag.get('detail', '')
                    print(f"  [{severity.upper()}] {summary}")
                    if detail:
                        print(f"    {detail}")
            
            return is_valid, diagnostics
        except json.JSONDecodeError:
            print(f"Validation failed:\n{stderr}")
            return False, []
    
    def plan(self, var_file: Optional[str] = None, vars: Optional[Dict] = None,
             target: Optional[str] = None, destroy: bool = False,
             detailed_exitcode: bool = False) -> Tuple[bool, Optional[str]]:
        """Generate execution plan"""
        args = ['plan', '-no-color', '-input=false']
        
        if destroy:
            args.append('-destroy')
        if detailed_exitcode:
            args.append('-detailed-exitcode')
        if var_file:
            args.extend(['-var-file', var_file])
        if target:
            args.extend(['-target', target])
        if vars:
            for key, value in vars.items():
                args.extend(['-var', f'{key}={value}'])
        
        # Save plan to file
        plan_file = 'tfplan'
        args.extend(['-out', plan_file])
        
        print("Generating execution plan...")
        rc, stdout, stderr = self._run_command(args, timeout=600)
        
        if rc == 0:
            print("Plan generated successfully")
            print(stdout)
            return True, plan_file
        elif rc == 2 and detailed_exitcode:
            # Changes detected
            print("Plan generated with changes detected")
            print(stdout)
            return True, plan_file
        else:
            print(f"Plan failed:\n{stderr}")
            return False, None
    
    def apply(self, plan_file: Optional[str] = None, auto_approve: bool = False,
              target: Optional[str] = None, var_file: Optional[str] = None,
              vars: Optional[Dict] = None) -> bool:
        """Apply Terraform changes"""
        args = ['apply', '-no-color', '-input=false']
        
        if auto_approve:
            args.append('-auto-approve')
        if target:
            args.extend(['-target', target])
        if var_file:
            args.extend(['-var-file', var_file])
        if vars:
            for key, value in vars.items():
                args.extend(['-var', f'{key}={value}'])
        
        if plan_file and os.path.exists(plan_file):
            args.append(plan_file)
        
        print("Applying Terraform changes...")
        rc, stdout, stderr = self._run_command(args, timeout=1800)
        
        if rc == 0:
            print("Apply completed successfully")
            print(stdout)
            return True
        else:
            print(f"Apply failed:\n{stderr}")
            return False
    
    def destroy(self, auto_approve: bool = False, target: Optional[str] = None,
                var_file: Optional[str] = None) -> bool:
        """Destroy Terraform-managed infrastructure"""
        args = ['destroy', '-no-color', '-input=false']
        
        if auto_approve:
            args.append('-auto-approve')
        if target:
            args.extend(['-target', target])
        if var_file:
            args.extend(['-var-file', var_file])
        
        print("Destroying resources...")
        rc, stdout, stderr = self._run_command(args, timeout=1800)
        
        if rc == 0:
            print("Destroy completed successfully")
            print(stdout)
            return True
        else:
            print(f"Destroy failed:\n{stderr}")
            return False
    
    def refresh(self) -> bool:
        """Refresh state to match real resources"""
        args = ['refresh', '-no-color', '-input=false']
        
        print("Refreshing state...")
        rc, stdout, stderr = self._run_command(args, timeout=600)
        
        if rc == 0:
            print("Refresh completed successfully")
            return True
        else:
            print(f"Refresh failed:\n{stderr}")
            return False
    
    # ==================== State Management ====================
    
    def state_list(self) -> List[str]:
        """List resources in state"""
        args = ['state', 'list', '-no-color']
        
        rc, stdout, stderr = self._run_command(args)
        
        if rc == 0:
            resources = [r.strip() for r in stdout.split('\n') if r.strip()]
            return resources
        else:
            print(f"State list failed:\n{stderr}")
            return []
    
    def state_show(self, address: str) -> Optional[Dict]:
        """Show resource details from state"""
        args = ['state', 'show', '-no-color', address]
        
        rc, stdout, stderr = self._run_command(args)
        
        if rc == 0:
            # Parse the output
            return self._parse_state_show(stdout)
        else:
            print(f"State show failed:\n{stderr}")
            return None
    
    def _parse_state_show(self, output: str) -> Dict:
        """Parse state show output"""
        lines = output.split('\n')
        resource = {'attributes': {}}
        
        for line in lines:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                parts = line.split('=', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip().strip('"')
                    resource['attributes'][key] = value
        
        return resource
    
    def state_rm(self, address: str) -> bool:
        """Remove resource from state"""
        args = ['state', 'rm', '-no-color', address]
        
        print(f"Removing {address} from state...")
        rc, stdout, stderr = self._run_command(args)
        
        if rc == 0:
            print(f"Successfully removed {address} from state")
            return True
        else:
            print(f"State rm failed:\n{stderr}")
            return False
    
    def state_mv(self, source: str, destination: str) -> bool:
        """Move resource in state"""
        args = ['state', 'mv', '-no-color', source, destination]
        
        print(f"Moving {source} to {destination}...")
        rc, stdout, stderr = self._run_command(args)
        
        if rc == 0:
            print(f"Successfully moved resource")
            return True
        else:
            print(f"State mv failed:\n{stderr}")
            return False
    
    def state_pull(self) -> Optional[Dict]:
        """Pull raw state"""
        args = ['state', 'pull', '-no-color']
        
        rc, stdout, stderr = self._run_command(args)
        
        if rc == 0:
            try:
                return json.loads(stdout)
            except json.JSONDecodeError:
                return {'raw': stdout}
        else:
            print(f"State pull failed:\n{stderr}")
            return None
    
    def state_push(self, state_file: str) -> bool:
        """Push state"""
        args = ['state', 'push', '-no-color', state_file]
        
        print(f"Pushing state from {state_file}...")
        rc, stdout, stderr = self._run_command(args)
        
        if rc == 0:
            print("State pushed successfully")
            return True
        else:
            print(f"State push failed:\n{stderr}")
            return False
    
    # ==================== Import Operations ====================
    
    def import_resource(self, address: str, id: str, var_file: Optional[str] = None) -> bool:
        """Import existing resource into state"""
        args = ['import', '-no-color', '-input=false']
        
        if var_file:
            args.extend(['-var-file', var_file])
        
        args.extend([address, id])
        
        print(f"Importing {address}...")
        rc, stdout, stderr = self._run_command(args, timeout=600)
        
        if rc == 0:
            print(f"Successfully imported {address}")
            return True
        else:
            print(f"Import failed:\n{stderr}")
            return False
    
    # ==================== Workspace Management ====================
    
    def workspace_list(self) -> Tuple[str, List[str]]:
        """List workspaces"""
        args = ['workspace', 'list', '-no-color']
        
        rc, stdout, stderr = self._run_command(args)
        
        if rc == 0:
            lines = stdout.strip().split('\n')
            current = None
            workspaces = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('*'):
                    current = line[1:].strip()
                    workspaces.append(current)
                elif line:
                    workspaces.append(line)
            
            return current, workspaces
        else:
            print(f"Workspace list failed:\n{stderr}")
            return None, []
    
    def workspace_new(self, name: str) -> bool:
        """Create new workspace"""
        args = ['workspace', 'new', '-no-color', name]
        
        print(f"Creating workspace: {name}...")
        rc, stdout, stderr = self._run_command(args)
        
        if rc == 0:
            print(f"Workspace {name} created")
            return True
        else:
            print(f"Workspace creation failed:\n{stderr}")
            return False
    
    def workspace_select(self, name: str) -> bool:
        """Select workspace"""
        args = ['workspace', 'select', '-no-color', name]
        
        print(f"Selecting workspace: {name}...")
        rc, stdout, stderr = self._run_command(args)
        
        if rc == 0:
            print(f"Now using workspace: {name}")
            return True
        else:
            print(f"Workspace selection failed:\n{stderr}")
            return False
    
    def workspace_delete(self, name: str, force: bool = False) -> bool:
        """Delete workspace"""
        args = ['workspace', 'delete', '-no-color']
        
        if force:
            args.append('-force')
        
        args.append(name)
        
        print(f"Deleting workspace: {name}...")
        rc, stdout, stderr = self._run_command(args)
        
        if rc == 0:
            print(f"Workspace {name} deleted")
            return True
        else:
            print(f"Workspace deletion failed:\n{stderr}")
            return False
    
    def workspace_show(self) -> Optional[str]:
        """Show current workspace"""
        args = ['workspace', 'show', '-no-color']
        
        rc, stdout, stderr = self._run_command(args)
        
        if rc == 0:
            return stdout.strip()
        else:
            return None
    
    # ==================== Module Operations ====================
    
    def modules_list(self) -> List[Dict]:
        """List modules"""
        # Parse modules from terraform config
        modules = []
        
        # Find all .tf files
        tf_files = Path(self.working_dir).glob('*.tf')
        
        for tf_file in tf_files:
            try:
                with open(tf_file, 'r') as f:
                    content = f.read()
                    
                # Simple regex parsing for module blocks
                module_pattern = r'module\s+"([^"]+)"\s*\{([^}]+)'
                for match in re.finditer(module_pattern, content, re.DOTALL):
                    module_name = match.group(1)
                    module_body = match.group(2)
                    
                    # Extract source
                    source_match = re.search(r'source\s*=\s*"([^"]+)"', module_body)
                    source = source_match.group(1) if source_match else 'N/A'
                    
                    modules.append({
                        'name': module_name,
                        'source': source,
                        'file': str(tf_file)
                    })
            except Exception as e:
                print(f"Error reading {tf_file}: {e}")
        
        return modules
    
    def providers_list(self) -> List[Dict]:
        """List providers"""
        args = ['providers', '-no-color']
        
        rc, stdout, stderr = self._run_command(args)
        
        providers = []
        if rc == 0:
            # Parse provider list output
            lines = stdout.split('\n')
            for line in lines:
                if 'provider[' in line:
                    match = re.search(r'provider\[([^\]]+)\]', line)
                    if match:
                        providers.append({'name': match.group(1)})
        
        return providers
    
    def get_modules(self) -> bool:
        """Download and update modules"""
        args = ['get', '-no-color', '-update']
        
        print("Downloading modules...")
        rc, stdout, stderr = self._run_command(args)
        
        if rc == 0:
            print("Modules downloaded successfully")
            return True
        else:
            print(f"Module download failed:\n{stderr}")
            return False
    
    # ==================== Format and Output ====================
    
    def fmt(self, check: bool = False, recursive: bool = False, write: bool = True) -> bool:
        """Format Terraform configuration"""
        args = ['fmt', '-no-color']
        
        if check:
            args.append('-check')
        if recursive:
            args.append('-recursive')
        if write:
            args.append('-write=true')
        else:
            args.append('-write=false')
        
        rc, stdout, stderr = self._run_command(args)
        
        if rc == 0:
            if check:
                print("All files are formatted correctly")
            else:
                print("Files formatted successfully")
            return True
        elif rc == 3 and check:
            print("Some files need formatting")
            return False
        else:
            print(f"Format failed:\n{stderr}")
            return False
    
    def output(self, name: Optional[str] = None, json_format: bool = True) -> Optional[Any]:
        """Get output values"""
        args = ['output', '-no-color']
        
        if json_format:
            args.append('-json')
        
        if name:
            args.append(name)
        
        rc, stdout, stderr = self._run_command(args)
        
        if rc == 0:
            if json_format:
                try:
                    return json.loads(stdout)
                except json.JSONDecodeError:
                    return stdout
            return stdout
        else:
            print(f"Output failed:\n{stderr}")
            return None
    
    def show(self, path: Optional[str] = None, json_format: bool = True) -> Optional[Any]:
        """Show state or plan"""
        args = ['show', '-no-color']
        
        if json_format:
            args.append('-json')
        
        if path:
            args.append(path)
        
        rc, stdout, stderr = self._run_command(args)
        
        if rc == 0:
            if json_format:
                try:
                    return json.loads(stdout)
                except json.JSONDecodeError:
                    return stdout
            return stdout
        else:
            print(f"Show failed:\n{stderr}")
            return None
    
    def taint(self, address: str) -> bool:
        """Taint resource"""
        args = ['taint', '-no-color', address]
        
        print(f"Tainting {address}...")
        rc, stdout, stderr = self._run_command(args)
        
        if rc == 0:
            print(f"Resource {address} tainted")
            return True
        else:
            print(f"Taint failed:\n{stderr}")
            return False
    
    def untaint(self, address: str) -> bool:
        """Untaint resource"""
        args = ['untaint', '-no-color', address]
        
        print(f"Untainting {address}...")
        rc, stdout, stderr = self._run_command(args)
        
        if rc == 0:
            print(f"Resource {address} untainted")
            return True
        else:
            print(f"Untaint failed:\n{stderr}")
            return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Terraform Skill - Infrastructure as Code Management',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--dir', '-d', default='.', help='Working directory')
    parser.add_argument('--terraform', '-t', default='terraform', help='Terraform executable path')
    
    subparsers = parser.add_subparsers(dest='command', help='Terraform command')
    
    # Init
    init_parser = subparsers.add_parser('init', help='Initialize Terraform')
    init_parser.add_argument('--upgrade', action='store_true', help='Upgrade modules and providers')
    init_parser.add_argument('--reconfigure', action='store_true', help='Reconfigure backend')
    
    # Validate
    subparsers.add_parser('validate', help='Validate configuration')
    
    # Plan
    plan_parser = subparsers.add_parser('plan', help='Generate execution plan')
    plan_parser.add_argument('--var-file', '-f', help='Variable file')
    plan_parser.add_argument('--target', help='Target resource')
    plan_parser.add_argument('--destroy', action='store_true', help='Plan destroy')
    
    # Apply
    apply_parser = subparsers.add_parser('apply', help='Apply changes')
    apply_parser.add_argument('--auto-approve', '-auto', action='store_true')
    apply_parser.add_argument('--plan', help='Plan file to apply')
    apply_parser.add_argument('--var-file', '-f', help='Variable file')
    apply_parser.add_argument('--target', help='Target resource')
    
    # Destroy
    destroy_parser = subparsers.add_parser('destroy', help='Destroy resources')
    destroy_parser.add_argument('--auto-approve', '-auto', action='store_true')
    destroy_parser.add_argument('--target', help='Target resource')
    destroy_parser.add_argument('--var-file', '-f', help='Variable file')
    
    # Refresh
    subparsers.add_parser('refresh', help='Refresh state')
    
    # State
    state_parser = subparsers.add_parser('state', help='State management')
    state_subparsers = state_parser.add_subparsers(dest='state_action')
    
    state_list = state_subparsers.add_parser('list', help='List resources')
    state_show = state_subparsers.add_parser('show', help='Show resource')
    state_show.add_argument('address', help='Resource address')
    state_rm = state_subparsers.add_parser('rm', help='Remove resource')
    state_rm.add_argument('address', help='Resource address')
    state_mv = state_subparsers.add_parser('mv', help='Move resource')
    state_mv.add_argument('source', help='Source address')
    state_mv.add_argument('destination', help='Destination address')
    state_pull = state_subparsers.add_parser('pull', help='Pull state')
    state_push = state_subparsers.add_parser('push', help='Push state')
    state_push.add_argument('file', help='State file')
    
    # Import
    import_parser = subparsers.add_parser('import', help='Import resource')
    import_parser.add_argument('address', help='Resource address')
    import_parser.add_argument('id', help='Resource ID')
    import_parser.add_argument('--var-file', '-f', help='Variable file')
    
    # Workspace
    workspace_parser = subparsers.add_parser('workspace', help='Workspace management')
    workspace_subparsers = workspace_parser.add_subparsers(dest='workspace_action')
    
    workspace_list = workspace_subparsers.add_parser('list', help='List workspaces')
    workspace_new = workspace_subparsers.add_parser('new', help='Create workspace')
    workspace_new.add_argument('name', help='Workspace name')
    workspace_select = workspace_subparsers.add_parser('select', help='Select workspace')
    workspace_select.add_argument('name', help='Workspace name')
    workspace_delete = workspace_subparsers.add_parser('delete', help='Delete workspace')
    workspace_delete.add_argument('name', help='Workspace name')
    workspace_delete.add_argument('--force', action='store_true')
    workspace_show = workspace_subparsers.add_parser('show', help='Show current workspace')
    
    # Modules
    modules_parser = subparsers.add_parser('modules', help='Module operations')
    modules_subparsers = modules_parser.add_subparsers(dest='modules_action')
    modules_list = modules_subparsers.add_parser('list', help='List modules')
    modules_get = modules_subparsers.add_parser('get', help='Download modules')
    modules_providers = modules_subparsers.add_parser('providers', help='List providers')
    
    # Format
    fmt_parser = subparsers.add_parser('fmt', help='Format configuration')
    fmt_parser.add_argument('--check', action='store_true', help='Check only')
    fmt_parser.add_argument('--recursive', '-r', action='store_true')
    
    # Output
    output_parser = subparsers.add_parser('output', help='Show outputs')
    output_parser.add_argument('name', nargs='?', help='Output name')
    
    # Show
    show_parser = subparsers.add_parser('show', help='Show state/plan')
    show_parser.add_argument('path', nargs='?', help='Path to state or plan file')
    
    # Taint/Untaint
    taint_parser = subparsers.add_parser('taint', help='Taint resource')
    taint_parser.add_argument('address', help='Resource address')
    untaint_parser = subparsers.add_parser('untaint', help='Untaint resource')
    untaint_parser.add_argument('address', help='Resource address')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize Terraform manager
    tf = TerraformManager(working_dir=args.dir, terraform_path=args.terraform)
    
    # Execute commands
    if args.command == 'init':
        tf.init(upgrade=args.upgrade, reconfigure=args.reconfigure)
    
    elif args.command == 'validate':
        tf.validate()
    
    elif args.command == 'plan':
        success, plan_file = tf.plan(
            var_file=args.var_file,
            target=args.target,
            destroy=args.destroy
        )
    
    elif args.command == 'apply':
        tf.apply(
            plan_file=args.plan,
            auto_approve=args.auto_approve,
            target=args.target,
            var_file=args.var_file
        )
    
    elif args.command == 'destroy':
        tf.destroy(
            auto_approve=args.auto_approve,
            target=args.target,
            var_file=args.var_file
        )
    
    elif args.command == 'refresh':
        tf.refresh()
    
    elif args.command == 'state':
        if args.state_action == 'list':
            resources = tf.state_list()
            for r in resources:
                print(r)
        elif args.state_action == 'show':
            resource = tf.state_show(args.address)
            if resource:
                print(json.dumps(resource, indent=2))
        elif args.state_action == 'rm':
            tf.state_rm(args.address)
        elif args.state_action == 'mv':
            tf.state_mv(args.source, args.destination)
        elif args.state_action == 'pull':
            state = tf.state_pull()
            if state:
                print(json.dumps(state, indent=2))
        elif args.state_action == 'push':
            tf.state_push(args.file)
    
    elif args.command == 'import':
        tf.import_resource(args.address, args.id, args.var_file)
    
    elif args.command == 'workspace':
        if args.workspace_action == 'list':
            current, workspaces = tf.workspace_list()
            for w in workspaces:
                prefix = '* ' if w == current else '  '
                print(f"{prefix}{w}")
        elif args.workspace_action == 'new':
            tf.workspace_new(args.name)
        elif args.workspace_action == 'select':
            tf.workspace_select(args.name)
        elif args.workspace_action == 'delete':
            tf.workspace_delete(args.name, args.force)
        elif args.workspace_action == 'show':
            current = tf.workspace_show()
            if current:
                print(current)
    
    elif args.command == 'modules':
        if args.modules_action == 'list':
            modules = tf.modules_list()
            print(json.dumps(modules, indent=2))
        elif args.modules_action == 'get':
            tf.get_modules()
        elif args.modules_action == 'providers':
            providers = tf.providers_list()
            print(json.dumps(providers, indent=2))
    
    elif args.command == 'fmt':
        tf.fmt(check=args.check, recursive=args.recursive)
    
    elif args.command == 'output':
        output = tf.output(name=args.name)
        if output:
            print(json.dumps(output, indent=2))
    
    elif args.command == 'show':
        result = tf.show(path=args.path)
        if result:
            print(json.dumps(result, indent=2))
    
    elif args.command == 'taint':
        tf.taint(args.address)
    
    elif args.command == 'untaint':
        tf.untaint(args.address)


if __name__ == '__main__':
    main()
