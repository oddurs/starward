---
id: stars
title: Star Catalog
sidebar_label: Star Catalog
sidebar_position: 7
description: Browse and search the Hipparcos bright star catalog with precise positions and stellar data.
---

# Star Catalog

The `stars` command provides access to the Hipparcos bright star catalog, containing precise astrometric and photometric data for bright stars visible to the naked eye and binoculars.

## Overview

The Hipparcos catalog (named after the ancient Greek astronomer) was compiled from observations by ESA's Hipparcos satellite (1989-1993). It provides:

- **Precise positions** — Milliarcsecond accuracy
- **Proper motions** — Stellar movement across the sky
- **Parallax** — Distance measurements
- **Photometry** — Brightness and color data
- **Spectral types** — Stellar classification

## Spectral Classes

Stars are classified by spectral type (temperature sequence):

| Class | Color | Temperature | Examples |
|-------|-------|-------------|----------|
| O | Blue | >30,000 K | Rare, massive stars |
| B | Blue-white | 10,000-30,000 K | Rigel, Spica |
| A | White | 7,500-10,000 K | Vega, Sirius |
| F | Yellow-white | 6,000-7,500 K | Procyon, Canopus |
| G | Yellow | 5,200-6,000 K | Sun, Alpha Centauri A |
| K | Orange | 3,700-5,200 K | Arcturus, Aldebaran |
| M | Red | 2,400-3,700 K | Betelgeuse, Antares |

---

## stars list

List stars from the Hipparcos catalog with optional filters.

```bash
starward stars list [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--constellation CODE` | Filter by constellation (3-letter code) |
| `--magnitude MAG` | Show stars brighter than magnitude |
| `--spectral CLASS` | Filter by spectral class (O, B, A, F, G, K, M) |
| `--limit N` | Maximum results (default: 50) |

**Examples:**

```bash
# List brightest stars
starward stars list

# Stars in Orion
starward stars list --constellation Ori

# Bright stars (magnitude < 2)
starward stars list --magnitude 2

# Red giants (K and M type)
starward stars list --spectral K
starward stars list --spectral M

# Combine filters: bright blue stars
starward stars list --spectral B --magnitude 3
```

---

## stars show

Display detailed information about a star.

```bash
starward stars show HIP_NUMBER
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `HIP_NUMBER` | Hipparcos catalog number |

**Example:**

```bash
starward stars show 32349
```

**Output:**

```
HIP 32349 — Sirius
────────────────────────────────────────
  Bayer           α Canis Majoris
  Constellation   CMa
  Coordinates     06h 45m 08.9s  −16° 42′ 58″
  Magnitude       −1.46
  Spectral Type   A1V
  B−V Color       0.00
  Parallax        379.21 mas
  Distance        8.60 ly
