---
id: angles
title: Angular Calculations
sidebar_label: Angles
sidebar_position: 3
---

# Angular Calculations

Angles are the fundamental unit of positional astronomy. This guide covers how to work with angles in astr0, calculate separations between objects, and find position angles.

---

## Understanding Astronomical Angles

### Units of Angular Measure

Astronomers use several units depending on the scale:

| Unit | Symbol | Size | Common Use |
|------|--------|------|------------|
| Degrees | ° | Full circle = 360° | Large angular distances |
| Arcminutes | ' or arcmin | 1° = 60' | Galaxy sizes, Moon's diameter |
| Arcseconds | " or arcsec | 1' = 60" | Star positions, seeing |
| Hours | h | Full circle = 24h | Right Ascension |
| Radians | rad | Full circle = 2π | Mathematical calculations |

### Why Hours for Right Ascension?

Right Ascension is traditionally measured in hours because the celestial sphere appears to rotate once in 24 hours. If you watch a star, 1 hour later it will have moved 15° westward (360°/24h = 15°/h).

**Conversion**: 1h = 15°, so 1m (time) = 15' and 1s (time) = 15"

---

## The Angle Class

In astr0, the `Angle` class handles all angle representations and conversions.

### Creating Angles

```bash
# In the CLI, convert between formats
astr0 angles convert 45.5 --from deg
astr0 angles convert 3.0333 --from hours
```

### Sexagesimal Notation

**Degrees-Minutes-Seconds (DMS)** for declination and angular distances:
- Format: `±DD° MM' SS.ss"`
- Example: `+45° 30' 15.5"` = 45.504306°

**Hours-Minutes-Seconds (HMS)** for Right Ascension:
- Format: `HHh MMm SS.ss`
- Example: `12h 30m 45s` = 187.6875°

### Parsing Angles

astr0's parser handles many formats:

```bash
astr0 coords parse "45d30m15.5s"    # DMS
astr0 coords parse "12h30m45s"      # HMS
astr0 coords parse "45:30:15.5"     # Colon notation
astr0 coords parse "45.504306"      # Decimal degrees
astr0 coords parse "+45 30 15.5"    # Space-separated
```

---

## Angular Separation

### What Is Angular Separation?

The **angular separation** between two points on the celestial sphere is the angle between them as seen from the center—the shortest path along a great circle.

Think of it as "how far apart do these two objects appear in the sky?"

### Calculating Separation

```bash
astr0 angles sep "10h30m +30d" "10h35m +31d"
```

Output:
```text
Point 1: 10ʰ 30ᵐ 00.00ˢ 30° 00′ 00.00″
Point 2: 10ʰ 35ᵐ 00.00ˢ 31° 00′ 00.00″
─────────────────────────────────────────────

Angular Separation:
  1° 17′ 12.34″
  = 1.28676°
  = 77.206′
  = 4632.34″
```

### The Vincenty Formula

For small separations, simple formulas work. But for accurate results at any distance, astr0 uses the **Vincenty formula**:

$$\sigma = \arctan\left(\frac{\sqrt{(\cos\phi_2\sin\Delta\lambda)^2 + (\cos\phi_1\sin\phi_2 - \sin\phi_1\cos\phi_2\cos\Delta\lambda)^2}}{\sin\phi_1\sin\phi_2 + \cos\phi_1\cos\phi_2\cos\Delta\lambda}\right)$$

Where:
- $\phi_1, \phi_2$ = declinations of the two points
- $\Delta\lambda$ = difference in Right Ascension

This formula is numerically stable for any separation, from 0° to 180°.

### See the Math

```bash
astr0 --verbose angles sep "10h +30d" "11h +31d"
```

```text
┌─ Input coordinates
│  Point 1: RA = 10ʰ 00ᵐ 00.00ˢ, Dec = 30° 00′ 00.00″
│  Point 2: RA = 11ʰ 00ᵐ 00.00ˢ, Dec = 31° 00′ 00.00″
└────────────────────────────────────────
┌─ RA difference
│  Δλ = 15.000000°
└────────────────────────────────────────
┌─ Trigonometric values
│  sin(φ₁) = 0.5000000000, cos(φ₁) = 0.8660254038
│  sin(φ₂) = 0.5150380749, cos(φ₂) = 0.8571673007
│  sin(Δλ) = 0.2588190451, cos(Δλ) = 0.9659258263
└────────────────────────────────────────
┌─ Vincenty formula
│  numerator = √[(cos φ₂ sin Δλ)² + (cos φ₁ sin φ₂ − sin φ₁ cos φ₂ cos Δλ)²]
│            = √[0.2218512223² + 0.0320560402²]
│            = 0.2241552019
│  
│  denominator = sin φ₁ sin φ₂ + cos φ₁ cos φ₂ cos Δλ
│              = 0.9745534595
└────────────────────────────────────────
┌─ Result
│  σ = atan2(0.2241552019, 0.9745534595)
│    = 12.9532°
│    = 12° 57′ 11.54″
└────────────────────────────────────────
```

---

## Position Angle

### What Is Position Angle?

The **position angle** (PA) describes the direction from one object to another on the celestial sphere. It's measured:
- **From North** (0°)
- **Through East** (90°)
- Increasing counterclockwise as seen on the sky

