#!/usr/bin/env python3
"""
Cypress E2E Testing Skill

Cypress E2E测试智能助手。Use when writing tests, automating testing, 
or when user mentions 'Cypress', 'E2E testing', 'end-to-end testing', 'browser automation'.

Capabilities:
- 测试生成: 自动生成Cypress E2E测试代码
- Page Object: 创建Page Object模式代码
- Fixtures: 管理测试数据和Fixtures
- 自定义命令: 生成自定义Cypress命令
- 报告生成: 生成测试报告和分析
"""

import json
import re
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from pathlib import Path
from datetime import datetime


@dataclass
class ElementLocator:
    """元素定位器"""
    name: str
    selector: str
    selector_type: str = "css"  # css, xpath, data-testid, text
    element_type: str = "input"  # input, button, link, text, dropdown
    
    def to_cypress_command(self) -> str:
        """转换为Cypress命令"""
        if self.selector_type == "data-testid":
            return f"cy.get('[data-testid={self.selector}]')"
        elif self.selector_type == "xpath":
            return f"cy.xpath('{self.selector}')"
        elif self.selector_type == "text":
            return f"cy.contains('{self.selector}')"
        else:
            return f"cy.get('{self.selector}')"


@dataclass
class TestAction:
    """测试动作"""
    action: str  # click, type, select, visit, wait, etc.
    target: Optional[str] = None
    value: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)
    
    def to_cypress_code(self) -> str:
        """转换为Cypress代码"""
        if self.action == "visit":
            return f"cy.visit('{self.value}')"
        elif self.action == "click":
            return f"cy.get('{self.target}').click()"
        elif self.action == "type":
            return f"cy.get('{self.target}').type('{self.value}')"
        elif self.action == "clear":
            return f"cy.get('{self.target}').clear()"
        elif self.action == "select":
            return f"cy.get('{self.target}').select('{self.value}')"
        elif self.action == "wait":
            if self.value:
                return f"cy.wait({self.value})"
            return f"cy.wait('{self.target}')"
        elif self.action == "intercept":
            return f"cy.intercept('{self.target}', {self.value})"
        elif self.action == "reload":
            return "cy.reload()"
        elif self.action == "go":
            return f"cy.go('{self.value}')"
        elif self.action == "screenshot":
            return f"cy.screenshot('{self.value or 'screenshot'}')"
        elif self.action == "fixture":
            return f"cy.fixture('{self.value}')"
        else:
            return f"// Action: {self.action}"


@dataclass
class Assertion:
    """断言"""
    target: str
    assertion: str  # exist, visible, have.text, have.value, have.class, etc.
    expected_value: Optional[str] = None
    negate: bool = False
    
    def to_cypress_code(self) -> str:
        """转换为Cypress代码"""
        should = "should" if not self.negate else "should"
        not_prefix = "not." if self.negate else ""
        
        if self.expected_value:
            if "have" in self.assertion or "eq" in self.assertion:
                return f"cy.get('{self.target}').{should}('{not_prefix}{self.assertion}', '{self.expected_value}')"
            return f"cy.get('{self.target}').{should}('{not_prefix}{self.assertion}').and('contain', '{self.expected_value}')"
        
        return f"cy.get('{self.target}').{should}('{not_prefix}{self.assertion}')"


@dataclass
class PageObject:
    """页面对象"""
    name: str
    url: str
    elements: List[ElementLocator] = field(default_factory=list)
    methods: List[Dict] = field(default_factory=list)


