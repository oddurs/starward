---
id: quickstart
title: Quick Start
sidebar_label: Quick Start
sidebar_position: 2
---

# Quick Start

Get up and running with astr0 in minutes.

## Current Time

```bash
# Show current time in multiple formats
astr0 time now
```

Output:
```
  Time Systems
  ─────────────────────────────────────────
  UTC:        2026-01-11 08:30:00
  JD:         2461051.854167
  MJD:        61051.354167
  Unix:       1768133400
```

## Planetary Positions

```bash
# All planets at once
astr0 planets all

# Specific planet
astr0 planets position mars
```

## Sun and Moon

```bash
# Solar position
astr0 sun position

# Sunrise/sunset (requires location)
astr0 sun rise --lat 40.7 --lon -74.0

# Moon phase
astr0 moon phase
```

## Coordinate Transformations

```bash
# Parse and transform coordinates
astr0 coords transform "12h30m +45d" --to galactic

# Angular separation between objects
astr0 angles sep "10h30m +20d" "11h00m +22d"
```

## Verbose Mode

Add `--verbose` or `-v` to see the math:

```bash
astr0 sun position --verbose
```

This shows step-by-step calculations with formulas and intermediate values.

## JSON Output

For scripting and integration:

```bash
astr0 planets position jupiter --json
```

## Setting Up an Observer

For rise/set calculations, save your location:

```bash
# Add a named observer
astr0 observer add "Home" 40.7128 -74.0060

# Set as default
astr0 observer default "Home"

# Now rise/set commands use your location automatically
astr0 sun rise
astr0 planets rise mars
```

## Python Library

```python
from astr0 import planet_position, Planet, jd_now

# Get Mars position
mars = planet_position(Planet.MARS)

print(f"Mars RA: {mars.ra.format_hms()}")
print(f"Mars Dec: {mars.dec.format_dms()}")
print(f"Distance: {mars.distance_au:.3f} AU")
print(f"Magnitude: {mars.magnitude:+.1f}")
```

## Next Steps

- [CLI Overview](/cli-reference/overview) — Full command reference
- [Python API](/python-api/overview) — Library documentation
- [Verbose Mode](/guides/verbose) — Understanding the calculations
