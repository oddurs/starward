"""
Tests for the angles module.
"""

import math
import pytest

from astr0.core.angles import Angle, angular_separation, position_angle
from astr0.verbose import VerboseContext


class TestAngleCreation:
    """Tests for Angle instantiation and parsing."""
    
    def test_from_degrees(self):
        a = Angle(degrees=45.5)
        assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)
    
    def test_from_radians(self):
        a = Angle(radians=math.pi / 4)
        assert math.isclose(a.degrees, 45.0, rel_tol=1e-10)
    
    def test_from_hours(self):
        a = Angle(hours=12.0)
        assert math.isclose(a.degrees, 180.0, rel_tol=1e-10)
    
    def test_from_arcminutes(self):
        a = Angle(arcminutes=60.0)
        assert math.isclose(a.degrees, 1.0, rel_tol=1e-10)
    
    def test_from_arcseconds(self):
        a = Angle(arcseconds=3600.0)
        assert math.isclose(a.degrees, 1.0, rel_tol=1e-10)
    
    def test_from_dms(self):
        a = Angle.from_dms(45, 30, 0)
        assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)
    
    def test_from_dms_negative(self):
        a = Angle.from_dms(-45, 30, 0)
        assert math.isclose(a.degrees, -45.5, rel_tol=1e-10)
    
    def test_from_hms(self):
        a = Angle.from_hms(12, 30, 0)
        assert math.isclose(a.hours, 12.5, rel_tol=1e-10)
    
    def test_requires_exactly_one_unit(self):
        with pytest.raises(ValueError, match="Exactly one"):
            Angle()
        
        with pytest.raises(ValueError, match="Exactly one"):
            Angle(degrees=45, radians=0.5)


class TestAngleParsing:
    """Tests for Angle.parse()."""
    
    def test_parse_degrees_plain(self):
        a = Angle.parse("45.5")
        assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)
    
    def test_parse_degrees_with_d(self):
        a = Angle.parse("45.5d")
        assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)
    
    def test_parse_dms(self):
        a = Angle.parse("45d30m00s")
        assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)
    
    def test_parse_dms_unicode(self):
        a = Angle.parse("45°30′00″")
        assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)
    
    def test_parse_hms(self):
        a = Angle.parse("12h30m00s")
        assert math.isclose(a.hours, 12.5, rel_tol=1e-10)
    
    def test_parse_colon_separated(self):
        a = Angle.parse("45:30:00")
        assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)
    
    def test_parse_space_separated(self):
        a = Angle.parse("45 30 00")
        assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)
    
    def test_parse_negative(self):
        a = Angle.parse("-45d30m00s")
        assert math.isclose(a.degrees, -45.5, rel_tol=1e-10)
    
    def test_parse_invalid(self):
        with pytest.raises(ValueError, match="Cannot parse"):
            Angle.parse("not an angle")


class TestAngleConversions:
    """Tests for angle unit conversions."""
    
    def test_to_dms(self):
        a = Angle(degrees=45.5)
        d, m, s = a.to_dms()
        assert d == 45
        assert m == 30
        assert math.isclose(s, 0.0, abs_tol=1e-10)
    
    def test_to_dms_negative(self):
        a = Angle(degrees=-45.5)
        d, m, s = a.to_dms()
        assert d == -45
        assert m == 30
        assert math.isclose(s, 0.0, abs_tol=1e-10)
    
    def test_to_hms(self):
        a = Angle(hours=12.5)
        h, m, s = a.to_hms()
        assert h == 12
        assert m == 30
        assert math.isclose(s, 0.0, abs_tol=1e-10)
    
    def test_radians_property(self):
        a = Angle(degrees=180)
        assert math.isclose(a.radians, math.pi, rel_tol=1e-10)
    
    def test_hours_property(self):
        a = Angle(degrees=180)
        assert math.isclose(a.hours, 12.0, rel_tol=1e-10)
    
    def test_arcminutes_property(self):
        a = Angle(degrees=1)
        assert math.isclose(a.arcminutes, 60.0, rel_tol=1e-10)
    
    def test_arcseconds_property(self):
        a = Angle(degrees=1)
        assert math.isclose(a.arcseconds, 3600.0, rel_tol=1e-10)


class TestAngleArithmetic:
    """Tests for angle arithmetic operations."""
    
    def test_add(self):
        a = Angle(degrees=45)
        b = Angle(degrees=30)
        c = a + b
        assert math.isclose(c.degrees, 75, rel_tol=1e-10)
    
    def test_subtract(self):
        a = Angle(degrees=45)
        b = Angle(degrees=30)
        c = a - b
        assert math.isclose(c.degrees, 15, rel_tol=1e-10)
    
    def test_multiply(self):
        a = Angle(degrees=45)
        c = a * 2
        assert math.isclose(c.degrees, 90, rel_tol=1e-10)
    
    def test_rmultiply(self):
        a = Angle(degrees=45)
        c = 2 * a
        assert math.isclose(c.degrees, 90, rel_tol=1e-10)
    
    def test_divide(self):
        a = Angle(degrees=90)
        c = a / 2
        assert math.isclose(c.degrees, 45, rel_tol=1e-10)
    
    def test_negate(self):
        a = Angle(degrees=45)
        c = -a
        assert math.isclose(c.degrees, -45, rel_tol=1e-10)
    
    def test_abs(self):
        a = Angle(degrees=-45)
        c = abs(a)
        assert math.isclose(c.degrees, 45, rel_tol=1e-10)


