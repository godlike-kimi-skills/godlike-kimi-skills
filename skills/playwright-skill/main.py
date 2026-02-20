#!/usr/bin/env python3
"""
Playwright Automation Testing Skill

Playwright自动化测试智能助手。Use when writing tests, automating testing, 
or when user mentions 'Playwright', 'browser automation', 'multi-browser testing', 'visual regression testing'.

Capabilities:
- 测试生成: 自动生成Playwright测试代码
- 多浏览器支持: Chromium、Firefox、WebKit
- 截图对比: 视觉回归测试
- 测试录制: 代码生成器支持
- API测试: 网络拦截和API测试
- 移动仿真: 移动设备模拟
"""

import json
import re
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from pathlib import Path
from datetime import datetime
from enum import Enum


class BrowserType(str, Enum):
    """浏览器类型"""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class DeviceType(str, Enum):
    """设备类型"""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"


@dataclass
class TestStep:
    """测试步骤"""
    action: str  # goto, click, fill, select, wait, screenshot, etc.
    selector: Optional[str] = None
    value: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)
    
    def to_playwright_code(self, use_async: bool = False) -> str:
        """转换为Playwright代码"""
        await_prefix = "await " if use_async else ""
        
        if self.action == "goto":
            return f"{await_prefix}page.goto('{self.value}')"
        elif self.action == "click":
            opts = self._format_options(["force", "timeout", "delay"])
            return f"{await_prefix}page.click('{self.selector}'{opts})"
        elif self.action == "fill":
            return f"{await_prefix}page.fill('{self.selector}', '{self.value}')"
        elif self.action == "type":
            opts = self._format_options(["delay"])
            return f"{await_prefix}page.type('{self.selector}', '{self.value}'{opts})"
        elif self.action == "select":
            return f"{await_prefix}page.selectOption('{self.selector}', '{self.value}')"
        elif self.action == "check":
            return f"{await_prefix}page.check('{self.selector}')"
        elif self.action == "uncheck":
            return f"{await_prefix}page.uncheck('{self.selector}')"
        elif self.action == "wait":
            if self.selector:
                return f"{await_prefix}page.waitForSelector('{self.selector}')"
            return f"{await_prefix}page.waitForTimeout({self.value or 1000})"
        elif self.action == "hover":
            return f"{await_prefix}page.hover('{self.selector}')"
        elif self.action == "focus":
            return f"{await_prefix}page.focus('{self.selector}')"
        elif self.action == "screenshot":
            opts = f"{{ path: '{self.value or 'screenshot.png'}' }}"
            return f"{await_prefix}page.screenshot({opts})"
        elif self.action == "element_screenshot":
            opts = f"{{ path: '{self.value or 'element.png'}' }}"
            return f"{await_prefix}page.locator('{self.selector}').screenshot({opts})"
        elif self.action == "expect_visible":
            return f"{await_prefix}expect(page.locator('{self.selector}')).toBeVisible()"
        elif self.action == "expect_text":
            return f"{await_prefix}expect(page.locator('{self.selector}')).toHaveText('{self.value}')"
        elif self.action == "expect_url":
            return f"{await_prefix}expect(page).toHaveURL('{self.value}')"
        elif self.action == "expect_title":
            return f"{await_prefix}expect(page).toHaveTitle('{self.value}')"
        elif self.action == "reload":
            return f"{await_prefix}page.reload()"
        elif self.action == "go_back":
            return f"{await_prefix}page.goBack()"
        elif self.action == "go_forward":
            return f"{await_prefix}page.goForward()"
        elif self.action == "press":
            return f"{await_prefix}page.press('{self.selector}', '{self.value}')"
        elif self.action == "set_viewport":
            size = self.value or "{ width: 1280, height: 720 }"
            return f"{await_prefix}page.setViewportSize({size})"
        elif self.action == "emulate":
            return f"{await_prefix}page.emulate({self.value})"
        else:
            return f"// Action: {self.action}"
    
    def _format_options(self, option_names: List[str]) -> str:
        """格式化选项"""
        opts = []
        for name in option_names:
            if name in self.options:
                value = self.options[name]
                if isinstance(value, str):
                    opts.append(f"{name}: '{value}'")
                else:
                    opts.append(f"{name}: {value}")
        
        if opts:
            return ", { " + ", ".join(opts) + " }"
        return ""


