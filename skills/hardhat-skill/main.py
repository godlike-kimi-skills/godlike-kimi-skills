"""
Hardhat Skill - Hardhat Ethereum development environment toolkit.
Use when developing blockchain applications, interacting with smart contracts, 
or when user mentions 'Ethereum', 'Web3', 'blockchain'.
"""

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
import yaml
from jinja2 import Environment, FileSystemLoader, Template


@dataclass
class CompileResult:
    """Represents compilation result."""
    success: bool
    contracts: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


@dataclass
class TestResult:
    """Represents test execution result."""
    success: bool
    passed: int
    failed: int
    duration: float
    output: str


class HardhatSkill:
    """
    Hardhat development environment skill with project initialization,
    contract compilation, testing, and deployment capabilities.
    """
    
    # Project templates
    TEMPLATES = {
        "basic": {
            "description": "Basic Hardhat project",
            "contracts": ["Lock.sol"],
            "tests": ["Lock.js"],
            "scripts": ["deploy.js"]
        },
        "advanced": {
            "description": "Advanced project with TypeScript",
            "contracts": ["Lock.sol", "Token.sol"],
            "tests": ["Lock.ts", "Token.ts"],
            "scripts": ["deploy.ts"]
        },
        "erc20": {
            "description": "ERC20 token project",
            "contracts": ["MyToken.sol"],
            "tests": ["MyToken.test.js"],
            "scripts": ["deploy-token.js"]
        },
        "erc721": {
            "description": "ERC721 NFT project",
            "contracts": ["MyNFT.sol"],
            "tests": ["MyNFT.test.js"],
            "scripts": ["deploy-nft.js"]
        }
    }
    
    def __init__(self, config_path: Optional[str] = None,
                 project_path: Optional[str] = None):
        """
        Initialize Hardhat Skill.
        
        Args:
            config_path: Path to configuration JSON file
            project_path: Path to Hardhat project (overrides config)
        """
        self.config = self._load_config(config_path)
        self.project_path = Path(project_path or self.config.get("project_path", "."))
        self._node_process: Optional[subprocess.Popen] = None
        self._env = Environment(loader=FileSystemLoader('.'))
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from JSON file."""
        default_config = {
            "project_path": ".",
            "default_network": "hardhat",
            "solidity_version": "0.8.19",
            "optimizer": {
                "enabled": True,
                "runs": 200
            },
            "paths": {
                "sources": "./contracts",
                "tests": "./test",
                "scripts": "./scripts",
                "cache": "./cache",
                "artifacts": "./artifacts"
            },
            "mocha": {
                "timeout": 40000
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                default_config.update(config)
        
        return default_config
    
    def _run_npx_command(self, command: List[str], cwd: Optional[str] = None,
                         capture_output: bool = True, timeout: Optional[int] = None) -> Tuple[int, str, str]:
        """
        Run npx command.
        
        Args:
            command: Command arguments
            cwd: Working directory
            capture_output: Capture stdout/stderr
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (returncode, stdout, stderr)
        """
        full_command = ["npx", "hardhat"] + command
        
        try:
            result = subprocess.run(
                full_command,
                cwd=cwd or str(self.project_path),
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except FileNotFoundError:
            return -1, "", "npx not found. Please install Node.js and npm."
    
    def check_hardhat_installed(self) -> bool:
        """Check if Hardhat is installed in project."""
        hardhat_dir = self.project_path / "node_modules" / "hardhat"
        return hardhat_dir.exists()
    
    def install_hardhat(self) -> bool:
        """Install Hardhat dependencies."""
        try:
            result = subprocess.run(
                ["npm", "install", "--save-dev", "hardhat"],
                cwd=str(self.project_path),
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            print("npm not found. Please install Node.js.")
            return False
    
    def init_project(self, name: str, template: str = "basic",
                     install_deps: bool = True) -> bool:
        """
        Initialize new Hardhat project.
        
        Args:
            name: Project name
            template: Project template (basic, advanced, erc20, erc721)
            install_deps: Install dependencies
            
        Returns:
            True if initialization successful
        """
        project_dir = Path(name)
        
        if project_dir.exists():
            print(f"Directory {name} already exists")
            return False
        
        # Create project directory
        project_dir.mkdir(parents=True)
        self.project_path = project_dir
        
        # Initialize npm
        subprocess.run(["npm", "init", "-y"], cwd=str(project_dir), capture_output=True)
        
        # Install Hardhat
        if not self.install_hardhat():
            return False
        
        # Create Hardhat config
        self._create_hardhat_config()
        
        # Create directory structure
        self._create_directories()
        
        # Create template files
        self._create_template_files(template)
        
        # Install additional dependencies
        if install_deps:
            self._install_template_dependencies(template)
        
        print(f"Project '{name}' initialized successfully with template '{template}'")
        return True
    
    def _create_directories(self) -> None:
        """Create project directory structure."""
        dirs = ["contracts", "test", "scripts"]
        for dir_name in dirs:
            (self.project_path / dir_name).mkdir(exist_ok=True)
    
    def _create_hardhat_config(self) -> None:
        """Create hardhat.config.js file."""
        solidity_version = self.config.get("solidity_version", "0.8.19")
        optimizer = self.config.get("optimizer", {"enabled": True, "runs": 200})
        networks = self.config.get("networks", {})
        etherscan = self.config.get("etherscan", {})
        
        config_content = f'''require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {{
  solidity: "{solidity_version}",
  settings: {{
    optimizer: {{
      enabled: {str(optimizer.get("enabled", True)).lower()},
      runs: {optimizer.get("runs", 200)}
    }}
  }},
  networks: {json.dumps(networks, indent=2)},
  etherscan: {{
    apiKey: {json.dumps(etherscan.get("apiKey", ""))}
  }},
  paths: {{
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  }},
  mocha: {{
    timeout: 40000
  }}
}};
'''
        
        config_path = self.project_path / "hardhat.config.js"
        with open(config_path, 'w') as f:
            f.write(config_content)
    
    def _create_template_files(self, template: str) -> None:
        """Create template files."""
        template_data = self.TEMPLATES.get(template, self.TEMPLATES["basic"])
        
        # Create sample contract
        sample_contract = '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract Lock {
    uint public unlockTime;
    address payable public owner;

    event Withdrawal(uint amount, uint when);

    constructor(uint _unlockTime) payable {
        require(
            block.timestamp < _unlockTime,
            "Unlock time should be in the future"
        );

        unlockTime = _unlockTime;
        owner = payable(msg.sender);
    }

    function withdraw() public {
        require(block.timestamp >= unlockTime, "You can't withdraw yet");
        require(msg.sender == owner, "You aren't the owner");

        emit Withdrawal(address(this).balance, block.timestamp);

        owner.transfer(address(this).balance);
    }
}
'''
        
        contract_path = self.project_path / "contracts" / "Lock.sol"
        with open(contract_path, 'w') as f:
            f.write(sample_contract)
        
        # Create sample test
        sample_test = '''const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Lock", function () {
  it("Should set the right unlockTime", async function () {
    const latestTime = Math.floor(Date.now() / 1000);
    const ONE_YEAR_IN_SECS = 365 * 24 * 60 * 60;
    const unlockTime = latestTime + ONE_YEAR_IN_SECS;

    const Lock = await ethers.getContractFactory("Lock");
    const lock = await Lock.deploy(unlockTime, { value: 1 });

    expect(await lock.unlockTime()).to.equal(unlockTime);
  });
});
'''
        
        test_path = self.project_path / "test" / "Lock.js"
        with open(test_path, 'w') as f:
            f.write(sample_test)
        
        # Create deploy script
        deploy_script = '''const hre = require("hardhat");

async function main() {
  const latestTime = Math.floor(Date.now() / 1000);
  const ONE_YEAR_IN_SECS = 365 * 24 * 60 * 60;
  const unlockTime = latestTime + ONE_YEAR_IN_SECS;

  const Lock = await hre.ethers.getContractFactory("Lock");
  const lock = await Lock.deploy(unlockTime, { value: hre.ethers.utils.parseEther("1") });

  await lock.deployed();

  console.log(`Lock deployed to ${lock.address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
'''
        
        script_path = self.project_path / "scripts" / "deploy.js"
        with open(script_path, 'w') as f:
            f.write(deploy_script)
    
    def _install_template_dependencies(self, template: str) -> None:
        """Install template-specific dependencies."""
        deps = ["@nomicfoundation/hardhat-toolbox"]
        
        if template in ["erc20", "erc721"]:
            deps.append("@openzeppelin/contracts")
        
        try:
            subprocess.run(
                ["npm", "install", "--save-dev"] + deps,
                cwd=str(self.project_path),
                capture_output=True
            )
        except Exception as e:
            print(f"Warning: Failed to install some dependencies: {e}")
    
    def compile_contracts(self, optimizer: bool = True, runs: int = 200,
                         force: bool = False, quiet: bool = False) -> CompileResult:
        """
        Compile Solidity contracts.
        
        Args:
            optimizer: Enable optimizer
            runs: Optimizer runs
            force: Force recompilation
            quiet: Suppress output
            
        Returns:
            CompileResult object
        """
        if not self.check_hardhat_installed():
            return CompileResult(False, {}, [], ["Hardhat not installed"])
        
        command = ["compile"]
        
        if force:
            command.append("--force")
        
        if quiet:
            command.append("--quiet")
        
        returncode, stdout, stderr = self._run_npx_command(
            command, timeout=300
        )
        
        success = returncode == 0
        contracts = {}
        errors = []
        warnings = []
        
        if success:
            # Parse compilation output
            contracts = self._parse_compilation_output(stdout)
        else:
            errors = self._parse_errors(stderr or stdout)
        
        return CompileResult(success, contracts, errors, warnings)
    
    def _parse_compilation_output(self, output: str) -> Dict[str, Any]:
        """Parse compilation output."""
        contracts = {}
        artifacts_dir = self.project_path / "artifacts"
        
        if artifacts_dir.exists():
            for contract_file in (self.project_path / "contracts").glob("*.sol"):
                contract_name = contract_file.stem
                artifact_path = artifacts_dir / "contracts" / contract_file.name / f"{contract_name}.json"
                
                if artifact_path.exists():
                    with open(artifact_path, 'r') as f:
                        artifact = json.load(f)
                        contracts[contract_name] = {
                            "abi": artifact.get("abi"),
                            "bytecode": artifact.get("bytecode"),
                            "deployedBytecode": artifact.get("deployedBytecode")
                        }
        
        return contracts
    
    def _parse_errors(self, output: str) -> List[str]:
        """Parse compilation errors."""
        errors = []
        for line in output.split('\n'):
            if 'error' in line.lower() or 'Error:' in line:
                errors.append(line.strip())
        return errors
    
    def test(self, grep: Optional[str] = None, 
             verbose: bool = False,
             network: Optional[str] = None) -> TestResult:
        """
        Run Hardhat tests.
        
        Args:
            grep: Only run tests matching pattern
            verbose: Verbose output
            network: Network to run on
            
        Returns:
            TestResult object
        """
        if not self.check_hardhat_installed():
            return TestResult(False, 0, 0, 0, "Hardhat not installed")
        
        command = ["test"]
        
        if grep:
            command.extend(["--grep", grep])
        
        if verbose:
            command.append("--verbose")
        
        if network:
            command.extend(["--network", network])
        
        start_time = time.time()
        returncode, stdout, stderr = self._run_npx_command(
            command, timeout=300
        )
        duration = time.time() - start_time
        
        output = stdout + stderr
        success = returncode == 0
        
        # Parse test results
        passed, failed = self._parse_test_results(output)
        
        return TestResult(success, passed, failed, duration, output)
    
    def _parse_test_results(self, output: str) -> Tuple[int, int]:
        """Parse test results from output."""
        passed = 0
        failed = 0
        
        # Look for passing/failing test patterns
        for line in output.split('\n'):
            if 'passing' in line.lower():
                match = re.search(r'(\d+) passing', line)
                if match:
                    passed = int(match.group(1))
            if 'failing' in line.lower():
                match = re.search(r'(\d+) failing', line)
                if match:
                    failed = int(match.group(1))
        
        return passed, failed
    
    def deploy(self, network: str = "hardhat", 
               script: str = "deploy.js",
               verify: bool = False) -> Tuple[bool, str]:
        """
        Deploy contracts using script.
        
        Args:
            network: Target network
            script: Deployment script path
            verify: Verify on Etherscan after deployment
            
        Returns:
            Tuple of (success, output)
        """
        if not self.check_hardhat_installed():
            return False, "Hardhat not installed"
        
        script_path = self.project_path / "scripts" / script
        if not script_path.exists():
            return False, f"Script not found: {script}"
        
        command = ["run", f"scripts/{script}", "--network", network]
        
        returncode, stdout, stderr = self._run_npx_command(
            command, timeout=300
        )
        
        success = returncode == 0
        output = stdout + stderr
        
        return success, output
    
    def run_task(self, task_name: str, args: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Run Hardhat task.
        
        Args:
            task_name: Name of task to run
            args: Additional task arguments
            
        Returns:
            Tuple of (success, output)
        """
        if not self.check_hardhat_installed():
            return False, "Hardhat not installed"
        
        command = [task_name] + (args or [])
        
        returncode, stdout, stderr = self._run_npx_command(command)
        
        return returncode == 0, stdout + stderr
    
    def verify_contract(self, address: str, contract: str,
                       network: str = "mainnet",
                       constructor_args: Optional[List] = None) -> Tuple[bool, str]:
        """
        Verify contract on Etherscan.
        
        Args:
            address: Contract address
            contract: Contract path (e.g., "contracts/MyToken.sol:MyToken")
            network: Network name
            constructor_args: Constructor arguments
            
        Returns:
            Tuple of (success, output)
        """
        if not self.check_hardhat_installed():
            return False, "Hardhat not installed"
        
        command = [
            "verify",
            "--network", network,
            address,
            contract
        ]
        
        if constructor_args:
            for arg in constructor_args:
                command.append(str(arg))
        
        returncode, stdout, stderr = self._run_npx_command(command, timeout=120)
        
        return returncode == 0, stdout + stderr
    
    def clean(self) -> bool:
        """
        Clean build artifacts.
        
        Returns:
            True if successful
        """
        if not self.check_hardhat_installed():
            return False
        
        returncode, _, _ = self._run_npx_command(["clean"])
        return returncode == 0
    
    def node_start(self, port: int = 8545, 
                   fork: Optional[str] = None,
                   fork_block_number: Optional[int] = None) -> bool:
        """
        Start local Hardhat node.
        
        Args:
            port: Node port
            fork: Fork URL
            fork_block_number: Fork block number
            
        Returns:
            True if started successfully
        """
        if not self.check_hardhat_installed():
            return False
        
        command = ["node", "--port", str(port)]
        
        if fork:
            command.extend(["--fork", fork])
            if fork_block_number:
                command.extend(["--fork-block-number", str(fork_block_number)])
        
        try:
            self._node_process = subprocess.Popen(
                ["npx", "hardhat"] + command,
                cwd=str(self.project_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for node to start
            time.sleep(3)
            
            if self._node_process.poll() is None:
                print(f"Hardhat node started on port {port}")
                return True
            else:
                print("Failed to start Hardhat node")
                return False
                
        except Exception as e:
            print(f"Error starting node: {e}")
            return False
    
    def node_stop(self) -> bool:
        """
        Stop local Hardhat node.
        
        Returns:
            True if stopped successfully
        """
        if self._node_process:
            self._node_process.terminate()
            try:
                self._node_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._node_process.kill()
            
            self._node_process = None
            print("Hardhat node stopped")
            return True
        
        return False
    
    def run_script(self, script: str, network: str = "hardhat") -> Tuple[bool, str]:
        """
        Run JavaScript/TypeScript script.
        
        Args:
            script: Script path
            network: Target network
            
        Returns:
            Tuple of (success, output)
        """
        return self.deploy(network, script)
    
    def get_accounts(self, network: str = "hardhat") -> List[str]:
        """
        Get list of accounts.
        
        Args:
            network: Network name
            
        Returns:
            List of addresses
        """
        success, output = self.run_task("accounts")
        
        if success:
            # Parse account addresses
            accounts = []
            for line in output.split('\n'):
                line = line.strip()
                if line.startswith('0x') and len(line) == 42:
                    accounts.append(line)
            return accounts
        
        return []
    
    def get_balance(self, address: str, network: str = "hardhat") -> Optional[str]:
        """
        Get ETH balance for address.
        
        Args:
            address: Ethereum address
            network: Network name
            
        Returns:
            Balance in ETH or None
        """
        command = ["console", "--network", network]
        code = f'''const balance = await ethers.provider.getBalance("{address}"); console.log(ethers.utils.formatEther(balance)); process.exit(0);'''
        
        returncode, stdout, stderr = self._run_npx_command(
            command + ["--eval", code], timeout=30
        )
        
        if returncode == 0:
            for line in stdout.split('\n'):
                try:
                    float(line.strip())
                    return line.strip()
                except ValueError:
                    continue
        
        return None
    
    def flatten_contract(self, contract_path: str) -> Tuple[bool, str]:
        """
        Flatten contract for verification.
        
        Args:
            contract_path: Path to contract file
            
        Returns:
            Tuple of (success, output)
        """
        output_path = self.project_path / "flattened.sol"
        
        command = [
            "flatten",
            contract_path
        ]
        
        returncode, stdout, stderr = self._run_npx_command(command)
        
        if returncode == 0:
            with open(output_path, 'w') as f:
                f.write(stdout)
            return True, str(output_path)
        
        return False, stderr
    
    def estimate_gas(self, contract: str, method: str, 
                     args: Optional[List] = None,
                     network: str = "hardhat") -> Optional[int]:
        """
        Estimate gas for contract method.
        
        Args:
            contract: Contract name
            method: Method name
            args: Method arguments
            network: Network name
            
        Returns:
            Estimated gas or None
        """
        args_str = json.dumps(args or [])
        code = f'''
        const Contract = await ethers.getContractFactory("{contract}");
        const estimate = await Contract.signer.estimateGas(
            Contract.interface.encodeFunctionData("{method}", {args_str})
        );
        console.log(estimate.toString());
        process.exit(0);
        '''
        
        command = ["console", "--network", network, "--eval", code]
        returncode, stdout, stderr = self._run_npx_command(command, timeout=30)
        
        if returncode == 0:
            for line in stdout.split('\n'):
                try:
                    return int(line.strip())
                except ValueError:
                    continue
        
        return None


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Hardhat Skill CLI")
    parser.add_argument("--config", default="config.json", help="Config file path")
    parser.add_argument("--project", help="Project path")
    parser.add_argument("command", choices=["init", "compile", "test", "deploy", "clean", "node"], help="Command")
    parser.add_argument("--name", help="Project name")
    parser.add_argument("--template", default="basic", help="Project template")
    parser.add_argument("--network", default="hardhat", help="Network")
    parser.add_argument("--script", default="deploy.js", help="Deployment script")
    
    args = parser.parse_args()
    
    skill = HardhatSkill(args.config, args.project)
    
    if args.command == "init":
        skill.init_project(args.name, args.template)
    elif args.command == "compile":
        result = skill.compile_contracts()
        print(f"Compilation {'successful' if result.success else 'failed'}")
    elif args.command == "test":
        result = skill.test(network=args.network)
        print(f"Tests: {result.passed} passed, {result.failed} failed")
    elif args.command == "deploy":
        success, output = skill.deploy(args.network, args.script)
        print(output)
    elif args.command == "clean":
        skill.clean()
    elif args.command == "node":
        skill.node_start()
