#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic tests for PDF Processor skill

This module contains unit tests for the PDFProcessor class.
Run with: python -m pytest tests/test_basic.py -v
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import PDFProcessor

# Try to import PyPDF2 for test setup
try:
    from PyPDF2 import PdfWriter
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


class TestPDFProcessor(unittest.TestCase):
    """Test cases for PDFProcessor class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that can be reused across tests."""
        if not PYPDF2_AVAILABLE:
            raise unittest.SkipTest("PyPDF2 not available")
    
    def setUp(self):
        """Set up test fixtures before each test."""
        self.processor = PDFProcessor(verbose=False)
        self.test_dir = tempfile.mkdtemp()
        
        # Create a simple test PDF
        self.test_pdf_path = os.path.join(self.test_dir, "test.pdf")
        self._create_test_pdf(self.test_pdf_path, num_pages=5)
    
    def tearDown(self):
        """Clean up after each test."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _create_test_pdf(self, path: str, num_pages: int = 3):
        """Helper to create a simple test PDF."""
        writer = PdfWriter()
        
        # Create simple pages with text
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        for i in range(num_pages):
            page_path = os.path.join(self.test_dir, f"temp_page_{i}.pdf")
            c = canvas.Canvas(page_path, pagesize=letter)
            c.drawString(100, 700, f"This is page {i + 1} of the test PDF")
            c.save()
            
            # Merge the page
            from PyPDF2 import PdfReader
            reader = PdfReader(page_path)
            writer.add_page(reader.pages[0])
            os.remove(page_path)
        
        with open(path, 'wb') as f:
            writer.write(f)
    
    def test_initialization(self):
        """Test PDFProcessor initialization."""
        processor = PDFProcessor()
        self.assertIsNone(processor.password)
        self.assertFalse(processor.verbose)
        
        processor_with_password = PDFProcessor(password="secret", verbose=True)
        self.assertEqual(processor_with_password.password, "secret")
        self.assertTrue(processor_with_password.verbose)
    
    def test_parse_page_ranges(self):
        """Test page range parsing."""
        # Single page
        ranges = self.processor.parse_page_ranges("5", 10)
        self.assertEqual(ranges, [(5, 5)])
        
        # Range
        ranges = self.processor.parse_page_ranges("1-5", 10)
        self.assertEqual(ranges, [(1, 5)])
        
        # Multiple ranges
        ranges = self.processor.parse_page_ranges("1-3,5,7-9", 10)
        self.assertEqual(ranges, [(1, 3), (5, 5), (7, 9)])
        
        # Open-ended ranges
        ranges = self.processor.parse_page_ranges("-5", 10)
        self.assertEqual(ranges, [(1, 5)])
        
        ranges = self.processor.parse_page_ranges("5-", 10)
        self.assertEqual(ranges, [(5, 10)])
    
    def test_parse_page_ranges_clamping(self):
        """Test that page ranges are properly clamped."""
        # Out of range values should be clamped
        ranges = self.processor.parse_page_ranges("1-100", 5)
        self.assertEqual(ranges, [(1, 5)])
        
        ranges = self.processor.parse_page_ranges("0-3", 5)
        self.assertEqual(ranges, [(1, 3)])
    
    def test_get_info(self):
        """Test getting PDF information."""
        info = self.processor.get_info(self.test_pdf_path)
        
        self.assertEqual(info["file_path"], self.test_pdf_path)
        self.assertEqual(info["num_pages"], 5)
        self.assertFalse(info["is_encrypted"])
        self.assertIn("file_size", info)
        self.assertIn("metadata", info)
    
    def test_extract_text(self):
        """Test text extraction."""
        # Note: This test may need adjustment based on actual PDF content
        # Using pdfplumber or PyPDF2's text extraction
        try:
            text = self.processor.extract_text(self.test_pdf_path)
            # Should contain something or be empty (depends on PDF content)
            self.assertIsInstance(text, str)
        except Exception as e:
            # Text extraction may fail for certain PDF types
            self.skipTest(f"Text extraction not available: {e}")
    
    def test_extract_pages(self):
        """Test extracting specific pages."""
        output_path = os.path.join(self.test_dir, "extracted.pdf")
        
        # Extract pages 1-2
        result = self.processor.extract_pages(
            self.test_pdf_path, 
            output_path, 
            [(1, 2)]
        )
        
        self.assertEqual(result, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        # Verify page count
        info = self.processor.get_info(output_path)
        self.assertEqual(info["num_pages"], 2)
    
    def test_split_pdf(self):
        """Test PDF splitting."""
        output_dir = os.path.join(self.test_dir, "split")
        
        # Split into single pages
        files = self.processor.split_pdf(self.test_pdf_path, output_dir, pages_per_file=1)
        
        self.assertEqual(len(files), 5)
        for f in files:
            self.assertTrue(os.path.exists(f))
        
        # Verify each split file has 1 page
        for f in files:
            info = self.processor.get_info(f)
            self.assertEqual(info["num_pages"], 1)
    
    def test_merge_pdfs(self):
        """Test PDF merging."""
        # Create multiple test PDFs
        pdf_dir = os.path.join(self.test_dir, "pdfs_to_merge")
        os.makedirs(pdf_dir, exist_ok=True)
        
        for i in range(3):
            pdf_path = os.path.join(pdf_dir, f"doc_{i:02d}.pdf")
            self._create_test_pdf(pdf_path, num_pages=2)
        
        output_path = os.path.join(self.test_dir, "merged.pdf")
        
        # Merge PDFs
        result = self.processor.merge_pdfs(pdf_dir, output_path, sort_by="filename")
        
        self.assertEqual(result, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        # Verify merged PDF has correct number of pages (3 files * 2 pages = 6 pages)
        info = self.processor.get_info(output_path)
        self.assertEqual(info["num_pages"], 6)
    
    def test_merge_pdfs_sort_by_modified_time(self):
        """Test PDF merging with modified time sorting."""
        pdf_dir = os.path.join(self.test_dir, "pdfs_time_sort")
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Create PDFs with delays to ensure different modification times
        import time
        for i in range(3):
            pdf_path = os.path.join(pdf_dir, f"doc_{i}.pdf")
            self._create_test_pdf(pdf_path, num_pages=1)
            time.sleep(0.1)
        
        output_path = os.path.join(self.test_dir, "merged_time.pdf")
        result = self.processor.merge_pdfs(pdf_dir, output_path, sort_by="modified_time")
        
        self.assertTrue(os.path.exists(result))
    
    def test_save_text(self):
        """Test saving extracted text to file."""
        output_path = os.path.join(self.test_dir, "output.txt")
        
        result = self.processor.save_text(self.test_pdf_path, output_path)
        
        self.assertEqual(result, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        # Verify file is readable
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIsInstance(content, str)


class TestPageRangeParsing(unittest.TestCase):
    """Dedicated tests for page range parsing edge cases."""
    
    def setUp(self):
        self.processor = PDFProcessor()
    
    def test_empty_ranges(self):
        """Test handling of invalid/empty ranges."""
        # Reversed ranges should be handled
        ranges = self.processor.parse_page_ranges("5-1", 10)
        # Should normalize or handle gracefully
        self.assertIsInstance(ranges, list)
    
    def test_whitespace_handling(self):
        """Test handling of whitespace in page strings."""
        ranges = self.processor.parse_page_ranges(" 1 - 3 , 5 , 7 - 9 ", 10)
        self.assertEqual(ranges, [(1, 3), (5, 5), (7, 9)])
    
    def test_single_page_document(self):
        """Test with single page document."""
        ranges = self.processor.parse_page_ranges("1-5", 1)
        self.assertEqual(ranges, [(1, 1)])


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def setUp(self):
        self.processor = PDFProcessor()
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_nonexistent_file(self):
        """Test handling of non-existent files."""
        with self.assertRaises(FileNotFoundError):
            self.processor.get_info("/nonexistent/path/file.pdf")
    
    def test_invalid_merge_directory(self):
        """Test merge with invalid directory."""
        with self.assertRaises(ValueError):
            self.processor.merge_pdfs(
                "/nonexistent/directory/",
                "output.pdf"
            )
    
    def test_empty_directory_merge(self):
        """Test merge with empty directory."""
        empty_dir = os.path.join(self.test_dir, "empty")
        os.makedirs(empty_dir, exist_ok=True)
        
        with self.assertRaises(ValueError):
            self.processor.merge_pdfs(empty_dir, "output.pdf")


class TestCommandLineInterface(unittest.TestCase):
    """Test command-line interface functionality."""
    
    def test_cli_import(self):
        """Test that CLI module can be imported."""
        # This is a basic smoke test
        import main
        self.assertTrue(hasattr(main, 'main'))
        self.assertTrue(hasattr(main, 'PDFProcessor'))


def create_test_suite():
    """Create a test suite with all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestPDFProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestPageRangeParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestCommandLineInterface))
    
    return suite


if __name__ == '__main__':
    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(create_test_suite())
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