class TestAngleNormalization:
    """Tests for angle normalization."""
    
    def test_normalize_positive(self):
        a = Angle(degrees=450)
        n = a.normalize()
        assert math.isclose(n.degrees, 90, rel_tol=1e-10)
    
    def test_normalize_negative(self):
        a = Angle(degrees=-90)
        n = a.normalize()
        assert math.isclose(n.degrees, 270, rel_tol=1e-10)
    
    def test_normalize_centered_zero(self):
        a = Angle(degrees=270)
        n = a.normalize(center=0)
        assert math.isclose(n.degrees, -90, rel_tol=1e-10)


class TestAngleTrig:
    """Tests for trigonometric functions."""
    
    def test_sin(self):
        a = Angle(degrees=90)
        assert math.isclose(a.sin(), 1.0, rel_tol=1e-10)
    
    def test_cos(self):
        a = Angle(degrees=0)
        assert math.isclose(a.cos(), 1.0, rel_tol=1e-10)
    
    def test_tan(self):
        a = Angle(degrees=45)
        assert math.isclose(a.tan(), 1.0, rel_tol=1e-10)


class TestAngularSeparation:
    """Tests for angular separation calculation."""
    
    def test_same_point(self):
        """Separation of a point with itself should be zero."""
        ra = Angle(hours=12)
        dec = Angle(degrees=45)
        sep = angular_separation(ra, dec, ra, dec)
        assert math.isclose(sep.degrees, 0, abs_tol=1e-10)
    
    def test_pole_to_pole(self):
        """Separation from North to South pole should be 180°."""
        ra = Angle(hours=0)
        sep = angular_separation(
            ra, Angle(degrees=90),
            ra, Angle(degrees=-90)
        )
        assert math.isclose(sep.degrees, 180, rel_tol=1e-10)
    
    def test_equator_90_degrees(self):
        """Two points 6 hours apart on the equator should be 90° apart."""
        dec = Angle(degrees=0)
        sep = angular_separation(
            Angle(hours=0), dec,
            Angle(hours=6), dec
        )
        assert math.isclose(sep.degrees, 90, rel_tol=1e-10)
    
    def test_known_value_sirius_betelgeuse(self):
        """Test against known separation (Sirius to Betelgeuse ~27°)."""
        # Sirius: RA 6h45m, Dec -16°43'
        # Betelgeuse: RA 5h55m, Dec +7°24'
        sirius_ra = Angle.from_hms(6, 45, 0)
        sirius_dec = Angle.from_dms(-16, 43, 0)
        betel_ra = Angle.from_hms(5, 55, 0)
        betel_dec = Angle.from_dms(7, 24, 0)
        
        sep = angular_separation(sirius_ra, sirius_dec, betel_ra, betel_dec)
        # Expected ~27 degrees
        assert 26 < sep.degrees < 28
    
    def test_verbose_output(self):
        """Test that verbose mode produces output."""
        ctx = VerboseContext()
        ra1, dec1 = Angle(hours=12), Angle(degrees=45)
        ra2, dec2 = Angle(hours=13), Angle(degrees=46)
        
        angular_separation(ra1, dec1, ra2, dec2, verbose=ctx)
        
        assert len(ctx.steps) > 0


class TestPositionAngle:
    """Tests for position angle calculation."""
    
    def test_north(self):
        """Point due north should have PA ~ 0°."""
        ra = Angle(hours=12)
        pa = position_angle(
            ra, Angle(degrees=45),
            ra, Angle(degrees=46)
        )
        assert math.isclose(pa.degrees, 0, abs_tol=0.1)
    
    def test_south(self):
        """Point due south should have PA ~ 180°."""
        ra = Angle(hours=12)
        pa = position_angle(
            ra, Angle(degrees=45),
            ra, Angle(degrees=44)
        )
        assert math.isclose(pa.degrees, 180, abs_tol=0.1)
    
    def test_east(self):
        """Point due east should have PA ~ 90°."""
        dec = Angle(degrees=0)
        pa = position_angle(
            Angle(hours=12), dec,
            Angle(hours=12.1), dec
        )
        assert math.isclose(pa.degrees, 90, abs_tol=1)
    
    def test_west(self):
        """Point due west should have PA ~ 270°."""
        dec = Angle(degrees=0)
        pa = position_angle(
            Angle(hours=12), dec,
            Angle(hours=11.9), dec
        )
        assert math.isclose(pa.degrees, 270, abs_tol=1)
