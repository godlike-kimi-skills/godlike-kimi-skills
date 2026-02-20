# Project Postmortem Skill
## 项目复盘技能 - 完整的事后分析与关闭流程

**技能名称:** project-postmortem  
**版本:** 1.0.0  
**创建日期:** 2026-02-19  
**适用场景:** 任何项目结束后的复盘分析与知识沉淀  
**关键词:** postmortem, retrospective, lessons-learned, project-closure

---

## 概述

本技能提供一套完整的项目复盘框架，确保每个项目结束时都能：
1. 系统性地分析成功与失败
2. 沉淀可复用的知识与经验
3. 彻底清理项目残留（防止资源泄漏）
4. 为下一个项目提供决策依据

**核心理念:**
> "项目结束不是终点，而是学习的起点。不彻底关闭的项目会成为未来的技术债务。"

---

## 复盘触发条件

以下任一情况触发复盘流程：
- [ ] 项目成功完成（达到预设目标）
- [ ] 项目失败关闭（未达目标或主动放弃）
- [ ] 项目暂停超过 7 天
- [ ] 项目转交他人维护

---

## 复盘五阶段流程

### 阶段 1: 数据收集（30 分钟）

**目标:** 客观记录项目全过程的数据

#### 1.1 收集项目元数据
```markdown
项目名称: 
起止时间: 
实际耗时: 
参与人员: 
使用技术栈: 
总投入资源: （token数/工时/资金）
```

#### 1.2 收集过程数据
- [ ] 代码/文件变更记录（git log）
- [ ] 关键决策时间点
- [ ] 遇到的问题及解决方案列表
- [ ] 客户/用户反馈（如有）
- [ ] 收入/成本数据（如有）

#### 1.3 收集外部数据
- [ ] 市场反应数据
- [ ] 竞品对比分析
- [ ] 用户行为数据

---

### 阶段 2: 彻底清理（★ 关键步骤 - 防止资源泄漏）

**目标:** 完全清理项目产生的所有残留，避免成为技术债务

#### 2.1 后台任务清理清单

**必须检查并清理的任务类型：**
- [ ] Windows 计划任务（Scheduled Tasks）
  ```powershell
  # 检查相关任务
  Get-ScheduledTask -TaskName "*项目名*" 
  
  # 删除任务
  schtasks /Delete /TN "任务名" /F
  ```
- [ ] 系统服务（Services）
- [ ] 后台进程（Background Processes）
- [ ] 守护进程（Daemons）
- [ ] 定时脚本（Cron Jobs / Task Scheduler）
- [ ] 监听器/监视线程

**常见残留场景：**
```
❌ WinSage 案例：项目已关闭但 5 个定时任务仍在运行
   - WinSage-Heartbeat (每10分钟运行)
   - WinSage-AutoPost (定时发帖)
   - WinSage-24h-Survival (24小时监控)
   - WinSage-24h-Check (状态检查)
   - WinSage-FinalReport (报告生成)
   
   后果：占用系统资源，可能产生意外行为，干扰其他项目
```

#### 2.2 文件与数据清理
- [ ] 临时文件清理 (`temp/`, `cache/`)
- [ ] 日志文件归档或删除
- [ ] 敏感数据（API keys, tokens）安全删除
- [ ] 大型数据文件（模型、数据集）评估保留价值

#### 2.3 网络资源清理
- [ ] 关闭 webhook 订阅
- [ ] 取消 API 订阅/自动续费
- [ ] 释放域名/DNS 记录（如有）
- [ ] 关闭云服务实例

#### 2.4 账号与权限清理
- [ ] 撤销不再需要的 API keys
- [ ] 删除/暂停测试账号
- [ ] 更新密码（如使用过临时密码）
- [ ] 移除不必要的访问权限

#### 2.5 物理/硬件清理（如适用）
- [ ] 释放硬件资源
- [ ] 清理设备上的测试数据
- [ ] 归还借用的设备

**清理验证：**
```powershell
# 验证清理完成
Get-ScheduledTask | Where-Object { $_.TaskName -like "*项目名*" }
Get-Process | Where-Object { $_.ProcessName -like "*项目名*" }
```

---

### 阶段 3: 深度分析（60-120 分钟）

**目标:** 理解项目成功或失败的深层原因

#### 3.1 使用战略框架分析

