"""
Hipparcos catalog types and data structures.

This module defines the HIPStar dataclass and spectral type constants
for working with Hipparcos catalog data.

The Hipparcos Catalog:
    The Hipparcos (HIgh Precision PARallax COllecting Satellite) was an ESA
    mission launched in 1989. It measured positions, parallaxes, and proper
    motions of ~118,000 stars with unprecedented precision (~1 milliarcsecond).

    This catalog revolutionized our knowledge of stellar distances. Before
    Hipparcos, ground-based parallax measurements were limited to ~100 parsecs.
    Hipparcos extended reliable distances to ~1000 parsecs.

Key Measurements:
    - Parallax: The apparent shift in a star's position due to Earth's orbital
      motion. Parallax (in arcseconds) = 1 / distance (in parsecs).
      1 parsec = 3.26 light-years.

    - Proper Motion: The star's angular motion across the sky in mas/year.
      Caused by the star's actual motion relative to the Sun.

    - Magnitude: The logarithmic brightness scale where lower = brighter.
      Each magnitude step is ~2.512× brightness difference.
      Sirius (mag -1.46) is ~25× brighter than a mag +2 star.

    - B-V Color Index: Difference between blue (B) and visual (V) magnitude.
      Negative values = blue/hot stars; Positive = red/cool stars.

Example:
    >>> from starward.core.hipparcos_types import HIPStar, SPECTRAL_CLASSES
    >>> sirius = HIPStar.from_dict({'hip_number': 32349, 'magnitude': -1.46, ...})
    >>> print(sirius.spectral_class)
    A
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# =============================================================================
# Spectral Classification System (Harvard Classification)
# =============================================================================
#
# Stars are classified by their surface temperature, which determines the
# spectral lines visible in their light. The sequence runs from hottest (O)
# to coolest (M), remembered by the mnemonic:
# "Oh Be A Fine Girl/Guy, Kiss Me"
#
# Temperature decreases: O → B → A → F → G → K → M → L → T → Y
#                      50,000K → 30,000K → 10,000K → 7,500K → 6,000K → 4,000K → 3,000K → cooler
#
# Each class is subdivided 0-9 (e.g., A0 is hottest A-type, A9 is coolest).
# Our Sun is a G2V star (G-type, subclass 2, main sequence).

SPECTRAL_CLASSES = ["O", "B", "A", "F", "G", "K", "M", "L", "T", "Y"]

# =============================================================================
# Luminosity Classes (Yerkes Classification / MK System)
# =============================================================================
#
# Stars of the same temperature can have vastly different luminosities
# depending on their size and evolutionary state. A red giant (III) and
# a red dwarf (V) may have similar temperatures but differ in luminosity
# by factors of 1000 or more.
#
# The full spectral type combines both: "A1V" = A-type, subclass 1, main sequence
#                                       "K5III" = K-type, subclass 5, giant

LUMINOSITY_CLASSES = {
    "Ia-0": "Hypergiant",           # Most luminous stars known
    "Ia": "Luminous supergiant",    # Like Betelgeuse, Deneb
    "Iab": "Intermediate supergiant",
    "Ib": "Less luminous supergiant",
    "II": "Bright giant",           # Transitional between giants and supergiants
    "III": "Giant",                 # Like Arcturus, Aldebaran - evolved off main sequence
    "IV": "Subgiant",               # Beginning to evolve off main sequence
    "V": "Main sequence (dwarf)",   # Core hydrogen fusion - like our Sun
    "VI": "Subdwarf",               # Low metallicity, below main sequence
    "VII": "White dwarf",           # Stellar remnants - electron-degenerate
}


@dataclass(frozen=True)
class HIPStar:
    """
    A star from the Hipparcos catalog.

    Attributes:
        hip_number: Hipparcos catalog number (primary identifier)
        name: Common name (e.g., "Sirius", "Vega")
        bayer: Bayer designation (e.g., "Alpha Canis Majoris")
        flamsteed: Flamsteed number within constellation
        ra_hours: Right Ascension in decimal hours (J2000)
        dec_degrees: Declination in decimal degrees (J2000)
        magnitude: Visual (V-band) magnitude
        bv_color: B-V color index
        spectral_type: Spectral classification (e.g., "A1V", "K5III")
        parallax: Parallax in milliarcseconds
        distance_ly: Distance in light-years
        proper_motion_ra: Proper motion in RA (mas/yr)
        proper_motion_dec: Proper motion in Dec (mas/yr)
        radial_velocity: Radial velocity in km/s
        constellation: IAU 3-letter constellation abbreviation

    Example:
        >>> sirius = HIPStar(
        ...     hip_number=32349,
        ...     name="Sirius",
        ...     bayer="Alpha Canis Majoris",
        ...     magnitude=-1.46,
        ...     spectral_type="A1V",
        ...     ...
        ... )
    """

    hip_number: int
    name: Optional[str]
    bayer: Optional[str]
    flamsteed: Optional[int]
    ra_hours: float
    dec_degrees: float
    magnitude: float
    bv_color: Optional[float]
    spectral_type: Optional[str]
    parallax: Optional[float]
    distance_ly: Optional[float]
    proper_motion_ra: Optional[float]
    proper_motion_dec: Optional[float]
    radial_velocity: Optional[float]
    constellation: str

    @classmethod
    def from_dict(cls, data: dict) -> "HIPStar":
        """
        Create a HIPStar from a dictionary (database row).

        Args:
            data: Dictionary with star data

        Returns:
            HIPStar instance
        """
        return cls(
            hip_number=data["hip_number"],
            name=data.get("name"),
            bayer=data.get("bayer"),
            flamsteed=data.get("flamsteed"),
            ra_hours=data["ra_hours"],
            dec_degrees=data["dec_degrees"],
            magnitude=data["magnitude"],
            bv_color=data.get("bv_color"),
            spectral_type=data.get("spectral_type"),
            parallax=data.get("parallax"),
            distance_ly=data.get("distance_ly"),
            proper_motion_ra=data.get("proper_motion_ra"),
            proper_motion_dec=data.get("proper_motion_dec"),
            radial_velocity=data.get("radial_velocity"),
            constellation=data["constellation"],
        )

    @property
    def designation(self) -> str:
        """Get the primary designation for this star."""
        if self.name:
            return self.name
        if self.bayer:
            return self.bayer
        if self.flamsteed and self.constellation:
            return f"{self.flamsteed} {self.constellation}"
        return f"HIP {self.hip_number}"

    @property
    def spectral_class(self) -> Optional[str]:
        """Get just the spectral class letter (O, B, A, F, G, K, M)."""
        if not self.spectral_type:
            return None
        for cls in SPECTRAL_CLASSES:
            if self.spectral_type.startswith(cls):
                return cls
        return None

    def __str__(self) -> str:
        """Return string representation."""
        mag_str = f"mag {self.magnitude:.2f}"
        if self.name:
            return f"HIP {self.hip_number} ({self.name}) - {mag_str}"
        elif self.bayer:
            return f"HIP {self.hip_number} ({self.bayer}) - {mag_str}"
        return f"HIP {self.hip_number} - {mag_str}"
