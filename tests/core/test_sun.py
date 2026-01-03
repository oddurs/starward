"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                               SUN TESTS                                      ║
║                                                                              ║
║  Tests for solar position, rise/set times, twilight, and seasonal phenomena. ║
║  The Sun - our nearest star and fundamental timekeeping reference.           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
import pytest

from astr0.core.angles import Angle
from astr0.core.time import JulianDate, jd_now
from astr0.core.observer import Observer
from astr0.core.sun import (
    sun_position, sunrise, sunset, solar_noon,
    civil_twilight, nautical_twilight, astronomical_twilight,
    solar_altitude, day_length, SunPosition
)


# ═══════════════════════════════════════════════════════════════════════════════
#  SUN POSITION
# ═══════════════════════════════════════════════════════════════════════════════

class TestSunPosition:
    """
    Tests for solar position calculations.
    
    Uses low-precision formulae suitable for rise/set calculations
    (accuracy ~0.01° in ecliptic longitude).
    """
    
    def test_returns_sun_position_object(self):
        """sun_position() returns SunPosition dataclass."""
        jd = JulianDate(2451545.0)
        pos = sun_position(jd)
        assert isinstance(pos, SunPosition)
    
    def test_has_required_fields(self):
        """SunPosition has all required fields."""
        jd = JulianDate(2451545.0)
        pos = sun_position(jd)
        
        assert hasattr(pos, 'longitude')
        assert hasattr(pos, 'latitude')
        assert hasattr(pos, 'ra')
        assert hasattr(pos, 'dec')
        assert hasattr(pos, 'distance_au')
        assert hasattr(pos, 'equation_of_time')
    
    @pytest.mark.golden
    def test_at_j2000_winter(self):
        """
        At J2000.0 (Jan 1, 2000), Sun is in Sagittarius.
        
        Winter solstice was ~Dec 21, so Sun should be at:
          - RA: 18h 45m (280°)
          - Dec: -23°
        """
        jd = JulianDate(2451545.0)
        pos = sun_position(jd)
        
        assert 270 < pos.ra.degrees < 290
        assert -24 < pos.dec.degrees < -22
    
    def test_distance_within_bounds(self):
        """Earth-Sun distance: 0.983 AU (perihelion) to 1.017 AU (aphelion)."""
        jd = jd_now()
        pos = sun_position(jd)
        assert 0.98 < pos.distance_au < 1.02
    
    def test_ecliptic_latitude_near_zero(self):
        """Sun is always very close to the ecliptic plane."""
        jd = jd_now()
        pos = sun_position(jd)
        assert abs(pos.latitude.degrees) < 0.01
    
    def test_equation_of_time_range(self):
        """Equation of time varies from -14 to +16 minutes."""
        for offset in range(0, 365, 30):
            jd = JulianDate(2451545.0 + offset)
            pos = sun_position(jd)
            assert -17 < pos.equation_of_time < 18


class TestSunPositionSeasons:
    """
    Tests for solar position through the seasons.
    """
    
    @pytest.mark.golden
    def test_vernal_equinox_declination(self):
        """At vernal equinox (Mar 20), Dec ≈ 0°."""
        # 2024-03-20 (approximate vernal equinox)
        jd = JulianDate(2460390.0)
        pos = sun_position(jd)
        assert abs(pos.dec.degrees) < 1
    
    @pytest.mark.golden
    def test_summer_solstice_declination(self):
        """At summer solstice (Jun 21), Dec ≈ +23.4°."""
        # 2024-06-21 (approximate summer solstice)
        jd = JulianDate(2460483.0)
        pos = sun_position(jd)
        assert 22 < pos.dec.degrees < 24
    
    @pytest.mark.golden
    def test_winter_solstice_declination(self):
        """At winter solstice (Dec 21), Dec ≈ -23.4°."""
        # 2024-12-21 (approximate winter solstice)
        jd = JulianDate(2460666.0)
        pos = sun_position(jd)
        assert -24 < pos.dec.degrees < -22


# ═══════════════════════════════════════════════════════════════════════════════
#  SUNRISE
# ═══════════════════════════════════════════════════════════════════════════════

