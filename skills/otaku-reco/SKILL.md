---
name: otaku-reco
description: Anime recommendation system using AniList data. Use when getting anime recommendations, discovering new shows, or finding similar anime.
---

# Otaku Recommendations

二次元番剧智能推荐。

## Features

- 基于AniList数据推荐
- 个性化推荐
- 相似番剧查找
- 无需数据库

## Usage

```bash
# 获取推荐
python D:/kimi/skills/otaku-reco/scripts/anime.py recommend

# 基于喜好推荐
python D:/kimi/skills/otaku-reco/scripts/anime.py recommend --genre action --genre sci-fi

# 相似番剧
python D:/kimi/skills/otaku-reco/scripts/anime.py similar "进击的巨人"
```
