---
id: sun-moon
title: Sun & Moon Commands
sidebar_label: Sun & Moon
sidebar_position: 5
---

# Sun & Moon Commands

Solar and lunar position calculations.

## Sun Commands

### `astr0 sun position`

Current solar position.

```bash
astr0 sun position
astr0 sun position --jd 2451545.0  # At J2000.0
```

### `astr0 sun rise` / `astr0 sun set`

Sunrise and sunset times.

```bash
astr0 sun rise --lat 40.7 --lon -74.0
astr0 sun set --observer home
```

### `astr0 sun twilight`

Twilight times (civil, nautical, astronomical).

```bash
astr0 sun twilight --lat 51.5 --lon -0.1
```

### `astr0 sun altitude`

Current solar altitude.

```bash
astr0 sun altitude --lat 40.7 --lon -74.0
```

## Moon Commands

### `astr0 moon position`

Current lunar position.

```bash
astr0 moon position
```

### `astr0 moon phase`

Current lunar phase.

```bash
astr0 moon phase
```

Output includes phase name, illumination percentage, and age in days.

### `astr0 moon rise` / `astr0 moon set`

Moonrise and moonset times.

```bash
astr0 moon rise --lat 40.7 --lon -74.0
```

### `astr0 moon next`

Find the next occurrence of a phase.

```bash
astr0 moon next full
astr0 moon next new
```

## Examples

```bash
# Solar noon at Greenwich
astr0 sun noon --lat 51.4769 --lon -0.0005

# Day length in summer vs winter
astr0 sun rise --lat 60 --lon 0 --jd 2460479.5  # June
astr0 sun rise --lat 60 --lon 0 --jd 2460296.5  # December

# Moon phase with verbose calculation
astr0 moon phase --verbose

# JSON output for scripting
astr0 sun position --json | jq '.ra_hours'
```

## Python API

```python
from astr0.core.sun import sun_position, sunrise, sunset
from astr0.core.moon import moon_position, moon_phase
from astr0.core.observer import Observer

# Sun position
sun = sun_position()
print(f"Sun RA: {sun.ra.format_hms()}")
print(f"Equation of time: {sun.equation_of_time:.1f} min")

# Sunrise at a location
observer = Observer.from_degrees("NYC", 40.7, -74.0)
rise = sunrise(observer)
print(f"Sunrise: {rise.to_datetime()}")

# Moon phase
phase = moon_phase()
print(f"Phase: {phase.phase_name.value}")
print(f"Illumination: {phase.percent_illuminated:.1f}%")
```
