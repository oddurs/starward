"""
starward — Astronomy Calculation Toolkit

A professional astronomy calculation toolkit with a soul.
"""

__version__ = "0.4.0"
__author__ = "starward contributors"

# Convenient imports for library usage
from starward.core.angles import Angle, angular_separation, position_angle
from starward.core.time import JulianDate, jd_now, utc_to_jd, jd_to_utc
from starward.core.coords import (
    ICRSCoord,
    GalacticCoord,
    HorizontalCoord,
    transform_coords,
)
from starward.core.constants import CONSTANTS
from starward.core.precision import (
    PrecisionConfig,
    PrecisionLevel,
    get_precision,
    set_precision,
    precision_context,
)
from starward.core.planets import (
    Planet,
    PlanetPosition,
    planet_position,
    all_planet_positions,
)

__all__ = [
    # Version
    "__version__",
    # Angles
    "Angle",
    "angular_separation",
    "position_angle",
    # Time
    "JulianDate",
    "jd_now",
    "utc_to_jd",
    "jd_to_utc",
    # Coordinates
    "ICRSCoord",
    "GalacticCoord",
    "HorizontalCoord",
    "transform_coords",
    # Constants
    "CONSTANTS",
    # Precision
    "PrecisionConfig",
    "PrecisionLevel",
    "get_precision",
    "set_precision",
    "precision_context",
    # Planets
    "Planet",
    "PlanetPosition",
    "planet_position",
    "all_planet_positions",
]
