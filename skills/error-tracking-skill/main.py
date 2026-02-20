#!/usr/bin/env python3
"""
Error Tracking Skill - 错误追踪分析工具
支持错误聚合、堆栈分析、频率统计

关键词触发：错误追踪、error tracking、堆栈分析、stack trace、错误聚合、
error aggregation、异常分析、exception analysis、错误频率、error frequency
"""

import re
import json
import hashlib
import argparse
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Iterator
from dataclasses import dataclass, field, asdict
from difflib import SequenceMatcher
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class StackFrame:
    """堆栈帧数据类"""
    file: str = ""
    line: int = 0
    function: str = ""
    code: str = ""
    module: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ErrorEntry:
    """错误条目数据类"""
    timestamp: Optional[datetime] = None
    error_type: str = ""
    message: str = ""
    stack_trace: List[StackFrame] = field(default_factory=list)
    source_file: str = ""
    context: str = ""
    raw_text: str = ""
    hash_id: str = ""
    
    def __post_init__(self):
        if not self.hash_id and self.raw_text:
            self.hash_id = hashlib.md5(self.raw_text.encode()).hexdigest()[:16]
    
    def get_stack_signature(self) -> str:
        """获取堆栈签名（用于相似度比较）"""
        frames = []
        for frame in self.stack_trace[:5]:  # 使用前5帧
            # 提取类/函数名，忽略行号
            func = re.sub(r'\d+', '', frame.function)
            frames.append(f"{frame.module}.{func}")
        return "|".join(frames)
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "error_type": self.error_type,
            "message": self.message[:200] if self.message else "",
            "stack_trace": [f.to_dict() for f in self.stack_trace],
            "source_file": self.source_file,
            "hash_id": self.hash_id
        }


