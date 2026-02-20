# Price Monitor

**加密货币价格监控与告警系统** - 多源数据、实时追踪、智能告警

支持Binance、CoinGecko等数据源，提供价格追踪、阈值告警、趋势分析功能。

---

## 核心功能

### 📊 价格追踪

| 功能 | 说明 | 数据源 |
|------|------|--------|
| **实时价格** | 当前市场价格 | Binance, CoinGecko |
| **历史数据** | OHLCV数据 | Binance API |
| **多币种** | 支持主流加密货币 | 500+交易对 |
| **汇率转换** | USD/CNY/EUR | 实时汇率 |

### 🔔 告警规则

```yaml
告警类型:
  - 价格突破: price > $X 或 price < $Y
  - 涨跌幅: change_24h > ±N%
  - 波动率: volatility > threshold
  - 成交量异常: volume_spike > Nx average

告警级别:
  - critical: 价格剧烈波动(>10%)
  - warning: 达到预设阈值
  - info: 一般价格变动
```

---

## 使用方法

### CLI 命令

```bash
# 查看当前价格
price-monitor check --token BTC --currency USD

# 添加价格监控
price-monitor watch \
  --token SOL \
  --above 150 \
  --below 100 \
  --notify slack

# 设置涨跌幅告警
price-monitor alert \
  --token ETH \
  --change-pct 5 \
  --direction both

# 批量监控
price-monitor batch \
  --tokens BTC,ETH,SOL,USDC \
  --interval 60

# 查看历史
price-monitor history --token BTC --days 7
```

### 配置文件

```yaml
# price-monitor-config.yaml
monitors:
  - token: BTC
    currency: USD
    alerts:
      - type: price_above
        value: 70000
        severity: info
      - type: change_pct
        value: 5
        window: 1h
        severity: warning
    
  - token: SOL
    currency: USD
    alerts:
      - type: price_below
        value: 100
        severity: critical

data_source:
  primary: binance
  fallback: coingecko
  
notification:
  channels:
    - type: slack
      webhook: "${SLACK_WEBHOOK_URL}"
    - type: email
      to: "${ALERT_EMAIL}"
```

---

## 与其他Skills集成

### Alert Manager 集成
```bash
# 告警自动路由到alert-manager
price-monitor alert \
  --token BTC \
  --above 70000 \
  --route-to alert-manager \
  --severity warning
```

### Workflow Builder 集成
```yaml
workflow:
  name: "daily-crypto-report"
  trigger:
    cron: "0 9 * * *"
  steps:
    - name: "get-prices"
      run: "price-monitor check --tokens BTC,ETH,SOL"
      
    - name: "analyze-trend"
      run: "price-monitor analyze --token BTC --days 7"
      
    - name: "send-report"
      run: "alert-manager notify --channel email --template daily_report"
```

### SQLite Manager 集成
```bash
# 价格数据自动存储
price-monitor watch \
  --token BTC \
  --store sqlite \
  --db-path "./data/prices.db"
```

---

## 数据源说明

| 数据源 | 延迟 | 限制 | 适用场景 |
|--------|------|------|----------|
| Binance | <1s | 1200 req/min | 高频监控 |
| CoinGecko | ~30s | 10-50 req/min | 低频/备用 |
| 本地缓存 | 0ms | 无限制 | 离线查询 |

---

## 版本信息

- **Version**: 2.0.0
- **Author**: KbotGenesis
- **更新**: 完全重写，添加告警系统和多源支持
