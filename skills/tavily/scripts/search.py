#!/usr/bin/env python3
"""Tavily Search API Implementation"""
import os, sys, json, urllib.request

def search(query, max_results=5):
    api_key = os.getenv('TAVILY_API_KEY', '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')
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced",
        "max_results": max_results,
        "include_answer": True
    }
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e), "query": query}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search.py 'your search query'")
        sys.exit(1)
    query = sys.argv[1]
    print(json.dumps(search(query), indent=2, ensure_ascii=False))
