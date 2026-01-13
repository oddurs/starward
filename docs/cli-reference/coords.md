---
id: coords
title: Coordinate Commands
sidebar_label: Coordinate Commands
sidebar_position: 4
---

# Coordinate Commands

Coordinate transformations between astronomical systems.

## Commands

### `astr0 coords transform`

Transform coordinates between systems.

```bash
# ICRS to Galactic
astr0 coords transform "12h30m45s +45d30m00s" --to galactic

# Galactic to ICRS
astr0 coords transform "l=120 b=+30" --to icrs

# To horizontal (requires observer)
astr0 coords transform "12h30m +45d" --to horizontal --lat 40.7 --lon -74.0
```

### `astr0 coords parse`

Parse and display coordinate formats.

```bash
astr0 coords parse "18h36m56s +38d47m01s"
```

## Supported Systems

| System | Description | Format |
|--------|-------------|--------|
| **ICRS** | Equatorial (RA/Dec) | `12h30m +45d` |
| **Galactic** | Galactic (l/b) | `l=120 b=+30` |
| **Horizontal** | Alt/Az | Requires observer |

## Coordinate Formats

astr0 accepts flexible input formats:

```bash
# Sexagesimal
"12h30m45.6s +45d30m15s"
"12:30:45.6 +45:30:15"

# Decimal degrees
"187.5 +45.5"

# Mixed
"12h30m +45.5"
```

## Examples

```bash
# Vega's galactic coordinates
astr0 coords transform "18h36m56s +38d47m01s" --to galactic

# M31 altitude from New York
astr0 coords transform "00h42m44s +41d16m09s" --to horizontal \
  --lat 40.7 --lon -74.0

# Verbose transformation
astr0 coords transform "12h +45d" --to galactic --verbose
```

## Python API

```python
from astr0 import ICRSCoord, GalacticCoord

# Parse coordinates
vega = ICRSCoord.parse("18h36m56s +38d47m01s")

# Transform to galactic
galactic = vega.to_galactic()
print(f"l = {galactic.l.degrees:.2f}°")
print(f"b = {galactic.b.degrees:.2f}°")

# Create from degrees
m31 = ICRSCoord.from_degrees(ra=10.684, dec=41.269)
```
