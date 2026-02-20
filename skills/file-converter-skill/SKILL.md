# File Converter Skill

**Category:** Utility  
**Version:** 1.0.0  
**Author:** godlike-kimi-skills

---

## Use When

- Converting data between CSV, JSON, XML, and Excel formats
- Changing text file encodings (UTF-8, GBK, Latin-1, etc.)
- Migrating data between different systems with incompatible formats
- Processing batch file conversions
- Validating JSON or XML file syntax
- Merging multiple CSV files into one
- Auto-detecting file encodings

---

## Out of Scope

- PDF generation or conversion
- Image format conversion (PNG, JPG, etc.)
- Audio/video format conversion
- Archive compression/decompression (ZIP, RAR)
- Document format conversion (DOC, DOCX, ODT)
- Database schema conversion
- Data transformation/filtering during conversion (use pandas for this)
- PDF text extraction
- OCR (Optical Character Recognition)

---

## Quick Reference

### Core Methods

```python
from skills.file_converter_skill.main import FileConverterSkill

skill = FileConverterSkill()

# CSV <-> JSON
skill.convert_csv_to_json("data.csv", "output.json")
skill.convert_json_to_csv("data.json", "output.csv")

# CSV <-> Excel
skill.convert_csv_to_excel("data.csv", "output.xlsx")
skill.convert_excel_to_csv("data.xlsx", "output.csv")

# JSON <-> XML
skill.convert_json_to_xml("data.json", "output.xml")
skill.convert_xml_to_json("data.xml", "output.json")

# Excel <-> JSON
skill.convert_excel_to_json("data.xlsx", "output.json")
skill.convert_json_to_excel("data.json", "output.xlsx")

# Encoding conversion
skill.convert_encoding("input.txt", "output.txt", from_encoding="GBK", to_encoding="UTF-8")

# Batch conversion
skill.batch_convert("input/", "output/", "csv", "json")

# Validation
is_valid = skill.validate_json("data.json")
is_valid = skill.validate_xml("data.xml")
```

---

## Conversion Matrix

| From \ To | CSV | JSON | XML | Excel |
|-----------|-----|------|-----|-------|
| **CSV** | - | ✅ | ❌ | ✅ |
| **JSON** | ✅ | - | ✅ | ✅ |
| **XML** | ❌ | ✅ | - | ❌ |
| **Excel** | ✅ | ✅ | ❌ | - |

---

## Supported Encodings

- `utf-8` (recommended)
- `utf-16`, `utf-32`
- `ascii`
- `latin-1`, `iso-8859-1`, `windows-1252`
- `gbk`, `gb2312` (Chinese)
- `big5` (Traditional Chinese)
- `shift_jis`, `euc-jp` (Japanese)

Encoding is auto-detected when not specified.

---

## CLI Usage

```bash
# CSV to JSON
python main.py csv2json input.csv output.json

# JSON to CSV
python main.py json2csv input.json output.csv

# CSV to Excel
python main.py csv2xlsx input.csv output.xlsx

# Excel to CSV
python main.py xlsx2csv input.xlsx output.csv

# JSON to XML
python main.py json2xml input.json output.xml

# XML to JSON
python main.py xml2json input.xml output.json

# Encoding conversion
python main.py encode input.txt output.txt utf-8
```

---

## Method Reference

### CSV Conversions

- `convert_csv_to_json(csv_path, json_path, encoding=None, indent=2)` - CSV to JSON
- `convert_csv_to_excel(csv_path, excel_path, encoding=None, sheet_name='Sheet1')` - CSV to Excel

### JSON Conversions

- `convert_json_to_csv(json_path, csv_path, encoding='utf-8')` - JSON to CSV
- `convert_json_to_excel(json_path, excel_path, sheet_name='Sheet1')` - JSON to Excel
- `convert_json_to_xml(json_path, xml_path, root_name='root', item_name='item')` - JSON to XML

### Excel Conversions

- `convert_excel_to_csv(excel_path, csv_path, sheet_name=None, encoding='utf-8')` - Excel to CSV
- `convert_excel_to_json(excel_path, json_path, sheet_name=None, indent=2)` - Excel to JSON

### XML Conversions

- `convert_xml_to_json(xml_path, json_path, indent=2)` - XML to JSON

### Utility Methods

- `convert_encoding(input_path, output_path, from_encoding=None, to_encoding='utf-8')` - Change encoding
- `batch_convert(input_dir, output_dir, from_format, to_format, **kwargs)` - Batch processing
- `validate_json(json_path)` - Validate JSON syntax
- `validate_xml(xml_path)` - Validate XML syntax
- `merge_csv_files(csv_paths, output_path)` - Merge multiple CSVs

---

## Dependencies

```
pandas>=2.0.0
openpyxl>=3.1.0
xmltodict>=0.13.0
chardet>=5.0.0
```

---

## Examples

### Data Migration Pipeline

```python
skill = FileConverterSkill()

# Convert legacy CSV to modern JSON
skill.convert_csv_to_json("legacy_data.csv", "modern_data.json")

# Convert to Excel for business users
skill.convert_json_to_excel("modern_data.json", "report.xlsx")

# Validate output
if skill.validate_json("modern_data.json"):
    print("Migration successful!")
```

### Multi-Encoding Data Processing

```python
skill = FileConverterSkill()

# Process files with different encodings
files = [
    ("chinese_data.csv", "gbk"),
    ("japanese_data.csv", "shift_jis"),
    ("european_data.csv", "latin-1"),
]

for filename, encoding in files:
    # Convert all to UTF-8 JSON
    skill.convert_csv_to_json(
        filename, 
        filename.replace(".csv", ".json"),
        encoding=encoding
    )
```

### Batch Processing

```python
skill = FileConverterSkill()

# Convert all CSV files in directory to JSON
converted = skill.batch_convert(
    input_dir="./raw_data/",
    output_dir="./processed/",
    from_format="csv",
    to_format="json"
)

print(f"Converted {len(converted)} files")
```
