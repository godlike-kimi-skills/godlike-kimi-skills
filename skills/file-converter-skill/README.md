# File Converter Skill

A powerful file format conversion utility for Kimi CLI that supports CSV, JSON, XML, Excel, and encoding conversions.

## Features

- 📊 **Data Format Conversion**: CSV ⟷ JSON ⟷ XML ⟷ Excel
- 🔤 **Encoding Conversion**: UTF-8, GBK, Latin-1, and more
- 📁 **Batch Processing**: Convert multiple files at once
- 🎯 **Schema Validation**: Validate data during conversion
- 💾 **Memory Efficient**: Stream processing for large files

## Installation

```bash
# Copy skill to Kimi skills directory
cp -r file-converter-skill ~/.kimi/skills/

# Install dependencies
pip install -r ~/.kimi/skills/file-converter-skill/requirements.txt
```

## Quick Start

```python
from skills.file_converter_skill.main import FileConverterSkill

skill = FileConverterSkill()

# CSV to JSON
skill.convert_csv_to_json("data.csv", "data.json")

# JSON to Excel
skill.convert_json_to_excel("data.json", "data.xlsx")

# Encoding conversion
skill.convert_encoding("file.txt", "UTF-8", "GBK", "output.txt")

# Batch conversion
skill.batch_convert("input/", "output/", "csv", "json")
```

## Documentation

- [SKILL.md](./SKILL.md) - Detailed usage guide
- [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md) - Example use cases

## License

MIT License
