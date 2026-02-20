#!/usr/bin/env python3
"""
Initialize a new software project with standard structure.
Usage: init_project.py <project-name> [--type <type>]
"""

import os
import sys
import argparse
from datetime import datetime

PROJECT_TEMPLATES = {
    "web": {
        "dirs": ["src", "public", "docs", "tests", "scripts", ".github/workflows"],
        "files": {
            "README.md": "# {name}\n\n{description}\n\n## Getting Started\n\n### Prerequisites\n\n- Node.js 18+\n- npm or yarn\n\n### Installation\n\n```bash\nnpm install\n```\n\n### Development\n\n```bash\nnpm run dev\n```\n\n## Project Structure\n\n```\nsrc/          # Source code\npublic/       # Static assets\ntests/        # Test files\ndocs/         # Documentation\n```\n",
            "package.json": '{\n  "name": "{name}",\n  "version": "1.0.0",\n  "description": "{description}",\n  "main": "src/index.js",\n  "scripts": {\n    "dev": "echo \\"Start dev server\\"",\n    "build": "echo \\"Build project\\"",\n    "test": "echo \\"Run tests\\"",\n    "lint": "echo \\"Run linter\\""\n  },\n  "keywords": [],\n  "author": "",\n  "license": "MIT"\n}\n',
            ".gitignore": "# Dependencies\nnode_modules/\n\n# Build\ndist/\nbuild/\n\n# Environment\n.env\n.env.local\n\n# IDE\n.vscode/\n.idea/\n\n# OS\n.DS_Store\nThumbs.db\n"
        }
    },
    "api": {
        "dirs": ["src", "src/routes", "src/models", "src/middleware", "tests", "docs", "scripts"],
        "files": {
            "README.md": "# {name}\n\n{description}\n\n## API Endpoints\n\n### Base URL\n\n`http://localhost:3000/api/v1`\n\n### Authentication\n\nDescribe auth method here.\n\n## Getting Started\n\n```bash\nnpm install\nnpm run dev\n```\n",
            "package.json": '{\n  "name": "{name}",\n  "version": "1.0.0",\n  "description": "{description}",\n  "main": "src/index.js",\n  "scripts": {\n    "dev": "echo \\"Start dev server\\"",\n    "start": "echo \\"Start production server\\"",\n    "test": "echo \\"Run tests\\""\n  },\n  "keywords": ["api"],\n  "author": "",\n  "license": "MIT"\n}\n',
            "src/index.js": "const express = require('express');\nconst app = express();\n\napp.use(express.json());\n\n// Routes\napp.get('/', (req, res) => {\n  res.json({ message: 'Welcome to {name} API' });\n});\n\nconst PORT = process.env.PORT || 3000;\napp.listen(PORT, () => {\n  console.log(`Server running on port ${PORT}`);\n});\n",
            ".gitignore": "node_modules/\n.env\n.env.local\ndist/\n.vscode/\n.idea/\n.DS_Store\n"
        }
    },
    "python-package": {
        "dirs": ["src/{name}", "tests", "docs", "scripts"],
        "files": {
            "README.md": "# {name}\n\n{description}\n\n## Installation\n\n```bash\npip install {name}\n```\n\n## Usage\n\n```python\nimport {name}\n\n# Example usage\n```\n\n## Development\n\n```bash\npip install -e .\npytest\n```\n",
            "pyproject.toml": "[build-system]\nrequires = [\"setuptools>=45\", \"wheel\"]\nbuild-backend = \"setuptools.build_meta\"\n\n[project]\nname = \"{name}\"\nversion = \"1.0.0\"\ndescription = \"{description}\"\nreadme = \"README.md\"\nrequires-python = \">=3.8\"\nlicense = {{text = \"MIT\"}}\nauthors = [\n    {{name = \"Author\", email = \"author@example.com\"}}\n]\nkeywords = []\nclassifiers = [\n    \"Development Status :: 3 - Alpha\",\n    \"Intended Audience :: Developers\",\n    \"License :: OSI Approved :: MIT License\",\n    \"Programming Language :: Python :: 3\",\n]\ndependencies = []\n\n[project.optional-dependencies]\ndev = [\"pytest\", \"black\", \"flake8\"]\n",
            "src/{name}/__init__.py": "\"\"\"{name} - {description}\"\"\"\n\n__version__ = \"1.0.0\"\n",
            "tests/__init__.py": "",
            "tests/test_basic.py": "def test_example():\n    assert True\n",
            ".gitignore": "# Python\n__pycache__/\n*.py[cod]\n*$py.class\n*.so\n.Python\nbuild/\ndevelop-eggs/\ndist/\ndownloads/\neggs/\n.eggs/\nlib/\nlib64/\nparts/\nsdist/\nvar/\nwheels/\n*.egg-info/\n.installed.cfg\n*.egg\n\n# Virtual environments\nvenv/\nenv/\nENV/\n\n# IDE\n.vscode/\n.idea/\n\n# Testing\n.pytest_cache/\n.coverage\nhtmlcov/\n\n# OS\n.DS_Store\nThumbs.db\n"
        }
    },
    "cli": {
        "dirs": ["src", "tests", "docs"],
        "files": {
            "README.md": "# {name}\n\n{description}\n\n## Installation\n\n```bash\npip install -e .\n```\n\n## Usage\n\n```bash\n{name} --help\n```\n",
            "pyproject.toml": "[build-system]\nrequires = [\"setuptools>=45\", \"wheel\"]\nbuild-backend = \"setuptools.build_meta\"\n\n[project]\nname = \"{name}\"\nversion = \"1.0.0\"\ndescription = \"{description}\"\nreadme = \"README.md\"\nrequires-python = \">=3.8\"\nlicense = {{text = \"MIT\"}}\nauthors = [\n    {{name = \"Author\", email = \"author@example.com\"}}\n]\nkeywords = [\"cli\"]\nclassifiers = [\n    \"Environment :: Console\",\n    \"License :: OSI Approved :: MIT License\",\n]\ndependencies = [\"click\"]\n\n[project.scripts]\n{name} = \"src.main:main\"\n",
            "src/main.py": "import click\n\n@click.command()\n@click.option('--verbose', '-v', is_flag=True, help='Verbose output')\ndef main(verbose):\n    \"\"\"{name} CLI\"\"\"\n    if verbose:\n        click.echo(\"Verbose mode enabled\")\n    click.echo(\"Hello from {name}!\")\n\nif __name__ == '__main__':\n    main()\n",
            ".gitignore": "__pycache__/\n*.py[cod]\n*.egg-info/\ndist/\nbuild/\nvenv/\n.env\n.vscode/\n.idea/\n.DS_Store\n"
        }
    },
    "node-package": {
        "dirs": ["lib", "tests", "docs", "examples"],
        "files": {
            "README.md": "# {name}\n\n{description}\n\n## Installation\n\n```bash\nnpm install {name}\n```\n\n## Usage\n\n```javascript\nconst {name} = require('{name}');\n\n// Example usage\n```\n",
            "package.json": '{\n  "name": "{name}",\n  "version": "1.0.0",\n  "description": "{description}",\n  "main": "lib/index.js",\n  "scripts": {\n    "test": "jest",\n    "lint": "eslint lib/ tests/"\n  },\n  "keywords": [],\n  "author": "",\n  "license": "MIT",\n  "devDependencies": {\n    "jest": "^29.0.0",\n    "eslint": "^8.0.0"\n  }\n}\n',
            "lib/index.js": "/**\n * {name}\n * {description}\n */\n\nfunction main() {\n  console.log('Hello from {name}!');\n}\n\nmodule.exports = {\n  main\n};\n",
            "tests/index.test.js": "const { main } = require('../lib/index');\n\ndescribe('{name}', () => {\n  test('should run without error', () => {\n    expect(() => main()).not.toThrow();\n  });\n});\n",
            ".gitignore": "node_modules/\n*.log\n.DS_Store\n.vscode/\n.idea/\ncoverage/\n.nyc_output/\n"
        }
    }
}


