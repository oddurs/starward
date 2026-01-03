# CLI Reference

Complete reference for all astr0 command-line commands.

---

## Global Options

These options apply to all commands and must appear **before** the subcommand:

| Option | Alias | Description |
|--------|-------|-------------|
| `--verbose` | `-v` | Show calculation steps |
| `--output` | `-o` | Output format: `plain` (default), `json`, or `latex` |
| `--json` | | Shortcut for `--output json` |
| `--precision` | `-p` | Output precision level (see below) |
| `--version` | | Show version and exit |
| `--help` | | Show help and exit |

⚠️ **Important**: Global options must come **before** the subcommand:
```bash
# ✓ Correct
astr0 --json time now
astr0 --verbose sun position
astr0 -p full time now

# ✗ Wrong (won't work)
astr0 time now --json
```

**Example**:
```bash
astr0 --verbose --output json time now
astr0 --json sun rise --lat 40.7 --lon -74.0
astr0 -p high angle sep "10h +30d" "11h +31d"
```

---

## Precision Levels

Control the display precision of numerical output. **All internal calculations use full IEEE 754 double precision** — this only affects how results are displayed.

| Level | Decimals | Use Case |
|-------|----------|----------|
| `compact` | 2 | Quick reference, minimal output |
| `display` | 4 | Human-readable, casual use |
| `standard` | 6 | Default precision for most work |
| `high` | 10 | Research applications |
| `full` | 15 | Maximum IEEE 754 precision |

```bash
# Compact: 0.26
astr0 -p compact time now

# Standard (default): 0.260077
astr0 time now

# Full precision: 0.260076993954923
astr0 -p full time now
```

You can also set precision via environment variable:
```bash
export ASTR0_PRECISION=high
astr0 time now  # Uses high precision
```

---

## Command Aliases

For faster typing, commands have short aliases:

| Command | Aliases |
|---------|---------|
| `time` | `t` |
| `coords` | `c`, `coord` |
| `angles` | `a`, `angle` |
| `constants` | `const` |

**Example**: `astr0 t now` is equivalent to `astr0 time now`

---

## time — Time Commands

Time conversions and astronomical time calculations.

### time now

Display current time in all astronomical formats.

```bash
astr0 time now
```

**Output includes**:
- UTC date and time
- Julian Date
- Modified Julian Date
- T (Julian centuries since J2000.0)
- Greenwich Mean Sidereal Time

---

### time convert

Convert Julian Date or MJD to calendar date.

```bash
astr0 time convert VALUE [--from FORMAT]
```

**Arguments**:
| Argument | Description |
|----------|-------------|
| `VALUE` | The Julian Date or MJD value |

**Options**:
| Option | Default | Description |
|--------|---------|-------------|
| `--from` | `jd` | Input format: `jd` or `mjd` |

**Examples**:
```bash
astr0 time convert 2460000.5
astr0 time convert 60000 --from mjd
```

---

### time jd

Convert calendar date to Julian Date.

```bash
astr0 time jd YEAR MONTH DAY [HOUR] [MINUTE] [SECOND]
```

**Arguments**:
| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `YEAR` | Yes | — | Year (e.g., 2024) |
| `MONTH` | Yes | — | Month (1-12) |
| `DAY` | Yes | — | Day (1-31) |
| `HOUR` | No | 0 | Hour (0-23) |
| `MINUTE` | No | 0 | Minute (0-59) |
| `SECOND` | No | 0 | Second (0-59) |

**Example**:
```bash
astr0 time jd 2024 7 4 12 0 0
```

---

### time lst

Calculate Local Sidereal Time for a longitude.

```bash
astr0 time lst LONGITUDE [--jd JD]
```

**Arguments**:
| Argument | Description |
|----------|-------------|
| `LONGITUDE` | Observer longitude in degrees (positive East) |

**Options**:
| Option | Default | Description |
|--------|---------|-------------|
| `--jd` | Current time | Julian Date for calculation |

**Examples**:
```bash
astr0 time lst -- -118.25          # Los Angeles (note: -- before negative)
astr0 time lst 0                   # Greenwich
astr0 time lst 139.69 --jd 2460000.5  # Tokyo at specific JD
```

**Note**: Use `--` before negative longitudes to prevent them being interpreted as flags.

---

## coords — Coordinate Commands

Coordinate parsing and transformations.

### coords transform

Transform coordinates between systems.

```bash
astr0 coords transform COORDINATES --to SYSTEM [options]
```

**Arguments**:
| Argument | Description |
|----------|-------------|
| `COORDINATES` | Input coordinates (see format below) |

**Options**:
| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--to` | Yes | — | Target system: `icrs`, `galactic`, `altaz`, `horizontal` |
| `--from` | No | `icrs` | Source system: `icrs`, `galactic` |
| `--lat` | For altaz | — | Observer latitude (degrees) |
| `--lon` | For altaz | — | Observer longitude (degrees) |
| `--jd` | No | Current | Julian Date (for altaz) |

**Coordinate formats accepted**:
```
"12h30m45s +45d30m00s"    # HMS/DMS
"12:30:45 +45:30:00"      # Colon notation
"187.6875 45.5"           # Decimal degrees
"l=135.0 b=71.6"          # Galactic (with --from galactic)
```

**Examples**:
```bash
# ICRS to Galactic
astr0 coords transform "12h30m +45d" --to galactic

# ICRS to Horizontal (requires location)
astr0 coords transform "12h30m +45d" --to altaz --lat 34.05 --lon -118.25

