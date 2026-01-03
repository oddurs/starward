"""
Precision and formatting standards for astr0.

This module defines precision levels for numerical output across the toolkit.
All calculations are performed in full IEEE 754 double precision (float64),
but display precision can be configured based on use case.

Precision Levels:
    FULL (15)      - Full double precision (~15-17 significant digits)
    HIGH (10)      - High precision for research applications
    STANDARD (6)   - Default for most astronomical calculations  
    DISPLAY (4)    - Readable precision for casual use
    COMPACT (2)    - Minimal precision for quick reference

The internal calculations NEVER sacrifice precision - only the display output
is affected by these settings.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import os


class PrecisionLevel(Enum):
    """Predefined precision levels for different use cases."""
    
    COMPACT = 2      # Quick reference: 3.14
    DISPLAY = 4      # Readable: 3.1416
    STANDARD = 6     # Default: 3.141593
    HIGH = 10        # Research: 3.1415926536
    FULL = 15        # Maximum: 3.14159265358979
    
    @classmethod
    def from_string(cls, s: str) -> 'PrecisionLevel':
        """Parse precision level from string."""
        try:
            return cls[s.upper()]
        except KeyError:
            # Try parsing as integer
            try:
                n = int(s)
                # Find closest predefined level or use custom
                for level in cls:
                    if level.value == n:
                        return level
                # Return as custom integer precision
                return n
            except ValueError:
                raise ValueError(
                    f"Invalid precision: '{s}'. "
                    f"Use {', '.join(l.name.lower() for l in cls)} or an integer."
                )


@dataclass
class PrecisionConfig:
    """
    Configuration for numerical precision in output.
    
    All internal calculations use full double precision.
    This only affects how results are displayed.
    
    Attributes:
        decimals: Number of decimal places for floating point numbers
        angle_arcsec: Decimal places for arcseconds in angle display
        time_seconds: Decimal places for seconds in time display
        coordinates: Decimal places for coordinate values (degrees/radians)
        scientific_threshold: Use scientific notation beyond this magnitude
    """
    
    decimals: int = 6           # General floating point
    angle_arcsec: int = 2       # Arcseconds: 45° 30' 15.23"
    time_seconds: int = 2       # Time seconds: 12h 30m 45.67s
    coordinates: int = 6        # Coordinate degrees: 123.456789°
    radians: int = 15           # Radians always full precision by default
    scientific_threshold: int = 6  # Use scientific notation for |exp| > this
    
    @classmethod
    def from_level(cls, level: PrecisionLevel | int) -> 'PrecisionConfig':
        """Create config from a precision level."""
        if isinstance(level, int):
            decimals = level
        else:
            decimals = level.value
        
        # Scale other precisions based on main decimals setting
        return cls(
            decimals=decimals,
            angle_arcsec=min(decimals, 3),  # Cap arcsec at 3 (0.001" = 0.5 microarcsec)
            time_seconds=min(decimals, 3),   # Cap time at 3 (milliseconds)
            coordinates=decimals,
            radians=max(decimals, 10),       # Radians get at least 10 decimals
            scientific_threshold=max(6, decimals),
        )
    
    @classmethod
    def compact(cls) -> 'PrecisionConfig':
        """Minimal precision for quick reference."""
        return cls.from_level(PrecisionLevel.COMPACT)
    
    @classmethod
    def display(cls) -> 'PrecisionConfig':
        """Readable precision for casual use."""
        return cls.from_level(PrecisionLevel.DISPLAY)
    
    @classmethod
    def standard(cls) -> 'PrecisionConfig':
        """Default precision for most calculations."""
        return cls.from_level(PrecisionLevel.STANDARD)
    
    @classmethod
    def high(cls) -> 'PrecisionConfig':
        """High precision for research applications."""
        return cls.from_level(PrecisionLevel.HIGH)
    
    @classmethod
    def full(cls) -> 'PrecisionConfig':
        """Full double precision display."""
        return cls.from_level(PrecisionLevel.FULL)
    
    def format_float(self, value: float, use_scientific: bool = True) -> str:
        """Format a floating point number according to precision settings."""
        if value == 0:
            return f"0.{'0' * self.decimals}"
        
        abs_val = abs(value)
        exp = 0 if abs_val == 0 else int(f"{abs_val:e}".split('e')[1])
        
        if use_scientific and abs(exp) > self.scientific_threshold:
            return f"{value:.{self.decimals}e}"
        return f"{value:.{self.decimals}f}"
    
    def format_radians(self, value: float) -> str:
        """Format a value in radians."""
        return f"{value:.{self.radians}f}"
    
    def format_degrees(self, value: float) -> str:
        """Format a value in degrees."""
        return f"{value:.{self.coordinates}f}"


# Global precision configuration
_global_precision: PrecisionConfig = PrecisionConfig.standard()


def get_precision() -> PrecisionConfig:
    """Get the current global precision configuration."""
    return _global_precision


def set_precision(config: PrecisionConfig | PrecisionLevel | int | str) -> None:
    """
    Set the global precision configuration.
    
    Args:
        config: Can be:
            - PrecisionConfig instance
            - PrecisionLevel enum value
            - Integer (number of decimal places)
            - String ('full', 'high', 'standard', 'display', 'compact', or integer)
    
    Examples:
        set_precision(PrecisionLevel.FULL)
        set_precision(10)
        set_precision('high')
        set_precision(PrecisionConfig(decimals=8, angle_arcsec=3))
    """
    global _global_precision
    
    if isinstance(config, PrecisionConfig):
        _global_precision = config
    elif isinstance(config, PrecisionLevel):
        _global_precision = PrecisionConfig.from_level(config)
    elif isinstance(config, int):
        _global_precision = PrecisionConfig.from_level(config)
    elif isinstance(config, str):
        level = PrecisionLevel.from_string(config)
        if isinstance(level, int):
            _global_precision = PrecisionConfig.from_level(level)
        else:
            _global_precision = PrecisionConfig.from_level(level)
    else:
        raise TypeError(f"Invalid precision type: {type(config)}")


def precision_context(config: PrecisionConfig | PrecisionLevel | int | str):
    """
    Context manager for temporary precision changes.
    
    Example:
        with precision_context(PrecisionLevel.FULL):
            print(angle)  # Full precision
        print(angle)  # Back to previous precision
    """
    class PrecisionContext:
        def __init__(self, new_config):
            self.new_config = new_config
            self.old_config = None
        
        def __enter__(self):
            self.old_config = get_precision()
            set_precision(self.new_config)
            return get_precision()
        
        def __exit__(self, *args):
            global _global_precision
            _global_precision = self.old_config
    
    return PrecisionContext(config)


# Initialize from environment variable if set
_env_precision = os.environ.get('ASTR0_PRECISION')
if _env_precision:
    try:
        set_precision(_env_precision)
    except ValueError:
        pass  # Ignore invalid env var


# Convenience constants for format strings
def _decimals() -> int:
    """Get current decimal precision."""
    return _global_precision.decimals

def _arcsec() -> int:
    """Get current arcsecond precision."""
    return _global_precision.angle_arcsec

def _time_sec() -> int:
    """Get current time seconds precision."""
    return _global_precision.time_seconds
