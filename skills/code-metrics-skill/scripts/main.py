#!/usr/bin/env python3
"""
Code Quality Metrics Skill
Supports: cyclomatic complexity, line counts, duplicate code detection, quality scoring
"""

import os
import sys
import json
import argparse
import ast
import hashlib
import re
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict, field
from pathlib import Path
from collections import defaultdict
import fnmatch

# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ComplexityMetrics:
    """Cyclomatic complexity metrics"""
    function_name: str
    line_number: int
    complexity: int
    classification: str  # low, medium, high, very high
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class LineMetrics:
    """Line count metrics"""
    total_lines: int = 0
    code_lines: int = 0
    blank_lines: int = 0
    comment_lines: int = 0
    docstring_lines: int = 0
    
    @property
    def comment_ratio(self) -> float:
        if self.code_lines == 0:
            return 0.0
        return (self.comment_lines + self.docstring_lines) / self.code_lines * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_lines": self.total_lines,
            "code_lines": self.code_lines,
            "blank_lines": self.blank_lines,
            "comment_lines": self.comment_lines,
            "docstring_lines": self.docstring_lines,
            "comment_ratio": round(self.comment_ratio, 2)
        }

@dataclass
class DuplicateBlock:
    """Duplicate code block information"""
    hash_value: str
    code_snippet: str
    occurrences: List[Tuple[str, int]]  # (file_path, line_number)
    line_count: int

@dataclass
class FileMetrics:
    """Complete metrics for a single file"""
    file_path: str
    file_size: int = 0
    lines: LineMetrics = field(default_factory=LineMetrics)
    complexity: List[ComplexityMetrics] = field(default_factory=list)
    duplicates: List[DuplicateBlock] = field(default_factory=list)
    maintainability_index: float = 0.0
    quality_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "file_size": self.file_size,
            "lines": self.lines.to_dict(),
            "complexity": [c.to_dict() for c in self.complexity],
            "duplicate_count": len(self.duplicates),
            "maintainability_index": round(self.maintainability_index, 2),
            "quality_score": round(self.quality_score, 2)
        }

@dataclass
class ProjectMetrics:
    """Aggregate metrics for entire project"""
    total_files: int = 0
    total_lines: int = 0
    total_code_lines: int = 0
    avg_complexity: float = 0.0
    max_complexity: int = 0
    high_complexity_functions: int = 0
    duplicate_blocks: int = 0
    quality_score: float = 0.0
    files: List[FileMetrics] = field(default_factory=list)

# ============================================================================
# Code Metrics Analyzer
# ============================================================================