class StackTraceParser:
    """堆栈跟踪解析器"""
    
    # Python Traceback正则
    PYTHON_TRACEBACK_PATTERN = re.compile(
        r'Traceback \(most recent call last\):\n'
        r'((?:  File "([^"]+)", line (\d+), in (\w+)\n'
        r'(?:    [^\n]+\n)?)+)'
        r'([\w\.]+):\s*(.*)$',
        re.MULTILINE
    )
    
    PYTHON_FRAME_PATTERN = re.compile(
        r'  File "([^"]+)", line (\d+), in (\w+)\n'
        r'(?:    ([^\n]+)\n)?'
    )
    
    # Java Stack Trace正则
    JAVA_EXCEPTION_PATTERN = re.compile(
        r'([\w\.]+Exception|[\w\.]+Error):\s*(.*?)\n'
        r'((?:\s+at\s+[\w\.$]+\([\w\.\$:]+:\d+\)\n)+)'
        r'(?:\s+Caused by:.*)?',
        re.MULTILINE | re.DOTALL
    )
    
    JAVA_FRAME_PATTERN = re.compile(
        r'\s+at\s+([\w\.$]+)\(([\w\.\$:]+)\:(\d+)\)'
    )
    
    # JavaScript Error正则
    JS_ERROR_PATTERN = re.compile(
        r'([\w\s]+Error):\s*(.*?)\n'
        r'((?:\s+at\s+.*\n?)+)',
        re.MULTILINE
    )
    
    JS_FRAME_PATTERN = re.compile(
        r'\s+at\s+(?:(\w+)\s+\()?([^)]+)\:(\d+)\:(\d+)\)?'
    )
    
    # Go Panic正则
    GO_PANIC_PATTERN = re.compile(
        r'panic:\s*(.*?)\n\n'
        r'goroutine\s+\d+.*\n'
        r'((?:.+\.go:\d+\n?)+)',
        re.MULTILINE
    )
    
    # 通用错误正则
    GENERIC_ERROR_PATTERN = re.compile(
        r'(?:ERROR|EXCEPTION|FATAL|CRITICAL)[\s:]+\s*'
        r'(?:([\w\.]+Exception|[\w\.]+Error)[\s:])?\s*'
        r'(.+?)(?=\n(?:ERROR|EXCEPTION|INFO|DEBUG|$))',
        re.IGNORECASE | re.DOTALL
    )
    
    # 时间戳正则
    TIMESTAMP_PATTERNS = [
        (r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)', 
         '%Y-%m-%d %H:%M:%S'),
        (r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})', '%b %d %H:%M:%S'),
        (r'(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})', '%d/%b/%Y:%H:%M:%S'),
    ]
    
    def parse_python_traceback(self, text: str) -> Optional[ErrorEntry]:
        """解析Python Traceback"""
        match = self.PYTHON_TRACEBACK_PATTERN.search(text)
        if not match:
            return None
        
        frames_text = match.group(1)
        error_type = match.group(5)
        message = match.group(6)
        
        frames = []
        for frame_match in self.PYTHON_FRAME_PATTERN.finditer(frames_text):
            frames.append(StackFrame(
                file=frame_match.group(1),
                line=int(frame_match.group(2)),
                function=frame_match.group(3),
                code=frame_match.group(4) or ""
            ))
        
        return ErrorEntry(
            error_type=error_type,
            message=message,
            stack_trace=frames,
            raw_text=text
        )
    
    def parse_java_stack_trace(self, text: str) -> Optional[ErrorEntry]:
        """解析Java Stack Trace"""
        match = self.JAVA_EXCEPTION_PATTERN.search(text)
        if not match:
            return None
        
        error_type = match.group(1)
        message = match.group(2)
        stack_text = match.group(3)
        
        frames = []
        for frame_match in self.JAVA_FRAME_PATTERN.finditer(stack_text):
            func_parts = frame_match.group(1).split('.')
            frames.append(StackFrame(
                file=frame_match.group(2),
                line=int(frame_match.group(3)),
                function=func_parts[-1] if func_parts else "",
                module='.'.join(func_parts[:-1]) if len(func_parts) > 1 else ""
            ))
        
        return ErrorEntry(
            error_type=error_type,
            message=message,
            stack_trace=frames,
            raw_text=text
        )
    
    def parse_javascript_error(self, text: str) -> Optional[ErrorEntry]:
        """解析JavaScript Error"""
        match = self.JS_ERROR_PATTERN.search(text)
        if not match:
            return None
        
        error_type = match.group(1)
        message = match.group(2)
        stack_text = match.group(3)
        
        frames = []
        for frame_match in self.JS_FRAME_PATTERN.finditer(stack_text):
            frames.append(StackFrame(
                file=frame_match.group(2),
                line=int(frame_match.group(3)),
                function=frame_match.group(1) or "anonymous",
                module=""
            ))
        
        return ErrorEntry(
            error_type=error_type,
            message=message,
            stack_trace=frames,
            raw_text=text
        )
    
    def parse_go_panic(self, text: str) -> Optional[ErrorEntry]:
        """解析Go Panic"""
        match = self.GO_PANIC_PATTERN.search(text)
        if not match:
            return None
        
        message = match.group(1)
        stack_text = match.group(2)
        
        frames = []
        for line in stack_text.strip().split('\n'):
            parts = line.strip().split(':')
            if len(parts) >= 2:
                frames.append(StackFrame(
                    file=parts[0],
                    line=int(parts[1]) if parts[1].isdigit() else 0,
                    function="",
                    module=""
                ))
        
        return ErrorEntry(
            error_type="panic",
            message=message,
            stack_trace=frames,
            raw_text=text
        )
    
    def parse_generic_error(self, text: str) -> Optional[ErrorEntry]:
        """解析通用错误格式"""
        match = self.GENERIC_ERROR_PATTERN.search(text)
        if not match:
            return None
        
        error_type = match.group(1) or "UnknownError"
        message = match.group(2).strip()
        
        return ErrorEntry(
            error_type=error_type,
            message=message,
            raw_text=text
        )
    
    def parse_timestamp(self, text: str) -> Optional[datetime]:
        """解析时间戳"""
        for pattern, fmt in self.TIMESTAMP_PATTERNS:
            match = re.search(pattern, text)
            if match:
                try:
                    ts_str = match.group(1)
                    if 'Z' in ts_str:
                        ts_str = ts_str.replace('Z', '+00:00')
                    return datetime.fromisoformat(ts_str)
                except ValueError:
                    try:
                        return datetime.strptime(ts_str, fmt)
                    except ValueError:
                        continue
        return None
    
    def detect_format(self, sample: str) -> str:
        """检测错误日志格式"""
        if 'Traceback (most recent call last)' in sample:
            return 'python'
        elif re.search(r'\w+Exception:|\w+Error:', sample) and 'at' in sample:
            return 'java'
        elif 'Error:' in sample and 'at' in sample:
            return 'javascript'
        elif 'panic:' in sample and 'goroutine' in sample:
            return 'go'
        else:
            return 'generic'
    
    def parse(self, text: str, format_hint: Optional[str] = None) -> Optional[ErrorEntry]:
        """自动解析错误文本"""
        if format_hint == 'python' or (not format_hint and 'Traceback' in text):
            entry = self.parse_python_traceback(text)
            if entry:
                entry.timestamp = self.parse_timestamp(text)
                return entry
        
        if format_hint == 'java' or (not format_hint and 'Exception:' in text):
            entry = self.parse_java_stack_trace(text)
            if entry:
                entry.timestamp = self.parse_timestamp(text)
                return entry
        
        if format_hint == 'javascript':
            entry = self.parse_javascript_error(text)
            if entry:
                entry.timestamp = self.parse_timestamp(text)
                return entry
        
        if format_hint == 'go' or (not format_hint and 'panic:' in text):
            entry = self.parse_go_panic(text)
            if entry:
                entry.timestamp = self.parse_timestamp(text)
                return entry
        
        entry = self.parse_generic_error(text)
        if entry:
            entry.timestamp = self.parse_timestamp(text)
            return entry
        
        return None


