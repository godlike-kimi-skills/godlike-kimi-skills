#!/usr/bin/env python3
"""
Playwright Skill 测试套件
"""

import unittest
import json
import os
from main import (
    PlaywrightSkill, TestStep, BrowserType, DeviceType,
    BrowserConfig, ProjectConfig
)


class TestPlaywrightSkill(unittest.TestCase):
    """Playwright Skill 测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.skill = PlaywrightSkill(base_url="http://localhost:3000")
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.skill.base_url, "http://localhost:3000")
        self.assertIsNotNone(self.skill.templates)
        self.assertIsNotNone(self.skill.supported_devices)
    
    def test_generate_test_basic(self):
        """测试生成基础测试"""
        code = self.skill.generate_test(
            suite_name="Login Tests",
            test_name="should login successfully",
            steps=[
                TestStep(action="goto", value="http://localhost:3000/login"),
                TestStep(action="fill", selector="#username", value="admin"),
                TestStep(action="fill", selector="#password", value="secret"),
                TestStep(action="click", selector="#login-btn"),
                TestStep(action="expect_url", value="http://localhost:3000/dashboard")
            ]
        )
        
        self.assertIn("import { test, expect }", code)
        self.assertIn("test.describe('Login Tests'", code)
        self.assertIn("await page.goto('http://localhost:3000/login')", code)
        self.assertIn("await page.fill('#username', 'admin')", code)
        self.assertIn("await expect(page).toHaveURL", code)
    
    def test_generate_multi_browser_test(self):
        """测试生成多浏览器测试"""
        code = self.skill.generate_multi_browser_test(
            suite_name="Cross Browser Tests",
            test_name="basic navigation",
            steps=[
                TestStep(action="goto", value="http://localhost:3000"),
                TestStep(action="expect_visible", selector="body")
            ],
            browsers=[BrowserType.CHROMIUM, BrowserType.FIREFOX]
        )
        
        self.assertIn("test('basic navigation - chromium'", code)
        self.assertIn("test('basic navigation - firefox'", code)
        self.assertIn("const context = await browser.newContext()", code)
    
    def test_generate_screenshot_test_full_page(self):
        """测试生成全页截图测试"""
        code = self.skill.generate_screenshot_test(
            url="http://localhost:3000",
            options={"full_page": True, "threshold": 0.3}
        )
        
        self.assertIn("toHaveScreenshot", code)
        self.assertIn("fullPage: true", code)
        self.assertIn("threshold: 0.3", code)
    
    def test_generate_screenshot_test_element(self):
        """测试生成元素截图测试"""
        code = self.skill.generate_screenshot_test(
            url="http://localhost:3000",
            selector=".header",
            options={"threshold": 0.2}
        )
        
        self.assertIn("page.locator('.header')", code)
        self.assertIn("toHaveScreenshot", code)
    
    def test_generate_api_test_get(self):
        """测试生成GET API测试"""
        code = self.skill.generate_api_test(
            endpoint="http://localhost:3000/api/users",
            method="GET",
            assertions=[
                {"type": "status", "expected": 200},
                {"type": "ok", "expected": True}
            ]
        )
        
        self.assertIn("page.request.get", code)
        self.assertIn("expect(response.status()).toBe(200)", code)
        self.assertIn("expect(response.ok()).toBe(true)", code)
    
    def test_generate_api_test_post(self):
        """测试生成POST API测试"""
        code = self.skill.generate_api_test(
            endpoint="http://localhost:3000/api/users",
            method="POST",
            data={"name": "John", "email": "john@example.com"},
            assertions=[
                {"type": "status", "expected": 201},
                {"type": "json", "expected": {"id": 1, "name": "John"}}
            ]
        )
        
        self.assertIn("page.request.post", code)
        self.assertIn('"name": "John"', code)
        self.assertIn("toEqual", code)
    
    def test_generate_mobile_test(self):
        """测试生成移动端测试"""
        code = self.skill.generate_mobile_test(
            suite_name="Mobile Tests",
            test_name="mobile navigation",
            device="iPhone 14",
            steps=[
                TestStep(action="goto", value="http://localhost:3000"),
                TestStep(action="click", selector=".menu-btn")
            ]
        )
        
        self.assertIn("test.use({ ...devices['iPhone 14'] })", code)
        self.assertIn("Mobile Tests", code)
    
    def test_generate_page_object(self):
        """测试生成Page Object"""
        code = self.skill.generate_page_object(
            page_name="Login",
            elements=[
                {"name": "usernameInput", "selector": "#username"},
                {"name": "passwordInput", "selector": "#password"},
                {"name": "loginButton", "selector": "button[type=submit]"}
            ],
            methods=[
                {
                    "name": "login",
                    "params": "username, password",
                    "body": "await this.usernameInput.fill(username);\n    await this.passwordInput.fill(password);\n    await this.loginButton.click();"
                }
            ]
        )
        
        self.assertIn("export class LoginPage", code)
        self.assertIn("this.usernameInput = page.locator('#username')", code)
        self.assertIn("get usernameInput()", code)
        self.assertIn("async login(username, password)", code)
    
    def test_generate_config(self):
        """测试生成配置"""
        config = self.skill.generate_config({
            "name": "My Tests",
            "browsers": ["chromium", "firefox"],
            "workers": 2,
            "retries": 1
        })
        
        self.assertIn("My Tests", config)
        self.assertIn("chromium", config)
        self.assertIn("firefox", config)
        self.assertIn("workers", config)
    
    def test_generate_fixtures(self):
        """测试生成fixtures"""
        code = self.skill.generate_fixtures([
            {"name": "users", "value": [{"id": 1, "name": "Alice"}]},
            {"name": "apiUrl", "value": "http://localhost:3000/api"}
        ])
        
        self.assertIn("export const users", code)
        self.assertIn("export const apiUrl", code)
    
    def test_generate_test_generator_command(self):
        """测试生成codegen命令"""
        cmd = self.skill.generate_test_generator_command(
            url="http://localhost:3000",
            output_file="tests/generated.spec.js",
            options={"browser": "chromium", "device": "iPhone 14"}
        )
        
        self.assertIn("npx playwright codegen", cmd)
        self.assertIn("--browser chromium", cmd)
        self.assertIn("--device='iPhone 14'", cmd)
        self.assertIn("-o tests/generated.spec.js", cmd)
    
    def test_setup_project(self):
        """测试设置项目"""
        files = self.skill.setup_project("./test-project")
        
        self.assertIn("playwright.config.js", files)
        self.assertIn("package.json", files)
        self.assertIn("tests/example.spec.js", files)
        self.assertIn("tests/fixtures/data.js", files)
    
    def test_test_step_to_code_goto(self):
        """测试步骤转换 - goto"""
        step = TestStep(action="goto", value="http://example.com")
        self.assertEqual(step.to_playwright_code(), "await page.goto('http://example.com')")
    
    def test_test_step_to_code_click(self):
        """测试步骤转换 - click"""
        step = TestStep(action="click", selector=".btn")
        self.assertEqual(step.to_playwright_code(), "await page.click('.btn')")
    
    def test_test_step_to_code_fill(self):
        """测试步骤转换 - fill"""
        step = TestStep(action="fill", selector="#input", value="text")
        self.assertEqual(step.to_playwright_code(), "await page.fill('#input', 'text')")
    
    def test_test_step_to_code_expect_visible(self):
        """测试步骤转换 - expect visible"""
        step = TestStep(action="expect_visible", selector=".element")
        self.assertEqual(
            step.to_playwright_code(),
            "await expect(page.locator('.element')).toBeVisible()"
        )
    
    def test_test_step_sync_mode(self):
        """测试步骤同步模式"""
        step = TestStep(action="goto", value="http://example.com")
        self.assertEqual(
            step.to_playwright_code(use_async=False),
            "page.goto('http://example.com')"
        )
    
    def test_supported_devices(self):
        """测试支持的设备"""
        self.assertIn("iPhone 14", self.skill.supported_devices)
        self.assertIn("Pixel 7", self.skill.supported_devices)
        self.assertIn("Desktop Chrome", self.skill.supported_devices)


class TestPlaywrightSkillIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        self.skill = PlaywrightSkill()
    
    def test_full_workflow(self):
        """测试完整工作流"""
        # 1. 设置项目
        files = self.skill.setup_project(".")
        self.assertGreater(len(files), 0)
        
        # 2. 生成Page Object
        page = self.skill.generate_page_object(
            page_name="Home",
            elements=[
                {"name": "nav", "selector": "nav"},
                {"name": "content", "selector": ".content"}
            ]
        )
        self.assertIsNotNone(page)
        
        # 3. 生成测试
        test = self.skill.generate_test(
            suite_name="Home Tests",
            test_name="navigation",
            steps=[
                TestStep(action="goto", value="http://localhost:3000"),
                TestStep(action="expect_visible", selector="body")
            ]
        )
        self.assertIsNotNone(test)
        
        # 4. 生成配置
        config = self.skill.generate_config()
        self.assertIsNotNone(config)


def run_tests():
    """运行测试套件"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestPlaywrightSkill))
    suite.addTests(loader.loadTestsFromTestCase(TestPlaywrightSkillIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
