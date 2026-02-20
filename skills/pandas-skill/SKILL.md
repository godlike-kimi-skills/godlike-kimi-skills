# Pandas Skill

Pandas data analysis skill for data cleaning, transformation, and statistical analysis. Use when analyzing data, creating visualizations, or when user mentions 'pandas', 'data analysis', 'data cleaning', 'dataframe'.

## Features

- **Data Loading**: Load data from CSV, Excel, JSON, SQL
- **Data Cleaning**: Handle missing values, duplicates, outliers
- **Data Transformation**: Filter, sort, group, merge, pivot
- **Statistical Analysis**: Descriptive stats, correlations, aggregations
- **Data Export**: Save to multiple formats

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Data Loading
```python
from main import PandasSkill

skill = PandasSkill()
df = skill.load_csv("data.csv")
```

### Data Cleaning
```python
# Remove duplicates
df_clean = skill.remove_duplicates(df)

# Handle missing values
df_filled = skill.fill_missing(df, strategy='mean')
```

### Statistical Analysis
```python
stats = skill.describe(df)
correlation = skill.correlation(df)
```

## API Reference

See `main.py` for complete API documentation.

## Testing

```bash
python test_skill.py
```

## License

MIT License
