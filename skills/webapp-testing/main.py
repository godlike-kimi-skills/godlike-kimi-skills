"""
Web Application Testing Skill
=============================

完整的Web应用端到端测试解决方案，基于Playwright实现。
支持多浏览器测试、视觉回归测试、性能测试和截图对比。

Author: Godlike Kimi Skills
License: MIT
Version: 1.0.0
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import Image, ImageChops

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TestConfig:
    """测试配置数据类"""
    url: str = ""
    browser: str = "chromium"  # chromium, firefox, webkit
    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    timeout: int = 30000
    screenshot_path: Optional[str] = None
    baseline_path: Optional[str] = None
    output_dir: str = "./test-results"
    threshold: float = 0.1
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    url: str
    timestamp: str
    load_time_ms: float
    dom_content_loaded_ms: float
    first_paint_ms: Optional[float] = None
    first_contentful_paint_ms: Optional[float] = None
    largest_contentful_paint_ms: Optional[float] = None
    time_to_interactive_ms: Optional[float] = None
    total_resource_size_kb: float = 0.0
    resource_count: int = 0
    error_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class ScreenshotComparisonResult:
    """截图对比结果数据类"""
    baseline_path: str
    current_path: str
    diff_path: Optional[str]
    similarity_score: float
    pixel_diff_count: int
    passed: bool
    threshold: float
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


class WebAppTester:
    """Web应用测试器主类"""
    
    def __init__(self, config: TestConfig):
        """
        初始化测试器
        
        Args:
            config: 测试配置
        """
        self.config = config
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        from playwright.async_api import async_playwright
        
        self._playwright = await async_playwright().start()
        
        # 启动浏览器
        browser_type = getattr(self._playwright, self.config.browser)
        self._browser = await browser_type.launch(headless=self.config.headless)
        
        # 创建上下文
        self._context = await self._browser.new_context(
            viewport={'width': self.config.viewport_width, 'height': self.config.viewport_height}
        )
        
        # 创建页面
        self._page = await self._context.new_page()
        self._page.set_default_timeout(self.config.timeout)
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
    
    async def navigate(self, url: Optional[str] = None) -> None:
        """
        导航到指定URL
        
        Args:
            url: 目标URL，如果为空则使用配置中的URL
        """
        target_url = url or self.config.url
        if not target_url:
            raise ValueError("URL is required")
        
        logger.info(f"Navigating to: {target_url}")
        await self._page.goto(target_url, wait_until='networkidle')
        
    async def take_screenshot(self, path: Optional[str] = None, full_page: bool = True) -> str:
        """
        截取页面截图
        
        Args:
            path: 截图保存路径，如果为空则自动生成
            full_page: 是否截取完整页面
            
        Returns:
            截图文件路径
        """
        if path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            path = os.path.join(self.config.output_dir, f'screenshot_{timestamp}.png')
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        
        await self._page.screenshot(path=path, full_page=full_page)
        logger.info(f"Screenshot saved: {path}")
        return path
    
    async def run_performance_test(self, url: Optional[str] = None) -> PerformanceMetrics:
        """
        运行性能测试
        
        Args:
            url: 目标URL
            
        Returns:
            性能指标
        """
        target_url = url or self.config.url
        if not target_url:
            raise ValueError("URL is required")
        
        logger.info(f"Running performance test for: {target_url}")
        
        # 收集性能数据
        start_time = time.time()
        
        # 导航到页面
        response = await self._page.goto(target_url, wait_until='networkidle')
        load_time = (time.time() - start_time) * 1000
        
        # 获取Web Vitals指标
        metrics = await self._page.evaluate("""() => {
            return {
                domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
                loadComplete: performance.timing.loadEventEnd - performance.timing.navigationStart,
                firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime,
                firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime,
                resources: performance.getEntriesByType('resource').length,
                resourceSize: performance.getEntriesByType('resource').reduce((acc, r) => acc + (r.transferSize || 0), 0)
            };
        }""")
        
        # 获取LCP
        lcp_data = await self._page.evaluate("""() => {
            return new Promise((resolve) => {
                new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    const lastEntry = entries[entries.length - 1];
                    resolve(lastEntry?.startTime);
                }).observe({entryTypes: ['largest-contentful-paint']});
                setTimeout(() => resolve(null), 1000);
            });
        }""")
        
        metrics_obj = PerformanceMetrics(
            url=target_url,
            timestamp=datetime.now().isoformat(),
            load_time_ms=load_time,
            dom_content_loaded_ms=metrics.get('domContentLoaded', 0),
            first_paint_ms=metrics.get('firstPaint'),
            first_contentful_paint_ms=metrics.get('firstContentfulPaint'),
            largest_contentful_paint_ms=lcp_data,
            total_resource_size_kb=metrics.get('resourceSize', 0) / 1024,
            resource_count=metrics.get('resources', 0)
        )
        
        return metrics_obj
    
    async def run_e2e_test(self, test_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        运行端到端测试
        
        Args:
            test_steps: 测试步骤列表
            
        Returns:
            测试结果
        """
        results = {
            'passed': 0,
            'failed': 0,
            'steps': [],
            'errors': []
        }
        
        for i, step in enumerate(test_steps):
            step_result = {'step': i + 1, 'action': step.get('action'), 'status': 'passed'}
            
            try:
                action = step.get('action')
                
                if action == 'navigate':
                    await self.navigate(step.get('url'))
                elif action == 'click':
                    selector = step.get('selector')
                    await self._page.click(selector)
                elif action == 'fill':
                    selector = step.get('selector')
                    value = step.get('value')
                    await self._page.fill(selector, value)
                elif action == 'wait':
                    selector = step.get('selector')
                    if selector:
                        await self._page.wait_for_selector(selector)
                    else:
                        await asyncio.sleep(step.get('seconds', 1))
                elif action == 'screenshot':
                    await self.take_screenshot(step.get('path'))
                elif action == 'assert':
                    selector = step.get('selector')
                    text = step.get('text')
                    if selector:
                        element = await self._page.query_selector(selector)
                        if element is None:
                            raise AssertionError(f"Element not found: {selector}")
                        if text:
                            element_text = await element.text_content()
                            if text not in element_text:
                                raise AssertionError(f"Text '{text}' not found in element")
                
                results['passed'] += 1
                
            except Exception as e:
                step_result['status'] = 'failed'
                step_result['error'] = str(e)
                results['failed'] += 1
                results['errors'].append({
                    'step': i + 1,
                    'action': step.get('action'),
                    'error': str(e)
                })
            
            results['steps'].append(step_result)
        
        results['total'] = len(test_steps)
        results['success'] = results['failed'] == 0
        
        return results


