#!/usr/bin/env python3
"""
Log Analyzer Skill - 智能日志分析工具
支持Nginx/Apache/App日志解析、错误统计、趋势分析

关键词触发：日志分析、log analysis、Nginx日志、Apache日志、错误统计、
error analysis、日志解析、log parsing、错误模式、error pattern、日志趋势
"""

import re
import json
import gzip
import argparse
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Iterator
from dataclasses import dataclass, asdict
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class LogEntry:
    """日志条目数据类"""
    timestamp: Optional[datetime] = None
    level: str = "INFO"
    message: str = ""
    source: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class NginxLogEntry:
    """Nginx日志条目"""
    ip: str = ""
    timestamp: Optional[datetime] = None
    method: str = ""
    url: str = ""
    protocol: str = ""
    status_code: int = 0
    response_size: int = 0
    referrer: str = ""
    user_agent: str = ""
    response_time: float = 0.0


@dataclass
class ApacheLogEntry:
    """Apache日志条目"""
    ip: str = ""
    identity: str = ""
    userid: str = ""
    timestamp: Optional[datetime] = None
    method: str = ""
    url: str = ""
    protocol: str = ""
    status_code: int = 0
    response_size: int = 0


class LogParser:
    """通用日志解析器"""
    
    # Nginx combined格式正则
    NGINX_PATTERN = re.compile(
        r'^(?P<ip>\S+)\s+-\s+-(?P<timestamp>\s+\[[^\]]+\])\s+'
        r'"(?P<method>\S+)\s+(?P<url>\S+)\s+(?P<protocol>[^"]*)"\s+'
        r'(?P<status>\d+)\s+(?P<size>\d+)\s+'
        r'"(?P<referrer>[^"]*)"\s+"(?P<user_agent>[^"]*)"'
        r'(?:\s+(?P<response_time>[\d.]+))?$'
    )
    
    # Apache combined格式正则
    APACHE_PATTERN = re.compile(
        r'^(?P<ip>\S+)\s+(?P<identity>\S+)\s+(?P<userid>\S+)\s+'
        r'\[(?P<timestamp>[^\]]+)\]\s+'
        r'"(?P<method>\S+)\s+(?P<url>\S+)\s+(?P<protocol>[^"]*)"\s+'
        r'(?P<status>\d+)\s+(?P<size>\d+)'
    )
    
    # 通用日志级别正则
    LOG_LEVEL_PATTERN = re.compile(
        r'\b(DEBUG|INFO|WARN(?:ING)?|ERROR|FATAL|CRITICAL|TRACE)\b',
        re.IGNORECASE
    )
    
    # 时间戳格式
    TIMESTAMP_FORMATS = [
        '%d/%b/%Y:%H:%M:%S %z',  # Nginx格式
        '%d/%b/%Y:%H:%M:%S',      # Apache格式
        '%Y-%m-%d %H:%M:%S',      # 标准格式
        '%Y-%m-%dT%H:%M:%S',      # ISO格式
        '%Y-%m-%dT%H:%M:%S.%fZ',  # ISO with microseconds
    ]
    
    def __init__(self, custom_pattern: Optional[str] = None):
        self.custom_pattern = re.compile(custom_pattern) if custom_pattern else None
    
    def parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """解析多种格式的时间戳"""
        timestamp_str = timestamp_str.strip('[]')
        for fmt in self.TIMESTAMP_FORMATS:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        return None
    
    def parse_nginx_line(self, line: str) -> Optional[NginxLogEntry]:
        """解析单行Nginx日志"""
        match = self.NGINX_PATTERN.match(line)
        if not match:
            return None
        
        data = match.groupdict()
        return NginxLogEntry(
            ip=data.get('ip', ''),
            timestamp=self.parse_timestamp(data.get('timestamp', '')),
            method=data.get('method', ''),
            url=data.get('url', ''),
            protocol=data.get('protocol', ''),
            status_code=int(data.get('status', 0)),
            response_size=int(data.get('size', 0)),
            referrer=data.get('referrer', ''),
            user_agent=data.get('user_agent', ''),
            response_time=float(data.get('response_time', 0) or 0)
        )
    
    def parse_apache_line(self, line: str) -> Optional[ApacheLogEntry]:
        """解析单行Apache日志"""
        match = self.APACHE_PATTERN.match(line)
        if not match:
            return None
        
        data = match.groupdict()
        return ApacheLogEntry(
            ip=data.get('ip', ''),
            identity=data.get('identity', ''),
            userid=data.get('userid', ''),
            timestamp=self.parse_timestamp(data.get('timestamp', '')),
            method=data.get('method', ''),
            url=data.get('url', ''),
            protocol=data.get('protocol', ''),
            status_code=int(data.get('status', 0)),
            response_size=int(data.get('size', 0))
        )
    
    def parse_generic_line(self, line: str) -> LogEntry:
        """解析通用日志行"""
        entry = LogEntry(message=line.strip())
        
        # 提取日志级别
        level_match = self.LOG_LEVEL_PATTERN.search(line)
        if level_match:
            entry.level = level_match.group(1).upper()
        
        # 尝试提取时间戳
        timestamp_patterns = [
            r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)',
            r'(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}(?: [+-]\d{4})?)',
        ]
        for pattern in timestamp_patterns:
            ts_match = re.search(pattern, line)
            if ts_match:
                entry.timestamp = self.parse_timestamp(ts_match.group(1))
                break
        
        return entry
    
    def detect_format(self, sample_lines: List[str]) -> str:
        """自动检测日志格式"""
        for line in sample_lines:
            if self.NGINX_PATTERN.match(line):
                return 'nginx'
            if self.APACHE_PATTERN.match(line):
                return 'apache'
            try:
                json.loads(line)
                return 'json'
            except json.JSONDecodeError:
                pass
        return 'generic'


