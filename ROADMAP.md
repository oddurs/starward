# astr0 — Astronomy Calculation Toolkit

> *"Per aspera ad astra"* — Through hardships to the stars

A professional astronomy calculation toolkit with a soul. Built for astronomers, astrophysicists, and curious stargazers who appreciate precision, transparency, and the occasional cosmic pun.

---

## 🌟 Philosophy

- **Precision First**: Every calculation traceable, every assumption explicit
- **Show Your Work**: Verbose mode that would make your physics professor proud  
- **Modular by Design**: Each module stands alone, plays well with others
- **Test Everything**: If it's not tested, it doesn't exist
- **Expand Gracefully**: Architecture that welcomes new features like old friends

---

## 📋 v0.1 — "First Light" ✅

The foundational release. Core infrastructure and essential calculations.

### Core Modules

| Module | Description | Status |
|--------|-------------|--------|
| `time` | Julian dates, MJD, LST, epoch conversions | ✅ |
| `coords` | Coordinate transformations (ICRS, AltAz, Galactic, Ecliptic) | ✅ |
| `angles` | Angular separations, position angles, formatting | ✅ |
| `constants` | Astronomical constants with references | ✅ |

### Infrastructure

- [x] CLI framework with subcommands
- [x] Verbose output system ("show your work")
- [x] Unit test suite with >90% coverage target
- [x] Input validation and error handling
- [x] JSON output option

### CLI Commands (v0.1)

```bash
astr0 time now                    # Current time in all formats
astr0 time convert <value>        # Convert between time systems
astr0 coord convert <coords>      # Transform coordinates
astr0 angle sep <c1> <c2>         # Angular separation
astr0 --verbose <command>         # Show calculation steps
astr0 --output json <command>     # JSON output
```

---

## 🚀 v0.2 — "Steady Tracking" ✅

Position calculations and solar system awareness.

### New Modules

| Module | Description | Status |
|--------|-------------|--------|
| `sun` | Solar position, sunrise/sunset, twilight | ✅ |
| `moon` | Lunar position, phases, illumination | ✅ |
| `observer` | Observer location management, horizon | ✅ |
| `visibility` | Object visibility, optimal viewing times | ✅ |

### Enhancements

- [x] Observer profile saving (~/.astr0/observers.toml)
- [x] LaTeX output option
- [x] Rise/set/transit calculations
- [x] Airmass calculations
- [x] Twilight calculations (civil, nautical, astronomical)
- [x] Moon phase prediction

### CLI Commands (v0.2)

```bash
# Sun commands
astr0 sun position                 # Current solar position
astr0 sun rise --lat 51.5 --lon -0.1
astr0 sun set --lat 51.5 --lon -0.1
astr0 sun twilight astronomical --lat 51.5 --lon -0.1

# Moon commands
astr0 moon position                # Current lunar position
astr0 moon phase                   # Current phase
astr0 moon next full               # Next full moon

# Observer commands
astr0 observer add "Home" 40.7 -74.0
astr0 observer list
astr0 observer default "Home"

# Visibility commands
astr0 vis altitude "00h42m44s" "+41d16m09s" --lat 40.7 --lon -74.0
astr0 vis transit "00h42m44s" "+41d16m09s" --lat 40.7 --lon -74.0
astr0 vis airmass "00h42m44s" "+41d16m09s" --lat 40.7 --lon -74.0
```

---

## 🪐 v0.3 — "Planetary Motion" 🔜

Solar system ephemerides and orbital mechanics.

### New Modules

| Module | Description |
|--------|-------------|
| `planets` | Planetary positions (VSOP87) |
| `orbits` | Orbital elements, Kepler's laws |
| `conjunctions` | Planetary conjunctions, oppositions |

### Enhancements

- Ephemeris generation (tabular output)
- Orbital diagrams (ASCII/SVG)
- Two-line element (TLE) parsing for satellites

---

## 🔭 v0.4 — "Deep Sky"

Catalogs and object databases.

### New Modules

