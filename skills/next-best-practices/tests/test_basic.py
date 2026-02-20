#!/usr/bin/env python3
"""
Basic tests for Next.js Best Practices Checker
Run with: python tests/test_basic.py
"""

import os
import sys
import tempfile
import json
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import NextJSBestPracticesChecker, CheckStatus, Severity, CheckResult


def create_test_file(base_dir: Path, rel_path: str, content: str = ""):
    """Helper to create test files"""
    file_path = base_dir / rel_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return file_path


def test_empty_project():
    """Test structure check on empty directory"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        checker = NextJSBestPracticesChecker(str(temp_dir))
        checker._check_structure()
        
        assert "structure" in checker.results
        category = checker.results["structure"]
        assert category.status in [CheckStatus.WARNING, CheckStatus.FAIL]
        print("[OK] test_empty_project passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_valid_app_structure():
    """Test with valid App Router project"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        create_test_file(temp_dir, "app/layout.tsx", "export default function Layout() {}")
        create_test_file(temp_dir, "app/page.tsx", "")
        create_test_file(temp_dir, "app/globals.css", "")
        create_test_file(temp_dir, "components/Button.tsx", "")
        create_test_file(temp_dir, "lib/utils.ts", "")
        create_test_file(temp_dir, "next.config.js", "module.exports = {}")
        create_test_file(temp_dir, "package.json", "{}")
        
        checker = NextJSBestPracticesChecker(str(temp_dir))
        checker._check_structure()
        
        assert "structure" in checker.results
        passing = [item for item in checker.results["structure"].items if item.status == CheckStatus.PASS]
        assert len(passing) > 0
        print("[OK] test_valid_app_structure passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_pages_router_detection():
    """Test detection of Pages Router"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        create_test_file(temp_dir, "pages/index.tsx", "")
        create_test_file(temp_dir, "pages/_app.tsx", "")
        
        checker = NextJSBestPracticesChecker(str(temp_dir))
        checker._check_structure()
        
        warning_items = [item for item in checker.results["structure"].items 
                        if item.status == CheckStatus.WARNING and "Pages Router" in item.message]
        assert len(warning_items) > 0
        print("[OK] test_pages_router_detection passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_app_router_patterns():
    """Test App Router specific patterns"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        create_test_file(temp_dir, "app/layout.tsx", "")
        create_test_file(temp_dir, "app/blog/[slug]/page.tsx", "")
        create_test_file(temp_dir, "app/(marketing)/about/page.tsx", "")
        
        checker = NextJSBestPracticesChecker(str(temp_dir))
        checker._check_app_router()
        
        assert "appRouter" in checker.results
        print("[OK] test_app_router_patterns passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_performance_image_check():
    """Test image optimization check"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        create_test_file(temp_dir, "components/ImageGallery.tsx", 
            "import Image from 'next/image'\nexport default function Gallery() {}")
        
        checker = NextJSBestPracticesChecker(str(temp_dir))
        checker._check_performance()
        
        assert "performance" in checker.results
        print("[OK] test_performance_image_check passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_performance_native_img_warning():
    """Test warning for native img tags"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        create_test_file(temp_dir, "components/BadImage.tsx", 
            '<img src="/photo.jpg" alt="test" />')
        
        checker = NextJSBestPracticesChecker(str(temp_dir))
        checker._check_performance()
        
        warning_items = [item for item in checker.results["performance"].items 
                        if item.status == CheckStatus.WARNING and "img" in item.message]
        assert len(warning_items) > 0
        print("[OK] test_performance_native_img_warning passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_seo_metadata_check():
    """Test SEO metadata check"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        create_test_file(temp_dir, "app/layout.tsx", 
            "export const metadata = { title: 'My App' }")
        
        checker = NextJSBestPracticesChecker(str(temp_dir))
        checker._check_seo()
        
        assert "seo" in checker.results
        print("[OK] test_seo_metadata_check passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_seo_robots_sitemap():
    """Test robots.txt and sitemap detection"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        create_test_file(temp_dir, "robots.txt", "User-agent: *\nAllow: /")
        create_test_file(temp_dir, "sitemap.ts", "")
        
        checker = NextJSBestPracticesChecker(str(temp_dir))
        checker._check_seo()
        
        category = checker.results["seo"]
        robots_items = [item for item in category.items if "robots.txt" in item.name]
        sitemap_items = [item for item in category.items if "Sitemap" in item.name]
        assert len(robots_items) > 0
        assert len(sitemap_items) > 0
        print("[OK] test_seo_robots_sitemap passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_caching_fetch_config():
    """Test fetch cache configuration check"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        create_test_file(temp_dir, "app/page.tsx", 
            "const data = await fetch('url', { cache: 'force-cache' })")
        
        checker = NextJSBestPracticesChecker(str(temp_dir))
        checker._check_caching()
        
        assert "caching" in checker.results
        print("[OK] test_caching_fetch_config passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_code_patterns_client_directive():
    """Test 'use client' directive detection"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        create_test_file(temp_dir, "components/ClientButton.tsx", 
            "'use client'\nimport { useState } from 'react'")
        
        checker = NextJSBestPracticesChecker(str(temp_dir))
        checker._check_code_patterns()
        
        assert "codePatterns" in checker.results
        print("[OK] test_code_patterns_client_directive passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_code_patterns_suspense():
    """Test Suspense usage detection"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        create_test_file(temp_dir, "app/layout.tsx", 
            "import { Suspense } from 'react'")
        
        checker = NextJSBestPracticesChecker(str(temp_dir))
        checker._check_code_patterns()
        
        suspense_items = [item for item in checker.results["codePatterns"].items if "Suspense" in item.name]
        assert len(suspense_items) > 0
        print("[OK] test_code_patterns_suspense passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_full_check_run():
    """Test running all checks"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        create_test_file(temp_dir, "app/layout.tsx", 
            "export const metadata = { title: 'Test' }\n"
            "export default function Layout({ children }) { return children }")
        create_test_file(temp_dir, "app/page.tsx", "")
        create_test_file(temp_dir, "app/loading.tsx", "")
        create_test_file(temp_dir, "components/Image.tsx", 
            "import Image from 'next/image'\nexport default Image")
        create_test_file(temp_dir, "next.config.js", "module.exports = { images: { domains: [] } }")
        
        checker = NextJSBestPracticesChecker(str(temp_dir))
        results = checker.run_check("all")
        
        assert "summary" in results
        assert "checks" in results
        assert results["summary"]["total"] > 0
        print("[OK] test_full_check_run passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_json_output():
    """Test JSON output format"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        create_test_file(temp_dir, "app/layout.tsx", "")
        
        checker = NextJSBestPracticesChecker(str(temp_dir))
        results = checker.run_check("structure")
        
        json_str = json.dumps(results, indent=2)
        assert json_str is not None
        assert len(json_str) > 0
        
        parsed = json.loads(json_str)
        assert "summary" in parsed
        print("[OK] test_json_output passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_severity_filtering():
    """Test that severity filtering works"""
    checker = NextJSBestPracticesChecker(".", Severity.ERROR)
    assert checker.min_severity == Severity.ERROR
    print("[OK] test_severity_filtering passed")


def test_check_result_creation():
    """Test creating a CheckResult"""
    result = CheckResult(
        name="Test Check",
        status=CheckStatus.PASS,
        message="Test passed",
        severity=Severity.INFO
    )
    
    assert result.name == "Test Check"
    assert result.status == CheckStatus.PASS
    assert result.message == "Test passed"
    assert result.severity == Severity.INFO
    print("[OK] test_check_result_creation passed")


def run_all_tests():
    """Run all tests"""
    print("Running Next.js Best Practices Checker Tests...")
    print("=" * 50)
    
    tests = [
        test_empty_project,
        test_valid_app_structure,
        test_pages_router_detection,
        test_app_router_patterns,
        test_performance_image_check,
        test_performance_native_img_warning,
        test_seo_metadata_check,
        test_seo_robots_sitemap,
        test_caching_fetch_config,
        test_code_patterns_client_directive,
        test_code_patterns_suspense,
        test_full_check_run,
        test_json_output,
        test_severity_filtering,
        test_check_result_creation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
