---
id: overview
title: Python API Overview
sidebar_label: Overview
sidebar_position: 1
description: Use astr0 as a Python library for astronomical calculations including time, coordinates, sun, moon, and planets.
---

# Python API Overview

astr0 can be used as a Python library for astronomical calculations.

## Installation

```bash
pip install astr0
```

## Quick Example

```python
from astr0 import (
    JulianDate, jd_now,
    ICRSCoord, Angle,
    Planet, planet_position,
)

# Current Julian Date
now = jd_now()
print(f"JD: {now.jd}")

# Parse coordinates
vega = ICRSCoord.parse("18h36m56s +38d47m01s")
print(f"Vega: RA={vega.ra.hours:.2f}h, Dec={vega.dec.degrees:.2f}°")

# Planetary position
mars = planet_position(Planet.MARS)
print(f"Mars magnitude: {mars.magnitude:+.1f}")
```

## Main Exports

The top-level `astr0` module exports commonly used classes:

```python
from astr0 import (
    # Time
    JulianDate,
    jd_now,
    utc_to_jd,
    jd_to_utc,

    # Angles
    Angle,
    angular_separation,
    position_angle,

    # Coordinates
    ICRSCoord,
    GalacticCoord,
    HorizontalCoord,

    # Planets
    Planet,
    PlanetPosition,
    planet_position,
    all_planet_positions,

    # Constants
    CONSTANTS,

    # Precision
    get_precision,
    set_precision,
)
```

## Core Modules

For more specialized functions, import from `astr0.core`:

```python
from astr0.core.sun import sun_position, sunrise, sunset
from astr0.core.moon import moon_position, moon_phase
from astr0.core.planets import planet_rise, planet_set
from astr0.core.observer import Observer
from astr0.core.visibility import compute_visibility
```

## Verbose Mode

Enable step-by-step calculation output:

```python
from astr0.verbose import VerboseContext
from astr0.core.sun import sun_position

# Create verbose context
vctx = VerboseContext()

# Run calculation with verbose output
sun = sun_position(verbose=vctx)

# Print the steps
print(vctx.format_steps())
```

## Detailed Reference

- [Core Modules](/python-api/modules) — Detailed module documentation
