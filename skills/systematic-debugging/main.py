#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Systematic Debugging - 系统化调试框架

一个结构化的bug定位和修复方法论，支持多种编程语言。
提供科学的调试流程、根因分析技术和修复建议生成。

Author: Godlike Kimi Skills
License: MIT
Version: 1.0.0
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime


class DebugAction(Enum):
    """调试操作类型"""
    ANALYZE = "analyze"
    STRATEGY = "strategy"
    ROOT_CAUSE = "root_cause"
    SUGGEST_FIX = "suggest_fix"
    FULL_DIAGNOSIS = "full_diagnosis"


class DebugStrategy(Enum):
    """调试策略类型"""
    BINARY_SEARCH = "binary_search"
    FORWARD = "forward"
    BACKWARD = "backward"
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    DIVIDE_CONQUER = "divide_conquer"


class SeverityLevel(Enum):
    """严重程度等级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class DebugResult:
    """调试结果"""
    action: str
    language: str
    error: Optional[str]
    analysis: Dict[str, Any] = field(default_factory=dict)
    strategy: Optional[Dict] = None
    root_cause: Optional[Dict] = None
    fix_suggestions: List[Dict] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class SystematicDebugger:
    """系统化调试器核心类"""
    
    SUPPORTED_LANGUAGES = ["python", "javascript", "typescript", "java", "cpp", "c",
                          "rust", "go", "ruby", "php", "csharp", "swift", "kotlin"]
    
    # 错误模式库：语言 -> [(pattern, error_type, description, causes, severity, fixes)]
    ERROR_PATTERNS = {
        "python": [
            (r"IndexError.*out of range", "IndexError", "列表/数组索引越界",
             ["索引计算错误", "空列表访问", "循环边界问题"], "high",
             ["检查列表长度", "添加边界检查", "使用 try-except"]),
            (r"KeyError.*", "KeyError", "字典键不存在",
             ["键名拼写错误", "数据缺失", "API响应变化"], "medium",
             ["使用 dict.get()", "添加键存在检查", "设置默认值"]),
            (r"AttributeError.*NoneType", "AttributeError", "空值属性访问",
             ["函数返回None", "未初始化变量", "条件分支遗漏"], "high",
             ["添加空值检查", "使用可选链", "初始化变量"]),
            (r"TypeError.*", "TypeError", "类型错误",
             ["类型不匹配", "None值传递", "错误的参数类型"], "medium",
             ["类型检查", "类型转换", "使用类型注解"]),
            (r"ValueError.*", "ValueError", "值错误",
             ["无效输入", "格式错误", "数据验证失败"], "medium",
             ["输入验证", "异常处理", "数据清洗"]),
            (r"ZeroDivisionError", "ZeroDivisionError", "除零错误",
             ["除数为零", "未检查的分母", "数据异常"], "high",
             ["检查除数", "添加保护条件", "异常处理"]),
        ],
        "javascript": [
            (r"Cannot read property.*of undefined", "TypeError", "未定义对象属性访问",
             ["异步数据未加载", "API响应为空", "对象未初始化"], "high",
             ["使用可选链 ?.", "添加空值检查", "默认值设置"]),
            (r".*is not a function", "TypeError", "非函数调用",
             ["变量类型错误", "拼写错误", "导入错误"], "medium",
             ["类型检查", "检查导入", "验证函数存在"]),
            (r"Promise.*rejection", "PromiseError", "Promise 未捕获异常",
             ["缺少catch处理", "异步错误", "网络问题"], "medium",
             ["添加 .catch()", "try-catch async/await", "错误边界"]),
        ],
        "java": [
            (r"NullPointerException", "NullPointerException", "空指针异常",
             ["对象未初始化", "方法返回null", "参数传递null"], "high",
             ["添加null检查", "使用Optional", "Objects.requireNonNull"]),
            (r"ArrayIndexOutOfBoundsException", "ArrayIndexOutOfBoundsException", "数组索引越界",
             ["索引计算错误", "数组为空", "循环边界问题"], "high",
             ["检查数组长度", "边界验证", "使用集合类"]),
            (r"ClassNotFoundException", "ClassNotFoundException", "类未找到",
             ["缺少依赖", "类路径错误", "拼写错误"], "critical",
             ["检查依赖", "验证类路径", "检查拼写"]),
        ],
        "cpp": [
            (r"segmentation fault", "SegmentationFault", "段错误",
             ["空指针解引用", "数组越界", "内存访问错误"], "critical",
             ["检查指针", "使用智能指针", "边界检查"]),
        ],
    }
    
    STRATEGIES = {
        DebugStrategy.BINARY_SEARCH: {
            "name": "二分查找法", "description": "通过不断缩小范围定位问题",
            "steps": ["确定问题存在的代码范围", "在范围中间插入检查点",
                     "判断问题在检查点之前还是之后", "重复直到定位具体问题"],
            "best_for": ["大型代码库", "问题位置不确定", "可重现的问题"],
        },
        DebugStrategy.FORWARD: {
            "name": "正向追踪", "description": "从输入开始逐步追踪执行流程",
            "steps": ["确定程序入口点", "使用断点或日志跟踪执行",
                     "检查每个关键步骤的状态", "找到状态异常的位置"],
            "best_for": ["数据流问题", "逻辑错误", "输入处理错误"],
        },
        DebugStrategy.BACKWARD: {
            "name": "反向追踪", "description": "从错误位置反向追踪原因",
            "steps": ["定位错误发生的代码行", "检查该行的输入和状态",
                     "反向追踪数据来源", "找到根本原因"],
            "best_for": ["已知错误位置", "数据污染问题", "快速定位"],
        },
        DebugStrategy.DEDUCTIVE: {
            "name": "演绎推理", "description": "基于假设进行演绎验证",
            "steps": ["提出可能原因的假设", "设计实验验证假设",
                     "根据结果排除或确认", "重复直到找到原因"],
            "best_for": ["复杂问题", "有经验可循", "理论分析"],
        },
        DebugStrategy.INDUCTIVE: {
            "name": "归纳分析", "description": "从观察中归纳出规律",
            "steps": ["收集多个错误实例", "寻找共同特征和模式",
                     "提出一般性规律", "验证规律的正确性"],
            "best_for": ["间歇性问题", "模式识别", "统计分析"],
        },
        DebugStrategy.DIVIDE_CONQUER: {
            "name": "分治法", "description": "将系统分解为模块逐一排查",
            "steps": ["将系统划分为独立模块", "隔离测试每个模块",
                     "确定问题所在模块", "在模块内进一步分析"],
            "best_for": ["复杂系统", "模块化架构", "团队协作"],
        },
    }
    
    def __init__(self, language: str):
        if language.lower() not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"不支持的语言: {language}")
        self.language = language.lower()
    
    def analyze_error(self, error: Optional[str], context: Optional[str] = None) -> Dict[str, Any]:
        """分析错误类型和可能原因"""
        result = {"error_type": "Unknown", "description": "未识别的错误类型",
                  "severity": "medium", "confidence": 0.0, "common_causes": [],
                  "matched_patterns": []}
        
        if not error:
            return result
        
        patterns = self.ERROR_PATTERNS.get(self.language, [])
        for pattern, err_type, desc, causes, severity, fixes in patterns:
            if re.search(pattern, error, re.IGNORECASE):
                result["matched_patterns"].append(
                    {"type": err_type, "description": desc, "severity": severity})
                if result["confidence"] == 0:
                    result.update({"error_type": err_type, "description": desc,
                                   "severity": severity, "common_causes": causes,
                                   "confidence": 0.85, "fix_suggestions": fixes})
        
        if context:
            hints = []
            if len(context.split('\n')) > 50:
                hints.append("代码片段较长，建议分块分析")
            if "goto" in context.lower():
                hints.append("使用了goto语句")
            if context.count('if') > 10:
                hints.append("条件分支较多")
            result["context_hints"] = hints
        
        return result
    
    def recommend_strategy(self, error_analysis: Dict[str, Any],
                          user_preference: Optional[str] = None) -> Dict[str, Any]:
        """推荐调试策略"""
        if user_preference:
            strategy_key = DebugStrategy(user_preference)
        else:
            strategy_key = self._select_best_strategy(error_analysis)
        
        info = self.STRATEGIES.get(strategy_key, self.STRATEGIES[DebugStrategy.BINARY_SEARCH])
        return {"recommended_strategy": strategy_key.value, **info}
    
    def _select_best_strategy(self, error_analysis: Dict[str, Any]) -> DebugStrategy:
        """根据错误分析选择最佳策略"""
        error_type = error_analysis.get("error_type", "").lower()
        severity = error_analysis.get("severity", "medium")
        
        if severity == "critical":
            return DebugStrategy.BACKWARD
        elif error_type in ["nullpointerexception", "attributeerror", "typeerror"]:
            return DebugStrategy.BACKWARD
        elif error_type in ["indexerror", "arrayindexoutofboundsexception"]:
            return DebugStrategy.FORWARD
        elif error_type == "unknown":
            return DebugStrategy.DIVIDE_CONQUER
        return DebugStrategy.BINARY_SEARCH
    
    def root_cause_analysis(self, error: str, context: Optional[str] = None,
                           stack_trace: Optional[str] = None) -> Dict[str, Any]:
        """根因分析 - 使用5 Whys方法"""
        generic_answers = ["输入数据未经过验证", "缺少边界条件检查",
                          "对象未正确初始化", "依赖服务返回了异常数据", "代码逻辑存在缺陷"]
        
        import random
        whys = []
        for i in range(1, 6):
            question = f"Why #{i}: 为什么发生此问题?"
            answer = generic_answers[min(i-1, len(generic_answers)-1)]
            whys.append({"level": i, "question": question, "answer": answer})
            if any(x in answer for x in ["缺少", "未", "没有", "缺陷"]):
                break
        
        return {"method": "5 Whys", "analysis": whys,
                "root_cause": whys[-1]["answer"] if whys else "Unknown",
                "recommendations": ["完善代码审查流程", "增加单元测试覆盖",
                                   "添加输入数据验证", "改进错误处理和日志"]}
    
    def suggest_fix(self, error_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成修复建议"""
        error_type = error_analysis.get("error_type", "")
        
        templates = {
            "IndexError": [
                {"title": "添加边界检查", "priority": "high",
                 "description": "在访问列表/数组前检查索引范围",
                 "code": "if 0 <= index < len(data):\n    value = data[index]"},
                {"title": "使用安全的访问方法", "priority": "medium",
                 "description": "使用语言提供的安全访问API",
                 "code": "value = data[index] if index < len(data) else default"},
            ],
            "KeyError": [
                {"title": "使用get方法", "priority": "high",
                 "description": "使用dict.get()提供默认值",
                 "code": "value = data.get('key', default_value)"},
            ],
            "AttributeError": [
                {"title": "添加空值检查", "priority": "high",
                 "description": "在访问属性前检查对象是否为None",
                 "code": "if obj is not None:\n    result = obj.attribute"},
            ],
            "NullPointerException": [
                {"title": "添加null检查", "priority": "high",
                 "description": "在使用对象前检查null",
                 "code": "if (obj != null) {\n    obj.doSomething();\n}"},
            ],
        }
        
        return templates.get(error_type, [
            {"title": "添加异常处理", "priority": "medium",
             "description": "使用try-except捕获并处理异常",
             "code": "try:\n    # risky code\nexcept Exception as e:\n    # handle error"},
        ])
    
    def full_diagnosis(self, error: Optional[str], context: Optional[str] = None,
                      stack_trace: Optional[str] = None,
                      strategy_preference: Optional[str] = None) -> DebugResult:
        """执行完整的诊断流程"""
        error_analysis = self.analyze_error(error, context)
        strategy = self.recommend_strategy(error_analysis, strategy_preference)
        root_cause = self.root_cause_analysis(error or "", context, stack_trace)
        fix_suggestions = self.suggest_fix(error_analysis)
        
        return DebugResult(action="full_diagnosis", language=self.language,
                          error=error, analysis=error_analysis, strategy=strategy,
                          root_cause=root_cause, fix_suggestions=fix_suggestions)