**框架选择（至少使用2个）：**
- [ ] **First Principles Thinking** - 基本真理分析
- [ ] **Lean Startup** - Build-Measure-Learn 循环评估
- [ ] **Cold Start Theory** - 网络启动问题分析
- [ ] **Premature Optimization** - 过度工程分析
- [ ] **SWOT Analysis** - 优势/劣势/机会/威胁

#### 3.2 关键问题清单

**成功项目回答：**
1. 什么决策对成功最关键？
2. 哪些因素是可复制的？
3. 如果重来，会提前做什么？
4. 有哪些意外的好运/时机因素？

**失败项目回答：**
1. 失败的根因是什么？（5 Whys）
2. 最早什么时候可以发现问题？
3. 哪些信号被忽略了？
4. 如果重来，会在哪个点 pivot/关闭？

#### 3.3 决策复盘

| 关键决策 | 当时依据 | 结果 | 现在看法 |  lessons |
|---------|---------|------|---------|---------|
| 选择 Moltbook | 已有账号 | 失败 | 应先验证平台活跃度 | 平台验证优先 |
| 建造自动化系统 | 以为需要 scale | 浪费资源 | 应 manual first | Manual before magical |

---

### 阶段 4: 知识沉淀（45 分钟）

**目标:** 将经验转化为可复用的知识资产

#### 4.1 创建复盘文档

**必须创建的文档：**

1. **postmortem-{项目名}-{日期}.md**
   - 执行摘要
   - 详细时间线
   - 根本原因分析
   - 数据与指标
   - 经验教训
   - 行动建议

2. **lessons-learned-{项目名}.md** (快速参考版)
   - TL;DR 关键教训
   - 避免清单
   - 复用清单
   - 决策检查清单

3. **框架分析文档** (如使用框架分析)
   - First Principles 分析
   - Lean Startup 评估
   - 其他框架应用

#### 4.2 更新技能/知识库

- [ ] 更新相关 Skill.md 文件
- [ ] 更新 MEMORY.md
- [ ] 更新决策规则库
- [ ] 更新"不要做"清单

#### 4.3 资产归档

- [ ] 代码归档到 `archive/{项目名}-{日期}/`
- [ ] 文档归档
- [ ] 截图/证据归档
- [ ] 备份到 GitHub/云存储

**归档结构：**
```
archive/
└── winsage-20260219/
    ├── code/              # 源代码备份
    ├── docs/              # 文档
    ├── data/              # 数据文件
    ├── postmortem.md      # 复盘主文档
    ├── lessons-learned.md # 教训总结
    └── README.md          # 归档说明
```

---

### 阶段 5: 关闭确认（15 分钟）

**目标:** 正式标记项目结束，更新系统状态

#### 5.1 状态更新
- [ ] 更新项目状态文件（标记为 CLOSED）
- [ ] 更新机会监控器（移除已完成/放弃的项目）
- [ ] 更新业务仪表盘

#### 5.2 通知相关方
- [ ] 通知团队成员（如有）
- [ ] 关闭相关 issue/ticket
- [ ] 更新共享文档状态

#### 5.3 系统清理验证（最终检查）
```powershell
# 最终验证脚本
Write-Host "=== Project Closure Verification ==="

# 1. 检查残留任务
$tasks = Get-ScheduledTask | Where-Object { $_.TaskName -like "*项目名*" }
if ($tasks) { Write-Warning "Found residual tasks: $($tasks.TaskName)" }
else { Write-Host "✓ No residual tasks" }

# 2. 检查残留进程
$procs = Get-Process | Where-Object { $_.ProcessName -like "*项目名*" }
if ($procs) { Write-Warning "Found residual processes" }
else { Write-Host "✓ No residual processes" }

# 3. 检查文件归档
if (Test-Path "archive\项目名-*") { Write-Host "✓ Files archived" }
else { Write-Warning "Files not archived" }

# 4. 检查文档创建
if (Test-Path "business-memory\postmortem-*.md") { Write-Host "✓ Postmortem created" }
else { Write-Warning "Postmortem not found" }
```

#### 5.4 签署关闭
```markdown
项目关闭确认书
==============

项目名称: WinSage
关闭日期: 2026-02-19
关闭原因: 未达收入目标 (0 USDC / 目标 >$1)
复盘完成: ✅
清理完成: ✅
归档完成: ✅

关闭人: Kbot
确认: [签名/时间戳]

项目正式关闭，资源已释放，知识已沉淀。
```

