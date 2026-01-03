<p align="center">
  <img src="docs/assets/logo.png" alt="astr0" width="200">
</p>

<h1 align="center">astr0</h1>

<p align="center">
  <strong>An Educational Astronomy Calculation Toolkit</strong>
</p>

<p align="center">
  <em>Show your work. Understand the cosmos.</em>
</p>

<p align="center">
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#features">Features</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#philosophy">Philosophy</a>
</p>

---

## The Problem

Most astronomy software treats calculations as black boxes. You input coordinates, out come numbers. But *how* did it compute that Julian Date? *Why* does the coordinate transformation work that way?

## The Solution

**astr0** is different. Every calculation can show its work with `--verbose` mode, transforming opaque computations into transparent learning opportunities. Whether you're a student of celestial mechanics, an amateur astronomer planning observations, or a researcher who wants to understand their tools, astr0 is built to illuminate.

```
$ astr0 --verbose angle sep "10h00m +45d" "10h30m +46d"

┌─────────────────────────────────────────────────────────┐
│  Angular Separation Calculation                         │
├─────────────────────────────────────────────────────────┤
│  Point 1: RA = 10h 00m 00.00s, Dec = +45° 00′ 00.0″    │
│  Point 2: RA = 10h 30m 00.00s, Dec = +46° 00′ 00.0″    │
├─────────────────────────────────────────────────────────┤
│  Step 1: Convert to radians                             │
│    α₁ = 2.617993878 rad, δ₁ = 0.785398163 rad          │
│    α₂ = 2.748893572 rad, δ₂ = 0.802851456 rad          │
│                                                         │
│  Step 2: Apply Vincenty formula                         │
│    Δα = 0.130899694 rad                                │
│    sin(δ₁) = 0.707107, cos(δ₁) = 0.707107              │
│    sin(δ₂) = 0.719340, cos(δ₂) = 0.694658              │
│                                                         │
│  Step 3: Calculate separation                           │
│    θ = 5.277° = 5° 16′ 37.2″                           │
└─────────────────────────────────────────────────────────┘

  Angular Separation: 5° 16′ 37.2″
```

---

## Installation

```bash
pip install astr0
```

**Requirements**: Python 3.9+

For development:
```bash
git clone https://github.com/yourusername/astr0.git
cd astr0
pip install -e ".[dev]"
```

---

## Quick Start

### Time

```bash
# Current astronomical time
astr0 time now

# Convert Julian Date
astr0 time convert 2451545.0

# Sidereal time at longitude
astr0 time lst 2460000.5 -74.0
```

### Sun & Moon

```bash
# Solar position
astr0 sun position

# Sunrise and sunset
astr0 sun rise --lat 51.5 --lon -0.1
astr0 sun set --lat 51.5 --lon -0.1

# Twilight times
astr0 sun twilight astronomical --lat 51.5 --lon -0.1

# Current moon phase
astr0 moon phase

# Next full moon
astr0 moon next full

# Moonrise
astr0 moon rise --lat 40.7 --lon -74.0
```

### Coordinates

```bash
# Transform between coordinate systems
astr0 coord convert "18h36m56s +38d47m01s" galactic

# Angular separation
astr0 angle sep "00h42m44s +41d16m09s" "01h33m51s +30d39m37s"
```

### Visibility Planning

```bash
# Target altitude now
astr0 vis altitude "00h42m44s" "+41d16m09s" --lat 40.7 --lon -74.0

# Transit time
astr0 vis transit "00h42m44s" "+41d16m09s" --lat 40.7 --lon -74.0

# Airmass
astr0 vis airmass "00h42m44s" "+41d16m09s" --lat 40.7 --lon -74.0
```

### Observer Management

```bash
# Save your location
astr0 observer add "Home" 40.7128 -74.0060 --timezone "America/New_York"

# Set as default
astr0 observer default "Home"

# List saved observers
astr0 observer list
```

### Constants

```bash
# List all constants
astr0 const list

# Search constants
astr0 const search solar
```

---

## Features

### ✦ v0.1 "First Light"

| Module | Capabilities |
|--------|-------------|
| **Time** | Julian Date ↔ Calendar, GMST, LST, MJD |
| **Angles** | Parse/format DMS/HMS, separation, position angle |
| **Coordinates** | ICRS, Galactic, Horizontal transforms |
| **Constants** | 30+ IAU/CODATA constants with uncertainties |

### ✦ v0.2 "Steady Tracking"

| Module | Capabilities |
|--------|-------------|
| **Sun** | Position, rise/set, twilight (civil/nautical/astronomical), equation of time |
| **Moon** | Position, phase, illumination, rise/set, next phase prediction |
| **Observer** | Location management, TOML persistence, timezone support |
| **Visibility** | Airmass, transit, rise/set, moon separation, night detection |

### Coming Soon

- **v0.3**: Planets (Mercury–Neptune), ecliptic coordinates
- **v0.4**: Catalog lookups (Messier, NGC, Hipparcos)
- **v0.5**: IAU 2006 precession/nutation, aberration

