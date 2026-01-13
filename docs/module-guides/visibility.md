---
id: visibility
title: Visibility Module
sidebar_label: Visibility
sidebar_position: 8
---

# Visibility Module

The Visibility module provides tools for planning astronomical observations—calculating airmass, transit times, rise/set events, and assessing overall target observability.

## Overview

Planning a successful observation requires knowing:

- When is the target above the horizon?
- What's the best time to observe (lowest airmass)?
- Will moonlight interfere?
- Is it actually dark enough?

This module answers all these questions.

## Quick Start

### CLI Usage

```bash
# Target altitude now
astr0 vis altitude "12h00m00s" "+45d00m00s" --lat 51.5 --lon -0.1

# Current airmass
astr0 vis airmass "12h00m00s" "+45d00m00s" --lat 51.5 --lon -0.1

# Transit time
astr0 vis transit "12h00m00s" "+45d00m00s" --lat 51.5 --lon -0.1

# Rise and set times
astr0 vis riseset "12h00m00s" "+45d00m00s" --lat 51.5 --lon -0.1

# Moon separation
astr0 vis moonsep "12h00m00s" "+45d00m00s"
```

### Python API

```python
from astr0.core.visibility import (
    airmass, target_altitude, target_azimuth,
    transit_time, transit_altitude_calc, target_rise_set,
    moon_target_separation, is_night, compute_visibility
)
from astr0.core.coords import ICRSCoord
from astr0.core.observer import Observer
from astr0.core.time import jd_now
from astr0.core.angles import Angle

# Setup
m31 = ICRSCoord.parse("00h42m44s +41d16m09s")  # Andromeda Galaxy
observer = Observer.from_degrees("Home", 40.7, -74.0)
jd = jd_now()

# Current visibility
alt = target_altitude(m31, observer, jd)
az = target_azimuth(m31, observer, jd)
X = airmass(alt)

print(f"Altitude: {alt.degrees:.1f}°")
print(f"Azimuth: {az.degrees:.1f}°")
print(f"Airmass: {X:.2f}")

# Best time to observe
transit = transit_time(m31, observer, jd)
max_alt = transit_altitude_calc(m31, observer)
print(f"Transit: {transit.to_datetime()}")
print(f"Max altitude: {max_alt.degrees:.1f}°")
```

## Airmass

Airmass measures how much atmosphere light must traverse. Lower is better.

| Airmass | Altitude | Quality |
|---------|----------|---------|
| 1.0 | 90° (zenith) | Excellent |
| 1.2 | 56° | Very good |
| 1.5 | 42° | Good |
| 2.0 | 30° | Acceptable |
| 3.0 | 19° | Poor |
| ∞ | 0° (horizon) | Below horizon |

```python
from astr0.core.visibility import airmass
from astr0.core.angles import Angle

# From altitude
alt = Angle(degrees=45)
X = airmass(alt)
print(f"Airmass at 45°: {X:.2f}")  # ~1.41

# From target
alt = target_altitude(target, observer, jd)
X = airmass(alt)
```

### Airmass Limits

Most observations should stay below airmass 2.0:

```python
def is_observable(target, observer, jd, max_airmass=2.0):
    alt = target_altitude(target, observer, jd)
    if alt.degrees <= 0:
        return False
    return airmass(alt) < max_airmass
```

## Target Altitude and Azimuth

```python
# Current position in local sky
alt = target_altitude(target, observer, jd)
az = target_azimuth(target, observer, jd)

print(f"Position: Alt {alt.degrees:.1f}°, Az {az.degrees:.1f}°")

# Azimuth convention: 0°=N, 90°=E, 180°=S, 270°=W
```

## Transit Time

Transit is when an object crosses the local meridian (highest altitude):

```python
# Time of next transit
transit = transit_time(target, observer, jd)
print(f"Transit at: {transit.to_datetime()}")

# Maximum altitude (achieved at transit)
max_alt = transit_altitude_calc(target, observer)
print(f"Maximum altitude: {max_alt.degrees:.1f}°")

# Minimum airmass
min_airmass = airmass(max_alt)
print(f"Best airmass: {min_airmass:.2f}")
```

### Transit Altitude Formula

For any observer at latitude φ and target at declination δ:

$$\text{max altitude} = 90° - |φ - δ|$$

```python
# A target at declination +40° viewed from latitude +40°
# transits at zenith (90° altitude)
```

## Rise and Set Times

```python
# Get rise and set times
rise, set_t = target_rise_set(target, observer, jd)

if rise and set_t:
    print(f"Rises: {rise.to_datetime()}")
    print(f"Sets: {set_t.to_datetime()}")
    
    # Duration above horizon
    hours_up = (set_t.jd - rise.jd) * 24
    print(f"Above horizon: {hours_up:.1f} hours")
```

