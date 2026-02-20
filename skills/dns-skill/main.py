#!/usr/bin/env python3
"""
DNS Query and Resolution Skill
==============================
DNS query tool with record lookup, reverse DNS, and nameserver analysis.

Use when scanning networks, managing remote servers, or when user mentions 
'SSH', 'DNS', 'network'.

Author: Kimi Skills Team
License: MIT
"""

import socket
import json
import dns.resolver
import dns.reversename
import dns.zone
import dns.query
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import ipaddress


class RecordType(Enum):
    """Enumeration of DNS record types."""
    A = "A"
    AAAA = "AAAA"
    MX = "MX"
    NS = "NS"
    TXT = "TXT"
    CNAME = "CNAME"
    SOA = "SOA"
    PTR = "PTR"
    SRV = "SRV"
    CAA = "CAA"
    DNSKEY = "DNSKEY"
    DS = "DS"


@dataclass
class DNSRecord:
    """Data class for DNS records."""
    name: str
    type: str
    ttl: int
    data: str
    priority: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class DNSQueryResult:
    """Data class for DNS query results."""
    domain: str
    record_type: str
    nameserver: str
    records: List[DNSRecord] = field(default_factory=list)
    query_time: float = 0.0
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "domain": self.domain,
            "record_type": self.record_type,
            "nameserver": self.nameserver,
            "records": [r.to_dict() for r in self.records],
            "query_time": self.query_time
        }
        if self.error:
            result["error"] = self.error
        return result


@dataclass
class ReverseDNSResult:
    """Data class for reverse DNS results."""
    ip: str
    hostnames: List[str]
    query_time: float = 0.0
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "ip": self.ip,
            "hostnames": self.hostnames,
            "query_time": self.query_time
        }
        if self.error:
            result["error"] = self.error
        return result


