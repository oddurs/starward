---
id: observer
title: Observer Module
sidebar_label: Observer
sidebar_position: 7
---

# Observer Module

The Observer module manages observing locations with support for persistent storage, timezone handling, and seamless integration with all position-dependent calculations.

## Overview

Your position on Earth fundamentally shapes what you see in the sky. The Observer module provides:

- Location management with latitude, longitude, and elevation
- Named observer profiles stored in TOML configuration
- Timezone support for local time conversions
- Integration with rise/set, transit, and visibility calculations

## Quick Start

### CLI Usage

```bash
# Add a new observer location
astr0 observer add "Backyard" 40.7128 -74.0060 --elevation 10 --timezone "America/New_York"

# List saved observers
astr0 observer list

# Show observer details
astr0 observer show "Backyard"

# Set default observer
astr0 observer default "Backyard"

# Remove an observer
astr0 observer remove "Backyard"
```

### Python API

```python
from astr0.core.observer import Observer, ObserverManager

# Create an observer directly
greenwich = Observer.from_degrees(
    name="Greenwich",
    latitude=51.4772,
    longitude=-0.0005,
    elevation=62.0,
    timezone="Europe/London"
)

# Use in calculations
from astr0.core.sun import sunrise, sunset
from astr0.core.time import jd_now

jd = jd_now()
rise = sunrise(greenwich, jd)
print(f"Sunrise at {greenwich.name}: {rise.to_datetime()}")
```

## Creating Observers

### From Decimal Degrees

```python
# Northern hemisphere, eastern longitude
tokyo = Observer.from_degrees(
    name="Tokyo",
    latitude=35.6762,
    longitude=139.6503,
    elevation=40.0,
    timezone="Asia/Tokyo"
)

# Southern hemisphere, western longitude
paranal = Observer.from_degrees(
    name="Paranal",
    latitude=-24.6253,
    longitude=-70.4043,
    elevation=2635.0,
    timezone="America/Santiago"
)
```

### Coordinate Conventions

| Parameter | Range | Convention |
|-----------|-------|------------|
| Latitude | -90° to +90° | + = North, - = South |
| Longitude | -180° to +180° | + = East, - = West |
| Elevation | ≥0 meters | Above sea level |

## Observer Properties

An `Observer` object provides:

```python
obs = Observer.from_degrees("Test", 40.0, -74.0, elevation=100.0)

# Access properties
print(obs.name)        # "Test"
print(obs.lat_deg)     # 40.0
print(obs.lon_deg)     # -74.0
print(obs.elevation)   # 100.0
print(obs.timezone)    # None or timezone string

# As Angle objects (for calculations)
print(obs.latitude)    # Angle object
print(obs.longitude)   # Angle object
```

## Persistent Storage

### Observer Manager

The `ObserverManager` handles saving and loading observer profiles:

```python
from astr0.core.observer import ObserverManager

# Get the manager (creates ~/.astr0/ if needed)
manager = ObserverManager()

# Add an observer
obs = Observer.from_degrees("Home", 40.0, -74.0)
manager.add(obs)

# List all observers
for name in manager.list_names():
    print(name)

# Get an observer by name
home = manager.get("Home")

# Set default observer
manager.set_default("Home")

# Get default observer
default = manager.get_default()

# Remove an observer
manager.remove("Home")
```

### Configuration File

Observers are stored in `~/.astr0/observers.toml`:

```toml
# Default observer
default = "Home"

[observers.Home]
name = "Home"
latitude = 40.0
longitude = -74.0
elevation = 100.0
timezone = "America/New_York"

[observers.MaunaKea]
name = "Mauna Kea"
latitude = 19.8208
longitude = -155.4681
elevation = 4207.0
timezone = "Pacific/Honolulu"
```

## Well-Known Observatories

Some famous observatory locations:

```python
# Major observatories
mauna_kea = Observer.from_degrees(
    "Mauna Kea", 19.8208, -155.4681, 4207.0, "Pacific/Honolulu"
)

paranal = Observer.from_degrees(
    "Paranal (VLT)", -24.6253, -70.4043, 2635.0, "America/Santiago"
)

la_palma = Observer.from_degrees(
    "Roque de los Muchachos", 28.7569, -17.8925, 2396.0, "Atlantic/Canary"
)

greenwich = Observer.from_degrees(
    "Royal Observatory Greenwich", 51.4772, -0.0005, 62.0, "Europe/London"
)
```

## Integration with Other Modules

### Sun Module

```python
from astr0.core.sun import sunrise, sunset, solar_noon

rise = sunrise(observer, jd)
set_t = sunset(observer, jd)
noon = solar_noon(observer, jd)
```

### Moon Module

```python
from astr0.core.moon import moonrise, moonset, moon_altitude

rise = moonrise(observer, jd)
alt = moon_altitude(observer, jd)
```

### Visibility Module

```python
from astr0.core.visibility import (
    target_altitude, transit_time, compute_visibility
)

alt = target_altitude(target_coord, observer, jd)
transit = transit_time(target_coord, observer, jd)
vis = compute_visibility(target_coord, observer, jd)
```

### Coordinate Transformations

```python
from astr0.core.coords import HorizontalCoord

# ICRS to horizontal (requires observer location)
horiz = HorizontalCoord.from_icrs(
    icrs_coord,
    jd=jd,
    lat=observer.latitude,
    lon=observer.longitude
)
```

## Elevation Effects

Higher elevation affects:

1. **Horizon**: Geometric horizon is depressed below eye level
2. **Refraction**: Slightly different atmospheric path
3. **Airmass**: Thinner atmosphere means lower airmass at same zenith angle

```python
# Observer at sea level vs mountain
sea_level = Observer.from_degrees("Beach", 40.0, -74.0, elevation=0)
mountain = Observer.from_degrees("Summit", 40.0, -74.0, elevation=3000)

# Rise/set times will differ slightly
```

## Timezone Handling

Timezones use IANA timezone names (e.g., "America/New_York"):

```python
obs = Observer.from_degrees(
    "New York",
    40.7128, -74.0060,
    timezone="America/New_York"
)

# All internal times are UTC/JD
# Use timezone for display purposes
```

## Serialization

Convert to dictionary for storage or transmission:

```python
# To dictionary
d = observer.to_dict()
# {
#     'name': 'Home',
#     'latitude': 40.0,
#     'longitude': -74.0,
#     'elevation': 100.0,
#     'timezone': 'America/New_York'
# }

# From dictionary
obs = Observer.from_dict(d)
```

## CLI Reference

```bash
# Add observer
astr0 observer add NAME LAT LON [--elevation M] [--timezone TZ]

# List observers
astr0 observer list [--json]

# Show observer
astr0 observer show NAME [--json]

# Set default
astr0 observer default NAME

# Remove observer
astr0 observer remove NAME
```

## See Also

- [Sun Module](/module-guides/sun) - Uses observer for rise/set
- [Moon Module](/module-guides/moon) - Uses observer for rise/set
- [Visibility Module](/module-guides/visibility) - Uses observer for all calculations