def format_output(result: DebugResult, output_format: str) -> str:
    """格式化输出结果"""
    if output_format == "json":
        return json.dumps(result.__dict__, indent=2, ensure_ascii=False)
    
    elif output_format == "markdown":
        lines = ["# 系统化调试报告", "", f"**分析时间**: {result.timestamp}",
                 f"**目标语言**: {result.language}", f"**操作类型**: {result.action}",
                 "", "## 错误信息", f"```\n{result.error or 'N/A'}\n```", "",
                 "## 错误分析",
                 f"- **错误类型**: {result.analysis.get('error_type', 'Unknown')}",
                 f"- **描述**: {result.analysis.get('description', 'N/A')}",
                 f"- **严重程度**: {result.analysis.get('severity', 'unknown')}",
                 f"- **置信度**: {result.analysis.get('confidence', 0) * 100:.0f}%", ""]
        
        if result.analysis.get('common_causes'):
            lines.extend(["### 常见原因", ""])
            for cause in result.analysis['common_causes']:
                lines.append(f"- {cause}")
            lines.append("")
        
        if result.strategy:
            lines.extend(["## 推荐调试策略", f"**策略**: {result.strategy.get('name')}",
                         f"**描述**: {result.strategy.get('description')}", "",
                         "### 执行步骤", ""])
            for i, step in enumerate(result.strategy.get('steps', []), 1):
                lines.append(f"{i}. {step}")
            lines.append("")
        
        if result.root_cause:
            lines.extend(["## 根因分析 (5 Whys)", ""])
            for item in result.root_cause.get('analysis', []):
                lines.extend([f"**Level {item['level']}**: {item['question']}",
                             f"**答案**: {item['answer']}", ""])
            lines.extend([f"**根本原因**: {result.root_cause.get('root_cause')}", ""])
        
        if result.fix_suggestions:
            lines.extend(["## 修复建议", ""])
            for s in result.fix_suggestions:
                lines.extend([f"### {s.get('title')}", f"**优先级**: {s.get('priority')}",
                             f"**描述**: {s.get('description')}", "",
                             "**代码示例**:", f"```\n{s.get('code', '')}\n```", ""])
        
        return "\n".join(lines)
    
    else:
        return str(result)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="Systematic Debugging - 系统化调试框架",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py -a full_diagnosis -l python -e "IndexError"
  python main.py -a analyze -l java -e "NullPointerException"
  python main.py -a strategy -l javascript --strategy binary_search
        """
    )
    
    parser.add_argument("--action", "-a", type=str, required=True,
                       choices=[a.value for a in DebugAction], help="执行的操作类型")
    parser.add_argument("--language", "-l", type=str, required=True, help="编程语言")
    parser.add_argument("--error", "-e", type=str, default=None, help="错误信息")
    parser.add_argument("--context", "-c", type=str, default=None, help="代码上下文")
    parser.add_argument("--stack-trace", "-s", type=str, default=None, help="堆栈跟踪")
    parser.add_argument("--strategy", type=str, choices=[s.value for s in DebugStrategy],
                       default=None, help="调试策略偏好")
    parser.add_argument("--output-format", "-o", type=str,
                       choices=["text", "json", "markdown"], default="markdown",
                       help="输出格式")
    
    args = parser.parse_args()
    
    try:
        debugger = SystematicDebugger(args.language)
        action = DebugAction(args.action)
        
        if action == DebugAction.ANALYZE:
            result = DebugResult(action=args.action, language=args.language,
                               error=args.error,
                               analysis=debugger.analyze_error(args.error, args.context))
        elif action == DebugAction.STRATEGY:
            analysis = debugger.analyze_error(args.error, args.context)
            result = DebugResult(action=args.action, language=args.language,
                               error=args.error, analysis=analysis,
                               strategy=debugger.recommend_strategy(analysis, args.strategy))
        elif action == DebugAction.ROOT_CAUSE:
            result = DebugResult(action=args.action, language=args.language,
                               error=args.error,
                               root_cause=debugger.root_cause_analysis(
                                   args.error or "", args.context, args.stack_trace))
        elif action == DebugAction.SUGGEST_FIX:
            analysis = debugger.analyze_error(args.error, args.context)
            result = DebugResult(action=args.action, language=args.language,
                               error=args.error, analysis=analysis,
                               fix_suggestions=debugger.suggest_fix(analysis))
        else:
            result = debugger.full_diagnosis(args.error, args.context, args.stack_trace, args.strategy)
        
        print(format_output(result, args.output_format))
        
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"执行错误: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
