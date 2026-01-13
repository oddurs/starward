---
id: coords
title: Coordinate Systems
sidebar_label: Coordinates
sidebar_position: 2
---

# Coordinate Systems

The sky is a sphere, and we need ways to specify locations on it. This guide explains the coordinate systems astronomers use and how to transform between them.

---

## The Celestial Sphere

Imagine extending Earth's axis into space. The points where this axis intersects the celestial sphere are the **celestial poles**. The extension of Earth's equator is the **celestial equator**.

This conceptual sphere, centered on the observer (or Earth), is called the **celestial sphere**. All coordinate systems are ways of locating points on this sphere.

---

## ICRS (Equatorial Coordinates)

The **International Celestial Reference System (ICRS)** is the modern standard equatorial coordinate system.

### The Two Coordinates

**Right Ascension (RA or α)** — The "longitude" of the sky
- Measured in hours, minutes, seconds (0h to 24h)
- Or in degrees (0° to 360°)
- Increases eastward from the vernal equinox

**Declination (Dec or δ)** — The "latitude" of the sky
- Measured in degrees, arcminutes, arcseconds (-90° to +90°)
- +90° is the North Celestial Pole
- -90° is the South Celestial Pole
- 0° is the celestial equator

### The Vernal Equinox

The zero point of Right Ascension is where the Sun crosses the celestial equator heading north—the **vernal equinox** (also called the First Point of Aries, though it's now in Pisces due to precession).

### Example: Polaris

The North Star has coordinates approximately:
- RA: 02h 31m 49s
- Dec: +89° 15' 51"

It's less than 1° from the North Celestial Pole.

---

## Parsing Coordinates in astr0

astr0 understands multiple input formats:

```bash
# HMS/DMS format
astr0 coords parse "12h30m45.2s +45d15m30s"

# Colon format
astr0 coords parse "12:30:45.2 +45:15:30"

# Decimal degrees
astr0 coords parse "187.6883 45.2583"

# Mixed
astr0 coords parse "12h30m +45.5"
```

The parser is flexible—it handles signs, optional seconds, and various separators.

---

## Galactic Coordinates

The **Galactic coordinate system** is centered on the Sun, with the fundamental plane being the Milky Way's disk.

### The Two Coordinates

**Galactic Longitude (l)** — Angle around the Galaxy
- Measured in degrees (0° to 360°)
- 0° points toward the Galactic Center
- 90° is the direction of Galactic rotation
- 180° is the anti-center

**Galactic Latitude (b)** — Angle above/below the plane
- Measured in degrees (-90° to +90°)
- +90° is the North Galactic Pole
- 0° is in the Galactic plane

### Why Use Galactic Coordinates?

Galactic coordinates reveal the structure of the Milky Way:
- Objects with b ≈ 0° are in the Galactic plane
- Objects with |b| > 30° are "high-latitude" (away from dust)
- l tells you which direction in the Galaxy

**Example**: The Galactic Center is at l = 0°, b = 0° (by definition).

### The Galactic Poles in ICRS

| Reference Point | RA (ICRS) | Dec (ICRS) |
|----------------|-----------|------------|
| North Galactic Pole | 12h 51m 26s | +27° 07' 42" |
| Galactic Center | 17h 45m 40s | -29° 00' 28" |

---

## Transforming Between ICRS and Galactic

```bash
astr0 coords transform "12h30m +45d" --to galactic
```

Output:
```text
Input (ICRS): 12h30m +45d
─────────────────────────────────────────────
Output (Galactic):
  l:  135.023680°
  b:  71.621544°
```

This object is at high Galactic latitude (b ≈ 72°), far from the Galactic plane.

### The Transformation Math

The ICRS ↔ Galactic transformation uses **spherical trigonometry**. The key parameters are:

| Constant | Value | Meaning |
|----------|-------|---------|
| α_NGP | 192.8595° | RA of North Galactic Pole |
| δ_NGP | 27.1283° | Dec of North Galactic Pole |
| l_NCP | 122.932° | Galactic longitude of North Celestial Pole |

**ICRS → Galactic**:

$$\sin b = \sin \delta \sin \delta_{NGP} + \cos \delta \cos \delta_{NGP} \cos(\alpha - \alpha_{NGP})$$

$$\tan(l_{NCP} - l) = \frac{\cos \delta \sin(\alpha - \alpha_{NGP})}{\sin \delta \cos \delta_{NGP} - \cos \delta \sin \delta_{NGP} \cos(\alpha - \alpha_{NGP})}$$

To see this calculation step by step:

```bash
astr0 --verbose coords transform "12h30m +45d" --to galactic
```

---

## Horizontal Coordinates (Alt/Az)

**Horizontal coordinates** are local to an observer. They depend on:
- Your location (latitude, longitude)
- The time of observation

### The Two Coordinates

**Altitude (alt)** — Angle above the horizon
- 0° = on the horizon
- +90° = directly overhead (zenith)
- Negative = below the horizon

**Azimuth (az)** — Compass direction
- 0° = North
- 90° = East
- 180° = South
- 270° = West

### Related Quantities

**Zenith Distance**: z = 90° - altitude

**Airmass**: How much atmosphere light traverses. astr0 uses the Pickering (2002) formula:

$$X = \frac{1}{\sin(alt + \frac{244}{165 + 47 \times alt^{1.1}})}$$

This is accurate even near the horizon.

### Transforming to Horizontal Coordinates

```bash
astr0 coords transform "12h30m +45d" --to altaz --lat 34.05 --lon -118.25
```

This shows where the object appears in the sky from Los Angeles right now.

Output:
```text
Input (ICRS): 12h30m +45d
─────────────────────────────────────────────
Output (Horizontal):
  Altitude:   45.234567°
  Azimuth:    287.123456°
  Zenith:     44.765433°
  Airmass:    1.41
```

**Interpretation**: The object is about 45° up, in the WNW, and you're looking through 1.4× the minimum atmosphere.

---

## The Horizontal Transformation

Converting ICRS → Horizontal requires:

1. **Calculate Local Sidereal Time (LST)** from the current time and longitude
2. **Calculate Hour Angle**: HA = LST - RA
3. **Apply spherical trigonometry** for the observer's latitude

**Hour Angle** is how far west an object is from the meridian:
- HA = 0h → on the meridian (highest point)
- HA > 0 → west of meridian (setting)
- HA < 0 → east of meridian (rising)

**The formulas**:

$$\sin(alt) = \sin(\delta) \sin(\phi) + \cos(\delta) \cos(\phi) \cos(HA)$$

$$\tan(az) = \frac{-\sin(HA)}{\tan(\delta) \cos(\phi) - \sin(\phi) \cos(HA)}$$

Where φ is the observer's latitude.

---

## Coordinate Format Reference

### Input Formats Accepted

| Format | Example | Notes |
|--------|---------|-------|
| HMS/DMS | `12h30m45s +45d15m30s` | Sexagesimal |
| HMS/DMS | `12h30m45.2s -45d15m30.5s` | With decimals |
| Colon | `12:30:45 +45:15:30` | Common in catalogs |
| Decimal | `187.5 45.25` | Degrees |
| Mixed | `12h30m +45.5` | RA in hours, Dec in degrees |
| Galactic | `l=135.0 b=71.6` | For `--from galactic` |

### Output Formats

Results are shown in the most appropriate format:
- **ICRS**: RA in HMS, Dec in DMS
- **Galactic**: l and b in degrees
- **Horizontal**: Alt and Az in degrees

---

## Practical Examples

### "Is M31 up tonight?"

Find M31's current altitude from your location:

```bash
astr0 coords transform "00h42m44s +41d16m09s" --to altaz --lat 40.7 --lon -74.0
```

If altitude > 0, it's above the horizon!

### "Where is the Galactic Center?"

```bash
astr0 coords transform "l=0 b=0" --from galactic --to icrs
```

Output: RA ≈ 17h45m40s, Dec ≈ -29°00'

### "How high does Vega get from my latitude?"

An object's maximum altitude equals 90° - |latitude - declination|.

Vega: Dec ≈ +38.8°
From latitude +40°: max alt ≈ 90° - |40 - 38.8| ≈ 88.8° (nearly overhead!)
From latitude -40°: max alt ≈ 90° - |-40 - 38.8| ≈ 11.2° (barely above horizon)

---

## Python API

```python
from astr0.core.coords import ICRSCoord, GalacticCoord, HorizontalCoord
from astr0.core.angles import Angle

# Create ICRS coordinates
coord = ICRSCoord.from_string("12h30m +45d")
print(f"RA: {coord.ra.to_hms()}")
print(f"Dec: {coord.dec.to_dms()}")

# Transform to Galactic
gal = coord.to_galactic()
print(f"l = {gal.l.degrees:.4f}°")
print(f"b = {gal.b.degrees:.4f}°")

# Transform to Horizontal (needs location and time)
from astr0.core.time import jd_now
jd = jd_now()
horiz = coord.to_horizontal(
    latitude=Angle(degrees=34.05),
    longitude=Angle(degrees=-118.25),
    jd=jd
)
print(f"Alt: {horiz.alt.degrees:.2f}°")
print(f"Az: {horiz.az.degrees:.2f}°")
print(f"Airmass: {horiz.airmass:.2f}")

# Create from Galactic and convert to ICRS
gal = GalacticCoord.from_degrees(l=0, b=0)  # Galactic Center
icrs = gal.to_icrs()
```

---

## Summary Table

| System | Coordinates | Reference | Use Case |
|--------|-------------|-----------|----------|
| ICRS | RA, Dec | Vernal equinox, celestial equator | Standard catalog positions |
| Galactic | l, b | Galactic center, Galactic plane | Milky Way structure |
| Horizontal | Alt, Az | Local horizon, North | Observing, telescope pointing |

---

## Further Reading

- Smart, W.M. "Textbook on Spherical Astronomy" — The classic reference
- Meeus, J. "Astronomical Algorithms" — Chapters 12-13 (Coordinate transformations)
- The Hipparcos and Tycho Catalogues (ESA SP-1200) — ICRS definition

---

*Next: [Angular Calculations](/module-guides/angles) — Measure distances on the sky*