class VisualComparator:
    """视觉对比器"""
    
    @staticmethod
    def compare_images(
        baseline_path: str,
        current_path: str,
        output_dir: str = './test-results',
        threshold: float = 0.1
    ) -> ScreenshotComparisonResult:
        """
        对比两张图片
        
        Args:
            baseline_path: 基准图片路径
            current_path: 当前图片路径
            output_dir: 输出目录
            threshold: 相似度阈值
            
        Returns:
            对比结果
        """
        if not os.path.exists(baseline_path):
            raise FileNotFoundError(f"Baseline image not found: {baseline_path}")
        if not os.path.exists(current_path):
            raise FileNotFoundError(f"Current image not found: {current_path}")
        
        # 加载图片
        baseline = Image.open(baseline_path).convert('RGB')
        current = Image.open(current_path).convert('RGB')
        
        # 调整大小使一致
        if baseline.size != current.size:
            current = current.resize(baseline.size, Image.Resampling.LANCZOS)
        
        # 计算像素差异
        diff = ImageChops.difference(baseline, current)
        
        # 转换为numpy数组进行计算
        diff_array = np.array(diff)
        
        # 计算差异像素数
        threshold_pixel = 10  # RGB差异阈值
        diff_pixels = np.sum(np.any(diff_array > threshold_pixel, axis=2))
        total_pixels = diff_array.shape[0] * diff_array.shape[1]
        
        # 计算相似度
        similarity = 1.0 - (diff_pixels / total_pixels)
        
        # 生成差异图
        diff_path = None
        if diff_pixels > 0:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            diff_path = os.path.join(output_dir, f'diff_{timestamp}.png')
            os.makedirs(output_dir, exist_ok=True)
            
            # 增强差异可见性
            diff_enhanced = diff.point(lambda x: x * 10 if x > 0 else 0)
            diff_enhanced.save(diff_path)
        
        passed = similarity >= (1 - threshold)
        
        return ScreenshotComparisonResult(
            baseline_path=baseline_path,
            current_path=current_path,
            diff_path=diff_path,
            similarity_score=similarity,
            pixel_diff_count=int(diff_pixels),
            passed=passed,
            threshold=threshold
        )
    
    @staticmethod
    def compare_multiple(
        baseline_dir: str,
        current_dir: str,
        output_dir: str = './test-results',
        threshold: float = 0.1
    ) -> List[ScreenshotComparisonResult]:
        """
        批量对比目录中的图片
        
        Args:
            baseline_dir: 基准图片目录
            current_dir: 当前图片目录
            output_dir: 输出目录
            threshold: 相似度阈值
            
        Returns:
            对比结果列表
        """
        results = []
        
        baseline_files = {f for f in os.listdir(baseline_dir) if f.endswith(('.png', '.jpg', '.jpeg'))}
        current_files = {f for f in os.listdir(current_dir) if f.endswith(('.png', '.jpg', '.jpeg'))}
        
        common_files = baseline_files & current_files
        
        for filename in common_files:
            baseline_path = os.path.join(baseline_dir, filename)
            current_path = os.path.join(current_dir, filename)
            
            try:
                result = VisualComparator.compare_images(
                    baseline_path, current_path, output_dir, threshold
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to compare {filename}: {e}")
        
        return results


class TestReporter:
    """测试报告生成器"""
    
    @staticmethod
    def generate_html_report(
        results: Dict[str, Any],
        output_path: str,
        title: str = "Web App Test Report"
    ) -> str:
        """
        生成HTML测试报告
        
        Args:
            results: 测试结果字典
            output_path: 输出路径
            title: 报告标题
            
        Returns:
            报告文件路径
        """
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .card h3 {{
            margin-top: 0;
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
        }}
        .card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }}
        .passed {{ color: #22c55e; }}
        .failed {{ color: #ef4444; }}
        .warning {{ color: #f59e0b; }}
        table {{
            width: 100%;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #666;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        .status-passed {{
            background: #dcfce7;
            color: #166534;
        }}
        .status-failed {{
            background: #fee2e2;
            color: #991b1b;
        }}
        .timestamp {{
            color: #999;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
"""
        
        # 添加汇总信息
        if 'total' in results:
            html_content += f"""
    <div class="summary">
        <div class="card">
            <h3>Total Tests</h3>
            <div class="value">{results.get('total', 0)}</div>
        </div>
        <div class="card">
            <h3>Passed</h3>
            <div class="value passed">{results.get('passed', 0)}</div>
        </div>
        <div class="card">
            <h3>Failed</h3>
            <div class="value failed">{results.get('failed', 0)}</div>
        </div>
        <div class="card">
            <h3>Success Rate</h3>
            <div class="value {'passed' if results.get('success') else 'failed'}">
                {results.get('passed', 0) / max(results.get('total', 1), 1) * 100:.1f}%
            </div>
        </div>
    </div>
"""
        
        # 添加详细结果表格
        if 'steps' in results:
            html_content += """
    <table>
        <thead>
            <tr>
                <th>Step</th>
                <th>Action</th>
                <th>Status</th>
                <th>Error</th>
            </tr>
        </thead>
        <tbody>
"""
            for step in results['steps']:
                status_class = 'status-passed' if step['status'] == 'passed' else 'status-failed'
                html_content += f"""
            <tr>
                <td>{step['step']}</td>
                <td>{step['action']}</td>
                <td><span class="status-badge {status_class}">{step['status'].upper()}</span></td>
                <td>{step.get('error', '-')}</td>
            </tr>
"""
            html_content += """
        </tbody>
    </table>
"""
        
        html_content += """
</body>
</html>
"""
        
        # 保存报告
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {output_path}")
        return output_path
    
    @staticmethod
    def generate_json_report(results: Dict[str, Any], output_path: str) -> str:
        """
        生成JSON测试报告
        
        Args:
            results: 测试结果字典
            output_path: 输出路径
            
        Returns:
            报告文件路径
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"JSON report generated: {output_path}")
        return output_path


async def run_test_action(config: TestConfig) -> Dict[str, Any]:
    """运行测试动作"""
    async with WebAppTester(config) as tester:
        await tester.navigate()
        
        # 示例测试步骤
        test_steps = [
            {'action': 'screenshot', 'path': os.path.join(config.output_dir, 'initial.png')},
        ]
        
        results = await tester.run_e2e_test(test_steps)
        return results


async def run_visual_action(config: TestConfig) -> Dict[str, Any]:
    """运行视觉测试动作"""
    async with WebAppTester(config) as tester:
        await tester.navigate()
        screenshot_path = await tester.take_screenshot(config.screenshot_path)
        
        results = {
            'screenshot_path': screenshot_path,
            'url': config.url,
            'viewport': f"{config.viewport_width}x{config.viewport_height}",
            'browser': config.browser
        }
        
        # 如果有基准图片，进行对比
        if config.baseline_path and os.path.exists(config.baseline_path):
            comparison = VisualComparator.compare_images(
                config.baseline_path,
                screenshot_path,
                config.output_dir,
                config.threshold
            )
            results['comparison'] = comparison.to_dict()
        
        return results


async def run_performance_action(config: TestConfig) -> Dict[str, Any]:
    """运行性能测试动作"""
    async with WebAppTester(config) as tester:
        metrics = await tester.run_performance_test()
        
        # 保存性能报告
        report_path = os.path.join(config.output_dir, 'performance_report.json')
        TestReporter.generate_json_report(metrics.to_dict(), report_path)
        
        return metrics.to_dict()


async def run_compare_action(config: TestConfig) -> Dict[str, Any]:
    """运行图片对比动作"""
    if not config.baseline_path or not config.screenshot_path:
        raise ValueError("Both baseline_path and screenshot_path are required for comparison")
    
    result = VisualComparator.compare_images(
        config.baseline_path,
        config.screenshot_path,
        config.output_dir,
        config.threshold
    )
    
    return result.to_dict()


def generate_config_template(output_path: str = './test-config.json') -> str:
    """生成配置文件模板"""
    template = {
        'name': 'My Web App Test',
        'base_url': 'https://example.com',
        'browsers': ['chromium', 'firefox', 'webkit'],
        'viewport': {'width': 1920, 'height': 1080},
        'tests': [
            {
                'name': 'Homepage Load',
                'path': '/',
                'assertions': [
                    {'type': 'title_contains', 'value': 'Example'}
                ]
            }
        ],
        'visual_testing': {
            'enabled': True,
            'threshold': 0.1,
            'baseline_dir': './baselines'
        },
        'performance': {
            'enabled': True,
            'metrics': ['load_time', 'first_paint', 'lcp']
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Config template generated: {output_path}")
    return output_path


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(description='Web Application Testing Tool')
    parser.add_argument('--action', required=True,
                       choices=['test', 'visual', 'performance', 'compare', 'generate-config'],
                       help='Action to perform')
    parser.add_argument('--url', help='Target URL')
    parser.add_argument('--browser', default='chromium',
                       choices=['chromium', 'firefox', 'webkit'],
                       help='Browser type')
    parser.add_argument('--headless', type=bool, default=True,
                       help='Run in headless mode')
    parser.add_argument('--screenshot-path', help='Screenshot save path')
    parser.add_argument('--baseline-path', help='Baseline screenshot path')
    parser.add_argument('--output-dir', default='./test-results',
                       help='Output directory')
    parser.add_argument('--viewport-width', type=int, default=1920,
                       help='Viewport width')
    parser.add_argument('--viewport-height', type=int, default=1080,
                       help='Viewport height')
    parser.add_argument('--threshold', type=float, default=0.1,
                       help='Visual comparison threshold')
    parser.add_argument('--timeout', type=int, default=30000,
                       help='Operation timeout in milliseconds')
    
    args = parser.parse_args()
    
    # 创建配置
    config = TestConfig(
        url=args.url or '',
        browser=args.browser,
        headless=args.headless,
        viewport_width=args.viewport_width,
        viewport_height=args.viewport_height,
        timeout=args.timeout,
        screenshot_path=args.screenshot_path,
        baseline_path=args.baseline_path,
        output_dir=args.output_dir,
        threshold=args.threshold
    )
    
    # 确保输出目录存在
    os.makedirs(config.output_dir, exist_ok=True)
    
    # 执行动作
    if args.action == 'generate-config':
        path = generate_config_template()
        print(f"Configuration template generated: {path}")
        return
    
    # 异步执行测试动作
    async def run_async():
        if args.action == 'test':
            return await run_test_action(config)
        elif args.action == 'visual':
            return await run_visual_action(config)
        elif args.action == 'performance':
            return await run_performance_action(config)
        elif args.action == 'compare':
            return await run_compare_action(config)
    
    try:
        result = asyncio.run(run_async())
        
        # 打印结果
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 生成HTML报告
        if args.action in ['test', 'visual', 'performance']:
            html_path = os.path.join(config.output_dir, 'report.html')
            TestReporter.generate_html_report(result, html_path)
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
