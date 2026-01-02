"""
Coordinate systems and transformations.

Supports ICRS (J2000 equatorial), Galactic, Ecliptic, and Horizontal (Alt/Az).
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Union

from astr0.core.angles import Angle
from astr0.core.constants import CONSTANTS
from astr0.core.time import JulianDate
from astr0.verbose import VerboseContext, step


class Coordinate(ABC):
    """Base class for all coordinate types."""
    
    @abstractmethod
    def to_icrs(self, verbose: Optional[VerboseContext] = None) -> ICRSCoord:
        """Convert to ICRS coordinates."""
        pass
    
    @classmethod
    @abstractmethod
    def from_icrs(
        cls, 
        coord: ICRSCoord,
        verbose: Optional[VerboseContext] = None,
        **kwargs
    ) -> "Coordinate":
        """Create from ICRS coordinates."""
        pass


@dataclass(frozen=True)
class ICRSCoord(Coordinate):
    """
    International Celestial Reference System coordinates (J2000 equatorial).
    
    The ICRS is the standard celestial coordinate system, practically 
    equivalent to FK5 J2000.0 for most purposes.
    
    Attributes:
        ra: Right Ascension
        dec: Declination (must be in range [-90°, +90°])
    """
    
    ra: Angle
    dec: Angle
    
    def __post_init__(self):
        if abs(self.dec.degrees) > 90:
            raise ValueError(f"Declination must be in [-90°, +90°], got {self.dec.degrees}°")
    
    @classmethod
    def from_degrees(cls, ra_deg: float, dec_deg: float) -> ICRSCoord:
        """Create from decimal degrees."""
        return cls(Angle(degrees=ra_deg), Angle(degrees=dec_deg))
    
    @classmethod
    def from_hms_dms(
        cls,
        ra_h: float, ra_m: float, ra_s: float,
        dec_d: float, dec_m: float, dec_s: float
    ) -> ICRSCoord:
        """Create from HMS/DMS components."""
        return cls(
            Angle.from_hms(ra_h, ra_m, ra_s),
            Angle.from_dms(dec_d, dec_m, dec_s)
        )
    
    @classmethod
    def parse(cls, value: str) -> ICRSCoord:
        """
        Parse ICRS coordinates from string.
        
        Supported formats:
            - "12h30m00s +45d30m00s"
            - "12:30:00 +45:30:00"
            - "187.5 45.5"
        """
        parts = value.strip().split()
        
        if len(parts) == 2:
            ra_str, dec_str = parts
        else:
            # Try to find the split point (usually at +/- for dec)
            import re
            match = re.match(r'^(.+?)\s*([+-]?\d.*)$', value.strip())
            if match:
                ra_str, dec_str = match.groups()
            else:
                raise ValueError(f"Cannot parse coordinates: {value!r}")
        
        # Check if RA is in HMS format
        if 'h' in ra_str.lower() or ':' in ra_str:
            ra = Angle.parse(ra_str)
            # If parsed as degrees (from colon format), might need conversion
            if ':' in ra_str and 'h' not in ra_str.lower():
                # Assume colon format for RA is HMS
                parts = ra_str.split(':')
                ra = Angle.from_hms(float(parts[0]), float(parts[1]), float(parts[2]))
        else:
            # Plain number, assume degrees
            ra = Angle(degrees=float(ra_str))
        
        dec = Angle.parse(dec_str)
        
        return cls(ra, dec)
    
    def to_icrs(self, verbose: Optional[VerboseContext] = None) -> ICRSCoord:
        """Return self (already ICRS)."""
        return self
    
    @classmethod
    def from_icrs(
        cls, 
        coord: ICRSCoord,
        verbose: Optional[VerboseContext] = None,
        **kwargs
    ) -> ICRSCoord:
        """Return the coordinate (already ICRS)."""
        return coord
    
    def to_galactic(self, verbose: Optional[VerboseContext] = None) -> GalacticCoord:
        """Convert to Galactic coordinates."""
        return GalacticCoord.from_icrs(self, verbose=verbose)
    
    def to_horizontal(
        self,
        jd: JulianDate,
        lat: Angle,
        lon: Angle,
        verbose: Optional[VerboseContext] = None
    ) -> HorizontalCoord:
        """Convert to horizontal (Alt/Az) coordinates."""
        return HorizontalCoord.from_icrs(self, jd=jd, lat=lat, lon=lon, verbose=verbose)
    
    def format(self, precision: int = 2) -> str:
        """Format as string."""
        return f"{self.ra.format_hms(precision)} {self.dec.format_dms(precision)}"
    
    def __str__(self) -> str:
        return self.format()
    
    def __repr__(self) -> str:
        return f"ICRSCoord(ra={self.ra.degrees:.6f}°, dec={self.dec.degrees:.6f}°)"


@dataclass(frozen=True)
class GalacticCoord(Coordinate):
    """
    Galactic coordinates.
    
    The Galactic coordinate system is centered on the Sun, with the 
    fundamental plane aligned with the Milky Way disk.
    
    Attributes:
        l: Galactic longitude (0° at Galactic center, increases toward l=90°)
        b: Galactic latitude (+90° at North Galactic Pole)
    """
    
    l: Angle  # noqa: E741 (ambiguous name)
    b: Angle
    
    def __post_init__(self):
        if abs(self.b.degrees) > 90:
            raise ValueError(f"Galactic latitude must be in [-90°, +90°], got {self.b.degrees}°")
    
    @classmethod
    def from_degrees(cls, l_deg: float, b_deg: float) -> GalacticCoord:  # noqa: E741
        """Create from decimal degrees."""
        return cls(Angle(degrees=l_deg), Angle(degrees=b_deg))
    
    def to_icrs(self, verbose: Optional[VerboseContext] = None) -> ICRSCoord:
        """Convert to ICRS coordinates using matrix transformation."""
        # Use the standard rotation matrix approach
        # Reference: "Practical Astronomy with your Calculator" by Duffett-Smith
        # and IAU 1958 Galactic coordinate system, precessed to J2000.0
        
        # North Galactic Pole in J2000.0 equatorial coordinates
        ra_ngp = math.radians(192.8594813)   # 12h 51m 26.28s
        dec_ngp = math.radians(27.1282511)   # +27° 07' 41.7"
        l_ncp = math.radians(122.9319185)    # galactic longitude of NCP
        
        if verbose:
            step(verbose, "Reference frame parameters",
                 f"NGP RA  = {math.degrees(ra_ngp):.6f}°\n"
                 f"NGP Dec = {math.degrees(dec_ngp):.6f}°\n"
                 f"l(NCP)  = {math.degrees(l_ncp):.6f}°")
        
        l_rad = self.l.radians
        b_rad = self.b.radians
        
        if verbose:
            step(verbose, "Input Galactic coordinates",
                 f"l = {self.l.degrees:.6f}°\n"
                 f"b = {self.b.degrees:.6f}°")
        
        # Compute intermediate values
        sin_b = math.sin(b_rad)
        cos_b = math.cos(b_rad)
        sin_dec_ngp = math.sin(dec_ngp)
        cos_dec_ngp = math.cos(dec_ngp)
        
        l_minus_lncp = l_rad - l_ncp
        sin_l_lncp = math.sin(l_minus_lncp)
        cos_l_lncp = math.cos(l_minus_lncp)
        
        # Declination: sin(dec) = sin(b)*sin(dec_ngp) + cos(b)*cos(dec_ngp)*cos(l - l_ncp)
        sin_dec = sin_b * sin_dec_ngp + cos_b * cos_dec_ngp * cos_l_lncp
        dec = math.asin(max(-1.0, min(1.0, sin_dec)))
        cos_dec = math.cos(dec)
        
        if verbose:
            step(verbose, "Declination",
                 f"sin(δ) = sin(b)sin(δ_NGP) + cos(b)cos(δ_NGP)cos(l−l_NCP)\n"
                 f"       = {sin_dec:.10f}\n"
                 f"δ = {math.degrees(dec):.6f}°")
        
        # Right Ascension: compute from the spherical trig relations
        # sin(ra - ra_ngp) * cos(dec) = -cos(b) * sin(l - l_ncp)
        # cos(ra - ra_ngp) * cos(dec) = sin(b)*cos(dec_ngp) - cos(b)*sin(dec_ngp)*cos(l - l_ncp)
        
        if abs(cos_dec) < 1e-10:
            # At pole, RA is undefined; set to 0
            ra = 0.0
        else:
            y = -cos_b * sin_l_lncp
            x = sin_b * cos_dec_ngp - cos_b * sin_dec_ngp * cos_l_lncp
            ra = ra_ngp + math.atan2(y, x)
        
        # Normalize RA to [0, 2π)
        ra = ra % (2 * math.pi)
        if ra < 0:
            ra += 2 * math.pi
        
        if verbose:
            step(verbose, "Right Ascension",
                 f"α = α_NGP + atan2(-cos(b)sin(l−l_NCP), sin(b)cos(δ_NGP) − cos(b)sin(δ_NGP)cos(l−l_NCP))\n"
                 f"  = {math.degrees(ra):.6f}°")
        
        result = ICRSCoord(Angle(radians=ra), Angle(radians=dec))
        
        if verbose:
            step(verbose, "Result (ICRS)",
                 f"RA = {result.ra.format_hms()}\n"
                 f"Dec = {result.dec.format_dms()}")
        
        return result
    
    @classmethod
    def from_icrs(
        cls, 
        coord: ICRSCoord,
        verbose: Optional[VerboseContext] = None,
        **kwargs
    ) -> GalacticCoord:
        """Convert from ICRS coordinates using standard spherical trig."""
        # North Galactic Pole in J2000.0 equatorial coordinates
        ra_ngp = math.radians(192.8594813)   # 12h 51m 26.28s
        dec_ngp = math.radians(27.1282511)   # +27° 07' 41.7"
        l_ncp = math.radians(122.9319185)    # galactic longitude of NCP
        
        if verbose:
            step(verbose, "Input ICRS coordinates",
                 f"RA = {coord.ra.format_hms()}\n"
                 f"Dec = {coord.dec.format_dms()}")
            step(verbose, "Reference frame parameters",
                 f"NGP RA  = {math.degrees(ra_ngp):.6f}°\n"
                 f"NGP Dec = {math.degrees(dec_ngp):.6f}°\n"
                 f"l(NCP)  = {math.degrees(l_ncp):.6f}°")
        
        ra = coord.ra.radians
        dec = coord.dec.radians
        
        # Compute intermediate values
        sin_dec = math.sin(dec)
        cos_dec = math.cos(dec)
        sin_dec_ngp = math.sin(dec_ngp)
        cos_dec_ngp = math.cos(dec_ngp)
        
        ra_minus_rangp = ra - ra_ngp
        sin_ra_rangp = math.sin(ra_minus_rangp)
        cos_ra_rangp = math.cos(ra_minus_rangp)
        
        # Galactic latitude: sin(b) = sin(dec)*sin(dec_ngp) + cos(dec)*cos(dec_ngp)*cos(ra - ra_ngp)
        sin_b = sin_dec * sin_dec_ngp + cos_dec * cos_dec_ngp * cos_ra_rangp
        b = math.asin(max(-1.0, min(1.0, sin_b)))
        cos_b = math.cos(b)
        
        if verbose:
            step(verbose, "Galactic latitude",
                 f"sin(b) = sin(δ)sin(δ_NGP) + cos(δ)cos(δ_NGP)cos(α−α_NGP)\n"
                 f"       = {sin_b:.10f}\n"
                 f"b = {math.degrees(b):.6f}°")
        
        # Galactic longitude
        # sin(l_ncp - l) * cos(b) = cos(dec) * sin(ra - ra_ngp)
        # cos(l_ncp - l) * cos(b) = sin(dec)*cos(dec_ngp) - cos(dec)*sin(dec_ngp)*cos(ra - ra_ngp)
        
        if abs(cos_b) < 1e-10:
            # At pole, l is undefined; set to 0
            l_rad = 0.0
        else:
            y = cos_dec * sin_ra_rangp
            x = sin_dec * cos_dec_ngp - cos_dec * sin_dec_ngp * cos_ra_rangp
            l_rad = l_ncp - math.atan2(y, x)
        
        # Normalize to [0, 2π)
        l_rad = l_rad % (2 * math.pi)
        if l_rad < 0:
            l_rad += 2 * math.pi
        
        if verbose:
            step(verbose, "Galactic longitude",
                 f"l = l_NCP − atan2(cos(δ)sin(α−α_NGP), sin(δ)cos(δ_NGP) − cos(δ)sin(δ_NGP)cos(α−α_NGP))\n"
                 f"  = {math.degrees(l_rad):.6f}°")
        
        result = cls(Angle(radians=l_rad), Angle(radians=b))
        
        if verbose:
            step(verbose, "Result (Galactic)",
                 f"l = {result.l.degrees:.6f}°\n"
                 f"b = {result.b.degrees:.6f}°")
        
        return result
    
    def format(self, precision: int = 4) -> str:
        """Format as string."""
        return f"l={self.l.degrees:.{precision}f}° b={self.b.degrees:.{precision}f}°"
    
    def __str__(self) -> str:
        return self.format()
    
    def __repr__(self) -> str:
        return f"GalacticCoord(l={self.l.degrees:.6f}°, b={self.b.degrees:.6f}°)"


@dataclass(frozen=True)
class HorizontalCoord(Coordinate):
    """
    Horizontal (Alt/Az) coordinates.
    
    Local coordinates relative to the observer's horizon.
    
    Attributes:
        alt: Altitude (elevation) above horizon
        az: Azimuth, measured from North through East
    """
    
    alt: Angle
    az: Angle
    
    def __post_init__(self):
        if abs(self.alt.degrees) > 90:
            raise ValueError(f"Altitude must be in [-90°, +90°], got {self.alt.degrees}°")
    
    @classmethod
    def from_degrees(cls, alt_deg: float, az_deg: float) -> HorizontalCoord:
        """Create from decimal degrees."""
        return cls(Angle(degrees=alt_deg), Angle(degrees=az_deg))
    
    def to_icrs(self, verbose: Optional[VerboseContext] = None) -> ICRSCoord:
        """
        Convert to ICRS coordinates.
        
        Note: This requires observation time and location, which are stored
        in the coordinate. Use the class method for new conversions.
        """
        raise NotImplementedError(
            "HorizontalCoord.to_icrs() requires time and location. "
            "Use ICRSCoord.from_horizontal() with explicit parameters."
        )
    
    @classmethod
    def from_icrs(
        cls, 
        coord: ICRSCoord,
        verbose: Optional[VerboseContext] = None,
        jd: Optional[JulianDate] = None,
        lat: Optional[Angle] = None,
        lon: Optional[Angle] = None,
        **kwargs
    ) -> HorizontalCoord:
        """
        Convert from ICRS coordinates.
        
        Args:
            coord: ICRS coordinates to convert
            jd: Julian Date of observation
            lat: Observer latitude (positive North)
            lon: Observer longitude (positive East)
            verbose: Verbose context for showing work
        """
        if jd is None or lat is None or lon is None:
            raise ValueError("jd, lat, and lon are required for ICRS to Horizontal conversion")
        
        if verbose:
            step(verbose, "Input parameters",
                 f"ICRS: RA = {coord.ra.format_hms()}, Dec = {coord.dec.format_dms()}\n"
                 f"JD = {jd.jd:.6f}\n"
                 f"Observer: lat = {lat.degrees:.6f}°, lon = {lon.degrees:.6f}°")
        
        # Calculate Local Sidereal Time
        lst = jd.lst(lon.degrees, verbose=verbose)
        lst_angle = Angle(hours=lst)
        
        if verbose:
            step(verbose, "Local Sidereal Time",
                 f"LST = {lst_angle.format_hms()}")
        
        # Hour Angle
        ha = lst_angle - Angle(hours=coord.ra.hours)
        ha = ha.normalize(center=0)  # Normalize to [-180, 180]
        
        if verbose:
            step(verbose, "Hour Angle",
                 f"HA = LST − RA\n"
                 f"   = {lst_angle.format_hms()} − {Angle(hours=coord.ra.hours).format_hms()}\n"
                 f"   = {ha.format_hms()}")
        
        # Convert to horizontal
        sin_dec = coord.dec.sin()
        cos_dec = coord.dec.cos()
        sin_lat = lat.sin()
        cos_lat = lat.cos()
        sin_ha = ha.sin()
        cos_ha = ha.cos()
        
        # Altitude
        sin_alt = sin_dec * sin_lat + cos_dec * cos_lat * cos_ha
        alt_rad = math.asin(sin_alt)
        
        if verbose:
            step(verbose, "Altitude calculation",
                 f"sin(alt) = sin(dec)×sin(lat) + cos(dec)×cos(lat)×cos(HA)\n"
                 f"         = {sin_dec:.10f}×{sin_lat:.10f} + {cos_dec:.10f}×{cos_lat:.10f}×{cos_ha:.10f}\n"
                 f"         = {sin_alt:.10f}\n"
                 f"alt = {math.degrees(alt_rad):.6f}°")
        
        # Azimuth
        y = -cos_dec * sin_ha
        x = sin_dec * cos_lat - cos_dec * sin_lat * cos_ha
        az_rad = math.atan2(y, x)
        
        # Normalize to [0, 360)
        az_rad = az_rad % (2 * math.pi)
        if az_rad < 0:
            az_rad += 2 * math.pi
        
        if verbose:
            step(verbose, "Azimuth calculation",
                 f"y = −cos(dec)×sin(HA) = {y:.10f}\n"
                 f"x = sin(dec)×cos(lat) − cos(dec)×sin(lat)×cos(HA) = {x:.10f}\n"
                 f"az = atan2(y, x) = {math.degrees(az_rad):.6f}°")
        
        result = cls(Angle(radians=alt_rad), Angle(radians=az_rad))
        
        if verbose:
            step(verbose, "Result (Horizontal)",
                 f"Alt = {result.alt.format_dms()}\n"
                 f"Az = {result.az.degrees:.4f}°")
        
        return result
    
    @property
    def airmass(self) -> float:
        """
        Calculate airmass using Pickering (2002) formula.
        
        More accurate than sec(z) for high airmass values.
        Valid for altitudes > 0°.
        """
        if self.alt.degrees <= 0:
            return float('inf')
        
        # Pickering (2002) formula - works well down to horizon
        alt_deg = self.alt.degrees
        # Avoid division issues very close to horizon
        if alt_deg < 0.1:
            return float('inf')
        
        # Pickering formula: 1 / sin(h + 244/(165 + 47*h^1.1))
        # where h is altitude in degrees
        h = alt_deg
        denominator = h + 244.0 / (165.0 + 47.0 * (h ** 1.1))
        return 1.0 / math.sin(math.radians(denominator))
    
    @property
    def zenith_angle(self) -> Angle:
        """Zenith angle (90° - altitude)."""
        return Angle(degrees=90.0) - self.alt
    
    def format(self, precision: int = 2) -> str:
        """Format as string."""
        return f"Alt={self.alt.format_dms(precision)} Az={self.az.degrees:.{precision}f}°"
    
    def __str__(self) -> str:
        return self.format()
    
    def __repr__(self) -> str:
        return f"HorizontalCoord(alt={self.alt.degrees:.6f}°, az={self.az.degrees:.6f}°)"


def transform_coords(
    coord: Coordinate,
    to_system: str,
    verbose: Optional[VerboseContext] = None,
    **kwargs
) -> Coordinate:
    """
    Transform coordinates between systems.
    
    Args:
        coord: Input coordinate (any system)
        to_system: Target system ('icrs', 'galactic', 'horizontal', 'altaz')
        verbose: Verbose context
        **kwargs: Additional arguments (jd, lat, lon for horizontal)
    
    Returns:
        Transformed coordinate
    """
    # Normalize system name
    system = to_system.lower().strip()
    system_map = {
        'icrs': 'icrs',
        'j2000': 'icrs',
        'equatorial': 'icrs',
        'galactic': 'galactic',
        'gal': 'galactic',
        'horizontal': 'horizontal',
        'altaz': 'horizontal',
        'alt-az': 'horizontal',
    }
    
    if system not in system_map:
        raise ValueError(f"Unknown coordinate system: {to_system}")
    
    target = system_map[system]
    
    # First convert to ICRS
    icrs = coord.to_icrs(verbose=verbose)
    
    # Then to target
    if target == 'icrs':
        return icrs
    elif target == 'galactic':
        return GalacticCoord.from_icrs(icrs, verbose=verbose)
    elif target == 'horizontal':
        return HorizontalCoord.from_icrs(icrs, verbose=verbose, **kwargs)
    else:
        raise ValueError(f"Unknown coordinate system: {to_system}")
