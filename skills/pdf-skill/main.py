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
import argparse
import json
from pathlib import Path
from typing import List, Tuple, Optional, Union, Dict, Any

# Import PDF libraries with graceful fallback
try:
    import PyPDF2
    from PyPDF2 import PdfReader, PdfWriter, PdfMerger
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

# Optional import for image conversion
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
            raise ImportError("At least one PDF library is required. "
                            "Please install: pip install PyPDF2 pdfplumber")
    
    def _log(self, msg: str) -> None:
        """Print verbose message if verbose mode is enabled."""
        if self.verbose:
            print(f"[PDF] {msg}")
    
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
            raise FileNotFoundError(f"PDF not found: {file_path}")
        
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
                    raise ValueError("PDF encrypted. Provide password.")
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
        self._log(f"Extracting: {file_path}")
        text_parts = []
        
        if PDFPLUMBER_AVAILABLE:
            with pdfplumber.open(file_path) as pdf:
                pages = page_numbers or range(1, len(pdf.pages) + 1)
                for num in pages:
                    if 1 <= num <= len(pdf.pages):
                        txt = pdf.pages[num - 1].extract_text()
                        if txt:
                            text_parts.append(f"--- Page {num} ---\n{txt}")
        else:
            reader = PdfReader(file_path)
            pages = page_numbers or range(1, len(reader.pages) + 1)
            for num in pages:
                if 1 <= num <= len(reader.pages):
                    txt = reader.pages[num - 1].extract_text()
                    if txt:
                        text_parts.append(f"--- Page {num} ---\n{txt}")
        return "\n\n".join(text_parts)
    
    def merge_pdfs(self, input_dir: str, output_path: str, sort_by: str = "filename") -> str:
        """
        Merge multiple PDF files into one.
        
        Args:
            input_dir: Directory containing PDF files
            output_path: Path for the merged output file
            sort_by: Sorting strategy ('filename' or 'modified_time')
            
        Returns:
            Path to the merged file
        """
        self._log(f"Merging from: {input_dir}")
        if not os.path.isdir(input_dir):
            raise ValueError(f"Input must be directory: {input_dir}")
        
        pdf_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) 
                     if f.lower().endswith('.pdf')]
        if not pdf_files:
            raise ValueError(f"No PDFs in: {input_dir}")
        
        pdf_files.sort(key=lambda x: x if sort_by == "filename" else os.path.getmtime(x))
        
        merger = PdfMerger()
        for f in pdf_files:
            self._log(f"Adding: {os.path.basename(f)}")
            merger.append(f)
        
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or '.', exist_ok=True)
        with open(output_path, 'wb') as out:
            merger.write(out)
        merger.close()
        self._log(f"Saved: {output_path}")
        return output_path
    
    def split_pdf(self, file_path: str, output_dir: str, pages_per_file: int = 1) -> List[str]:
        """
        Split a PDF into multiple files.
        
        Args:
            file_path: Path to the input PDF
            output_dir: Directory for output files
            pages_per_file: Number of pages per output file
            
        Returns:
            List of output file paths
        """
        self._log(f"Splitting: {file_path}")
        reader = PdfReader(file_path)
        os.makedirs(output_dir, exist_ok=True)
        
        output_files, base_name = [], Path(file_path).stem
        for start in range(0, len(reader.pages), pages_per_file):
            writer = PdfWriter()
            end = min(start + pages_per_file, len(reader.pages))
            for i in range(start, end):
                writer.add_page(reader.pages[i])
            out_name = f"{base_name}_page_{start + 1}-{end}.pdf"
            out_path = os.path.join(output_dir, out_name)
            with open(out_path, 'wb') as f:
                writer.write(f)
            output_files.append(out_path)
            self._log(f"Created: {out_name}")
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
        for part in pages_str.split(','):
            part = part.strip()
            if '-' in part:
                s, e = part.split('-', 1)
                start = int(s) if s else 1
                end = int(e) if e else max_pages
            else:
                start = end = int(part)
            # Validate and clamp values
            start = max(1, min(start, max_pages))
            end = max(1, min(end, max_pages))
            if start <= end:
                ranges.append((start, end))
        return ranges
    
    def extract_pages(self, file_path: str, output_path: str, page_ranges: List[Tuple[int, int]]) -> str:
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
            for i in range(start - 1, end):
                if 0 <= i < len(reader.pages):
                    writer.add_page(reader.pages[i])
        
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or '.', exist_ok=True)
        with open(output_path, 'wb') as f:
            writer.write(f)
        self._log(f"Saved: {output_path}")
        return output_path
    
    def pdf_to_images(self, file_path: str, output_dir: str, dpi: int = 200, fmt: str = "png") -> List[str]:
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
        self._log(f"Converting to images: {file_path}")
        if not PYMUPDF_AVAILABLE:
            raise ImportError("Install pymupdf for image conversion: pip install pymupdf")
        
        os.makedirs(output_dir, exist_ok=True)
        doc = fitz.open(file_path)
        base_name = Path(file_path).stem
        output_files = []
        
        for i in range(len(doc)):
            page = doc.load_page(i)
            zoom = dpi / 72  # 72 is the default PDF DPI
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            out_name = f"{base_name}_page_{i + 1}.{fmt}"
            out_path = os.path.join(output_dir, out_name)
            pix.save(out_path)
            output_files.append(out_path)
            self._log(f"Created: {out_name}")
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
        self._log(f"Getting info: {file_path}")
        reader = PdfReader(file_path)
        info = reader.metadata or {}
        return {
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "num_pages": len(reader.pages),
            "is_encrypted": reader.is_encrypted,
            "metadata": {k: str(v) for k, v in info.items()} if info else {}
        }
    
    def save_text(self, file_path: str, output_path: str, page_numbers: Optional[List[int]] = None) -> str:
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
        epilog="""Examples:
  %(prog)s --action extract_text --input doc.pdf --output text.txt
  %(prog)s --action merge --input ./pdfs/ --output merged.pdf
  %(prog)s --action split --input doc.pdf --output ./pages/
  %(prog)s --action extract_pages --input doc.pdf --pages "1-5,10" --output extract.pdf
  %(prog)s --action pdf_to_images --input doc.pdf --output ./images/ --dpi 300
  %(prog)s --action info --input doc.pdf"""
    )
    
    parser.add_argument('--action', required=True,
                        choices=['extract_text', 'merge', 'split', 'extract_pages', 'pdf_to_images', 'info'],
                        help='Operation to perform')
    parser.add_argument('--input', required=True, help='Input file or directory')
    parser.add_argument('--output', help='Output file or directory')
    parser.add_argument('--pages', help='Page ranges (e.g., "1-5,10,15-20")')
    parser.add_argument('--password', help='PDF password')
    parser.add_argument('--dpi', type=int, default=200, help='DPI for images (default: 200)')
    parser.add_argument('--format', default='png', choices=['png', 'jpg', 'jpeg', 'tiff'],
                        help='Image format (default: png)')
    parser.add_argument('--merge_strategy', default='filename', choices=['filename', 'modified_time'],
                        help='Merge sorting strategy (default: filename)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    args = parser.parse_args()
    processor = PDFProcessor(password=args.password, verbose=args.verbose)
    
    try:
        if args.action == 'extract_text':
            out = args.output or args.input.replace('.pdf', '.txt')
            processor.save_text(args.input, out)
            print(f"Text saved: {out}")
        
        elif args.action == 'merge':
            out = args.output or 'merged.pdf'
            processor.merge_pdfs(args.input, out, sort_by=args.merge_strategy)
            print(f"Merged: {out}")
        
        elif args.action == 'split':
            out = args.output or './split_pages/'
            files = processor.split_pdf(args.input, out)
            print(f"Split into {len(files)} files: {out}")
        
        elif args.action == 'extract_pages':
            if not args.pages or not args.output:
                parser.error('--pages and --output required')
            reader = PdfReader(args.input)
            ranges = processor.parse_page_ranges(args.pages, len(reader.pages))
            processor.extract_pages(args.input, args.output, ranges)
            print(f"Extracted: {args.output}")
        
        elif args.action == 'pdf_to_images':
            out = args.output or './pdf_images/'
            files = processor.pdf_to_images(args.input, out, dpi=args.dpi, fmt=args.format)
            print(f"Created {len(files)} images: {out}")
        
        elif args.action == 'info':
            print(json.dumps(processor.get_info(args.input), indent=2, default=str))
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == '__main__':
    exit(main())