class ErrorTracker:
    """错误追踪器主类"""
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.parser = StackTraceParser()
        self.errors: List[ErrorEntry] = []
        self.similarity_threshold = similarity_threshold
    
    def analyze_file(self, file_path: str, format_hint: Optional[str] = None) -> Dict:
        """分析单个日志文件"""
        logger.info(f"分析文件: {file_path}")
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        errors = []
        content = path.read_text(encoding='utf-8', errors='ignore')
        
        # 分割日志条目（简单按空行分割）
        entries = re.split(r'\n\n+', content)
        
        for entry_text in entries:
            if not entry_text.strip():
                continue
            
            error = self.parser.parse(entry_text, format_hint)
            if error:
                error.source_file = file_path
                errors.append(error)
        
        self.errors.extend(errors)
        
        return self._summarize_errors(errors)
    
    def analyze_files(self, file_paths: List[str], **options) -> Dict:
        """分析多个日志文件"""
        all_results = []
        by_source = {}
        
        for file_path in file_paths:
            try:
                result = self.analyze_file(file_path, **options)
                all_results.append(result)
                by_source[file_path] = result
            except Exception as e:
                logger.error(f"分析文件失败 {file_path}: {e}")
                by_source[file_path] = {"error": str(e)}
        
        # 汇总
        total_errors = sum(r.get('total_errors', 0) for r in all_results)
        all_types = set()
        for r in all_results:
            all_types.update(r.get('by_type', {}).keys())
        
        return {
            "total_errors": total_errors,
            "unique_types": len(all_types),
            "files_analyzed": len(file_paths),
            "by_source": by_source,
            "all_error_types": list(all_types)
        }
    
    def _summarize_errors(self, errors: List[ErrorEntry]) -> Dict:
        """汇总错误信息"""
        by_type = defaultdict(list)
        for error in errors:
            by_type[error.error_type].append(error)
        
        # 统计时间分布
        hourly_dist = Counter()
        for error in errors:
            if error.timestamp:
                hourly_dist[error.timestamp.hour] += 1
        
        return {
            "total_errors": len(errors),
            "unique_types": len(by_type),
            "by_type": {k: [e.to_dict() for e in v] for k, v in by_type.items()},
            "hourly_distribution": dict(sorted(hourly_dist.items())),
            "top_errors": self._get_top_errors_list(errors, n=5)
        }
    
    def _get_top_errors_list(self, errors: List[ErrorEntry], n: int = 10) -> List[Dict]:
        """获取最常见的错误列表"""
        type_counts = Counter(e.error_type for e in errors)
        return [
            {"type": error_type, "count": count}
            for error_type, count in type_counts.most_common(n)
        ]
    
    def aggregate_by_type(self) -> Dict[str, List[ErrorEntry]]:
        """按错误类型聚合"""
        grouped = defaultdict(list)
        for error in self.errors:
            grouped[error.error_type].append(error)
        return dict(grouped)
    
    def aggregate_by_stack_similarity(self, threshold: Optional[float] = None) -> List[Dict]:
        """按堆栈相似度聚合错误"""
        threshold = threshold or self.similarity_threshold
        
        groups = []
        ungrouped = self.errors.copy()
        
        while ungrouped:
            current = ungrouped.pop(0)
            group = [current]
            
            # 查找相似的错误
            i = 0
            while i < len(ungrouped):
                if self._calculate_similarity(current, ungrouped[i]) >= threshold:
                    group.append(ungrouped.pop(i))
                else:
                    i += 1
            
            groups.append({
                "representative": current.to_dict(),
                "count": len(group),
                "errors": [e.to_dict() for e in group],
                "first_seen": min((e.timestamp for e in group if e.timestamp), default=None),
                "last_seen": max((e.timestamp for e in group if e.timestamp), default=None),
                "similarity_threshold": threshold
            })
        
        # 按数量排序
        groups.sort(key=lambda g: g['count'], reverse=True)
        return groups
    
    def _calculate_similarity(self, error1: ErrorEntry, error2: ErrorEntry) -> float:
        """计算两个错误的相似度"""
        # 类型不同，相似度为0
        if error1.error_type != error2.error_type:
            return 0.0
        
        # 如果有堆栈信息，使用堆栈相似度
        if error1.stack_trace and error2.stack_trace:
            sig1 = error1.get_stack_signature()
            sig2 = error2.get_stack_signature()
            return SequenceMatcher(None, sig1, sig2).ratio()
        
        # 否则使用消息相似度
        if error1.message and error2.message:
            return SequenceMatcher(None, error1.message, error2.message).ratio()
        
        return 0.0
    
    def analyze_trend(self, hours: int = 24, interval: str = '1h') -> Dict:
        """分析错误趋势"""
        if not self.errors:
            return {"error": "没有错误数据"}
        
        now = datetime.now()
        start_time = now - timedelta(hours=hours)
        
        # 过滤时间范围内的错误
        recent_errors = [e for e in self.errors 
                        if e.timestamp and e.timestamp >= start_time]
        
        # 按时间间隔分组
        interval_minutes = self._parse_interval(interval)
        buckets = defaultdict(list)
        
        for error in recent_errors:
            if error.timestamp:
                bucket_key = error.timestamp.replace(
                    minute=(error.timestamp.minute // interval_minutes) * interval_minutes,
                    second=0,
                    microsecond=0
                )
                buckets[bucket_key].append(error)
        
        timeline = []
        for time_key in sorted(buckets.keys()):
            timeline.append({
                "time": time_key.isoformat(),
                "count": len(buckets[time_key]),
                "types": dict(Counter(e.error_type for e in buckets[time_key]))
            })
        
        # 计算统计信息
        counts = [len(buckets[t]) for t in sorted(buckets.keys())]
        avg_count = sum(counts) / len(counts) if counts else 0
        peak_time = max(buckets.keys(), key=lambda k: len(buckets[k])) if buckets else None
        
        return {
            "hours": hours,
            "interval": interval,
            "total_errors": len(recent_errors),
            "timeline": timeline,
            "average_per_interval": round(avg_count, 2),
            "peak_time": peak_time.isoformat() if peak_time else None,
            "peak_count": max(counts) if counts else 0
        }
    
    def _parse_interval(self, interval: str) -> int:
        """解析时间间隔"""
        match = re.match(r'(\d+)([mhd])', interval)
        if not match:
            return 60  # 默认1小时
        
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit == 'm':
            return value
        elif unit == 'h':
            return value * 60
        elif unit == 'd':
            return value * 60 * 24
        
        return 60
    
    def get_top_errors(self, n: int = 10, by: str = 'count') -> List[Dict]:
        """获取最常见的错误"""
        if by == 'count':
            type_counts = Counter(e.error_type for e in self.errors)
            return [
                {"type": t, "count": c}
                for t, c in type_counts.most_common(n)
            ]
        elif by == 'recent':
            sorted_errors = sorted(
                self.errors,
                key=lambda e: e.timestamp or datetime.min,
                reverse=True
            )
            return [e.to_dict() for e in sorted_errors[:n]]
        else:
            return []
    
    def find_similar_errors(self, error: ErrorEntry, threshold: Optional[float] = None) -> List[ErrorEntry]:
        """查找相似的错误"""
        threshold = threshold or self.similarity_threshold
        similar = []
        
        for e in self.errors:
            if e.hash_id != error.hash_id:
                similarity = self._calculate_similarity(error, e)
                if similarity >= threshold:
                    similar.append((e, similarity))
        
        # 按相似度排序
        similar.sort(key=lambda x: x[1], reverse=True)
        return [e for e, _ in similar]
    
    def generate_report(self, format: str = 'json', **options) -> str:
        """生成分析报告"""
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_errors": len(self.errors),
                "unique_types": len(set(e.error_type for e in self.errors)),
                "time_range": self._get_time_range()
            },
            "aggregated_by_type": self.aggregate_by_type(),
            "aggregated_by_similarity": self.aggregate_by_stack_similarity(),
            "trend": self.analyze_trend(hours=options.get('hours', 24)),
            "top_errors": self.get_top_errors(n=options.get('top_n', 10))
        }
        
        if format == 'json':
            return json.dumps(report_data, indent=2, ensure_ascii=False, default=str)
        elif format == 'html':
            return self._format_html_report(report_data, **options)
        elif format == 'markdown':
            return self._format_markdown_report(report_data)
        else:
            return str(report_data)
    
    def _get_time_range(self) -> Dict:
        """获取错误时间范围"""
        timestamps = [e.timestamp for e in self.errors if e.timestamp]
        if not timestamps:
            return {"start": None, "end": None}
        return {
            "start": min(timestamps).isoformat(),
            "end": max(timestamps).isoformat()
        }
    
    def _format_html_report(self, data: Dict, **options) -> str:
        """生成HTML报告"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Error Tracking Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #d32f2f; }}
        h2 {{ color: #333; border-bottom: 2px solid #d32f2f; padding-bottom: 10px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .error-group {{ background: #fff3f3; border: 1px solid #ffcdd2; padding: 15px; margin: 10px 0; border-radius: 4px; }}
        .error-type {{ font-weight: bold; color: #d32f2f; }}
        .count {{ color: #666; }}
        .stack-trace {{ font-family: monospace; font-size: 12px; background: #f5f5f5; padding: 10px; overflow-x: auto; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #d32f2f; color: white; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>🐛 错误追踪报告</h1>
    <p>生成时间: {data['generated_at']}</p>
    
    <div class="summary">
        <h2>摘要</h2>
        <p>总错误数: <strong>{data['summary']['total_errors']}</strong></p>
        <p>唯一错误类型: <strong>{data['summary']['unique_types']}</strong></p>
    </div>
"""
        
        # 添加错误分组
        html += '<h2>按相似度聚合的错误</h2>'
        for group in data['aggregated_by_similarity'][:20]:  # 最多显示20组
            html += f'''
    <div class="error-group">
        <div class="error-type">{group['representative']['error_type']}</div>
        <div class="count">发生次数: {group['count']}</div>
        <p>{group['representative']['message'][:200]}...</p>
    </div>
'''
        
        html += '</body></html>'
        return html
    
    def _format_markdown_report(self, data: Dict) -> str:
        """生成Markdown报告"""
        lines = [
            "# 错误追踪报告",
            f"\n生成时间: {data['generated_at']}\n",
            "## 摘要",
            f"- 总错误数: {data['summary']['total_errors']}",
            f"- 唯一错误类型: {data['summary']['unique_types']}\n",
            "## Top 10 错误",
            "| 错误类型 | 次数 |",
            "|----------|------|"
        ]
        
        for error in data['top_errors'][:10]:
            lines.append(f"| {error['type']} | {error['count']} |")
        
        lines.append("\n## 错误分组")
        for group in data['aggregated_by_similarity'][:10]:
            lines.append(f"\n### {group['representative']['error_type']} ({group['count']} 次)")
            lines.append(f"消息: {group['representative']['message'][:100]}...")
        
        return '\n'.join(lines)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='错误追踪分析工具')
    parser.add_argument('--input', '-i', required=True, help='输入日志文件路径')
    parser.add_argument('--format', '-f', choices=['python', 'java', 'javascript', 'go', 'auto'],
                       default='auto', help='日志格式')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--threshold', type=float, default=0.8, help='相似度阈值')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # analyze命令
    subparsers.add_parser('analyze', help='分析错误')
    
    # aggregate命令
    aggregate_parser = subparsers.add_parser('aggregate', help='聚合相似错误')
    aggregate_parser.add_argument('--threshold', type=float, default=0.8, help='相似度阈值')
    
    # trend命令
    trend_parser = subparsers.add_parser('trend', help='分析趋势')
    trend_parser.add_argument('--hours', type=int, default=24, help='时间范围')
    
    # report命令
    report_parser = subparsers.add_parser('report', help='生成报告')
    report_parser.add_argument('--format', choices=['json', 'html', 'markdown'],
                              default='json', help='报告格式')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    tracker = ErrorTracker(similarity_threshold=args.threshold)
    
    try:
        if args.command == 'analyze':
            result = tracker.analyze_file(args.input, format_hint=args.format)
            output = json.dumps(result, indent=2, ensure_ascii=False, default=str)
        
        elif args.command == 'aggregate':
            tracker.analyze_file(args.input, format_hint=args.format)
            result = tracker.aggregate_by_stack_similarity(threshold=args.threshold)
            output = json.dumps(result, indent=2, ensure_ascii=False, default=str)
        
        elif args.command == 'trend':
            tracker.analyze_file(args.input, format_hint=args.format)
            result = tracker.analyze_trend(hours=args.hours)
            output = json.dumps(result, indent=2, ensure_ascii=False, default=str)
        
        elif args.command == 'report':
            tracker.analyze_file(args.input, format_hint=args.format)
            output = tracker.generate_report(format=args.report_format)
        
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
        logger.error(f"分析失败: {e}")
        raise


if __name__ == '__main__':
    main()
