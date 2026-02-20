# Date Time Skill - Usage Examples

## Example 1: International Meeting Scheduler

Schedule meetings across multiple timezones:

```python
from skills.date_time_skill.main import DateTimeSkill

skill = DateTimeSkill()

# Meeting scheduled in UTC
meeting_utc = "2026-03-15 14:00:00"

attendees = [
    ("New York", "America/New_York"),
    ("London", "Europe/London"),
    ("Berlin", "Europe/Berlin"),
    ("Tokyo", "Asia/Tokyo"),
    ("Shanghai", "Asia/Shanghai"),
    ("Sydney", "Australia/Sydney"),
]

print(f"Meeting Time (UTC): {meeting_utc}")
print("-" * 50)

for city, timezone in attendees:
    local_time = skill.convert_timezone(meeting_utc, "UTC", timezone)
    day = skill.get_day_of_week(local_time.split()[0])
    print(f"{city:15} ({timezone:20}): {local_time} ({day})")
```

Output:
```
Meeting Time (UTC): 2026-03-15 14:00:00
--------------------------------------------------
New York        (America/New_York    ): 2026-03-15 10:00:00 (Sunday)
London          (Europe/London       ): 2026-03-15 14:00:00 (Sunday)
Berlin          (Europe/Berlin       ): 2026-03-15 15:00:00 (Sunday)
Tokyo           (Asia/Tokyo          ): 2026-03-15 23:00:00 (Sunday)
Shanghai        (Asia/Shanghai       ): 2026-03-15 22:00:00 (Sunday)
Sydney          (Australia/Sydney    ): 2026-03-16 01:00:00 (Monday)
```

## Example 2: Project Timeline Calculator

Calculate project milestones with business days:

```python
skill = DateTimeSkill()

project_start = "2026-04-01"
phases = [
    ("Planning", 10),
    ("Design", 15),
    ("Development", 60),
    ("Testing", 20),
    ("Deployment", 5),
]

current_date = project_start
print(f"Project Start: {current_date}")
print("-" * 40)

total_business_days = 0
for phase_name, days in phases:
    start = current_date
    end = skill.add_business_days(current_date, days)
    total_business_days += days
    
    duration = skill.date_difference(start, end, unit='days')
    print(f"{phase_name:15} {start} to {end} ({int(duration)} calendar days)")
    
    current_date = skill.add_days(end, 1)

project_end = skill.add_business_days(project_start, total_business_days)
print("-" * 40)
print(f"Project End:   {project_end}")
print(f"Total Business Days: {total_business_days}")
```

## Example 3: Age Calculator

Calculate exact age with precision:

```python
skill = DateTimeSkill()

birth_date = "1990-06-15"
today = skill.get_current_time("UTC", "iso_date")

years = skill.date_difference(birth_date, today, unit='years')
months = skill.date_difference(birth_date, today, unit='months')
days = skill.date_difference(birth_date, today, unit='days')

print(f"Birth Date: {birth_date}")
print(f"Today:      {today}")
print(f"Age:        {int(years)} years")
print(f"            {int(months)} months")
print(f"            {int(days)} days")
```

## Example 4: Business Day Counter

Calculate working days in a month:

```python
skill = DateTimeSkill()

year, month = 2026, 2
first_day = f"{year}-{month:02d}-01"
last_day = f"{year}-{month:02d}-{skill.get_days_in_month(year, month)}"

business_days = skill.count_business_days(first_day, last_day)
weekends = skill.date_difference(first_day, last_day, unit='days') + 1 - business_days

print(f"Month: {year}-{month:02d}")
print(f"Business Days: {business_days}")
print(f"Weekend Days:  {int(weekends)}")
print(f"Total Days:    {skill.get_days_in_month(year, month)}")
```

## Example 5: Deadline Reminder System

Check upcoming deadlines:

```python
skill = DateTimeSkill()

deadlines = [
    ("Q1 Report", "2026-03-31"),
    ("Tax Filing", "2026-04-15"),
    ("Project Launch", "2026-05-01"),
]

today = skill.get_current_time("UTC", "iso_date")

print(f"Today: {today}")
print("-" * 40)

for name, deadline in deadlines:
    days_left = skill.date_difference(today, deadline, unit='days')
    
    if days_left < 0:
        status = "OVERDUE"
    elif days_left == 0:
        status = "DUE TODAY"
    elif days_left <= 7:
        status = "URGENT"
    elif days_left <= 30:
        status = "UPCOMING"
    else:
        status = "PLANNED"
    
    print(f"{name:20} {deadline} ({int(days_left)} days) - {status}")
```

## Example 6: Multi-format Date Display

Display dates in various formats:

```python
skill = DateTimeSkill()

date = "2026-12-25"

formats = [
    'iso_date',
    'iso_datetime',
    'us',
    'us_datetime',
    'eu',
    'full',
    'compact',
]

print(f"Original: {date}")
print("-" * 40)

for fmt in formats:
    formatted = skill.format_date(date, fmt)
    print(f"{fmt:20}: {formatted}")
```

Output:
```
Original: 2026-12-25
----------------------------------------
iso_date            : 2026-12-25
iso_datetime        : 2026-12-25 00:00:00
us                  : 12/25/2026
us_datetime         : 12/25/2026 12:00 AM
eu                  : 25/12/2026
full                : Friday, December 25, 2026
compact             : 20261225
```