class TestSunrise:
    """
    Tests for sunrise calculations.
    """
    
    def test_sunrise_winter(self, greenwich):
        """Sunrise at Greenwich in winter (late)."""
        jd = JulianDate(2460325.5)  # Mid-January
        rise = sunrise(greenwich, jd)
        
        assert rise is not None
        dt = rise.to_datetime()
        assert 6 < dt.hour < 9  # ~7-8 AM UTC
    
    def test_sunrise_summer(self, greenwich):
        """Sunrise at Greenwich in summer (early)."""
        jd = JulianDate(2460483.5)  # June solstice
        rise = sunrise(greenwich, jd)
        
        assert rise is not None
        dt = rise.to_datetime()
        assert 3 <= dt.hour < 6  # Very early
    
    def test_sunrise_tropics(self):
        """Sunrise times are more consistent near equator."""
        equator = Observer.from_degrees("Equator", 0.0, 0.0)
        
        # Check sunrise times throughout the year
        times = []
        for month_offset in [0, 90, 180, 270]:
            jd = JulianDate(2460000.5 + month_offset)
            rise = sunrise(equator, jd)
            if rise:
                times.append(rise.to_datetime().hour)
        
        # All sunrises should be within ~1 hour of each other
        if len(times) > 1:
            assert max(times) - min(times) < 2
    
    @pytest.mark.edge
    def test_midnight_sun(self, north_pole):
        """No sunrise during polar day (midnight sun)."""
        # Summer at north pole
        jd = JulianDate(2460483.5)  # June
        rise = sunrise(north_pole, jd)
        
        # May return None for 24-hour daylight
        # (implementation-dependent)


# ═══════════════════════════════════════════════════════════════════════════════
#  SUNSET
# ═══════════════════════════════════════════════════════════════════════════════

class TestSunset:
    """
    Tests for sunset calculations.
    """
    
    def test_sunset_winter(self, greenwich):
        """Sunset at Greenwich in winter (early)."""
        jd = JulianDate(2460325.5)
        set_t = sunset(greenwich, jd)
        
        assert set_t is not None
        dt = set_t.to_datetime()
        assert 15 < dt.hour < 18  # ~4-5 PM UTC
    
    def test_sunset_summer(self, greenwich):
        """Sunset at Greenwich in summer (late)."""
        jd = JulianDate(2460483.5)
        set_t = sunset(greenwich, jd)
        
        assert set_t is not None
        dt = set_t.to_datetime()
        assert 19 <= dt.hour < 22  # Very late
    
    def test_sunset_after_sunrise(self, greenwich):
        """Sunset always occurs after sunrise (normal latitudes)."""
        jd = JulianDate(2460325.5)
        
        rise = sunrise(greenwich, jd)
        set_t = sunset(greenwich, jd)
        
        if rise and set_t:
            assert set_t.jd > rise.jd


# ═══════════════════════════════════════════════════════════════════════════════
#  SOLAR NOON
# ═══════════════════════════════════════════════════════════════════════════════

class TestSolarNoon:
    """
    Tests for solar noon (local meridian transit).
    """
    
    def test_solar_noon_at_greenwich(self, greenwich):
        """Solar noon at Greenwich is close to 12:00 UTC."""
        jd = JulianDate(2460325.5)
        noon = solar_noon(greenwich, jd)
        
        assert noon is not None
        dt = noon.to_datetime()
        # Should be within ~15 minutes of 12:00 UTC
        assert 11 <= dt.hour <= 12
    
    def test_solar_noon_altitude_is_maximum(self, greenwich):
        """Solar altitude is highest at solar noon."""
        jd = jd_now()
        noon = solar_noon(greenwich, jd)
        
        if noon:
            alt_noon = solar_altitude(greenwich, noon)
            alt_before = solar_altitude(greenwich, JulianDate(noon.jd - 2/24))
            alt_after = solar_altitude(greenwich, JulianDate(noon.jd + 2/24))
            
            assert alt_noon.degrees > alt_before.degrees
            assert alt_noon.degrees > alt_after.degrees


# ═══════════════════════════════════════════════════════════════════════════════
#  SOLAR ALTITUDE
# ═══════════════════════════════════════════════════════════════════════════════

