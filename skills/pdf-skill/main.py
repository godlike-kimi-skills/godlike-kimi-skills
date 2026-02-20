#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Processor - A comprehensive PDF manipulation tool

This module provides a PDFProcessor class for handling various PDF operations
including text extraction, merging, splitting, and conversion.

Author: godlike-kimi-skills
License: MIT
Version: 1.0.0
"""

import os
import re
import argparse
import json
from pathlib import Path
from typing import List, Tuple, Optional, Union, Dict, Any
from datetime import datetime

# Import PDF libraries with graceful fallback
try:
    import PyPDF2
    from PyPDF2 import PdfReader, PdfWriter
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

# Optional imports for image conversion
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class PDFProcessor:
    """
    A comprehensive PDF processing class that handles various PDF operations.
    
    This class provides methods for:
    - Text extraction from PDF documents
    - Merging multiple PDF files
    - Splitting PDFs by pages
    - Extracting specific page ranges
    - Converting PDF pages to images
    - Retrieving PDF metadata
    
    Attributes:
        password (str): Password for encrypted PDFs
        verbose (bool): Enable verbose output
    """
    
    def __init__(self, password: Optional[str] = None, verbose: bool = False):
        """
        Initialize the PDFProcessor.
        
        Args:
            password: Password for encrypted PDF documents
            verbose: Enable verbose logging
        """
        self.password = password
        self.verbose = verbose
        
        if not PYPDF2_AVAILABLE and not PDFPLUMBER_AVAILABLE:
            raise ImportError(
                "At least one PDF library is required. "
                "Please install: pip install PyPDF2 pdfplumber"
            )
    
    def _log(self, message: str) -> None:
        """Print verbose message if verbose mode is enabled."""
        if self.verbose:
            print(f"[PDFProcessor] {message}")
    
    def _open_pdf(self, file_path: str) -> Union[PdfReader, Any]:
        """
        Open a PDF file with password handling.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            PdfReader object or pdfplumber PDF object
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If password is required but not provided
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if PDFPLUMBER_AVAILABLE:
            pdf = pdfplumber.open(file_path)
            if pdf.doc.is_encrypted and self.password:
                pdf.close()
                pdf = pdfplumber.open(file_path, password=self.password)
            return pdf
        else:
            reader = PdfReader(file_path)
            if reader.is_encrypted:
                if self.password:
                    reader.decrypt(self.password)
                else:
                    raise ValueError("PDF is encrypted. Please provide password.")
            return reader
    
    def extract_text(self, file_path: str, page_numbers: Optional[List[int]] = None) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            page_numbers: Optional list of page numbers to extract (1-indexed)
            
        Returns:
            Extracted text as string
        """
        self._log(f"Extracting text from: {file_path}")
        
        text_parts = []
        
        if PDFPLUMBER_AVAILABLE:
            with pdfplumber.open(file_path) as pdf:
                pages_to_process = page_numbers if page_numbers else range(1, len(pdf.pages) + 1)
                for page_num in pages_to_process:
                    if 1 <= page_num <= len(pdf.pages):
                        page = pdf.pages[page_num - 1]
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(f"--- Page {page_num} ---\n{page_text}")
        else:
            reader = PdfReader(file_path)
            pages_to_process = page_numbers if page_numbers else range(1, len(reader.pages) + 1)
            for page_num in pages_to_process:
                if 1 <= page_num <= len(reader.pages):
                    page = reader.pages[page_num - 1]
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"--- Page {page_num} ---\n{page_text}")
        
        return "\n\n".join(text_parts)
    
    def merge_pdfs(self, input_dir: str, output_path: str, 
                   sort_by: str = "filename") -> str:
        """
        Merge multiple PDF files into one.
        
        Args:
            input_dir: Directory containing PDF files
            output_path: Path for the merged output file
            sort_by: Sorting strategy ('filename' or 'modified_time')
            
        Returns:
            Path to the merged file
        """
        self._log(f"Merging PDFs from: {input_dir}")
        
        if not os.path.isdir(input_dir):
            raise ValueError(f"Input must be a directory: {input_dir}")
        
        # Collect all PDF files
        pdf_files = [
            os.path.join(input_dir, f) for f in os.listdir(input_dir)
            if f.lower().endswith('.pdf')
        ]
        
        if not pdf_files:
            raise ValueError(f"No PDF files found in: {input_dir}")
        
        # Sort files
        if sort_by == "filename":
            pdf_files.sort()
        elif sort_by == "modified_time":
            pdf_files.sort(key=lambda x: os.path.getmtime(x))
        else:
            raise ValueError(f"Unknown sort strategy: {sort_by}")
        
        self._log(f"Found {len(pdf_files)} PDF files to merge")
        
        # Merge PDFs
        merger = PyPDF2.PdfMerger()
        
        for pdf_file in pdf_files:
            self._log(f"Adding: {os.path.basename(pdf_file)}")
            merger.append(pdf_file)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or '.', exist_ok=True)
        
        # Write output
        with open(output_path, 'wb') as output_file:
            merger.write(output_file)
        
        merger.close()
        self._log(f"Merged PDF saved to: {output_path}")
        
        return output_path
    
    def split_pdf(self, file_path: str, output_dir: str, 
                  pages_per_file: int = 1) -> List[str]:
        """
        Split a PDF into multiple files.
        
        Args:
            file_path: Path to the input PDF
            output_dir: Directory for output files
            pages_per_file: Number of pages per output file
            
        Returns:
            List of output file paths
        """
        self._log(f"Splitting PDF: {file_path}")
        
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)
        
        os.makedirs(output_dir, exist_ok=True)
        
        output_files = []
        base_name = Path(file_path).stem
        
        for start_page in range(0, total_pages, pages_per_file):
            writer = PdfWriter()
            end_page = min(start_page + pages_per_file, total_pages)
            
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])
            
            output_filename = f"{base_name}_page_{start_page + 1}-{end_page}.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            output_files.append(output_path)
            self._log(f"Created: {output_filename}")
        
        return output_files
    
    def parse_page_ranges(self, pages_str: str, max_pages: int) -> List[Tuple[int, int]]:
        """
        Parse page range string into list of tuples.
        
        Args:
            pages_str: Page range string (e.g., "1-5,10,15-20")
            max_pages: Maximum number of pages in the document
            
        Returns:
            List of (start, end) tuples
        """
        ranges = []
        parts = pages_str.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                start_str, end_str = part.split('-', 1)
                start = int(start_str) if start_str else 1
                end = int(end_str) if end_str else max_pages
            else:
                start = end = int(part)
            
            # Validate and clamp values
            start = max(1, min(start, max_pages))
            end = max(1, min(end, max_pages))
            
            if start <= end:
                ranges.append((start, end))
        
        return ranges
    
    def extract_pages(self, file_path: str, output_path: str, 
                      page_ranges: List[Tuple[int, int]]) -> str:
        """
        Extract specific pages from a PDF.
        
        Args:
            file_path: Path to the input PDF
            output_path: Path for the output PDF
            page_ranges: List of (start, end) page tuples (1-indexed)
            
        Returns:
            Path to the output file
        """
        self._log(f"Extracting pages from: {file_path}")
        
        reader = PdfReader(file_path)
        writer = PdfWriter()
        
        for start, end in page_ranges:
            for page_num in range(start - 1, end):
                if 0 <= page_num < len(reader.pages):
                    writer.add_page(reader.pages[page_num])
        
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or '.', exist_ok=True)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        self._log(f"Extracted PDF saved to: {output_path}")
        return output_path
    
    def pdf_to_images(self, file_path: str, output_dir: str, 
                      dpi: int = 200, fmt: str = "png") -> List[str]:
        """
        Convert PDF pages to images.
        
        Args:
            file_path: Path to the input PDF
            output_dir: Directory for output images
            dpi: Resolution in dots per inch
            fmt: Image format (png, jpg, jpeg, tiff)
            
        Returns:
            List of output image paths
        """
        self._log(f"Converting PDF to images: {file_path}")
        
        if not PYMUPDF_AVAILABLE:
            raise ImportError(
                "PyMuPDF (fitz) is required for PDF to image conversion. "
                "Install with: pip install pymupdf"
            )
        
        os.makedirs(output_dir, exist_ok=True)
        
        doc = fitz.open(file_path)
        base_name = Path(file_path).stem
        output_files = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Calculate zoom matrix based on DPI
            zoom = dpi / 72  # 72 is the default PDF DPI
            mat = fitz.Matrix(zoom, zoom)
            
            pix = page.get_pixmap(matrix=mat)
            
            output_filename = f"{base_name}_page_{page_num + 1}.{fmt}"
            output_path = os.path.join(output_dir, output_filename)
            
            pix.save(output_path)
            output_files.append(output_path)
            
            self._log(f"Created: {output_filename}")
        
        doc.close()
        return output_files
    
    def get_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get PDF document information.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing PDF metadata
        """
        self._log(f"Getting info for: {file_path}")
        
        reader = PdfReader(file_path)
        info = reader.metadata
        
        result = {
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "num_pages": len(reader.pages),
            "is_encrypted": reader.is_encrypted,
            "metadata": {}
        }
        
        if info:
            result["metadata"] = {
                "title": info.title,
                "author": info.author,
                "subject": info.subject,
                "creator": info.creator,
                "producer": info.producer,
                "creation_date": info.creation_date,
                "modification_date": info.modification_date,
            }
        
        return result
    
    def save_text(self, file_path: str, output_path: str, 
                  page_numbers: Optional[List[int]] = None) -> str:
        """
        Extract text and save to file.
        
        Args:
            file_path: Path to the PDF file
            output_path: Path for the output text file
            page_numbers: Optional list of page numbers
            
        Returns:
            Path to the output file
        """
        text = self.extract_text(file_path, page_numbers)
        
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or '.', exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return output_path


