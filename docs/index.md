
# astr0 Documentation
---

## Contributing

Want to help make astr0 better? See our [CONTRIBUTING.md](../CONTRIBUTING.md) for how to get started, coding standards, and the contribution process. All contributions—code, docs, tests, ideas—are welcome!


> *"The cosmos is within us. We are made of star-stuff."* — Carl Sagan

Welcome to **astr0**, an educational astronomy calculation toolkit designed to help you understand the mathematics behind astronomical computations. Whether you're a student learning celestial mechanics, an amateur astronomer planning observations, or a researcher needing quick calculations, astr0 is built to be your companion.

## What Makes astr0 Different?

**Show Your Work** — Every calculation can be displayed step-by-step using `--verbose` mode. We believe that understanding *how* a result is computed is just as important as the result itself.

```bash
astr0 --verbose angles sep "10h +30d" "11h +31d"
```

This philosophy makes astr0 not just a tool, but a **learning resource**.

---

## Documentation Modules

### Core Modules (v0.1)

| Module | Description |
|--------|-------------|
| [Getting Started](getting-started.md) | Installation and your first calculations |
| [Time & Julian Dates](time.md) | Understanding astronomical time systems |
| [Coordinate Systems](coords.md) | Celestial coordinate systems and transformations |
| [Angular Calculations](angles.md) | Working with angles, separations, and position angles |
| [Astronomical Constants](constants.md) | Reference values used in calculations |

### Celestial Bodies (v0.2)

| Module | Description |
|--------|-------------|
| [Sun](sun.md) | Solar position, rise/set, twilight calculations |
| [Moon](moon.md) | Lunar position, phases, rise/set times |

### Observation Planning (v0.2)

| Module | Description |
|--------|-------------|
| [Observer](observer.md) | Location management and storage |
| [Visibility](visibility.md) | Airmass, transit, rise/set, observability |

### Reference

| Module | Description |
|--------|-------------|
| [Verbose Mode](verbose.md) | The "show your work" system |
| [CLI Reference](cli-reference.md) | Complete command-line reference |
| [Python API](api.md) | Using astr0 as a Python library |

---

## Quick Examples

### What time is it, astronomically?

```bash
astr0 time now
```

### Where is the Sun right now?

```bash
astr0 sun position
```

### When is sunrise and sunset?

```bash
astr0 sun rise --lat 51.5 --lon -0.1
astr0 sun set --lat 51.5 --lon -0.1
```

### What's the Moon phase?

```bash
astr0 moon phase
```

### When is the next full moon?

```bash
astr0 moon next full
```

### Can I observe M31 tonight?

```bash
astr0 vis report "00h42m44s" "+41d16m09s" --lat 40.7 --lon -74.0
```

### Where is that star in Galactic coordinates?

```bash
astr0 coords transform "18h36m56s -26d54m32s" --to galactic
```

### How far apart are these two objects?

```bash
astr0 angles sep "00h42m44s +41d16m09s" "01h33m51s +30d39m37s"
```

---

## Design Philosophy

1. **Precision First** — Every calculation uses full double precision
2. **Show Your Work** — Verbose mode explains every step
3. **Test Everything** — 200+ tests validate against authoritative sources
4. **Expand Gracefully** — Modular architecture for future features

---

## Version

You're reading the documentation for **astr0 v0.2.0 "Steady Tracking"**.

See the [Roadmap](../ROADMAP.md) for upcoming features including planetary ephemerides, catalog lookups, and advanced precession models.

---

*Per aspera ad astra* — Through hardships to the stars ✦