class DNSSkill:
    """
    DNS Query and Resolution Skill class.
    
    Provides comprehensive DNS capabilities:
    - DNS record queries (A, AAAA, MX, NS, TXT, etc.)
    - Reverse DNS lookups
    - Nameserver analysis
    - Zone transfers (AXFR)
    - DNS propagation checking
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize DNSSkill.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.default_nameserver = self.config.get(
            "default_nameserver",
            "8.8.8.8"
        )
        self.default_timeout = self.config.get("default_timeout", 5)
        self.record_types = self.config.get(
            "record_types",
            ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "PTR"]
        )
        
        # Configure resolver
        self.resolver = dns.resolver.Resolver()
        self.resolver.nameservers = [self.default_nameserver]
        self.resolver.timeout = self.default_timeout
        self.resolver.lifetime = self.default_timeout * 2

    def _parse_record(self, answer, record_type: str) -> List[DNSRecord]:
        """Parse DNS answer into DNSRecord objects."""
        records = []
        
        for rdata in answer:
            record_data = str(rdata)
            priority = None
            
            # Handle specific record types
            if record_type == "MX":
                priority = rdata.preference
                record_data = str(rdata.exchange).rstrip('.')
            elif record_type in ["NS", "CNAME"]:
                record_data = str(rdata).rstrip('.')
            elif record_type == "SOA":
                record_data = f"{rdata.mname} {rdata.rname} {rdata.serial}"
            elif record_type == "TXT":
                record_data = ' '.join([str(s) for s in rdata.strings])
            
            records.append(DNSRecord(
                name=str(answer.qname).rstrip('.'),
                type=record_type,
                ttl=answer.ttl,
                data=record_data,
                priority=priority
            ))
        
        return records

    def query(
        self,
        domain: str,
        record_type: str = "A",
        nameserver: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> DNSQueryResult:
        """
        Query DNS records.
        
        Args:
            domain: Domain to query
            record_type: Record type (A, AAAA, MX, NS, etc.)
            nameserver: DNS server to use
            timeout: Query timeout
            
        Returns:
            DNSQueryResult object
        """
        import time
        start_time = time.time()
        
        # Configure resolver
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [nameserver] if nameserver else [self.default_nameserver]
        resolver.timeout = timeout or self.default_timeout
        resolver.lifetime = (timeout or self.default_timeout) * 2
        
        try:
            answer = resolver.resolve(domain, record_type)
            records = self._parse_record(answer, record_type)
            query_time = time.time() - start_time
            
            return DNSQueryResult(
                domain=domain,
                record_type=record_type,
                nameserver=resolver.nameservers[0],
                records=records,
                query_time=query_time
            )
            
        except dns.resolver.NXDOMAIN:
            return DNSQueryResult(
                domain=domain,
                record_type=record_type,
                nameserver=resolver.nameservers[0],
                error="Domain does not exist (NXDOMAIN)",
                query_time=time.time() - start_time
            )
        except dns.resolver.NoAnswer:
            return DNSQueryResult(
                domain=domain,
                record_type=record_type,
                nameserver=resolver.nameservers[0],
                error="No records found",
                query_time=time.time() - start_time
            )
        except dns.resolver.Timeout:
            return DNSQueryResult(
                domain=domain,
                record_type=record_type,
                nameserver=resolver.nameservers[0],
                error="Query timeout",
                query_time=time.time() - start_time
            )
        except Exception as e:
            return DNSQueryResult(
                domain=domain,
                record_type=record_type,
                nameserver=resolver.nameservers[0],
                error=str(e),
                query_time=time.time() - start_time
            )

    def resolve(self, domain: str) -> Dict[str, Any]:
        """
        Resolve domain to IP addresses.
        
        Args:
            domain: Domain to resolve
            
        Returns:
            Dictionary with IP addresses
        """
        ipv4_result = self.query(domain, "A")
        ipv6_result = self.query(domain, "AAAA")
        
        ipv4_addresses = [r.data for r in ipv4_result.records]
        ipv6_addresses = [r.data for r in ipv6_result.records]
        
        return {
            "domain": domain,
            "ipv4": ipv4_addresses,
            "ipv6": ipv6_addresses,
            "success": bool(ipv4_addresses or ipv6_addresses)
        }

    def reverse_lookup(
        self,
        ip: str,
        nameserver: Optional[str] = None
    ) -> ReverseDNSResult:
        """
        Perform reverse DNS lookup.
        
        Args:
            ip: IP address to lookup
            nameserver: DNS server to use
            
        Returns:
            ReverseDNSResult object
        """
        import time
        start_time = time.time()
        
        try:
            # Validate IP
            ip_obj = ipaddress.ip_address(ip)
            
            # Create reverse name
            reverse_name = dns.reversename.from_address(ip)
            
            # Configure resolver
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [nameserver] if nameserver else [self.default_nameserver]
            resolver.timeout = self.default_timeout
            
            # Query PTR records
            answer = resolver.resolve(reverse_name, "PTR")
            hostnames = [str(rdata).rstrip('.') for rdata in answer]
            
            return ReverseDNSResult(
                ip=ip,
                hostnames=hostnames,
                query_time=time.time() - start_time
            )
            
        except ValueError:
            return ReverseDNSResult(
                ip=ip,
                hostnames=[],
                error="Invalid IP address",
                query_time=time.time() - start_time
            )
        except dns.resolver.NXDOMAIN:
            return ReverseDNSResult(
                ip=ip,
                hostnames=[],
                error="No PTR record found",
                query_time=time.time() - start_time
            )
        except Exception as e:
            return ReverseDNSResult(
                ip=ip,
                hostnames=[],
                error=str(e),
                query_time=time.time() - start_time
            )

    def get_nameservers(self, domain: str) -> Dict[str, Any]:
        """
        Get nameservers for a domain.
        
        Args:
            domain: Domain to query
            
        Returns:
            Dictionary with nameserver information
        """
        result = self.query(domain, "NS")
        nameservers = [r.data for r in result.records]
        
        return {
            "domain": domain,
            "nameservers": nameservers,
            "count": len(nameservers),
            "query_time": result.query_time
        }

    def get_mx_records(self, domain: str) -> Dict[str, Any]:
        """
        Get MX records for a domain.
        
        Args:
            domain: Domain to query
            
        Returns:
            Dictionary with MX record information
        """
        result = self.query(domain, "MX")
        mx_records = []
        
        for record in result.records:
            mx_records.append({
                "server": record.data,
                "priority": record.priority
            })
        
        # Sort by priority
        mx_records.sort(key=lambda x: x["priority"])
        
        return {
            "domain": domain,
            "mx_records": mx_records,
            "count": len(mx_records),
            "query_time": result.query_time
        }

    def get_txt_records(self, domain: str) -> Dict[str, Any]:
        """
        Get TXT records for a domain.
        
        Args:
            domain: Domain to query
            
        Returns:
            Dictionary with TXT record information
        """
        result = self.query(domain, "TXT")
        txt_records = [r.data for r in result.records]
        
        return {
            "domain": domain,
            "txt_records": txt_records,
            "count": len(txt_records),
            "query_time": result.query_time
        }

    def check_propagation(
        self,
        domain: str,
        record_type: str = "A",
        nameservers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Check DNS propagation across multiple nameservers.
        
        Args:
            domain: Domain to check
            record_type: Record type to check
            nameservers: List of nameservers to query
            
        Returns:
            Propagation check results
        """
        if nameservers is None:
            nameservers = [
                "8.8.8.8",      # Google
                "8.8.4.4",
                "1.1.1.1",      # Cloudflare
                "1.0.0.1",
                "208.67.222.222", # OpenDNS
                "208.67.220.220"
            ]
        
        results = []
        all_values = set()
        
        for ns in nameservers:
            result = self.query(domain, record_type, nameserver=ns)
            values = [r.data for r in result.records]
            all_values.update(values)
            
            results.append({
                "nameserver": ns,
                "values": values,
                "success": result.error is None,
                "error": result.error
            })
        
        # Check consistency
        consistent = all(
            set(r["values"]) == all_values for r in results if r["success"]
        )
        
        return {
            "domain": domain,
            "record_type": record_type,
            "propagated": consistent,
            "unique_values": list(all_values),
            "nameserver_results": results
        }

    def zone_transfer(self, domain: str, nameserver: str) -> Dict[str, Any]:
        """
        Attempt zone transfer (AXFR).
        
        Args:
            domain: Domain to transfer
            nameserver: Nameserver to query
            
        Returns:
            Zone transfer results
        """
        try:
            records = []
            z = dns.zone.from_xfr(dns.query.xfr(nameserver, domain))
            
            for name, node in z.nodes.items():
                for rdataset in node.rdatasets:
                    record_type = dns.rdatatype.to_text(rdataset.rdtype)
                    for rdata in rdataset:
                        records.append({
                            "name": str(name),
                            "type": record_type,
                            "ttl": rdataset.ttl,
                            "data": str(rdata)
                        })
            
            return {
                "success": True,
                "domain": domain,
                "nameserver": nameserver,
                "records": records,
                "count": len(records)
            }
            
        except Exception as e:
            return {
                "success": False,
                "domain": domain,
                "nameserver": nameserver,
                "error": str(e)
            }