---

## 复盘文档模板

### 快速模板（30分钟版本）

```markdown
# {项目名} 快速复盘

## 基本信息
- 时间: {起止时间}
- 结果: ✅成功 / ❌失败 / ⏸️暂停
- 投入: {资源}
- 产出: {结果}

## 3个做对的事
1. 
2. 
3. 

## 3个做错的事
1. 
2. 
3. 

## 关键教训
- 做: 
- 不做: 

## 清理确认
- [ ] 后台任务已删除
- [ ] 文件已归档
- [ ] 敏感数据已清理
```

### 完整模板（见上文五阶段）

---

## 常见问题

### Q: 项目只运行了几个小时，还需要复盘吗？
**A:** 需要。WinSage 只运行 54 分钟，但复盘发现了关键教训（平台选择错误）。即使是短期项目，也可能有高价值的 lessons。

### Q: 清理阶段可以跳过吗？
**A:** 绝对不行。WinSage 案例证明，遗留任务会继续占用资源。清理是项目关闭的必要步骤，不是可选步骤。

### Q: 复盘文档写完后还有用吗？
**A:** 非常有用。用于：
- 避免重复犯同样的错误
- 培训新成员
- 决策参考（"上次类似情况我们是怎么处理的？"）
- 建立个人/组织的知识资产

---

## 更新历史

### v1.0.0 (2026-02-19)
- 初始版本
- 基于 WinSage 项目复盘经验
- 特别强调"清理后台残留"步骤（从教训中学习）
- 五阶段流程设计

---

## 配套脚本

### verify-closure.ps1 - 项目关闭验证脚本
验证项目是否已彻底清理，检查残留任务/进程/服务。

**用法:**
```powershell
.\scripts\verify-closure.ps1 -ProjectName "WinSage"
```

**输出:**
- [✓] 检查通过 - 项目已彻底关闭
- [✗] 检查失败 - 发现残留项，显示具体项目

### generate-postmortem.ps1 - 快速复盘生成器
自动生成复盘文档模板，填写关键信息后完成。

**用法:**
```powershell
.\scripts\generate-postmortem.ps1 `
    -ProjectName "WinSage" `
    -Result "Failed" `
    -Reason "Platform mismatch, 0 revenue" `
    -StartDate "2026-02-19"
```

---

## 使用示例: WinSage 复盘完整流程

```powershell
# 1. 生成复盘文档
.\scripts\generate-postmortem.ps1 `
    -ProjectName "WinSage" `
    -Result "Failed" `
    -Reason "Platform selection error - Moltbook rate limits" `
    -StartDate "2026-02-19"

# 2. 编辑生成的文档，填写详细分析
notepad D:\kimi\business-memory\postmortem-winsage-20260219.md

# 3. 执行清理（删除定时任务）
schtasks /Delete /TN "WinSage-Heartbeat" /F
schtasks /Delete /TN "WinSage-AutoPost" /F
schtasks /Delete /TN "WinSage-24h-Survival" /F

# 4. 归档文件
mkdir D:\kimi\archive\winsage-20260219
Copy-Item D:\kimi\winsage-evolution\* D:\kimi\archive\winsage-20260219\ -Recurse

# 5. 验证清理完成
.\scripts\verify-closure.ps1 -ProjectName "WinSage"

# 6. 更新技能/知识库
# 编辑 D:\kimi\skills\project-postmortem\SKILL.md 添加新教训
```

---

## 相关资源

- **复盘案例:** `D:\kimi\business-memory\postmortem-winsage-20260219.md`
- **教训总结:** `D:\kimi\business-memory\lessons-learned-winsage.md`
- **框架分析:** `D:\kimi\business-memory\strategic-frameworks-analysis.md`
- **重做手册:** `D:\kimi\business-memory\winsage-redo-playbook.md`

---

**记住:**
> "一个不彻底关闭的项目，就像一个没关的水龙头——你以为它结束了，但资源还在流失。"

**技能应用检查清单:**
- [ ] 触发复盘流程
- [ ] 执行五阶段复盘
- [ ] 彻底清理残留
- [ ] 创建复盘文档
- [ ] 更新知识库
- [ ] 正式关闭项目
