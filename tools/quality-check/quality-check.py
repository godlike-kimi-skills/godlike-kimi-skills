#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Godlike Skills 质量检查工具 / Quality Check Tool

自动化质量评估脚本 / Automated quality assessment script
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QualityScore:
    """质量分数数据结构 / Quality score data structure"""
    dimension: str
    score: int
    max_score: int
    details: List[str]


class QualityChecker:
    """质量检查器 / Quality checker"""
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.scores: List[QualityScore] = []
        self.total_score = 0
        self.max_total = 100
        
    def check_all(self) -> Dict:
        """执行所有检查 / Run all checks"""
        print("=" * 60)
        print("🔍 Godlike Skills 质量检查 / Quality Check")
        print("=" * 60)
        print()
        
        # 1. 功能完整性检查 / Functional completeness
        self._check_functionality()
        
        # 2. 代码质量检查 / Code quality
        self._check_code_quality()
        
        # 3. 文档质量检查 / Documentation quality
        self._check_documentation()
        
        # 4. 安全性检查 / Security
        self._check_security()
        
        # 5. 规范符合度检查 / Standards compliance
        self._check_standards()
        
        # 6. 社区反馈检查 / Community feedback
        self._check_community()
        
        # 计算总分 / Calculate total score
        self.total_score = sum(s.score for s in self.scores)
        
        return self._generate_report()
    
    def _check_functionality(self):
        """功能完整性检查 / Check functionality"""
        print("📦 检查功能完整性 / Checking functionality...")
        
        score = 0
        details = []
        max_score = 25
        
        # 检查SKILL.md存在 / Check SKILL.md exists
        skill_md = self.skill_path / "SKILL.md"
        if skill_md.exists():
            score += 10
            details.append("✅ SKILL.md 存在 / exists")
            
            # 检查功能描述 / Check function description
            content = skill_md.read_text(encoding='utf-8')
            if "功能" in content or "Features" in content:
                score += 5
                details.append("✅ 功能描述完整 / Function description complete")
        else:
            details.append("❌ 缺少 SKILL.md / Missing SKILL.md")
        
        # 检查脚本存在 / Check scripts exist
        scripts_dir = self.skill_path / "scripts"
        if scripts_dir.exists() and list(scripts_dir.glob("*.py")):
            score += 5
            details.append("✅ 脚本文件存在 / Script files exist")
        else:
            details.append("❌ 缺少脚本文件 / Missing script files")
        
        # 检查示例 / Check examples
        examples_dir = self.skill_path / "examples"
        if examples_dir.exists() and list(examples_dir.glob("*")):
            score += 5
            details.append("✅ 示例文件存在 / Examples exist")
        
        self.scores.append(QualityScore(
            dimension="功能完整性 / Functionality",
            score=min(score, max_score),
            max_score=max_score,
            details=details
        ))
        print(f"   得分 / Score: {score}/{max_score}")
        print()
    
    def _check_code_quality(self):
        """代码质量检查 / Check code quality"""
        print("💻 检查代码质量 / Checking code quality...")
        
        score = 0
        details = []
        max_score = 25
        
        scripts_dir = self.skill_path / "scripts"
        if scripts_dir.exists():
            py_files = list(scripts_dir.glob("*.py"))
            
            # 检查是否有测试 / Check for tests
            tests_dir = self.skill_path / "tests"
            if tests_dir.exists() and list(tests_dir.glob("test_*.py")):
                score += 10
                details.append("✅ 包含测试文件 / Test files included")
            else:
                details.append("⚠️ 缺少测试文件 / Missing test files")
            
            # 检查代码注释 / Check code comments
            for py_file in py_files[:3]:  # 检查前3个文件
                content = py_file.read_text(encoding='utf-8')
                if '"""' in content or "'''" in content:
                    score += 5
                    details.append(f"✅ {py_file.name} 有文档注释 / Has docstrings")
                    break
            
            # 检查错误处理 / Check error handling
            for py_file in py_files[:1]:
                content = py_file.read_text(encoding='utf-8')
                if "try:" in content and "except" in content:
                    score += 5
                    details.append("✅ 包含错误处理 / Error handling included")
                    break
                else:
                    details.append("⚠️ 建议添加错误处理 / Suggest adding error handling")
        
        self.scores.append(QualityScore(
            dimension="代码质量 / Code Quality",
            score=min(score, max_score),
            max_score=max_score,
            details=details
        ))
        print(f"   得分 / Score: {score}/{max_score}")
        print()
    
    def _check_documentation(self):
        """文档质量检查 / Check documentation"""
        print("📚 检查文档质量 / Checking documentation...")
        
        score = 0
        details = []
        max_score = 20
        
        skill_md = self.skill_path / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding='utf-8')
            
            # 检查双语 / Check bilingual
            has_chinese = bool(re.search(r'[\u4e00-\u9fff]', content))
            has_english = bool(re.search(r'[a-zA-Z]{5,}', content))
            
            if has_chinese and has_english:
                score += 6
                details.append("✅ 双语文档 / Bilingual documentation")
            elif has_chinese:
                score += 3
                details.append("⚠️ 建议添加英文 / Suggest adding English")
            
            # 检查关键章节 / Check key sections
            sections = ["安装", "使用", "示例", "参数", "Introduction", "Usage", "Example"]
            found_sections = sum(1 for s in sections if s in content)
            if found_sections >= 4:
                score += 8
                details.append(f"✅ 文档结构完整 ({found_sections}个章节) / Document structure complete")
            else:
                details.append(f"⚠️ 文档章节不足 / Insufficient sections ({found_sections})")
            
            # 检查示例 / Check examples
            if "```" in content:
                score += 6
                details.append("✅ 包含代码示例 / Code examples included")
        
        self.scores.append(QualityScore(
            dimension="文档质量 / Documentation",
            score=min(score, max_score),
            max_score=max_score,
            details=details
        ))
        print(f"   得分 / Score: {score}/{max_score}")
        print()
    
    def _check_security(self):
        """安全性检查 / Check security"""
        print("🔒 检查安全性 / Checking security...")
        
        score = 15  # 默认满分，发现问题扣分
        details = []
        max_score = 15
        
        # 扫描所有Python文件 / Scan all Python files
        dangerous_patterns = [
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "硬编码API Key / Hardcoded API Key"),
            (r'token\s*=\s*["\'][^"\']+["\']', "硬编码Token / Hardcoded Token"),
            (r'password\s*=\s*["\'][^"\']+["\']', "硬编码密码 / Hardcoded Password"),
            (r'eval\s*\(', "使用eval() / Use of eval()"),
            (r'exec\s*\(', "使用exec() / Use of exec()"),
            (r'subprocess\.call.*shell\s*=\s*True', "shell=True安全风险 / shell=True security risk"),
        ]
        
        all_py_files = list(self.skill_path.rglob("*.py"))
        for py_file in all_py_files:
            content = py_file.read_text(encoding='utf-8')
            for pattern, desc in dangerous_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    score -= 5
                    details.append(f"❌ {py_file.name}: {desc}")
        
        if score == max_score:
            details.append("✅ 无安全风险 / No security risks found")
        
        score = max(0, score)
        
        self.scores.append(QualityScore(
            dimension="安全性 / Security",
            score=score,
            max_score=max_score,
            details=details
        ))
        print(f"   得分 / Score: {score}/{max_score}")
        print()
    
    def _check_standards(self):
        """规范符合度检查 / Check standards compliance"""
        print("📋 检查规范符合度 / Checking standards compliance...")
        
        score = 0
        details = []
        max_score = 10
        
        # 检查目录结构 / Check directory structure
        required_dirs = ["scripts"]
        optional_dirs = ["tests", "examples", "docs"]
        
        for d in required_dirs:
            if (self.skill_path / d).exists():
                score += 2
                details.append(f"✅ 目录 {d}/ 存在 / Directory exists")
        
        for d in optional_dirs:
            if (self.skill_path / d).exists():
                score += 1
                details.append(f"✅ 可选目录 {d}/ 存在 / Optional directory exists")
        
        # 检查必要文件 / Check required files
        required_files = ["SKILL.md", "requirements.txt", ".gitignore"]
        for f in required_files:
            if (self.skill_path / f).exists():
                score += 1
                details.append(f"✅ 文件 {f} 存在 / File exists")
        
        score = min(score, max_score)
        
        self.scores.append(QualityScore(
            dimension="规范符合度 / Standards",
            score=score,
            max_score=max_score,
            details=details
        ))
        print(f"   得分 / Score: {score}/{max_score}")
        print()
    
    def _check_community(self):
        """社区反馈检查 / Check community feedback"""
        print("👥 检查社区反馈 / Checking community feedback...")
        
        score = 0
        details = []
        max_score = 5
        
        # 这里需要GitHub API获取stars等数据
        # 简化处理，默认基础分
        score = 3
        details.append("✅ 基础社区分 / Base community score")
        details.append("📊 详细的社区数据需GitHub API / Detailed data requires GitHub API")
        
        self.scores.append(QualityScore(
            dimension="社区反馈 / Community",
            score=score,
            max_score=max_score,
            details=details
        ))
        print(f"   得分 / Score: {score}/{max_score}")
        print()
    
    def _generate_report(self) -> Dict:
        """生成质量报告 / Generate quality report"""
        print("=" * 60)
        print("📊 质量检查报告 / Quality Check Report")
        print("=" * 60)
        print()
        
        # 详细分数 / Detailed scores
        for s in self.scores:
            print(f"{s.dimension}:")
            print(f"  得分 / Score: {s.score}/{s.max_score}")
            for d in s.details:
                print(f"    {d}")
            print()
        
        # 总分 / Total score
        percentage = (self.total_score / self.max_total) * 100
        print("-" * 60)
        print(f"🎯 总分 / Total Score: {self.total_score}/{self.max_total} ({percentage:.1f}%)")
        print()
        
        # 等级评定 / Grade assessment
        grade = self._calculate_grade(percentage)
        print(f"🏆 质量等级 / Quality Grade: {grade}")
        print()
        
        # 建议 / Recommendations
        self._print_recommendations()
        
        return {
            "total_score": self.total_score,
            "max_score": self.max_total,
            "percentage": percentage,
            "grade": grade,
            "dimensions": [
                {
                    "dimension": s.dimension,
                    "score": s.score,
                    "max_score": s.max_score,
                    "percentage": (s.score / s.max_score) * 100 if s.max_score > 0 else 0,
                    "details": s.details
                }
                for s in self.scores
            ]
        }
    
    def _calculate_grade(self, percentage: float) -> str:
        """计算等级 / Calculate grade"""
        if percentage >= 95:
            return "AAA (钻石 Diamond) ⭐⭐⭐⭐⭐"
        elif percentage >= 80:
            return "AA (黄金 Gold) ⭐⭐⭐⭐"
        elif percentage >= 60:
            return "A (白银 Silver) ⭐⭐⭐"
        elif percentage >= 40:
            return "B (青铜 Bronze) ⭐⭐"
        else:
            return "C (待改进 Needs Improvement) ⭐"
    
    def _print_recommendations(self):
        """打印改进建议 / Print recommendations"""
        print("💡 改进建议 / Recommendations:")
        print()
        
        # 找出最低分项 / Find lowest scoring dimension
        lowest = min(self.scores, key=lambda s: (s.score / s.max_score) if s.max_score > 0 else 1)
        
        if "文档" in lowest.dimension or "Documentation" in lowest.dimension:
            print("  1. 完善文档 / Improve documentation:")
            print("     - 添加双语描述 / Add bilingual descriptions")
            print("     - 补充使用示例 / Add usage examples")
            print("     - 完善参数说明 / Complete parameter descriptions")
        
        if "代码" in lowest.dimension or "Code" in lowest.dimension:
            print("  2. 提升代码质量 / Improve code quality:")
            print("     - 添加测试文件 / Add test files")
            print("     - 完善错误处理 / Improve error handling")
            print("     - 添加代码注释 / Add code comments")
        
        if "安全" in lowest.dimension or "Security" in lowest.dimension:
            print("  3. 修复安全问题 / Fix security issues:")
            print("     - 移除硬编码密钥 / Remove hardcoded secrets")
            print("     - 使用环境变量 / Use environment variables")
        
        print()
        print("  详细标准请参考 / Detailed standards:")
        print("  docs/quality-assurance/QUALITY_STANDARDS.md")
        print()


def main():
    """主入口 / Main entry"""
    if len(sys.argv) < 2:
        print("Usage: python quality-check.py <skill-path>")
        print("Example: python quality-check.py skills/my-skill")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    
    if not os.path.exists(skill_path):
        print(f"❌ 路径不存在 / Path does not exist: {skill_path}")
        sys.exit(1)
    
    checker = QualityChecker(skill_path)
    report = checker.check_all()
    
    # 保存报告 / Save report
    report_path = Path(skill_path) / "quality-report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 报告已保存 / Report saved: {report_path}")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
