#!/usr/bin/env python3
"""
Next.js Best Practices Checker
A comprehensive tool for analyzing Next.js projects with focus on App Router architecture.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUGGESTION = "suggestion"


class CheckStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    INFO = "info"
    SUGGESTION = "suggestion"


@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    message: str
    severity: Severity = Severity.INFO
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class CheckCategory:
    name: str
    status: CheckStatus
    items: List[CheckResult] = field(default_factory=list)


class NextJSBestPracticesChecker:
    """Main checker class for Next.js best practices."""
    
    def __init__(self, project_path: str, min_severity: Severity = Severity.WARNING):
        self.project_path = Path(project_path).resolve()
        self.min_severity = min_severity
        self.results: Dict[str, CheckCategory] = {}
        
    def run_check(self, check_type: str = "all") -> Dict[str, Any]:
        """Run specified check type."""
        checks = {
            "structure": self._check_structure,
            "app-router": self._check_app_router,
            "performance": self._check_performance,
            "seo": self._check_seo,
            "caching": self._check_caching,
            "code-patterns": self._check_code_patterns
        }
        
        if check_type == "all":
            for check_func in checks.values():
                check_func()
        elif check_type in checks:
            checks[check_type]()
            
        return self._format_results()
    
    def _check_structure(self) -> None:
        items = []
        app_dir = self.project_path / "app"
        
        if app_dir.exists():
            items.append(CheckResult("App Directory", CheckStatus.PASS,
                "[OK] app/ directory exists (using App Router)", Severity.INFO))
            
            for filename, desc in [("layout.tsx", "Root layout"), ("page.tsx", "Home page"), ("globals.css", "Global styles")]:
                if (app_dir / filename).exists():
                    items.append(CheckResult(f"Essential: {desc}", CheckStatus.PASS,
                        f"[OK] {filename} found", Severity.INFO))
                else:
                    items.append(CheckResult(f"Essential: {desc}", CheckStatus.WARNING,
                        f"[WARN]  Missing {filename}", Severity.WARNING, suggestion=f"Create app/{filename}"))
            
            for filename, desc in [("error.tsx", "Error handling"), ("loading.tsx", "Loading state")]:
                if (app_dir / filename).exists():
                    items.append(CheckResult(desc, CheckStatus.PASS, f"[OK] {filename} found", Severity.INFO))
                else:
                    items.append(CheckResult(desc, CheckStatus.SUGGESTION,
                        f"[TIP] Consider adding {filename}", Severity.SUGGESTION))
        else:
            pages_dir = self.project_path / "pages"
            if pages_dir.exists():
                items.append(CheckResult("App Directory", CheckStatus.WARNING,
                    "[WARN]  Using Pages Router (legacy), consider migrating to App Router", Severity.WARNING))
            else:
                items.append(CheckResult("App Directory", CheckStatus.FAIL,
                    "[ERR] No app/ or pages/ directory found", Severity.ERROR))
        
        for dirname, desc in [("components", "React components"), ("lib", "Utility functions"), ("public", "Static assets")]:
            if (self.project_path / dirname).exists():
                items.append(CheckResult(f"Directory: {dirname}/", CheckStatus.PASS,
                    f"[OK] {dirname}/ directory exists ({desc})", Severity.INFO))
            else:
                items.append(CheckResult(f"Directory: {dirname}/", CheckStatus.SUGGESTION,
                    f"[TIP] Consider adding {dirname}/ directory ({desc})", Severity.SUGGESTION))
        
        for filename in ["next.config.js", "next.config.ts", "tsconfig.json", "package.json"]:
            if (self.project_path / filename).exists():
                items.append(CheckResult(f"Config: {filename}", CheckStatus.PASS, f"[OK] {filename} found", Severity.INFO))
        
        self.results["structure"] = CheckCategory("Project Structure", self._determine_status(items), items)
    
    def _check_app_router(self) -> None:
        items = []
        app_dir = self.project_path / "app"
        
        if not app_dir.exists():
            self.results["appRouter"] = CheckCategory("App Router", CheckStatus.FAIL,
                [CheckResult("App Router", CheckStatus.FAIL, "[ERR] App Router not found", Severity.ERROR)])
            return
        
        dynamic_routes = list(app_dir.rglob(r"*\[*\]*"))
        if dynamic_routes:
            items.append(CheckResult("Dynamic Routes", CheckStatus.PASS,
                f"[OK] Found {len(dynamic_routes)} dynamic route(s)", Severity.INFO))
        
        route_groups = [f for f in app_dir.rglob("*") if re.search(r'\([^)]+\)', str(f.name))]
        if route_groups:
            items.append(CheckResult("Route Groups", CheckStatus.PASS,
                f"[OK] Found {len(route_groups)} route group(s)", Severity.INFO))
        
        parallel_routes = list(app_dir.rglob("@*"))
        if parallel_routes:
            items.append(CheckResult("Parallel Routes", CheckStatus.PASS,
                f"[OK] Found {len(parallel_routes)} parallel route slot(s)", Severity.INFO))
        
        has_static_params = any("generateStaticParams" in (self._read_file(f) or "")
                                 for f in app_dir.rglob("*.tsx"))
        if has_static_params:
            items.append(CheckResult("Static Generation", CheckStatus.PASS,
                "[OK] Using generateStaticParams for SSG", Severity.INFO))
        
        configs = ["dynamic", "revalidate", "fetchCache", "runtime", "preferredRegion"]
        found = [c for c in configs if any(f"export const {c}" in (self._read_file(f) or "")
                                           for f in app_dir.rglob("*.tsx"))]
        if found:
            items.append(CheckResult("Route Segment Config", CheckStatus.PASS,
                f"[OK] Using route segment config: {', '.join(found)}", Severity.INFO))
        else:
            items.append(CheckResult("Route Segment Config", CheckStatus.SUGGESTION,
                "[TIP] Consider using route segment config", Severity.SUGGESTION,
                "Add export const dynamic/revalidate/fetchCache to route files"))
        
        self.results["appRouter"] = CheckCategory("App Router", self._determine_status(items), items)
    
    def _check_performance(self) -> None:
        items = []
        
        image_imports = self._search_files(["*.tsx", "*.ts"], r'from\s+["\']next/image["\']')
        img_tags = self._search_files(["*.tsx", "*.ts"], r'<img\s+[^>]*src=')
        
        if image_imports:
            items.append(CheckResult("Image Optimization", CheckStatus.PASS,
                f"[OK] Using next/image ({len(image_imports)} file(s))", Severity.INFO))
        if img_tags:
            items.append(CheckResult("Image Tags", CheckStatus.WARNING,
                f"[WARN]  Found {len(img_tags)} file(s) using native <img> tag", Severity.WARNING,
                "Replace <img> with next/image for automatic optimization"))
        
        font_imports = self._search_files(["*.tsx", "*.ts"], r'from\s+["\']next/font')
        if font_imports:
            items.append(CheckResult("Font Optimization", CheckStatus.PASS,
                f"[OK] Using next/font ({len(font_imports)} file(s))", Severity.INFO))
        else:
            items.append(CheckResult("Font Optimization", CheckStatus.SUGGESTION,
                "[TIP] Consider using next/font for font optimization", Severity.SUGGESTION))
        
        script_imports = self._search_files(["*.tsx", "*.ts"], r'from\s+["\']next/script["\']')
        if script_imports:
            items.append(CheckResult("Script Optimization", CheckStatus.PASS,
                f"[OK] Using next/script ({len(script_imports)} file(s))", Severity.INFO))
        
        external_scripts = self._search_files(["*.tsx", "*.ts"], r'<script\s+src="https?://')
        if external_scripts:
            items.append(CheckResult("External Scripts", CheckStatus.WARNING,
                f"[WARN]  Found {len(external_scripts)} file(s) with external scripts", Severity.WARNING,
                "Use next/script with appropriate strategy for external scripts"))
        
        config_file = self.project_path / "next.config.ts"
        if not config_file.exists():
            config_file = self.project_path / "next.config.js"
        
        if config_file.exists():
            content = self._read_file(config_file) or ""
            if "images" in content and ("domains" in content or "remotePatterns" in content):
                items.append(CheckResult("Image Domains Config", CheckStatus.PASS,
                    "[OK] Image domains configured in next.config", Severity.INFO))
            elif image_imports:
                items.append(CheckResult("Image Domains Config", CheckStatus.WARNING,
                    "[WARN]  Consider configuring image.domains in next.config", Severity.WARNING))
        
        self.results["performance"] = CheckCategory("Performance", self._determine_status(items), items)
    
    def _check_seo(self) -> None:
        items = []
        
        metadata = self._search_files(["*.tsx", "*.ts"], r'export\s+(const|let|var)\s+metadata')
        if metadata:
            items.append(CheckResult("Metadata API", CheckStatus.PASS,
                f"[OK] Using Metadata API ({len(metadata)} file(s))", Severity.INFO))
        else:
            items.append(CheckResult("Metadata API", CheckStatus.WARNING,
                "[WARN]  No Metadata API usage found", Severity.WARNING, "Export metadata object for SEO"))
        
        og_usage = self._search_files(["*.tsx", "*.ts"], r'openGraph|twitter|og:')
        if og_usage:
            items.append(CheckResult("Social Meta Tags", CheckStatus.PASS,
                "[OK] OpenGraph/Twitter Card tags configured", Severity.INFO))
        
        if (self.project_path / "robots.txt").exists():
            items.append(CheckResult("robots.txt", CheckStatus.PASS, "[OK] robots.txt found", Severity.INFO))
        else:
            items.append(CheckResult("robots.txt", CheckStatus.SUGGESTION,
                "[TIP] Consider adding robots.txt", Severity.SUGGESTION))
        
        has_sitemap = any((self.project_path / f).exists() for f in ["sitemap.xml", "sitemap.ts", "sitemap.js"])
        if has_sitemap:
            items.append(CheckResult("Sitemap", CheckStatus.PASS, "[OK] Sitemap found", Severity.INFO))
        else:
            items.append(CheckResult("Sitemap", CheckStatus.SUGGESTION,
                "[TIP] Consider adding sitemap.xml or sitemap.ts", Severity.SUGGESTION,
                "Create sitemap.ts in app/ for automatic generation"))
        
        jsonld = self._search_files(["*.tsx", "*.ts"], r'application/ld\+json|jsonld|structuredData')
        if jsonld:
            items.append(CheckResult("Structured Data", CheckStatus.PASS,
                "[OK] JSON-LD structured data found", Severity.INFO))
        
        self.results["seo"] = CheckCategory("SEO", self._determine_status(items), items)
    
    def _check_caching(self) -> None:
        items = []
        app_dir = self.project_path / "app"
        
        if not app_dir.exists():
            self.results["caching"] = CheckCategory("Caching", CheckStatus.FAIL,
                [CheckResult("Caching", CheckStatus.FAIL, "[ERR] App directory not found", Severity.ERROR)])
            return
        
        fetch_cache = self._search_files(["*.tsx", "*.ts"],
            r'cache:\s*["\'](force-cache|no-store|reload|no-cache|only-if-cached)["\']')
        if fetch_cache:
            items.append(CheckResult("Fetch Cache", CheckStatus.PASS,
                f"[OK] Explicit fetch cache config ({len(fetch_cache)} file(s))", Severity.INFO))
        
        revalidate = self._search_files(["*.tsx", "*.ts"], r'revalidate:\s*\d+|next:\s*\{\s*revalidate')
        if revalidate:
            items.append(CheckResult("ISR Revalidation", CheckStatus.PASS,
                f"[OK] ISR revalidation configured ({len(revalidate)} file(s))", Severity.INFO))
        
        dynamic = self._search_files(["*.tsx", "*.ts"],
            r'export\s+const\s+dynamic\s*=\s*["\'](auto|force-dynamic|error|force-static)["\']')
        if dynamic:
            items.append(CheckResult("Dynamic Export", CheckStatus.PASS,
                f"[OK] Dynamic export configured ({len(dynamic)} file(s))", Severity.INFO))
        
        fetch_calls = self._search_files(["*.tsx", "*.ts"], r'await\s+fetch\s*\(')
        if fetch_calls and not fetch_cache:
            items.append(CheckResult("Fetch Cache Config", CheckStatus.SUGGESTION,
                "[TIP] Consider adding explicit cache configuration to fetch calls", Severity.SUGGESTION,
                "Use cache: 'force-cache' or cache: 'no-store' explicitly"))
        
        unstable = self._search_files(["*.tsx", "*.ts"], r'unstable_cache|unstable_noStore')
        if unstable:
            items.append(CheckResult("Advanced Caching", CheckStatus.PASS,
                "[OK] Using unstable_cache for fine-grained caching", Severity.INFO))
        
        self.results["caching"] = CheckCategory("Caching", self._determine_status(items), items)
    
    def _check_code_patterns(self) -> None:
        items = []
        
        client_directives = self._search_files(["*.tsx", "*.ts"], r'["\']use client["\']')
        if client_directives:
            items.append(CheckResult("Client Components", CheckStatus.PASS,
                f"[OK] Found {len(client_directives)} Client Component(s)", Severity.INFO))
        
        server_directives = self._search_files(["*.tsx", "*.ts"], r'["\']use server["\']')
        if server_directives:
            items.append(CheckResult("Server Actions", CheckStatus.PASS,
                f"[OK] Found {len(server_directives)} Server Action(s)", Severity.INFO))
        
        suspense = self._search_files(["*.tsx", "*.ts"], r'<Suspense|from\s+["\']react["\'].*Suspense')
        if suspense:
            items.append(CheckResult("Streaming with Suspense", CheckStatus.PASS,
                f"[OK] Using Suspense for streaming ({len(suspense)} file(s))", Severity.INFO))
        else:
            items.append(CheckResult("Streaming with Suspense", CheckStatus.SUGGESTION,
                "[TIP] Consider using Suspense for better loading UX", Severity.SUGGESTION,
                "Wrap slow components with <Suspense fallback={<Loading />} />"))
        
        async_comps = self._search_files(["*.tsx", "*.ts"], r'export\s+(default\s+)?async\s+function\s+\w+')
        if async_comps:
            items.append(CheckResult("Async Server Components", CheckStatus.PASS,
                f"[OK] Found {len(async_comps)} async Server Component(s)", Severity.INFO))
        
        hooks = self._search_files(["*.tsx", "*.ts"],
            r'useState|useEffect|useContext|useReducer|useCallback|useMemo')
        if hooks:
            items.append(CheckResult("React Hooks", CheckStatus.INFO,
                f"[OK] Found {len(hooks)} file(s) using React hooks", Severity.INFO))
        
        self.results["codePatterns"] = CheckCategory("Code Patterns", self._determine_status(items), items)
    
    def _search_files(self, patterns: List[str], regex: str) -> List[Tuple[Path, int]]:
        results = []
        compiled = re.compile(regex)
        for pattern in patterns:
            for file_path in self.project_path.rglob(pattern):
                if "node_modules" in str(file_path):
                    continue
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if compiled.search(content):
                        results.append((file_path.relative_to(self.project_path), len(compiled.findall(content))))
                except Exception:
                    continue
        return results
    
    def _read_file(self, file_path: Path) -> Optional[str]:
        try:
            return file_path.read_text(encoding="utf-8")
        except Exception:
            return None
    
    def _determine_status(self, items: List[CheckResult]) -> CheckStatus:
        if not items:
            return CheckStatus.INFO
        has_errors = any(item.status == CheckStatus.FAIL for item in items)
        has_warnings = any(item.status == CheckStatus.WARNING for item in items)
        if has_errors:
            return CheckStatus.FAIL
        elif has_warnings:
            return CheckStatus.WARNING
        return CheckStatus.PASS
    
    def _format_results(self) -> Dict[str, Any]:
        total = passed = warnings = errors = 0
        formatted = {}
        
        for key, category in self.results.items():
            cat_items = []
            for item in category.items:
                total += 1
                if item.status == CheckStatus.PASS:
                    passed += 1
                elif item.status == CheckStatus.WARNING:
                    warnings += 1
                elif item.status == CheckStatus.FAIL:
                    errors += 1
                
                cat_items.append({
                    "name": item.name,
                    "status": item.status.value,
                    "message": item.message,
                    "severity": item.severity.value,
                    "file_path": item.file_path,
                    "line_number": item.line_number,
                    "suggestion": item.suggestion
                })
            
            formatted[key] = {"name": category.name, "status": category.status.value, "items": cat_items}
        
        return {
            "summary": {"total": total, "passed": passed, "warnings": warnings, "errors": errors},
            "checks": formatted
        }


def print_console(results: Dict[str, Any]) -> None:
    print("\n[Next.js Best Practices Check]")
    print("=" * 50)
    
    emojis = {"structure": "[STRUCT]", "appRouter": "[APP]", "performance": "[PERF]", "seo": "[SEO]", "caching": "[CACHE]", "codePatterns": "[CODE]"}
    names = {"structure": "Project Structure", "appRouter": "App Router", "performance": "Performance",
             "seo": "SEO", "caching": "Caching", "codePatterns": "Code Patterns"}
    
    for key, category in results["checks"].items():
        print(f"\n{emojis.get(key, '•')} {names.get(key, category['name'])}")
        for item in category["items"]:
            print(f"  {item['message']}")
            if item.get("suggestion"):
                print(f"     [TIP] {item['suggestion']}")
    
    print("\n" + "=" * 50)
    s = results["summary"]
    print(f"Results: {s['passed']} passed, {s['warnings']} warnings, {s['errors']} errors")


def print_markdown(results: Dict[str, Any]) -> None:
    print("# Next.js Best Practices Report\n")
    s = results["summary"]
    print(f"## Summary\n")
    print(f"- **Total Checks**: {s['total']}")
    print(f"- **Passed**: {s['passed']} [OK]")
    print(f"- **Warnings**: {s['warnings']} [WARN]")
    print(f"- **Errors**: {s['errors']} [ERR]\n")
    
    for key, category in results["checks"].items():
        print(f"## {category['name']}\n")
        for item in category["items"]:
            icon = "[OK]" if item["status"] == "pass" else "[WARN]" if item["status"] == "warning" else "[ERR]" if item["status"] == "fail" else "[TIP]"
            print(f"### {icon} {item['name']}\n")
            print(f"{item['message']}\n")
            if item.get("suggestion"):
                print(f"**Suggestion**: {item['suggestion']}\n")


def main():
    parser = argparse.ArgumentParser(description="Next.js Best Practices Checker")
    parser.add_argument("--action", type=str, required=True, choices=["check", "fix", "suggest", "analyze"])
    parser.add_argument("--file-path", type=str, default=".", help="Path to file or directory")
    parser.add_argument("--check-type", type=str, default="all",
                        choices=["all", "structure", "performance", "seo", "caching", "app-router", "code-patterns"])
    parser.add_argument("--output-format", type=str, default="console", choices=["json", "markdown", "console"])
    parser.add_argument("--severity", type=str, default="warning", choices=["error", "warning", "info", "suggestion"])
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        print(f"Error: Path '{args.file_path}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    severity_map = {"error": Severity.ERROR, "warning": Severity.WARNING, "info": Severity.INFO, "suggestion": Severity.SUGGESTION}
    checker = NextJSBestPracticesChecker(args.file_path, severity_map.get(args.severity, Severity.WARNING))
    results = checker.run_check(args.check_type)
    
    if args.output_format == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
    elif args.output_format == "markdown":
        print_markdown(results)
    else:
        print_console(results)
    
    sys.exit(1 if results["summary"]["errors"] > 0 else 0)


if __name__ == "__main__":
    main()
