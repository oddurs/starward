---
id: moon
title: Moon Module
sidebar_label: Moon
sidebar_position: 5
---

# Moon Module

The Moon module provides calculations for lunar position, phases, rise/set times, and related phenomena. Essential for planning observations and understanding our celestial companion.

## Overview

The Moon's motion is complex—more so than any other celestial body we observe regularly. This module implements algorithms suitable for:

- Lunar position (RA/Dec, ecliptic coordinates)
- Moon phase (illumination, age, phase name)
- Moonrise and moonset times
- Next occurrence of major phases
- Angular diameter and parallax

**Accuracy**: Position ~0.5° (sufficient for rise/set and phase calculations).

## Quick Start

### CLI Usage

```bash
# Current lunar position
astr0 moon position

# Current phase information
astr0 moon phase

# Moonrise and moonset
astr0 moon rise --lat 51.5 --lon -0.1
astr0 moon set --lat 51.5 --lon -0.1

# Next full moon
astr0 moon next full

# Next new moon
astr0 moon next new
```

### Python API

```python
from astr0.core.moon import (
    moon_position, moon_phase, moon_altitude,
    moonrise, moonset, next_phase, MoonPhase
)
from astr0.core.observer import Observer
from astr0.core.time import jd_now

# Create an observer
greenwich = Observer.from_degrees("Greenwich", 51.4772, -0.0005)

# Get current lunar position
jd = jd_now()
pos = moon_position(jd)
print(f"Moon RA: {pos.ra.hours:.2f}h, Dec: {pos.dec.degrees:.1f}°")
print(f"Distance: {pos.distance_km:.0f} km")

# Current phase
phase = moon_phase(jd)
print(f"Phase: {phase.name}")
print(f"Illumination: {phase.percent_illuminated:.0f}%")
print(f"Age: {phase.age_days:.1f} days")

# Moonrise and moonset
rise = moonrise(greenwich, jd)
if rise:
    print(f"Moonrise: {rise.to_datetime()}")

# Next full moon
next_full = next_phase(jd, MoonPhase.FULL_MOON)
print(f"Next full moon: {next_full.to_datetime()}")
```

## Lunar Position

The `moon_position()` function returns a `MoonPosition` object containing:

| Field | Description |
|-------|-------------|
| `longitude` | Ecliptic longitude (Angle) |
| `latitude` | Ecliptic latitude (Angle, ±5.3°) |
| `ra` | Right Ascension (Angle) |
| `dec` | Declination (Angle) |
| `distance_km` | Distance in kilometers |
| `angular_diameter` | Apparent size (Angle) |
| `parallax` | Horizontal parallax (Angle) |

### Distance and Size

The Moon's distance varies from ~356,500 km (perigee) to ~406,700 km (apogee), causing its apparent size to vary:

```python
pos = moon_position(jd)
print(f"Distance: {pos.distance_km:.0f} km")
print(f"Angular diameter: {pos.angular_diameter.arcminutes:.1f} arcmin")
print(f"Parallax: {pos.parallax.degrees:.2f}°")
```

When the Moon is closer, it appears larger—a "supermoon" occurs when a full moon coincides with perigee.

## Moon Phase

The `moon_phase()` function returns a `MoonPhaseInfo` object:

| Field | Description |
|-------|-------------|
| `phase_angle` | Phase angle (0° = new, 180° = full) |
| `illumination` | Illuminated fraction (0-1) |
| `percent_illuminated` | Percentage (0-100) |
| `age_days` | Days since new moon (0-29.5) |
| `name` | Phase name (string) |

### Phase Names

The lunar cycle is divided into eight phases:

| Phase | Age (days) | Illumination |
|-------|-----------|--------------|
| New Moon | 0 | 0% |
| Waxing Crescent | 1-7 | 0-50% |
| First Quarter | ~7.4 | 50% |
| Waxing Gibbous | 7-15 | 50-100% |
| Full Moon | ~14.8 | 100% |
| Waning Gibbous | 15-22 | 100-50% |
| Last Quarter | ~22.1 | 50% |
| Waning Crescent | 22-29.5 | 50-0% |

