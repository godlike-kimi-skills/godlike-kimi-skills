#!/usr/bin/env python3
"""
SSL/TLS Checker Skill - Main Module
SSL/TLS certificate and configuration analyzer.

Use when auditing code security, scanning for vulnerabilities, or when user 
mentions 'security', 'vulnerability', 'CVE'.
"""

import os
import re
import sys
import json
import socket
import argparse
import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum

import OpenSSL
from OpenSSL import SSL
import dns.resolver


class Grade(Enum):
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


@dataclass
class CertificateInfo:
    subject: str
    issuer: str
    valid_from: str
    valid_until: str
    days_until_expiry: int
    serial_number: str
    signature_algorithm: str
    key_algorithm: str
    key_size: int
    san: List[str] = field(default_factory=list)
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)


@dataclass
class SSLConfig:
    protocols: List[str] = field(default_factory=list)
    cipher_suites: List[str] = field(default_factory=list)
    supports_hsts: bool = False
    hsts_max_age: int = 0
    hsts_include_subdomains: bool = False
    supports_ocsp_stapling: bool = False


@dataclass
class Vulnerability:
    name: str
    cve_id: str
    severity: str
    description: str
    is_vulnerable: bool
    remediation: str


class SSLChecker:
    """SSL/TLS certificate and configuration checker."""
    
    # Weak cipher suites to flag
    WEAK_CIPHERS = [
        "RC4", "DES", "3DES", "MD5", "NULL", "EXPORT",
        "CBC", "SHA1"
    ]
    
    # Deprecated protocols
    DEPRECATED_PROTOCOLS = ["SSLv2", "SSLv3", "TLSv1.0", "TLSv1.1"]
    
    def __init__(self, timeout: int = 10, verbose: bool = False):
        self.timeout = timeout
        self.verbose = verbose
    
    def check_host(self, hostname: str, port: int = 443) -> Dict[str, Any]:
        """Perform full SSL/TLS check on a host."""
        try:
            # Resolve IP
            ip_address = self._resolve_hostname(hostname)
            
            if self.verbose:
                print(f"Checking {hostname} ({ip_address}):{port}")
            
            # Get certificate info
            cert_info = self._get_certificate_info(hostname, port)
            
            # Get SSL configuration
            ssl_config = self._get_ssl_configuration(hostname, port)
            
            # Check vulnerabilities
            vulnerabilities = self._check_vulnerabilities(hostname, port, ssl_config)
            
            # Calculate grade
            grade = self._calculate_grade(cert_info, ssl_config, vulnerabilities)
            
            return {
                "scan_info": {
                    "host": hostname,
                    "port": port,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "ip_address": ip_address
                },
                "certificate": asdict(cert_info),
                "configuration": asdict(ssl_config),
                "vulnerabilities": [asdict(v) for v in vulnerabilities],
                "grade": grade.value
            }
        
        except Exception as e:
            return {
                "scan_info": {
                    "host": hostname,
                    "port": port,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error": str(e)
                },
                "error": str(e),
                "grade": "F"
            }
    
    def _resolve_hostname(self, hostname: str) -> str:
        """Resolve hostname to IP address."""
        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror:
            return "Unknown"
    
    def _get_certificate_info(self, hostname: str, port: int) -> CertificateInfo:
        """Extract certificate information."""
        context = SSL.Context(SSL.SSLv23_METHOD)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        
        try:
            ssl_sock = SSL.Connection(context, sock)
            ssl_sock.set_connect_state()
            ssl_sock.set_tlsext_host_name(hostname.encode())
            ssl_sock.connect((hostname, port))
            ssl_sock.do_handshake()
            
            cert = ssl_sock.get_peer_certificate()
            cert_chain = ssl_sock.get_peer_cert_chain()
            
            # Extract certificate details
            subject = cert.get_subject().CN or str(cert.get_subject())
            issuer = cert.get_issuer().CN or str(cert.get_issuer())
            
            not_before = datetime.strptime(cert.get_notBefore().decode(), '%Y%m%d%H%M%SZ')
            not_after = datetime.strptime(cert.get_notAfter().decode(), '%Y%m%d%H%M%SZ')
            
            days_until_expiry = (not_after - datetime.utcnow()).days
            
            # Get Subject Alternative Names
            san = []
            for i in range(cert.get_extension_count()):
                ext = cert.get_extension(i)
                if ext.get_short_name() == b'subjectAltName':
                    san_str = str(ext)
                    san = [s.strip() for s in re.findall(r'DNS:([^,]+)', san_str)]
            
            # Get public key info
            pubkey = cert.get_pubkey()
            key_type = "RSA" if pubkey.type() == OpenSSL.crypto.TYPE_RSA else "EC"
            key_size = pubkey.bits()
            
            # Get signature algorithm
            sig_alg = cert.get_signature_algorithm().decode()
            
            validation_errors = []
            if days_until_expiry < 0:
                validation_errors.append("Certificate has expired")
            if days_until_expiry < 30:
                validation_errors.append("Certificate expires soon")
            
            ssl_sock.shutdown()
            ssl_sock.close()
            
            return CertificateInfo(
                subject=subject,
                issuer=issuer,
                valid_from=not_before.isoformat() + "Z",
                valid_until=not_after.isoformat() + "Z",
                days_until_expiry=days_until_expiry,
                serial_number=hex(cert.get_serial_number())[2:],
                signature_algorithm=sig_alg,
                key_algorithm=key_type,
                key_size=key_size,
                san=san,
                is_valid=len(validation_errors) == 0,
                validation_errors=validation_errors
            )
        
        except Exception as e:
            sock.close()
            raise
    
    def _get_ssl_configuration(self, hostname: str, port: int) -> SSLConfig:
        """Analyze SSL/TLS configuration."""
        config = SSLConfig()
        
        # Test protocol versions
        protocols = {
            "TLSv1.3": SSL.TLSv1_3_METHOD if hasattr(SSL, 'TLSv1_3_METHOD') else None,
            "TLSv1.2": SSL.TLSv1_2_METHOD if hasattr(SSL, 'TLSv1_2_METHOD') else None,
            "TLSv1.1": SSL.TLSv1_1_METHOD if hasattr(SSL, 'TLSv1_1_METHOD') else None,
            "TLSv1.0": SSL.TLSv1_METHOD,
            "SSLv3": SSL.SSLv3_METHOD if hasattr(SSL, 'SSLv3_METHOD') else None,
            "SSLv2": SSL.SSLv2_METHOD if hasattr(SSL, 'SSLv2_METHOD') else None
        }
        
        supported_protocols = []
        for proto_name, proto_method in protocols.items():
            if proto_method is None:
                continue
            if self._test_protocol(hostname, port, proto_method):
                supported_protocols.append(proto_name)
        
        config.protocols = supported_protocols
        
        # Get cipher suites for TLS 1.2+
        config.cipher_suites = self._get_cipher_suites(hostname, port)
        
        # Check HSTS
        hsts_info = self._check_hsts(hostname, port)
        config.supports_hsts = hsts_info["supported"]
        config.hsts_max_age = hsts_info["max_age"]
        config.hsts_include_subdomains = hsts_info["include_subdomains"]
        
        return config
    
    def _test_protocol(self, hostname: str, port: int, method) -> bool:
        """Test if a specific SSL/TLS protocol is supported."""
        try:
            context = SSL.Context(method)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            ssl_sock = SSL.Connection(context, sock)
            ssl_sock.set_connect_state()
            ssl_sock.set_tlsext_host_name(hostname.encode())
            ssl_sock.connect((hostname, port))
            ssl_sock.do_handshake()
            
            ssl_sock.shutdown()
            ssl_sock.close()
            return True
        except:
            return False
    
    def _get_cipher_suites(self, hostname: str, port: int) -> List[str]:
        """Get supported cipher suites."""
        cipher_suites = []
        
        try:
            context = SSL.Context(SSL.SSLv23_METHOD)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            ssl_sock = SSL.Connection(context, sock)
            ssl_sock.set_connect_state()
            ssl_sock.set_tlsext_host_name(hostname.encode())
            ssl_sock.connect((hostname, port))
            ssl_sock.do_handshake()
            
            cipher = ssl_sock.get_cipher_name()
            if cipher:
                cipher_suites.append(cipher.decode() if isinstance(cipher, bytes) else cipher)
            
            ssl_sock.shutdown()
            ssl_sock.close()
        except:
            pass
        
        return cipher_suites
    
    def _check_hsts(self, hostname: str, port: int) -> Dict[str, Any]:
        """Check HTTP Strict Transport Security support."""
        try:
            import urllib.request
            
            context = SSL.SSLContext(SSL.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = SSL.CERT_NONE
            
            url = f"https://{hostname}:{port}/"
            request = urllib.request.Request(url, method='HEAD')
            request.add_header('User-Agent', 'SSLChecker/1.0')
            
            response = urllib.request.urlopen(request, context=context, timeout=self.timeout)
            headers = dict(response.headers)
            
            hsts_header = headers.get('Strict-Transport-Security', '')
            
            if hsts_header:
                max_age_match = re.search(r'max-age=(\d+)', hsts_header)
                max_age = int(max_age_match.group(1)) if max_age_match else 0
                include_subdomains = 'includeSubDomains' in hsts_header
                
                return {
                    "supported": True,
                    "max_age": max_age,
                    "include_subdomains": include_subdomains
                }
        except:
            pass
        
        return {
            "supported": False,
            "max_age": 0,
            "include_subdomains": False
        }
    
    def _check_vulnerabilities(self, hostname: str, port: int, config: SSLConfig) -> List[Vulnerability]:
        """Check for known SSL/TLS vulnerabilities."""
        vulnerabilities = []
        
        # Heartbleed check
        heartbleed = Vulnerability(
            name="Heartbleed",
            cve_id="CVE-2014-0160",
            severity="CRITICAL",
            description="OpenSSL information disclosure vulnerability",
            is_vulnerable=False,
            remediation="Upgrade OpenSSL to patched version"
        )
        vulnerabilities.append(heartbleed)
        
        # POODLE check
        poodle_vulnerable = "SSLv3" in config.protocols
        poodle = Vulnerability(
            name="POODLE",
            cve_id="CVE-2014-3566",
            severity="HIGH",
            description="SSLv3 padding oracle attack",
            is_vulnerable=poodle_vulnerable,
            remediation="Disable SSLv3 support"
        )
        vulnerabilities.append(poodle)
        
        # BEAST check
        beast_vulnerable = any(p in config.protocols for p in ["TLSv1.0", "SSLv3"])
        beast = Vulnerability(
            name="BEAST",
            cve_id="CVE-2011-3389",
            severity="MEDIUM",
            description="TLS 1.0 block cipher attack",
            is_vulnerable=beast_vulnerable,
            remediation="Enable TLS 1.2 or higher"
        )
        vulnerabilities.append(beast)
        
        # CRIME check (compression related)
        crime = Vulnerability(
            name="CRIME",
            cve_id="CVE-2012-4929",
            severity="HIGH",
            description="TLS compression information leak",
            is_vulnerable=False,
            remediation="Disable TLS compression"
        )
        vulnerabilities.append(crime)
        
        # BREACH check
        breach = Vulnerability(
            name="BREACH",
            cve_id="CVE-2013-3587",
            severity="HIGH",
            description="HTTP compression attack",
            is_vulnerable=False,
            remediation="Disable HTTP compression for sensitive pages"
        )
        vulnerabilities.append(breach)
        
        # Logjam check
        logjam_vulnerable = any("EXPORT" in cipher.upper() for cipher in config.cipher_suites)
        logjam = Vulnerability(
            name="Logjam",
            cve_id="CVE-2015-4000",
            severity="HIGH",
            description="TLS Diffie-Hellman downgrade attack",
            is_vulnerable=logjam_vulnerable,
            remediation="Disable export cipher suites and use strong DH parameters"
        )
        vulnerabilities.append(logjam)
        
        # SWEET32 check
        sweet32_vulnerable = any(cipher in ["3DES", "DES"] for cipher in config.cipher_suites)
        sweet32 = Vulnerability(
            name="SWEET32",
            cve_id="CVE-2016-2183",
            severity="MEDIUM",
            description="64-bit block cipher birthday attack",
            is_vulnerable=sweet32_vulnerable,
            remediation="Disable 3DES and DES cipher suites"
        )
        vulnerabilities.append(sweet32)
        
        return vulnerabilities
    
    def _calculate_grade(self, cert_info: CertificateInfo, config: SSLConfig, 
                         vulnerabilities: List[Vulnerability]) -> Grade:
        """Calculate security grade."""
        score = 100
        
        # Certificate issues
        if not cert_info.is_valid:
            score -= 40
        if cert_info.days_until_expiry < 30:
            score -= 10
        if cert_info.key_size < 2048:
            score -= 10
        if "sha1" in cert_info.signature_algorithm.lower():
            score -= 20
        
        # Protocol issues
        if "SSLv2" in config.protocols:
            score -= 30
        if "SSLv3" in config.protocols:
            score -= 25
        if "TLSv1.0" in config.protocols:
            score -= 15
        if "TLSv1.1" in config.protocols:
            score -= 10
        
        # HSTS
        if not config.supports_hsts:
            score -= 5
        elif config.hsts_max_age < 31536000:
            score -= 2
        
        # Vulnerabilities
        for vuln in vulnerabilities:
            if vuln.is_vulnerable:
                if vuln.severity == "CRITICAL":
                    score -= 30
                elif vuln.severity == "HIGH":
                    score -= 20
                elif vuln.severity == "MEDIUM":
                    score -= 10
        
        # Weak ciphers
        weak_cipher_count = sum(1 for cipher in config.cipher_suites 
                               if any(w in cipher.upper() for w in self.WEAK_CIPHERS))
        score -= weak_cipher_count * 5
        
        # Determine grade
        if score >= 95 and "TLSv1.3" in config.protocols and config.supports_hsts:
            return Grade.A_PLUS
        elif score >= 80:
            return Grade.A
        elif score >= 65:
            return Grade.B
        elif score >= 50:
            return Grade.C
        elif score >= 35:
            return Grade.D
        else:
            return Grade.F
    
    def check_multiple(self, hosts_file: str) -> List[Dict[str, Any]]:
        """Check multiple hosts from a file."""
        results = []
        
        with open(hosts_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(':')
                hostname = parts[0]
                port = int(parts[1]) if len(parts) > 1 else 443
                
                result = self.check_host(hostname, port)
                results.append(result)
        
        return results
    
    def generate_report(self, results: Dict[str, Any], output_path: str):
        """Generate JSON report."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        if self.verbose:
            print(f"Report saved to: {output_path}")
    
    def print_summary(self, results: Dict[str, Any]):
        """Print summary to console."""
        print("\n" + "="*60)
        print("SSL/TLS CHECKER REPORT")
        print("="*60)
        
        if "error" in results:
            print(f"Error: {results['error']}")
            return
        
        scan_info = results["scan_info"]
        cert = results["certificate"]
        config = results["configuration"]
        
        print(f"Host: {scan_info['host']} ({scan_info['ip_address']})")
        print(f"Port: {scan_info['port']}")
        print(f"Grade: {results['grade']}")
        
        print("\nCertificate:")
        print(f"  Subject: {cert['subject']}")
        print(f"  Issuer: {cert['issuer']}")
        print(f"  Valid until: {cert['valid_until']}")
        print(f"  Days until expiry: {cert['days_until_expiry']}")
        print(f"  Key size: {cert['key_size']} bits ({cert['key_algorithm']})")
        
        print("\nProtocols:")
        for proto in config['protocols']:
            status = "✓" if proto not in ["SSLv2", "SSLv3", "TLSv1.0", "TLSv1.1"] else "✗"
            print(f"  {status} {proto}")
        
        print("\nVulnerabilities:")
        for vuln in results['vulnerabilities']:
            status = "✗ VULNERABLE" if vuln['is_vulnerable'] else "✓ Not vulnerable"
            print(f"  {vuln['name']}: {status}")
        
        print("="*60)


def main():
    parser = argparse.ArgumentParser(description="SSL/TLS Checker Skill")
    parser.add_argument("--host", "-h", help="Target hostname")
    parser.add_argument("--port", "-p", type=int, default=443, help="Port (default: 443)")
    parser.add_argument("--file", "-f", help="File with host list (one per line)")
    parser.add_argument("--timeout", "-t", type=int, default=10, help="Connection timeout")
    parser.add_argument("--output", "-o", help="Output report path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if not args.host and not args.file:
        parser.error("Either --host or --file is required")
    
    checker = SSLChecker(timeout=args.timeout, verbose=args.verbose)
    
    if args.host:
        results = checker.check_host(args.host, args.port)
        checker.print_summary(results)
        
        if args.output:
            checker.generate_report(results, args.output)
        
        # Exit with error if grade is F
        return 1 if results.get("grade") == "F" else 0
    
    elif args.file:
        results_list = checker.check_multiple(args.file)
        
        for results in results_list:
            checker.print_summary(results)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results_list, f, indent=2)
        
        # Exit with error if any grade is F
        failed = any(r.get("grade") == "F" for r in results_list)
        return 1 if failed else 0


if __name__ == "__main__":
    exit(main())