@dataclass
class BrowserConfig:
    """浏览器配置"""
    name: str
    use: Dict[str, Any] = field(default_factory=dict)
    
    def to_config_dict(self) -> Dict:
        """转换为配置字典"""
        return {
            "name": self.name,
            "use": self.use
        }


@dataclass
class ProjectConfig:
    """项目配置"""
    name: str
    test_dir: str = "./tests"
    output_dir: str = "./test-results"
    timeout: int = 30000
    expect_timeout: int = 5000
    fully_parallel: bool = True
    forbid_only: bool = False
    retries: int = 0
    workers: int = 4
    reporter: List[str] = None
    use: Dict[str, Any] = None
    projects: List[BrowserConfig] = None
    
    def __post_init__(self):
        if self.reporter is None:
            self.reporter = [["html", {"outputFolder": "playwright-report"}]]
        if self.use is None:
            self.use = {
                "baseURL": "http://localhost:3000",
                "trace": "on-first-retry",
                "screenshot": "only-on-failure",
                "video": "retain-on-failure"
            }
        if self.projects is None:
            self.projects = [
                BrowserConfig("chromium", {"browserName": "chromium"}),
                BrowserConfig("firefox", {"browserName": "firefox"}),
                BrowserConfig("webkit", {"browserName": "webkit"})
            ]


