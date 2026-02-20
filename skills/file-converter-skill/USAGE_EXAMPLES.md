# File Converter Skill - Usage Examples

## Example 1: Data Migration Pipeline

Convert data between multiple formats for system migration:

```python
from skills.file_converter_skill.main import FileConverterSkill
import os

skill = FileConverterSkill()

# Migration from legacy CSV system to modern JSON API
legacy_files = ["users.csv", "orders.csv", "products.csv"]

for csv_file in legacy_files:
    if os.path.exists(csv_file):
        base_name = csv_file.replace(".csv", "")
        
        # Step 1: CSV to JSON
        json_file = f"{base_name}.json"
        skill.convert_csv_to_json(csv_file, json_file)
        print(f"✓ Converted {csv_file} to {json_file}")
        
        # Step 2: Validate JSON
        if skill.validate_json(json_file):
            print(f"✓ {json_file} is valid JSON")
        
        # Step 3: Create Excel backup
        excel_file = f"{base_name}_backup.xlsx"
        skill.convert_csv_to_excel(csv_file, excel_file)
        print(f"✓ Created backup: {excel_file}")

print("\nMigration complete!")
```

## Example 2: Multi-Encoding Data Processing

Handle files with different character encodings:

```python
skill = FileConverterSkill()

# Process international data files
international_files = [
    ("china_data.csv", "gbk"),
    ("japan_data.csv", "shift_jis"),
    ("germany_data.csv", "latin-1"),
    ("russia_data.csv", "cp1251"),
]

for filename, source_encoding in international_files:
    if os.path.exists(filename):
        # Convert to UTF-8 JSON (universal format)
        output_name = filename.replace(".csv", "_utf8.json")
        
        skill.convert_csv_to_json(
            filename, 
            output_name,
            encoding=source_encoding
        )
        
        print(f"✓ Converted {filename} ({source_encoding}) → {output_name} (UTF-8)")
```

## Example 3: Excel Report Generator

Convert various data sources to Excel reports:

```python
skill = FileConverterSkill()

# Combine multiple JSON data sources into Excel workbook
import pandas as pd

# Create individual sheets from different sources
data_sources = {
    "Users": "users.json",
    "Sales": "sales_data.json",
    "Inventory": "inventory.json",
}

# Convert each JSON to individual CSV first
csv_files = []
for sheet_name, json_file in data_sources.items():
    if os.path.exists(json_file):
        csv_file = json_file.replace(".json", ".csv")
        skill.convert_json_to_csv(json_file, csv_file)
        csv_files.append((sheet_name, csv_file))

# Now combine into single Excel with multiple sheets
with pd.ExcelWriter('consolidated_report.xlsx', engine='openpyxl') as writer:
    for sheet_name, csv_file in csv_files:
        df = pd.read_csv(csv_file)
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print("✓ Created consolidated_report.xlsx with multiple sheets")
```

## Example 4: XML Configuration Migration

Convert legacy XML configurations to modern JSON:

```python
skill = FileConverterSkill()

# Sample XML structure:
# <config>
#   <database>
#     <host>localhost</host>
#     <port>5432</port>
#   </database>
# </config>

xml_files = ["database.xml", "app_config.xml", "logging.xml"]

for xml_file in xml_files:
    if os.path.exists(xml_file):
        json_file = xml_file.replace(".xml", ".json")
        
        try:
            skill.convert_xml_to_json(xml_file, json_file)
            print(f"✓ Converted {xml_file} → {json_file}")
            
            # Verify JSON is valid
            if skill.validate_json(json_file):
                print(f"  ✓ {json_file} validated successfully")
        except Exception as e:
            print(f"✗ Error converting {xml_file}: {e}")
```

## Example 5: Batch Processing Directory

Convert all files in a directory:

```python
skill = FileConverterSkill()

# Batch convert all CSV files to JSON
converted = skill.batch_convert(
    input_dir="./raw_csv_data/",
    output_dir="./processed_json/",
    from_format="csv",
    to_format="json"
)

print(f"Converted {len(converted)} files:")
for f in converted:
    print(f"  ✓ {f}")

# Another batch: Excel to CSV
converted = skill.batch_convert(
    input_dir="./excel_reports/",
    output_dir="./csv_exports/",
    from_format="xlsx",
    to_format="csv",
    encoding="utf-8"
)

print(f"\nConverted {len(converted)} Excel files to CSV")
```

## Example 6: Data Validation Pipeline

Validate data integrity during conversion:

```python
skill = FileConverterSkill()

def validate_and_convert(input_file, output_format):
    """Validate input and convert to output format"""
    
    # Step 1: Validate input
    ext = input_file.split('.')[-1].lower()
    
    if ext == 'json':
        if not skill.validate_json(input_file):
            print(f"✗ {input_file} is invalid JSON")
            return False
    elif ext == 'xml':
        if not skill.validate_xml(input_file):
            print(f"✗ {input_file} is invalid XML")
            return False
    
    print(f"✓ {input_file} validated")
    
    # Step 2: Convert
    output_file = input_file.rsplit('.', 1)[0] + f'.{output_format}'
    
    if ext == 'csv' and output_format == 'json':
        skill.convert_csv_to_json(input_file, output_file)
    elif ext == 'json' and output_format == 'csv':
        skill.convert_json_to_csv(input_file, output_file)
    # ... other conversions
    
    print(f"✓ Converted to {output_file}")
    return True

# Process files
files_to_process = ["data1.json", "data2.csv", "config.xml"]
for file in files_to_process:
    if os.path.exists(file):
        validate_and_convert(file, "json")
```

## Example 7: CSV File Merger

Merge multiple CSV files into one:

```python
skill = FileConverterSkill()

# Monthly sales data files
monthly_files = [
    "sales_jan.csv",
    "sales_feb.csv",
    "sales_mar.csv",
]

# Filter existing files
existing_files = [f for f in monthly_files if os.path.exists(f)]

if existing_files:
    skill.merge_csv_files(existing_files, "sales_q1_combined.csv")
    print(f"✓ Merged {len(existing_files)} files into sales_q1_combined.csv")
    
    # Convert merged file to Excel for reporting
    skill.convert_csv_to_excel("sales_q1_combined.csv", "sales_q1_report.xlsx")
    print("✓ Created Excel report: sales_q1_report.xlsx")
```

## Example 8: Encoding Detection and Fix

Auto-detect and fix encoding issues:

```python
skill = FileConverterSkill()

# Files with unknown encoding
mystery_files = ["legacy_export.txt", "old_data.csv", "backup.dat"]

for file in mystery_files:
    if os.path.exists(file):
        # Detect encoding
        detected = skill._detect_encoding(file)
        print(f"{file}: detected encoding = {detected}")
        
        # Convert to UTF-8
        output = file.replace('.', '_utf8.')
        skill.convert_encoding(file, output, to_encoding='utf-8')
        print(f"  ✓ Converted to UTF-8: {output}")
```