| Module | Description |
|--------|-------------|
| `catalogs` | NGC, IC, Messier, HD lookups |
| `stars` | Stellar parameters, spectral types |
| `dso` | Deep sky object information |
| `finder` | Object finder by criteria |

### Enhancements

- Local catalog caching
- Custom object lists
- Observation planning

---

## 🌌 v0.5 — "Cosmological"

Extragalactic and cosmological calculations.

### New Modules

| Module | Description |
|--------|-------------|
| `cosmo` | Cosmological distances, redshift |
| `magnitudes` | Absolute/apparent, extinction |
| `luminosity` | Flux, luminosity calculations |

### Enhancements

- Multiple cosmology models
- K-corrections
- Distance ladder calculations

---

## 🛸 v0.6 — "Observatory Ready"

Professional observatory support.

### New Modules

| Module | Description |
|--------|-------------|
| `optics` | Telescope/camera calculations |
| `imaging` | FOV, pixel scale, SNR |
| `scheduler` | Observation scheduling |
| `weather` | Seeing, transparency integration |

### Enhancements

- FITS header parsing
- Exposure time calculator
- Mosaic planning

---

## 🎨 Future Horizons (v1.0+)

- **Python API**: Import astr0 as a library
- **Web interface**: Browser-based calculator
- **Plugin system**: Community extensions
- **GPU acceleration**: For heavy ephemeris work
- **Real-time feeds**: Live satellite tracking, alerts
- **Interactive mode**: REPL with history

---

## 🏗️ Architecture Principles

```
astr0/
├── src/astr0/
│   ├── cli/           # Click-based CLI commands
│   ├── core/          # Core calculation modules
│   ├── output/        # Formatters (plain, json, latex)
│   ├── verbose/       # "Show your work" engine
│   └── utils/         # Shared utilities
├── tests/             # Pytest test suite
│   ├── unit/          # Unit tests per module
│   ├── integration/   # CLI integration tests
│   └── fixtures/      # Test data
└── docs/              # Documentation
```

### Key Design Decisions

1. **Pure Python Core**: No compiled dependencies for portability
2. **Lazy Imports**: Fast CLI startup, load modules on demand
3. **Immutable Data**: Calculation results are immutable dataclasses
4. **Verbose Registry**: Calculations register their steps automatically
5. **Output Agnostic**: Core returns data, formatters handle display

---

## 📊 Testing Strategy

- **Unit Tests**: Every function, every edge case
- **Property Tests**: Hypothesis for numerical stability
- **Golden Tests**: Known values from authoritative sources (USNO, JPL)
- **Roundtrip Tests**: Transform → inverse transform = identity
- **CLI Tests**: Every command, every flag

### Test Suite Structure (v0.2)

```
tests/
├── conftest.py         # Shared fixtures and markers
├── core/               # Core module tests
│   ├── test_angles.py
│   ├── test_coords.py
│   ├── test_time.py
│   ├── test_constants.py
│   ├── test_sun.py
│   ├── test_moon.py
│   ├── test_observer.py
│   └── test_visibility.py
├── cli/                # CLI integration tests
│   └── test_commands.py
└── output/             # Formatter tests
    └── test_formatters.py
```

**Current Status**: 200+ tests, validated against USNO, JPL, and Meeus

---

## 🌠 The Name

**astr0** — Where astronomy meets code. The zero represents:
- The origin point of our coordinate systems
- The null hypothesis we test against
- The first index (we're programmers, after all)
- ∅ The empty set of bugs we aspire to

---

## 📈 Version History

| Version | Codename | Status | Highlights |
|---------|----------|--------|------------|
| v0.1 | First Light | ✅ Complete | Time, coords, angles, constants |
| v0.2 | Steady Tracking | ✅ Complete | Sun, moon, observer, visibility |
| v0.3 | Planetary Motion | 🔜 Next | Planets, orbits, conjunctions |
| v0.4 | Deep Sky | 📋 Planned | Catalogs, DSOs, star data |
| v0.5 | Cosmological | 📋 Planned | Redshift, distances, cosmology |
| v0.6 | Observatory Ready | 📋 Planned | Optics, imaging, scheduling |

---

*Built with 🔭 and ☕ for those who look up*
