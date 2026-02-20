# Matplotlib Skill

Matplotlib data visualization skill for chart generation, style customization, and export saving. Use when analyzing data, creating visualizations, or when user mentions 'matplotlib', 'plot', 'chart', 'visualization', 'graph'.

## Features

- **Basic Charts**: Line, Bar, Scatter, Pie, Histogram
- **Statistical Charts**: Boxplot, Violin, Heatmap
- **Advanced Charts**: 3D plots, Subplots, Twin axes
- **Style Customization**: Colors, Themes, Annotations
- **Export Formats**: PNG, PDF, SVG, JPG

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Line Plot
```python
from main import MatplotlibSkill

skill = MatplotlibSkill()
skill.line_plot(x=[1, 2, 3, 4], y=[1, 4, 9, 16])
skill.save_figure("plot.png")
```

### Bar Chart
```python
skill.bar_chart(categories=['A', 'B', 'C'], values=[10, 20, 15])
```

### Custom Styling
```python
skill.set_style('seaborn')
skill.set_color_palette('viridis')
```

## API Reference

See `main.py` for complete API documentation.

## Testing

```bash
python test_skill.py
```

## License

MIT License