---

## Python API

Use astr0 as a library in your Python projects:

```python
from astr0.core.time import JulianDate, jd_now
from astr0.core.coords import ICRSCoord
from astr0.core.angles import Angle, angular_separation
from astr0.core.sun import sun_position, sunrise, sunset
from astr0.core.moon import moon_phase, next_phase, MoonPhase
from astr0.core.observer import Observer
from astr0.core.visibility import airmass, target_altitude, compute_visibility

# Time
jd = jd_now()
j2000 = JulianDate.j2000()
past = JulianDate.from_calendar(1969, 7, 20, 20, 17, 0)

# Coordinates
vega = ICRSCoord.parse("18h36m56.3s +38d47m01s")
m31 = ICRSCoord.from_degrees(10.684, 41.269)
galactic = vega.to_galactic()

# Angles
sep = angular_separation(vega.ra, vega.dec, m31.ra, m31.dec)
angle = Angle.parse("45d30m15.5s")

# Sun
pos = sun_position(jd)
greenwich = Observer.from_degrees("Greenwich", 51.4772, -0.0005)
rise = sunrise(greenwich, jd)

# Moon
phase = moon_phase(jd)
print(f"Moon: {phase.name}, {phase.percent_illuminated:.0f}% illuminated")
next_full = next_phase(jd, MoonPhase.FULL_MOON)

# Visibility
alt = target_altitude(m31, greenwich, jd)
X = airmass(alt)
vis = compute_visibility(m31, greenwich, jd)
```

---

## Philosophy

### 1. **Transparency Over Magic**

Every function can explain itself. Use verbose mode to see the mathematics:

```python
from astr0.verbose import VerboseContext

ctx = VerboseContext()
result = angular_separation(ra1, dec1, ra2, dec2, verbose=ctx)

for step in ctx.steps:
    print(step)
```

### 2. **Education First**

astr0 is designed for learning. The code is documented, the algorithms are cited, and the output explains itself.

### 3. **Precision Matters**

- Full IEEE 754 double precision throughout
- Tested against authoritative sources (USNO, JPL, IAU)
- Explicit uncertainty handling for constants

### 4. **Progressive Complexity**

Start simple, go deep when needed:

```bash
# Simple: just the answer
astr0 sun rise --lat 51.5 --lon -0.1

# Intermediate: JSON for scripting
astr0 sun rise --lat 51.5 --lon -0.1 --json

# Advanced: show all work
astr0 sun rise --lat 51.5 --lon -0.1 --verbose
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [Getting Started](docs/getting-started.md) | Installation and first steps |
| [Time Module](docs/time.md) | Julian dates and sidereal time |
| [Coordinates](docs/coords.md) | Celestial coordinate systems |
| [Angles](docs/angles.md) | Angular calculations |
| [Sun](docs/sun.md) | Solar position and phenomena |
| [Moon](docs/moon.md) | Lunar position and phases |
| [Observer](docs/observer.md) | Location management |
| [Visibility](docs/visibility.md) | Observation planning |
| [Constants](docs/constants.md) | Astronomical constants |
| [CLI Reference](docs/cli-reference.md) | Complete command reference |
| [API Reference](docs/api.md) | Python library documentation |

---

## Command Shortcuts

For speed, astr0 supports command aliases:

| Full Command | Shortcut |
|--------------|----------|
| `astr0 time` | `astr0 t` |
| `astr0 angle` | `astr0 a` |
| `astr0 coord` | `astr0 c` |
| `astr0 const` | `astr0 k` |
| `astr0 sun` | `astr0 s` |
| `astr0 moon` | `astr0 m` |
| `astr0 observer` | `astr0 o` |
| `astr0 vis` | `astr0 v` |

---

## Output Formats

```bash
# Human-readable (default)
astr0 time now

# JSON for scripting
astr0 time now --json

# LaTeX for publications
astr0 coord convert "18h36m56s +38d47m01s" galactic --latex
```

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=astr0

# Run specific module tests
pytest tests/core/test_sun.py

# Run only fast tests
pytest -m "not slow"
```

200+ tests validate calculations against authoritative sources including:
- US Naval Observatory
- JPL Horizons
- IAU SOFA library
- Astronomical Algorithms (Meeus)

---

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas especially seeking help:
- Higher-precision algorithms (VSOP87, ELP/MPP02)
- Planetary ephemerides
- Additional coordinate systems
- Documentation improvements
- Test coverage expansion

---

## Acknowledgments

astr0 builds upon decades of astronomical research. Key references:

- Meeus, Jean. *Astronomical Algorithms* (2nd ed.)
- Urban & Seidelmann. *Explanatory Supplement to the Astronomical Almanac* (3rd ed.)
- IAU SOFA Collection
- JPL Solar System Dynamics

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center">
  <em>Per aspera ad astra</em> ✦ <em>Through hardships to the stars</em>
</p>

<p align="center">
  Made with 🔭 for the curious
</p>
