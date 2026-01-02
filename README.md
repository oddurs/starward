# astr0 🔭

> A professional astronomy calculation toolkit with a soul

```
    *  .  *       .   *   .    *    .  *
  .    *    Per aspera ad astra    .    *
    .    *  .       .   *   .   *    .
```

## Installation

```bash
pip install astr0
```

Or for development:

```bash
git clone https://github.com/astr0/astr0
cd astr0
pip install -e ".[dev]"
```

## Quick Start

```bash
# What time is it... astronomically speaking?
astr0 time now

# Convert a Julian Date
astr0 time convert 2460000.5

# Transform coordinates from ICRS to Galactic
astr0 coords transform "12h30m00s +45d00m00s" --to galactic

# Angular separation between two objects
astr0 angles sep "10h30m +30d" "10h35m +31d"

# Show your work (verbose mode)
astr0 --verbose coords transform "18h36m56.3s -26d54m32s" --to altaz --lat 34.05 --lon -118.25
```

## Features

- **Time Conversions**: Julian Date, Modified JD, Local Sidereal Time
- **Coordinate Transforms**: ICRS, Galactic, Ecliptic, Horizontal (Alt/Az)
- **Angular Calculations**: Separations, position angles
- **Verbose Mode**: See every step of every calculation
- **Multiple Outputs**: Plain text, JSON (LaTeX coming soon)

## Philosophy

1. **Precision First** — Every calculation is traceable
2. **Show Your Work** — `--verbose` mode explains everything
3. **Test Everything** — Validated against authoritative sources
4. **Expand Gracefully** — Modular architecture

## Documentation

See [ROADMAP.md](ROADMAP.md) for the full vision and upcoming features.

## License

MIT © astr0 contributors

---

*"The cosmos is within us. We are made of star-stuff."* — Carl Sagan