# Galactic to ICRS
astr0 coords transform "l=0 b=0" --from galactic --to icrs
```

---

### coords parse

Parse and display coordinate components.

```bash
astr0 coords parse COORDINATES
```

**Arguments**:
| Argument | Description |
|----------|-------------|
| `COORDINATES` | Coordinate string to parse |

**Example**:
```bash
astr0 coords parse "12h30m45.2s -45d30m15s"
```

**Output**:
```
Parsed Coordinates:
  RA:  12h 30m 45.20s = 187.6883°
  Dec: -45° 30′ 15.00″ = -45.5042°
```

---

## angles — Angular Calculations

Angular measurements and calculations.

### angles sep

Calculate angular separation between two points.

```bash
astr0 angles sep COORD1 COORD2
```

**Arguments**:
| Argument | Description |
|----------|-------------|
| `COORD1` | First coordinate |
| `COORD2` | Second coordinate |

**Example**:
```bash
astr0 angles sep "10h30m +30d" "10h35m +31d"
```

**Output**:
```
Angular Separation:
  1° 17′ 12.34″
  = 1.28676°
  = 77.206′
  = 4632.34″
```

**With verbose mode**:
```bash
astr0 --verbose angles sep "10h +30d" "11h +31d"
```
Shows the complete Vincenty formula calculation.

---

### angles pa

Calculate position angle from point 1 to point 2.

```bash
astr0 angles pa COORD1 COORD2
```

**Arguments**:
| Argument | Description |
|----------|-------------|
| `COORD1` | Reference point |
| `COORD2` | Target point |

**Example**:
```bash
astr0 angles pa "10h30m +30d" "10h35m +31d"
```

**Output**:
```
Position Angle: 32.45° (N through E)
```

Position angle is measured from North (0°) through East (90°).

---

### angles convert

Convert an angle between units.

```bash
astr0 angles convert VALUE [--from UNIT]
```

**Arguments**:
| Argument | Description |
|----------|-------------|
| `VALUE` | Numeric value to convert |

**Options**:
| Option | Default | Description |
|--------|---------|-------------|
| `--from` | `deg` | Input unit: `deg`, `rad`, `hours`, `arcmin`, `arcsec` |

**Examples**:
```bash
astr0 angles convert 45.5 --from deg
astr0 angles convert 3.14159 --from rad
astr0 angles convert 12.5 --from hours
```

---

## constants — Astronomical Constants

Access to authoritative astronomical constants.

### constants list

List all available constants.

```bash
astr0 constants list
```

Displays all constants with their values, units, and references.

---

### constants search

Search for constants by name.

```bash
astr0 constants search QUERY
```

**Arguments**:
| Argument | Description |
|----------|-------------|
| `QUERY` | Search term (case-insensitive) |

**Examples**:
```bash
astr0 constants search solar
astr0 constants search earth
astr0 constants search julian
```

---

### constants show

Display a specific constant.

```bash
astr0 constants show NAME
```

**Arguments**:
| Argument | Description |
|----------|-------------|
| `NAME` | Constant attribute name |

**Available constants**:
- `c` — Speed of light
- `G` — Gravitational constant
- `AU` — Astronomical Unit
- `JD_J2000` — Julian Date of J2000.0
- `MJD_OFFSET` — Modified JD offset
- `julian_year` — Julian year in days
- `julian_century` — Julian century in days
- `arcsec_per_rad` — Arcseconds per radian
- `earth_radius_eq` — Earth equatorial radius
- `earth_flattening` — Earth flattening
- `earth_rotation_rate` — Earth rotation rate
- `obliquity_j2000` — Mean obliquity at J2000.0
- `ra_ngp` — RA of North Galactic Pole
- `dec_ngp` — Dec of North Galactic Pole
- `l_ncp` — Galactic longitude of NCP
- `M_sun` — Solar mass
- `R_sun` — Solar radius
- `L_sun` — Solar luminosity

**Example**:
```bash
astr0 constants show c
```

---

## about

Display information about astr0.

```bash
astr0 about
```

Shows the ASCII banner, version, license, and motto.

---

## Output Formats

### Plain (Default)

Human-readable formatted output with Unicode characters.

```bash
astr0 time now
```

### JSON

Machine-readable JSON output.

```bash
astr0 --output json time now
```

```json
{
  "utc": "2026-01-03T00:15:00.000000+00:00",
  "julian_date": 2461043.5104166665,
  "modified_jd": 61043.01041666651,
  "j2000_centuries": 0.26005504109589043,
  "gmst_hours": 7.093055555555556
}
```

JSON output is useful for:
- Scripting and automation
- Piping to `jq` for processing
- Integration with other tools

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Command line usage error |

---

## Environment Variables

Currently, astr0 does not use environment variables. Future versions may support:
- `ASTR0_DEFAULT_FORMAT` — Default output format
- `ASTR0_OBSERVER_LAT` / `ASTR0_OBSERVER_LON` — Default observer location

---

## Tips

### Handling Negative Numbers

Use `--` to separate options from arguments with negative values:

```bash
astr0 time lst -- -118.25
```

### Combining Options

```bash
astr0 -v -o json coords transform "12h +45d" --to galactic
```

### Chaining with Other Tools

```bash
# Get just the Julian Date
astr0 --output json time now | jq '.julian_date'

# Store result in a variable
JD=$(astr0 --output json time now | jq -r '.julian_date')
```

---

*Next: [Python API](api.md) — Using astr0 as a library*