Position angles are important for:
- Binary star observations
- Jet directions in AGN
- Proper motion directions
- Extended source orientations

### Calculating Position Angle

```bash
astr0 angles pa "10h30m +30d" "10h35m +31d"
```

Output:
```text
Position Angle: 32.45° (N through E)
```

This means: starting from Point 1, Point 2 is roughly northeast.

### The Formula

$$PA = \arctan\left(\frac{\sin(\alpha_2 - \alpha_1)}{\cos\delta_1\tan\delta_2 - \sin\delta_1\cos(\alpha_2 - \alpha_1)}\right)$$

The result is normalized to [0°, 360°).

---

## Angle Conversions

### Using the CLI

```bash
# Degrees to all formats
astr0 angles convert 45.5 --from deg

# Hours to degrees
astr0 angles convert 12.5 --from hours

# Radians to degrees
astr0 angles convert 0.7854 --from rad
```

### Conversion Table

| From | To Degrees |
|------|------------|
| 1 hour | 15° |
| 1 minute (time) | 0.25° = 15' |
| 1 second (time) | 0.004167° = 15" |
| 1 radian | 57.2958° |
| 1 arcminute | 0.01667° |
| 1 arcsecond | 0.000278° |

---

## Working with Small Angles

For very small angles, the small-angle approximation is useful:

$$\sin\theta \approx \theta \quad \text{and} \quad \tan\theta \approx \theta \quad \text{(in radians)}$$

This is accurate to 1% for angles < 14° and to 0.1% for angles < 4.5°.

### Arcseconds Per Radian

One of our constants:

$$\frac{180° \times 3600"}{\pi} = 206264.806..."$$

This is useful for converting small angles:

$$\theta_{arcsec} = \theta_{rad} \times 206264.8$$

---

## Common Angular Scales

| Object | Angular Size |
|--------|--------------|
| Moon / Sun | ~30' = 0.5° |
| Jupiter | 30-50" |
| Mars (at opposition) | ~25" |
| Hubble resolution | ~0.05" |
| Ground-based seeing | 0.5-2" |
| Full sky (hemisphere) | 20,626 square degrees |

---

## Practical Examples

### How far apart are the Pointer Stars?

Dubhe and Merak in the Big Dipper "point" to Polaris.

- Dubhe: 11h 03m 43s, +61° 45' 03"
- Merak: 11h 01m 50s, +56° 22' 56"

```bash
astr0 angles sep "11h03m43s +61d45m03s" "11h01m50s +56d22m56s"
```

Answer: About 5.4° apart.

### What's the position angle from Albireo A to B?

Albireo is a famous double star. PA tells you the orientation.

```bash
astr0 angles pa "19h30m43.3s +27d57m34.8s" "19h30m45.4s +27d57m54.9s"
```

### Angular size of an object

If you know an object's physical size (d) and distance (D):

$$\theta = \arctan\left(\frac{d}{D}\right) \approx \frac{d}{D} \text{ (radians, for small angles)}$$

**Example**: The Moon is 3,474 km diameter at 384,400 km distance:
$$\theta = \frac{3474}{384400} = 0.00904 \text{ rad} = 0.518° = 31' $$

---

## Python API

```python
from astr0.core.angles import Angle, angular_separation, position_angle

# Create angles various ways
a1 = Angle(degrees=45.5)
a2 = Angle(hours=3.0333)
a3 = Angle(radians=0.7854)
a4 = Angle.from_dms(45, 30, 15.5)
a5 = Angle.from_hms(12, 30, 45)
a6 = Angle.parse("45d30m15.5s")

# Access in different units
print(f"{a1.degrees}° = {a1.hours}h = {a1.radians} rad")
print(f"{a1.arcminutes}' = {a1.arcseconds}\"")

# Format nicely
print(a4.to_dms())  # "45° 30′ 15.50″"
print(a5.to_hms())  # "12ʰ 30ᵐ 45.00ˢ"

# Arithmetic
total = a1 + a2
diff = a1 - a2
scaled = a1 * 2
half = a1 / 2

# Normalize to a range
normalized = a1.normalize(center=180)  # [0, 360)

# Trigonometry
print(a1.sin(), a1.cos(), a1.tan())

# Angular separation
from astr0.core.coords import ICRSCoord
c1 = ICRSCoord.from_string("10h30m +30d")
c2 = ICRSCoord.from_string("10h35m +31d")
sep = angular_separation(c1.ra, c1.dec, c2.ra, c2.dec)
print(f"Separation: {sep.to_dms()}")

# Position angle
pa = position_angle(c1.ra, c1.dec, c2.ra, c2.dec)
print(f"PA: {pa.degrees}°")
```

---

## Key Formulas Reference

| Calculation | Formula |
|-------------|---------|
| Hours ↔ Degrees | $h \times 15 = °$ |
| DMS → Decimal | $° + '/60 + "/3600$ |
| Small angle (rad) | $\theta_{arcsec} / 206264.8$ |
| Vincenty | See section above |
| Position angle | See section above |

---

## Further Reading

- Green, R.M. "Spherical Astronomy" — Comprehensive treatment
- Meeus, J. "Astronomical Algorithms" — Chapter 17 (Angular separation)
- "The Observer's Handbook" — Practical observing information

---

*Next: [Astronomical Constants](/module-guides/constants) — The numbers behind it all*
