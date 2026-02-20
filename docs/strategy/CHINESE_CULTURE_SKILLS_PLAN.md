# 中国艺术文化类 Skills 开发计划

> 🌙 月神技能 - 文化艺术系列

---

## 10个精选项目

### 1. 🏮 九歌诗词 (jiuge-poetry)
**参考**: 清华九歌诗词生成系统

**功能**:
- 自动生成古诗词（五言/七言绝句、律诗）
- 藏头诗生成
- 词牌名填词（沁园春、水调歌头等）
- 集句诗生成

**使用场景**:
```bash
kimi skill run jiuge-poetry --type 五言绝句 --theme 月亮
# 生成: 明月几时有，把酒问青天...

kimi skill run jiuge-poetry --type 藏头诗 --text 月神技能
# 生成: 【月】下独酌酒，【神】游天地间...
```

**技术栈**: NLP模型、古诗语料库

---

### 2. 🖌️ 中国书法 (chinese-calligraphy)
**参考**: zi2zi-chain书法字体生成

**功能**:
- 印刷体转书法字体（楷书、行书、草书）
- 个性化手写字体生成
- 书法风格迁移
- 字体配对推荐

**使用场景**:
```bash
kimi skill run chinese-calligraphy --text "月神技能" --style 行书
# 输出书法风格的ASCII艺术或SVG

kimi skill run chinese-calligraphy --analyze 王羲之兰亭序
# 分析书法风格特点
```

---

### 3. 🎨 传统色卡 (chinese-colors)
**参考**: chinese-colors项目、故宫色彩美学

**功能**:
- 查询中国传统色（560+种）
- 颜色名称→RGB/HEX转换
- 配色方案推荐（五色观、五行色）
- 诗词中的颜色提取

**使用场景**:
```bash
kimi skill run chinese-colors --name 月白
# 输出: #F5F5F0 - "皎洁如月光"

kimi skill run chinese-colors --scheme 五行
# 输出: 木(青)、火(赤)、土(黄)、金(白)、水(黑)

kimi skill run chinese-colors --poem "日照香炉生紫烟"
# 提取: 紫烟 #B598A3
```

---

### 4. 📅 农历黄历 (chinese-lunar)
**参考**: cnlunar项目

**功能**:
- 公历农历转换
- 二十四节气查询
- 黄历宜忌（建除十二神、值神、凶煞）
- 生肖星座
- 节假日判断

**使用场景**:
```bash
kimi skill run chinese-lunar --date 2026-02-20
# 输出: 农历正月初三，立春后，宜开市、纳财

kimi skill run chinese-lunar --solar-term
# 输出: 当前节气及下一个节气时间

kimi skill run chinese-lunar --almanac --date 2026-05-01
# 输出: 五一劳动节，农历三月十五，宜...
```

---

### 5. ☯️ 易经占卜 (iching-divination)
**参考**: iching开源项目

**功能**:
- 蓍草法占卜（大衍之数）
- 六十四卦查询
- 卦象解析（本卦、变卦、爻辞）
- 梅花易数起卦

**使用场景**:
```bash
kimi skill run iching-divination --question "是否应该接受这个offer"
# 输出: 占得【乾卦】九五，飞龙在天...

kimi skill run iching-divination --hexagram 乾
# 输出: 乾卦详解、六爻解释、应用建议
```

**文化说明**: 仅供娱乐，AI解卦，不可迷信

---

### 6. 🏥 中医五行 (tcm-five-elements)
**参考**: 中医理论微分方程模型

**功能**:
- 五行属性分析（金木水火土）
- 体质辨识
- 五行生克关系计算
- 食疗/穴位推荐
- 五运六气推算

**使用场景**:
```bash
kimi skill run tcm-five-elements --birth 1990-05-20
# 分析: 庚午年，五行属金，体质偏热...

kimi skill run tcm-five-elements --element 木 --status 弱
# 建议: 补木食物(青菜)、养肝穴位(太冲)

kimi skill run tcm-five-elements --interaction 木 土
# 输出: 木克土，平衡建议...
```

---

### 7. 🌸 花语诗词 (flower-poetry)
**参考**: 中国花文化、诗词数据库

**功能**:
- 花卉诗词查询（梅、兰、竹、菊等）
- 花语解读
- 根据花卉生成诗词
- 十二花神查询