class LogAnalyzer:
    """日志分析器主类"""
    
    def __init__(self, chunk_size: int = 10000, max_lines: int = 1000000):
        self.parser = LogParser()
        self.chunk_size = chunk_size
        self.max_lines = max_lines
    
    def _read_log_file(self, log_path: str) -> Iterator[str]:
        """读取日志文件，支持gzip压缩"""
        path = Path(log_path)
        if not path.exists():
            raise FileNotFoundError(f"日志文件不存在: {log_path}")
        
        opener = gzip.open if path.suffix == '.gz' else open
        mode = 'rt' if path.suffix == '.gz' else 'r'
        
        with opener(path, mode, encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if i >= self.max_lines:
                    logger.warning(f"达到最大行数限制 {self.max_lines}")
                    break
                yield line.strip()
    
    def analyze_nginx_log(self, log_path: str, **options) -> Dict:
        """分析Nginx日志"""
        logger.info(f"分析Nginx日志: {log_path}")
        
        entries = []
        errors = []
        
        for line in self._read_log_file(log_path):
            try:
                entry = self.parser.parse_nginx_line(line)
                if entry:
                    entries.append(entry)
            except Exception as e:
                errors.append({"line": line, "error": str(e)})
        
        if not entries:
            return {"error": "未解析到有效日志条目", "parse_errors": len(errors)}
        
        # 统计计算
        total_requests = len(entries)
        status_counter = Counter(e.status_code for e in entries)
        url_counter = Counter(e.url for e in entries)
        ip_counter = Counter(e.ip for e in entries)
        
        # 错误统计 (4xx, 5xx)
        error_requests = sum(count for code, count in status_counter.items() if code >= 400)
        error_rate = error_requests / total_requests if total_requests > 0 else 0
        
        # 响应时间统计
        response_times = [e.response_time for e in entries if e.response_time > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # HTTP方法统计
        method_counter = Counter(e.method for e in entries)
        
        # 时间分布（按小时）
        hourly_distribution = Counter()
        for e in entries:
            if e.timestamp:
                hourly_distribution[e.timestamp.hour] += 1
        
        return {
            "log_type": "nginx",
            "total_requests": total_requests,
            "unique_visitors": len(ip_counter),
            "error_rate": error_rate,
            "error_requests": error_requests,
            "avg_response_time": round(avg_response_time, 3),
            "status_distribution": dict(status_counter.most_common(10)),
            "top_urls": url_counter.most_common(20),
            "top_ips": ip_counter.most_common(20),
            "method_distribution": dict(method_counter),
            "hourly_distribution": dict(sorted(hourly_distribution.items())),
            "parse_errors": len(errors),
            "time_range": {
                "start": min(e.timestamp for e in entries if e.timestamp).isoformat() if any(e.timestamp for e in entries) else None,
                "end": max(e.timestamp for e in entries if e.timestamp).isoformat() if any(e.timestamp for e in entries) else None
            }
        }
    
    def analyze_apache_log(self, log_path: str, **options) -> Dict:
        """分析Apache日志"""
        logger.info(f"分析Apache日志: {log_path}")
        
        entries = []
        errors = []
        
        for line in self._read_log_file(log_path):
            try:
                entry = self.parser.parse_apache_line(line)
                if entry:
                    entries.append(entry)
            except Exception as e:
                errors.append({"line": line, "error": str(e)})
        
        if not entries:
            return {"error": "未解析到有效日志条目", "parse_errors": len(errors)}
        
        total_requests = len(entries)
        status_counter = Counter(e.status_code for e in entries)
        url_counter = Counter(e.url for e in entries)
        ip_counter = Counter(e.ip for e in entries)
        
        error_requests = sum(count for code, count in status_counter.items() if code >= 400)
        error_rate = error_requests / total_requests if total_requests > 0 else 0
        
        total_response_size = sum(e.response_size for e in entries)
        
        return {
            "log_type": "apache",
            "total_requests": total_requests,
            "unique_visitors": len(ip_counter),
            "error_rate": error_rate,
            "error_requests": error_requests,
            "total_bandwidth": total_response_size,
            "avg_response_size": total_response_size / total_requests if total_requests > 0 else 0,
            "status_distribution": dict(status_counter.most_common(10)),
            "top_urls": url_counter.most_common(20),
            "top_ips": ip_counter.most_common(20),
            "parse_errors": len(errors),
            "time_range": {
                "start": min(e.timestamp for e in entries if e.timestamp).isoformat() if any(e.timestamp for e in entries) else None,
                "end": max(e.timestamp for e in entries if e.timestamp).isoformat() if any(e.timestamp for e in entries) else None
            }
        }
    
    def analyze_error_trend(self, log_path: str, hours: int = 24, 
                          error_patterns: Optional[List[str]] = None) -> Dict:
        """分析错误趋势"""
        logger.info(f"分析错误趋势: {log_path}, 时间范围: {hours}小时")
        
        if error_patterns is None:
            error_patterns = [r"ERROR", r"EXCEPTION", r"FATAL", r"CRITICAL"]
        
        compiled_patterns = [re.compile(p, re.IGNORECASE) for p in error_patterns]
        
        # 按小时统计错误
        hourly_errors = defaultdict(lambda: defaultdict(int))
        error_types = Counter()
        total_lines = 0
        matched_errors = 0
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for line in self._read_log_file(log_path):
            total_lines += 1
            
            # 提取时间戳
            entry = self.parser.parse_generic_line(line)
            
            # 时间过滤
            if entry.timestamp and entry.timestamp < cutoff_time:
                continue
            
            # 匹配错误模式
            for pattern in compiled_patterns:
                if pattern.search(line):
                    matched_errors += 1
                    hour_key = entry.timestamp.hour if entry.timestamp else 0
                    error_type = pattern.pattern
                    hourly_errors[hour_key][error_type] += 1
                    error_types[error_type] += 1
                    break
        
        # 构建趋势数据
        trend_data = []
        for hour in sorted(hourly_errors.keys()):
            trend_data.append({
                "hour": hour,
                "total": sum(hourly_errors[hour].values()),
                "by_type": dict(hourly_errors[hour])
            })
        
        return {
            "analysis_period_hours": hours,
            "total_lines_processed": total_lines,
            "total_errors_found": matched_errors,
            "error_rate": matched_errors / total_lines if total_lines > 0 else 0,
            "error_types": dict(error_types),
            "hourly_trend": trend_data,
            "peak_error_hour": max(hourly_errors.keys(), key=lambda h: sum(hourly_errors[h].values())) if hourly_errors else None
        }
    
    def extract_errors(self, log_path: str, context_lines: int = 2) -> Dict:
        """提取错误日志条目"""
        logger.info(f"提取错误: {log_path}")
        
        errors = []
        lines = list(self._read_log_file(log_path))
        
        for i, line in enumerate(lines):
            entry = self.parser.parse_generic_line(line)
            
            if entry.level in ['ERROR', 'FATAL', 'CRITICAL']:
                # 获取上下文
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                context = lines[start:end]
                
                errors.append({
                    "timestamp": entry.timestamp.isoformat() if entry.timestamp else None,
                    "level": entry.level,
                    "message": entry.message,
                    "context": context,
                    "line_number": i + 1
                })
        
        # 按错误级别分组
        by_level = defaultdict(list)
        for error in errors:
            by_level[error["level"]].append(error)
        
        return {
            "total_errors": len(errors),
            "by_level": {k: len(v) for k, v in by_level.items()},
            "recent_errors": errors[:50],  # 最多返回50条
            "error_patterns": self._extract_error_patterns(errors)
        }
    
    def _extract_error_patterns(self, errors: List[Dict]) -> List[Dict]:
        """提取常见错误模式"""
        # 简单的错误分类
        patterns = Counter()
        
        for error in errors:
            msg = error["message"]
            # 提取异常类型
            exception_match = re.search(r'(\w+Exception|\w+Error):', msg)
            if exception_match:
                patterns[exception_match.group(1)] += 1
        
        return [{"pattern": p, "count": c} for p, c in patterns.most_common(10)]
    
    def generate_report(self, log_files: List[str], output_format: str = 'json',
                       **options) -> str:
        """生成综合分析报告"""
        logger.info(f"生成报告，文件数: {len(log_files)}, 格式: {output_format}")
        
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "files_analyzed": log_files,
            "results": []
        }
        
        for log_file in log_files:
            # 自动检测格式
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                sample = [f.readline() for _ in range(5)]
            
            log_format = self.parser.detect_format(sample)
            
            if log_format == 'nginx':
                result = self.analyze_nginx_log(log_file, **options)
            elif log_format == 'apache':
                result = self.analyze_apache_log(log_file, **options)
            else:
                result = self.analyze_error_trend(log_file, **options)
            
            result["file"] = log_file
            result["detected_format"] = log_format
            report_data["results"].append(result)
        
        # 格式化输出
        if output_format == 'json':
            return json.dumps(report_data, indent=2, ensure_ascii=False)
        elif output_format == 'markdown':
            return self._format_markdown_report(report_data)
        elif output_format == 'html':
            return self._format_html_report(report_data)
        else:
            return str(report_data)
    
    def _format_markdown_report(self, data: Dict) -> str:
        """生成Markdown格式报告"""
        lines = ["# 日志分析报告\n", f"生成时间: {data['generated_at']}\n"]
        
        for result in data["results"]:
            lines.append(f"\n## {result['file']}\n")
            lines.append(f"格式: {result.get('detected_format', 'unknown')}\n")
            
            if "total_requests" in result:
                lines.append(f"- 总请求数: {result['total_requests']}")
                lines.append(f"- 错误率: {result.get('error_rate', 0):.2%}")
                lines.append(f"- 独立访客: {result.get('unique_visitors', 0)}")
            
            if "total_errors_found" in result:
                lines.append(f"- 错误数: {result['total_errors_found']}")
                lines.append(f"- 错误率: {result.get('error_rate', 0):.2%}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_html_report(self, data: Dict) -> str:
        """生成HTML格式报告"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>日志分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 1px solid #ddd; padding-bottom: 10px; }}
        .metric {{ background: #f5f5f5; padding: 10px; margin: 5px 0; border-radius: 4px; }}
        .error {{ color: #d32f2f; }}
        .success {{ color: #388e3c; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f0f0f0; }}
    </style>
</head>
<body>
    <h1>日志分析报告</h1>
    <p>生成时间: {data['generated_at']}</p>
"""
        
        for result in data["results"]:
            html += f"<h2>{result['file']}</h2>"
            html += f"<p>格式: {result.get('detected_format', 'unknown')}</p>"
            
            html += '<div class="metrics">'
            if "total_requests" in result:
                html += f'<div class="metric">总请求数: {result["total_requests"]}</div>'
                html += f'<div class="metric">错误率: {result.get("error_rate", 0):.2%}</div>'
            if "total_errors_found" in result:
                html += f'<div class="metric error">错误数: {result["total_errors_found"]}</div>'
            html += '</div>'
        
        html += "</body></html>"
        return html


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='日志分析工具')
    parser.add_argument('--input', '-i', required=True, help='输入日志文件路径')
    parser.add_argument('--format', '-f', choices=['nginx', 'apache', 'auto'],
                       default='auto', help='日志格式')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--report-type', choices=['json', 'html', 'markdown'],
                       default='json', help='报告格式')
    parser.add_argument('--analyze-trend', action='store_true', help='分析趋势')
    parser.add_argument('--hours', type=int, default=24, help='分析时间范围（小时）')
    parser.add_argument('--max-lines', type=int, default=1000000, help='最大处理行数')
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer(max_lines=args.max_lines)
    
    try:
        if args.analyze_trend:
            result = analyzer.analyze_error_trend(args.input, hours=args.hours)
        else:
            if args.format == 'nginx':
                result = analyzer.analyze_nginx_log(args.input)
            elif args.format == 'apache':
                result = analyzer.analyze_apache_log(args.input)
            else:
                # 自动检测
                with open(args.input, 'r', encoding='utf-8', errors='ignore') as f:
                    sample = [f.readline() for _ in range(5)]
                detected = analyzer.parser.detect_format(sample)
                if detected == 'nginx':
                    result = analyzer.analyze_nginx_log(args.input)
                elif detected == 'apache':
                    result = analyzer.analyze_apache_log(args.input)
                else:
                    result = analyzer.analyze_error_trend(args.input, hours=args.hours)
        
        output = json.dumps(result, indent=2, ensure_ascii=False)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"报告已保存: {args.output}")
        else:
            print(output)
            
    except Exception as e:
        logger.error(f"分析失败: {e}")
        raise


if __name__ == '__main__':
    main()
