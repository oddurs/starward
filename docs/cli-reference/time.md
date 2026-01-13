---
id: time
title: Time Commands
sidebar_label: Time Commands
sidebar_position: 3
---

# Time Commands

Time system conversions and calculations.

## Commands

### `astr0 time now`

Display current time in multiple formats.

```bash
astr0 time now
```

Output includes UTC, Julian Date, Modified Julian Date, and Unix timestamp.

### `astr0 time convert`

Convert between time formats.

```bash
# From Julian Date
astr0 time convert 2451545.0

# From ISO date
astr0 time convert "2000-01-01T12:00:00"

# From Unix timestamp
astr0 time convert 946728000
```

### `astr0 time jd`

Get Julian Date for a specific time.

```bash
astr0 time jd "2024-06-21 12:00:00"
```

## Time Systems

| System | Description |
|--------|-------------|
| **JD** | Julian Date — days since Jan 1, 4713 BC |
| **MJD** | Modified JD — JD minus 2400000.5 |
| **Unix** | Seconds since Jan 1, 1970 |
| **LST** | Local Sidereal Time |

## Examples

```bash
# Current time with verbose calculation
astr0 time now --verbose

# JSON output for scripting
astr0 time now --json

# Convert J2000.0 epoch
astr0 time convert 2451545.0
```

## Python API

```python
from astr0 import JulianDate, jd_now, utc_to_jd

# Current time
now = jd_now()
print(f"JD: {now.jd}")

# Convert from datetime
from datetime import datetime
jd = utc_to_jd(datetime(2024, 6, 21, 12, 0, 0))

# Access properties
print(f"T (centuries since J2000): {jd.t_j2000}")
```
