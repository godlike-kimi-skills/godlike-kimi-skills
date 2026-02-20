# NumPy Skill

NumPy numerical computing skill for array operations, mathematical operations, and random number generation. Use when analyzing data, creating visualizations, or when user mentions 'numpy', 'array operations', 'numerical computing', 'linear algebra'.

## Features

- **Array Creation**: Create arrays from lists, ranges, random values
- **Array Operations**: Reshape, slice, index, concatenate
- **Mathematical Operations**: Element-wise and matrix operations
- **Linear Algebra**: Matrix multiplication, decomposition, eigenvalues
- **Random Number Generation**: Various distributions

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Array Creation
```python
from main import NumpySkill

skill = NumpySkill()
arr = skill.create_array([1, 2, 3, 4, 5])
```

### Array Operations
```python
# Reshape
arr_2d = skill.reshape(arr, (2, 2))

# Mathematical operations
result = skill.add(arr, 10)
```

### Linear Algebra
```python
# Matrix multiplication
result = skill.matrix_multiply(matrix_a, matrix_b)

# Eigenvalues
eigenvalues = skill.eigenvalues(matrix)
```

## API Reference

See `main.py` for complete API documentation.

## Testing

```bash
python test_skill.py
```

## License

MIT License
