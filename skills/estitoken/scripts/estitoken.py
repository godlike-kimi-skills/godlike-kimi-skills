#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EstiToken - Token消耗估算器
智能任务Token消耗估算与成本分析工具

借鉴: tiktoken, OpenAI Token计数器, Claude Code Token优化策略
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import fnmatch


@dataclass
class ModelPricing:
    """模型定价信息"""
    name: str
    input_price: float  # 每1K tokens价格(USD)
    output_price: float
    max_context: int
    description: str


# 模型定价表 (USD per 1K tokens)
MODELS = {
    "kimi-for-coding": ModelPricing(
        name="kimi-for-coding",
        input_price=0.005,
        output_price=0.025,
        max_context=262144,
        description="Kimi标准模型，适合日常编码任务"
    ),
    "kimi-k2": ModelPricing(
        name="kimi-k2-0905-preview",
        input_price=0.015,
        output_price=0.060,
        max_context=262144,
        description="Kimi高级模型，适合复杂推理"
    ),
    "gpt-4": ModelPricing(
        name="gpt-4",
        input_price=0.030,
        output_price=0.060,
        max_context=8192,
        description="GPT-4标准版"
    ),
    "gpt-4-turbo": ModelPricing(
        name="gpt-4-turbo",
        input_price=0.010,
        output_price=0.030,
        max_context=128000,
        description="GPT-4 Turbo，更大上下文"
    ),
    "claude-3-opus": ModelPricing(
        name="claude-3-opus",
        input_price=0.015,
        output_price=0.075,
        max_context=200000,
        description="Claude 3 Opus，最强推理"
    ),
    "claude-3-sonnet": ModelPricing(
        name="claude-3-sonnet",
        input_price=0.003,
        output_price=0.015,
        max_context=200000,
        description="Claude 3 Sonnet，平衡性价比"
    ),
}

# 任务复杂度系数
COMPLEXITY_MULTIPLIERS = {
    "low": 1.0,
    "medium": 2.5,
    "high": 5.0,
    "expert": 8.0,
}

# 任务类型基准Token消耗 (输入:输出比例)
TASK_PATTERNS = {
    "file_read": (100, 50),
    "code_review": (1000, 500),
    "documentation": (500, 1000),
    "refactoring": (1000, 800),
    "debugging": (2000, 1500),
    "architecture": (3000, 2500),
    "planning": (2000, 2000),
    "code_generation": (500, 1500),
    "testing": (800, 600),
    "optimization": (1500, 1000),
}


