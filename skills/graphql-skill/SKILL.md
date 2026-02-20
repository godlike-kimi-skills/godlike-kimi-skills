---
name: graphql-skill
description: GraphQL query and debugging tool. Use when executing GraphQL queries, exploring GraphQL schemas, debugging GraphQL mutations, or when user mentions 'GraphQL', 'gql', 'query', 'mutation', 'subscription', 'schema introspection', 'GraphQL API', 'graphql endpoint'. Supports Query/Mutation/Subscription execution, schema introspection, variable management, and response formatting.
---

# GraphQL Skill

GraphQL client for query execution, schema exploration, and API debugging.

## Capabilities

- **Query Execution**: Send queries to any GraphQL endpoint
- **Mutation Support**: Execute mutations with variables
- **Schema Introspection**: View available types, queries, mutations
- **Variable Management**: Define and use query variables
- **Response Formatting**: Pretty print JSON responses
- **Authentication**: Header-based auth support
- **Subscription**: WebSocket subscription support

## Use When

- Executing GraphQL queries
- Testing GraphQL mutations
- Exploring GraphQL schemas
- Debugging GraphQL APIs
- Fetching data from GraphQL endpoints
- Validating GraphQL queries
- Working with GraphQL variables

## Out of Scope

- GraphQL server implementation
- Schema definition/stitching
- Complex caching strategies
- Persisted queries setup
- GraphQL federation

## Quick Start

### Execute Query

```python
from scripts.main import GraphQLClient

client = GraphQLClient("https://api.example.com/graphql")

query = """
query GetUser($id: ID!) {
    user(id: $id) {
        name
        email
    }
}
"""

result = client.query(query, variables={"id": "123"})
print(result)
```

### Schema Introspection

```python
# Get schema types
schema = client.get_schema()

# Get available queries
queries = client.get_queries()

# Get available mutations
mutations = client.get_mutations()
```

### CLI Usage

```bash
# Execute query from file
python scripts/main.py https://api.example.com/graphql -f query.gql

# Execute inline query
python scripts/main.py https://api.example.com/graphql -q "{ users { name email } }"

# With variables
python scripts/main.py https://api.example.com/graphql -f query.gql -v '{"id": "123"}'

# Schema introspection
python scripts/main.py https://api.example.com/graphql --introspect

# With authentication
python scripts/main.py https://api.example.com/graphql -f query.gql -H "Authorization: Bearer token"
```

## Reference

See [references/graphql_basics.md](references/graphql_basics.md) for GraphQL syntax reference.