```python
phase = moon_phase(jd)
print(f"Phase: {phase.name}")
print(f"Age: {phase.age_days:.1f} days")
print(f"Illumination: {phase.percent_illuminated:.0f}%")
```

## Finding Next Phases

Find the next occurrence of a major phase:

```python
from astr0.core.moon import next_phase, MoonPhase

jd = jd_now()

# Major phases
next_new = next_phase(jd, MoonPhase.NEW_MOON)
next_first = next_phase(jd, MoonPhase.FIRST_QUARTER)
next_full = next_phase(jd, MoonPhase.FULL_MOON)
next_last = next_phase(jd, MoonPhase.LAST_QUARTER)

print(f"Next new moon: {next_new.to_datetime()}")
print(f"Next full moon: {next_full.to_datetime()}")
```

## Moonrise and Moonset

Unlike the Sun, the Moon rises and sets at very different times each day (about 50 minutes later each day on average):

```python
rise = moonrise(observer, jd)
set_t = moonset(observer, jd)

if rise and set_t:
    print(f"Moonrise: {rise.to_datetime()}")
    print(f"Moonset: {set_t.to_datetime()}")
```

### Edge Cases

- The Moon may not rise or set on a given day
- Near full moon, moonrise occurs around sunset
- Near new moon, moonrise occurs around sunrise

## Moon Altitude

Calculate the Moon's altitude at any time:

```python
alt = moon_altitude(observer, jd)
print(f"Moon altitude: {alt.degrees:.1f}°")

if alt.degrees > 0:
    print("Moon is up")
```

## The Synodic Month

The synodic month (new moon to new moon) averages 29.53 days but varies due to the elliptical orbit:

```python
# Find two consecutive new moons
new1 = next_phase(jd, MoonPhase.NEW_MOON)
new2 = next_phase(JulianDate(new1.jd + 1), MoonPhase.NEW_MOON)

synodic_month = new2.jd - new1.jd
print(f"This synodic month: {synodic_month:.2f} days")
```

## Observation Planning

### Moon-Target Separation

For deep-sky observations, moonlight can be problematic. Use the visibility module:

```python
from astr0.core.visibility import moon_target_separation
from astr0.core.coords import ICRSCoord

target = ICRSCoord.from_degrees(83.63, 22.01)  # M1 Crab Nebula
sep = moon_target_separation(target, jd)
print(f"Moon separation: {sep.degrees:.1f}°")

if sep.degrees < 30:
    print("Moon may affect observations")
```

### Best Observation Windows

For faint objects, plan observations when:
1. Moon is below the horizon
2. Moon is far from target (>60°)
3. Moon is near new phase

## Lunar Libration

Although not directly computed by this module, the Moon's apparent "wobble" (libration) means we can see about 59% of its surface over time, not just 50%.

## Algorithm Details

This module uses the simplified lunar theory from Jean Meeus' *Astronomical Algorithms*, incorporating:

- Mean orbital elements
- Major perturbations from the Sun
- Variation in orbital speed
- Parallax correction

For higher precision (sub-arcminute), consider ELP/MPP02 (not yet implemented).

## CLI Reference

```bash
# Position
astr0 moon position [--jd JD] [--json] [--verbose]

# Phase
astr0 moon phase [--jd JD] [--json]

# Rise/Set
astr0 moon rise --lat LAT --lon LON [--jd JD]
astr0 moon set --lat LAT --lon LON [--jd JD]

# Altitude
astr0 moon altitude --lat LAT --lon LON [--jd JD]

# Next phase (full|new|first|last)
astr0 moon next PHASE [--jd JD]
```

## See Also

- [Sun Module](/module-guides/sun) - Solar calculations
- [Visibility Module](/module-guides/visibility) - Observation planning
- [Observer Module](/module-guides/observer) - Location management