# Entry points for Kimi Skills Framework
def query(domain: str, record_type: str = "A", **kwargs) -> Dict[str, Any]:
    """
    Query DNS records.
    
    Args:
        domain: Domain to query
        record_type: Record type
        **kwargs: Additional parameters
        
    Returns:
        Query result dictionary
    """
    skill = DNSSkill()
    result = skill.query(domain, record_type, **kwargs)
    return result.to_dict()


def resolve(domain: str, **kwargs) -> Dict[str, Any]:
    """Resolve domain entry point."""
    skill = DNSSkill()
    return skill.resolve(domain)


def reverse_lookup(ip: str, **kwargs) -> Dict[str, Any]:
    """Reverse DNS lookup entry point."""
    skill = DNSSkill()
    result = skill.reverse_lookup(ip, **kwargs)
    return result.to_dict()


def get_nameservers(domain: str, **kwargs) -> Dict[str, Any]:
    """Get nameservers entry point."""
    skill = DNSSkill()
    return skill.get_nameservers(domain)


def check_propagation(domain: str, **kwargs) -> Dict[str, Any]:
    """Check DNS propagation entry point."""
    skill = DNSSkill()
    return skill.check_propagation(domain, **kwargs)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="DNS Query Skill")
    parser.add_argument("domain", help="Domain to query")
    parser.add_argument("-t", "--type", default="A",
                       help="Record type")
    parser.add_argument("-n", "--nameserver")
    parser.add_argument("--reverse", action="store_true",
                       help="Perform reverse lookup")
    parser.add_argument("--mx", action="store_true",
                       help="Get MX records")
    parser.add_argument("--ns", action="store_true",
                       help="Get NS records")
    parser.add_argument("--txt", action="store_true",
                       help="Get TXT records")
    parser.add_argument("--propagation", action="store_true",
                       help="Check propagation")
    
    args = parser.parse_args()
    
    if args.reverse:
        result = reverse_lookup(args.domain)
    elif args.mx:
        result = get_mx_records(args.domain)
    elif args.ns:
        result = get_nameservers(args.domain)
    elif args.txt:
        result = get_txt_records(args.domain)
    elif args.propagation:
        result = check_propagation(args.domain, args.type)
    else:
        result = query(args.domain, args.type, nameserver=args.nameserver)
    
    print(json.dumps(result, indent=2))
