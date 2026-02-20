#!/usr/bin/env python3
"""Init Script Generator - Project initialization scripts"""

import argparse
import json
from datetime import datetime
from pathlib import Path


TEMPLATES = {
    'python': {
        'dirs': ['src', 'tests', 'docs'],
        'files': {
            'README.md': '# {name}\n\n{description}',
            'requirements.txt': '# Dependencies\n',
            'setup.py': '''from setuptools import setup, find_packages

setup(
    name="{name}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
)''',
            '.gitignore': '__pycache__/\n*.pyc\n.venv/\n.env',
            'pytest.ini': '[pytest]\ntestpaths = tests'
        }
    },
    'node': {
        'dirs': ['src', 'test'],
        'files': {
            'package.json': '''{{
  "name": "{name}",
  "version": "0.1.0",
  "main": "src/index.js",
  "scripts": {{
    "test": "jest",
    "lint": "eslint src/"
  }}
}}''',
            'README.md': '# {name}\n\n{description}',
            '.gitignore': 'node_modules/\ndist/\n.env'
        }
    }
}


def generate_project(project_type: str, name: str, features: List[str] = None):
    """Generate project structure"""
    template = TEMPLATES.get(project_type)
    if not template:
        print(f"Unknown project type: {project_type}")
        return
    
    project_dir = Path(name)
    project_dir.mkdir(exist_ok=True)
    
    # Create directories
    for dir_name in template['dirs']:
        (project_dir / dir_name).mkdir(exist_ok=True)
    
    # Create files
    description = f"A {project_type} project named {name}"
    for file_name, content in template['files'].items():
        file_path = project_dir / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content.format(name=name, description=description), encoding='utf-8')
    
    print(f"Generated {project_type} project: {name}")
    print(f"Features: {', '.join(features) if features else 'basic'}")


def generate_docker_config(base_image: str, output_dir: str):
    """Generate Dockerfile"""
    dockerfile = f"""FROM {base_image}

WORKDIR /app
COPY . .

# Install dependencies
# RUN pip install -r requirements.txt

CMD ["python", "main.py"]
"""
    
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'Dockerfile').write_text(dockerfile, encoding='utf-8')
    
    dockerignore = '''__pycache__/
*.pyc
.git/
.env
.venv/
'''
    (output / '.dockerignore').write_text(dockerignore, encoding='utf-8')
    
    print(f"Docker config generated: {output_dir}")


def generate_ci_config(project_type: str, output_dir: str):
    """Generate CI/CD configuration"""
    github_dir = Path(output_dir) / '.github' / 'workflows'
    github_dir.mkdir(parents=True, exist_ok=True)
    
    ci_yaml = f"""name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup {project_type}
      run: echo "Setup {project_type}"
    - name: Run tests
      run: echo "Running tests"
"""
    
    (github_dir / 'ci.yml').write_text(ci_yaml, encoding='utf-8')
    print(f"CI config generated: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description='Init Script Generator')
    subparsers = parser.add_subparsers(dest='command')
    
    python_parser = subparsers.add_parser('python')
    python_parser.add_argument('--name', required=True)
    python_parser.add_argument('--features', nargs='*')
    
    node_parser = subparsers.add_parser('node')
    node_parser.add_argument('--name', required=True)
    node_parser.add_argument('--type', default='javascript')
    
    docker_parser = subparsers.add_parser('docker')
    docker_parser.add_argument('--base', default='python:3.12-slim')
    docker_parser.add_argument('--output', default='.')
    
    ci_parser = subparsers.add_parser('ci')
    ci_parser.add_argument('--type', required=True)
    ci_parser.add_argument('--output', default='.')
    
    args = parser.parse_args()
    
    if args.command == 'python':
        generate_project('python', args.name, args.features)
    elif args.command == 'node':
        generate_project('node', args.name)
    elif args.command == 'docker':
        generate_docker_config(args.base, args.output)
    elif args.command == 'ci':
        generate_ci_config(args.type, args.output)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
