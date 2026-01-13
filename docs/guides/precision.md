---
id: precision
title: Precision Levels
sidebar_label: Precision Levels
sidebar_position: 2
---

# Precision Levels

astr0 supports multiple precision levels for different use cases.

## Available Levels

| Level | Decimals | Example | Use Case |
|-------|----------|---------|----------|
| `compact` | 2 | `45.67°` | Quick reference |
| `display` | 4 | `45.6789°` | Readable output |
| `standard` | 6 | `45.678901°` | Default, general use |
| `high` | 10 | `45.6789012345°` | Research |
| `full` | 15 | `45.678901234567890°` | Maximum precision |

## CLI Usage

```bash
# Set precision for a command
astr0 --precision high sun position

# Short form
astr0 -p full planets position mars

# With aliases
astr0 -p compact p all
```

## Python API

```python
from astr0 import get_precision, set_precision, precision_context

# Check current precision
prec = get_precision()
print(f"Decimals: {prec.decimals}")

# Set globally
set_precision('high')

# Use context manager for temporary change
with precision_context('full'):
    # High precision calculations here
    pass
# Back to previous precision
```

## PrecisionConfig

```python
from astr0.core.precision import PrecisionConfig, PrecisionLevel

# Get config for a level
config = PrecisionConfig.from_level(PrecisionLevel.HIGH)

# Properties
config.decimals     # Number of decimal places
config.format_spec  # Python format specifier
```

## When to Use Each Level

### Compact (2 decimals)
- Quick observing checks
- Rough planning
- Display in tight spaces

### Display (4 decimals)
- General observation planning
- Casual use
- Documentation examples

### Standard (6 decimals)
- Default for most calculations
- Rise/set times
- Coordinate transformations

### High (10 decimals)
- Research applications
- Comparing with catalogs
- Precise ephemerides

### Full (15 decimals)
- Maximum precision needed
- Algorithm verification
- Cross-checking sources

## Internal Precision

Note: Precision levels only affect *output formatting*. All internal calculations use full floating-point precision (64-bit IEEE 754). The precision setting determines how many decimal places are shown in results.

```python
# Internal calculation is always full precision
sun = sun_position()

# Display precision affects formatting
set_precision('compact')
print(f"RA: {sun.ra.degrees:.{get_precision().decimals}f}°")
# Output: "RA: 45.67°"

set_precision('full')
print(f"RA: {sun.ra.degrees:.{get_precision().decimals}f}°")
# Output: "RA: 45.678901234567890°"
```