────────────────────────────────────────
```

### Well-Known Stars

| HIP | Name | Description |
|-----|------|-------------|
| 32349 | Sirius | Brightest star in the night sky |
| 91262 | Vega | Standard star, A0V reference |
| 11767 | Polaris | North Star, Cepheid variable |
| 27989 | Betelgeuse | Red supergiant in Orion |
| 69673 | Arcturus | Brightest star in northern hemisphere |
| 24436 | Rigel | Blue supergiant in Orion |
| 21421 | Aldebaran | Orange giant, eye of Taurus |
| 37826 | Pollux | Brightest star in Gemini |

---

## stars search

Search stars by name, Bayer designation, spectral type, or constellation.

```bash
starward stars search QUERY [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `QUERY` | Search term (case-insensitive) |

**Options:**

| Option | Description |
|--------|-------------|
| `--limit N` | Maximum results (default: 25) |

**Examples:**

```bash
# Search by common name
starward stars search "sirius"
starward stars search "betelgeuse"

# Search by Bayer designation
starward stars search "alpha"
starward stars search "alpha orionis"

# Search by spectral type
starward stars search "A0V"
starward stars search "M2"

# Search by constellation
starward stars search "Ori"
```

---

## stars stats

Display catalog statistics.

```bash
starward stars stats
```

**Output:**

```
Hipparcos Catalog Statistics
────────────────────────────────────────
  Total stars       9,110
  Named stars         312
  Brightest         Sirius (−1.46)

  By Spectral Class:
    O                    15
    B                   234
    A                 1,456
    F                 1,823
    G                 2,145
    K                 2,567
    M                   870
────────────────────────────────────────
```

---

## stars altitude

Calculate the current altitude of a star.

```bash
starward stars altitude HIP_NUMBER [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--lat FLOAT` | Observer latitude (degrees) |
| `--lon FLOAT` | Observer longitude (degrees) |
| `--observer NAME` | Use named observer profile |
| `--jd FLOAT` | Julian Date (default: now) |

**Example:**

```bash
starward stars altitude 32349 --lat 40.7 --lon -74.0
```

**Output:**

```
Sirius (HIP 32349)
  Altitude: 23° 45′ 12″
  Azimuth:  187° 32′ 44″
  Status:   Above horizon
```

---

## stars rise / transit / set

Calculate rise, transit, or set times for a star.

```bash
starward stars rise HIP_NUMBER [OPTIONS]
starward stars transit HIP_NUMBER [OPTIONS]
starward stars set HIP_NUMBER [OPTIONS]
```

**Options:** Same as `altitude` command.

**Examples:**

```bash
# When does Sirius rise tonight?
starward stars rise 32349 --lat 40.7 --lon -74.0

# When does Vega transit?
starward stars transit 91262 --observer greenwich

# When does Betelgeuse set?
starward stars set 27989 --lat 51.5 --lon 0
```

**Output:**

```
Sirius (HIP 32349) Rise Time
────────────────────────────────────────
  Rise:     18:23:45 UTC
  Azimuth:  118° 32′ (ESE)
────────────────────────────────────────
```

---

## JSON Output

All commands support JSON output for scripting:

```bash
starward --json stars show 32349
starward --json stars list --constellation Ori
starward --json stars stats
```

**Example JSON:**

```json
{
  "number": 32349,
  "name": "Sirius",
  "bayer": "Alpha Canis Majoris",
  "constellation": "CMa",
  "ra_hours": 6.7525,
  "dec_degrees": -16.7161,
  "magnitude": -1.46,
  "spectral_type": "A1V",
  "bv_color": 0.00,
  "parallax_mas": 379.21,
  "distance_ly": 8.60
}
```

---

## Tips

### Finding Stars

```bash
# Find a star by common name
starward stars search "arcturus"
starward stars search "polaris"

# Find stars by Greek letter designation
starward stars search "alpha centauri"
starward stars search "beta orionis"

# Find all named stars in a constellation
starward stars list --constellation Ori
```

### Observing Bright Stars

```bash
# List the 10 brightest stars
starward stars list --magnitude 1.5

# Check if a star is visible now
starward stars altitude 32349 --lat 40.7 --lon -74.0

# Find best viewing time (transit)
starward stars transit 91262 --observer home
```

### Stellar Classification

```bash
# Find hot blue stars
starward stars list --spectral B --magnitude 4

# Find red giants
starward stars list --spectral K --magnitude 3
starward stars list --spectral M --magnitude 4

# Find Sun-like stars
starward stars list --spectral G --magnitude 5
```

### Scripting Examples

```bash
# Get coordinates for a star
starward --json stars show 32349 | jq '{ra: .ra_hours, dec: .dec_degrees}'

# Export all Orion stars
starward --json stars list --constellation Ori > orion_stars.json

# Get magnitude of brightest stars
starward --json stars list --magnitude 1 | jq '.[].magnitude'
```

---

## See Also

- [Deep-Sky Catalogs](/docs/cli-reference/deep-sky) — Messier, NGC, IC, Caldwell
- [Object Finder](/docs/cli-reference/finder) — Cross-catalog search including stars
- [Visibility Commands](/docs/cli-reference/reference#stars-altitude--rise--transit--set) — Rise, set, transit calculations

---

*Next: [Object Finder](/docs/cli-reference/finder) — Cross-catalog search*
