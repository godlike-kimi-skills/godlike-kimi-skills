#!/usr/bin/env python3
"""Tests for GraphQL Skill."""

import json
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock

from main import (
    GraphQLClient, GraphQLResponse,
    parse_headers, format_graphql_response
)


class TestGraphQLResponse(unittest.TestCase):
    """Test GraphQLResponse class."""
    
    def test_is_success_with_data(self):
        """Test success check with data."""
        response = GraphQLResponse(data={"user": {"name": "John"}})
        self.assertTrue(response.is_success())
    
    def test_is_success_with_errors(self):
        """Test success check with errors."""
        response = GraphQLResponse(
            data={"user": None},
            errors=[{"message": "User not found"}]
        )
        self.assertFalse(response.is_success())
    
    def test_is_success_empty(self):
        """Test success check with empty response."""
        response = GraphQLResponse()
        self.assertFalse(response.is_success())
    
    def test_get_error_messages(self):
        """Test error message extraction."""
        response = GraphQLResponse(
            errors=[
                {"message": "Error 1"},
                {"message": "Error 2"},
                {"other": "field"}
            ]
        )
        messages = response.get_error_messages()
        self.assertEqual(messages, ["Error 1", "Error 2", "{'other': 'field'}"])


class TestGraphQLClient(unittest.TestCase):
    """Test GraphQLClient functionality."""
    
    def setUp(self):
        """Set up test client."""
        self.client = GraphQLClient("https://api.example.com/graphql")
    
    def tearDown(self):
        """Clean up."""
        self.client.close()
    
    def test_init(self):
        """Test client initialization."""
        client = GraphQLClient(
            "https://api.test.com/graphql",
            headers={"Authorization": "Bearer token"},
            timeout=60
        )
        self.assertEqual(client.endpoint, "https://api.test.com/graphql")
        self.assertEqual(client.timeout, 60)
        client.close()
    
    @patch('main.requests.Session.post')
    def test_query_success(self, mock_post):
        """Test successful query execution."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"user": {"name": "John", "id": "123"}}
        }
        mock_post.return_value = mock_response
        
        result = self.client.query("{ user { name id } }")
        
        self.assertTrue(result.is_success())
        self.assertEqual(result.data["user"]["name"], "John")
    
    @patch('main.requests.Session.post')
    def test_query_with_errors(self, mock_post):
        """Test query with errors."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": None,
            "errors": [{"message": "Field 'user' not found"}]
        }
        mock_post.return_value = mock_response
        
        result = self.client.query("{ invalid }")
        
        self.assertFalse(result.is_success())
        self.assertEqual(len(result.errors), 1)
    
    @patch('main.requests.Session.post')
    def test_query_with_variables(self, mock_post):
        """Test query with variables."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"user": {"name": "John"}}
        }
        mock_post.return_value = mock_response
        
        result = self.client.query(
            "query GetUser($id: ID!) { user(id: $id) { name } }",
            variables={"id": "123"}
        )
        
        self.assertTrue(result.is_success())
        # Verify the request was made with correct payload
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['json']['variables'], {"id": "123"})
    
    @patch('main.requests.Session.post')
    def test_mutate(self, mock_post):
        """Test mutation execution."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"createUser": {"id": "123", "name": "New User"}}
        }
        mock_post.return_value = mock_response
        
        mutation = """
        mutation CreateUser($name: String!) {
            createUser(name: $name) { id name }
        }
        """
        result = self.client.mutate(mutation, variables={"name": "New User"})
        
        self.assertTrue(result.is_success())
        self.assertEqual(result.data["createUser"]["name"], "New User")
    
    @patch('main.requests.Session.post')
    def test_get_schema(self, mock_post):
        """Test schema introspection."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "__schema": {
                    "queryType": {"name": "Query"},
                    "mutationType": {"name": "Mutation"},
                    "types": [
                        {"name": "Query", "fields": [{"name": "user"}]},
                        {"name": "User", "fields": [{"name": "name"}]}
                    ]
                }
            }
        }
        mock_post.return_value = mock_response
        
        schema = self.client.get_schema()
        
        self.assertIn("types", schema)
        self.assertEqual(schema["queryType"]["name"], "Query")
    
    @patch('main.requests.Session.post')
    def test_get_queries(self, mock_post):
        """Test getting available queries."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "__schema": {
                    "queryType": {"name": "Query"},
                    "types": [
                        {
                            "name": "Query",
                            "fields": [
                                {"name": "user", "type": {"name": "User"}},
                                {"name": "users", "type": {"name": "[User]"}}
                            ]
                        }
                    ]
                }
            }
        }
        mock_post.return_value = mock_response
        
        queries = self.client.get_queries()
        
        self.assertEqual(len(queries), 2)
        query_names = [q["name"] for q in queries]
        self.assertIn("user", query_names)
        self.assertIn("users", query_names)
    
    @patch('main.requests.Session.post')
    def test_get_mutations(self, mock_post):
        """Test getting available mutations."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "__schema": {
                    "queryType": {"name": "Query"},
                    "mutationType": {"name": "Mutation"},
                    "types": [
                        {"name": "Query", "fields": []},
                        {
                            "name": "Mutation",
                            "fields": [
                                {"name": "createUser", "type": {"name": "User"}},
                                {"name": "updateUser", "type": {"name": "User"}}
                            ]
                        }
                    ]
                }
            }
        }
        mock_post.return_value = mock_response
        
        mutations = self.client.get_mutations()
        
        self.assertEqual(len(mutations), 2)
        mutation_names = [m["name"] for m in mutations]
        self.assertIn("createUser", mutation_names)
        self.assertIn("updateUser", mutation_names)
    
    @patch('main.requests.Session.post')
    def test_get_type(self, mock_post):
        """Test getting specific type."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "__schema": {
                    "queryType": {"name": "Query"},
                    "types": [
                        {
                            "name": "User",
                            "fields": [
                                {"name": "id", "type": {"name": "ID"}},
                                {"name": "name", "type": {"name": "String"}}
                            ]
                        }
                    ]
                }
            }
        }
        mock_post.return_value = mock_response
        
        user_type = self.client.get_type("User")
        
        self.assertIsNotNone(user_type)
        self.assertEqual(user_type["name"], "User")
    
    def test_format_type(self):
        """Test type formatting."""
        self.assertEqual(
            self.client._format_type({"name": "String", "kind": "SCALAR"}),
            "String"
        )
        self.assertEqual(
            self.client._format_type({
                "kind": "NON_NULL",
                "ofType": {"name": "String", "kind": "SCALAR"}
            }),
            "String!"
        )
        self.assertEqual(
            self.client._format_type({
                "kind": "LIST",
                "ofType": {"name": "User", "kind": "OBJECT"}
            }),
            "[User]"
        )
    
    def test_validate_query_valid(self):
        """Test valid query validation."""
        query = "{ user { name } }"
        errors = self.client.validate_query(query)
        self.assertEqual(len(errors), 0)
    
    def test_validate_query_empty(self):
        """Test empty query validation."""
        errors = self.client.validate_query("")
        self.assertIn("Query is empty", errors)
    
    def test_validate_query_mismatched_braces(self):
        """Test mismatched braces detection."""
        query = "{ user { name }"
        errors = self.client.validate_query(query)
        self.assertTrue(any("Mismatched braces" in e for e in errors))
    
    def test_validate_query_mismatched_parens(self):
        """Test mismatched parentheses detection."""
        query = "{ user(id: \"123\" { name } }"
        errors = self.client.validate_query(query)
        self.assertTrue(any("Mismatched parentheses" in e for e in errors))
    
    @patch('main.requests.Session.post')
    def test_parse_response_invalid_json(self, mock_post):
        """Test parsing invalid JSON response."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.side_effect = json.JSONDecodeError("test", "invalid", 0)
        mock_response.text = "Internal Server Error"
        
        result = self.client._parse_response(mock_response)
        
        self.assertFalse(result.is_success())
        self.assertIn("Invalid JSON", result.get_error_messages()[0])


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_parse_headers(self):
        """Test header parsing."""
        headers = parse_headers(["Authorization: Bearer token", "Content-Type: application/json"])
        self.assertEqual(headers["Authorization"], "Bearer token")
        self.assertEqual(headers["Content-Type"], "application/json")
    
    def test_parse_headers_invalid(self):
        """Test header parsing with invalid format."""
        headers = parse_headers(["InvalidHeader", "Valid: Header"])
        self.assertEqual(headers["Valid"], "Header")
        self.assertNotIn("InvalidHeader", headers)
    
    def test_format_graphql_response_success(self):
        """Test formatting successful response."""
        response = GraphQLResponse(
            data={"user": {"name": "John"}},
            status_code=200
        )
        output = format_graphql_response(response)
        self.assertIn("Success: True", output)
        self.assertIn("John", output)
    
    def test_format_graphql_response_with_errors(self):
        """Test formatting error response."""
        response = GraphQLResponse(
            data=None,
            errors=[{"message": "User not found"}],
            status_code=200
        )
        output = format_graphql_response(response)
        self.assertIn("Success: False", output)
        self.assertIn("Errors:", output)
        self.assertIn("User not found", output)


class TestContextManager(unittest.TestCase):
    """Test context manager functionality."""
    
    def test_context_manager(self):
        """Test client as context manager."""
        with GraphQLClient("https://api.example.com/graphql") as client:
            self.assertIsNotNone(client.session)
        # Session should be closed after exiting context


class TestFormatSchema(unittest.TestCase):
    """Test schema formatting."""
    
    @patch('main.requests.Session.post')
    def test_format_schema(self, mock_post):
        """Test schema formatting."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "__schema": {
                    "queryType": {"name": "Query"},
                    "mutationType": {"name": "Mutation"},
                    "subscriptionType": {"name": "Subscription"},
                    "types": [
                        {
                            "name": "Query",
                            "fields": [
                                {
                                    "name": "user",
                                    "type": {"name": "User", "kind": "OBJECT"},
                                    "args": [
                                        {"name": "id", "type": {"name": "ID", "kind": "SCALAR"}}
                                    ]
                                }
                            ]
                        },
                        {
                            "name": "Mutation",
                            "fields": [
                                {
                                    "name": "createUser",
                                    "type": {"name": "User", "kind": "OBJECT"},
                                    "args": [
                                        {"name": "name", "type": {"name": "String", "kind": "SCALAR"}}
                                    ]
                                }
                            ]
                        },
                        {
                            "name": "Subscription",
                            "fields": [
                                {
                                    "name": "userCreated",
                                    "type": {"name": "User", "kind": "OBJECT"},
                                    "args": []
                                }
                            ]
                        }
                    ]
                }
            }
        }
        mock_post.return_value = mock_response
        
        client = GraphQLClient("https://api.example.com/graphql")
        output = client.format_schema()
        
        self.assertIn("GraphQL Schema", output)
        self.assertIn("Queries:", output)
        self.assertIn("Mutations:", output)
        self.assertIn("Subscriptions:", output)
        self.assertIn("user", output)
        self.assertIn("createUser", output)
        
        client.close()


if __name__ == "__main__":
    unittest.main()
