# Chinese Lunar / 农历黄历

**🏆 金印级 (AAA)** - 农历转换、节气查询、黄历宜忌

> 二十四节气轮回转，甲子轮回又一年。阴阳合历，天人合一。

---

## 功能特性

### 📅 历法转换
- **公历转农历**：精确转换1900-2100年
- **农历转公历**：双向转换支持
- **生肖查询**：根据年份查生肖
- **干支纪年**：甲子、乙丑...六十甲子循环

### 🌾 二十四节气
- **节气查询**：精确到分钟的天文计算
- **节气列表**：全年二十四节气时间
- **节气解释**：每个节气的含义与习俗
- **节气诗词**：相关古诗词推荐

### 🏮 传统节日
- **节日查询**：春节、元宵、清明、端午、中秋、重阳等
- **节日倒计时**：距离下一个传统节日还有多久
- **节日习俗**：各地传统习俗介绍

### 📜 黄历宜忌
- **每日宜忌**：根据《协纪辨方书》推算
- **吉神凶煞**：建除十二神、二十八宿
- **冲煞方位**：每日冲煞生肖与方位
- **彭祖百忌**：每日禁忌

---

## 使用方法

### 日期查询
```bash
# 查询今天
kimi chinese-lunar

# 查询指定公历日期
kimi chinese-lunar 2024-02-10
kimi chinese-lunar --date 2024-02-10

# 查询指定农历日期
kimi chinese-lunar --lunar 2024-01-01
```

### 节气查询
```bash
# 查询今年所有节气
kimi chinese-lunar --solar-terms

# 查询指定年份节气
kimi chinese-lunar --solar-terms 2024

# 查询当前节气
kimi chinese-lunar --current-term
```

### 节日查询
```bash
# 查询今年所有节日
kimi chinese-lunar --festivals

# 下一个节日
kimi chinese-lunar --next-festival

# 节日倒计时
kimi chinese-lunar --countdown 春节
```

### 黄历宜忌
```bash
# 查询今日黄历
kimi chinese-lunar --almanac

# 查询指定日期黄历
kimi chinese-lunar --almanac 2024-02-10
```

---

## 输出示例

```
📅 2024年2月10日 星期六

农历：甲辰年 丙寅月 甲辰日
     正月初一

生肖：龙 🐉
干支：甲子年（纳音：海中金）

🌾 节气：立春 (已过) → 雨水 (还有8天)

🏮 节日：春节（农历新年）
     习俗：贴春联、放鞭炮、拜年、吃饺子

📜 黄历宜忌：
   ✅ 宜：祭祀、祈福、开光、出行
   ❌ 忌：嫁娶、安葬、动土、破土

   吉神：天德、月德、天恩
   凶煞：月破、大耗
   
   冲煞：冲狗煞南
   彭祖百忌：甲不开仓财物耗散
```

---

## 技术说明

### 历法算法
- 基于《天文算法》实现
- 支持1900-2100年精确转换
- 考虑闰月、大小月

### 节气计算
- 太阳黄经计算
- 精确到分钟级别
- 支持节气交节时刻

### 黄历推算
- 参考《钦定协纪辨方书》
- 建除十二神算法
- 二十八宿值日

---

## 参考项目

- **cnlunar**: https://github.com/OPN48/cnlunar
- **lunar-javascript**: https://github.com/6tail/lunar-javascript
- **中国农历算法**: 基于紫金山天文台数据

---

## 版本信息

- **Version**: 1.0.0
- **Author**: Godlike Kimi Skills
- **License**: MIT
- **Tags**: chinese, lunar, calendar, solar-term, almanac
