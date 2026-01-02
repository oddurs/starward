"""
Time representations and conversions for astronomy.

Supports Julian Date, Modified Julian Date, and various time scales.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Union

from astr0.core.constants import CONSTANTS
from astr0.verbose import VerboseContext, step


@dataclass(frozen=True)
class JulianDate:
    """
    Represents a Julian Date with full precision.
    
    Julian Date is the continuous count of days since the beginning of
    the Julian Period (January 1, 4713 BC in the proleptic Julian calendar).
    
    Create from various sources:
        >>> JulianDate(2460000.5)
        >>> JulianDate.from_datetime(datetime.now(timezone.utc))
        >>> JulianDate.from_mjd(60000.0)
        >>> JulianDate.j2000()
    """
    
    jd: float
    
    @classmethod
    def j2000(cls) -> JulianDate:
        """Return the Julian Date of J2000.0 epoch."""
        return cls(float(CONSTANTS.JD_J2000))
    
    @classmethod
    def from_mjd(cls, mjd: float) -> JulianDate:
        """Create from Modified Julian Date."""
        return cls(mjd + float(CONSTANTS.MJD_OFFSET))
    
    @classmethod
    def from_datetime(
        cls, 
        dt: datetime,
        verbose: Optional[VerboseContext] = None
    ) -> JulianDate:
        """
        Create from a Python datetime object.
        
        The datetime should be in UTC for accurate results.
        """
        # Ensure we're working with UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        elif dt.tzinfo != timezone.utc:
            dt = dt.astimezone(timezone.utc)
        
        year = dt.year
        month = dt.month
        day = dt.day
        
        # Fractional day from hours, minutes, seconds
        day_fraction = (
            dt.hour / 24.0 +
            dt.minute / 1440.0 +
            dt.second / 86400.0 +
            dt.microsecond / 86400000000.0
        )
        
        if verbose:
            step(verbose, "Input datetime",
                 f"{dt.isoformat()}\n"
                 f"Year: {year}, Month: {month}, Day: {day}\n"
                 f"Day fraction: {day_fraction:.10f}")
        
        # Algorithm from Meeus, "Astronomical Algorithms"
        if month <= 2:
            year -= 1
            month += 12
        
        a = int(year / 100)
        b = 2 - a + int(a / 4)  # Gregorian calendar correction
        
        if verbose:
            step(verbose, "Calendar correction (Gregorian)",
                 f"A = int({year + (1 if month > 2 else 0)}/100) = {a}\n"
                 f"B = 2 - A + int(A/4) = {b}")
        
        jd = (
            int(365.25 * (year + 4716)) +
            int(30.6001 * (month + 1)) +
            day + day_fraction +
            b - 1524.5
        )
        
        if verbose:
            step(verbose, "Julian Date calculation",
                 f"JD = int(365.25 × (Y + 4716)) + int(30.6001 × (M + 1)) + D + B − 1524.5\n"
                 f"   = int(365.25 × {year + 4716}) + int(30.6001 × {month + 1}) + {day + day_fraction:.10f} + {b} − 1524.5\n"
                 f"   = {int(365.25 * (year + 4716))} + {int(30.6001 * (month + 1))} + {day + day_fraction:.10f} + {b} − 1524.5\n"
                 f"   = {jd:.10f}")
        
        return cls(jd)
    
    @classmethod
    def from_calendar(
        cls,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: float = 0.0,
        verbose: Optional[VerboseContext] = None
    ) -> JulianDate:
        """Create from calendar date components (assumed UTC)."""
        micro = int((second % 1) * 1_000_000)
        dt = datetime(
            year, month, day,
            hour, minute, int(second), micro,
            tzinfo=timezone.utc
        )
        return cls.from_datetime(dt, verbose=verbose)
    
    @property
    def mjd(self) -> float:
        """Modified Julian Date."""
        return self.jd - float(CONSTANTS.MJD_OFFSET)
    
    @property
    def t_j2000(self) -> float:
        """Julian centuries since J2000.0."""
        return (self.jd - float(CONSTANTS.JD_J2000)) / float(CONSTANTS.JULIAN_CENTURY)
    
    @property
    def t_j2000_days(self) -> float:
        """Days since J2000.0."""
        return self.jd - float(CONSTANTS.JD_J2000)
    
    def to_datetime(self, verbose: Optional[VerboseContext] = None) -> datetime:
        """
        Convert to Python datetime in UTC.
        
        Algorithm from Meeus, "Astronomical Algorithms" Ch. 7
        """
        jd = self.jd + 0.5
        z = int(jd)
        f = jd - z
        
        if verbose:
            step(verbose, "Initial decomposition",
                 f"JD + 0.5 = {jd:.10f}\n"
                 f"Z (integer part) = {z}\n"
                 f"F (fractional part) = {f:.10f}")
        
        if z < 2299161:
            a = z
        else:
            alpha = int((z - 1867216.25) / 36524.25)
            a = z + 1 + alpha - int(alpha / 4)
        
        if verbose and z >= 2299161:
            step(verbose, "Gregorian correction",
                 f"α = int((Z - 1867216.25) / 36524.25) = {alpha}\n"
                 f"A = Z + 1 + α - int(α/4) = {a}")
        
        b = a + 1524
        c = int((b - 122.1) / 365.25)
        d = int(365.25 * c)
        e = int((b - d) / 30.6001)
        
        day = b - d - int(30.6001 * e)
        
        if e < 14:
            month = e - 1
        else:
            month = e - 13
        
        if month > 2:
            year = c - 4716
        else:
            year = c - 4715
        
        if verbose:
            step(verbose, "Date extraction",
                 f"Year: {year}, Month: {month}, Day: {day}")
        
        # Convert fractional day to time
        hours_total = f * 24
        hour = int(hours_total)
        minutes_total = (hours_total - hour) * 60
        minute = int(minutes_total)
        seconds_total = (minutes_total - minute) * 60
        second = int(seconds_total)
        microsecond = int((seconds_total - second) * 1_000_000)
        
        if verbose:
            step(verbose, "Time extraction",
                 f"Fractional day = {f:.10f}\n"
                 f"Hours: {hour}, Minutes: {minute}, Seconds: {second}.{microsecond:06d}")
        
        return datetime(year, month, day, hour, minute, second, microsecond, tzinfo=timezone.utc)
    
    def gmst(self, verbose: Optional[VerboseContext] = None) -> float:
        """
        Greenwich Mean Sidereal Time in hours.
        
        Uses the IAU 2006 precession model.
        """
        # Julian centuries from J2000.0
        t = self.t_j2000
        
        if verbose:
            step(verbose, "Julian centuries since J2000.0",
                 f"T = (JD - 2451545.0) / 36525\n"
                 f"  = ({self.jd:.10f} - 2451545.0) / 36525\n"
                 f"  = {t:.12f}")
        
        # Mean sidereal time at Greenwich in seconds
        # IAU 2006 precession model
        gmst_sec = (
            67310.54841 +
            (876600.0 * 3600 + 8640184.812866) * t +
            0.093104 * t**2 -
            6.2e-6 * t**3
        )
        
        if verbose:
            step(verbose, "GMST calculation (IAU 2006)",
                 f"θ = 67310.54841 + (876600×3600 + 8640184.812866)×T + 0.093104×T² − 6.2×10⁻⁶×T³\n"
                 f"  = 67310.54841 + {(876600.0 * 3600 + 8640184.812866) * t:.6f} + "
                 f"{0.093104 * t**2:.10f} − {6.2e-6 * t**3:.10f}\n"
                 f"  = {gmst_sec:.6f} seconds")
        
        # Convert to hours and normalize
        gmst_hours = (gmst_sec / 3600.0) % 24
        if gmst_hours < 0:
            gmst_hours += 24
        
        if verbose:
            step(verbose, "Result",
                 f"GMST = {gmst_hours:.10f} hours\n"
                 f"     = {int(gmst_hours)}h {int((gmst_hours % 1) * 60)}m "
                 f"{((gmst_hours * 60) % 1) * 60:.2f}s")
        
        return gmst_hours
    
    def lst(
        self, 
        longitude_deg: float,
        verbose: Optional[VerboseContext] = None
    ) -> float:
        """
        Local Sidereal Time at given longitude (degrees, positive East).
        
        Returns hours in range [0, 24).
        """
        gmst = self.gmst(verbose=verbose)
        
        # Convert longitude to hours
        lon_hours = longitude_deg / 15.0
        
        if verbose:
            step(verbose, "Longitude correction",
                 f"Longitude = {longitude_deg:.6f}° = {lon_hours:.10f} hours")
        
        lst = (gmst + lon_hours) % 24
        if lst < 0:
            lst += 24
        
        if verbose:
            step(verbose, "Local Sidereal Time",
                 f"LST = GMST + longitude_hours\n"
                 f"    = {gmst:.10f} + {lon_hours:.10f}\n"
                 f"    = {lst:.10f} hours")
        
        return lst
    
    def __add__(self, days: float) -> JulianDate:
        """Add days to Julian Date."""
        return JulianDate(self.jd + days)
    
    def __sub__(self, other: Union[JulianDate, float]) -> Union[JulianDate, float]:
        """Subtract days or another JulianDate."""
        if isinstance(other, JulianDate):
            return self.jd - other.jd
        return JulianDate(self.jd - other)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, JulianDate):
            return NotImplemented
        return math.isclose(self.jd, other.jd, rel_tol=1e-12)
    
    def __lt__(self, other: JulianDate) -> bool:
        return self.jd < other.jd
    
    def __le__(self, other: JulianDate) -> bool:
        return self.jd <= other.jd
    
    def __repr__(self) -> str:
        return f"JulianDate({self.jd:.10f})"
    
    def __str__(self) -> str:
        return f"JD {self.jd:.6f}"


# Convenience functions

def jd_now() -> JulianDate:
    """Return the current Julian Date."""
    return JulianDate.from_datetime(datetime.now(timezone.utc))


def utc_to_jd(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: float = 0.0,
    verbose: Optional[VerboseContext] = None
) -> JulianDate:
    """Convert calendar date (UTC) to Julian Date."""
    return JulianDate.from_calendar(year, month, day, hour, minute, second, verbose=verbose)


def jd_to_utc(jd: float, verbose: Optional[VerboseContext] = None) -> datetime:
    """Convert Julian Date to datetime (UTC)."""
    return JulianDate(jd).to_datetime(verbose=verbose)


def mjd_to_jd(mjd: float) -> float:
    """Convert Modified Julian Date to Julian Date."""
    return mjd + float(CONSTANTS.MJD_OFFSET)


def jd_to_mjd(jd: float) -> float:
    """Convert Julian Date to Modified Julian Date."""
    return jd - float(CONSTANTS.MJD_OFFSET)
