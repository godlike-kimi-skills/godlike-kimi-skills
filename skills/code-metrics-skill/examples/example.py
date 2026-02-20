#!/usr/bin/env python3
"""
Code Metrics Skill Usage Examples
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, '..')

from scripts.main import (
    CodeMetricsAnalyzer, ComplexityMetrics, LineMetrics,
    FileMetrics, ProjectMetrics, CacheConfig
)

def create_sample_project(base_dir):
    """Create a sample Python project for analysis"""
    # Create directory structure
    src_dir = os.path.join(base_dir, "src")
    os.makedirs(src_dir)
    
    # Sample module with various complexity levels
    sample_module = '''
"""
Sample module for testing code metrics.
"""

def simple_function():
    """A simple function with low complexity."""
    return 42

def medium_complexity(x):
    """Function with medium complexity."""
    if x > 0:
        if x < 10:
            return "small"
        elif x < 100:
            return "medium"
        else:
            return "large"
    elif x == 0:
        return "zero"
    else:
        return "negative"

def high_complexity(data):
    """Function with high complexity - needs refactoring."""
    result = []
    for item in data:
        if item["type"] == "A":
            if item["value"] > 10:
                if item["active"]:
                    result.append(item["value"] * 2)
                else:
                    result.append(item["value"])
            else:
                result.append(0)
        elif item["type"] == "B":
            if item["value"] < 5:
                result.append(item["value"] + 10)
            else:
                result.append(item["value"] - 5)
        elif item["type"] == "C":
            result.append(item["value"] ** 2)
        else:
            result.append(None)
    return result

class SampleClass:
    """A sample class."""
    
    def __init__(self):
        self.data = []
    
    def add(self, item):
        """Add item to data."""
        self.data.append(item)
    
    def process(self):
        """Process all items."""
        for item in self.data:
            print(item)

# Some duplicate code for testing
def duplicate_function_1():
    """First occurrence of duplicate code."""
    x = 1
    y = 2
    z = 3
    result = x + y + z
    return result * 2

def duplicate_function_2():
    """Second occurrence of duplicate code."""
    x = 1
    y = 2
    z = 3
    result = x + y + z
    return result * 2
'''
    
    with open(os.path.join(src_dir, "module.py"), 'w') as f:
        f.write(sample_module)
    
    # Another module
    utils_module = '''
"""Utility functions."""

def helper_function():
    """A helper function."""
    return "help"

def complex_helper(n):
    """Another complex function."""
    if n == 0:
        return 0
    elif n == 1:
        return 1
    elif n == 2:
        return 1
    else:
        a, b = 1, 1
        for _ in range(n - 2):
            a, b = b, a + b
        return b
'''
    
    with open(os.path.join(src_dir, "utils.py"), 'w') as f:
        f.write(utils_module)

def example_single_file_analysis():
    """Demonstrate single file analysis"""
    temp_dir = tempfile.mkdtemp()
    create_sample_project(temp_dir)
    
    analyzer = CodeMetricsAnalyzer(temp_dir)
    file_path = Path(os.path.join(temp_dir, "src", "module.py"))
    
    print("=" * 60)
    print("Single File Analysis")
    print("=" * 60)
    
    metrics = analyzer.analyze_file(file_path)
    
    print(f"\nFile: {metrics.file_path}")
    print(f"File Size: {metrics.file_size} bytes")
    print(f"\nLine Metrics:")
    print(f"  Total Lines: {metrics.lines.total_lines}")
    print(f"  Code Lines: {metrics.lines.code_lines}")
    print(f"  Comment Lines: {metrics.lines.comment_lines}")
    print(f"  Blank Lines: {metrics.lines.blank_lines}")
    print(f"  Comment Ratio: {metrics.lines.comment_ratio:.1f}%")
    
    print(f"\nComplexity Metrics ({len(metrics.complexity)} functions):")
    for comp in metrics.complexity:
        print(f"  {comp.function_name}: {comp.complexity} ({comp.classification})")
    
    print(f"\nQuality Metrics:")
    print(f"  Maintainability Index: {metrics.maintainability_index:.1f}")
    print(f"  Quality Score: {metrics.quality_score:.1f}/100")
    print(f"  Duplicate Blocks: {len(metrics.duplicates)}")
    
    # Cleanup
    shutil.rmtree(temp_dir)

def example_project_analysis():
    """Demonstrate full project analysis"""
    temp_dir = tempfile.mkdtemp()
    create_sample_project(temp_dir)
    
    analyzer = CodeMetricsAnalyzer(temp_dir)
    
    print("\n" + "=" * 60)
    print("Project Analysis")
    print("=" * 60)
    
    project = analyzer.analyze_project()
    
    print(f"\nSummary:")
    print(f"  Total Files: {project.total_files}")
    print(f"  Total Lines: {project.total_lines:,}")
    print(f"  Code Lines: {project.total_code_lines:,}")
    print(f"  Average Complexity: {project.avg_complexity:.2f}")
    print(f"  Max Complexity: {project.max_complexity}")
    print(f"  High Complexity Functions: {project.high_complexity_functions}")
    print(f"  Duplicate Blocks: {project.duplicate_blocks}")
    print(f"  Overall Quality Score: {project.quality_score:.1f}/100")
    
    print(f"\nFile Details:")
    for file_metrics in project.files:
        print(f"  {Path(file_metrics.file_path).name}:")
        print(f"    Lines: {file_metrics.lines.total_lines}")
        print(f"    Functions: {len(file_metrics.complexity)}")
        print(f"    Quality: {file_metrics.quality_score:.1f}/100")
    
    # Cleanup
    shutil.rmtree(temp_dir)

def example_text_report():
    """Demonstrate text report generation"""
    temp_dir = tempfile.mkdtemp()
    create_sample_project(temp_dir)
    
    analyzer = CodeMetricsAnalyzer(temp_dir)
    project = analyzer.analyze_project()
    
    print("\n" + "=" * 60)
    print("Text Report")
    print("=" * 60)
    
    report = analyzer.generate_report(project, format="text")
    print(report)
    
    # Cleanup
    shutil.rmtree(temp_dir)

def example_json_report():
    """Demonstrate JSON report generation"""
    import json
    
    temp_dir = tempfile.mkdtemp()
    create_sample_project(temp_dir)
    
    analyzer = CodeMetricsAnalyzer(temp_dir)
    project = analyzer.analyze_project()
    
    print("\n" + "=" * 60)
    print("JSON Report (Summary)")
    print("=" * 60)
    
    report = analyzer.generate_report(project, format="json")
    data = json.loads(report)
    
    print(json.dumps(data["summary"], indent=2))
    
    # Cleanup
    shutil.rmtree(temp_dir)

def example_complexity_threshold():
    """Demonstrate complexity threshold filtering"""
    temp_dir = tempfile.mkdtemp()
    create_sample_project(temp_dir)
    
    analyzer = CodeMetricsAnalyzer(temp_dir)
    project = analyzer.analyze_project()
    
    print("\n" + "=" * 60)
    print("High Complexity Functions (>10)")
    print("=" * 60)
    
    for file_metrics in project.files:
        high_complexity = [c for c in file_metrics.complexity if c.complexity > 10]
        if high_complexity:
            print(f"\n{Path(file_metrics.file_path).name}:")
            for comp in high_complexity:
                print(f"  Line {comp.line_number}: {comp.function_name} (complexity: {comp.complexity})")
    
    # Cleanup
    shutil.rmtree(temp_dir)

def example_exclude_patterns():
    """Demonstrate exclude patterns"""
    temp_dir = tempfile.mkdtemp()
    create_sample_project(temp_dir)
    
    # Create a test directory that should be excluded
    test_dir = os.path.join(temp_dir, "tests")
    os.makedirs(test_dir)
    with open(os.path.join(test_dir, "test_sample.py"), 'w') as f:
        f.write("def test(): pass\n")
    
    print("\n" + "=" * 60)
    print("Exclude Patterns")
    print("=" * 60)
    
    # With exclusion
    analyzer = CodeMetricsAnalyzer(temp_dir, exclude_patterns=["*test*"])
    files = analyzer.get_python_files()
    
    print(f"\nFiles found (excluding *test*): {len(files)}")
    for f in files:
        print(f"  - {f.name}")
    
    # Without exclusion
    analyzer2 = CodeMetricsAnalyzer(temp_dir)
    files2 = analyzer2.get_python_files()
    
    print(f"\nFiles found (no exclusion): {len(files2)}")
    for f in files2:
        print(f"  - {f.name}")
    
    # Cleanup
    shutil.rmtree(temp_dir)

def example_line_counting():
    """Demonstrate detailed line counting"""
    temp_dir = tempfile.mkdtemp()
    create_sample_project(temp_dir)
    
    analyzer = CodeMetricsAnalyzer(temp_dir)
    file_path = Path(os.path.join(temp_dir, "src", "module.py"))
    
    print("\n" + "=" * 60)
    print("Detailed Line Counting")
    print("=" * 60)
    
    metrics = analyzer.count_lines(file_path)
    
    print(f"\nTotal Lines: {metrics.total_lines}")
    print(f"Code Lines: {metrics.code_lines}")
    print(f"Blank Lines: {metrics.blank_lines}")
    print(f"Comment Lines: {metrics.comment_lines}")
    print(f"Docstring Lines: {metrics.docstring_lines}")
    print(f"Comment Ratio: {metrics.comment_ratio:.1f}%")
    
    # Cleanup
    shutil.rmtree(temp_dir)

def example_quality_trends():
    """Demonstrate tracking quality over time (conceptual)"""
    temp_dir = tempfile.mkdtemp()
    create_sample_project(temp_dir)
    
    analyzer = CodeMetricsAnalyzer(temp_dir)
    project = analyzer.analyze_project()
    
    print("\n" + "=" * 60)
    print("Quality Assessment")
    print("=" * 60)
    
    quality = project.quality_score
    
    if quality >= 80:
        rating = "Excellent"
        color = "🟢"
    elif quality >= 60:
        rating = "Good"
        color = "🟡"
    elif quality >= 40:
        rating = "Fair"
        color = "🟠"
    else:
        rating = "Poor"
        color = "🔴"
    
    print(f"\nOverall Quality Score: {quality:.1f}/100")
    print(f"Rating: {color} {rating}")
    
    # Recommendations
    print("\nRecommendations:")
    if project.high_complexity_functions > 0:
        print(f"  - Refactor {project.high_complexity_functions} high-complexity functions")
    if project.duplicate_blocks > 0:
        print(f"  - Eliminate {project.duplicate_blocks} duplicate code blocks")
    if quality < 60:
        print("  - Add more comments and documentation")
        print("  - Consider breaking down large files")
    
    # Cleanup
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("=" * 60)
    print("Code Metrics Skill Examples")
    print("=" * 60)
    
    print("\n1. Single File Analysis:")
    example_single_file_analysis()
    
    print("\n2. Project Analysis:")
    example_project_analysis()
    
    print("\n3. Text Report:")
    example_text_report()
    
    print("\n4. JSON Report:")
    example_json_report()
    
    print("\n5. Complexity Threshold:")
    example_complexity_threshold()
    
    print("\n6. Exclude Patterns:")
    example_exclude_patterns()
    
    print("\n7. Line Counting:")
    example_line_counting()
    
    print("\n8. Quality Assessment:")
    example_quality_trends()
