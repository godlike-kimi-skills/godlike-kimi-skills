#!/usr/bin/env python3
"""
Nmap Port Scanning Skill
========================
Nmap port scanning tool with service detection and OS fingerprinting capabilities.

Use when scanning networks, managing remote servers, or when user mentions 
'SSH', 'DNS', 'network'.

Author: Kimi Skills Team
License: MIT
"""

import json
import sys
import subprocess
import socket
import re
import ipaddress
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from enum import Enum
import xml.etree.ElementTree as ET


class ScanType(Enum):
    """Enumeration of supported scan types."""
    TCP_SYN = "-sS"
    TCP_CONNECT = "-sT"
    UDP = "-sU"
    ACK = "-sA"
    WINDOW = "-sW"
    MAIMON = "-sM"


class ScanIntensity(Enum):
    """Enumeration of scan intensity levels."""
    QUICK = "-T4 -F"
    NORMAL = "-T3"
    INTENSIVE = "-T2 -A"
    PARANOID = "-T1 -A -v"


@dataclass
class ScanResult:
    """Data class to represent scan results."""
    host: str
    state: str
    ports: List[Dict[str, Any]]
    os_info: Optional[Dict[str, Any]] = None
    services: List[Dict[str, Any]] = None
    scan_time: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert scan result to dictionary."""
        return asdict(self)


class NmapSkill:
    """
    Nmap Port Scanning Skill class.
    
    Provides comprehensive network scanning capabilities including:
    - Port scanning (TCP, UDP)
    - Service detection and version identification
    - OS fingerprinting
    - Script scanning
    - Output in multiple formats
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize NmapSkill with configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.default_ports = self.config.get("default_ports", "1-1000")
        self.timeout = self.config.get("timeout", 300)
        self.max_retries = self.config.get("max_retries", 2)
        self._nmap_path = self._find_nmap()

    def _find_nmap(self) -> Optional[str]:
        """Find nmap executable path."""
        import shutil
        return shutil.which("nmap")

    def _validate_target(self, target: str) -> bool:
        """
        Validate target specification.
        
        Args:
            target: Target IP, hostname, or CIDR notation
            
        Returns:
            True if valid, False otherwise
        """
        if not target:
            return False
        
        # Check for valid hostname
        if re.match(r'^[a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)*$', target):
            return True
        
        # Check for valid IP address
        try:
            ipaddress.ip_address(target)
            return True
        except ValueError:
            pass
        
        # Check for valid CIDR notation
        try:
            ipaddress.ip_network(target, strict=False)
            return True
        except ValueError:
            pass
        
        # Check for IP range
        if re.match(r'^(\d{1,3}\.){3}\d{1,3}-(\d{1,3}\.){3}\d{1,3}$', target):
            return True
        
        return False

    def _build_command(
        self,
        target: str,
        ports: Optional[str] = None,
        scan_type: ScanType = ScanType.TCP_SYN,
        intensity: ScanIntensity = ScanIntensity.NORMAL,
        service_detection: bool = True,
        os_detection: bool = False,
        script_scan: Optional[str] = None,
        output_xml: Optional[str] = None
    ) -> List[str]:
        """
        Build nmap command arguments.
        
        Args:
            target: Target to scan
            ports: Port specification (e.g., "80,443" or "1-1000")
            scan_type: Type of scan to perform
            intensity: Scan intensity level
            service_detection: Enable service version detection
            os_detection: Enable OS detection
            script_scan: NSE script to run
            output_xml: XML output file path
            
        Returns:
            List of command arguments
        """
        cmd = [self._nmap_path or "nmap"]
        
        # Add scan type
        cmd.append(scan_type.value)
        
        # Add timing/intensity
        cmd.extend(intensity.value.split())
        
        # Add ports
        if ports:
            cmd.extend(["-p", ports])
        else:
            cmd.extend(["-p", self.default_ports])
        
        # Add service detection
        if service_detection:
            cmd.append("-sV")
        
        # Add OS detection (requires root/admin)
        if os_detection:
            cmd.append("-O")
        
        # Add script scan
        if script_scan:
            cmd.extend(["--script", script_scan])
        
        # Add XML output
        if output_xml:
            cmd.extend(["-oX", output_xml])
        
        # Add timeout
        cmd.extend(["--host-timeout", str(self.timeout)])
        
        # Add max retries
        cmd.extend(["--max-retries", str(self.max_retries)])
        
        # Add target
        cmd.append(target)
        
        return cmd

    def _parse_xml_output(self, xml_file: str) -> List[ScanResult]:
        """
        Parse nmap XML output file.
        
        Args:
            xml_file: Path to XML output file
            
        Returns:
            List of ScanResult objects
        """
        results = []
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            for host in root.findall("host"):
                host_result = self._parse_host(host)
                if host_result:
                    results.append(host_result)
                    
        except ET.ParseError as e:
            return [ScanResult(
                host="",
                state="error",
                ports=[],
                error=f"XML parse error: {str(e)}"
            )]
        
        return results

    def _parse_host(self, host_elem) -> Optional[ScanResult]:
        """Parse individual host element from XML."""
        # Get host address
        address_elem = host_elem.find("address")
        if address_elem is None:
            return None
        
        host_ip = address_elem.get("addr", "unknown")
        
        # Get host status
        status_elem = host_elem.find("status")
        state = status_elem.get("state", "unknown") if status_elem else "unknown"
        
        # Parse ports
        ports_elem = host_elem.find("ports")
        ports = []
        if ports_elem is not None:
            for port in ports_elem.findall("port"):
                port_info = self._parse_port(port)
                if port_info:
                    ports.append(port_info)
        
        # Parse OS info
        os_info = None
        os_elem = host_elem.find("os")
        if os_elem is not None:
            os_info = self._parse_os(os_elem)
        
        return ScanResult(
            host=host_ip,
            state=state,
            ports=ports,
            os_info=os_info,
            services=[p for p in ports if p.get("service")]
        )

    def _parse_port(self, port_elem) -> Optional[Dict[str, Any]]:
        """Parse port element from XML."""
        port_id = port_elem.get("portid", "")
        protocol = port_elem.get("protocol", "tcp")
        
        state_elem = port_elem.find("state")
        port_state = state_elem.get("state", "unknown") if state_elem else "unknown"
        
        service_elem = port_elem.find("service")
        service = {}
        if service_elem is not None:
            service = {
                "name": service_elem.get("name", ""),
                "product": service_elem.get("product", ""),
                "version": service_elem.get("version", ""),
                "extrainfo": service_elem.get("extrainfo", ""),
                "ostype": service_elem.get("ostype", ""),
                "method": service_elem.get("method", "")
            }
        
        return {
            "port": port_id,
            "protocol": protocol,
            "state": port_state,
            "service": service
        }

    def _parse_os(self, os_elem) -> Dict[str, Any]:
        """Parse OS element from XML."""
        osmatch = os_elem.find("osmatch")
        if osmatch is not None:
            return {
                "name": osmatch.get("name", ""),
                "accuracy": osmatch.get("accuracy", ""),
                "line": osmatch.get("line", "")
            }
        return {}

    def scan(
        self,
        target: str,
        ports: Optional[str] = None,
        scan_type: str = "tcp_syn",
        intensity: str = "normal",
        service_detection: bool = True,
        os_detection: bool = False,
        script_scan: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform nmap scan on target.
        
        Args:
            target: Target IP, hostname, or network range
            ports: Port specification (default: 1-1000)
            scan_type: Type of scan (tcp_syn, tcp_connect, udp)
            intensity: Scan intensity (quick, normal, intensive, paranoid)
            service_detection: Enable service version detection
            os_detection: Enable OS detection (requires root)
            script_scan: NSE script to run
            
        Returns:
            Dictionary containing scan results
        """
        if not self._nmap_path:
            return {
                "success": False,
                "error": "nmap not found. Please install nmap."
            }
        
        if not self._validate_target(target):
            return {
                "success": False,
                "error": f"Invalid target: {target}"
            }
        
        # Map string parameters to enums
        scan_type_enum = ScanType(scan_type.replace("-", "_").upper())
        intensity_enum = ScanIntensity(intensity.upper())
        
        # Create temporary XML output file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            xml_output = f.name
        
        try:
            # Build and execute command
            cmd = self._build_command(
                target=target,
                ports=ports,
                scan_type=scan_type_enum,
                intensity=intensity_enum,
                service_detection=service_detection,
                os_detection=os_detection,
                script_scan=script_scan,
                output_xml=xml_output
            )
            
            import time
            start_time = time.time()
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            scan_time = time.time() - start_time
            
            # Parse results
            scan_results = self._parse_xml_output(xml_output)
            
            # Format output
            results_list = []
            for r in scan_results:
                result_dict = r.to_dict()
                result_dict["scan_time"] = scan_time
                results_list.append(result_dict)
            
            return {
                "success": True,
                "command": " ".join(cmd),
                "target": target,
                "results": results_list,
                "hosts_up": len([r for r in scan_results if r.state == "up"]),
                "total_hosts": len(scan_results),
                "scan_time": scan_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Scan timed out after {self.timeout} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            # Cleanup temp file
            try:
                Path(xml_output).unlink(missing_ok=True)
            except:
                pass

    def quick_scan(self, target: str, ports: str = "top-100") -> Dict[str, Any]:
        """
        Quick scan of top ports.
        
        Args:
            target: Target to scan
            ports: Port specification or "top-100"
            
        Returns:
            Scan results
        """
        port_spec = "--top-ports 100" if ports == "top-100" else ports
        return self.scan(
            target=target,
            ports=port_spec,
            scan_type="tcp_syn",
            intensity="quick",
            service_detection=True
        )

    def comprehensive_scan(self, target: str) -> Dict[str, Any]:
        """
        Comprehensive scan with all features.
        
        Args:
            target: Target to scan
            
        Returns:
            Comprehensive scan results
        """
        return self.scan(
            target=target,
            ports="1-65535",
            scan_type="tcp_syn",
            intensity="intensive",
            service_detection=True,
            os_detection=True
        )


# Entry point for Kimi Skills Framework
def scan(target: str, **kwargs) -> Dict[str, Any]:
    """
    Main entry point for nmap scanning.
    
    Args:
        target: Target IP, hostname, or network range
        **kwargs: Additional scan parameters
        
    Returns:
        Scan results dictionary
    """
    skill = NmapSkill()
    return skill.scan(target, **kwargs)


def quick_scan(target: str, **kwargs) -> Dict[str, Any]:
    """Quick scan entry point."""
    skill = NmapSkill()
    return skill.quick_scan(target, **kwargs)


def comprehensive_scan(target: str, **kwargs) -> Dict[str, Any]:
    """Comprehensive scan entry point."""
    skill = NmapSkill()
    return skill.comprehensive_scan(target)


if __name__ == "__main__":
    # CLI interface
    import argparse
    
    parser = argparse.ArgumentParser(description="Nmap Port Scanning Skill")
    parser.add_argument("target", help="Target to scan")
    parser.add_argument("-p", "--ports", help="Port specification")
    parser.add_argument("-s", "--scan-type", default="tcp_syn", 
                       choices=["tcp_syn", "tcp_connect", "udp"])
    parser.add_argument("-i", "--intensity", default="normal",
                       choices=["quick", "normal", "intensive", "paranoid"])
    parser.add_argument("--service", action="store_true", help="Enable service detection")
    parser.add_argument("--os", action="store_true", help="Enable OS detection")
    parser.add_argument("--script", help="NSE script to run")
    
    args = parser.parse_args()
    
    result = scan(
        target=args.target,
        ports=args.ports,
        scan_type=args.scan_type,
        intensity=args.intensity,
        service_detection=args.service,
        os_detection=args.os,
        script_scan=args.script
    )
    
    print(json.dumps(result, indent=2))
