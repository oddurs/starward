---
id: time
title: Time & Julian Dates
sidebar_label: Time
sidebar_position: 1
---

# Time & Julian Dates

Time in astronomy is more nuanced than your watch suggests. This guide explains the time systems astronomers use and how to work with them in astr0.

---

## Why Astronomers Don't Use Regular Dates

Imagine trying to calculate the number of days between February 28, 1900 and March 1, 2000. You'd need to account for:

- Varying month lengths (28, 29, 30, 31 days)
- Leap years (but not century years... except every 400 years!)
- Calendar reforms (Gregorian vs Julian calendar)
- Time zones and daylight saving

Astronomers solved this problem by counting days from a single reference point: the **Julian Date**.

---

## The Julian Date System

### What Is a Julian Date?

A Julian Date (JD) is simply the number of **days** (including fractions) since **noon Universal Time on January 1, 4713 BCE** (Julian calendar).

Why that date? It was chosen by Joseph Scaliger in 1583 as a convenient starting point before any recorded history, so all historical dates have positive JD values.

### Key Reference Points

| Event | Julian Date |
|-------|-------------|
| Start of Julian Day system | 0.0 |
| January 1, 2000 at noon (J2000.0) | 2,451,545.0 |
| Today (approximately) | ~2,461,043 |

### Why Noon?

JD starts at noon because astronomers historically made observations at night. Having the day change at midnight would split a single night's observations across two dates—inconvenient! With noon as the start, a night's work all falls on the same Julian Date.

---

## Working with Julian Dates

### Get the Current JD

```bash
astr0 time now
```

Output:
```text
╭────────────────────────────────────────────╮
│  Current Astronomical Time                 │
├────────────────────────────────────────────┤
│  UTC:                 2026-01-03 00:15:00 │
│  Julian Date:              2461043.510417 │
│  Modified JD:                61043.010417 │
│  T (J2000):                  0.2600550411 │
│  GMST:                     07h 05m 34.60s │
╰────────────────────────────────────────────╯
```

### Convert a Julian Date to Calendar Date

```bash
astr0 time convert 2460000.5
```

Output:
```text
JD 2460000.500000 = 2023-02-25 00:00:00 UTC
```

### Convert Calendar Date to Julian Date

```bash
astr0 time jd 2024 7 4 12 0 0
```

This converts July 4, 2024 at 12:00:00 UTC to JD.

---

## Modified Julian Date (MJD)

The standard JD has a problem: the numbers are getting large. For modern dates, JD is over 2.4 million. This can cause precision issues in some computer systems.

The **Modified Julian Date** solves this:

$$\text{MJD} = \text{JD} - 2400000.5$$

This shifts the epoch to **midnight on November 17, 1858**, giving smaller numbers and starting at midnight instead of noon.

| System | J2000.0 Value | Epoch |
|--------|---------------|-------|
| JD | 2,451,545.0 | Jan 1, 4713 BCE noon |
| MJD | 51,544.5 | Nov 17, 1858 midnight |

### Converting Between JD and MJD

```bash
astr0 time convert 60000 --from mjd
```

Output:
```text
MJD 60000.000000 = JD 2460000.500000 = 2023-02-25 00:00:00 UTC
```

---

## J2000.0 and Julian Centuries

### The J2000.0 Epoch

Modern astronomy uses **J2000.0** as the standard reference epoch:

- **Date**: January 1, 2000 at 12:00:00 TT (Terrestrial Time)
- **Julian Date**: 2,451,545.0

Celestial coordinates, orbital elements, and many other quantities are referenced to this epoch.

### Julian Centuries (T)

Many astronomical formulas express time as **Julian centuries since J2000.0**:

$$T = \frac{\text{JD} - 2451545.0}{36525}$$

Where 36,525 is the number of days in a Julian century (365.25 × 100).

In astr0, this is shown as "T (J2000)" in the `time now` output.

**Example**: T = 0.26 means we're about 0.26 centuries (26 years) past J2000.0.

---

## Sidereal Time

### What Is Sidereal Time?

The **sidereal day** is the time it takes Earth to rotate once relative to the distant stars—about 23 hours, 56 minutes, and 4 seconds.

