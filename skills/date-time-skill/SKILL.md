# Date Time Skill

**Category:** Utility  
**Version:** 1.0.0  
**Author:** godlike-kimi-skills

---

## Use When

- Converting dates/times between different timezones
- Calculating date differences (days, months, years between dates)
- Adding or subtracting time periods from dates
- Formatting dates in various output formats
- Checking if a date falls on a weekend or calculating business days
- Working with international dates and multiple timezone requirements
- Need to determine ISO week numbers or day of week
- Calculating age or time elapsed between events

---

## Out of Scope

- Calendar scheduling or appointment management
- Recurring event calculations (e.g., "every second Tuesday")
- Holiday calculations (business days excluding holidays)
- Complex date parsing from natural language ("next week", "two days ago")
- Astronomical time calculations (sunrise, sunset, moon phases)
- Stopwatch or timer functionality
- Time series data analysis
- Cron expression generation

---

## Quick Reference

### Core Methods

```python
from skills.date_time_skill.main import DateTimeSkill

skill = DateTimeSkill()

# Timezone Conversion
result = skill.convert_timezone("2026-02-20 14:30:00", "Asia/Shanghai", "America/New_York")
# Returns: "2026-02-20 01:30:00"

# Date Calculations
future = skill.add_days("2026-02-20", 30)       # "2026-03-22"
future = skill.add_months("2026-02-20", 3)      # "2026-05-20"
future = skill.add_years("2026-02-20", 1)       # "2027-02-20"

# Date Differences
days = skill.date_difference("2026-01-01", "2026-12-31", unit='days')      # 364
weeks = skill.date_difference("2026-01-01", "2026-12-31", unit='weeks')   # 52.0

# Business Days
business_days = skill.count_business_days("2026-02-01", "2026-02-28")     # 20
new_date = skill.add_business_days("2026-02-20", 5)                        # "2026-02-27"

# Formatting
formatted = skill.format_date("2026-02-20", "full")       # "Friday, February 20, 2026"
iso = skill.format_date("2026-02-20", "iso_date")         # "2026-02-20"
```

---

## Supported Timezones

Access 500+ IANA timezones via `pytz`:
- `UTC`, `GMT`
- `America/New_York`, `America/Los_Angeles`, `America/Chicago`
- `Europe/London`, `Europe/Paris`, `Europe/Berlin`
- `Asia/Shanghai`, `Asia/Tokyo`, `Asia/Singapore`
- `Australia/Sydney`, `Pacific/Auckland`

```python
# List timezones
asia_zones = skill.list_timezones("Asia")
all_zones = skill.list_timezones()

# Get timezone info
info = skill.get_timezone_info("Asia/Shanghai")
# Returns: {'name': 'Asia/Shanghai', 'utc_offset': '+0800', 'dst_active': False, ...}
```

---

## Output Formats

| Format Key | Example Output |
|------------|----------------|
| `iso` | `2026-02-20T14:30:00` |
| `iso_date` | `2026-02-20` |
| `iso_datetime` | `2026-02-20 14:30:00` |
| `us` | `02/20/2026` |
| `us_datetime` | `02/20/2026 02:30 PM` |
| `eu` | `20/02/2026` |
| `full` | `Friday, February 20, 2026` |
| `compact` | `20260220` |

Custom formats use Python `strftime` syntax.

---

## CLI Usage

```bash
# Convert timezone
python main.py convert "2026-02-20 14:30:00" Asia/Shanghai America/New_York

# Get current time
python main.py now Asia/Shanghai

# Add days
python main.py add "2026-02-20" 30

# Calculate difference
python main.py diff "2026-01-01" "2026-12-31"

# Format date
python main.py format "2026-02-20" full
```

---

## Method Reference

### Timezone Operations

- `convert_timezone(date, from_tz, to_tz, output_format='iso_datetime')` - Convert between timezones
- `get_current_time(timezone='UTC', output_format='iso_datetime')` - Get current time in timezone
- `list_timezones(region=None)` - List available timezones
- `get_timezone_info(timezone)` - Get timezone metadata

### Date Arithmetic

- `add_days(date, days)` - Add/subtract days
- `add_months(date, months)` - Add/subtract months
- `add_years(date, years)` - Add/subtract years
- `add_business_days(date, days)` - Add business days (skip weekends)

### Date Queries

- `date_difference(date1, date2, unit='days')` - Calculate difference
- `is_weekend(date)` - Check if date is weekend
- `is_leap_year(year)` - Check if leap year
- `get_week_number(date)` - Get ISO week number
- `get_day_of_week(date)` - Get day name
- `get_days_in_month(year, month)` - Days in month
- `count_business_days(start, end)` - Count business days

### Formatting

- `parse_date(date_string)` - Parse date to datetime object
- `format_date(date, output_format)` - Format date string

---

## Dependencies

```
pytz>=2023.3
python-dateutil>=2.8.2
```

---

## Examples

### International Meeting Scheduler

```python
skill = DateTimeSkill()
meeting_time = "2026-03-15 10:00:00"

attendees = [
    ("New York", "America/New_York"),
    ("London", "Europe/London"),
    ("Tokyo", "Asia/Tokyo"),
    ("Shanghai", "Asia/Shanghai"),
]

print("Meeting times around the world:")
for city, tz in attendees:
    local_time = skill.convert_timezone(meeting_time, "UTC", tz)
    print(f"  {city}: {local_time}")
```

### Project Deadline Calculator

```python
skill = DateTimeSkill()
start_date = "2026-03-01"
duration_days = 90

end_date = skill.add_business_days(start_date, duration_days)
weeks = skill.date_difference(start_date, end_date, unit='weeks')

print(f"Project starts: {start_date}")
print(f"Project ends (business days): {end_date}")
print(f"Duration: {weeks:.1f} weeks")
```
