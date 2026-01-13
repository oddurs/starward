---
id: planets
title: Planet Commands
sidebar_label: Planets
sidebar_position: 6
---

# Planet Commands

Planetary position and visibility calculations.

## Supported Planets

| Planet | Symbol | Alias |
|--------|--------|-------|
| Mercury | ☿ | `mercury` |
| Venus | ♀ | `venus` |
| Mars | ♂ | `mars` |
| Jupiter | ♃ | `jupiter` |
| Saturn | ♄ | `saturn` |
| Uranus | ⛢ | `uranus` |
| Neptune | ♆ | `neptune` |

## Commands

### `astr0 planets position <planet>`

Position of a specific planet.

```bash
astr0 planets position mars
astr0 planets position jupiter --jd 2451545.0
```

Output includes:
- Equatorial coordinates (RA/Dec)
- Distance from Earth and Sun
- Apparent magnitude
- Elongation from Sun
- Phase/illumination

### `astr0 planets all`

Summary of all planetary positions.

```bash
astr0 planets all
```

### `astr0 planets rise <planet>`

Planet rise time.

```bash
astr0 planets rise jupiter --lat 40.7 --lon -74.0
astr0 planets rise mars --observer home
```

### `astr0 planets set <planet>`

Planet set time.

```bash
astr0 planets set saturn --lat 40.7 --lon -74.0
```

### `astr0 planets transit <planet>`

Meridian transit time (when planet is highest).

```bash
astr0 planets transit jupiter --lat 40.7 --lon -74.0
```

### `astr0 planets altitude <planet>`

Current altitude of a planet.

```bash
astr0 planets altitude mars --lat 40.7 --lon -74.0
```

## Examples

```bash
# Quick overview using alias
astr0 p all

# Mars position with verbose calculation
astr0 planets position mars --verbose

# JSON for scripting
astr0 planets position jupiter --json | jq '.magnitude'

# Best time to observe Saturn
astr0 planets transit saturn --lat 34.05 --lon -118.25

# Check if Jupiter is up
astr0 planets altitude jupiter --lat 40.7 --lon -74.0
```

## Understanding the Output

### Elongation

The angular distance from the Sun:
- **0°** — Conjunction (behind or in front of Sun)
- **90°** — Quadrature (quarter phase for inner planets)
- **180°** — Opposition (best viewing for outer planets)

### Magnitude

Apparent brightness (lower = brighter):
- Venus: typically -4 to -3
- Jupiter: typically -2 to -1
- Saturn: typically +1 to +2
- Uranus: typically +5 to +6
- Neptune: typically +8

## Python API

```python
from astr0 import Planet, planet_position, all_planet_positions
from astr0.core.planets import planet_rise, planet_altitude
from astr0.core.observer import Observer

# Single planet
mars = planet_position(Planet.MARS)
print(f"Mars: RA {mars.ra.format_hms()}, Mag {mars.magnitude:+.1f}")

# All planets
positions = all_planet_positions()
for planet, pos in positions.items():
    print(f"{planet.value}: {pos.elongation.degrees:.1f}° from Sun")

# Rise time
observer = Observer.from_degrees("Home", 40.7, -74.0)
rise = planet_rise(Planet.JUPITER, observer)
if rise:
    print(f"Jupiter rises: {rise.to_datetime()}")
```