class PlaywrightSkill:
    """Playwright测试Skill主类"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.templates = self._load_templates()
        self.supported_devices = self._load_devices()
    
    def _load_templates(self) -> Dict[str, str]:
        """加载模板"""
        return {
            "spec_file": '''import {{ test, expect }} from '@playwright/test';
{imports}

test.describe('{suite_name}', () => {{
  {hooks}
  
  {tests}
}});
''',
            "test_sync": '''
test('{test_name}', async ({{ page }}) => {{
  {steps}
}});
''',
            "test_with_context": '''
test('{test_name}', async ({{ page, context }}) => {{
  {setup}
  
  {steps}
}});
''',
            "before_each": '''test.beforeEach(async ({{ page }}) => {{
  {steps}
}});
''',
            "page_object": '''export class {class_name} {{
  constructor(page) {{
    this.page = page;
    {element_initializers}
  }}
  
  {element_getters}
  
  {methods}
}}'''
        }
    
    def _load_devices(self) -> Dict[str, Dict]:
        """加载支持的设备"""
        return {
            "iPhone 14": {"userAgent": "Mozilla/5.0...", "viewport": {"width": 390, "height": 844}},
            "iPhone 14 Pro Max": {"userAgent": "Mozilla/5.0...", "viewport": {"width": 430, "height": 932}},
            "Pixel 7": {"userAgent": "Mozilla/5.0...", "viewport": {"width": 412, "height": 915}},
            "iPad Pro 11": {"userAgent": "Mozilla/5.0...", "viewport": {"width": 834, "height": 1194}},
            "Desktop Chrome": {"viewport": {"width": 1920, "height": 1080}},
            "Desktop Safari": {"viewport": {"width": 1280, "height": 720}}
        }
    
    def generate_test(
        self,
        suite_name: str,
        test_name: str,
        steps: List[Union[TestStep, Dict]],
        options: Optional[Dict] = None
    ) -> str:
        """
        生成Playwright测试代码
        
        Args:
            suite_name: 测试套件名称
            test_name: 测试名称
            steps: 测试步骤
            options: 选项
            
        Returns:
            生成的测试代码
        """
        options = options or {}
        use_async = options.get("async", True)
        
        # 转换步骤
        step_objects = [s if isinstance(s, TestStep) else TestStep(**s) for s in steps]
        step_code = "\n  ".join([s.to_playwright_code(use_async) for s in step_objects])
        
        imports = options.get("imports", "")
        hooks = options.get("hooks", "")
        
        test_code = self.templates["test_sync"].format(
            test_name=test_name,
            steps=step_code
        )
        
        return self.templates["spec_file"].format(
            imports=imports,
            suite_name=suite_name,
            hooks=hooks,
            tests=test_code
        )
    
    def generate_multi_browser_test(
        self,
        suite_name: str,
        test_name: str,
        steps: List[Union[TestStep, Dict]],
        browsers: List[BrowserType] = None
    ) -> str:
        """
        生成多浏览器测试
        
        Args:
            suite_name: 测试套件名称
            test_name: 测试名称
            steps: 测试步骤
            browsers: 浏览器列表
            
        Returns:
            生成的测试代码
        """
        browsers = browsers or [BrowserType.CHROMIUM, BrowserType.FIREFOX, BrowserType.WEBKIT]
        
        step_objects = [s if isinstance(s, TestStep) else TestStep(**s) for s in steps]
        step_code = "\n    ".join([s.to_playwright_code(True) for s in step_objects])
        
        tests = []
        for browser in browsers:
            test = f'''
test('{test_name} - {browser.value}', async ({{ browser }}) => {{
  const context = await browser.newContext();
  const page = await context.newPage();
  
  {step_code}
  
  await context.close();
}});'''
            tests.append(test)
        
        return self.templates["spec_file"].format(
            imports="",
            suite_name=suite_name,
            hooks="",
            tests="".join(tests)
        )
    
    def generate_screenshot_test(
        self,
        url: str,
        selector: Optional[str] = None,
        options: Optional[Dict] = None
    ) -> str:
        """
        生成截图对比测试
        
        Args:
            url: 页面URL
            selector: 元素选择器（可选）
            options: 选项
            
        Returns:
            生成的测试代码
        """
        opts = options or {}
        threshold = opts.get("threshold", 0.2)
        full_page = opts.get("full_page", False)
        mask_selectors = opts.get("mask", [])
        
        mask_code = ""
        if mask_selectors:
            mask_code = f", mask: {json.dumps(mask_selectors)}"
        
        if selector:
            screenshot_step = f'''
  const element = page.locator('{selector}');
  await expect(element).toHaveScreenshot({{ 
    threshold: {threshold}{mask_code} 
  }});'''
        else:
            screenshot_step = f'''
  await expect(page).toHaveScreenshot({{ 
    fullPage: {str(full_page).lower()},
    threshold: {threshold}{mask_code}
  }});'''
        
        return f'''import {{ test, expect }} from '@playwright/test';

test('visual regression - {url}', async ({{ page }}) => {{
  await page.goto('{url}');
  {screenshot_step}
}});
'''
    
    def generate_api_test(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict] = None,
        assertions: Optional[List[Dict]] = None
    ) -> str:
        """
        生成API测试
        
        Args:
            endpoint: API端点
            method: HTTP方法
            data: 请求数据
            assertions: 断言列表
            
        Returns:
            生成的测试代码
        """
        assertions = assertions or []
        
        if method.upper() == "GET":
            request_code = f"const response = await page.request.get('{endpoint}');"
        elif method.upper() == "POST":
            data_str = json.dumps(data) if data else "{}"
            request_code = f"const response = await page.request.post('{endpoint}', {{ data: {data_str} }});"
        elif method.upper() == "PUT":
            data_str = json.dumps(data) if data else "{}"
            request_code = f"const response = await page.request.put('{endpoint}', {{ data: {data_str} }});"
        elif method.upper() == "DELETE":
            request_code = f"const response = await page.request.delete('{endpoint}');"
        else:
            request_code = f"// Unsupported method: {method}"
        
        assertion_code = []
        for assertion in assertions:
            assertion_type = assertion.get("type", "status")
            expected = assertion.get("expected")
            
            if assertion_type == "status":
                assertion_code.append(f"expect(response.status()).toBe({expected});")
            elif assertion_type == "ok":
                assertion_code.append(f"expect(response.ok()).toBe({str(expected).lower()});")
            elif assertion_type == "json":
                assertion_code.append(f"expect(await response.json()).toEqual({json.dumps(expected)});")
        
        return f'''import {{ test, expect }} from '@playwright/test';

test('API test - {endpoint}', async ({{ page }}) => {{
  {request_code}
  
  {chr(10).join(assertion_code)}
}});
'''
    
    def generate_mobile_test(
        self,
        suite_name: str,
        test_name: str,
        device: str,
        steps: List[Union[TestStep, Dict]]
    ) -> str:
        """
        生成移动端测试
        
        Args:
            suite_name: 测试套件名称
            test_name: 测试名称
            device: 设备名称
            steps: 测试步骤
            
        Returns:
            生成的测试代码
        """
        step_objects = [s if isinstance(s, TestStep) else TestStep(**s) for s in steps]
        step_code = "\n  ".join([s.to_playwright_code(True) for s in step_objects])
        
        return f'''import {{ test, expect, devices }} from '@playwright/test';

test.use({{ ...devices['{device}'] }});

test.describe('{suite_name}', () => {{
  test('{test_name}', async ({{ page }}) => {{
    {step_code}
  }});
}});
'''
    
    def generate_page_object(
        self,
        page_name: str,
        elements: List[Dict],
        methods: Optional[List[Dict]] = None
    ) -> str:
        """
        生成Page Object
        
        Args:
            page_name: 页面名称
            elements: 元素列表
            methods: 方法列表
            
        Returns:
            Page Object代码
        """
        element_initializers = []
        element_getters = []
        
        for elem in elements:
            name = elem.get("name")
            selector = elem.get("selector")
            element_initializers.append(f"this.{name} = page.locator('{selector}');")
            element_getters.append(f"get {name}() {{ return this.{name}; }}")
        
        method_code = []
        if methods:
            for method in methods:
                name = method.get("name")
                params = method.get("params", "")
                body = method.get("body", "")
                method_code.append(f'''async {name}({params}) {{
    {body}
  }}''')
        
        return self.templates["page_object"].format(
            class_name=f"{page_name}Page",
            element_initializers="\n    ".join(element_initializers),
            element_getters="\n  ".join(element_getters),
            methods="\n  ".join(method_code) if method_code else ""
        )
    
    def generate_config(
        self,
        options: Optional[Dict] = None
    ) -> str:
        """
        生成playwright.config.js
        
        Args:
            options: 配置选项
            
        Returns:
            配置文件内容
        """
        opts = options or {}
        
        config = ProjectConfig(
            name=opts.get("name", "Playwright Tests"),
            test_dir=opts.get("testDir", "./tests"),
            output_dir=opts.get("outputDir", "./test-results"),
            timeout=opts.get("timeout", 30000),
            expect_timeout=opts.get("expectTimeout", 5000),
            fully_parallel=opts.get("fullyParallel", True),
            forbid_only=opts.get("forbidOnly", False),
            retries=opts.get("retries", 0),
            workers=opts.get("workers", 4),
            reporter=opts.get("reporter", [["html", {"outputFolder": "playwright-report"}]]),
            use=opts.get("use", {
                "baseURL": self.base_url,
                "trace": "on-first-retry",
                "screenshot": "only-on-failure",
                "video": "retain-on-failure"
            })
        )
        
        projects = []
        browsers = opts.get("browsers", ["chromium", "firefox", "webkit"])
        
        for browser in browsers:
            projects.append({
                "name": browser,
                "use": {"browserName": browser}
            })
        
        # 添加移动设备项目
        devices = opts.get("devices", [])
        for device in devices:
            projects.append({
                "name": f"{device} - Mobile Safari",
                "use": {**{"browserName": "webkit"}, "...devices": f"['{device}']"}
            })
        
        config_dict = {
            "testDir": config.test_dir,
            "outputDir": config.output_dir,
            "fullyParallel": config.fully_parallel,
            "forbidOnly": config.forbid_only,
            "retries": config.retries,
            "workers": config.workers,
            "reporter": config.reporter,
            "use": config.use,
            "projects": projects
        }
        
        # 手动格式化JSON以保持可读性
        config_str = json.dumps(config_dict, indent=2)
        # 替换 "...devices" 为展开语法
        config_str = config_str.replace('"...devices": ', "...devices.")
        
        return f'''// @ts-check
const {{ defineConfig, devices }} = require('@playwright/test');

module.exports = defineConfig({config_str});
'''
    
    def generate_fixtures(self, fixtures: List[Dict]) -> str:
        """
        生成fixtures
        
        Args:
            fixtures: fixture列表
            
        Returns:
            fixtures代码
        """
        fixture_lines = []
        
        for fixture in fixtures:
            name = fixture.get("name")
            value = fixture.get("value")
            
            if isinstance(value, dict):
                fixture_lines.append(f"export const {name} = {json.dumps(value, indent=2)};")
            elif isinstance(value, str):
                fixture_lines.append(f"export const {name} = '{value}';")
            else:
                fixture_lines.append(f"export const {name} = {value};")
        
        return "\n\n".join(fixture_lines)
    
    def generate_test_generator_command(
        self,
        url: str,
        output_file: str,
        options: Optional[Dict] = None
    ) -> str:
        """
        生成codegen命令
        
        Args:
            url: 目标URL
            output_file: 输出文件
            options: 选项
            
        Returns:
            命令字符串
        """
        opts = options or {}
        browser = opts.get("browser", "chromium")
        device = opts.get("device")
        
        cmd_parts = [f"npx playwright codegen", f"--target javascript", f"--browser {browser}"]
        
        if device:
            cmd_parts.append(f"--device='{device}'")
        
        if opts.get("viewport"):
            vp = opts.get("viewport")
            cmd_parts.append(f"--viewport-size={vp['width']},{vp['height']}")
        
        cmd_parts.append(f"-o {output_file}")
        cmd_parts.append(url)
        
        return " ".join(cmd_parts)
    
    def setup_project(self, project_path: str, options: Optional[Dict] = None) -> Dict[str, str]:
        """
        设置Playwright项目
        
        Args:
            project_path: 项目路径
            options: 选项
            
        Returns:
            生成的文件字典
        """
        files = {}
        
        # playwright.config.js
        files["playwright.config.js"] = self.generate_config(options)
        
        # package.json
        files["package.json"] = json.dumps({
            "name": options.get("project_name", "playwright-tests"),
            "version": "1.0.0",
            "scripts": {
                "test": "playwright test",
                "test:ui": "playwright test --ui",
                "test:debug": "playwright test --debug",
                "test:headed": "playwright test --headed",
                "report": "playwright show-report"
            },
            "devDependencies": {
                "@playwright/test": "^1.40.0"
            }
        }, indent=2)
        
        # 示例测试
        files["tests/example.spec.js"] = self.generate_test(
            suite_name="Example Tests",
            test_name="basic navigation",
            steps=[
                TestStep(action="goto", value=self.base_url),
                TestStep(action="expect_visible", selector="body")
            ]
        )
        
        # fixtures
        files["tests/fixtures/data.js"] = self.generate_fixtures([
            {"name": "users", "value": [{"id": 1, "name": "User 1"}]},
            {"name": "products", "value": [{"id": 1, "name": "Product 1"}]}
        ])
        
        return files


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Playwright Testing Skill')
    parser.add_argument('action', choices=['test', 'config', 'screenshot', 'api', 'setup'])
    parser.add_argument('--url', '-u', help='Target URL')
    parser.add_argument('--name', '-n', help='Test name')
    parser.add_argument('--browser', '-b', default='chromium', help='Browser type')
    parser.add_argument('--output', '-o', help='Output file')
    
    args = parser.parse_args()
    
    skill = PlaywrightSkill()
    
    if args.action == 'test':
        code = skill.generate_test(
            suite_name=args.name or "Test Suite",
            test_name="basic test",
            steps=[
                {"action": "goto", "value": args.url or "http://localhost:3000"},
                {"action": "expect_visible", "selector": "body"}
            ]
        )
        print(code)
        
    elif args.action == 'config':
        config = skill.generate_config()
        print(config)
        
    elif args.action == 'screenshot':
        code = skill.generate_screenshot_test(args.url or "http://localhost:3000")
        print(code)
        
    elif args.action == 'api':
        code = skill.generate_api_test(args.url or "/api/users", "GET")
        print(code)
        
    elif args.action == 'setup':
        files = skill.setup_project('.')
        for filename, content in files.items():
            print(f"\n=== {filename} ===")
            print(content[:500] + "..." if len(content) > 500 else content)


if __name__ == '__main__':
    main()