### Circumpolar Objects

Objects that never set (circumpolar) or never rise:

```python
rise, set_t = target_rise_set(target, observer, jd)

if rise is None and set_t is None:
    max_alt = transit_altitude_calc(target, observer)
    if max_alt.degrees > 0:
        print("Circumpolar - always above horizon")
    else:
        print("Never rises at this latitude")
```

## Moon Separation

For deep-sky imaging, moonlight is the enemy:

```python
from astr0.core.visibility import moon_target_separation

sep = moon_target_separation(target, jd)
print(f"Moon separation: {sep.degrees:.1f}°")

# Rule of thumb
if sep.degrees < 30:
    print("⚠️ Moon nearby - may affect observations")
elif sep.degrees < 60:
    print("Moon moderately close")
else:
    print("Good moon separation")
```

## Night Check

Is it actually dark?

```python
from astr0.core.visibility import is_night

if is_night(observer, jd):
    print("It's nighttime!")
else:
    print("Sun is up")
```

For astronomical darkness (Sun below -18°), combine with twilight:

```python
from astr0.core.sun import astronomical_twilight

astro_start, astro_end = astronomical_twilight(observer, jd)
# True darkness is between these times
```

## Comprehensive Visibility

The `compute_visibility()` function provides a complete assessment:

```python
from astr0.core.visibility import compute_visibility

vis = compute_visibility(target, observer, jd)

# vis is a dictionary containing:
# - altitude: current altitude
# - azimuth: current azimuth  
# - airmass: current airmass
# - transit_time: time of transit
# - transit_altitude: maximum altitude
# - rise_time: rise time
# - set_time: set time
# - moon_separation: angular distance from Moon
# - is_night: whether Sun is down
# - is_observable: overall assessment
```

## Planning an Observing Session

Example workflow for planning observations:

```python
from astr0.core.visibility import *
from astr0.core.sun import sunset, astronomical_twilight
from astr0.core.moon import moon_phase

# Tonight's observation planning
observer = Observer.from_degrees("Home", 40.7, -74.0)
jd_start = JulianDate.from_calendar(2024, 3, 15, 20, 0, 0)  # 8 PM local

# When does it get dark?
astro_start, astro_end = astronomical_twilight(observer, jd_start)
print(f"Astronomical darkness: {astro_start.to_datetime()} to {astro_end.to_datetime()}")

# Moon situation
phase = moon_phase(jd_start)
print(f"Moon phase: {phase.name} ({phase.percent_illuminated:.0f}%)")

# Target visibility
targets = [
    ("M31", ICRSCoord.parse("00h42m44s +41d16m09s")),
    ("M42", ICRSCoord.parse("05h35m17s -05d23m28s")),
    ("M51", ICRSCoord.parse("13h29m53s +47d11m43s")),
]

print("\nTarget Visibility Tonight:")
for name, coord in targets:
    vis = compute_visibility(coord, observer, jd_start)
    print(f"\n{name}:")
    print(f"  Transit: {vis['transit_time'].to_datetime().strftime('%H:%M')}")
    print(f"  Max alt: {vis['transit_altitude'].degrees:.0f}°")
    print(f"  Moon sep: {vis['moon_separation'].degrees:.0f}°")
```

## Altitude Over Time

Track altitude throughout the night:

```python
import matplotlib.pyplot as plt

times = []
altitudes = []

# Sample every 30 minutes for 12 hours
for i in range(25):
    jd_sample = JulianDate(jd_start.jd + i * 0.5/24)
    alt = target_altitude(target, observer, jd_sample)
    times.append(i * 0.5)
    altitudes.append(alt.degrees)

plt.plot(times, altitudes)
plt.xlabel("Hours from start")
plt.ylabel("Altitude (degrees)")
plt.axhline(y=30, color='r', linestyle='--', label='30° limit')
plt.title("Target Altitude Tonight")
plt.legend()
plt.show()
```

## CLI Reference

```bash
# Altitude
astr0 vis altitude RA DEC --lat LAT --lon LON [--jd JD] [--json]

# Airmass
astr0 vis airmass RA DEC --lat LAT --lon LON [--jd JD]

# Transit
astr0 vis transit RA DEC --lat LAT --lon LON [--jd JD]

# Rise/Set
astr0 vis riseset RA DEC --lat LAT --lon LON [--jd JD]

# Moon separation
astr0 vis moonsep RA DEC [--jd JD]

# Full visibility report
astr0 vis report RA DEC --lat LAT --lon LON [--jd JD] [--json]
```

## See Also

- [Sun Module](/module-guides/sun) - Twilight and darkness
- [Moon Module](/module-guides/moon) - Lunar interference
- [Observer Module](/module-guides/observer) - Location management
- [Coords Module](/module-guides/coords) - Coordinate systems