**使用场景**:
```bash
kimi skill run flower-poetry --flower 梅花
# 输出: 墙角数枝梅，凌寒独自开...

kimi skill run flower-poetry --month 正月
# 输出: 正月花神 - 梅花

kimi skill run flower-poetry --generate --theme 荷花
# 生成一首关于荷花的原创诗词
```

---

### 8. 🎭 成语典故 (idiom-stories)
**参考**: 成语词典、典故数据库

**功能**:
- 成语查询（出处、释义、近反义词）
- 成语接龙
- 典故故事讲解
- 成语分类（寓言、历史、神话）
- 根据场景推荐成语

**使用场景**:
```bash
kimi skill run idiom-stories --idiom 嫦娥奔月
# 输出: 出自《淮南子》，讲述嫦娥偷吃仙药...

kimi skill run idiom-stories --category 月亮
# 输出: 花好月圆、月明星稀...

kimi skill run idiom-stories --context "项目终于成功了"
# 推荐: 大功告成、功成名就...
```

---

### 9. 🗺️ 古地图志 (ancient-geography)
**参考**: 中国历史地理信息系统

**功能**:
- 古今地名对照
- 诗词中的地理位置
- 丝绸之路/茶马古道路线
- 古代行政区划查询
- 游历路线规划（李白/苏轼足迹）

**使用场景**:
```bash
kimi skill run ancient-geography --name 长安
# 输出: 今陕西西安，唐朝都城...

kimi skill run ancient-geography --poet 李白 --route
# 输出: 李白生平游历路线图

kimi skill run ancient-geography --query "烟花三月下扬州"
# 输出: 扬州今属江苏，唐代繁华都市...
```

---

### 10. 🎵 古谱音律 (ancient-music)
**参考**: 古琴减字谱、律吕算法

**功能**:
- 五声音阶（宫商角徵羽）转换
- 古琴减字谱解析
- 十二律吕计算
- 古曲推荐（高山流水、广陵散）
- 音乐治疗（五音疗疾）

**使用场景**:
```bash
kimi skill run ancient-music --scale 宫调
# 输出: 宫调式音阶，适合庄重场合...

kimi skill run ancient-music --therapy --mood 焦虑
# 推荐: 角调式音乐，养肝疏肝...

kimi skill run ancient-music --notation "@@【减字谱】"
# 解析减字谱并转换为现代记谱
```

---

## 开发优先级

| 优先级 | Skill | 原因 |
|--------|-------|------|
| **P0** | 传统色卡 | 需求普遍，实现简单 |
| **P0** | 农历黄历 | 实用性强，技术成熟 |
| **P1** | 九歌诗词 | 文化底蕴深，有参考项目 |
| **P1** | 成语典故 | 数据丰富，用户需求大 |
| **P2** | 易经占卜 | 趣味性强，有技术参考 |
| **P2** | 中医五行 | 健康相关，关注度高 |
| **P3** | 中国书法 | 视觉效果好，有特色 |
| **P3** | 花语诗词 | 文艺属性，传播性好 |
| **P4** | 古地图志 | 教育价值高 |
| **P4** | 古谱音律 | 专业性强，受众较小 |

---

## 数据资源

### 开源数据集
- **诗词**: 全唐诗、全宋词数据库
- **颜色**: 中国传统色560种
- **农历**: 农历算法库（1900-2100）
- **易经**: 六十四卦文本
- **成语**: 成语词典（5万+）

### API资源
- 百度AI诗词生成API
- 汉典API（字词查询）
- 中国天气网节气数据

---

## 技术实现建议

### 通用技术栈
```python
# 核心依赖
- pydantic  # 数据验证
- click     # CLI接口
- rich      # 终端美化
- requests  # API调用

# 可选依赖
- jieba     # 中文分词
- cnlunar   # 农历计算
```

### 目录结构
```
<skill-name>/
├── SKILL.md           # 技能描述
├── main.py            # 主入口
├── data/              # 静态数据
│   ├── colors.json    # 颜色数据
│   ├── poems.json     # 诗词数据
│   └── idioms.json    # 成语数据
├── utils/             # 工具函数
│   ├── __init__.py
│   └── converter.py   # 转换工具
└── tests/
    └── test_basic.py
```

---

## 文化注意事项

1. **易经占卜** - 明确标注"仅供娱乐，AI解卦，不可迷信"
2. **中医五行** - 强调"非医疗建议，身体不适请就医"
3. **传统色** - 引用《中国传统色》等权威资料，注明出处
4. **诗词** - 标注作者和朝代，尊重版权

---

**让AI传承中华文化，从月神技能开始。** 🏮