class CypressSkill:
    """Cypress E2E测试Skill主类"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """加载测试模板"""
        return {
            "test_file": '''{imports}

describe('{suite_name}', () => {{
  {before_hook}
  
  {test_cases}
  
  {after_hook}
}});
''',
            "test_case": '''
  it('{test_name}', () => {{
    {setup}
    
    {actions}
    
    {assertions}
  }});
''',
            "before_each": '''beforeEach(() => {{
    {actions}
  }});''',
            "before_all": '''before(() => {{
    {actions}
  }});''',
            "page_object": '''class {class_name} {{
  constructor() {{
    this.url = '{url}';
    {element_initializers}
  }}
  
  {element_getters}
  
  {methods}
}}

export default {class_name};
''',
            "custom_command": '''Cypress.Commands.add('{command_name}', {options}({params}) => {{
  {implementation}
}});'''
        }
    
    def generate_test(
        self,
        suite_name: str,
        url: str,
        actions: List[Union[TestAction, Dict]],
        assertions: List[Union[Assertion, Dict]],
        setup_actions: Optional[List[Union[TestAction, Dict]]] = None,
        options: Optional[Dict] = None
    ) -> str:
        """
        生成Cypress测试代码
        
        Args:
            suite_name: 测试套件名称
            url: 测试URL
            actions: 测试动作列表
            assertions: 断言列表
            setup_actions: 设置动作列表
            options: 其他选项
            
        Returns:
            生成的测试代码
        """
        options = options or {}
        
        # 转换字典为对象
        action_objects = [a if isinstance(a, TestAction) else TestAction(**a) for a in actions]
        assertion_objects = [a if isinstance(a, Assertion) else Assertion(**a) for a in assertions]
        setup_objects = []
        if setup_actions:
            setup_objects = [a if isinstance(a, TestAction) else TestAction(**a) for a in setup_actions]
        
        # 生成动作代码
        action_code = "\n    ".join([a.to_cypress_code() for a in action_objects])
        assertion_code = "\n    ".join([a.to_cypress_code() for a in assertion_objects])
        setup_code = "\n    ".join([a.to_cypress_code() for a in setup_objects]) if setup_objects else ""
        
        # 生成测试用例
        test_case = self.templates["test_case"].format(
            test_name=options.get("test_name", "should complete the test flow"),
            setup=setup_code,
            actions=action_code,
            assertions=assertion_code
        )
        
        # 生成beforeEach
        before_actions = [f"cy.visit('{url}')"]
        if options.get("intercept"):
            for intercept in options["intercept"]:
                before_actions.append(f"cy.intercept('{intercept['method']}', '{intercept['url']}').as('{intercept['alias']}')")
        
        before_hook = self.templates["before_each"].format(
            actions="\n    ".join(before_actions)
        ) if options.get("use_before_each", True) else ""
        
        return self.templates["test_file"].format(
            imports=options.get("imports", ""),
            suite_name=suite_name,
            before_hook=before_hook,
            test_cases=test_case,
            after_hook=""
        )
    
    def generate_page_object(
        self,
        page_name: str,
        url: str,
        elements: List[Union[ElementLocator, Dict]],
        custom_methods: Optional[List[Dict]] = None
    ) -> str:
        """
        生成Page Object
        
        Args:
            page_name: 页面类名
            url: 页面URL
            elements: 元素列表
            custom_methods: 自定义方法
            
        Returns:
            Page Object代码
        """
        # 转换字典为对象
        element_objects = [e if isinstance(e, ElementLocator) else ElementLocator(**e) for e in elements]
        
        # 元素初始化
        element_initializers = []
        element_getters = []
        
        for elem in element_objects:
            element_initializers.append(f"this.{elem.name} = '{elem.selector}';")
            
            getter = f'''  get {elem.name}() {{
    return cy.get(this.{elem.name});
  }}'''
            element_getters.append(getter)
        
        # 生成方法
        methods = []
        
        # 默认visit方法
        methods.append(f'''  visit() {{
    cy.visit(this.url);
    return this;
  }}''')
        
        # 根据元素类型生成操作方法
        for elem in element_objects:
            if elem.element_type == "input":
                methods.append(f'''  fill{self._capitalize(elem.name)}(value) {{
    this.{elem.name}.type(value);
    return this;
  }}''')
            elif elem.element_type == "button":
                methods.append(f'''  click{self._capitalize(elem.name)}() {{
    this.{elem.name}.click();
    return this;
  }}''')
        
        # 自定义方法
        if custom_methods:
            for method in custom_methods:
                method_name = method.get("name")
                params = method.get("params", "")
                body = method.get("body", "")
                methods.append(f'''  {method_name}({params}) {{
    {body}
    return this;
  }}''')
        
        # 生成完整类
        class_name = f"{page_name}Page"
        
        return f'''class {class_name} {{
  constructor() {{
    this.url = '{url}';
    {chr(10).join(["    " + e for e in element_initializers])}
  }}
  
{chr(10).join(element_getters)}
  
{chr(10 + "\n  ".join([]) + chr(10)).join(methods)}
}}

export default {class_name};
'''
    
    def _capitalize(self, s: str) -> str:
        """首字母大写"""
        return s[0].upper() + s[1:] if s else s
    
    def generate_fixture(
        self,
        name: str,
        data: Dict[str, Any],
        options: Optional[Dict] = None
    ) -> str:
        """
        生成Fixture数据
        
        Args:
            name: fixture名称
            data: fixture数据
            options: 选项
            
        Returns:
            JSON字符串
        """
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def generate_fixtures_set(
        self,
        fixtures_config: List[Dict]
    ) -> Dict[str, str]:
        """
        生成一组Fixtures
        
        Args:
            fixtures_config: fixture配置列表
            
        Returns:
            文件名到内容的字典
        """
        fixtures = {}
        
        for config in fixtures_config:
            name = config.get("name")
            data = config.get("data", {})
            fixtures[f"{name}.json"] = self.generate_fixture(name, data)
        
        return fixtures
    
    def generate_custom_command(
        self,
        command_name: str,
        implementation: str,
        options: Optional[Dict] = None
    ) -> str:
        """
        生成自定义Cypress命令
        
        Args:
            command_name: 命令名称
            implementation: 实现代码
            options: 选项
            
        Returns:
            命令代码
        """
        opts = options or {}
        prev_subject = opts.get("prevSubject", False)
        params = opts.get("params", "")
        
        if prev_subject:
            return f'''Cypress.Commands.add('{command_name}', {{ prevSubject: true }}, (subject{params and ', ' + params}) => {{
  {implementation}
}});'''
        
        return f'''Cypress.Commands.add('{command_name}', ({params}) => {{
  {implementation}
}});'''
    
    def generate_api_intercept(
        self,
        route: str,
        method: str = "GET",
        response: Optional[Dict] = None,
        options: Optional[Dict] = None
    ) -> str:
        """
        生成API拦截代码
        
        Args:
            route: API路由
            method: HTTP方法
            response: 响应数据
            options: 选项
            
        Returns:
            拦截代码
        """
        alias = options.get("alias", "apiCall") if options else "apiCall"
        status_code = options.get("statusCode", 200) if options else 200
        
        if response:
            response_json = json.dumps(response, indent=2)
            return f'''cy.intercept('{method}', '{route}', {{
  statusCode: {status_code},
  body: {response_json}
}}).as('{alias}');'''
        
        return f"cy.intercept('{method}', '{route}').as('{alias}');"
    
    def generate_test_suite_from_user_flow(
        self,
        flow_name: str,
        steps: List[Dict],
        options: Optional[Dict] = None
    ) -> str:
        """
        根据用户流程生成测试套件
        
        Args:
            flow_name: 流程名称
            steps: 流程步骤列表
            options: 选项
            
        Returns:
            测试套件代码
        """
        test_cases = []
        
        for i, step in enumerate(steps):
            step_name = step.get("name", f"Step {i+1}")
            actions = step.get("actions", [])
            assertions = step.get("assertions", [])
            
            action_code = "\n    ".join([self._action_to_code(a) for a in actions])
            assertion_code = "\n    ".join([self._assertion_to_code(a) for a in assertions])
            
            test_case = self.templates["test_case"].format(
                test_name=f"should complete: {step_name}",
                setup="",
                actions=action_code,
                assertions=assertion_code
            )
            test_cases.append(test_case)
        
        return self.templates["test_file"].format(
            imports=options.get("imports", "") if options else "",
            suite_name=flow_name,
            before_hook="",
            test_cases="".join(test_cases),
            after_hook=""
        )
    
    def _action_to_code(self, action: Dict) -> str:
        """将动作转换为代码"""
        action_type = action.get("type", "click")
        target = action.get("target", "")
        value = action.get("value", "")
        
        if action_type == "visit":
            return f"cy.visit('{target}')"
        elif action_type == "click":
            return f"cy.get('{target}').click()"
        elif action_type == "type":
            return f"cy.get('{target}').type('{value}')"
        elif action_type == "select":
            return f"cy.get('{target}').select('{value}')"
        elif action_type == "wait":
            return f"cy.wait({value})"
        return f"// {action_type}"
    
    def _assertion_to_code(self, assertion: Dict) -> str:
        """将断言转换为代码"""
        target = assertion.get("target", "")
        type_ = assertion.get("type", "exist")
        value = assertion.get("value", "")
        
        if value:
            return f"cy.get('{target}').should('{type_}', '{value}')"
        return f"cy.get('{target}').should('{type_}')"
    
    def generate_cypress_config(self, options: Optional[Dict] = None) -> str:
        """
        生成Cypress配置文件
        
        Args:
            options: 配置选项
            
        Returns:
            cypress.config.js内容
        """
        opts = options or {}
        
        config = {
            "e2e": {
                "baseUrl": opts.get("baseUrl", self.base_url),
                "specPattern": opts.get("specPattern", "cypress/e2e/**/*.cy.js"),
                "supportFile": opts.get("supportFile", "cypress/support/e2e.js"),
                "viewportWidth": opts.get("viewportWidth", 1280),
                "viewportHeight": opts.get("viewportHeight", 720),
                "video": opts.get("video", False),
                "screenshotOnRunFailure": opts.get("screenshotOnRunFailure", True),
                "defaultCommandTimeout": opts.get("defaultCommandTimeout", 4000),
                "requestTimeout": opts.get("requestTimeout", 5000),
                "responseTimeout": opts.get("responseTimeout", 30000),
                "pageLoadTimeout": opts.get("pageLoadTimeout", 60000),
                "setupNodeEvents": "(on, config) => { /* node event listeners */ }"
            },
            "component": {
                "devServer": {
                    "framework": opts.get("framework", "react"),
                    "bundler": opts.get("bundler", "webpack")
                },
                "specPattern": "cypress/component/**/*.cy.js"
            }
        }
        
        return f'''const {{ defineConfig }} = require('cypress');

module.exports = defineConfig({json.dumps(config, indent=2)});
'''
    
    def generate_support_file(self, custom_commands: Optional[List[Dict]] = None) -> str:
        """
        生成support/e2e.js文件
        
        Args:
            custom_commands: 自定义命令列表
            
        Returns:
            support文件内容
        """
        commands = []
        
        if custom_commands:
            for cmd in custom_commands:
                commands.append(self.generate_custom_command(
                    cmd["name"],
                    cmd["implementation"],
                    cmd.get("options")
                ))
        
        default_content = '''// Cypress support file
// This file runs before every test

// Import commands.js using ES2015 syntax:
import './commands';

// Alternatively you can use CommonJS syntax:
// require('./commands');

// Hide fetch/XHR requests from command log
const app = window.top;
if (!app.document.head.querySelector('[data-hide-command-log-request]')) {
  const style = app.document.createElement('style');
  style.innerHTML = '.command-name-request, .command-name-xhr { display: none }';
  style.setAttribute('data-hide-command-log-request', '');
  app.document.head.appendChild(style);
}

// Global beforeEach
beforeEach(() => {
  // Reset state before each test
  cy.clearCookies();
  cy.clearLocalStorage();
});
'''
        
        if commands:
            return default_content + "\n// Custom Commands\n" + "\n".join(commands)
        
        return default_content
    
    def analyze_test_results(self, results: Dict) -> Dict[str, Any]:
        """
        分析测试结果
        
        Args:
            results: 测试结果数据
            
        Returns:
            分析报告
        """
        total_tests = results.get("totalTests", 0)
        passed = results.get("totalPassed", 0)
        failed = results.get("totalFailed", 0)
        pending = results.get("totalPending", 0)
        skipped = results.get("totalSkipped", 0)
        duration = results.get("totalDuration", 0)
        
        pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        return {
            "summary": {
                "total": total_tests,
                "passed": passed,
                "failed": failed,
                "pending": pending,
                "skipped": skipped,
                "pass_rate": round(pass_rate, 2),
                "duration_ms": duration
            },
            "failed_tests": results.get("failures", []),
            "timestamp": datetime.now().isoformat()
        }
    
    def setup_project(self, project_path: str, options: Optional[Dict] = None) -> Dict[str, str]:
        """
        设置Cypress项目结构
        
        Args:
            project_path: 项目路径
            options: 选项
            
        Returns:
            生成的文件内容字典
        """
        files = {}
        
        # cypress.config.js
        files["cypress.config.js"] = self.generate_cypress_config(options)
        
        # support files
        files["cypress/support/e2e.js"] = self.generate_support_file()
        files["cypress/support/commands.js"] = '''// Custom commands
declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Custom command to select DOM element by data-testid attribute.
       * @example cy.dataTestId('greeting')
       */
      dataTestId(value: string): Chainable<Element>
    }
  }
}

Cypress.Commands.add('dataTestId', (value) => {
  return cy.get(`[data-testid=${value}]`);
});
'''
        
        # fixtures
        files["cypress/fixtures/example.json"] = self.generate_fixture(
            "example",
            {
                "user": {"name": "Test User", "email": "test@example.com"},
                "products": [{"id": 1, "name": "Product 1"}]
            }
        )
        
        # sample test
        files["cypress/e2e/example.cy.js"] = self.generate_test(
            suite_name="Example Test Suite",
            url=self.base_url,
            actions=[
                {"action": "visit", "value": self.base_url},
                {"action": "click", "target": "button"}
            ],
            assertions=[
                {"target": "h1", "assertion": "exist"},
                {"target": ".content", "assertion": "be.visible"}
            ]
        )
        
        return files


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cypress E2E Testing Skill')
    parser.add_argument('action', choices=['test', 'page', 'fixture', 'config', 'setup'])
    parser.add_argument('--name', '-n', help='Name for test/page/fixture')
    parser.add_argument('--url', '-u', help='URL for test/page')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--base-url', default='http://localhost:3000', help='Base URL')
    
    args = parser.parse_args()
    
    skill = CypressSkill(base_url=args.base_url)
    
    if args.action == 'test':
        code = skill.generate_test(
            suite_name=args.name or "Test Suite",
            url=args.url or args.base_url,
            actions=[{"action": "visit", "value": args.url}],
            assertions=[{"target": "body", "assertion": "exist"}]
        )
        print(code)
        
    elif args.action == 'page':
        code = skill.generate_page_object(
            page_name=args.name or "Home",
            url=args.url or args.base_url,
            elements=[
                {"name": "header", "selector": "header", "element_type": "text"},
                {"name": "submitButton", "selector": "button[type=submit]", "element_type": "button"}
            ]
        )
        print(code)
        
    elif args.action == 'config':
        config = skill.generate_cypress_config()
        print(config)
        
    elif args.action == 'setup':
        files = skill.setup_project('.')
        for filename, content in files.items():
            print(f"\n=== {filename} ===")
            print(content[:500] + "..." if len(content) > 500 else content)


if __name__ == '__main__':
    main()
