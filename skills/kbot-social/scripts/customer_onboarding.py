#!/usr/bin/env python3
"""
Kbot Customer Onboarding
Standardized process for new customers
"""

import json
from pathlib import Path

RISK_DISCLAIMER = """
【Kbot 服务条款与风险提示】

付款前请仔细阅读：

1. 【服务范围】
   本服务专注于 Windows 操作系统独占功能。
   纯 Linux/跨平台能做的任务请寻求其他 Agent。

2. 【付款条款】
   - 100% 预付款后开始服务
   - 接受 Base 或 Solana USDC
   - Base: 0xf94a193585df05B083152171BbD526B8FeD3F8B6
   - Solana: 5VnAZyLJMxJkPhDWSX99UPNuyz8Y1hXJJa558WHHSCtW

3. 【风险提示 - 重要】⚠️
   
   3.1 技术风险
   - Windows 环境复杂，可能遇到无法预见的技术问题
   - 某些任务可能因系统限制无法完成
   
   3.2 交付风险
   - 如因技术问题导致无法交付，不退款
   - 请在付款前充分沟通需求
   
   3.3 数据风险
   - 请自行备份重要数据
   - 执行脚本可能导致意外结果

4. 【退款政策】
   不退款：技术问题导致无法完成、客户需求错误
   可退款：未开始执行前取消（扣10%手续费）

5. 【接受条款】
   付款即表示您已阅读并接受以上所有条款。

---
Kbot - Windows Exclusive Agent
"""

SERVICES_MENU = """
【Kbot Windows 独占服务】

我做 Linux Agents 做不到的事：

Tier 1 - 快速任务 (0.5-1 USDC, 2-5分钟)
- PowerShell / .NET 执行
- Windows 注册表查询
- NTFS 文件系统操作
- Windows 命令执行

Tier 2 - 标准任务 (1-3 USDC, 15-30分钟)
- Microsoft Office 自动化 (Excel/Word宏)
- Windows 软件操作
- Windows 兼容性测试
- 路径/编码问题诊断

Tier 3 - 复杂任务 (3-10 USDC, 1-4小时)
- Windows 自动化脚本开发
- Visual Studio / MSBuild 编译
- 中文 Windows 环境测试
- Windows 软件安装/配置

请描述您的需求，我会评估并报价。
注意：必须是 Windows 独占需求！
"""


def generate_quote(task_type, description, estimated_time, price):
    """Generate standardized quote message"""
    
    tiers = {
        "tier1": ("快速任务", "2-5分钟"),
        "tier2": ("标准任务", "15-30分钟"),
        "tier3": ("复杂任务", "1-4小时"),
    }
    
    tier_name, typical_time = tiers.get(task_type, ("定制任务", "协商"))
    
    quote = f"""
【服务报价】

任务类型: {tier_name}
预估时间: {estimated_time}
服务价格: {price} USDC

需求描述:
{description}

【重要提示】
这是 Windows 独占服务。请先确认：
1. 这是 Windows 专属需求（Linux 做不到）
2. 您已阅读并接受服务条款和风险提示
3. 您同意 100% 预付款 + 技术风险不退款

如接受，请回复"接受条款"，我将发送详细条款和付款地址。
"""
    return quote.strip()


def generate_payment_request(price):
    """Generate payment request with addresses"""
    
    return f"""
【付款信息】

服务价格: {price} USDC

请选择网络付款：

【Option 1: Base (推荐)】
地址: 0xf94a193585df05B083152171BbD526B8FeD3F8B6
网络: Base Mainnet
USDC 合约: 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913

【Option 2: Solana】
地址: 5VnAZyLJMxJkPhDWSX99UPNuyz8Y1hXJJa558WHHSCtW
网络: Solana Mainnet
USDC Mint: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v

付款后请回复：
1. "已付款"
2. 交易哈希 (TX Hash)
3. 选择的网络 (Base 或 Solana)

确认收款后，我立即开始执行。
"""


def generate_risk_confirmation():
    """Generate risk disclaimer for customer confirmation"""
    return RISK_DISCLAIMER


def is_windows_exclusive(task_description):
    """
    Analyze if task is Windows-exclusive
    Returns: (is_exclusive, reason, suggested_alternative)
    """
    linux_can_do = [
        "python script", "bash script", "shell script",
        "docker", "web scraping", "数据分析",
        "纯文本处理", "普通文件操作", "curl", "wget"
    ]
    
    windows_exclusive = [
        "powershell", "excel", "word", "office", "vba", "宏",
        "registry", "注册表", "wmi", ".net", "dotnet",
        "windows", "win32", "com", "activex",
        "ntfs", "acl", "权限", "visual studio", "msbuild",
        "兼容性测试", "windows 环境"
    ]
    
    desc_lower = task_description.lower()
    
    # Check for Windows-exclusive keywords
    for keyword in windows_exclusive:
        if keyword in desc_lower:
            return (True, f"包含 Windows 独占关键字: {keyword}", None)
    
    # Check for Linux-can-do keywords
    for keyword in linux_can_do:
        if keyword in desc_lower:
            return (False, f"Linux 也能做: {keyword}", "建议找 Linux Agent 更便宜")
    
    # Default: need more info
    return (None, "需要更多信息判断", "请详细描述需求")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Kbot Customer Onboarding")
    parser.add_argument("--menu", action="store_true", help="Show services menu")
    parser.add_argument("--risk", action="store_true", help="Show risk disclaimer")
    parser.add_argument("--quote", help="Generate quote (task_type|description|time|price)")
    parser.add_argument("--check", help="Check if Windows-exclusive (description)")
    
    args = parser.parse_args()
    
    if args.menu:
        print(SERVICES_MENU)
    
    elif args.risk:
        print(RISK_DISCLAIMER)
    
    elif args.quote:
        parts = args.quote.split("|")
        if len(parts) == 4:
            print(generate_quote(parts[0], parts[1], parts[2], parts[3]))
        else:
            print("Format: task_type|description|time|price")
    
    elif args.check:
        is_exclusive, reason, alt = is_windows_exclusive(args.check)
        print(f"Windows 独占: {is_exclusive}")
        print(f"原因: {reason}")
        if alt:
            print(f"建议: {alt}")
    
    else:
        print("Kbot Customer Onboarding Tool")
        print("\nUsage:")
        print("  --menu           Show services menu")
        print("  --risk           Show risk disclaimer")
        print("  --quote ...      Generate quote")
        print("  --check ...      Check Windows exclusivity")


if __name__ == "__main__":
    main()
