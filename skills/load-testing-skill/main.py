#!/usr/bin/env python3
"""
Load Testing Skill

负载测试工具智能助手。Use when writing tests, automating testing, 
or when user mentions 'load testing', 'stress testing', 'performance testing', 'Locust', 'k6', 'JMeter'.

Capabilities:
- Locust脚本生成: 生成Python Locust负载测试脚本
- k6脚本生成: 生成JavaScript k6负载测试脚本
- 测试场景设计: 设计负载测试场景和策略
- 报告分析: 分析性能测试结果
- 阈值配置: 配置性能指标阈值
- 分布式测试: 生成分布式测试配置
"""

import json
import re
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from pathlib import Path
from datetime import datetime
from enum import Enum


class LoadTestTool(str, Enum):
    """负载测试工具类型"""
    LOCUST = "locust"
    K6 = "k6"
    JMETER = "jmeter"
    ARTILLERY = "artillery"


class LoadPattern(str, Enum):
    """负载模式"""
    CONSTANT = "constant"           # 恒定负载
    RAMP_UP = "ramp_up"            # 逐步增加
    RAMP_UP_DOWN = "ramp_up_down"  # 增加后减少
    SPIKE = "spike"                # 峰值测试
    STRESS = "stress"              # 压力测试
    SOAK = "soak"                  # 浸泡测试


@dataclass
class Endpoint:
    """API端点定义"""
    path: str
    method: str = "GET"
    weight: int = 1
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict] = None
    params: Optional[Dict] = None
    expect_status: int = 200
    response_time_threshold: int = 500  # ms


@dataclass
class LoadProfile:
    """负载配置"""
    name: str
    pattern: LoadPattern
    users: int = 10
    spawn_rate: int = 1
    duration: str = "5m"
    ramp_up: Optional[str] = None
    ramp_down: Optional[str] = None
    
    def to_locust_config(self) -> str:
        """转换为Locust配置"""
        if self.pattern == LoadPattern.CONSTANT:
            return f"""
    @task
    def constant_load(self):
        self.run_tasks()
"""
        elif self.pattern == LoadPattern.RAMP_UP:
            return f"""
    wait_time = between(1, {max(1, 10 - self.spawn_rate)})
"""
        return ""
    
    def to_k6_options(self) -> Dict:
        """转换为k6选项"""
        stages = []
        duration_sec = self._parse_duration(self.duration)
        
        if self.pattern == LoadPattern.CONSTANT:
            stages = [
                {"duration": self.duration, "target": self.users}
            ]
        elif self.pattern == LoadPattern.RAMP_UP:
            stages = [
                {"duration": self.ramp_up or "2m", "target": self.users},
                {"duration": self.duration, "target": self.users}
            ]
        elif self.pattern == LoadPattern.RAMP_UP_DOWN:
            mid_duration = duration_sec // 2
            stages = [
                {"duration": self.ramp_up or "2m", "target": self.users},
                {"duration": f"{mid_duration}s", "target": self.users},
                {"duration": self.ramp_down or "2m", "target": 0}
            ]
        elif self.pattern == LoadPattern.SPIKE:
            stages = [
                {"duration": "10s", "target": self.users},
                {"duration": self.duration, "target": self.users},
                {"duration": "10s", "target": 0}
            ]
        
        return {"stages": stages}
    
    def _parse_duration(self, duration: str) -> int:
        """解析持续时间字符串为秒"""
        match = re.match(r'(\d+)([smhd])', duration)
        if match:
            value, unit = int(match.group(1)), match.group(2)
            multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
            return value * multipliers.get(unit, 1)
        return 300  # 默认5分钟


@dataclass
class Threshold:
    """性能阈值"""
    metric: str  # http_req_duration, http_req_failed, etc.
    condition: str  # <, >, <=, >=
    value: float
    abort_on_fail: bool = False


