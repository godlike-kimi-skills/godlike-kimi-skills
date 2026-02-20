#!/usr/bin/env python3
"""
GraphQL Skill - Main module for GraphQL query execution and debugging.

Features:
- Query/Mutation execution
- Schema introspection
- Variable management
- Response formatting
- WebSocket subscriptions
- Authentication support
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import requests
import websocket


@dataclass
class GraphQLResponse:
    """GraphQL response container."""
    data: Optional[Dict] = None
    errors: List[Dict] = field(default_factory=list)
    extensions: Optional[Dict] = None
    status_code: int = 200
    raw_response: str = ""
    
    def is_success(self) -> bool:
        """Check if response has no errors."""
        return not self.errors and self.data is not None
    
    def get_error_messages(self) -> List[str]:
        """Get list of error messages."""
        return [e.get('message', str(e)) for e in self.errors]


class GraphQLClient:
    """
    GraphQL client for query execution and schema introspection.
    
    Features:
    - Execute queries and mutations
    - Schema introspection and exploration
    - Variable substitution
    - Custom headers and authentication
    - WebSocket subscription support
    - Response formatting
    """
    
    # Introspection query for schema discovery
    INTROSPECTION_QUERY = """
    query IntrospectionQuery {
        __schema {
            queryType { name }
            mutationType { name }
            subscriptionType { name }
            types {
                ...FullType
            }
        }
    }

    fragment FullType on __Type {
        kind
        name
        description
        fields(includeDeprecated: true) {
            name
            description
            args {
                ...InputValue
            }
            type {
                ...TypeRef
            }
            isDeprecated
            deprecationReason
        }
        inputFields {
            ...InputValue
        }
        interfaces {
            ...TypeRef
        }
        enumValues(includeDeprecated: true) {
            name
            description
            isDeprecated
            deprecationReason
        }
        possibleTypes {
            ...TypeRef
        }
    }

    fragment InputValue on __InputValue {
        name
        description
        type { ...TypeRef }
        defaultValue
    }

    fragment TypeRef on __Type {
        kind
        name
        ofType {
            kind
            name
            ofType {
                kind
                name
                ofType {
                    kind
                    name
                    ofType {
                        kind
                        name
                        ofType {
                            kind
                            name
                            ofType {
                                kind
                                name
                                ofType {
                                    kind
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    
    def __init__(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30
    ):
        """
        Initialize GraphQL client.
        
        Args:
            endpoint: GraphQL endpoint URL
            headers: Default headers to include in all requests
            timeout: Request timeout in seconds
        """
        self.endpoint = endpoint
        self.headers = headers or {}
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self._schema_cache: Optional[Dict] = None
    
    def _make_request(
        self,
        query: str,
        variables: Optional[Dict] = None,
        operation_name: Optional[str] = None
    ) -> requests.Response:
        """Make HTTP request to GraphQL endpoint."""
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        if operation_name:
            payload["operationName"] = operation_name
        
        response = self.session.post(
            self.endpoint,
            json=payload,
            timeout=self.timeout
        )
        
        return response
    
    def _parse_response(self, response: requests.Response) -> GraphQLResponse:
        """Parse HTTP response into GraphQLResponse."""
        try:
            data = response.json()
        except json.JSONDecodeError:
            return GraphQLResponse(
                status_code=response.status_code,
                errors=[{"message": f"Invalid JSON response: {response.text[:200]}"}],
                raw_response=response.text
            )
        
        return GraphQLResponse(
            data=data.get('data'),
            errors=data.get('errors', []),
            extensions=data.get('extensions'),
            status_code=response.status_code,
            raw_response=response.text
        )
    
    def query(
        self,
        query_string: str,
        variables: Optional[Dict] = None,
        operation_name: Optional[str] = None
    ) -> GraphQLResponse:
        """
        Execute a GraphQL query.
        
        Args:
            query_string: GraphQL query string
            variables: Query variables
            operation_name: Operation name for multi-operation queries
        
        Returns:
            GraphQLResponse with data/errors
        """
        response = self._make_request(query_string, variables, operation_name)
        return self._parse_response(response)
    
    def mutate(
        self,
        mutation_string: str,
        variables: Optional[Dict] = None,
        operation_name: Optional[str] = None
    ) -> GraphQLResponse:
        """
        Execute a GraphQL mutation.
        
        Args:
            mutation_string: GraphQL mutation string
            variables: Mutation variables
            operation_name: Operation name
        
        Returns:
            GraphQLResponse with data/errors
        """
        return self.query(mutation_string, variables, operation_name)
    
    def get_schema(self, use_cache: bool = True) -> Dict:
        """
        Get GraphQL schema via introspection.
        
        Args:
            use_cache: Use cached schema if available
        
        Returns:
            Schema dictionary
        """
        if use_cache and self._schema_cache:
            return self._schema_cache
        
        response = self.query(self.INTROSPECTION_QUERY)
        
        if not response.is_success():
            raise RuntimeError(f"Schema introspection failed: {response.get_error_messages()}")
        
        schema = response.data.get('__schema', {})
        self._schema_cache = schema
        return schema
    
    def get_queries(self) -> List[Dict]:
        """Get available query fields from schema."""
        schema = self.get_schema()
        query_type = schema.get('queryType')
        
        if not query_type:
            return []
        
        types = schema.get('types', [])
        query_type_def = next(
            (t for t in types if t.get('name') == query_type.get('name')),
            None
        )
        
        return query_type_def.get('fields', []) if query_type_def else []
    
    def get_mutations(self) -> List[Dict]:
        """Get available mutation fields from schema."""
        schema = self.get_schema()
        mutation_type = schema.get('mutationType')
        
        if not mutation_type:
            return []
        
        types = schema.get('types', [])
        mutation_type_def = next(
            (t for t in types if t.get('name') == mutation_type.get('name')),
            None
        )
        
        return mutation_type_def.get('fields', []) if mutation_type_def else []
    
    def get_subscriptions(self) -> List[Dict]:
        """Get available subscription fields from schema."""
        schema = self.get_schema()
        subscription_type = schema.get('subscriptionType')
        
        if not subscription_type:
            return []
        
        types = schema.get('types', [])
        subscription_type_def = next(
            (t for t in types if t.get('name') == subscription_type.get('name')),
            None
        )
        
        return subscription_type_def.get('fields', []) if subscription_type_def else []
    
    def get_type(self, type_name: str) -> Optional[Dict]:
        """Get type definition by name."""
        schema = self.get_schema()
        types = schema.get('types', [])
        return next((t for t in types if t.get('name') == type_name), None)
    
    def format_schema(self) -> str:
        """Format schema as readable text."""
        lines = ["GraphQL Schema\n", "=" * 60]
        
        # Queries
        queries = self.get_queries()
        if queries:
            lines.append("\nQueries:")
            for field in queries:
                args = ", ".join([
                    f"{arg['name']}: {self._format_type(arg['type'])}"
                    for arg in field.get('args', [])
                ])
                return_type = self._format_type(field.get('type'))
                lines.append(f"  {field['name']}({args}): {return_type}")
        
        # Mutations
        mutations = self.get_mutations()
        if mutations:
            lines.append("\nMutations:")
            for field in mutations:
                args = ", ".join([
                    f"{arg['name']}: {self._format_type(arg['type'])}"
                    for arg in field.get('args', [])
                ])
                return_type = self._format_type(field.get('type'))
                lines.append(f"  {field['name']}({args}): {return_type}")
        
        # Subscriptions
        subscriptions = self.get_subscriptions()
        if subscriptions:
            lines.append("\nSubscriptions:")
            for field in subscriptions:
                return_type = self._format_type(field.get('type'))
                lines.append(f"  {field['name']}: {return_type}")
        
        return "\n".join(lines)
    
    def _format_type(self, type_def: Dict) -> str:
        """Format type definition as string."""
        kind = type_def.get('kind')
        name = type_def.get('name')
        of_type = type_def.get('ofType')
        
        if kind == 'NON_NULL' and of_type:
            return f"{self._format_type(of_type)}!"
        elif kind == 'LIST' and of_type:
            return f"[{self._format_type(of_type)}]"
        else:
            return name or kind
    
    def subscribe(
        self,
        subscription_query: str,
        variables: Optional[Dict] = None,
        on_message: Optional[callable] = None,
        on_error: Optional[callable] = None,
        timeout: int = 30
    ):
        """
        Execute GraphQL subscription via WebSocket.
        
        Args:
            subscription_query: Subscription query string
            variables: Subscription variables
            on_message: Callback for messages
            on_error: Callback for errors
            timeout: Connection timeout
        """
        # Convert HTTP URL to WebSocket URL
        parsed = urlparse(self.endpoint)
        protocol = "wss" if parsed.scheme == "https" else "ws"
        ws_url = f"{protocol}://{parsed.netloc}{parsed.path}"
        
        # GraphQL WS protocol message
        init_message = {"type": "connection_init"}
        subscribe_message = {
            "type": "start",
            "id": "1",
            "payload": {
                "query": subscription_query,
                "variables": variables or {}
            }
        }
        
        def on_open(ws):
            ws.send(json.dumps(init_message))
            ws.send(json.dumps(subscribe_message))
        
        def on_message_wrapper(ws, message):
            data = json.loads(message)
            if on_message:
                on_message(data)
        
        def on_error_wrapper(ws, error):
            if on_error:
                on_error(error)
        
        ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message_wrapper,
            on_error=on_error_wrapper,
            header=[f"{k}: {v}" for k, v in self.headers.items()]
        )
        
        ws.run_forever(ping_timeout=timeout)
    
    def validate_query(self, query_string: str) -> List[str]:
        """
        Basic query validation.
        
        Args:
            query_string: Query to validate
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check for basic syntax issues
        if not query_string.strip():
            errors.append("Query is empty")
            return errors
        
        # Check for matching braces
        open_count = query_string.count('{')
        close_count = query_string.count('}')
        if open_count != close_count:
            errors.append(f"Mismatched braces: {open_count} opening, {close_count} closing")
        
        # Check for matching parentheses
        open_parens = query_string.count('(')
        close_parens = query_string.count(')')
        if open_parens != close_parens:
            errors.append(f"Mismatched parentheses: {open_parens} opening, {close_parens} closing")
        
        # Check for query/mutation/subscription keyword
        if not any(kw in query_string for kw in ['query', 'mutation', 'subscription', '{']):
            errors.append("Query must start with 'query', 'mutation', 'subscription', or '{'")
        
        return errors
    
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


def format_graphql_response(response: GraphQLResponse, verbose: bool = False) -> str:
    """Format GraphQL response for display."""
    lines = [
        f"Status: {response.status_code}",
        f"Success: {response.is_success()}",
        ""
    ]
    
    if response.errors:
        lines.append("Errors:")
        for error in response.errors:
            lines.append(f"  - {error.get('message', str(error))}")
        lines.append("")
    
    if response.data:
        lines.append("Data:")
        lines.append(json.dumps(response.data, indent=2))
    
    if verbose and response.extensions:
        lines.append("\nExtensions:")
        lines.append(json.dumps(response.extensions, indent=2))
    
    return "\n".join(lines)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GraphQL Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://api.example.com/graphql -f query.gql
  %(prog)s https://api.example.com/graphql -q "{ users { name } }"
  %(prog)s https://api.example.com/graphql -f query.gql -v '{"id": "123"}'
  %(prog)s https://api.example.com/graphql --introspect
  %(prog)s https://api.example.com/graphql -H "Authorization: Bearer token" -f query.gql
        """
    )
    
    parser.add_argument("endpoint", help="GraphQL endpoint URL")
    parser.add_argument("-f", "--file", help="Query file path")
    parser.add_argument("-q", "--query", help="Query string")
    parser.add_argument("-v", "--variables", help="Variables JSON string")
    parser.add_argument("-H", "--header", action="append", default=[],
                       help="HTTP header (format: 'Key: Value')")
    parser.add_argument("--introspect", action="store_true",
                       help="Show schema introspection")
    parser.add_argument("--queries", action="store_true",
                       help="List available queries")
    parser.add_argument("--mutations", action="store_true",
                       help="List available mutations")
    parser.add_argument("-t", "--timeout", type=int, default=30,
                       help="Request timeout in seconds")
    parser.add_argument("--validate", action="store_true",
                       help="Validate query syntax only")
    parser.add_argument("-o", "--output", help="Output file for response")
    parser.add_argument("--verbose", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Parse headers
    headers = parse_headers(args.header)
    
    try:
        client = GraphQLClient(args.endpoint, headers=headers, timeout=args.timeout)
        
        # Schema introspection
        if args.introspect:
            print(client.format_schema())
            return
        
        if args.queries:
            queries = client.get_queries()
            print("Available Queries:")
            for q in queries:
                print(f"  - {q['name']}")
            return
        
        if args.mutations:
            mutations = client.get_mutations()
            print("Available Mutations:")
            for m in mutations:
                print(f"  - {m['name']}")
            return
        
        # Get query
        query_string = None
        if args.file:
            with open(args.file) as f:
                query_string = f.read()
        elif args.query:
            query_string = args.query
        else:
            print("Error: Provide query via -f/--file or -q/--query", file=sys.stderr)
            sys.exit(1)
        
        # Validate query
        if args.validate:
            errors = client.validate_query(query_string)
            if errors:
                print("Validation errors:")
                for error in errors:
                    print(f"  - {error}")
                sys.exit(1)
            else:
                print("Query is valid")
                return
        
        # Parse variables
        variables = None
        if args.variables:
            variables = json.loads(args.variables)
        
        # Execute query
        response = client.query(query_string, variables)
        
        # Format output
        output = format_graphql_response(response, args.verbose)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Response saved to {args.output}")
        else:
            print(output)
        
        # Exit with error code if query failed
        sys.exit(0 if response.is_success() else 1)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
