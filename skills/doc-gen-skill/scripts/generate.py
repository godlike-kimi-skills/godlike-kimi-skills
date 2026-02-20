#!/usr/bin/env python3
"""Doc Gen Skill - Documentation generator"""

import argparse
import json
from datetime import datetime
from pathlib import Path


def generate_api_docs(source_dir: str, output_dir: str):
    """Generate API documentation from source code"""
    source = Path(source_dir)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    
    # Simulated API documentation
    api_docs = {
        'project': 'Sample Project',
        'generated_at': datetime.now().isoformat(),
        'endpoints': [
            {'path': '/api/v1/users', 'method': 'GET', 'description': 'List users'},
            {'path': '/api/v1/users', 'method': 'POST', 'description': 'Create user'},
        ]
    }
    
    (output / 'api.json').write_text(json.dumps(api_docs, indent=2), encoding='utf-8')
    (output / 'index.md').write_text(f"""# API Documentation

Generated: {datetime.now().isoformat()}

## Endpoints

- `GET /api/v1/users` - List users
- `POST /api/v1/users` - Create user
""", encoding='utf-8')
    
    print(f"API docs generated: {output_dir}")


def generate_project_docs(template: str, project_name: str):
    """Generate project documentation"""
    docs_dir = Path(f"{project_name}-docs")
    docs_dir.mkdir(exist_ok=True)
    
    if template == 'mkdocs':
        (docs_dir / 'mkdocs.yml').write_text(f"""site_name: {project_name}
theme: material
nav:
  - Home: index.md
  - Getting Started: getting-started.md
""")
        (docs_dir / 'docs' / 'index.md').write_text(f"# {project_name}\n\nWelcome to {project_name} documentation.", encoding='utf-8')
    
    print(f"Project docs generated: {docs_dir}")


def export_pdf(input_dir: str, output_file: str):
    """Export documentation to PDF"""
    input_path = Path(input_dir)
    
    # Simulated PDF export
    print(f"Exporting documentation from {input_dir} to PDF...")
    print(f"Output: {output_file}")
    print("Note: Requires pandoc and LaTeX for actual PDF generation")


def main():
    parser = argparse.ArgumentParser(description='Doc Gen Skill')
    subparsers = parser.add_subparsers(dest='command')
    
    api_parser = subparsers.add_parser('api')
    api_parser.add_argument('--source', required=True)
    api_parser.add_argument('--output', required=True)
    
    project_parser = subparsers.add_parser('project')
    project_parser.add_argument('--template', default='mkdocs')
    project_parser.add_argument('--name', required=True)
    
    export_parser = subparsers.add_parser('export')
    export_parser.add_argument('--input', required=True)
    export_parser.add_argument('--format', choices=['pdf', 'html'], required=True)
    export_parser.add_argument('--output', required=True)
    
    args = parser.parse_args()
    
    if args.command == 'api':
        generate_api_docs(args.source, args.output)
    elif args.command == 'project':
        generate_project_docs(args.template, args.name)
    elif args.command == 'export':
        export_pdf(args.input, args.output)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
