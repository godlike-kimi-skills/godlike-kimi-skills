# Jupyter Skill

Jupyter Notebook management skill for notebook creation, execution, and conversion. Use when analyzing data, creating visualizations, or when user mentions 'jupyter', 'notebook', 'ipynb', 'jupyter lab'.

## Features

- **Notebook Creation**: Create new notebooks programmatically
- **Cell Management**: Add, edit, delete cells
- **Notebook Execution**: Run notebooks and capture outputs
- **Format Conversion**: Convert to HTML, PDF, Python, Markdown
- **Notebook Analysis**: Extract code, count cells, get metadata

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Create New Notebook
```python
from main import JupyterSkill

skill = JupyterSkill()
notebook = skill.create_notebook()
skill.add_code_cell(notebook, "print('Hello World')")
skill.save_notebook(notebook, "hello.ipynb")
```

### Execute Notebook
```python
result = skill.execute_notebook("hello.ipynb", output_path="output.ipynb")
```

### Convert Notebook
```python
skill.convert_notebook("notebook.ipynb", "html", output="output.html")
```

## API Reference

See `main.py` for complete API documentation.

## Testing

```bash
python test_skill.py
```

## License

MIT License
