# 嫦娥月兔风格设计规范 / Chang'e Jade Rabbit Style Guide

> 🌙 **设计主题**: 月之暗面 × 嫦娥玉兔 × 中国美学  
> 🎯 **核心概念**: 月夜、桂树、玉兔、祥云、水墨  
> **适配品牌**: Kimi (月之暗面) 开源社区

---

## 一、设计理念 / Design Philosophy

### 1.1 文化融合

```
月之暗面 (Kimi品牌)
    ↓
月亮意象 → 嫦娥奔月 → 玉兔捣药 → 桂树飘香
    ↓
中国色彩 + 水墨意境 + 传统纹样
```

### 1.2 视觉关键词

| 中文 | English | 意象 |
|------|---------|------|
| 月白 | Moon White | 皎洁、纯净 |
| 青黛 | Indigo | 夜空、深邃 |
| 朱砂 | Cinnabar | 活力、醒目 |
| 金色 | Gold | 尊贵、品质 |
| 水墨 | Ink Wash | 雅致、东方 |

---

## 二、色彩系统 / Color System

### 2.1 主色调

```css
:root {
  /* 月白 - 主背景 */
  --moon-white: #F5F5F0;
  --moon-light: #FAFAF7;
  --moon-dark: #E8E8E0;
  
  /* 青黛 - 主色 */
  --indigo-primary: #2C3E50;
  --indigo-light: #34495E;
  --indigo-dark: #1A252F;
  
  /* 朱砂 - 强调 */
  --cinnabar: #C9372C;
  --cinnabar-light: #E74C3C;
  --cinnabar-dark: #A93226;
  
  /* 金色 - 点缀 */
  --gold: #D4AF37;
  --gold-light: #F4D03F;
  --gold-dark: #B7950B;
  
  /* 墨色 - 文字 */
  --ink-black: #1A1A1A;
  --ink-gray: #4A4A4A;
  --ink-light: #7A7A7A;
}
```

### 2.2 色彩搭配方案

**方案一: 月夜清风 (推荐)**
- 背景: 月白 (#F5F5F0)
- 主色: 青黛 (#2C3E50)
- 强调: 朱砂 (#C9372C)
- 点缀: 金色 (#D4AF37)

---

## 三、图形元素 / Graphic Elements

### 3.1 Logo概念

**主Logo: 玉兔捣药**
- 兔子剪影 + 月亮背景 + 桂树点缀
- 单线条设计，可缩放

**简化Logo: 月兔剪影**
```
    🌙
   /🐇\
```

### 3.2 装饰纹样

**祥云纹** - 用于分隔线、背景装饰
**桂树叶** - 用于列表标记
**玉兔足迹** 🐾 - 用于步骤指示

### 3.3 图标映射

| 功能 | 中国元素 | Emoji |
|------|----------|-------|
| Skills | 灯笼 | 🏮 |
| Install | 卷轴 | 📜 |
| Quality | 玉玺 | 🏆 |
| Community | 竹林 | 🎋 |
| GitHub | 月亮 | 🌙 |

---

## 四、README 重构方案

### 4.1 新Header设计

```markdown
<p align="center">
  <img src="assets/logo-moon-rabbit.svg" width="100" alt="月兔Logo" />
</p>

<h1 align="center" style="color: #2C3E50;">
  月神技能 <span style="color: #C9372C;">·</span> Godlike Kimi Skills
</h1>

<p align="center">
  <em>🏮 嫦娥应悔偷灵药，碧海青天夜夜心 🏮</em>
</p>
```

### 4.2 徽章重新设计 (中国色)

```markdown
<p align="center">
  <img src="https://img.shields.io/badge/🌙_Skills-200+-2C3E50?style=flat-square&labelColor=F5F5F0" />
  <img src="https://img.shields.io/badge/🏮_Categories-15+-C9372C?style=flat-square&labelColor=F5F5F0" />
  <img src="https://img.shields.io/badge/🐇_中文支持-100%25-D4AF37?style=flat-square&labelColor=F5F5F0" />
  <img src="https://img.shields.io/badge/✨_AI_运营-Wang_Johnny-9370DB?style=flat-square&labelColor=F5F5F0" />
</p>
```

### 4.3 分类命名 (诗意化)

| 原分类 | 新命名 | 意象 |
|--------|--------|------|
| 金融投资 | 🌙 月华金融 | 月光洒金 |
| 思维框架 | 🐇 玉兔思维 | 玉兔聪慧 |
| 开发工具 | 🏮 桂树开发 | 月桂飘香 |
| 系统管理 | ✨ 繁星系统 | 星辰点点 |
| 自动化 | 🎋 竹林自动化 | 竹海听风 |

---

## 五、品质徽章 (中国等级制)

| 等级 | 徽章 | 名称 | 说明 |
|------|------|------|------|
| AAA | 🏆 | 金印 | 大师级 |
| AA | 🥈 | 银牌 | 优秀级 |
| A | 🥉 | 铜牌 | 良好级 |
| B | 📜 | 玉简 | 合格级 |
| C | 🏷️ | 木牌 | 入门级 |

---

## 六、实施清单

### Phase 1: 立即可做
- [ ] 更新README徽章颜色
- [ ] 修改分类标题 (诗意化)
- [ ] 添加中国元素Emoji

### Phase 2: 需要设计
- [ ] Logo SVG设计
- [ ] 分隔线图案
- [ ] 背景纹理

### Phase 3: 高级优化
- [ ] GitHub Pages主题
- [ ] 动画效果
- [ ] 深色模式适配

---

**设计宣言:**

> 月之暗面，玉兔呈祥。古韵新风，技传四方。
