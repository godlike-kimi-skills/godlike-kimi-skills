#!/usr/bin/env python3
"""
File Converter Skill - File format conversion utility
Supports CSV/JSON/XML/Excel conversion and encoding transformation
"""

import json
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import Union, List, Dict, Optional, Any
import pandas as pd
import chardet


class FileConverterSkill:
    """
    A comprehensive file format converter supporting:
    - CSV, JSON, XML, Excel interconversion
    - Text encoding conversion
    - Batch file processing
    - Schema validation
    """
    
    def __init__(self):
        """Initialize the FileConverterSkill"""
        self._supported_encodings = [
            'utf-8', 'utf-16', 'utf-32', 'ascii',
            'latin-1', 'iso-8859-1', 'windows-1252',
            'gbk', 'gb2312', 'big5', 'shift_jis', 'euc-jp'
        ]
    
    def _detect_encoding(self, file_path: str) -> str:
        """
        Detect file encoding
        
        Args:
            file_path: Path to file
            
        Returns:
            Detected encoding
        """
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)
            result = chardet.detect(raw_data)
            return result.get('encoding', 'utf-8') or 'utf-8'
    
    def convert_csv_to_json(
        self, 
        csv_path: str, 
        json_path: str,
        encoding: Optional[str] = None,
        indent: int = 2
    ) -> str:
        """
        Convert CSV file to JSON
        
        Args:
            csv_path: Path to input CSV file
            json_path: Path to output JSON file
            encoding: File encoding (auto-detected if None)
            indent: JSON indentation level
            
        Returns:
            Path to output file
        """
        enc = encoding or self._detect_encoding(csv_path)
        
        data = []
        with open(csv_path, 'r', encoding=enc, errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(dict(row))
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        return json_path
    
    def convert_json_to_csv(
        self, 
        json_path: str, 
        csv_path: str,
        encoding: str = 'utf-8'
    ) -> str:
        """
        Convert JSON file to CSV
        
        Args:
            json_path: Path to input JSON file
            csv_path: Path to output CSV file
            encoding: Output file encoding
            
        Returns:
            Path to output file
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("JSON must contain an array of objects")
        
        if len(data) == 0:
            raise ValueError("JSON array is empty")
        
        fieldnames = list(data[0].keys())
        
        with open(csv_path, 'w', encoding=encoding, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        return csv_path
    
    def convert_csv_to_excel(
        self, 
        csv_path: str, 
        excel_path: str,
        encoding: Optional[str] = None,
        sheet_name: str = 'Sheet1'
    ) -> str:
        """
        Convert CSV file to Excel
        
        Args:
            csv_path: Path to input CSV file
            excel_path: Path to output Excel file
            encoding: File encoding (auto-detected if None)
            sheet_name: Name of the Excel sheet
            
        Returns:
            Path to output file
        """
        enc = encoding or self._detect_encoding(csv_path)
        df = pd.read_csv(csv_path, encoding=enc)
        df.to_excel(excel_path, sheet_name=sheet_name, index=False)
        return excel_path
    
    def convert_excel_to_csv(
        self, 
        excel_path: str, 
        csv_path: str,
        sheet_name: Optional[str] = None,
        encoding: str = 'utf-8'
    ) -> str:
        """
        Convert Excel file to CSV
        
        Args:
            excel_path: Path to input Excel file
            csv_path: Path to output CSV file
            sheet_name: Sheet to convert (first sheet if None)
            encoding: Output file encoding
            
        Returns:
            Path to output file
        """
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        df.to_csv(csv_path, index=False, encoding=encoding)
        return csv_path
    
    def convert_json_to_excel(
        self, 
        json_path: str, 
        excel_path: str,
        sheet_name: str = 'Sheet1'
    ) -> str:
        """
        Convert JSON file to Excel
        
        Args:
            json_path: Path to input JSON file
            excel_path: Path to output Excel file
            sheet_name: Name of the Excel sheet
            
        Returns:
            Path to output file
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        df.to_excel(excel_path, sheet_name=sheet_name, index=False)
        return excel_path
    
    def convert_excel_to_json(
        self, 
        excel_path: str, 
        json_path: str,
        sheet_name: Optional[str] = None,
        indent: int = 2
    ) -> str:
        """
        Convert Excel file to JSON
        
        Args:
            excel_path: Path to input Excel file
            json_path: Path to output JSON file
            sheet_name: Sheet to convert (first sheet if None)
            indent: JSON indentation level
            
        Returns:
            Path to output file
        """
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        data = df.to_dict(orient='records')
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        return json_path
    
    def _dict_to_xml(self, data: Dict, parent: ET.Element) -> None:
        """Helper: Convert dict to XML elements"""
        for key, value in data.items():
            child = ET.SubElement(parent, str(key))
            if isinstance(value, dict):
                self._dict_to_xml(value, child)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        item_elem = ET.SubElement(child, 'item')
                        self._dict_to_xml(item, item_elem)
                    else:
                        item_elem = ET.SubElement(child, 'item')
                        item_elem.text = str(item)
            else:
                child.text = str(value) if value is not None else ''
    
    def convert_json_to_xml(
        self, 
        json_path: str, 
        xml_path: str,
        root_name: str = 'root',
        item_name: str = 'item'
    ) -> str:
        """
        Convert JSON file to XML
        
        Args:
            json_path: Path to input JSON file
            xml_path: Path to output XML file
            root_name: Name of root element
            item_name: Name for array items
            
        Returns:
            Path to output file
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        root = ET.Element(root_name)
        
        if isinstance(data, list):
            for item in data:
                item_elem = ET.SubElement(root, item_name)
                if isinstance(item, dict):
                    self._dict_to_xml(item, item_elem)
                else:
                    item_elem.text = str(item)
        elif isinstance(data, dict):
            self._dict_to_xml(data, root)
        else:
            root.text = str(data)
        
        # Pretty print XML
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent='  ')
        
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        return xml_path
    
    def convert_xml_to_json(
        self, 
        xml_path: str, 
        json_path: str,
        indent: int = 2
    ) -> str:
        """
        Convert XML file to JSON
        
        Args:
            xml_path: Path to input XML file
            json_path: Path to output JSON file
            indent: JSON indentation level
            
        Returns:
            Path to output file
        """
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        def element_to_dict(element: ET.Element) -> Union[Dict, str]:
            result = {}
            
            # Add attributes
            for key, value in element.attrib.items():
                result[f'@{key}'] = value
            
            # Add children
            children = list(element)
            if children:
                for child in children:
                    child_data = element_to_dict(child)
                    if child.tag in result:
                        if not isinstance(result[child.tag], list):
                            result[child.tag] = [result[child.tag]]
                        result[child.tag].append(child_data)
                    else:
                        result[child.tag] = child_data
            
            # Add text content
            text = element.text.strip() if element.text else ''
            if text:
                if result:
                    result['#text'] = text
                else:
                    return text
            
            return result if result else ''
        
        data = element_to_dict(root)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        return json_path
    
    def convert_encoding(
        self, 
        input_path: str, 
        output_path: str,
        from_encoding: Optional[str] = None,
        to_encoding: str = 'utf-8',
        errors: str = 'replace'
    ) -> str:
        """
        Convert file encoding
        
        Args:
            input_path: Path to input file
            output_path: Path to output file
            from_encoding: Source encoding (auto-detected if None)
            to_encoding: Target encoding
            errors: Error handling strategy
            
        Returns:
            Path to output file
        """
        source_enc = from_encoding or self._detect_encoding(input_path)
        
        with open(input_path, 'r', encoding=source_enc, errors=errors) as f:
            content = f.read()
        
        with open(output_path, 'w', encoding=to_encoding, errors=errors) as f:
            f.write(content)
        
        return output_path
    
    def batch_convert(
        self, 
        input_dir: str, 
        output_dir: str,
        from_format: str,
        to_format: str,
        **kwargs
    ) -> List[str]:
        """
        Batch convert files in a directory
        
        Args:
            input_dir: Input directory path
            output_dir: Output directory path
            from_format: Source format (csv, json, xml, xlsx)
            to_format: Target format (csv, json, xml, xlsx)
            **kwargs: Additional arguments for conversion
            
        Returns:
            List of output file paths
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Map extensions
        ext_map = {
            'csv': '.csv', 'json': '.json', 
            'xml': '.xml', 'xlsx': '.xlsx', 'excel': '.xlsx'
        }
        
        input_ext = ext_map.get(from_format.lower(), f'.{from_format}')
        output_ext = ext_map.get(to_format.lower(), f'.{to_format}')
        
        converted_files = []
        
        for input_file in input_path.glob(f'*{input_ext}'):
            output_file = output_path / input_file.with_suffix(output_ext).name
            
            # Route to appropriate converter
            converter_map = {
                ('csv', 'json'): self.convert_csv_to_json,
                ('csv', 'xlsx'): self.convert_csv_to_excel,
                ('json', 'csv'): self.convert_json_to_csv,
                ('json', 'xlsx'): self.convert_json_to_excel,
                ('json', 'xml'): self.convert_json_to_xml,
                ('xlsx', 'csv'): self.convert_excel_to_csv,
                ('xlsx', 'json'): self.convert_excel_to_json,
                ('excel', 'csv'): self.convert_excel_to_csv,
                ('excel', 'json'): self.convert_excel_to_json,
                ('xml', 'json'): self.convert_xml_to_json,
            }
            
            converter = converter_map.get((from_format.lower(), to_format.lower()))
            if converter:
                converter(str(input_file), str(output_file), **kwargs)
                converted_files.append(str(output_file))
        
        return converted_files
    
    def validate_json(self, json_path: str) -> bool:
        """
        Validate JSON file syntax
        
        Args:
            json_path: Path to JSON file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, IOError):
            return False
    
    def validate_xml(self, xml_path: str) -> bool:
        """
        Validate XML file syntax
        
        Args:
            xml_path: Path to XML file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            ET.parse(xml_path)
            return True
        except ET.ParseError:
            return False
    
    def merge_csv_files(
        self, 
        csv_paths: List[str], 
        output_path: str,
        encoding: str = 'utf-8'
    ) -> str:
        """
        Merge multiple CSV files
        
        Args:
            csv_paths: List of CSV file paths
            output_path: Output merged file path
            encoding: File encoding
            
        Returns:
            Path to output file
        """
        if not csv_paths:
            raise ValueError("No input files provided")
        
        # Read first file to get headers
        first_enc = self._detect_encoding(csv_paths[0])
        with open(csv_paths[0], 'r', encoding=first_enc) as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            all_rows = list(reader)
        
        # Read remaining files
        for csv_path in csv_paths[1:]:
            enc = self._detect_encoding(csv_path)
            with open(csv_path, 'r', encoding=enc) as f:
                reader = csv.DictReader(f)
                all_rows.extend(reader)
        
        # Write merged file
        with open(output_path, 'w', encoding=encoding, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)
        
        return output_path


# CLI interface
if __name__ == '__main__':
    import sys
    
    skill = FileConverterSkill()
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <command> [args...]")
        print("Commands: csv2json, json2csv, csv2xlsx, xlsx2csv, json2xml, xml2json, encode")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == 'csv2json' and len(sys.argv) >= 4:
            result = skill.convert_csv_to_json(sys.argv[2], sys.argv[3])
            print(f"Converted: {result}")
        elif command == 'json2csv' and len(sys.argv) >= 4:
            result = skill.convert_json_to_csv(sys.argv[2], sys.argv[3])
            print(f"Converted: {result}")
        elif command == 'csv2xlsx' and len(sys.argv) >= 4:
            result = skill.convert_csv_to_excel(sys.argv[2], sys.argv[3])
            print(f"Converted: {result}")
        elif command == 'xlsx2csv' and len(sys.argv) >= 4:
            result = skill.convert_excel_to_csv(sys.argv[2], sys.argv[3])
            print(f"Converted: {result}")
        elif command == 'json2xml' and len(sys.argv) >= 4:
            result = skill.convert_json_to_xml(sys.argv[2], sys.argv[3])
            print(f"Converted: {result}")
        elif command == 'xml2json' and len(sys.argv) >= 4:
            result = skill.convert_xml_to_json(sys.argv[2], sys.argv[3])
            print(f"Converted: {result}")
        elif command == 'encode' and len(sys.argv) >= 5:
            result = skill.convert_encoding(sys.argv[2], sys.argv[3], to_encoding=sys.argv[4])
            print(f"Converted: {result}")
        else:
            print("Invalid command or arguments")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
