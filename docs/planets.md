# Planets Module

The Planets module provides position calculations for the eight major planets (Mercury through Neptune) using algorithms from Jean Meeus' *Astronomical Algorithms*.

## Overview

Planetary positions are essential for observation planning and understanding solar system dynamics. This module calculates:

- Equatorial coordinates (RA/Dec)
- Distance from Earth and Sun
- Apparent magnitude
- Elongation from Sun
- Phase and illumination
- Rise/set/transit times

**Accuracy**: Positions typically within 1 arcminute, suitable for telescope pointing and observation planning.

## Supported Planets

| Planet | Symbol | Enum Value |
|--------|--------|------------|
| Mercury | ☿ | `Planet.MERCURY` |
| Venus | ♀ | `Planet.VENUS` |
| Mars | ♂ | `Planet.MARS` |
| Jupiter | ♃ | `Planet.JUPITER` |
| Saturn | ♄ | `Planet.SATURN` |
| Uranus | ⛢ | `Planet.URANUS` |
| Neptune | ♆ | `Planet.NEPTUNE` |

## Quick Start

### CLI Usage

```bash
# Single planet position
astr0 planets position mars

# All planets summary
astr0 planets all

# Planet rise/set times
astr0 planets rise jupiter --lat 40.7 --lon -74.0
astr0 planets set saturn --lat 40.7 --lon -74.0

# Transit time (when planet is highest)
astr0 planets transit jupiter --lat 40.7 --lon -74.0

# Current altitude
astr0 planets altitude mars --lat 40.7 --lon -74.0
```

### Python API

```python
from astr0.core.planets import (
    Planet, planet_position, all_planet_positions,
    planet_rise, planet_set, planet_transit, planet_altitude
)
from astr0.core.observer import Observer
from astr0.core.time import jd_now

# Get current Mars position
jd = jd_now()
mars = planet_position(Planet.MARS, jd)

print(f"Mars RA: {mars.ra.format_hms()}")
print(f"Mars Dec: {mars.dec.format_dms()}")
print(f"Distance: {mars.distance_au:.3f} AU")
print(f"Magnitude: {mars.magnitude:+.1f}")
print(f"Elongation: {mars.elongation.degrees:.1f}°")
print(f"Illumination: {mars.illumination:.1f}%")

# All planets at once
positions = all_planet_positions(jd)
for planet, pos in positions.items():
    print(f"{planet.value}: {pos.elongation.degrees:.0f}° from Sun, mag {pos.magnitude:+.1f}")

# Rise/set/transit for an observer
observer = Observer.from_degrees("Home", 40.7, -74.0)
rise = planet_rise(Planet.JUPITER, observer, jd)
transit = planet_transit(Planet.JUPITER, observer, jd)
set_time = planet_set(Planet.JUPITER, observer, jd)

if rise:
    print(f"Jupiter rises: {rise.to_datetime()}")
if transit:
    print(f"Jupiter transits: {transit.to_datetime()}")
if set_time:
    print(f"Jupiter sets: {set_time.to_datetime()}")
```

## Planet Position

The `planet_position()` function returns a `PlanetPosition` object:

| Field | Description |
|-------|-------------|
| `ra` | Right Ascension (Angle) |
| `dec` | Declination (Angle) |
| `distance_au` | Distance from Earth in AU |
| `distance_sun_au` | Distance from Sun in AU |
| `magnitude` | Apparent visual magnitude |
| `elongation` | Angular distance from Sun (Angle) |
| `illumination` | Illuminated fraction (0-100%) |
| `phase_angle` | Phase angle (Angle) |

### Elongation

Elongation indicates a planet's position relative to the Sun:

| Elongation | Meaning |
|------------|---------|
| 0° | Conjunction (same direction as Sun) |
| 90° | Quadrature (quarter phase for inner planets) |
| 180° | Opposition (opposite the Sun, best for outer planets) |

```python
mars = planet_position(Planet.MARS, jd)
if mars.elongation.degrees > 150:
    print("Mars is near opposition - excellent viewing!")
```

### Apparent Magnitude

Typical magnitude ranges:

| Planet | Range | Notes |
|--------|-------|-------|
| Venus | -4.6 to -3 | Brightest planet |
| Jupiter | -2.9 to -1.6 | Always prominent |
| Mars | +1.8 to -2.9 | Varies greatly with distance |
| Saturn | +1.5 to -0.2 | Rings affect brightness |
| Mercury | +5 to -2 | Hard to observe |
| Uranus | +5.6 to +5.9 | Barely naked-eye |
| Neptune | +7.8 to +8 | Requires binoculars |

## Rise, Set, and Transit

Calculate when planets rise, set, and cross the meridian:

```python
observer = Observer.from_degrees("Los Angeles", 34.05, -118.25)
jd = jd_now()

# Jupiter visibility tonight
rise = planet_rise(Planet.JUPITER, observer, jd)
transit = planet_transit(Planet.JUPITER, observer, jd)
set_time = planet_set(Planet.JUPITER, observer, jd)

# Best viewing is around transit
if transit:
    alt = planet_altitude(Planet.JUPITER, observer, transit)
    print(f"Jupiter highest at {transit.to_datetime()}: {alt.degrees:.1f}° altitude")
```

### Circumpolar Planets

At high latitudes, planets near the celestial pole may never set:

```python
if rise is None and set_time is None:
    alt = planet_altitude(Planet.JUPITER, observer, jd)
    if alt.degrees > 0:
        print("Planet is circumpolar (always above horizon)")
    else:
        print("Planet never rises at this location")
```

## Observation Planning

### Finding the Best Time to Observe

```python
# Check which planets are well-placed tonight
positions = all_planet_positions(jd)

print("Tonight's planets:")
for planet, pos in positions.items():
    if pos.elongation.degrees > 30:  # Reasonable distance from Sun
        print(f"  {planet.value}: mag {pos.magnitude:+.1f}, "
              f"{pos.elongation.degrees:.0f}° from Sun")
```

### Outer Planet Opposition

Outer planets (Mars through Neptune) are best observed near opposition:

```python
# Check if an outer planet is near opposition
mars = planet_position(Planet.MARS, jd)
if mars.elongation.degrees > 170:
    print(f"Mars is near opposition!")
    print(f"  Distance: {mars.distance_au:.3f} AU")
    print(f"  Magnitude: {mars.magnitude:+.1f}")
```

### Inner Planet Elongation

Mercury and Venus are best observed at maximum elongation:

```python
venus = planet_position(Planet.VENUS, jd)
print(f"Venus elongation: {venus.elongation.degrees:.1f}°")
# Best viewing when elongation > 40°
```

## Verbose Mode

See the calculation steps:

```bash
astr0 planets position mars --verbose
```

```python
from astr0.verbose import VerboseContext

ctx = VerboseContext()
pos = planet_position(Planet.MARS, jd, verbose=ctx)

for step in ctx.steps:
    print(step)
```

## Algorithm Details

This module implements the planetary position algorithms from Jean Meeus' *Astronomical Algorithms*, which calculate:

1. **Heliocentric coordinates** using orbital elements
2. **Geocentric coordinates** by combining with Earth's position
3. **Apparent position** with light-time correction
4. **Magnitude** using standard phase functions

The algorithms provide accuracy suitable for observation planning. For high-precision ephemerides, dedicated services like JPL Horizons are recommended.

## See Also

- [Sun Module](sun.md) - Solar position and phenomena
- [Moon Module](moon.md) - Lunar calculations
- [Visibility Module](visibility.md) - Observation planning
- [CLI Planets Reference](cli-planets.md) - Full CLI command reference
