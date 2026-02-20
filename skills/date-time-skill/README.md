# Date Time Skill

A comprehensive date and time utility skill for Kimi CLI that provides timezone conversion, date calculations, and formatting capabilities.

## Features

- 🌍 **Timezone Conversion**: Convert between 500+ timezones worldwide
- 📅 **Date Calculations**: Add/subtract days, months, years; calculate differences
- 🎨 **Date Formatting**: Multiple output formats (ISO, local, custom)
- 🌐 **Multi-language Support**: Support for various date formats and locales
- ⏰ **Business Days**: Calculate working days excluding weekends

## Installation

```bash
# Copy skill to Kimi skills directory
cp -r date-time-skill ~/.kimi/skills/

# Install dependencies
pip install -r ~/.kimi/skills/date-time-skill/requirements.txt
```

## Quick Start

```python
from skills.date_time_skill.main import DateTimeSkill

skill = DateTimeSkill()

# Convert timezone
result = skill.convert_timezone("2026-02-20 14:30:00", "Asia/Shanghai", "America/New_York")
print(result)  # 2026-02-20 01:30:00 EST

# Calculate date difference
days = skill.date_difference("2026-01-01", "2026-12-31")
print(f"Days: {days}")  # Days: 364

# Add days to date
future = skill.add_days("2026-02-20", 30)
print(future)  # 2026-03-22
```

## Documentation

- [SKILL.md](./SKILL.md) - Detailed usage guide
- [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md) - Example use cases

## License

MIT License