class CodeMetricsAnalyzer:
    """Main class for analyzing code metrics"""
    
    def __init__(self, project_path: str, exclude_patterns: List[str] = None):
        self.project_path = Path(project_path).resolve()
        self.exclude_patterns = exclude_patterns or [
            "*venv*", "*node_modules*", "*.git*", "*__pycache__*",
            "*test*", "*tests*", "*build*", "*dist*", "*.egg-info*"
        ]
        self.duplicate_map: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        self.min_duplicate_lines = 5
    
    def should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded"""
        path_str = str(path)
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(path.name, pattern):
                return True
        return False
    
    def get_python_files(self) -> List[Path]:
        """Get all Python files in project"""
        files = []
        for py_file in self.project_path.rglob("*.py"):
            if not self.should_exclude(py_file):
                files.append(py_file)
        return files
    
    # ========================================================================
    # Line Counting
    # ========================================================================
    
    def count_lines(self, file_path: Path) -> LineMetrics:
        """Count lines in a Python file"""
        metrics = LineMetrics()
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception:
            return metrics
        
        metrics.total_lines = len(lines)
        in_docstring = False
        docstring_delimiter = None
        
        for line in lines:
            stripped = line.strip()
            
            # Check for docstring start/end
            if not in_docstring:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    if stripped.count('"""') == 1 or stripped.count("'''") == 1:
                        in_docstring = True
                        docstring_delimiter = '"""' if '"""' in stripped else "'''"
                    metrics.docstring_lines += 1
                elif stripped.startswith('#'):
                    metrics.comment_lines += 1
                elif stripped == '':
                    metrics.blank_lines += 1
                else:
                    metrics.code_lines += 1
            else:
                metrics.docstring_lines += 1
                if docstring_delimiter in stripped:
                    in_docstring = False
                    docstring_delimiter = None
        
        return metrics
    
    # ========================================================================
    # Cyclomatic Complexity
    # ========================================================================
    
    def calculate_complexity(self, file_path: Path) -> List[ComplexityMetrics]:
        """Calculate cyclomatic complexity for all functions in file"""
        complexities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            tree = ast.parse(content)
        except Exception:
            return complexities
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = self._count_complexity(node)
                classification = self._classify_complexity(complexity)
                
                complexities.append(ComplexityMetrics(
                    function_name=node.name,
                    line_number=node.lineno,
                    complexity=complexity,
                    classification=classification
                ))
        
        return complexities
    
    def _count_complexity(self, node: ast.AST) -> int:
        """Count cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (
                ast.If, ast.While, ast.For, ast.ExceptHandler,
                ast.With, ast.Assert, ast.comprehension
            )):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _classify_complexity(self, complexity: int) -> str:
        """Classify complexity level"""
        if complexity <= 5:
            return "low"
        elif complexity <= 10:
            return "medium"
        elif complexity <= 20:
            return "high"
        else:
            return "very high"
    
    # ========================================================================
    # Duplicate Detection
    # ========================================================================
    
    def find_duplicates(self, file_path: Path) -> List[DuplicateBlock]:
        """Find duplicate code blocks in file"""
        duplicates = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception:
            return duplicates
        
        # Create normalized code blocks
        for i in range(len(lines) - self.min_duplicate_lines + 1):
            block_lines = lines[i:i + self.min_duplicate_lines]
            normalized = self._normalize_code(''.join(block_lines))
            
            if normalized:
                hash_value = hashlib.md5(normalized.encode()).hexdigest()
                self.duplicate_map[hash_value].append((str(file_path), i + 1))
        
        return duplicates
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code for comparison"""
        # Remove comments
        code = re.sub(r'#.*', '', code)
        # Remove extra whitespace
        code = re.sub(r'\s+', ' ', code)
        # Strip and lowercase
        code = code.strip().lower()
        return code
    
    def get_duplicate_blocks(self) -> List[DuplicateBlock]:
        """Get all duplicate code blocks"""
        blocks = []
        
        for hash_value, occurrences in self.duplicate_map.items():
            if len(occurrences) > 1:
                # Get code snippet from first occurrence
                file_path, line_num = occurrences[0]
                try:
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                    snippet = ''.join(lines[line_num-1:line_num-1+self.min_duplicate_lines])
                except:
                    snippet = ""
                
                blocks.append(DuplicateBlock(
                    hash_value=hash_value,
                    code_snippet=snippet[:200],
                    occurrences=occurrences,
                    line_count=self.min_duplicate_lines
                ))
        
        return blocks
    
    # ========================================================================
    # Maintainability Index
    # ========================================================================
    
    def calculate_maintainability(self, lines: LineMetrics, 
                                   complexities: List[ComplexityMetrics]) -> float:
        """Calculate maintainability index (0-100)"""
        if lines.code_lines == 0:
            return 0.0
        
        # Simplified maintainability calculation
        avg_complexity = (sum(c.complexity for c in complexities) / len(complexities)) if complexities else 1
        comment_ratio = lines.comment_ratio
        
        # Higher is better
        score = 100
        score -= avg_complexity * 2  # Penalty for complexity
        score -= max(0, 20 - comment_ratio)  # Penalty for low comments
        score -= lines.code_lines / 100  # Penalty for large files
        
        return max(0, min(100, score))
    
    def calculate_quality_score(self, metrics: FileMetrics) -> float:
        """Calculate overall quality score (0-100)"""
        score = 100.0
        
        # Complexity penalty
        high_complexity = sum(1 for c in metrics.complexity if c.complexity > 10)
        score -= high_complexity * 5
        
        # Duplicate penalty
        score -= len(metrics.duplicates) * 10
        
        # File size penalty
        if metrics.lines.code_lines > 500:
            score -= 10
        if metrics.lines.code_lines > 1000:
            score -= 20
        
        # Comment ratio bonus/penalty
        if metrics.lines.comment_ratio < 10:
            score -= 10
        elif metrics.lines.comment_ratio > 30:
            score += 5
        
        # Maintainability factor
        score = score * (metrics.maintainability_index / 100)
        
        return max(0, min(100, score))
    
    # ========================================================================
    # Analysis
    # ========================================================================
    
    def analyze_file(self, file_path: Path) -> FileMetrics:
        """Analyze a single file"""
        metrics = FileMetrics(file_path=str(file_path))
        metrics.file_size = file_path.stat().st_size
        
        # Line counts
        metrics.lines = self.count_lines(file_path)
        
        # Complexity
        metrics.complexity = self.calculate_complexity(file_path)
        
        # Duplicates (will be populated later)
        metrics.duplicates = []
        
        # Maintainability
        metrics.maintainability_index = self.calculate_maintainability(
            metrics.lines, metrics.complexity
        )
        
        # Quality score
        metrics.quality_score = self.calculate_quality_score(metrics)
        
        return metrics
    
    def analyze_project(self) -> ProjectMetrics:
        """Analyze entire project"""
        project = ProjectMetrics()
        files = self.get_python_files()
        
        # First pass: analyze each file and collect duplicates
        for file_path in files:
            file_metrics = self.analyze_file(file_path)
            self.find_duplicates(file_path)
            project.files.append(file_metrics)
        
        # Get all duplicates
        all_duplicates = self.get_duplicate_blocks()
        
        # Assign duplicates to files
        for dup in all_duplicates:
            for file_path, _ in dup.occurrences:
                for fm in project.files:
                    if fm.file_path == file_path:
                        fm.duplicates.append(dup)
        
        # Calculate aggregate metrics
        project.total_files = len(project.files)
        project.total_lines = sum(f.lines.total_lines for f in project.files)
        project.total_code_lines = sum(f.lines.code_lines for f in project.files)
        
        all_complexities = [c.complexity for f in project.files for c in f.complexity]
        if all_complexities:
            project.avg_complexity = sum(all_complexities) / len(all_complexities)
            project.max_complexity = max(all_complexities)
        
        project.high_complexity_functions = sum(
            1 for f in project.files for c in f.complexity if c.complexity > 10
        )
        project.duplicate_blocks = len(all_duplicates)
        
        # Overall quality score
        if project.files:
            project.quality_score = sum(f.quality_score for f in project.files) / len(project.files)
        
        return project
    
    # ========================================================================
    # Reporting
    # ========================================================================
    
    def generate_report(self, project: ProjectMetrics, format: str = "text") -> str:
        """Generate analysis report"""
        if format == "json":
            return json.dumps({
                "summary": {
                    "total_files": project.total_files,
                    "total_lines": project.total_lines,
                    "total_code_lines": project.total_code_lines,
                    "avg_complexity": round(project.avg_complexity, 2),
                    "max_complexity": project.max_complexity,
                    "high_complexity_functions": project.high_complexity_functions,
                    "duplicate_blocks": project.duplicate_blocks,
                    "quality_score": round(project.quality_score, 2)
                },
                "files": [f.to_dict() for f in project.files]
            }, indent=2)
        
        # Text format
        lines = []
        lines.append("=" * 60)
        lines.append("CODE QUALITY METRICS REPORT")
        lines.append("=" * 60)
        lines.append("")
        lines.append("SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Total Files: {project.total_files}")
        lines.append(f"Total Lines: {project.total_lines:,}")
        lines.append(f"Code Lines: {project.total_code_lines:,}")
        lines.append(f"Average Complexity: {project.avg_complexity:.2f}")
        lines.append(f"Max Complexity: {project.max_complexity}")
        lines.append(f"High Complexity Functions: {project.high_complexity_functions}")
        lines.append(f"Duplicate Blocks: {project.duplicate_blocks}")
        lines.append(f"Overall Quality Score: {project.quality_score:.1f}/100")
        lines.append("")
        
        # Top complex files
        lines.append("TOP 10 MOST COMPLEX FILES")
        lines.append("-" * 40)
        sorted_files = sorted(
            project.files,
            key=lambda f: max((c.complexity for c in f.complexity), default=0),
            reverse=True
        )[:10]
        
        for fm in sorted_files:
            max_comp = max((c.complexity for c in fm.complexity), default=0)
            lines.append(f"  {fm.file_path}: max complexity = {max_comp}")
        
        lines.append("")
        
        # Lowest quality files
        lines.append("TOP 10 LOWEST QUALITY FILES")
        lines.append("-" * 40)
        sorted_by_quality = sorted(project.files, key=lambda f: f.quality_score)[:10]
        
        for fm in sorted_by_quality:
            lines.append(f"  {fm.file_path}: score = {fm.quality_score:.1f}")
        
        lines.append("")
        lines.append("=" * 60)
        
        return '\n'.join(lines)