def main():
    """Command-line interface for PDF Processor."""
    parser = argparse.ArgumentParser(
        description="PDF Processor - Comprehensive PDF manipulation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --action extract_text --input doc.pdf --output text.txt
  %(prog)s --action merge --input ./pdfs/ --output merged.pdf
  %(prog)s --action split --input doc.pdf --output ./pages/
  %(prog)s --action extract_pages --input doc.pdf --pages "1-5,10" --output extract.pdf
  %(prog)s --action pdf_to_images --input doc.pdf --output ./images/ --dpi 300
  %(prog)s --action info --input doc.pdf
        """
    )
    
    parser.add_argument('--action', required=True,
                        choices=['extract_text', 'merge', 'split', 'extract_pages', 
                                'pdf_to_images', 'info'],
                        help='Operation to perform')
    parser.add_argument('--input', required=True,
                        help='Input file or directory')
    parser.add_argument('--output',
                        help='Output file or directory')
    parser.add_argument('--pages',
                        help='Page ranges (e.g., "1-5,10,15-20")')
    parser.add_argument('--password',
                        help='Password for encrypted PDFs')
    parser.add_argument('--dpi', type=int, default=200,
                        help='DPI for image conversion (default: 200)')
    parser.add_argument('--format', default='png',
                        choices=['png', 'jpg', 'jpeg', 'tiff'],
                        help='Image format (default: png)')
    parser.add_argument('--merge_strategy', default='filename',
                        choices=['filename', 'modified_time'],
                        help='Merge sorting strategy (default: filename)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = PDFProcessor(password=args.password, verbose=args.verbose)
    
    try:
        if args.action == 'extract_text':
            output = args.output or args.input.replace('.pdf', '.txt')
            processor.save_text(args.input, output)
            print(f"Text extracted to: {output}")
        
        elif args.action == 'merge':
            output = args.output or 'merged.pdf'
            processor.merge_pdfs(args.input, output, sort_by=args.merge_strategy)
            print(f"Merged PDF saved to: {output}")
        
        elif args.action == 'split':
            output = args.output or './split_pages/'
            files = processor.split_pdf(args.input, output)
            print(f"Split into {len(files)} files in: {output}")
        
        elif args.action == 'extract_pages':
            if not args.pages:
                parser.error('--pages is required for extract_pages action')
            if not args.output:
                parser.error('--output is required for extract_pages action')
            
            reader = PdfReader(args.input)
            page_ranges = processor.parse_page_ranges(args.pages, len(reader.pages))
            processor.extract_pages(args.input, args.output, page_ranges)
            print(f"Extracted pages saved to: {args.output}")
        
        elif args.action == 'pdf_to_images':
            output = args.output or './pdf_images/'
            files = processor.pdf_to_images(args.input, output, dpi=args.dpi, fmt=args.format)
            print(f"Converted to {len(files)} images in: {output}")
        
        elif args.action == 'info':
            info = processor.get_info(args.input)
            print(json.dumps(info, indent=2, default=str))
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
