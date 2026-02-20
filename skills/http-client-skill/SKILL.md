---
name: http-client-skill
description: HTTP client and API testing tool. Use when making HTTP requests, testing REST APIs, debugging endpoints, or when user mentions 'HTTP', 'REST', 'API', 'endpoint', 'GET', 'POST', 'curl', 'requests', 'status code', 'header', 'JSON API'. Supports GET/POST/PUT/DELETE/PATCH methods, custom headers, query parameters, request body handling, response analysis, and error handling.
---

# HTTP Client Skill

HTTP client for making requests to REST APIs and web services with comprehensive request/response handling.

## Capabilities

- **HTTP Methods**: GET, POST, PUT, DELETE, PATCH
- **Header Management**: Custom headers, authentication, content-type
- **Request Body**: JSON, form data, raw body support
- **Response Analysis**: Status codes, headers, body parsing
- **Error Handling**: Timeout, retry, connection errors
- **Query Parameters**: URL encoding, parameter building

## Use When

- Testing REST APIs or web endpoints
- Debugging HTTP requests and responses
- Making API calls to external services
- Checking API status and health
- Verifying authentication headers
- Analyzing response data

## Out of Scope

- Web scraping (use web-scraper skill)
- Browser automation (use browser-automation skill)
- WebSocket connections
- File upload streaming
- Proxy configuration
- Certificate management

## Quick Start

### Basic GET Request

```python
from scripts.main import HTTPClient

client = HTTPClient()
response = client.get("https://api.example.com/users")
print(response.status_code)
print(response.json())
```

### POST with JSON Body

```python
client = HTTPClient()
response = client.post(
    "https://api.example.com/users",
    json={"name": "John", "email": "john@example.com"},
    headers={"Authorization": "Bearer token123"}
)
```

### Using Headers and Params

```python
response = client.get(
    "https://api.example.com/search",
    params={"q": "python", "limit": 10},
    headers={"Accept": "application/json"}
)
```

## CLI Usage

```bash
# GET request
python scripts/main.py GET https://api.github.com/users/octocat

# POST with JSON
python scripts/main.py POST https://httpbin.org/post -j '{"key": "value"}'

# With headers
python scripts/main.py GET https://api.example.com/data -H "Authorization: Bearer token" -H "Accept: application/json"

# With query params
python scripts/main.py GET https://api.example.com/search -p "q=python&limit=5"
```

## Reference

See [references/http_methods.md](references/http_methods.md) for detailed method documentation.
