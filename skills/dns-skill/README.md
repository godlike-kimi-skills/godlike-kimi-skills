# dns-skill

DNS query and resolution tool with record lookup, reverse DNS, and nameserver analysis.

Use when scanning networks, managing remote servers, or when user mentions 'SSH', 'DNS', 'network'.

## Features

- **DNS Resolution**: Resolve domains to IP addresses
- **Record Queries**: Query A, AAAA, MX, NS, TXT, SOA, PTR records
- **Reverse DNS**: IP to hostname lookups
- **Nameserver Analysis**: Get and analyze nameservers
- **Propagation Check**: Check DNS propagation across servers
- **Zone Transfer**: Attempt AXFR zone transfers
- **MX Analysis**: Mail server record queries

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### As a Skill

```python
from main import query, resolve, reverse_lookup, get_nameservers

# Query specific record type
result = query("example.com", "A")

# Resolve domain (A and AAAA)
result = resolve("example.com")

# Reverse DNS lookup
result = reverse_lookup("8.8.8.8")

# Get nameservers
result = get_nameservers("example.com")

# Get MX records
result = query("example.com", "MX")

# Get TXT records
result = query("example.com", "TXT")

# Check DNS propagation
result = check_propagation("example.com", "A")
```

### Command Line

```bash
# Query A record
python main.py example.com

# Query specific type
python main.py example.com -t MX

# Reverse lookup
python main.py 8.8.8.8 --reverse

# Get MX records
python main.py example.com --mx

# Get NS records
python main.py example.com --ns

# Get TXT records
python main.py example.com --txt

# Check propagation
python main.py example.com --propagation
```

## Configuration

Edit `skill.json` to customize:

```json
{
  "config": {
    "default_nameserver": "8.8.8.8",
    "default_timeout": 5,
    "record_types": ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "PTR"]
  }
}
```

## Supported Record Types

- **A**: IPv4 address
- **AAAA**: IPv6 address
- **MX**: Mail exchange
- **NS**: Nameserver
- **TXT**: Text record
- **CNAME**: Canonical name
- **SOA**: Start of authority
- **PTR**: Pointer (reverse DNS)
- **SRV**: Service record
- **CAA**: Certification Authority Authorization

## Advanced Usage

```python
from main import DNSSkill

skill = DNSSkill()

# Custom nameserver
result = skill.query(
    domain="example.com",
    record_type="A",
    nameserver="1.1.1.1"
)

# Zone transfer attempt
result = skill.zone_transfer("example.com", "ns1.example.com")

# Check propagation
result = skill.check_propagation(
    domain="example.com",
    record_type="A",
    nameservers=["8.8.8.8", "1.1.1.1", "208.67.222.222"]
)
```

## Output Format

### A Record Query

```json
{
  "domain": "example.com",
  "record_type": "A",
  "nameserver": "8.8.8.8",
  "records": [
    {
      "name": "example.com",
      "type": "A",
      "ttl": 3600,
      "data": "93.184.216.34",
      "priority": null
    }
  ],
  "query_time": 0.045
}
```

### MX Record Query

```json
{
  "domain": "example.com",
  "record_type": "MX",
  "nameserver": "8.8.8.8",
  "records": [
    {
      "name": "example.com",
      "type": "MX",
      "ttl": 3600,
      "data": "mail.example.com",
      "priority": 10
    }
  ],
  "query_time": 0.052
}
```

### Reverse DNS

```json
{
  "ip": "8.8.8.8",
  "hostnames": ["dns.google"],
  "query_time": 0.038
}
```

### Propagation Check

```json
{
  "domain": "example.com",
  "record_type": "A",
  "propagated": true,
  "unique_values": ["93.184.216.34"],
  "nameserver_results": [
    {
      "nameserver": "8.8.8.8",
      "values": ["93.184.216.34"],
      "success": true,
      "error": null
    }
  ]
}
```

## Testing

```bash
python -m pytest tests/
```

## License

MIT License - See LICENSE file
