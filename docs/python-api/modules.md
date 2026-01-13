---
id: modules
title: Core Modules
sidebar_label: Core Modules
sidebar_position: 3
---

# Core Modules

Detailed documentation for astr0's core calculation modules.

## astr0.core.time

Julian Date and time conversions.

### JulianDate

```python
from astr0.core.time import JulianDate, jd_now

# Current time
now = jd_now()

# From Julian Date number
jd = JulianDate(2451545.0)  # J2000.0

# Properties
jd.jd           # Julian Date as float
jd.mjd          # Modified Julian Date
jd.t_j2000      # Julian centuries since J2000.0
jd.to_datetime() # Convert to Python datetime
```

### Conversion Functions

```python
from astr0.core.time import utc_to_jd, jd_to_utc
from datetime import datetime

jd = utc_to_jd(datetime(2024, 6, 21, 12, 0, 0))
dt = jd_to_utc(jd)
```

## astr0.core.angles

Angular quantities and calculations.

### Angle

```python
from astr0.core.angles import Angle

# Create from degrees
a = Angle(degrees=45.5)

# Create from radians
a = Angle(radians=0.7854)

# Properties
a.degrees    # As degrees
a.radians    # As radians
a.hours      # As hours (for RA)

# Formatting
a.format_dms()   # "+45° 30′ 00.00″"
a.format_hms()   # "3h 02m 00.00s"
a.to_dms()       # Human-readable DMS
a.to_hms()       # Human-readable HMS

# Normalization
a.normalize()    # Wrap to [0, 360)
```

### Angular Separation

```python
from astr0.core.angles import angular_separation, position_angle

# Separation between two points
sep = angular_separation(ra1, dec1, ra2, dec2)

# Position angle
pa = position_angle(ra1, dec1, ra2, dec2)
```

## astr0.core.coords

Coordinate systems and transformations.

### ICRSCoord

```python
from astr0.core.coords import ICRSCoord

# Parse from string
coord = ICRSCoord.parse("18h36m56s +38d47m01s")

# From degrees
coord = ICRSCoord.from_degrees(ra=278.956, dec=38.784)

# Access components
coord.ra      # Angle
coord.dec     # Angle

# Transform
galactic = coord.to_galactic()
horizontal = coord.to_horizontal(jd, lat, lon)
```

### GalacticCoord

```python
from astr0.core.coords import GalacticCoord

coord = GalacticCoord.from_degrees(l=120.0, b=30.0)
icrs = coord.to_icrs()
```

## astr0.core.sun

Solar calculations.

```python
from astr0.core.sun import (
    sun_position,
    sunrise, sunset, solar_noon,
    solar_altitude, day_length,
    civil_twilight, nautical_twilight, astronomical_twilight,
)

# Position
sun = sun_position()
sun.ra          # Right ascension
sun.dec         # Declination
sun.distance_au # Distance in AU

# Events (require Observer)
rise = sunrise(observer)
set_time = sunset(observer)
length = day_length(observer)
```

## astr0.core.moon

Lunar calculations.

```python
from astr0.core.moon import (
    moon_position,
    moon_phase, MoonPhase,
    moonrise, moonset,
    next_phase,
)

# Position
moon = moon_position()
moon.ra
moon.dec
moon.distance_km
moon.angular_diameter

# Phase
phase = moon_phase()
phase.phase_name       # MoonPhase enum
phase.illumination     # 0-1
phase.age_days         # Days since new moon

# Next full moon
full = next_phase(MoonPhase.FULL_MOON)
```

## astr0.core.planets

Planetary calculations.

```python
from astr0.core.planets import (
    Planet,
    planet_position,
    all_planet_positions,
    planet_rise, planet_set, planet_transit,
    planet_altitude,
)

# Position
pos = planet_position(Planet.JUPITER)
pos.ra
pos.dec
pos.distance_au      # From Earth
pos.helio_distance   # From Sun
pos.magnitude
pos.elongation
pos.phase_angle

# All planets
positions = all_planet_positions()

# Events
rise = planet_rise(Planet.MARS, observer)
```

## astr0.core.observer

Observer location management.

```python
from astr0.core.observer import Observer, get_observer

# Create observer
obs = Observer.from_degrees("NYC", latitude=40.7, longitude=-74.0)

# Properties
obs.latitude   # Angle
obs.longitude  # Angle
obs.lat_deg    # Degrees
obs.lon_deg    # Degrees

# Load saved observer
home = get_observer("home")
```

## astr0.core.visibility

Visibility calculations for observing planning.

```python
from astr0.core.visibility import (
    compute_visibility,
    airmass,
    target_altitude,
    transit_time,
)

# Comprehensive visibility
vis = compute_visibility(target_coord, observer, jd)
vis.current_altitude
vis.transit_time
vis.moon_separation

# Airmass
X = airmass(altitude)
```