class LoadTestingSkill:
    """负载测试Skill主类"""
    
    def __init__(self, default_host: str = "http://localhost:3000"):
        self.default_host = default_host
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """加载模板"""
        return {
            "locustfile": '''from locust import HttpUser, task, between, events
from locust.runners import MasterRunner
{imports}

{config}

class {user_class_name}(HttpUser):
    host = "{host}"
    wait_time = between({min_wait}, {max_wait})
    {weight}
    
    def on_start(self):
        """Setup for each user"""
        {on_start}
    
    def on_stop(self):
        """Teardown for each user"""
        {on_stop}
    
    {tasks}

{event_handlers}
''',
            "k6_script": '''import http from 'k6/http';
import {{ check, sleep, group }} from 'k6';
import {{ Rate, Trend, Counter, Gauge }} from 'k6/metrics';
{imports}

{custom_metrics}

export const options = {options};

{setup_teardown}

export default function() {{
  {main_function}
}}
''',
            "jmeter_test_plan": '''<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="{test_name}">
      {test_plan_content}
    </TestPlan>
  </hashTree>
</jmeterTestPlan>
'''
        }
    
    def generate_locust_script(
        self,
        host: str,
        endpoints: List[Union[Endpoint, Dict]],
        options: Optional[Dict] = None
    ) -> str:
        """
        生成Locust测试脚本
        
        Args:
            host: 目标主机
            endpoints: 端点列表
            options: 选项
            
        Returns:
            Locust脚本内容
        """
        opts = options or {}
        
        # 转换端点
        endpoint_objects = [e if isinstance(e, Endpoint) else Endpoint(**e) for e in endpoints]
        
        # 生成任务
        tasks = []
        for i, endpoint in enumerate(endpoint_objects):
            task_code = self._generate_locust_task(endpoint, i)
            tasks.append(task_code)
        
        # 事件处理器
        event_handlers = self._generate_locust_events(opts.get("events", {}))
        
        # 组装脚本
        return self.templates["locustfile"].format(
            imports=opts.get("imports", ""),
            config=opts.get("config", ""),
            user_class_name=opts.get("user_class", "LoadTestUser"),
            host=host,
            min_wait=opts.get("min_wait", 1),
            max_wait=opts.get("max_wait", 5),
            weight=f"\n    weight = {opts.get('weight', 1)}" if opts.get('weight') else "",
            on_start=opts.get("on_start", "pass"),
            on_stop=opts.get("on_stop", "pass"),
            tasks="\n    ".join(tasks),
            event_handlers=event_handlers
        )
    
    def _generate_locust_task(self, endpoint: Endpoint, index: int) -> str:
        """生成Locust任务"""
        task_name = f"task_{endpoint.method.lower()}_{index}"
        
        headers_code = ""
        if endpoint.headers:
            headers_str = json.dumps(endpoint.headers)
            headers_code = f", headers={headers_str}"
        
        body_code = ""
        if endpoint.body:
            body_str = json.dumps(endpoint.body)
            body_code = f", json={body_str}"
        
        return f'''@task({endpoint.weight})
    def {task_name}(self):
        with self.client.{endpoint.method.lower()}("{endpoint.path}"{headers_code}{body_code}, catch_response=True) as response:
            if response.status_code == {endpoint.expect_status}:
                response.success()
            else:
                response.failure(f"Unexpected status: {{response.status_code}}")'''
    
    def _generate_locust_events(self, events: Dict) -> str:
        """生成Locust事件处理器"""
        handlers = []
        
        if events.get("test_start"):
            handlers.append(f'''
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("Test started")
    {events["test_start"]}''')
        
        if events.get("test_stop"):
            handlers.append(f'''
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("Test stopped")
    {events["test_stop"]}''')
        
        if events.get("request"):
            handlers.append(f'''
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    {events["request"]}''')
        
        return "\n".join(handlers)
    
    def generate_k6_script(
        self,
        url: str,
        scenarios: Optional[Dict[str, Dict]] = None,
        endpoints: Optional[List[Union[Endpoint, Dict]]] = None,
        thresholds: Optional[List[Union[Threshold, Dict]]] = None,
        options: Optional[Dict] = None
    ) -> str:
        """
        生成k6测试脚本
        
        Args:
            url: 目标URL
            scenarios: 场景配置
            endpoints: 端点列表
            thresholds: 阈值列表
            options: 选项
            
        Returns:
            k6脚本内容
        """
        opts = options or {}
        
        # 生成选项
        k6_options = self._generate_k6_options(scenarios, thresholds, opts)
        
        # 生成主函数
        main_function = self._generate_k6_main_function(url, endpoints, opts)
        
        # 自定义指标
        custom_metrics = self._generate_k6_custom_metrics(opts.get("metrics", []))
        
        # 设置和清理
        setup_teardown = self._generate_k6_setup_teardown(opts)
        
        return self.templates["k6_script"].format(
            imports=opts.get("imports", ""),
            custom_metrics=custom_metrics,
            options=json.dumps(k6_options, indent=2),
            setup_teardown=setup_teardown,
            main_function=main_function
        )
    
    def _generate_k6_options(
        self,
        scenarios: Optional[Dict],
        thresholds: Optional[List],
        options: Dict
    ) -> Dict:
        """生成k6选项"""
        k6_options = {}
        
        # 场景配置
        if scenarios:
            k6_options["scenarios"] = {}
            for name, config in scenarios.items():
                k6_options["scenarios"][name] = {
                    "executor": config.get("executor", "ramping-vus"),
                    "startVUs": config.get("startVUs", 0),
                    "stages": config.get("stages", []),
                    "gracefulRampDown": config.get("gracefulRampDown", "30s")
                }
        else:
            # 默认配置
            k6_options["stages"] = [
                {"duration": "2m", "target": 10},
                {"duration": "5m", "target": 10},
                {"duration": "2m", "target": 0}
            ]
        
        # 阈值配置
        if thresholds:
            k6_options["thresholds"] = {}
            for threshold in thresholds:
                t = threshold if isinstance(threshold, Threshold) else Threshold(**threshold)
                k6_options["thresholds"][t.metric] = [f"{t.condition}{t.value}"]
        else:
            k6_options["thresholds"] = {
                "http_req_duration": ["p(95)<500"],
                "http_req_failed": ["rate<0.1"]
            }
        
        # 其他选项
        if options.get("vus"):
            k6_options["vus"] = options["vus"]
        if options.get("duration"):
            k6_options["duration"] = options["duration"]
        
        return k6_options
    
    def _generate_k6_main_function(
        self,
        base_url: str,
        endpoints: Optional[List],
        options: Dict
    ) -> str:
        """生成k6主函数"""
        if not endpoints:
            # 默认示例
            return f'''
  const response = http.get('{base_url}');
  
  check(response, {{
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  }});
  
  sleep(1);
'''
        
        lines = []
        endpoint_objects = [e if isinstance(e, Endpoint) else Endpoint(**e) for e in endpoints]
        
        for endpoint in endpoint_objects:
            lines.append(f'''
  group('{endpoint.method} {endpoint.path}', () => {{
    const response = http.{endpoint.method.lower()}('{base_url}{endpoint.path}');
    
    check(response, {{
      'status is {endpoint.expect_status}': (r) => r.status === {endpoint.expect_status},
      'response time < {endpoint.response_time_threshold}ms': (r) => r.timings.duration < {endpoint.response_time_threshold},
    }});
  }});
  
  sleep(1);
''')
        
        return "".join(lines)
    
    def _generate_k6_custom_metrics(self, metrics: List[Dict]) -> str:
        """生成k6自定义指标"""
        lines = []
        
        for metric in metrics:
            metric_type = metric.get("type", "Trend")
            name = metric.get("name", "custom_metric")
            lines.append(f"const {name} = new {metric_type}('{name}');")
        
        return "\n".join(lines) if lines else ""
    
    def _generate_k6_setup_teardown(self, options: Dict) -> str:
        """生成k6设置和清理代码"""
        lines = []
        
        if options.get("setup"):
            lines.append(f'''export function setup() {{
  {options["setup"]}
  return {{}};
}}''')
        
        if options.get("teardown"):
            lines.append(f'''export function teardown(data) {{
  {options["teardown"]}
}}''')
        
        return "\n\n".join(lines)
    
    def generate_load_scenario(
        self,
        name: str,
        pattern: LoadPattern,
        users: int,
        duration: str,
        options: Optional[Dict] = None
    ) -> Dict:
        """
        生成负载场景配置
        
        Args:
            name: 场景名称
            pattern: 负载模式
            users: 用户数
            duration: 持续时间
            options: 选项
            
        Returns:
            场景配置
        """
        profile = LoadProfile(
            name=name,
            pattern=pattern,
            users=users,
            duration=duration,
            **(options or {})
        )
        
        return {
            "name": name,
            "pattern": pattern.value,
            "locust_config": profile.to_locust_config(),
            "k6_options": profile.to_k6_options()
        }
    
    def generate_distributed_config(
        self,
        tool: LoadTestTool,
        workers: int,
        master_host: str = "localhost",
        options: Optional[Dict] = None
    ) -> str:
        """
        生成分布式测试配置
        
        Args:
            tool: 测试工具
            workers: worker数量
            master_host: master主机
            options: 选项
            
        Returns:
            配置文件内容
        """
        if tool == LoadTestTool.LOCUST:
            return f'''# Locust分布式配置
# Master节点启动:
# locust -f locustfile.py --master --master-bind-host={master_host} --master-bind-port=5557

# Worker节点启动 (在每个worker上执行):
# locust -f locustfile.py --worker --master-host={master_host} --master-port=5557

# 预期Worker数量: {workers}
'''
        elif tool == LoadTestTool.K6:
            return f'''// k6分布式配置使用k6 cloud或xk6-disruptor
// 或使用k6 cloud运行:
// k6 cloud script.js

// 或使用Docker Compose部署多个实例
version: '3'
services:
  influxdb:
    image: influxdb:1.8
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
  
  k6-{workers}workers:
    image: grafana/k6
    command: run --out influxdb=http://influxdb:8086/k6 /script.js
    volumes:
      - ./script.js:/script.js
'''
        
        return ""
    
    def analyze_results(
        self,
        results: Dict,
        thresholds: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        分析测试结果
        
        Args:
            results: 原始结果数据
            thresholds: 阈值配置
            
        Returns:
            分析报告
        """
        thresholds = thresholds or {}
        
        analysis = {
            "summary": {},
            "metrics": {},
            "bottlenecks": [],
            "recommendations": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # 解析基本指标
        if "requests" in results:
            total_requests = results["requests"]
            failed_requests = results.get("failures", 0)
            analysis["summary"]["total_requests"] = total_requests
            analysis["summary"]["failed_requests"] = failed_requests
            analysis["summary"]["error_rate"] = failed_requests / total_requests if total_requests > 0 else 0
        
        # 响应时间分析
        if "response_times" in results:
            times = results["response_times"]
            analysis["metrics"]["avg_response_time"] = sum(times) / len(times)
            analysis["metrics"]["min_response_time"] = min(times)
            analysis["metrics"]["max_response_time"] = max(times)
            analysis["metrics"]["p50"] = sorted(times)[len(times) // 2]
            analysis["metrics"]["p95"] = sorted(times)[int(len(times) * 0.95)]
            analysis["metrics"]["p99"] = sorted(times)[int(len(times) * 0.99)]
        
        # 吞吐量分析
        if "throughput" in results:
            analysis["metrics"]["throughput_rps"] = results["throughput"]
        
        # 检查瓶颈
        if analysis["metrics"].get("p95", 0) > thresholds.get("p95", 500):
            analysis["bottlenecks"].append("High 95th percentile response time")
            analysis["recommendations"].append("Consider optimizing database queries or adding caching")
        
        if analysis["summary"].get("error_rate", 0) > thresholds.get("error_rate", 0.01):
            analysis["bottlenecks"].append("High error rate detected")
            analysis["recommendations"].append("Review error logs and fix failing endpoints")
        
        return analysis
    
    def generate_report(
        self,
        results: Dict,
        output_format: str = "html"
    ) -> str:
        """
        生成测试报告
        
        Args:
            results: 测试结果
            output_format: 输出格式
            
        Returns:
            报告内容
        """
        analysis = self.analyze_results(results)
        
        if output_format == "html":
            return self._generate_html_report(analysis)
        elif output_format == "markdown":
            return self._generate_markdown_report(analysis)
        else:
            return json.dumps(analysis, indent=2)
    
    def _generate_html_report(self, analysis: Dict) -> str:
        """生成HTML报告"""
        return f'''<!DOCTYPE html>
<html>
<head>
    <title>Load Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
        .metric {{ margin: 10px 0; }}
        .bottleneck {{ color: #d9534f; }}
        .recommendation {{ color: #5bc0de; }}
    </style>
</head>
<body>
    <h1>Load Test Report</h1>
    <p>Generated at: {analysis["timestamp"]}</p>
    
    <div class="summary">
        <h2>Summary</h2>
        {self._dict_to_html(analysis.get("summary", {}))}
    </div>
    
    <div class="metrics">
        <h2>Metrics</h2>
        {self._dict_to_html(analysis.get("metrics", {}))}
    </div>
    
    <div class="bottlenecks">
        <h2>Bottlenecks</h2>
        <ul>{''.join(f"<li class='bottleneck'>{b}</li>" for b in analysis.get("bottlenecks", []))}</ul>
    </div>
    
    <div class="recommendations">
        <h2>Recommendations</h2>
        <ul>{''.join(f"<li class='recommendation'>{r}</li>" for r in analysis.get("recommendations", []))}</ul>
    </div>
</body>
</html>'''
    
    def _generate_markdown_report(self, analysis: Dict) -> str:
        """生成Markdown报告"""
        lines = [
            "# Load Test Report",
            f"\nGenerated at: {analysis['timestamp']}",
            "\n## Summary",
            self._dict_to_markdown(analysis.get("summary", {})),
            "\n## Metrics",
            self._dict_to_markdown(analysis.get("metrics", {})),
            "\n## Bottlenecks",
        ]
        
        for bottleneck in analysis.get("bottlenecks", []):
            lines.append(f"- ⚠️ {bottleneck}")
        
        lines.append("\n## Recommendations")
        for rec in analysis.get("recommendations", []):
            lines.append(f"- 💡 {rec}")
        
        return "\n".join(lines)
    
    def _dict_to_html(self, d: Dict) -> str:
        """字典转HTML"""
        items = [f"<div class='metric'><strong>{k}:</strong> {v}</div>" for k, v in d.items()]
        return "".join(items)
    
    def _dict_to_markdown(self, d: Dict) -> str:
        """字典转Markdown"""
        items = [f"- **{k}:** {v}" for k, v in d.items()]
        return "\n".join(items)
    
    def setup_project(self, project_path: str, tools: List[LoadTestTool] = None) -> Dict[str, str]:
        """
        设置负载测试项目
        
        Args:
            project_path: 项目路径
            tools: 工具列表
            
        Returns:
            生成的文件字典
        """
        tools = tools or [LoadTestTool.LOCUST, LoadTestTool.K6]
        files = {}
        
        # Locust
        if LoadTestTool.LOCUST in tools:
            files["locustfile.py"] = self.generate_locust_script(
                host=self.default_host,
                endpoints=[
                    Endpoint(path="/api/users", method="GET", weight=3),
                    Endpoint(path="/api/users", method="POST", weight=1)
                ]
            )
        
        # k6
        if LoadTestTool.K6 in tools:
            files["script.js"] = self.generate_k6_script(
                url=self.default_host,
                scenarios={
                    "smoke": {"vus": 10, "duration": "1m"},
                    "load": {"stages": [
                        {"duration": "2m", "target": 50},
                        {"duration": "5m", "target": 50},
                        {"duration": "2m", "target": 0}
                    ]}
                }
            )
        
        # Docker Compose
        files["docker-compose.yml"] = '''version: '3'
services:
  locust:
    image: locustio/locust
    ports:
      - "8089:8089"
    volumes:
      - ./locustfile.py:/mnt/locust/locustfile.py
    command: -f /mnt/locust/locustfile.py --host=http://target

  k6:
    image: grafana/k6
    volumes:
      - ./script.js:/script.js
    command: run /script.js
'''
        
        return files


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Load Testing Skill')
    parser.add_argument('action', choices=['locust', 'k6', 'scenario', 'report', 'setup'])
    parser.add_argument('--host', '-h', default='http://localhost:3000', help='Target host')
    parser.add_argument('--users', '-u', type=int, default=10, help='Number of users')
    parser.add_argument('--duration', '-d', default='5m', help='Test duration')
    parser.add_argument('--output', '-o', help='Output file')
    
    args = parser.parse_args()
    
    skill = LoadTestingSkill(default_host=args.host)
    
    if args.action == 'locust':
        code = skill.generate_locust_script(
            host=args.host,
            endpoints=[
                {"path": "/api/users", "method": "GET", "weight": 3},
                {"path": "/api/users", "method": "POST", "weight": 1}
            ]
        )
        print(code)
        
    elif args.action == 'k6':
        code = skill.generate_k6_script(
            url=args.host,
            options={"vus": args.users, "duration": args.duration}
        )
        print(code)
        
    elif args.action == 'scenario':
        scenario = skill.generate_load_scenario(
            name="load_test",
            pattern=LoadPattern.RAMP_UP,
            users=args.users,
            duration=args.duration
        )
        print(json.dumps(scenario, indent=2))
        
    elif args.action == 'setup':
        files = skill.setup_project('.')
        for filename, content in files.items():
            print(f"\n=== {filename} ===")
            print(content[:500] + "..." if len(content) > 500 else content)


if __name__ == '__main__':
    main()
