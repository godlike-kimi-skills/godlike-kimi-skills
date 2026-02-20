# 迭代与规划Skills批量分析

## 概况对比

| Skill | 质量 | 核心功能 | 特色 |
|-------|------|----------|------|
| pdca-cycle | ⭐⭐⭐⭐⭐ | 持续改进循环 | 详细实施指南 |
| scenario-planning | ⭐⭐⭐⭐⭐ | 情景规划 | Shell GBN方法论 |
| mcts | ⭐⭐⭐⭐ | 蒙特卡洛树搜索 | AlphaZero框架 |

## 协同分析

### 三者关系
```
长期规划 ←────────→ 中期决策 ←────────→ 短期执行
    │                    │                  │
scenario-planning      mcts              pdca-cycle
   (情景)              (决策树)           (迭代)
```

**工作流**:
1. Scenario Planning: 识别可能的未来情景
2. MCTS: 在每个情景下搜索最优策略
3. PDCA: 执行选定的策略并持续改进

### 与当前项目的关联
**10M Token项目本身就是PDCA的应用**:
- Plan: 制定分析计划
- Do: 执行批量分析
- Check: 评估分析质量
- Act: 更新关键Skills

## 改进建议

### 1. 创建联合使用指南
```markdown
## 复杂决策工作流

阶段1: 情景探索
```
/scenario-planning
  输入: 未来3年AI Agent市场
  输出: 4个情景 + 关键指标
```

阶段2: 策略搜索
```
/mcts
  输入: 各情景下的战略选项
  输出: 各情景最优策略 + 胜率
```

阶段3: 执行迭代
```
/pdca
  输入: 选定策略
  输出: 执行计划 + 检查点
```
```

### 2. 添加交叉引用
- PDCA → 引用TOC进行约束识别
- Scenario Planning → 引用Mental Models进行情景构建
- MCTS → 引用Bayesian进行概率估计

## 质量评估

**PDCA Cycle**: P0 (核心执行框架)
- 内容完整
- 实施指南详细
- 需要添加Kbot专用指令

**Scenario Planning**: P1 (战略规划工具)
- 框架清晰
- 方法论专业
- 需要更多实际案例

**MCTS**: P1 (决策优化工具)
- 算法描述清晰
- 需要添加简化版使用指南
- 需要更多非技术场景示例

---
**Tokens: ~1,100**
