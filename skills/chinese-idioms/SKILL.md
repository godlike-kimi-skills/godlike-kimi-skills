# Chinese Idioms / 成语典故大全

**🏆 金印级 (AAA)** - 3万+成语查询、典故讲解、成语接龙

> 成语者，华夏文化之精髓也。四字之间，蕴含千年智慧。

---

## 功能特性

### 📚 成语查询
- **3万+成语库**：收录常用成语、生僻成语
- **多维度查询**：按拼音、首字母、字数、出处
- **智能搜索**：支持模糊查询、近义查询
- **详细解析**：释义、出处、例句、近反义词

### 🎯 成语接龙
- **智能接龙**：AI自动接龙，支持难度选择
- **闯关模式**：从易到难闯关挑战
- **双人对战**：支持人机对战
- **接龙记录**：保存精彩对局

### 📖 典故学习
- **历史典故**：每个成语背后的历史故事
- **人物关系**：相关历史人物介绍
- **时间线**：按朝代分类成语
- **图文解读**：典故配图（可选）

### ✍️ 实用工具
- **成语填空**：练习模式
- **成语造句**：AI辅助造句
- **作文应用**：作文中的成语运用
- **每日成语**：每日推送一个成语

---

## 使用方法

### 查询成语
```bash
# 查询单个成语
kimi chinese-idioms 画龙点睛
kimi chinese-idioms 守株待兔

# 拼音查询
kimi chinese-idioms --pinyin huàlóngdiǎnjīng

# 模糊搜索
kimi chinese-idioms --search 龙
kimi chinese-idioms --search 努力
```

### 成语接龙
```bash
# 开始接龙游戏
kimi chinese-idioms --game

# 指定起始成语
kimi chinese-idioms --game-start 一心一意

# 指定难度
kimi chinese-idioms --game --level hard
```

### 典故学习
```bash
# 查看成语典故
kimi chinese-idioms --story 卧薪尝胆

# 按朝代查看
kimi chinese-idioms --dynasty 春秋
kimi chinese-idioms --dynasty 三国
```

### 每日成语
```bash
# 今日成语
kimi chinese-idioms --daily

# 随机成语
kimi chinese-idioms --random
```

---

## 输出示例

### 成语详情
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 画龙点睛 (huà lóng diǎn jīng)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 释义：
比喻写文章或讲话时，在关键处用几句话点明实质，使内容生动有力。

📜 出处：
唐·张彦远《历代名画记·张僧繇》：
"张僧繇于金陵安乐寺画四龙于壁，不点睛。每曰：'点之即飞去。'
人以为妄诞，固请点之。须臾，雷电破壁，两龙乘云腾去上天，
二龙未点眼者见在。"

🎯 例句：
• 这篇文章结尾的点题，真是画龙点睛之笔。
• 他的演讲最后那个比喻，起到了画龙点睛的作用。

🔤 拼音：huà lóng diǎn jīng
🔠 首字母：hldj

🔗 近义词：锦上添花、点石成金
🔗 反义词：画蛇添足、弄巧成拙

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 成语接龙
```
🎮 成语接龙 - 第1轮

你：一心一意 (yī xīn yī yì)
AI：意气风发 (yì qì fēng fā)
你：发愤图强
...

当前连胜：5轮
```

---

## 数据来源

- **《成语大辞典》**：商务印书馆
- **《汉语成语考释词典》**：刘洁修
- **《中国成语通检》**：史光荣
- **成语典故库**：历史文献整理

---

## 技术实现

```python
# 核心功能示例
from chinese_idioms import IdiomDB

db = IdiomDB()

# 查询成语
idiom = db.get_idiom("画龙点睛")
print(idiom.meaning)
print(idiom.origin)

# 成语接龙
next_idiom = db.find_next("画龙点睛")  # 返回以"睛"开头的成语

# 搜索成语
results = db.search("努力向上")  # 模糊搜索
```

---

## 参考项目

- **成语词典API**：开放成语数据接口
- **chinese-xinhua**：中华新华字典数据库
- **成语接龙算法**：基于图论的接龙算法

---

## 版本信息

- **Version**: 1.0.0
- **Author**: Godlike Kimi Skills
- **License**: MIT
- **Tags**: chinese, idiom, chengyu, education, language