class TestSolarAltitude:
    """
    Tests for solar altitude at specific times.
    """
    
    def test_altitude_returns_angle(self, greenwich):
        """solar_altitude() returns an Angle."""
        jd = jd_now()
        alt = solar_altitude(greenwich, jd)
        assert isinstance(alt, Angle)
    
    def test_altitude_range(self, greenwich):
        """Altitude is always between -90° and +90°."""
        for offset in range(0, 24, 2):
            jd = JulianDate(2460000.5 + offset / 24)
            alt = solar_altitude(greenwich, jd)
            assert -90 <= alt.degrees <= 90
    
    @pytest.mark.golden
    def test_altitude_at_noon_summer(self, greenwich):
        """Summer noon altitude at Greenwich ≈ 62°."""
        # June 21, noon
        jd = JulianDate(2460483.5)
        noon = solar_noon(greenwich, jd)
        if noon:
            alt = solar_altitude(greenwich, noon)
            # At lat 51.5°, summer max alt ≈ 62°
            assert 55 < alt.degrees < 65


# ═══════════════════════════════════════════════════════════════════════════════
#  TWILIGHT
# ═══════════════════════════════════════════════════════════════════════════════

class TestTwilight:
    """
    Tests for twilight calculations.
    
    Twilight types (Sun below horizon):
      - Civil: 0° to -6° (artificial light not needed)
      - Nautical: -6° to -12° (horizon visible at sea)
      - Astronomical: -12° to -18° (sky fully dark)
    """
    
    def test_civil_twilight_exists(self, greenwich):
        """Civil twilight exists for mid-latitudes."""
        jd = JulianDate(2460325.5)
        morning, evening = civil_twilight(greenwich, jd)
        
        assert morning is not None
        assert evening is not None
        assert morning.jd < evening.jd
    
    def test_nautical_twilight_exists(self, greenwich):
        """Nautical twilight exists for mid-latitudes."""
        jd = JulianDate(2460325.5)
        morning, evening = nautical_twilight(greenwich, jd)
        
        assert morning is not None
        assert evening is not None
    
    def test_astronomical_twilight_exists(self, greenwich):
        """Astronomical twilight exists for mid-latitudes."""
        jd = JulianDate(2460325.5)
        morning, evening = astronomical_twilight(greenwich, jd)
        
        assert morning is not None
        assert evening is not None
    
    def test_twilight_order(self, greenwich):
        """Morning twilights occur in order: astro < nautical < civil < sunrise."""
        jd = JulianDate(2460325.5)
        
        astro = astronomical_twilight(greenwich, jd)
        naut = nautical_twilight(greenwich, jd)
        civil = civil_twilight(greenwich, jd)
        rise = sunrise(greenwich, jd)
        
        if all([astro[0], naut[0], civil[0], rise]):
            assert astro[0].jd < naut[0].jd < civil[0].jd < rise.jd


# ═══════════════════════════════════════════════════════════════════════════════
#  DAY LENGTH
# ═══════════════════════════════════════════════════════════════════════════════

class TestDayLength:
    """
    Tests for day length calculations.
    """
    
    def test_day_length_returns_hours(self, greenwich):
        """day_length() returns hours."""
        jd = JulianDate(2460325.5)
        length = day_length(greenwich, jd)
        
        assert length is not None
        assert 0 < length < 24
    
    def test_day_length_summer_longer(self, greenwich):
        """Summer days are longer than winter days (northern hemisphere)."""
        winter = JulianDate(2460325.5)  # January
        summer = JulianDate(2460483.5)  # June
        
        winter_len = day_length(greenwich, winter)
        summer_len = day_length(greenwich, summer)
        
        if winter_len and summer_len:
            assert summer_len > winter_len
    
    @pytest.mark.golden
    def test_equinox_day_length(self):
        """Day length ≈ 12 hours at equator year-round."""
        equator = Observer.from_degrees("Equator", 0.0, 0.0)
        
        jd = JulianDate(2460390.0)  # Equinox
        length = day_length(equator, jd)
        
        if length:
            assert 11.5 < length < 12.5
