#!/usr/bin/env python3
"""
Prometheus Skill - Prometheus监控查询工具
支持PromQL查询、指标分析、告警规则管理

关键词触发：Prometheus、PromQL、监控查询、metrics query、告警规则、
alert rule、指标分析、metric analysis、时序数据、time series
"""

import re
import json
import csv
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from urllib.parse import urlencode, quote
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """查询结果数据类"""
    metric: Dict[str, str]
    value: Optional[tuple] = None
    values: Optional[list] = None
    
    def get_value(self) -> float:
        """获取数值"""
        if self.value:
            return float(self.value[1])
        return 0.0
    
    def get_timestamp(self) -> float:
        """获取时间戳"""
        if self.value:
            return float(self.value[0])
        return 0.0


class PrometheusClient:
    """Prometheus HTTP API客户端"""
    
    def __init__(self, base_url: str, timeout: int = 30, headers: Optional[Dict] = None):
        """
        初始化Prometheus客户端
        
        Args:
            base_url: Prometheus服务器URL，如 http://localhost:9090
            timeout: 请求超时时间（秒）
            headers: 自定义请求头
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.headers = headers or {}
        self.headers.setdefault('Accept', 'application/json')
    
    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """发送HTTP请求"""
        url = f"{self.base_url}/api/v1/{endpoint}"
        if params:
            query_string = urlencode(params, safe=':[]{}"\\/=')
            url = f"{url}?{query_string}"
        
        req = urllib.request.Request(url, headers=self.headers, method='GET')
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data.get('status') != 'success':
                    error = data.get('error', 'Unknown error')
                    raise Exception(f"Prometheus query failed: {error}")
                return data
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"HTTP Error {e.code}: {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"Connection failed: {e.reason}")
    
    def health_check(self) -> Dict[str, Any]:
        """检查Prometheus健康状态"""
        try:
            url = f"{self.base_url}/-/healthy"
            req = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return {
                    "status": "healthy",
                    "code": response.status,
                    "message": response.read().decode('utf-8').strip()
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def query(self, query: str, time: Optional[str] = None) -> Dict:
        """
        执行即时查询
        
        Args:
            query: PromQL查询语句
            time: 查询时间点，如 '2024-01-01T00:00:00Z'
        
        Returns:
            查询结果字典
        """
        params = {'query': query}
        if time:
            params['time'] = self._parse_time(time)
        
        logger.info(f"执行查询: {query[:80]}...")
        return self._request('query', params)
    
    def query_range(self, query: str, start: str, end: str, step: str) -> Dict:
        """
        执行范围查询
        
        Args:
            query: PromQL查询语句
            start: 开始时间（相对或绝对）
            end: 结束时间（相对或绝对）
            step: 查询步长，如 '1m', '5m', '1h'
        
        Returns:
            时序数据字典
        """
        params = {
            'query': query,
            'start': self._parse_time(start),
            'end': self._parse_time(end),
            'step': self._parse_duration(step)
        }
        
        logger.info(f"执行范围查询: {query[:60]}... 时间范围: {start} 到 {end}")
        return self._request('query_range', params)
    
    def series(self, match: List[str], start: Optional[str] = None, 
               end: Optional[str] = None) -> Dict:
        """
        查询时间序列元数据
        
        Args:
            match: 标签匹配器列表，如 ['up{job="prometheus"}']
            start: 开始时间（可选）
            end: 结束时间（可选）
        
        Returns:
            时间序列列表
        """
        params = {'match[]': match}
        if start:
            params['start'] = self._parse_time(start)
        if end:
            params['end'] = self._parse_time(end)
        
        return self._request('series', params)
    
    def labels(self, start: Optional[str] = None, end: Optional[str] = None) -> Dict:
        """
        获取所有标签名称
        
        Returns:
            标签名称列表
        """
        params = {}
        if start:
            params['start'] = self._parse_time(start)
        if end:
            params['end'] = self._parse_time(end)
        
        return self._request('labels', params)
    
    def label_values(self, label: str, match: Optional[List[str]] = None) -> Dict:
        """
        获取标签的所有值
        
        Args:
            label: 标签名称
            match: 标签匹配器（可选）
        
        Returns:
            标签值列表
        """
        endpoint = f'label/{quote(label, safe="")}/values'
        params = {}
        if match:
            params['match[]'] = match
        
        return self._request(endpoint, params)
    
    def targets(self) -> Dict:
        """
        获取监控目标状态
        
        Returns:
            目标列表和状态
        """
        return self._request('targets')
    
    def target_metadata(self, match_target: Optional[str] = None) -> Dict:
        """
        获取目标元数据
        
        Args:
            match_target: 目标匹配器（可选）
        
        Returns:
            目标元数据
        """
        params = {}
        if match_target:
            params['match_target'] = match_target
        return self._request('targets/metadata', params)
    
    def alert_rules(self) -> Dict:
        """
        获取所有告警规则
        
        Returns:
            告警规则组
        """
        return self._request('rules')
    
    def active_alerts(self) -> List[Dict]:
        """
        获取当前活动告警
        
        Returns:
            活动告警列表
        """
        result = self._request('alerts')
        return result.get('data', {}).get('alerts', [])
    
    def metadata(self, metric: Optional[str] = None) -> Dict:
        """
        获取指标元数据
        
        Args:
            metric: 指标名称（可选，不提供则返回所有）
        
        Returns:
            指标元数据
        """
        params = {}
        if metric:
            params['metric'] = metric
        return self._request('metadata', params)
    
    def buildinfo(self) -> Dict:
        """获取Prometheus构建信息"""
        return self._request('status/buildinfo')
    
    def runtimeinfo(self) -> Dict:
        """获取Prometheus运行时信息"""
        return self._request('status/runtimeinfo')
    
    def tsdb(self) -> Dict:
        """获取TSDB统计信息"""
        return self._request('status/tsdb')
    
    def flags(self) -> Dict:
        """获取启动参数"""
        return self._request('status/flags')
    
    def export_metrics(self, query: str, format: str = 'json', 
                      output: Optional[str] = None) -> str:
        """
        导出指标数据
        
        Args:
            query: 查询语句
            format: 导出格式（json/csv/prometheus）
            output: 输出文件路径（可选）
        
        Returns:
            导出的数据或文件路径
        """
        result = self.query(query)
        data = result.get('data', {})
        
        if format == 'json':
            exported = json.dumps(data, indent=2, ensure_ascii=False)
        elif format == 'csv':
            exported = self._to_csv(data)
        elif format == 'prometheus':
            exported = self._to_prometheus_format(data)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(exported)
            logger.info(f"数据已导出到: {output}")
            return output
        
        return exported
    
    def _to_csv(self, data: Dict) -> str:
        """转换为CSV格式"""
        result_type = data.get('resultType')
        results = data.get('result', [])
        
        lines = []
        if result_type == 'vector':
            lines.append('metric,timestamp,value')
            for item in results:
                metric = json.dumps(item.get('metric', {}))
                value = item.get('value', [])
                if value:
                    lines.append(f'"{metric}",{value[0]},{value[1]}')
        elif result_type == 'matrix':
            lines.append('metric,timestamp,value')
            for item in results:
                metric = json.dumps(item.get('metric', {}))
                for ts, val in item.get('values', []):
                    lines.append(f'"{metric}",{ts},{val}')
        
        return '\n'.join(lines)
    
    def _to_prometheus_format(self, data: Dict) -> str:
        """转换为Prometheus exposition格式"""
        lines = []
        results = data.get('result', [])
        
        for item in results:
            metric = item.get('metric', {})
            name = metric.get('__name__', 'metric')
            labels = ','.join([f'{k}="{v}"' for k, v in metric.items() if k != '__name__'])
            
            value_data = item.get('value', item.get('values', [[]])[-1])
            if value_data:
                value = value_data[1] if isinstance(value_data, list) else value_data
                if labels:
                    lines.append(f'{name}{{{labels}}} {value}')
                else:
                    lines.append(f'{name} {value}')
        
        return '\n'.join(lines)
    
    def _parse_time(self, time_str: str) -> str:
        """解析时间字符串"""
        if time_str == 'now':
            return datetime.utcnow().isoformat() + 'Z'
        
        # 处理相对时间，如 '-1h', '-30m', '-1d'
        relative_match = re.match(r'^-(⁠\d+)([smhdw])$', time_str)
        if relative_match:
            value = int(relative_match.group(1))
            unit = relative_match.group(2)
            
            delta = {
                's': timedelta(seconds=value),
                'm': timedelta(minutes=value),
                'h': timedelta(hours=value),
                'd': timedelta(days=value),
                'w': timedelta(weeks=value)
            }.get(unit, timedelta(hours=value))
            
            return (datetime.utcnow() - delta).isoformat() + 'Z'
        
        return time_str
    
    def _parse_duration(self, duration: str) -> str:
        """解析持续时间字符串"""
        # 确保格式正确，如 '1m', '5m', '1h'
        if re.match(r'^\d+[smhdw]$', duration):
            return duration
        raise ValueError(f"Invalid duration format: {duration}")
    
    def analyze_metric(self, metric_name: str, aggregations: Optional[List[str]] = None) -> Dict:
        """
        分析指标统计信息
        
        Args:
            metric_name: 指标名称
            aggregations: 聚合函数列表，如 ['avg', 'max', 'min']
        
        Returns:
            统计分析结果
        """
        if aggregations is None:
            aggregations = ['avg', 'max', 'min', 'count']
        
        stats = {}
        
        for agg in aggregations:
            query = f"{agg}({metric_name})"
            try:
                result = self.query(query)
                data = result.get('data', {})
                if data.get('result'):
                    value = data['result'][0].get('value', [])
                    if value:
                        stats[agg] = float(value[1])
            except Exception as e:
                logger.warning(f"Failed to compute {agg}: {e}")
                stats[agg] = None
        
        return {
            "metric": metric_name,
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def find_metrics(self, pattern: str) -> List[str]:
        """
        查找匹配的指标名称
        
        Args:
            pattern: 匹配模式，支持通配符 *
        
        Returns:
            匹配的指标名称列表
        """
        # 获取所有指标元数据
        metadata = self.metadata()
        metrics = list(metadata.get('data', {}).keys())
        
        # 转换通配符为正则表达式
        regex_pattern = pattern.replace('*', '.*')
        regex = re.compile(regex_pattern)
        
        return [m for m in metrics if regex.match(m)]
    
    def generate_report(self, queries: Dict[str, str], output_format: str = 'json') -> str:
        """
        生成综合监控报告
        
        Args:
            queries: 查询名称和语句的字典
            output_format: 输出格式
        
        Returns:
            报告内容
        """
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "prometheus_url": self.base_url,
            "results": {}
        }
        
        for name, query in queries.items():
            try:
                result = self.query(query)
                report["results"][name] = {
                    "status": "success",
                    "data": result.get('data', {})
                }
            except Exception as e:
                report["results"][name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        if output_format == 'json':
            return json.dumps(report, indent=2, ensure_ascii=False)
        elif output_format == 'markdown':
            return self._format_markdown_report(report)
        else:
            return str(report)
    
    def _format_markdown_report(self, report: Dict) -> str:
        """生成Markdown格式报告"""
        lines = [
            "# Prometheus 监控报告",
            f"\n生成时间: {report['generated_at']}",
            f"\nPrometheus地址: {report['prometheus_url']}\n"
        ]
        
        for name, result in report['results'].items():
            lines.append(f"\n## {name}\n")
            
            if result['status'] == 'error':
                lines.append(f"❌ 错误: {result['error']}\n")
                continue
            
            data = result.get('data', {})
            result_type = data.get('resultType', 'unknown')
            results = data.get('result', [])
            
            lines.append(f"结果类型: {result_type}")
            lines.append(f"数据点数: {len(results)}\n")
            
            if result_type == 'vector' and results:
                lines.append("| 指标 | 值 |")
                lines.append("|------|-----|")
                for item in results[:10]:  # 最多显示10条
                    metric = item.get('metric', {})
                    value = item.get('value', [])
                    metric_str = ', '.join([f"{k}={v}" for k, v in metric.items() if k != '__name__'])
                    val_str = value[1] if len(value) > 1 else 'N/A'
                    lines.append(f"| {metric_str} | {val_str} |")
                if len(results) > 10:
                    lines.append(f"| ... | 还有 {len(results) - 10} 条数据 |")
            
            lines.append("")
        
        return '\n'.join(lines)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='Prometheus监控查询工具')
    parser.add_argument('--url', default='http://localhost:9090',
                       help='Prometheus服务器URL')
    parser.add_argument('--timeout', type=int, default=30,
                       help='请求超时时间')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # query命令
    query_parser = subparsers.add_parser('query', help='执行即时查询')
    query_parser.add_argument('promql', help='PromQL查询语句')
    query_parser.add_argument('--time', help='查询时间点')
    
    # range命令
    range_parser = subparsers.add_parser('range', help='执行范围查询')
    range_parser.add_argument('promql', help='PromQL查询语句')
    range_parser.add_argument('--start', default='-1h', help='开始时间')
    range_parser.add_argument('--end', default='now', help='结束时间')
    range_parser.add_argument('--step', default='1m', help='步长')
    
    # export命令
    export_parser = subparsers.add_parser('export', help='导出指标数据')
    export_parser.add_argument('promql', help='PromQL查询语句')
    export_parser.add_argument('--format', choices=['json', 'csv', 'prometheus'],
                              default='json', help='导出格式')
    
    # alerts命令
    subparsers.add_parser('alerts', help='列出活动告警')
    
    # rules命令
    subparsers.add_parser('rules', help='列出告警规则')
    
    # targets命令
    subparsers.add_parser('targets', help='列出监控目标')
    
    # health命令
    subparsers.add_parser('health', help='检查健康状态')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    client = PrometheusClient(args.url, timeout=args.timeout)
    
    try:
        if args.command == 'query':
            result = client.query(args.promql, args.time)
            output = json.dumps(result, indent=2, ensure_ascii=False)
        
        elif args.command == 'range':
            result = client.query_range(args.promql, args.start, args.end, args.step)
            output = json.dumps(result, indent=2, ensure_ascii=False)
        
        elif args.command == 'export':
            exported = client.export_metrics(args.promql, args.format, args.output)
            if args.output:
                print(f"数据已导出到: {exported}")
                return
            output = exported
        
        elif args.command == 'alerts':
            alerts = client.active_alerts()
            output = json.dumps(alerts, indent=2, ensure_ascii=False)
        
        elif args.command == 'rules':
            rules = client.alert_rules()
            output = json.dumps(rules, indent=2, ensure_ascii=False)
        
        elif args.command == 'targets':
            targets = client.targets()
            output = json.dumps(targets, indent=2, ensure_ascii=False)
        
        elif args.command == 'health':
            health = client.health_check()
            output = json.dumps(health, indent=2, ensure_ascii=False)
        
        else:
            parser.print_help()
            return
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"结果已保存到: {args.output}")
        else:
            print(output)
            
    except Exception as e:
        logger.error(f"操作失败: {e}")
        raise


if __name__ == '__main__':
    main()
