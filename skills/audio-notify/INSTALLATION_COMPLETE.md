# Kbot Audio Notify Skill - Installation Complete

## ✅ 安装状态

### 步骤 1: 前置条件检查 ✓
- PowerShell 版本: 5.1 (满足 ≥5.1 要求)
- 执行策略: Bypass (已允许脚本运行)
- 音频设备: 已检测到 3 个可用设备
- 音量控制: API 可访问
- 音频输出: 正常工作

### 步骤 2: 核心文件已部署 ✓

```
D:\kimi\skills\audio-notify\
├── SKILL.md                          # 技能说明文档
├── scripts/
│   ├── config.ps1                    # 配置文件
│   ├── success-sound.ps1             # 成功提示音脚本
│   ├── error-sound.ps1               # 错误告警音脚本
│   ├── install-check.ps1             # 安装检查脚本
│   ├── test-all.ps1                  # 测试脚本
│   └── uninstall.ps1                 # 卸载脚本
└── sounds/                           # 自定义音频文件目录
```

### 步骤 3: 技能已创建 ✓

| 组件 | 说明 |
|------|------|
| 成功提示音 | 高频 1000Hz，愉悦音效 |
| 错误告警音 | 低频 800Hz，3次重复，紧急感 |
| 音量控制 | 自动设置为系统最大音量 (100%) |
| 自定义音频 | 支持 WAV/MP3 格式替换 |

## 🎯 使用方法

### 1. 手动测试音频

```powershell
# 测试成功提示音
powershell -ExecutionPolicy Bypass -File D:\kimi\skills\audio-notify\scripts\success-sound.ps1

# 测试错误告警音
powershell -ExecutionPolicy Bypass -File D:\kimi\skills\audio-notify\scripts\error-sound.ps1
```

### 2. 在 Kbot 任务中使用

在任意 Kbot 脚本中添加以下代码：

```powershell
# 任务成功时播放
& "D:\kimi\skills\audio-notify\scripts\success-sound.ps1"

# 任务失败时播放
& "D:\kimi\skills\audio-notify\scripts\error-sound.ps1"
```

### 3. 集成到现有 Kbot 脚本

修改 `D:\kimi\scripts\wake-up.ps1`：

在文件末尾添加（在 `Good Morning` 之前）：
```powershell
# 播放成功提示音
& "D:\kimi\skills\audio-notify\scripts\success-sound.ps1"
```

在 catch 块中添加（在错误日志之后）：
```powershell
# 播放错误告警音
& "D:\kimi\skills\audio-notify\scripts\error-sound.ps1"
```

## ⚙️ 自定义配置

编辑 `D:\kimi\skills\audio-notify\scripts\config.ps1`：

```powershell
# 音量设置 (0-100)
$global:AudioNotify_Volume = 100

# 成功声音频率/时长
$global:AudioNotify_SuccessFrequency = 1000  # Hz
$global:AudioNotify_SuccessDuration = 300     # ms

# 错误声音频率/时长/重复次数
$global:AudioNotify_ErrorFrequency = 800
$global:AudioNotify_ErrorDuration = 500
$global:AudioNotify_ErrorRepeat = 3

# 自定义音频文件路径
$global:AudioNotify_CustomSuccessPath = "D:\kimi\skills\audio-notify\sounds\my-success.wav"
$global:AudioNotify_CustomErrorPath = "D:\kimi\skills\audio-notify\sounds\my-error.wav"
```

## 🧪 测试指令

```powershell
# 完整安装检查
powershell -ExecutionPolicy Bypass -File D:\kimi\skills\audio-notify\scripts\install-check.ps1

# 运行测试套件
powershell -ExecutionPolicy Bypass -File D:\kimi\skills\audio-notify\scripts\test-all.ps1
```

## 🔊 音频特性

| 场景 | 声音特征 | 穿透力 |
|------|----------|--------|
| 任务成功 | 高频 1000Hz，单次短促 | ★★★☆☆ |
| 任务错误 | 低频 800Hz，3次重复 | ★★★★★ |
| 系统音量 | 自动调至 100% | ★★★★★ |

**确保在睡觉/听音乐时也能听到的设计**：
- 自动将系统音量调至最大
- 错误音使用更低频率（穿透力更强）
- 错误音重复 3 次，确保被注意到

## 🗑️ 卸载

```powershell
powershell -ExecutionPolicy Bypass -File D:\kimi\skills\audio-notify\scripts\uninstall.ps1
```

## 📝 注意事项

1. **执行策略**: 如果提示无法运行脚本，执行：
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **音频权限**: 确保扬声器未静音，Windows 音量混合器中没有限制 PowerShell 的音量

3. **自定义音频**: 将 WAV/MP3 文件放入 `sounds/` 目录，并在 `config.ps1` 中配置路径

## ✅ 验证完成

```
安装状态: ✓ 完成
测试状态: ✓ 音频输出正常
钩子状态: 需手动集成到 Kbot 脚本（见上文使用方法）
```

**Kbot Audio Notify 技能已就绪！**