class TokenEstimator:
    """Token估算器核心类"""
    
    def __init__(self, stats_path: Optional[Path] = None):
        self.stats_path = stats_path or (Path.home() / ".kimi" / "estitoken-stats.json")
        self.stats = self._load_stats()
    
    def _load_stats(self) -> dict:
        """加载统计历史"""
        if self.stats_path.exists():
            try:
                with open(self.stats_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "estimates": [],
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    
    def _save_stats(self):
        """保存统计历史"""
        self.stats_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.stats_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
    
    def estimate_text(self, text: str, content_type: str = "mixed") -> int:
        """
        估算文本的Token数量
        
        Args:
            text: 输入文本
            content_type: 内容类型 (chinese/english/code/mixed)
        
        Returns:
            估算的Token数量
        """
        if not text:
            return 0
        
        char_count = len(text)
        
        # 根据内容类型选择系数
        if content_type == "chinese":
            # 中文约 1.5 字符/token
            return int(char_count / 1.5)
        elif content_type == "english":
            # 英文约 4 字符/token
            return int(char_count / 4)
        elif content_type == "code":
            # 代码约 3.5 字符/token
            return int(char_count / 3.5)
        else:  # mixed - 智能检测
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
            english_chars = len(re.findall(r'[a-zA-Z]', text))
            
            if chinese_chars > english_chars:
                return int(char_count / 2)
            else:
                return int(char_count / 3.5)
    
    def detect_content_type(self, text: str) -> str:
        """自动检测内容类型"""
        chinese_ratio = len(re.findall(r'[\u4e00-\u9fff]', text)) / max(len(text), 1)
        code_patterns = len(re.findall(r'[{};()=<>]|def |class |import |function', text))
        
        if code_patterns > 5:
            return "code"
        elif chinese_ratio > 0.3:
            return "chinese"
        else:
            return "english"
    
    def estimate_file(self, filepath: Union[str, Path], 
                     content_type: Optional[str] = None) -> Dict:
        """
        估算单个文件的Token数量
        
        Returns:
            包含文件信息的字典
        """
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")
        
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return {
                "path": str(path),
                "error": str(e),
                "tokens": 0
            }
        
        # 自动检测内容类型
        detected_type = content_type or self.detect_content_type(content)
        tokens = self.estimate_text(content, detected_type)
        
        return {
            "path": str(path),
            "name": path.name,
            "size": path.stat().st_size,
            "chars": len(content),
            "lines": content.count('\n') + 1,
            "tokens": tokens,
            "content_type": detected_type
        }
    
    def estimate_directory(self, dirpath: Union[str, Path], 
                          pattern: str = "*",
                          recursive: bool = True) -> List[Dict]:
        """
        批量估算目录下的文件
        
        Args:
            dirpath: 目录路径
            pattern: 文件匹配模式 (如 "*.py", "*.md")
            recursive: 是否递归子目录
        
        Returns:
            文件估算结果列表
        """
        path = Path(dirpath)
        results = []
        
        if recursive:
            files = list(path.rglob(pattern))
        else:
            files = list(path.glob(pattern))
        
        # 排除常见非文本文件
        exclude_patterns = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.ico', 
                          '*.pdf', '*.zip', '*.tar.gz', '*.exe', '*.dll']
        
        for filepath in files:
            if filepath.is_file():
                # 检查是否在排除列表
                should_exclude = any(fnmatch.fnmatch(filepath.name, p) 
                                   for p in exclude_patterns)
                if should_exclude:
                    continue
                
                try:
                    result = self.estimate_file(filepath)
                    results.append(result)
                except Exception:
                    pass  # 跳过无法读取的文件
        
        return sorted(results, key=lambda x: x.get('tokens', 0), reverse=True)
    
    def estimate_task(self, task_description: str, 
                     complexity: str = "medium",
                     context_tokens: int = 0) -> Dict:
        """
        基于任务描述估算Token消耗
        
        Args:
            task_description: 任务描述
            complexity: 复杂度 (low/medium/high/expert)
            context_tokens: 已有上下文Token数
        
        Returns:
            任务估算结果
        """
        # 检测任务类型
        task_type = self._detect_task_type(task_description)
        
        # 获取基准消耗
        base_input, base_output = TASK_PATTERNS.get(task_type, (1000, 500))
        
        # 应用复杂度系数
        multiplier = COMPLEXITY_MULTIPLIERS.get(complexity, 2.5)
        
        estimated_input = int((base_input + context_tokens) * multiplier)
        estimated_output = int(base_output * multiplier)
        
        return {
            "task": task_description,
            "task_type": task_type,
            "complexity": complexity,
            "multiplier": multiplier,
            "input_tokens": estimated_input,
            "output_tokens": estimated_output,
            "total_tokens": estimated_input + estimated_output,
            "context_tokens": context_tokens
        }
    
    def _detect_task_type(self, description: str) -> str:
        """从描述中检测任务类型"""
        description_lower = description.lower()
        
        keywords = {
            "file_read": ["读取", "查看", "打开", "read", "open"],
            "code_review": ["审查", "review", "检查", "代码审查", "codereview"],
            "documentation": ["文档", "documentation", "readme", "注释"],
            "refactoring": ["重构", "refactor", "重写", "优化代码"],
            "debugging": ["调试", "debug", "修复", "fix", "bug"],
            "architecture": ["架构", "architecture", "设计", "design", "系统"],
            "planning": ["规划", "计划", "plan", "roadmap", "里程碑"],
            "code_generation": ["生成代码", "编写", "create", "generate", "实现"],
            "testing": ["测试", "test", "单元测试", "unittest"],
            "optimization": ["优化", "optimize", "性能", "提速"],
        }
        
        for task_type, words in keywords.items():
            if any(word in description_lower for word in words):
                return task_type
        
        return "code_generation"  # 默认类型
    
    def log_estimate(self, result: Dict):
        """记录估算历史"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            **result
        }
        self.stats["estimates"].append(entry)
        self._save_stats()


class CostAnalyzer:
    """成本分析器"""
    
    def __init__(self, model: str = "kimi-for-coding"):
        self.model = model
        self.pricing = MODELS.get(model)
        if not self.pricing:
            raise ValueError(f"未知模型: {model}")
    
    def calculate_cost(self, input_tokens: int, output_tokens: int = 0) -> Dict:
        """
        计算成本
        
        Returns:
            成本明细字典
        """
        input_cost = (input_tokens / 1000) * self.pricing.input_price
        output_cost = (output_tokens / 1000) * self.pricing.output_price
        total_cost = input_cost + output_cost
        
        return {
            "model": self.model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "currency": "USD"
        }
    
    def compare_models(self, input_tokens: int, 
                       output_tokens: int = 0) -> List[Dict]:
        """对比多个模型的成本"""
        results = []
        for model_name, pricing in MODELS.items():
            analyzer = CostAnalyzer(model_name)
            cost = analyzer.calculate_cost(input_tokens, output_tokens)
            results.append(cost)
        
        return sorted(results, key=lambda x: x["total_cost"])
    
    def generate_report(self, estimates: List[Dict]) -> str:
        """生成格式化的报告"""
        if not estimates:
            return "没有估算数据"
        
        total_tokens = sum(e.get('tokens', 0) for e in estimates)
        total_chars = sum(e.get('chars', 0) for e in estimates)
        total_lines = sum(e.get('lines', 0) for e in estimates)
        
        # 成本计算
        cost = self.calculate_cost(total_tokens, total_tokens // 2)
        
        lines = [
            "=" * 60,
            "                    Token 估算报告",
            "=" * 60,
            "",
            f"📊 统计信息:",
            f"  文件数: {len(estimates)}",
            f"  总字符: {total_chars:,}",
            f"  总行数: {total_lines:,}",
            f"  总Token: {total_tokens:,}",
            "",
            f"💰 成本估算 ({self.model}):",
            f"  输入: ${cost['input_cost']:.4f} ({cost['input_tokens']:,} tokens)",
            f"  输出: ${cost['output_cost']:.4f} ({cost['output_tokens']:,} tokens)",
            f"  总计: ${cost['total_cost']:.4f}",
            "",
        ]
        
        # 添加文件列表
        if len(estimates) <= 10:
            lines.append("📁 文件明细:")
            for i, e in enumerate(estimates[:10], 1):
                lines.append(f"  {i}. {e.get('name', 'unknown'):30} {e.get('tokens', 0):>6} tokens")
        else:
            lines.append(f"📁 Top 10 文件 (共 {len(estimates)} 个):")
            for i, e in enumerate(estimates[:10], 1):
                lines.append(f"  {i}. {e.get('name', 'unknown'):30} {e.get('tokens', 0):>6} tokens")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("  EstiToken - Token消耗估算器 v1.0.0")
    print("  智能任务Token消耗估算与成本分析")
    print("=" * 60)
    print()


def main():
    parser = argparse.ArgumentParser(
        description="EstiToken - Token消耗估算器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  estitoken "这是一段中文文本"                    # 估算文本
  estitoken --file README.md                       # 估算文件
  estitoken --dir ./src --pattern "*.py"          # 估算目录
  estitoken --task "重构项目" --complexity high   # 估算任务
  estitoken --report                               # 查看报告
        """
    )
    
    # 输入选项
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("text", nargs="?", help="要估算的文本")
    input_group.add_argument("--file", "-f", help="要估算的文件路径")
    input_group.add_argument("--dir", "-d", help="要估算的目录路径")
    input_group.add_argument("--task", "-t", help="任务描述")
    input_group.add_argument("--report", "-r", action="store_true", help="显示统计报告")
    
    # 选项
    parser.add_argument("--pattern", "-p", default="*", 
                       help="文件匹配模式 (默认: *)")
    parser.add_argument("--model", "-m", default="kimi-for-coding",
                       choices=list(MODELS.keys()),
                       help="使用的模型 (默认: kimi-for-coding)")
    parser.add_argument("--complexity", "-c", default="medium",
                       choices=["low", "medium", "high", "expert"],
                       help="任务复杂度 (默认: medium)")
    parser.add_argument("--compare", action="store_true",
                       help="对比所有模型成本")
    parser.add_argument("--json", "-j", action="store_true",
                       help="输出JSON格式")
    parser.add_argument("--no-banner", action="store_true",
                       help="不显示横幅")
    
    args = parser.parse_args()
    
    if not args.no_banner:
        print_banner()
    
    estimator = TokenEstimator()
    analyzer = CostAnalyzer(args.model)
    
    # 文本估算
    if args.text:
        content_type = estimator.detect_content_type(args.text)
        tokens = estimator.estimate_text(args.text, content_type)
        cost = analyzer.calculate_cost(tokens, tokens // 2)
        
        result = {
            "type": "text",
            "content_type": content_type,
            "chars": len(args.text),
            "tokens": tokens,
            "cost": cost
        }
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"文本类型: {content_type}")
            print(f"字符数: {len(args.text)}")
            print(f"估算Token: ~{tokens}")
            print(f"预估成本: ${cost['total_cost']:.4f}")
    
    # 文件估算
    elif args.file:
        try:
            result = estimator.estimate_file(args.file)
            cost = analyzer.calculate_cost(result['tokens'], result['tokens'] // 2)
            result['cost'] = cost
            
            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"文件: {result['name']}")
                print(f"大小: {result['size']:,} bytes")
                print(f"行数: {result['lines']}")
                print(f"字符: {result['chars']}")
                print(f"Token: ~{result['tokens']}")
                print(f"预估成本: ${cost['total_cost']:.4f}")
                
                if args.compare:
                    print("\n模型对比:")
                    comparisons = analyzer.compare_models(result['tokens'], result['tokens'] // 2)
                    for c in comparisons:
                        print(f"  {c['model']:20} ${c['total_cost']:.4f}")
        
        except FileNotFoundError:
            print(f"错误: 文件不存在 - {args.file}")
            sys.exit(1)
    
    # 目录估算
    elif args.dir:
        results = estimator.estimate_directory(args.dir, args.pattern)
        
        if not results:
            print(f"未找到匹配文件: {args.dir}/{args.pattern}")
            sys.exit(0)
        
        report = analyzer.generate_report(results)
        print(report)
        
        if args.compare:
            total_tokens = sum(e.get('tokens', 0) for e in results)
            print("\n" + "=" * 60)
            print("模型成本对比:")
            print("=" * 60)
            comparisons = analyzer.compare_models(total_tokens, total_tokens // 2)
            for c in comparisons:
                print(f"  {c['model']:20} ${c['total_cost']:.4f}")
    
    # 任务估算
    elif args.task:
        result = estimator.estimate_task(args.task, args.complexity)
        cost = analyzer.calculate_cost(result['input_tokens'], result['output_tokens'])
        result['cost'] = cost
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"任务: {result['task']}")
            print(f"类型: {result['task_type']}")
            print(f"复杂度: {result['complexity']} (x{result['multiplier']})")
            print(f"输入Token: ~{result['input_tokens']}")
            print(f"输出Token: ~{result['output_tokens']}")
            print(f"总计: ~{result['total_tokens']} tokens")
            print(f"预估成本: ${cost['total_cost']:.4f}")
    
    # 报告
    elif args.report:
        print("统计报告功能开发中...")
        print(f"统计数据保存在: {estimator.stats_path}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