Because Earth also orbits the Sun, the solar day (noon to noon) is about 4 minutes longer than the sidereal day. Over a year, this adds up to one extra sidereal day.

**Sidereal time** tells you which part of the celestial sphere is currently on your meridian (the line from north to south through your zenith).

### Greenwich Mean Sidereal Time (GMST)

GMST is the hour angle of the vernal equinox as seen from Greenwich. It's shown in the `time now` output.

**Why does it matter?** If an object has Right Ascension = GMST, it's currently crossing the Greenwich meridian.

### Local Sidereal Time (LST)

LST adjusts GMST for your longitude:

$$\text{LST} = \text{GMST} + \frac{\text{longitude}}{15}$$

Where longitude is in degrees (positive east).

**Example**: Calculate LST for Los Angeles (longitude -118.25°):

```bash
astr0 time lst -- -118.25
```

(The `--` tells the CLI that `-118.25` is a value, not a flag.)

Output:
```text
Longitude:    -118.2500° (W)
Julian Date:  2461043.510878
─────────────────────────────────────────────
GMST:         07h 06m 14.11s
LST:          23h 13m 14.11s
```

**Interpretation**: At this moment in LA, objects with RA ≈ 23h 13m are on the meridian and highest in the sky.

---

## The Math Behind GMST

Want to see how GMST is calculated? Use verbose mode:

```bash
astr0 --verbose time now
```

You'll see the calculation using the IAU 2006 formula:

```text
┌─ Calculate GMST
│  T = (JD - 2451545.0) / 36525 = 0.26005504...
│
│  GMST (degrees) = 280.46061837
│                 + 360.98564736629 × D
│                 + 0.000387933 × T²
│                 − T³/38710000
│  where D = JD - 2451545.0
│
│  GMST = 280.46061837 + 342152.4... + ...
│       = 106.4583...° = 7.097h
└────────────────────────────────────────
```

---

## The Julian Date Algorithm

Converting between calendar dates and Julian Dates uses an elegant algorithm. Here's the formula for calendar → JD:

For a date Y-M-D at hour H:

$$JD = 367Y - \text{INT}\left(\frac{7(Y + \text{INT}(\frac{M+9}{12}))}{4}\right) + \text{INT}\left(\frac{275M}{9}\right) + D + 1721013.5 + \frac{H}{24}$$

This formula handles leap years automatically through integer division tricks.

---

## Common Tasks

### Days Between Two Dates

Julian Dates make this trivial:

```bash
# JD of July 4, 1776
astr0 time jd 1776 7 4
# JD of July 4, 2026
astr0 time jd 2026 7 4
# Subtract the results: ~91,311 days (250 years)
```

### What Day of the Week?

JD mod 7 gives the day of the week:
- 0 = Monday
- 1 = Tuesday
- ... and so on

The integer part of the JD at noon gives this directly.

### Is a Star Visible Tonight?

If an object's Right Ascension equals your LST, it's on your meridian—highest in the sky and best positioned for observation. Objects within a few hours of your LST are well-placed for viewing.

---

## Python API

For programmatic access:

```python
from astr0.core.time import JulianDate, jd_now

# Current time
jd = jd_now()
print(f"JD: {jd.jd}")
print(f"MJD: {jd.mjd}")
print(f"T (J2000): {jd.t_j2000}")
print(f"GMST: {jd.gmst()} hours")

# From calendar
jd = JulianDate.from_calendar(2024, 7, 4, 12, 0, 0)

# To calendar
dt = jd.to_datetime()

# LST for a longitude
lst = jd.lst(longitude=-118.25)
```

---

## Key Formulas Reference

| Quantity | Formula |
|----------|---------|
| MJD → JD | $JD = MJD + 2400000.5$ |
| T (centuries) | $T = (JD - 2451545.0) / 36525$ |
| LST | $LST = GMST + \lambda/15$ |

---

## Further Reading

- Explanatory Supplement to the Astronomical Almanac (Seidelmann, ed.)
- Meeus, J. "Astronomical Algorithms" — Chapter 7 (Julian Day)
- USNO Circular 179 — Time systems explained

---

*Next: [Coordinate Systems](/module-guides/coords) — Navigate the celestial sphere*
