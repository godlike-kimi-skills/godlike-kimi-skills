#!/usr/bin/env python3
"""
HTTP Client Skill - Main module for HTTP requests and API testing.

Supports GET, POST, PUT, DELETE, PATCH methods with headers,
query parameters, JSON body, and response analysis.
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union
from urllib.parse import urlencode, parse_qs, urlparse, urlunparse

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


@dataclass
class Response:
    """HTTP Response wrapper with convenient accessors."""
    
    status_code: int
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    url: str = ""
    elapsed_ms: float = 0.0
    
    def json(self) -> Any:
        """Parse response body as JSON."""
        try:
            return json.loads(self.body)
        except json.JSONDecodeError as e:
            raise ValueError(f"Response is not valid JSON: {e}")
    
    def is_success(self) -> bool:
        """Check if response status is 2xx."""
        return 200 <= self.status_code < 300
    
    def is_redirect(self) -> bool:
        """Check if response status is 3xx."""
        return 300 <= self.status_code < 400
    
    def is_client_error(self) -> bool:
        """Check if response status is 4xx."""
        return 400 <= self.status_code < 500
    
    def is_server_error(self) -> bool:
        """Check if response status is 5xx."""
        return self.status_code >= 500
    
    def get_header(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get header value case-insensitively."""
        name_lower = name.lower()
        for key, value in self.headers.items():
            if key.lower() == name_lower:
                return value
        return default
    
    def __repr__(self) -> str:
        return f"Response(status={self.status_code}, url='{self.url}')"


class HTTPClient:
    """
    HTTP Client for making API requests with retry logic and error handling.
    
    Features:
    - Support for all HTTP methods
    - Automatic retries with exponential backoff
    - Custom headers and query parameters
    - JSON and form data body support
    - Response parsing and validation
    - Timeout configuration
    """
    
    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        default_headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize HTTP client.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            default_headers: Headers to include in all requests
        """
        self.timeout = timeout
        self.default_headers = default_headers or {
            "User-Agent": "HTTPClient-Skill/1.0"
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.default_headers)
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _build_url(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Build URL with query parameters."""
        if not params:
            return url
        
        parsed = urlparse(url)
        existing_params = parse_qs(parsed.query)
        existing_params.update({k: [str(v)] for k, v in params.items()})
        new_query = urlencode(existing_params, doseq=True)
        
        return urlunparse(parsed._replace(query=new_query))
    
    def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict, str]] = None,
        json_data: Optional[Dict] = None,
        **kwargs
    ) -> Response:
        """Execute HTTP request and return wrapped response."""
        url = self._build_url(url, params)
        
        request_headers = dict(self.session.headers)
        if headers:
            request_headers.update(headers)
        
        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                headers=request_headers,
                data=data,
                json=json_data,
                timeout=self.timeout,
                **kwargs
            )
            
            return Response(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=response.text,
                url=response.url,
                elapsed_ms=response.elapsed.total_seconds() * 1000
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request to {url} timed out after {self.timeout}s")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to {url}: {e}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed: {e}")
    
    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Response:
        """Execute GET request."""
        return self._make_request("GET", url, headers, params, **kwargs)
    
    def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict, str]] = None,
        json: Optional[Dict] = None,
        **kwargs
    ) -> Response:
        """Execute POST request."""
        return self._make_request("POST", url, headers, params, data, json, **kwargs)
    
    def put(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict, str]] = None,
        json: Optional[Dict] = None,
        **kwargs
    ) -> Response:
        """Execute PUT request."""
        return self._make_request("PUT", url, headers, params, data, json, **kwargs)
    
    def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Response:
        """Execute DELETE request."""
        return self._make_request("DELETE", url, headers, params, **kwargs)
    
    def patch(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict, str]] = None,
        json: Optional[Dict] = None,
        **kwargs
    ) -> Response:
        """Execute PATCH request."""
        return self._make_request("PATCH", url, headers, params, data, json, **kwargs)
    
    def head(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Response:
        """Execute HEAD request."""
        return self._make_request("HEAD", url, headers, params, **kwargs)
    
    def options(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Response:
        """Execute OPTIONS request."""
        return self._make_request("OPTIONS", url, headers, params, **kwargs)
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def parse_headers(header_list: list) -> Dict[str, str]:
    """Parse header strings into dictionary."""
    headers = {}
    for header in header_list:
        if ":" in header:
            key, value = header.split(":", 1)
            headers[key.strip()] = value.strip()
    return headers


def parse_params(param_string: str) -> Dict[str, str]:
    """Parse query parameter string into dictionary."""
    params = {}
    for param in param_string.split("&"):
        if "=" in param:
            key, value = param.split("=", 1)
            params[key] = value
    return params


def format_response(response: Response, verbose: bool = False) -> str:
    """Format response for display."""
    lines = [
        f"Status: {response.status_code}",
        f"URL: {response.url}",
        f"Time: {response.elapsed_ms:.2f}ms",
        ""
    ]
    
    if verbose:
        lines.append("Headers:")
        for key, value in response.headers.items():
            lines.append(f"  {key}: {value}")
        lines.append("")
    
    lines.append("Body:")
    try:
        # Try to pretty print JSON
        json_data = response.json()
        lines.append(json.dumps(json_data, indent=2))
    except ValueError:
        lines.append(response.body[:2000])  # Limit body output
    
    return "\n".join(lines)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="HTTP Client for API testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s GET https://api.github.com/users/octocat
  %(prog)s POST https://httpbin.org/post -j '{"key": "value"}'
  %(prog)s PUT https://api.example.com/users/1 -j '{"name": "John"}'
  %(prog)s DELETE https://api.example.com/users/1
        """
    )
    
    parser.add_argument("method", choices=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
                       help="HTTP method")
    parser.add_argument("url", help="Request URL")
    parser.add_argument("-H", "--header", action="append", default=[],
                       help="HTTP header (format: 'Key: Value')")
    parser.add_argument("-p", "--params",
                       help="Query parameters (format: 'key1=value1&key2=value2')")
    parser.add_argument("-j", "--json",
                       help="JSON body (as string)")
    parser.add_argument("-d", "--data",
                       help="Raw body data")
    parser.add_argument("-t", "--timeout", type=int, default=30,
                       help="Request timeout in seconds (default: 30)")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Show response headers")
    parser.add_argument("-s", "--status-only", action="store_true",
                       help="Only show status code")
    
    args = parser.parse_args()
    
    # Parse headers and params
    headers = parse_headers(args.header)
    params = parse_params(args.params) if args.params else None
    
    # Parse JSON body
    json_data = None
    if args.json:
        try:
            json_data = json.loads(args.json)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON body - {e}", file=sys.stderr)
            sys.exit(1)
    
    # Make request
    try:
        client = HTTPClient(timeout=args.timeout)
        
        method_func = getattr(client, args.method.lower())
        kwargs = {}
        if json_data:
            kwargs["json"] = json_data
        if args.data:
            kwargs["data"] = args.data
        
        response = method_func(args.url, headers=headers, params=params, **kwargs)
        
        if args.status_only:
            print(response.status_code)
        else:
            print(format_response(response, args.verbose))
        
        # Exit with non-zero status for error responses
        sys.exit(0 if response.is_success() else 1)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
