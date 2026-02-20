---
name: audio-notify
version: 1.0
description: High-volume audio notifications for Kbot task completion and errors. Ensures alerts are heard even when sleeping or listening to music.
---

# Audio Notify Skill

High-volume audio notification system for Kbot tasks on Windows.

## Features

- **Native Windows API**: Uses Windows Media API and Console.Beep for maximum compatibility
- **High Volume**: Automatically sets system volume to maximum before playing alerts
- **Dual Mode**: Separate sounds for success and error conditions
- **Customizable**: Support custom WAV/MP3 audio files
- **Kbot Integration**: Automatic hooks on task completion/error

## Installation

Run installation check:
```powershell
powershell -ExecutionPolicy Bypass -File D:/kimi/skills/audio-notify/scripts/install-check.ps1
```

## Usage

### Test Sounds
```powershell
# Test success sound
powershell -ExecutionPolicy Bypass -File D:/kimi/skills/audio-notify/scripts/success-sound.ps1

# Test error sound
powershell -ExecutionPolicy Bypass -File D:/kimi/skills/audio-notify/scripts/error-sound.ps1
```

### With Kbot Tasks
The skill automatically hooks into Kbot:
- Task completes successfully → Success sound plays
- Task fails → Error sound plays (3x alert)

### Custom Audio Files
Place your custom WAV/MP3 files in:
- `D:/kimi/skills/audio-notify/sounds/custom-success.wav`
- `D:/kimi/skills/audio-notify/sounds/custom-error.wav`

## Configuration

Edit `config.ps1` to customize:
- Volume level (0-100)
- Sound frequency/duration
- Custom audio file paths

## Uninstall

```powershell
powershell -ExecutionPolicy Bypass -File D:/kimi/skills/audio-notify/scripts/uninstall.ps1
```
