# dns-skill

DNS query and resolution tool with record lookup, reverse DNS, and nameserver analysis.

Use when scanning networks, managing remote servers, or when user mentions 'SSH', 'DNS', 'network'.

## Overview

This skill provides comprehensive DNS query capabilities including record lookups, reverse DNS, propagation checking, and zone transfer attempts.

## Triggers

- "dns lookup"
- "resolve domain"
- "reverse dns"
- "nameserver"
- "mx record"
- "txt record"
- "dns query"

## Functions

### query(domain, record_type="A", **kwargs)

Query DNS records for a domain.

**Parameters:**
- `domain` (str): Domain to query
- `record_type` (str): Record type (A, AAAA, MX, NS, TXT, etc.)
- `nameserver` (str): Custom DNS server
- `timeout` (int): Query timeout in seconds

**Returns:**
Dictionary with query results including records, TTL, and query time.

### resolve(domain)

Resolve domain to IP addresses (A and AAAA records).

**Parameters:**
- `domain` (str): Domain to resolve

**Returns:**
Dictionary with IPv4 and IPv6 addresses.

### reverse_lookup(ip, **kwargs)

Perform reverse DNS lookup.

**Parameters:**
- `ip` (str): IP address to lookup
- `nameserver` (str): Custom DNS server

**Returns:**
Dictionary with hostnames for the IP.

### get_nameservers(domain)

Get nameservers for a domain.

**Parameters:**
- `domain` (str): Domain to query

**Returns:**
Dictionary with nameserver list.

### check_propagation(domain, **kwargs)

Check DNS propagation across multiple nameservers.

**Parameters:**
- `domain` (str): Domain to check
- `record_type` (str): Record type to check
- `nameservers` (list): List of nameservers to query

**Returns:**
Propagation status and results from each nameserver.

## Examples

```python
# Query A record
query("example.com", "A")

# Query MX records
query("example.com", "MX")

# Query TXT records
query("example.com", "TXT")

# Resolve domain
resolve("example.com")

# Reverse lookup
reverse_lookup("8.8.8.8")

# Get nameservers
get_nameservers("example.com")

# Check propagation
check_propagation("example.com", "A")
```

## Record Types

| Type | Description |
|------|-------------|
| A | IPv4 address |
| AAAA | IPv6 address |
| MX | Mail exchange server |
| NS | Nameserver |
| TXT | Text record (SPF, DKIM) |
| CNAME | Canonical name/alias |
| SOA | Start of authority |
| PTR | Reverse DNS pointer |
| SRV | Service record |
| CAA | Certificate authority |

## Error Handling

The skill handles DNS errors:
- NXDOMAIN: Domain doesn't exist
- NoAnswer: No records of specified type
- Timeout: Query timeout
- Server failure

## Requirements

- Python 3.8+
- dnspython library
