#!/usr/bin/env python3
"""
Superpowers Tool Set
Based on Kubernetes Operators and GitHub Actions patterns
"""

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


class Superpowers:
    """Collection of powerful tools"""

    @staticmethod
    def api_call(method: str, url: str, headers: str = None, data: str = None) -> Dict:
        """Make HTTP API call"""
        import urllib.request
        import urllib.error

        req = urllib.request.Request(url, method=method)
        if headers:
            for h in headers.split(','):
                key, value = h.split(':', 1)
                req.add_header(key.strip(), value.strip())

        try:
            if data:
                req.data = data.encode('utf-8')
            with urllib.request.urlopen(req, timeout=30) as response:
                return {
                    'status': response.status,
                    'headers': dict(response.headers),
                    'body': response.read().decode('utf-8')[:1000]
                }
        except urllib.error.HTTPError as e:
            return {'error': f'HTTP {e.code}: {e.reason}'}
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def file_process(action: str, pattern: str, path: str) -> Dict:
        """Process files (grep-style)"""
        results = []
        target = Path(path)

        if target.is_file():
            files = [target]
        else:
            files = list(target.rglob('*')) if target.is_dir() else []

        for file_path in files:
            if not file_path.is_file():
                continue
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                if action == 'grep':
                    matches = list(re.finditer(pattern, content))
                    if matches:
                        results.append({
                            'file': str(file_path),
                            'matches': len(matches),
                            'lines': [content[max(0, m.start()-50):m.end()+50] for m in matches[:3]]
                        })
            except Exception as e:
                results.append({'file': str(file_path), 'error': str(e)})

        return {'action': action, 'pattern': pattern, 'results': results}

    @staticmethod
    def transform(input_file: str, output_format: str) -> Dict:
        """Transform data between formats"""
        input_path = Path(input_file)
        if not input_path.exists():
            return {'error': f'File not found: {input_file}'}

        try:
            content = input_path.read_text(encoding='utf-8')
            data = json.loads(content)

            if output_format == 'csv':
                if isinstance(data, list) and data:
                    headers = list(data[0].keys())
                    lines = [','.join(headers)]
                    for row in data:
                        lines.append(','.join(str(row.get(h, '')) for h in headers))
                    output = '\n'.join(lines)
                else:
                    output = str(data)
            else:
                output = json.dumps(data, indent=2)

            output_path = input_path.with_suffix(f'.{output_format}')
            output_path.write_text(output, encoding='utf-8')

            return {
                'input': input_file,
                'output': str(output_path),
                'format': output_format
            }

        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def system_info() -> Dict:
        """Get system information"""
        import platform
        return {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'machine': platform.machine()
        }


def main():
    parser = argparse.ArgumentParser(description='Superpowers Tools')
    subparsers = parser.add_subparsers(dest='command')

    api_parser = subparsers.add_parser('api-call')
    api_parser.add_argument('method')
    api_parser.add_argument('url')
    api_parser.add_argument('--headers')
    api_parser.add_argument('--data')

    file_parser = subparsers.add_parser('file-process')
    file_parser.add_argument('--action', required=True)
    file_parser.add_argument('--pattern', required=True)
    file_parser.add_argument('--path', required=True)

    transform_parser = subparsers.add_parser('transform')
    transform_parser.add_argument('--input', required=True)
    transform_parser.add_argument('--output-format', required=True)

    subparsers.add_parser('system-info')

    args = parser.parse_args()
    tools = Superpowers()

    if args.command == 'api-call':
        result = tools.api_call(args.method, args.url, args.headers, args.data)
        print(json.dumps(result, indent=2))

    elif args.command == 'file-process':
        result = tools.file_process(args.action, args.pattern, args.path)
        print(json.dumps(result, indent=2))

    elif args.command == 'transform':
        result = tools.transform(args.input, args.output_format)
        print(json.dumps(result, indent=2))

    elif args.command == 'system-info':
        result = tools.system_info()
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
