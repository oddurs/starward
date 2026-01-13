---
id: verbose
title: Verbose Mode
sidebar_label: Verbose Mode
sidebar_position: 1
---

# Verbose Mode

astr0's verbose mode shows the mathematics behind every calculation — perfect for learning, verification, and debugging.

## CLI Usage

Add `--verbose` or `-v` to any command:

```bash
astr0 sun position --verbose
astr0 planets position mars -v
```

## What Gets Shown

Verbose mode displays:

- **Input parameters** — Julian Date, observer location
- **Intermediate values** — Mean anomaly, eccentricity, etc.
- **Formulas** — The actual equations being computed
- **Step-by-step progression** — How values build on each other
- **Final results** — With full precision

## Python API

```python
from astr0.verbose import VerboseContext
from astr0.core.sun import sun_position

# Create a verbose context
vctx = VerboseContext()

# Pass it to any calculation
sun = sun_position(verbose=vctx)

# Get formatted output
print(vctx.format_steps())

# Or as a dictionary (for JSON output)
data = vctx.to_dict()
```

## Educational Use

Verbose mode is invaluable for:

1. **Learning** — See how astronomical algorithms work
2. **Teaching** — Demonstrate calculations step by step
3. **Verification** — Cross-check results with other sources
4. **Debugging** — Find where calculations diverge

## Algorithm References

astr0 calculations follow algorithms from:

- **Meeus, Jean** — *Astronomical Algorithms*, 2nd Edition
- **USNO** — United States Naval Observatory data
- **JPL** — Jet Propulsion Laboratory ephemerides
