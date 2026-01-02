"""
Tests for the constants module.
"""

import pytest

from astr0.core.constants import CONSTANTS, Constant


class TestConstant:
    """Tests for the Constant dataclass."""
    
    def test_float_conversion(self):
        c = Constant(name="Test", value=299792458.0, unit="m/s")
        assert float(c) == 299792458.0
    
    def test_repr(self):
        c = Constant(name="Test", value=1.0, unit="m")
        assert "Test" in repr(c)
        assert "1.0" in repr(c)
        assert "m" in repr(c)
    
    def test_repr_with_uncertainty(self):
        c = Constant(name="Test", value=1.0, unit="m", uncertainty=0.1)
        assert "±" in repr(c)


class TestAstronomicalConstants:
    """Tests for the AstronomicalConstants class."""
    
    def test_speed_of_light(self):
        assert CONSTANTS.c.value == 299792458.0
        assert CONSTANTS.c.unit == "m/s"
    
    def test_au_exact(self):
        """AU is exact by definition since 2012."""
        assert CONSTANTS.AU.value == 149597870700.0
        assert CONSTANTS.AU.uncertainty == 0.0
    
    def test_j2000_jd(self):
        """J2000.0 Julian Date."""
        assert CONSTANTS.JD_J2000.value == 2451545.0
    
    def test_mjd_offset(self):
        """MJD offset value."""
        assert CONSTANTS.MJD_OFFSET.value == 2400000.5
    
    def test_julian_century(self):
        """Julian century in days."""
        assert CONSTANTS.JULIAN_CENTURY.value == 36525.0
    
    def test_list_all(self):
        """list_all should return all constants."""
        all_constants = CONSTANTS.list_all()
        assert len(all_constants) > 10
        assert all(isinstance(c, Constant) for c in all_constants)
    
    def test_search_speed(self):
        """Search should find speed of light."""
        results = CONSTANTS.search("speed")
        assert len(results) == 1
        assert results[0].name == "Speed of light"
    
    def test_search_solar(self):
        """Search should find solar constants."""
        results = CONSTANTS.search("solar")
        assert len(results) >= 3  # Mass, radius, luminosity
    
    def test_search_case_insensitive(self):
        """Search should be case insensitive."""
        results1 = CONSTANTS.search("SOLAR")
        results2 = CONSTANTS.search("solar")
        assert len(results1) == len(results2)
    
    def test_galactic_pole_values(self):
        """Galactic pole coordinates should be correct."""
        assert abs(CONSTANTS.GALACTIC_POLE_RA.value - 192.86) < 0.01
        assert abs(CONSTANTS.GALACTIC_POLE_DEC.value - 27.13) < 0.01


class TestPhysicalConsistency:
    """Tests for physical consistency of constants."""
    
    def test_julian_year_days(self):
        """Julian year should be 365.25 days."""
        assert CONSTANTS.JULIAN_YEAR.value == 365.25
    
    def test_julian_century_is_100_years(self):
        """Julian century should be 100 Julian years."""
        assert CONSTANTS.JULIAN_CENTURY.value == 100 * CONSTANTS.JULIAN_YEAR.value
    
    def test_arcsec_per_radian(self):
        """Check arcsec per radian calculation."""
        import math
        expected = 3600 * 180 / math.pi
        assert abs(CONSTANTS.ARCSEC_PER_RADIAN.value - expected) < 1e-6
