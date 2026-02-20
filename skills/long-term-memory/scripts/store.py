#!/usr/bin/env python3
import sys, json
from pathlib import Path

def store(key, value):
    f = Path.home() / ".kimi" / "memory.json"
    data = json.loads(f.read_text()) if f.exists() else {}
    data[key] = {"value": value, "time": str(Path().stat())}
    f.write_text(json.dumps(data, indent=2))
    return {"stored": key}

if __name__ == "__main__":
    print(json.dumps(store(sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else {}))
