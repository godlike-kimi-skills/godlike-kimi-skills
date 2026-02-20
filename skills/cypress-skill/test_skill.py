#!/usr/bin/env python3
"""
Cypress Skill 测试套件
"""

import unittest
import json
import os
import tempfile
from main import (
    CypressSkill, ElementLocator, TestAction, Assertion,
    PageObject, MockConfig
)


class TestCypressSkill(unittest.TestCase):
    """Cypress Skill 测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.skill = CypressSkill(base_url="http://localhost:3000")
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.skill.base_url, "http://localhost:3000")
        self.assertIsNotNone(self.skill.templates)
    
    def test_generate_test_basic(self):
        """测试生成基础测试"""
        test_code = self.skill.generate_test(
            suite_name="Login Test",
            url="http://localhost:3000/login",
            actions=[
                TestAction(action="type", target="#username", value="admin"),
                TestAction(action="type", target="#password", value="secret"),
                TestAction(action="click", target="#login-btn")
            ],
            assertions=[
                Assertion(target=".dashboard", assertion="be.visible"),
                Assertion(target=".welcome", assertion="contain.text", expected_value="Welcome")
            ]
        )
        
        self.assertIn("describe('Login Test'", test_code)
        self.assertIn("cy.get('#username').type('admin')", test_code)
        self.assertIn("cy.get('.dashboard').should('be.visible')", test_code)
    
    def test_generate_test_with_intercept(self):
        """测试生成带API拦截的测试"""
        test_code = self.skill.generate_test(
            suite_name="API Test",
            url="http://localhost:3000",
            actions=[TestAction(action="click", target="#fetch-btn")],
            assertions=[Assertion(target=".result", assertion="exist")],
            options={
                "intercept": [{"method": "GET", "url": "/api/data", "alias": "getData"}]
            }
        )
        
        self.assertIn("cy.intercept", test_code)
    
    def test_generate_page_object(self):
        """测试生成Page Object"""
        code = self.skill.generate_page_object(
            page_name="Login",
            url="/login",
            elements=[
                ElementLocator(name="username", selector="#username", element_type="input"),
                ElementLocator(name="password", selector="#password", element_type="input"),
                ElementLocator(name="submitBtn", selector="button[type=submit]", element_type="button")
            ]
        )
        
        self.assertIn("class LoginPage", code)
        self.assertIn("this.username = '#username'", code)
        self.assertIn("get username()", code)
        self.assertIn("fillUsername(value)", code)
        self.assertIn("clickSubmitBtn()", code)
    
    def test_generate_fixture(self):
        """测试生成Fixture"""
        data = {
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"}
            ]
        }
        
        fixture = self.skill.generate_fixture("users", data)
        parsed = json.loads(fixture)
        
        self.assertEqual(len(parsed["users"]), 2)
    
    def test_generate_fixtures_set(self):
        """测试生成一组Fixtures"""
        fixtures = self.skill.generate_fixtures_set([
            {"name": "users", "data": {"admin": {"role": "admin"}}},
            {"name": "products", "data": {"list": []}}
        ])
        
        self.assertIn("users.json", fixtures)
        self.assertIn("products.json", fixtures)
    
    def test_generate_custom_command(self):
        """测试生成自定义命令"""
        code = self.skill.generate_custom_command(
            command_name="dataTestId",
            implementation="return cy.get(`[data-testid=${value}]`);",
            options={"params": "value"}
        )
        
        self.assertIn("Cypress.Commands.add('dataTestId'", code)
    
    def test_generate_custom_command_with_subject(self):
        """测试生成带subject的自定义命令"""
        code = self.skill.generate_custom_command(
            command_name="shouldBeVisible",
            implementation="return subject.should('be.visible');",
            options={"prevSubject": True, "params": ""}
        )
        
        self.assertIn("prevSubject: true", code)
    
    def test_generate_api_intercept(self):
        """测试生成API拦截"""
        code = self.skill.generate_api_intercept(
            route="/api/users",
            method="GET",
            response={"data": []},
            options={"alias": "getUsers"}
        )
        
        self.assertIn("cy.intercept('GET', '/api/users'", code)
        self.assertIn(".as('getUsers')", code)
    
    def test_generate_test_suite_from_user_flow(self):
        """测试从用户流生成测试套件"""
        code = self.skill.generate_test_suite_from_user_flow(
            flow_name="Checkout Flow",
            steps=[
                {
                    "name": "Add to cart",
                    "actions": [{"type": "click", "target": ".add-to-cart"}],
                    "assertions": [{"target": ".cart-badge", "type": "contain.text", "value": "1"}]
                },
                {
                    "name": "Go to checkout",
                    "actions": [{"type": "click", "target": ".checkout-btn"}],
                    "assertions": [{"target": ".checkout-form", "type": "be.visible"}]
                }
            ]
        )
        
        self.assertIn("describe('Checkout Flow'", code)
        self.assertIn("should complete: Add to cart", code)
        self.assertIn("should complete: Go to checkout", code)
    
    def test_generate_cypress_config(self):
        """测试生成Cypress配置"""
        config = self.skill.generate_cypress_config({
            "baseUrl": "http://localhost:8080",
            "viewportWidth": 1920,
            "video": True
        })
        
        self.assertIn("baseUrl", config)
        self.assertIn("viewportWidth", config)
    
    def test_generate_support_file(self):
        """测试生成support文件"""
        support = self.skill.generate_support_file()
        
        self.assertIn("import './commands'", support)
        self.assertIn("beforeEach", support)
    
    def test_analyze_test_results(self):
        """测试分析测试结果"""
        results = {
            "totalTests": 100,
            "totalPassed": 95,
            "totalFailed": 3,
            "totalPending": 2,
            "totalSkipped": 0,
            "totalDuration": 15000,
            "failures": [{"title": "Test 1", "error": "Timeout"}]
        }
        
        analysis = self.skill.analyze_test_results(results)
        
        self.assertEqual(analysis["summary"]["total"], 100)
        self.assertEqual(analysis["summary"]["pass_rate"], 95.0)
        self.assertEqual(len(analysis["failed_tests"]), 1)
    
    def test_setup_project(self):
        """测试设置项目"""
        files = self.skill.setup_project("./test-project")
        
        self.assertIn("cypress.config.js", files)
        self.assertIn("cypress/support/e2e.js", files)
        self.assertIn("cypress/support/commands.js", files)
        self.assertIn("cypress/fixtures/example.json", files)
        self.assertIn("cypress/e2e/example.cy.js", files)
    
    def test_element_locator_to_cypress_command(self):
        """测试元素定位器转换"""
        # CSS selector
        elem1 = ElementLocator(name="btn", selector=".submit", selector_type="css")
        self.assertEqual(elem1.to_cypress_command(), "cy.get('.submit')")
        
        # Data-testid
        elem2 = ElementLocator(name="btn", selector="submit-btn", selector_type="data-testid")
        self.assertEqual(elem2.to_cypress_command(), "cy.get('[data-testid=submit-btn]')")
        
        # XPath
        elem3 = ElementLocator(name="btn", selector="//button", selector_type="xpath")
        self.assertEqual(elem3.to_cypress_command(), "cy.xpath('//button')")
        
        # Text
        elem4 = ElementLocator(name="btn", selector="Submit", selector_type="text")
        self.assertEqual(elem4.to_cypress_command(), "cy.contains('Submit')")
    
    def test_test_action_to_cypress_code(self):
        """测试动作转换"""
        action1 = TestAction(action="visit", value="http://example.com")
        self.assertEqual(action1.to_cypress_code(), "cy.visit('http://example.com')")
        
        action2 = TestAction(action="click", target=".btn")
        self.assertEqual(action2.to_cypress_code(), "cy.get('.btn').click()")
        
        action3 = TestAction(action="type", target="#input", value="text")
        self.assertEqual(action3.to_cypress_code(), "cy.get('#input').type('text')")
    
    def test_assertion_to_cypress_code(self):
        """测试断言转换"""
        assertion1 = Assertion(target=".msg", assertion="exist")
        self.assertEqual(assertion1.to_cypress_code(), "cy.get('.msg').should('exist')")
        
        assertion2 = Assertion(target=".title", assertion="have.text", expected_value="Hello")
        self.assertIn("should('have.text', 'Hello')", assertion2.to_cypress_code())


class TestCypressSkillIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        self.skill = CypressSkill()
    
    def test_full_e2e_workflow(self):
        """测试完整E2E工作流"""
        # 1. 设置项目
        files = self.skill.setup_project(".")
        self.assertGreater(len(files), 0)
        
        # 2. 生成Page Object
        page = self.skill.generate_page_object(
            page_name="Dashboard",
            url="/dashboard",
            elements=[
                ElementLocator(name="nav", selector="nav"),
                ElementLocator(name="content", selector=".content")
            ]
        )
        self.assertIsNotNone(page)
        
        # 3. 生成测试
        test = self.skill.generate_test(
            suite_name="Dashboard Test",
            url="/dashboard",
            actions=[TestAction(action="visit", value="/dashboard")],
            assertions=[Assertion(target=".dashboard", assertion="exist")]
        )
        self.assertIsNotNone(test)


def run_tests():
    """运行测试套件"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestCypressSkill))
    suite.addTests(loader.loadTestsFromTestCase(TestCypressSkillIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
