#!/usr/bin/env python3
"""
Load Testing Skill 测试套件
"""

import unittest
import json
from main import (
    LoadTestingSkill, LoadTestTool, LoadPattern,
    Endpoint, LoadProfile, Threshold
)


class TestLoadTestingSkill(unittest.TestCase):
    """Load Testing Skill 测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.skill = LoadTestingSkill(default_host="http://localhost:3000")
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.skill.default_host, "http://localhost:3000")
        self.assertIsNotNone(self.skill.templates)
    
    def test_generate_locust_script_basic(self):
        """测试生成基础Locust脚本"""
        code = self.skill.generate_locust_script(
            host="http://api.example.com",
            endpoints=[
                Endpoint(path="/users", method="GET", weight=3),
                Endpoint(path="/users", method="POST", weight=1)
            ]
        )
        
        self.assertIn("from locust import HttpUser, task, between", code)
        self.assertIn("host = \"http://api.example.com\"", code)
        self.assertIn("@task(3)", code)
        self.assertIn("@task(1)", code)
        self.assertIn("def task_get_0", code)
        self.assertIn("def task_post_1", code)
    
    def test_generate_locust_script_with_headers(self):
        """测试生成带Headers的Locust脚本"""
        code = self.skill.generate_locust_script(
            host="http://api.example.com",
            endpoints=[
                Endpoint(
                    path="/api/protected",
                    method="GET",
                    headers={"Authorization": "Bearer token123"}
                )
            ]
        )
        
        self.assertIn("\"Authorization\": \"Bearer token123\"", code)
    
    def test_generate_locust_script_with_body(self):
        """测试生成带Body的Locust脚本"""
        code = self.skill.generate_locust_script(
            host="http://api.example.com",
            endpoints=[
                Endpoint(
                    path="/users",
                    method="POST",
                    body={"name": "John", "email": "john@example.com"}
                )
            ]
        )
        
        self.assertIn('"name": "John"', code)
    
    def test_generate_k6_script_basic(self):
        """测试生成基础k6脚本"""
        code = self.skill.generate_k6_script(
            url="http://api.example.com",
            options={"vus": 10, "duration": "5m"}
        )
        
        self.assertIn("import http from 'k6/http'", code)
        self.assertIn("export const options", code)
        self.assertIn("http.get('http://api.example.com')", code)
        self.assertIn("check(response", code)
    
    def test_generate_k6_script_with_scenarios(self):
        """测试生成带场景的k6脚本"""
        code = self.skill.generate_k6_script(
            url="http://api.example.com",
            scenarios={
                "smoke": {
                    "executor": "ramping-vus",
                    "startVUs": 0,
                    "stages": [
                        {"duration": "1m", "target": 10}
                    ]
                }
            }
        )
        
        self.assertIn("scenarios", code)
        self.assertIn("smoke", code)
    
    def test_generate_k6_script_with_thresholds(self):
        """测试生成带阈值的k6脚本"""
        code = self.skill.generate_k6_script(
            url="http://api.example.com",
            thresholds=[
                Threshold(metric="http_req_duration", condition="<", value=500),
                Threshold(metric="http_req_failed", condition="<", value=0.1)
            ]
        )
        
        self.assertIn("thresholds", code)
        self.assertIn("http_req_duration", code)
    
    def test_generate_k6_script_with_endpoints(self):
        """测试生成带多个端点的k6脚本"""
        code = self.skill.generate_k6_script(
            url="http://api.example.com",
            endpoints=[
                Endpoint(path="/users", method="GET"),
                Endpoint(path="/products", method="GET")
            ]
        )
        
        self.assertIn("group('GET /users'", code)
        self.assertIn("group('GET /products'", code)
    
    def test_generate_load_scenario_constant(self):
        """测试生成恒定负载场景"""
        scenario = self.skill.generate_load_scenario(
            name="constant_load",
            pattern=LoadPattern.CONSTANT,
            users=50,
            duration="5m"
        )
        
        self.assertEqual(scenario["name"], "constant_load")
        self.assertEqual(scenario["pattern"], "constant")
        self.assertIn("locust_config", scenario)
        self.assertIn("k6_options", scenario)
    
    def test_generate_load_scenario_ramp_up(self):
        """测试生成递增负载场景"""
        scenario = self.skill.generate_load_scenario(
            name="ramp_up",
            pattern=LoadPattern.RAMP_UP,
            users=100,
            duration="10m",
            options={"ramp_up": "3m"}
        )
        
        k6_stages = scenario["k6_options"]["stages"]
        self.assertEqual(len(k6_stages), 2)
        self.assertEqual(k6_stages[0]["target"], 100)
    
    def test_generate_load_scenario_ramp_up_down(self):
        """测试生成递增递减场景"""
        scenario = self.skill.generate_load_scenario(
            name="ramp_up_down",
            pattern=LoadPattern.RAMP_UP_DOWN,
            users=100,
            duration="10m",
            options={"ramp_up": "2m", "ramp_down": "2m"}
        )
        
        k6_stages = scenario["k6_options"]["stages"]
        self.assertEqual(len(k6_stages), 3)
        self.assertEqual(k6_stages[2]["target"], 0)
    
    def test_generate_distributed_config_locust(self):
        """测试生成Locust分布式配置"""
        config = self.skill.generate_distributed_config(
            tool=LoadTestTool.LOCUST,
            workers=5,
            master_host="192.168.1.100"
        )
        
        self.assertIn("--master", config)
        self.assertIn("--worker", config)
        self.assertIn("192.168.1.100", config)
        self.assertIn("预期Worker数量: 5", config)
    
    def test_generate_distributed_config_k6(self):
        """测试生成k6分布式配置"""
        config = self.skill.generate_distributed_config(
            tool=LoadTestTool.K6,
            workers=3
        )
        
        self.assertIn("docker-compose", config)
        self.assertIn("influxdb", config)
        self.assertIn("grafana", config)
    
    def test_analyze_results_basic(self):
        """测试基础结果分析"""
        results = {
            "requests": 1000,
            "failures": 10,
            "response_times": [100, 200, 150, 300, 250] * 200,
            "throughput": 50.5
        }
        
        analysis = self.skill.analyze_results(results)
        
        self.assertEqual(analysis["summary"]["total_requests"], 1000)
        self.assertEqual(analysis["summary"]["failed_requests"], 10)
        self.assertEqual(analysis["summary"]["error_rate"], 0.01)
        self.assertIn("metrics", analysis)
    
    def test_analyze_results_with_bottlenecks(self):
        """测试带瓶颈的结果分析"""
        results = {
            "requests": 1000,
            "failures": 100,
            "response_times": [100, 200, 500, 1000, 2000] * 200,
            "throughput": 20.0
        }
        
        analysis = self.skill.analyze_results(
            results,
            thresholds={"p95": 500, "error_rate": 0.05}
        )
        
        self.assertGreater(len(analysis["bottlenecks"]), 0)
        self.assertGreater(len(analysis["recommendations"]), 0)
    
    def test_generate_report_html(self):
        """测试生成HTML报告"""
        results = {
            "requests": 1000,
            "failures": 10,
            "response_times": [100] * 1000,
            "throughput": 50.0
        }
        
        report = self.skill.generate_report(results, output_format="html")
        
        self.assertIn("<!DOCTYPE html>", report)
        self.assertIn("Load Test Report", report)
        self.assertIn("<div class=\"summary\">", report)
    
    def test_generate_report_markdown(self):
        """测试生成Markdown报告"""
        results = {
            "requests": 1000,
            "failures": 10,
            "response_times": [100] * 1000,
            "throughput": 50.0
        }
        
        report = self.skill.generate_report(results, output_format="markdown")
        
        self.assertIn("# Load Test Report", report)
        self.assertIn("## Summary", report)
    
    def test_setup_project(self):
        """测试设置项目"""
        files = self.skill.setup_project(
            "./test-project",
            tools=[LoadTestTool.LOCUST, LoadTestTool.K6]
        )
        
        self.assertIn("locustfile.py", files)
        self.assertIn("script.js", files)
        self.assertIn("docker-compose.yml", files)
    
    def test_load_profile_to_k6_options_constant(self):
        """测试恒定负载配置转换"""
        profile = LoadProfile(
            name="constant",
            pattern=LoadPattern.CONSTANT,
            users=50,
            duration="5m"
        )
        
        options = profile.to_k6_options()
        
        self.assertEqual(len(options["stages"]), 1)
        self.assertEqual(options["stages"][0]["target"], 50)
    
    def test_load_profile_to_k6_options_spike(self):
        """测试峰值负载配置转换"""
        profile = LoadProfile(
            name="spike",
            pattern=LoadPattern.SPIKE,
            users=200,
            duration="2m"
        )
        
        options = profile.to_k6_options()
        
        self.assertEqual(len(options["stages"]), 3)
        self.assertEqual(options["stages"][0]["duration"], "10s")
    
    def test_parse_duration(self):
        """测试持续时间解析"""
        profile = LoadProfile(
            name="test",
            pattern=LoadPattern.CONSTANT,
            users=10,
            duration="5m"
        )
        
        self.assertEqual(profile._parse_duration("30s"), 30)
        self.assertEqual(profile._parse_duration("5m"), 300)
        self.assertEqual(profile._parse_duration("2h"), 7200)
        self.assertEqual(profile._parse_duration("1d"), 86400)


class TestLoadTestingSkillIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        self.skill = LoadTestingSkill()
    
    def test_full_locust_workflow(self):
        """测试完整Locust工作流"""
        # 1. 生成脚本
        script = self.skill.generate_locust_script(
            host="http://api.example.com",
            endpoints=[
                Endpoint(path="/users", method="GET"),
                Endpoint(path="/posts", method="GET"),
                Endpoint(path="/users", method="POST", body={"name": "test"})
            ]
        )
        self.assertIsNotNone(script)
        
        # 2. 生成分布式配置
        config = self.skill.generate_distributed_config(
            tool=LoadTestTool.LOCUST,
            workers=3
        )
        self.assertIsNotNone(config)
        
        # 3. 设置项目
        files = self.skill.setup_project(".", tools=[LoadTestTool.LOCUST])
        self.assertIn("locustfile.py", files)
    
    def test_full_k6_workflow(self):
        """测试完整k6工作流"""
        # 1. 生成脚本
        script = self.skill.generate_k6_script(
            url="http://api.example.com",
            scenarios={
                "smoke": {"vus": 10, "duration": "1m"}
            },
            thresholds=[
                Threshold(metric="http_req_duration", condition="<", value=200)
            ]
        )
        self.assertIsNotNone(script)
        
        # 2. 生成场景
        scenario = self.skill.generate_load_scenario(
            name="stress_test",
            pattern=LoadPattern.STRESS,
            users=500,
            duration="10m"
        )
        self.assertIsNotNone(scenario)
        
        # 3. 设置项目
        files = self.skill.setup_project(".", tools=[LoadTestTool.K6])
        self.assertIn("script.js", files)
    
    def test_analyze_and_report(self):
        """测试分析和报告"""
        # 模拟测试结果
        results = {
            "requests": 10000,
            "failures": 50,
            "response_times": list(range(50, 550)) * 20,
            "throughput": 100.0
        }
        
        # 分析结果
        analysis = self.skill.analyze_results(results)
        self.assertIsNotNone(analysis)
        
        # 生成报告
        html_report = self.skill.generate_report(results, "html")
        self.assertIn("<!DOCTYPE html>", html_report)
        
        markdown_report = self.skill.generate_report(results, "markdown")
        self.assertIn("# Load Test Report", markdown_report)


def run_tests():
    """运行测试套件"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestLoadTestingSkill))
    suite.addTests(loader.loadTestsFromTestCase(TestLoadTestingSkillIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
