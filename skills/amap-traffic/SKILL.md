---
name: amap-traffic
description: Amap (Gaode Maps) traffic and navigation. Use when checking traffic conditions, planning routes, or getting navigation info in China.
---

# Amap Traffic

高德地图实时路况与路线规划。

## Features

- 实时路况查询
- 路线规划
- 导航建议
- 交通态势

## Usage

```bash
# 查询路况
python D:/kimi/skills/amap-traffic/scripts/amap.py traffic "北京市"

# 路线规划
python D:/kimi/skills/amap-traffic/scripts/amap.py route "北京" "上海" --mode driving

# 最优路线
python D:/kimi/skills/amap-traffic/scripts/amap.py route "起点" "终点" --optimal
```

## API Key

需要高德地图 API Key。