def create_project(name, project_type, base_path=None):
    """Create a new project with the specified type."""
    if base_path is None:
        base_path = os.getcwd()
    
    project_path = os.path.join(base_path, name)
    
    if os.path.exists(project_path):
        print(f"Error: Directory '{name}' already exists!")
        return False
    
    template = PROJECT_TEMPLATES.get(project_type)
    if not template:
        print(f"Error: Unknown project type '{project_type}'")
        print(f"Available types: {', '.join(PROJECT_TEMPLATES.keys())}")
        return False
    
    # Create directories
    for dir_path in template["dirs"]:
        dir_path = dir_path.format(name=name)
        full_path = os.path.join(project_path, dir_path)
        os.makedirs(full_path, exist_ok=True)
        print(f"  Created: {dir_path}/")
    
    # Create files
    description = f"A {project_type} project"
    for file_name, content in template["files"].items():
        file_name = file_name.format(name=name)
        full_path = os.path.join(project_path, file_name)
        content = content.format(name=name, description=description)
        
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Created: {file_name}")
    
    print(f"\n✅ Project '{name}' created successfully!")
    print(f"   Location: {project_path}")
    print(f"   Type: {project_type}")
    print(f"\nNext steps:")
    print(f"  cd {name}")
    if project_type in ["web", "api", "node-package"]:
        print(f"  npm install")
    elif project_type in ["python-package", "cli"]:
        print(f"  pip install -e .")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Initialize a new project')
    parser.add_argument('name', help='Project name')
    parser.add_argument('--type', '-t', default='web',
                       choices=list(PROJECT_TEMPLATES.keys()),
                       help='Project type')
    parser.add_argument('--path', '-p', default=None,
                       help='Base path for project (default: current directory)')
    
    args = parser.parse_args()
    
    create_project(args.name, args.type, args.path)


if __name__ == '__main__':
    main()
