# Audio Notify Configuration

# Volume settings (0-100)
$global:AudioNotify_Volume = 100

# Sound settings
$global:AudioNotify_SuccessFrequency = 1000  # Hz
$global:AudioNotify_SuccessDuration = 300     # ms
$global:AudioNotify_ErrorFrequency = 800     # Hz
$global:AudioNotify_ErrorDuration = 500      # ms

# Custom audio files (leave empty to use system sounds)
$global:AudioNotify_CustomSuccessPath = ""   # e.g., "D:\kimi\skills\audio-notify\sounds\custom-success.wav"
$global:AudioNotify_CustomErrorPath = ""     # e.g., "D:\kimi\skills\audio-notify\sounds\custom-error.wav"

# Repeat error sound count
$global:AudioNotify_ErrorRepeat = 3

# Delay between error sounds (ms)
$global:AudioNotify_ErrorDelay = 200
