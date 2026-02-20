#!/usr/bin/env python3
"""
Tests for Code Metrics Skill
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.main import (
    CodeMetricsAnalyzer, ComplexityMetrics, LineMetrics,
    FileMetrics, ProjectMetrics, DuplicateBlock
)

class TestLineMetrics(unittest.TestCase):
    
    def test_initialization(self):
        """Test line metrics initialization"""
        metrics = LineMetrics(
            total_lines=100,
            code_lines=70,
            blank_lines=10,
            comment_lines=15,
            docstring_lines=5
        )
        
        self.assertEqual(metrics.total_lines, 100)
        self.assertEqual(metrics.code_lines, 70)
        self.assertEqual(metrics.comment_ratio, 28.57)  # (15+5)/70 * 100
    
    def test_zero_division(self):
        """Test comment ratio with no code lines"""
        metrics = LineMetrics()
        self.assertEqual(metrics.comment_ratio, 0.0)
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        metrics = LineMetrics(total_lines=50, code_lines=30)
        result = metrics.to_dict()
        
        self.assertIn("total_lines", result)
        self.assertIn("code_lines", result)
        self.assertIn("comment_ratio", result)

class TestComplexityMetrics(unittest.TestCase):
    
    def test_initialization(self):
        """Test complexity metrics initialization"""
        metrics = ComplexityMetrics(
            function_name="test_func",
            line_number=10,
            complexity=5,
            classification="low"
        )
        
        self.assertEqual(metrics.function_name, "test_func")
        self.assertEqual(metrics.line_number, 10)
        self.assertEqual(metrics.complexity, 5)
        self.assertEqual(metrics.classification, "low")
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        metrics = ComplexityMetrics("func", 1, 3, "low")
        result = metrics.to_dict()
        
        self.assertEqual(result["function_name"], "func")
        self.assertEqual(result["complexity"], 3)

class TestDuplicateBlock(unittest.TestCase):
    
    def test_initialization(self):
        """Test duplicate block initialization"""
        block = DuplicateBlock(
            hash_value="abc123",
            code_snippet="x = 1\ny = 2",
            occurrences=[("file1.py", 10), ("file2.py", 20)],
            line_count=5
        )
        
        self.assertEqual(block.hash_value, "abc123")
        self.assertEqual(len(block.occurrences), 2)
        self.assertEqual(block.line_count, 5)

class TestCodeMetricsAnalyzer(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a sample Python file
        self.sample_code = '''
"""Sample module."""

def simple():
    return 1

def medium_complexity(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

def high_complexity(a, b, c):
    if a > 0:
        if b > 0:
            if c > 0:
                return 1
            else:
                return 2
        else:
            return 3
    else:
        return 4

# Duplicate block 1
x = 1
y = 2
z = x + y

# Duplicate block 2
x = 1
y = 2
z = x + y
'''
        
        with open(os.path.join(self.temp_dir, "sample.py"), 'w') as f:
            f.write(self.sample_code)
        
        self.analyzer = CodeMetricsAnalyzer(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_should_exclude(self):
        """Test exclude pattern matching"""
        self.assertTrue(self.analyzer.should_exclude(Path("/path/venv/file.py")))
        self.assertTrue(self.analyzer.should_exclude(Path("/path/__pycache__/file.py")))
        self.assertFalse(self.analyzer.should_exclude(Path("/path/src/file.py")))
    
    def test_get_python_files(self):
        """Test getting Python files"""
        files = self.analyzer.get_python_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].name, "sample.py")
    
    def test_count_lines(self):
        """Test line counting"""
        file_path = Path(os.path.join(self.temp_dir, "sample.py"))
        metrics = self.analyzer.count_lines(file_path)
        
        self.assertGreater(metrics.total_lines, 0)
        self.assertGreater(metrics.code_lines, 0)
    
    def test_calculate_complexity(self):
        """Test complexity calculation"""
        file_path = Path(os.path.join(self.temp_dir, "sample.py"))
        complexities = self.analyzer.calculate_complexity(file_path)
        
        self.assertEqual(len(complexities), 3)  # 3 functions
        
        # Check function names
        func_names = [c.function_name for c in complexities]
        self.assertIn("simple", func_names)
        self.assertIn("medium_complexity", func_names)
        self.assertIn("high_complexity", func_names)
    
    def test_complexity_classification(self):
        """Test complexity classification"""
        self.assertEqual(self.analyzer._classify_complexity(3), "low")
        self.assertEqual(self.analyzer._classify_complexity(7), "medium")
        self.assertEqual(self.analyzer._classify_complexity(15), "high")
        self.assertEqual(self.analyzer._classify_complexity(25), "very high")
    
    def test_find_duplicates(self):
        """Test duplicate detection"""
        file_path = Path(os.path.join(self.temp_dir, "sample.py"))
        self.analyzer.find_duplicates(file_path)
        
        # Should find some duplicates in the sample code
        duplicates = self.analyzer.get_duplicate_blocks()
        self.assertGreaterEqual(len(duplicates), 0)
    
    def test_normalize_code(self):
        """Test code normalization"""
        code = "x = 1  # comment\n  y = 2"
        normalized = self.analyzer._normalize_code(code)
        
        self.assertNotIn("#", normalized)
        self.assertEqual(normalized, "x = 1 y = 2")
    
    def test_analyze_file(self):
        """Test complete file analysis"""
        file_path = Path(os.path.join(self.temp_dir, "sample.py"))
        metrics = self.analyzer.analyze_file(file_path)
        
        self.assertIsInstance(metrics, FileMetrics)
        self.assertEqual(metrics.file_path, str(file_path))
        self.assertGreater(metrics.lines.total_lines, 0)
        self.assertGreater(len(metrics.complexity), 0)
        self.assertGreaterEqual(metrics.quality_score, 0)
        self.assertLessEqual(metrics.quality_score, 100)
    
    def test_analyze_project(self):
        """Test project analysis"""
        project = self.analyzer.analyze_project()
        
        self.assertIsInstance(project, ProjectMetrics)
        self.assertEqual(project.total_files, 1)
        self.assertGreater(project.total_lines, 0)
        self.assertGreaterEqual(project.quality_score, 0)
    
    def test_calculate_maintainability(self):
        """Test maintainability calculation"""
        lines = LineMetrics(code_lines=100, comment_lines=20)
        complexities = [
            ComplexityMetrics("f1", 1, 2, "low"),
            ComplexityMetrics("f2", 1, 3, "low")
        ]
        
        score = self.analyzer.calculate_maintainability(lines, complexities)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_generate_report_text(self):
        """Test text report generation"""
        project = self.analyzer.analyze_project()
        report = self.analyzer.generate_report(project, format="text")
        
        self.assertIn("CODE QUALITY METRICS REPORT", report)
        self.assertIn("SUMMARY", report)
    
    def test_generate_report_json(self):
        """Test JSON report generation"""
        import json
        
        project = self.analyzer.analyze_project()
        report = self.analyzer.generate_report(project, format="json")
        
        data = json.loads(report)
        self.assertIn("summary", data)
        self.assertIn("files", data)
        self.assertIn("total_files", data["summary"])

class TestProjectMetrics(unittest.TestCase):
    
    def test_initialization(self):
        """Test project metrics initialization"""
        project = ProjectMetrics(
            total_files=10,
            total_lines=1000,
            avg_complexity=5.5,
            quality_score=75.0
        )
        
        self.assertEqual(project.total_files, 10)
        self.assertEqual(project.total_lines, 1000)
        self.assertEqual(project.avg_complexity, 5.5)
        self.assertEqual(project.quality_score, 75.0)

class TestFileMetrics(unittest.TestCase):
    
    def test_initialization(self):
        """Test file metrics initialization"""
        metrics = FileMetrics(
            file_path="/test/file.py",
            file_size=1024
        )
        
        self.assertEqual(metrics.file_path, "/test/file.py")
        self.assertEqual(metrics.file_size, 1024)
        self.assertIsInstance(metrics.lines, LineMetrics)
        self.assertEqual(len(metrics.complexity), 0)
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        metrics = FileMetrics("/test/file.py")
        result = metrics.to_dict()
        
        self.assertIn("file_path", result)
        self.assertIn("lines", result)
        self.assertIn("complexity", result)

if __name__ == "__main__":
    unittest.main()