# ============================================================================
# CLI Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Code Quality Metrics Analyzer")
    parser.add_argument("path", nargs="?", default=".", help="Project path")
    parser.add_argument("--exclude", action="append", help="Exclude patterns")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format")
    parser.add_argument("--output", help="Output file")
    parser.add_argument("--min-complexity", type=int, default=10,
                        help="Min complexity to report")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Analyze single file
    file_parser = subparsers.add_parser("analyze-file", help="Analyze single file")
    file_parser.add_argument("file", help="Python file to analyze")
    
    # Show complexity
    subparsers.add_parser("complexity", help="Show complexity report")
    
    # Show duplicates
    subparsers.add_parser("duplicates", help="Show duplicate code")
    
    args = parser.parse_args()
    
    exclude_patterns = args.exclude or []
    
    if args.command == "analyze-file":
        analyzer = CodeMetricsAnalyzer(os.path.dirname(args.file) or ".", exclude_patterns)
        metrics = analyzer.analyze_file(Path(args.file))
        print(json.dumps(metrics.to_dict(), indent=2))
        return
    
    # Full project analysis
    analyzer = CodeMetricsAnalyzer(args.path, exclude_patterns)
    
    print("Analyzing project...")
    project = analyzer.analyze_project()
    
    report = analyzer.generate_report(project, args.format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)

if __name__ == "__main__":
    main()
