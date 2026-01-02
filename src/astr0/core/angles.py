"""
Angle representation and angular calculations.

Supports multiple input formats and provides precise angular arithmetic.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Optional, Union

from astr0.verbose import VerboseContext, step


@dataclass(frozen=True)
class Angle:
    """
    Represents an angle with full precision.
    
    Create from various formats:
        >>> Angle(degrees=45.5)
        >>> Angle(radians=math.pi/4)
        >>> Angle(hours=12.5)
        >>> Angle.from_dms(45, 30, 0)
        >>> Angle.from_hms(12, 30, 0)
        >>> Angle.parse("45d30m00s")
        >>> Angle.parse("12h30m00s")
    """
    
    _radians: float
    
    def __init__(
        self,
        *,
        degrees: Optional[float] = None,
        radians: Optional[float] = None,
        hours: Optional[float] = None,
        arcminutes: Optional[float] = None,
        arcseconds: Optional[float] = None,
    ):
        # Count how many were provided
        provided = sum(x is not None for x in [degrees, radians, hours, arcminutes, arcseconds])
        if provided != 1:
            raise ValueError("Exactly one of degrees, radians, hours, arcminutes, or arcseconds must be provided")
        
        if radians is not None:
            rad = radians
        elif degrees is not None:
            rad = math.radians(degrees)
        elif hours is not None:
            rad = math.radians(hours * 15.0)
        elif arcminutes is not None:
            rad = math.radians(arcminutes / 60.0)
        elif arcseconds is not None:
            rad = math.radians(arcseconds / 3600.0)
        else:
            rad = 0.0
            
        object.__setattr__(self, '_radians', rad)
    
    @classmethod
    def from_dms(cls, degrees: float, minutes: float = 0, seconds: float = 0) -> Angle:
        """Create from degrees, arcminutes, arcseconds."""
        sign = -1 if degrees < 0 or (degrees == 0 and str(degrees).startswith('-')) else 1
        total = abs(degrees) + minutes / 60 + seconds / 3600
        return cls(degrees=sign * total)
    
    @classmethod
    def from_hms(cls, hours: float, minutes: float = 0, seconds: float = 0) -> Angle:
        """Create from hours, minutes, seconds."""
        sign = -1 if hours < 0 else 1
        total = abs(hours) + minutes / 60 + seconds / 3600
        return cls(hours=sign * total)
    
    @classmethod
    def parse(cls, value: str) -> Angle:
        """
        Parse angle from string.
        
        Supported formats:
            - "45.5" or "45.5d" — degrees
            - "45d30m00s" — DMS
            - "12h30m00s" — HMS  
            - "45:30:00" — DMS (assumed)
            - "+45 30 00" — DMS with spaces
        """
        value = value.strip()
        
        # Check for HMS format (hours)
        hms_pattern = r'^([+-]?\d+(?:\.\d*)?)[hH]\s*(\d+(?:\.\d*)?)?[mM]?\s*(\d+(?:\.\d*)?)?[sS]?$'
        match = re.match(hms_pattern, value)
        if match:
            h = float(match.group(1))
            m = float(match.group(2) or 0)
            s = float(match.group(3) or 0)
            return cls.from_hms(h, m, s)
        
        # Check for DMS format
        dms_pattern = r'^([+-]?\d+(?:\.\d*)?)[dD°]\s*(\d+(?:\.\d*)?)[\′\'mM]?\s*(\d+(?:\.\d*)?)[\″\"sS]?$'
        match = re.match(dms_pattern, value)
        if match:
            d = float(match.group(1))
            m = float(match.group(2) or 0)
            s = float(match.group(3) or 0)
            return cls.from_dms(d, m, s)
        
        # Check for colon-separated (assume DMS)
        colon_pattern = r'^([+-]?\d+(?:\.\d*)?):(\d+(?:\.\d*)?):(\d+(?:\.\d*)?)$'
        match = re.match(colon_pattern, value)
        if match:
            d = float(match.group(1))
            m = float(match.group(2))
            s = float(match.group(3))
            return cls.from_dms(d, m, s)
        
        # Check for space-separated (assume DMS)
        space_pattern = r'^([+-]?\d+(?:\.\d*)?)\s+(\d+(?:\.\d*)?)\s+(\d+(?:\.\d*)?)$'
        match = re.match(space_pattern, value)
        if match:
            d = float(match.group(1))
            m = float(match.group(2))
            s = float(match.group(3))
            return cls.from_dms(d, m, s)
        
        # Plain number (degrees)
        plain_pattern = r'^([+-]?\d+(?:\.\d*)?)[dD°]?$'
        match = re.match(plain_pattern, value)
        if match:
            return cls(degrees=float(match.group(1)))
        
        raise ValueError(f"Cannot parse angle: {value!r}")
    
    # Properties for different units
    @property
    def radians(self) -> float:
        """Angle in radians."""
        return self._radians
    
    @property
    def degrees(self) -> float:
        """Angle in decimal degrees."""
        return math.degrees(self._radians)
    
    @property
    def hours(self) -> float:
        """Angle in decimal hours (for RA)."""
        return self.degrees / 15.0
    
    @property
    def arcminutes(self) -> float:
        """Angle in arcminutes."""
        return self.degrees * 60.0
    
    @property
    def arcseconds(self) -> float:
        """Angle in arcseconds."""
        return self.degrees * 3600.0
    
    def to_dms(self) -> tuple[int, int, float]:
        """Convert to (degrees, arcminutes, arcseconds)."""
        total_seconds = abs(self.arcseconds)
        degrees = int(total_seconds // 3600)
        remaining = total_seconds % 3600
        minutes = int(remaining // 60)
        seconds = remaining % 60
        
        if self._radians < 0:
            degrees = -degrees
        
        return degrees, minutes, seconds
    
    def to_hms(self) -> tuple[int, int, float]:
        """Convert to (hours, minutes, seconds)."""
        total_seconds = abs(self.hours * 3600)
        hours = int(total_seconds // 3600)
        remaining = total_seconds % 3600
        minutes = int(remaining // 60)
        seconds = remaining % 60
        
        if self._radians < 0:
            hours = -hours
            
        return hours, minutes, seconds
    
    def format_dms(self, precision: int = 2, unicode: bool = True) -> str:
        """Format as degrees, arcminutes, arcseconds string."""
        d, m, s = self.to_dms()
        
        if unicode:
            sign = "" if d >= 0 or (d == 0 and self._radians >= 0) else "-"
            return f"{sign}{abs(d)}° {m:02d}′ {s:0{precision+3}.{precision}f}″"
        else:
            sign = "+" if d >= 0 and self._radians >= 0 else ""
            return f"{sign}{d}d {m:02d}m {s:0{precision+3}.{precision}f}s"
    
    def format_hms(self, precision: int = 2, unicode: bool = True) -> str:
        """Format as hours, minutes, seconds string."""
        h, m, s = self.to_hms()
        
        if unicode:
            return f"{h}ʰ {m:02d}ᵐ {s:0{precision+3}.{precision}f}ˢ"
        else:
            return f"{h}h {m:02d}m {s:0{precision+3}.{precision}f}s"
    
    # Arithmetic
    def __add__(self, other: Angle) -> Angle:
        if not isinstance(other, Angle):
            return NotImplemented
        return Angle(radians=self._radians + other._radians)
    
    def __sub__(self, other: Angle) -> Angle:
        if not isinstance(other, Angle):
            return NotImplemented
        return Angle(radians=self._radians - other._radians)
    
    def __mul__(self, scalar: float) -> Angle:
        return Angle(radians=self._radians * scalar)
    
    def __rmul__(self, scalar: float) -> Angle:
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar: float) -> Angle:
        return Angle(radians=self._radians / scalar)
    
    def __neg__(self) -> Angle:
        return Angle(radians=-self._radians)
    
    def __abs__(self) -> Angle:
        return Angle(radians=abs(self._radians))
    
    # Comparison
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Angle):
            return NotImplemented
        return math.isclose(self._radians, other._radians, rel_tol=1e-12)
    
    def __lt__(self, other: Angle) -> bool:
        return self._radians < other._radians
    
    def __le__(self, other: Angle) -> bool:
        return self._radians <= other._radians
    
    def __gt__(self, other: Angle) -> bool:
        return self._radians > other._radians
    
    def __ge__(self, other: Angle) -> bool:
        return self._radians >= other._radians
    
    # Normalization
    def normalize(self, center: float = 180.0) -> Angle:
        """
        Normalize angle to a range centered on `center`.
        
        Default normalizes to [0, 360).
        Use center=0 for [-180, 180).
        """
        deg = self.degrees
        lower = center - 180.0
        while deg < lower:
            deg += 360.0
        while deg >= lower + 360.0:
            deg -= 360.0
        return Angle(degrees=deg)
    
    def __repr__(self) -> str:
        return f"Angle({self.degrees:.10f}°)"
    
    def __str__(self) -> str:
        return self.format_dms()
    
    # Trig functions
    def sin(self) -> float:
        return math.sin(self._radians)
    
    def cos(self) -> float:
        return math.cos(self._radians)
    
    def tan(self) -> float:
        return math.tan(self._radians)


def angular_separation(
    ra1: Angle, dec1: Angle,
    ra2: Angle, dec2: Angle,
    verbose: Optional[VerboseContext] = None
) -> Angle:
    """
    Calculate angular separation between two points using the Vincenty formula.
    
    This formula is accurate for all angular separations, including very small
    and nearly antipodal points.
    
    Args:
        ra1, dec1: First point (right ascension, declination)
        ra2, dec2: Second point
        verbose: Optional verbose context for showing work
    
    Returns:
        Angular separation as an Angle
    """
    # Convert to radians
    λ1, φ1 = ra1.radians, dec1.radians
    λ2, φ2 = ra2.radians, dec2.radians
    
    if verbose:
        step(verbose, "Input coordinates",
             f"Point 1: RA = {ra1.format_hms()}, Dec = {dec1.format_dms()}\n"
             f"Point 2: RA = {ra2.format_hms()}, Dec = {dec2.format_dms()}")
    
    # Difference in RA
    Δλ = λ2 - λ1
    
    if verbose:
        step(verbose, "RA difference", f"Δλ = {math.degrees(Δλ):.6f}°")
    
    # Vincenty formula (stable for all separations)
    sin_φ1, cos_φ1 = math.sin(φ1), math.cos(φ1)
    sin_φ2, cos_φ2 = math.sin(φ2), math.cos(φ2)
    sin_Δλ, cos_Δλ = math.sin(Δλ), math.cos(Δλ)
    
    if verbose:
        step(verbose, "Trigonometric values",
             f"sin(φ₁) = {sin_φ1:.10f}, cos(φ₁) = {cos_φ1:.10f}\n"
             f"sin(φ₂) = {sin_φ2:.10f}, cos(φ₂) = {cos_φ2:.10f}\n"
             f"sin(Δλ) = {sin_Δλ:.10f}, cos(Δλ) = {cos_Δλ:.10f}")
    
    # Numerator
    term1 = cos_φ2 * sin_Δλ
    term2 = cos_φ1 * sin_φ2 - sin_φ1 * cos_φ2 * cos_Δλ
    numerator = math.sqrt(term1**2 + term2**2)
    
    # Denominator
    denominator = sin_φ1 * sin_φ2 + cos_φ1 * cos_φ2 * cos_Δλ
    
    if verbose:
        step(verbose, "Vincenty formula",
             f"numerator = √[(cos φ₂ sin Δλ)² + (cos φ₁ sin φ₂ − sin φ₁ cos φ₂ cos Δλ)²]\n"
             f"          = √[{term1:.10f}² + {term2:.10f}²]\n"
             f"          = {numerator:.10f}\n\n"
             f"denominator = sin φ₁ sin φ₂ + cos φ₁ cos φ₂ cos Δλ\n"
             f"            = {denominator:.10f}")
    
    # Angular separation
    sep_rad = math.atan2(numerator, denominator)
    result = Angle(radians=sep_rad)
    
    if verbose:
        step(verbose, "Result",
             f"σ = atan2({numerator:.10f}, {denominator:.10f})\n"
             f"  = {result.degrees:.10f}°\n"
             f"  = {result.format_dms()}")
    
    return result


def position_angle(
    ra1: Angle, dec1: Angle,
    ra2: Angle, dec2: Angle,
    verbose: Optional[VerboseContext] = None
) -> Angle:
    """
    Calculate position angle from point 1 to point 2.
    
    Position angle is measured from North through East (counterclockwise).
    - 0° = North
    - 90° = East
    - 180° = South
    - 270° = West
    
    Args:
        ra1, dec1: First point (origin)
        ra2, dec2: Second point (target)
        verbose: Optional verbose context
    
    Returns:
        Position angle as an Angle in range [0, 360)
    """
    # Convert to radians
    λ1, φ1 = ra1.radians, dec1.radians
    λ2, φ2 = ra2.radians, dec2.radians
    
    if verbose:
        step(verbose, "Input coordinates",
             f"From: RA = {ra1.format_hms()}, Dec = {dec1.format_dms()}\n"
             f"To:   RA = {ra2.format_hms()}, Dec = {dec2.format_dms()}")
    
    Δλ = λ2 - λ1
    
    # Position angle formula
    y = math.sin(Δλ) * math.cos(φ2)
    x = math.cos(φ1) * math.sin(φ2) - math.sin(φ1) * math.cos(φ2) * math.cos(Δλ)
    
    if verbose:
        step(verbose, "Position angle formula",
             f"y = sin(Δλ) × cos(φ₂) = {y:.10f}\n"
             f"x = cos(φ₁) × sin(φ₂) − sin(φ₁) × cos(φ₂) × cos(Δλ) = {x:.10f}")
    
    pa_rad = math.atan2(y, x)
    result = Angle(radians=pa_rad).normalize()
    
    if verbose:
        step(verbose, "Result",
             f"PA = atan2({y:.10f}, {x:.10f})\n"
             f"   = {result.degrees:.6f}°")
    
    return result
