"""
Tests for the time module.
"""

import math
from datetime import datetime, timezone
import pytest

from astr0.core.time import (
    JulianDate, jd_now, utc_to_jd, jd_to_utc,
    mjd_to_jd, jd_to_mjd
)
from astr0.core.constants import CONSTANTS
from astr0.verbose import VerboseContext


class TestJulianDateCreation:
    """Tests for JulianDate instantiation."""
    
    def test_direct_creation(self):
        jd = JulianDate(2451545.0)
        assert jd.jd == 2451545.0
    
    def test_j2000(self):
        jd = JulianDate.j2000()
        assert jd.jd == 2451545.0
    
    def test_from_mjd(self):
        jd = JulianDate.from_mjd(51544.5)
        assert math.isclose(jd.jd, 2451545.0, rel_tol=1e-10)
    
    def test_from_datetime_j2000(self):
        """J2000.0 is 2000-01-01 12:00:00 UTC."""
        dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        jd = JulianDate.from_datetime(dt)
        assert math.isclose(jd.jd, 2451545.0, rel_tol=1e-10)
    
    def test_from_calendar(self):
        jd = JulianDate.from_calendar(2000, 1, 1, 12, 0, 0)
        assert math.isclose(jd.jd, 2451545.0, rel_tol=1e-10)


class TestJulianDateKnownValues:
    """Test against known Julian Date values from authoritative sources."""
    
    # Test values from USNO/Naval Observatory
    KNOWN_VALUES = [
        # (year, month, day, hour, minute, second, expected_jd)
        (2000, 1, 1, 12, 0, 0, 2451545.0),  # J2000.0
        (1858, 11, 17, 0, 0, 0, 2400000.5),  # MJD epoch
        (2024, 1, 1, 0, 0, 0, 2460310.5),
        (1999, 12, 31, 0, 0, 0, 2451543.5),
        (2100, 1, 1, 0, 0, 0, 2488069.5),
    ]
    
    @pytest.mark.parametrize("y,m,d,h,mi,s,expected", KNOWN_VALUES)
    def test_known_jd(self, y, m, d, h, mi, s, expected):
        jd = JulianDate.from_calendar(y, m, d, h, mi, s)
        assert math.isclose(jd.jd, expected, rel_tol=1e-9)


class TestJulianDateRoundtrip:
    """Test that datetime → JD → datetime gives the same result."""
    
    def test_roundtrip_j2000(self):
        original = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        jd = JulianDate.from_datetime(original)
        result = jd.to_datetime()
        
        # Should be within a microsecond
        delta = abs((result - original).total_seconds())
        assert delta < 1e-6
    
    def test_roundtrip_arbitrary_date(self):
        original = datetime(2024, 6, 15, 14, 30, 45, 123456, tzinfo=timezone.utc)
        jd = JulianDate.from_datetime(original)
        result = jd.to_datetime()
        
        delta = abs((result - original).total_seconds())
        assert delta < 1e-5  # Microsecond precision
    
    def test_roundtrip_jd_to_datetime_to_jd(self):
        original_jd = 2460000.123456
        jd = JulianDate(original_jd)
        dt = jd.to_datetime()
        back = JulianDate.from_datetime(dt)
        
        assert math.isclose(back.jd, original_jd, rel_tol=1e-10)


class TestMJDConversions:
    """Tests for Modified Julian Date conversions."""
    
    def test_mjd_property(self):
        jd = JulianDate(2451545.0)
        assert math.isclose(jd.mjd, 51544.5, rel_tol=1e-10)
    
    def test_mjd_to_jd_function(self):
        assert math.isclose(mjd_to_jd(51544.5), 2451545.0, rel_tol=1e-10)
    
    def test_jd_to_mjd_function(self):
        assert math.isclose(jd_to_mjd(2451545.0), 51544.5, rel_tol=1e-10)


class TestJulianCenturies:
    """Tests for Julian centuries since J2000.0."""
    
    def test_t_j2000_at_j2000(self):
        jd = JulianDate.j2000()
        assert math.isclose(jd.t_j2000, 0.0, abs_tol=1e-10)
    
    def test_t_j2000_one_century_later(self):
        # J2100.0 should be 1 century after J2000.0
        jd = JulianDate(2451545.0 + 36525.0)
        assert math.isclose(jd.t_j2000, 1.0, rel_tol=1e-10)


class TestGMST:
    """Tests for Greenwich Mean Sidereal Time."""
    
    def test_gmst_at_j2000(self):
        """GMST at J2000.0 should be approximately 18h 41m."""
        jd = JulianDate.j2000()
        gmst = jd.gmst()
        # Expected: approximately 18.697 hours (from USNO)
        assert 18.6 < gmst < 18.8
    
    def test_gmst_range(self):
        """GMST should always be in [0, 24) hours."""
        for offset in [0, 100, 1000, -100, -1000]:
            jd = JulianDate.j2000() + offset
            gmst = jd.gmst()
            assert 0 <= gmst < 24
    
    def test_gmst_verbose(self):
        """Test verbose output."""
        ctx = VerboseContext()
        jd = JulianDate.j2000()
        jd.gmst(verbose=ctx)
        assert len(ctx.steps) > 0


class TestLST:
    """Tests for Local Sidereal Time."""
    
    def test_lst_at_greenwich(self):
        """LST at Greenwich (lon=0) should equal GMST."""
        jd = JulianDate.j2000()
        gmst = jd.gmst()
        lst = jd.lst(0.0)
        assert math.isclose(lst, gmst, rel_tol=1e-10)
    
    def test_lst_180_east(self):
        """LST at 180° East should be GMST + 12h."""
        jd = JulianDate.j2000()
        gmst = jd.gmst()
        lst = jd.lst(180.0)
        expected = (gmst + 12.0) % 24
        assert math.isclose(lst, expected, rel_tol=1e-10)
    
    def test_lst_range(self):
        """LST should always be in [0, 24) hours."""
        jd = JulianDate.j2000()
        for lon in [-180, -90, 0, 90, 180]:
            lst = jd.lst(lon)
            assert 0 <= lst < 24


class TestJulianDateArithmetic:
    """Tests for arithmetic operations."""
    
    def test_add_days(self):
        jd = JulianDate(2451545.0)
        result = jd + 1.0
        assert result.jd == 2451546.0
    
    def test_subtract_days(self):
        jd = JulianDate(2451545.0)
        result = jd - 1.0
        assert isinstance(result, JulianDate)
        assert result.jd == 2451544.0
    
    def test_subtract_jd(self):
        jd1 = JulianDate(2451545.0)
        jd2 = JulianDate(2451544.0)
        result = jd1 - jd2
        assert isinstance(result, float)
        assert result == 1.0


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_jd_now(self):
        """jd_now() should return a reasonable JD."""
        jd = jd_now()
        # Should be after J2000.0
        assert jd.jd > 2451545.0
        # Should be before year 3000
        assert jd.jd < 2816788.0
    
    def test_utc_to_jd(self):
        jd = utc_to_jd(2000, 1, 1, 12, 0, 0)
        assert math.isclose(jd.jd, 2451545.0, rel_tol=1e-10)
    
    def test_jd_to_utc(self):
        dt = jd_to_utc(2451545.0)
        assert dt.year == 2000
        assert dt.month == 1
        assert dt.day == 1
        assert dt.hour == 12
