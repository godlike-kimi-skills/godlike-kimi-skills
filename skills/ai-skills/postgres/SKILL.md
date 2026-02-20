---
name: postgres
version: 1.0
description: PostgreSQL database operation skill. Schema design, query optimization, migration assistance, and performance tuning.
---

# PostgreSQL Skill

Database design and operation assistant.

## Features

- Schema design recommendations
- Query optimization
- Migration script generation
- Index analysis
- Performance diagnostics

## Usage

```bash
# Optimize a query
python D:/kimi/skills/ai-skills/postgres/scripts/pg.py optimize "SELECT * FROM users WHERE email LIKE '%@gmail.com'"

# Generate schema
python D:/kimi/skills/ai-skills/postgres/scripts/pg.py schema --entities user,post,comment

# Analyze migrations
python D:/kimi/skills/ai-skills/postgres/scripts/pg.py migrate --from v1 --to v2
```
