---
id: sun
title: Sun Module
sidebar_label: Sun
sidebar_position: 4
---

# Sun Module

The Sun module provides calculations for solar position, rise/set times, twilight, and related phenomena. These are fundamental for planning observations and understanding seasonal changes.

## Overview

The Sun is not only our nearest star but also the fundamental timekeeping reference for astronomy. This module implements low-precision algorithms suitable for:

- Sunrise and sunset calculations
- Twilight (civil, nautical, astronomical)
- Solar noon determination
- Day length calculation
- Equation of time

**Accuracy**: Position ~0.01° in ecliptic longitude, times within ~1 minute.

## Quick Start

### CLI Usage

```bash
# Current solar position
astr0 sun position

# Sunrise for today at a location
astr0 sun rise --lat 51.5 --lon -0.1

# Sunset
astr0 sun set --lat 51.5 --lon -0.1

# Civil twilight times
astr0 sun twilight civil --lat 51.5 --lon -0.1

# Solar altitude at current time
astr0 sun altitude --lat 51.5 --lon -0.1
```

### Python API

```python
from astr0.core.sun import (
    sun_position, sunrise, sunset, solar_noon,
    civil_twilight, nautical_twilight, astronomical_twilight,
    solar_altitude, day_length
)
from astr0.core.observer import Observer
from astr0.core.time import jd_now

# Create an observer
greenwich = Observer.from_degrees("Greenwich", 51.4772, -0.0005)

# Get current solar position
jd = jd_now()
pos = sun_position(jd)
print(f"Sun RA: {pos.ra.hours:.2f}h, Dec: {pos.dec.degrees:.1f}°")
print(f"Distance: {pos.distance_au:.4f} AU")

# Sunrise and sunset
rise = sunrise(greenwich, jd)
set_t = sunset(greenwich, jd)
print(f"Sunrise: {rise.to_datetime()}")
print(f"Sunset: {set_t.to_datetime()}")

# Twilight times
morning_twi, evening_twi = civil_twilight(greenwich, jd)

# Day length
hours = day_length(greenwich, jd)
print(f"Day length: {hours:.1f} hours")
```

## Solar Position

The `sun_position()` function returns a `SunPosition` object containing:

| Field | Description |
|-------|-------------|
| `longitude` | Ecliptic longitude (Angle) |
| `latitude` | Ecliptic latitude (Angle, always ~0) |
| `ra` | Right Ascension (Angle) |
| `dec` | Declination (Angle) |
| `distance_au` | Distance in AU |
| `equation_of_time` | Equation of time in minutes |

### Equation of Time

The equation of time (EoT) is the difference between apparent solar time and mean solar time. It varies from about -14 minutes to +16 minutes throughout the year.

```python
pos = sun_position(jd)
eot = pos.equation_of_time  # in minutes
```

## Sunrise and Sunset

Standard definitions use the moment when the Sun's upper limb touches the horizon, accounting for atmospheric refraction.

```python
# Default: standard refraction (34 arcminutes)
rise = sunrise(observer, jd)

# Custom horizon (e.g., elevated observer)
rise = sunrise(observer, jd, horizon=-0.5)  # 0.5° below geometric horizon
```

### Edge Cases

- **Polar day**: No sunrise/sunset during midnight sun (returns `None`)
- **Polar night**: No sunrise/sunset during polar night (returns `None`)

## Twilight

Three types of twilight are defined by how far the Sun is below the horizon:

| Type | Sun altitude | Description |
|------|-------------|-------------|
| Civil | 0° to -6° | Enough light for outdoor activities |
| Nautical | -6° to -12° | Horizon visible at sea |
| Astronomical | -12° to -18° | Sky fully dark for observations |

```python
# Each returns (morning_twilight, evening_twilight)
civil_morning, civil_evening = civil_twilight(observer, jd)
naut_morning, naut_evening = nautical_twilight(observer, jd)
astro_morning, astro_evening = astronomical_twilight(observer, jd)
```

## Solar Altitude

Calculate the Sun's altitude at any time:

```python
alt = solar_altitude(observer, jd)
print(f"Sun altitude: {alt.degrees:.1f}°")

# Check if Sun is up
if alt.degrees > 0:
    print("Daytime")
elif alt.degrees > -18:
    print("Twilight")
else:
    print("Night")
```

## Solar Noon

Solar noon is when the Sun crosses the local meridian (highest point):

```python
noon = solar_noon(observer, jd)
max_alt = solar_altitude(observer, noon)
print(f"Solar noon: {noon.to_datetime()}")
print(f"Maximum altitude: {max_alt.degrees:.1f}°")
```

## Day Length

Day length varies with latitude and time of year:

```python
# Hours of daylight
hours = day_length(observer, jd)

# Near summer solstice at Arctic Circle
arctic = Observer.from_degrees("Arctic", 66.5, 0)
summer_jd = JulianDate.from_calendar(2024, 6, 21, 12, 0, 0)
hours = day_length(arctic, summer_jd)
# Result: ~24 hours (midnight sun)
```

## Seasonal Variations

Solar declination varies from -23.4° (winter solstice) to +23.4° (summer solstice):

```python
from astr0.core.time import JulianDate

# Check solar declination throughout the year
for month in range(1, 13):
    jd = JulianDate.from_calendar(2024, month, 15, 12, 0, 0)
    pos = sun_position(jd)
    print(f"Month {month:2d}: Dec = {pos.dec.degrees:+.1f}°")
```

## Verbose Mode

Enable verbose mode to see calculation steps:

```python
from astr0.verbose import VerboseContext

ctx = VerboseContext()
pos = sun_position(jd, verbose=ctx)

for step in ctx.steps:
    print(step)
```

## Algorithm Details

This module uses the low-precision solar position algorithm from Jean Meeus' *Astronomical Algorithms*. The algorithm accounts for:

- Mean solar longitude
- Mean anomaly
- Equation of center (elliptical orbit)
- Obliquity of the ecliptic (axial tilt)
- Nutation (simplified)

For higher precision requirements, consider the VSOP87 theory (not yet implemented).

## See Also

- [Moon Module](/module-guides/moon) - Lunar calculations
- [Visibility Module](/module-guides/visibility) - Observation planning
- [Observer Module](/module-guides/observer) - Location management
