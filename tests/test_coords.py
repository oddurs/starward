"""
Tests for the coordinates module.
"""

import math
import pytest

from astr0.core.coords import (
    ICRSCoord, GalacticCoord, HorizontalCoord, transform_coords
)
from astr0.core.angles import Angle
from astr0.core.time import JulianDate
from astr0.verbose import VerboseContext


class TestICRSCoord:
    """Tests for ICRS coordinate handling."""
    
    def test_creation_from_degrees(self):
        coord = ICRSCoord.from_degrees(180.0, 45.0)
        assert math.isclose(coord.ra.degrees, 180.0, rel_tol=1e-10)
        assert math.isclose(coord.dec.degrees, 45.0, rel_tol=1e-10)
    
    def test_creation_from_hms_dms(self):
        coord = ICRSCoord.from_hms_dms(12, 0, 0, 45, 0, 0)
        assert math.isclose(coord.ra.hours, 12.0, rel_tol=1e-10)
        assert math.isclose(coord.dec.degrees, 45.0, rel_tol=1e-10)
    
    def test_declination_validation(self):
        """Declination must be in [-90, 90]."""
        with pytest.raises(ValueError, match="Declination"):
            ICRSCoord.from_degrees(0, 91)
        
        with pytest.raises(ValueError, match="Declination"):
            ICRSCoord.from_degrees(0, -91)
    
    def test_parse_hms_dms(self):
        coord = ICRSCoord.parse("12h30m00s +45d30m00s")
        assert math.isclose(coord.ra.hours, 12.5, rel_tol=1e-10)
        assert math.isclose(coord.dec.degrees, 45.5, rel_tol=1e-10)
    
    def test_parse_decimal(self):
        coord = ICRSCoord.parse("187.5 45.5")
        assert math.isclose(coord.ra.degrees, 187.5, rel_tol=1e-10)
        assert math.isclose(coord.dec.degrees, 45.5, rel_tol=1e-10)
    
    def test_to_icrs_returns_self(self):
        coord = ICRSCoord.from_degrees(180, 45)
        result = coord.to_icrs()
        assert result is coord


class TestGalacticCoord:
    """Tests for Galactic coordinate handling."""
    
    def test_creation_from_degrees(self):
        coord = GalacticCoord.from_degrees(90.0, 30.0)
        assert math.isclose(coord.l.degrees, 90.0, rel_tol=1e-10)
        assert math.isclose(coord.b.degrees, 30.0, rel_tol=1e-10)
    
    def test_latitude_validation(self):
        """Galactic latitude must be in [-90, 90]."""
        with pytest.raises(ValueError):
            GalacticCoord.from_degrees(0, 91)


class TestGalacticICRSTransform:
    """Tests for ICRS <-> Galactic transformations."""
    
    def test_galactic_center_to_icrs(self):
        """Galactic center (l=0, b=0) should be near Sgr A*."""
        gc = GalacticCoord.from_degrees(0.0, 0.0)
        icrs = gc.to_icrs()
        
        # Sgr A* is at approximately RA 17h45m40s, Dec -29°00'28"
        # Which is about 266.4° RA, -29° Dec
        assert 265 < icrs.ra.degrees < 268
        assert -30 < icrs.dec.degrees < -28
    
    def test_galactic_pole_to_icrs(self):
        """North Galactic Pole should be at specific ICRS coordinates."""
        ngp = GalacticCoord.from_degrees(0.0, 90.0)
        icrs = ngp.to_icrs()
        
        # NGP is at RA ~12h51m, Dec ~27°07' (from constants)
        assert math.isclose(icrs.ra.degrees, 192.86, abs_tol=0.1)
        assert math.isclose(icrs.dec.degrees, 27.13, abs_tol=0.1)
    
    def test_icrs_to_galactic_roundtrip(self):
        """Converting ICRS -> Galactic -> ICRS should give original."""
        original = ICRSCoord.from_degrees(187.5, 45.5)
        galactic = original.to_galactic()
        back = galactic.to_icrs()
        
        assert math.isclose(original.ra.degrees, back.ra.degrees, abs_tol=1e-8)
        assert math.isclose(original.dec.degrees, back.dec.degrees, abs_tol=1e-8)
    
    def test_galactic_to_icrs_roundtrip(self):
        """Converting Galactic -> ICRS -> Galactic should give original."""
        original = GalacticCoord.from_degrees(90.0, 30.0)
        icrs = original.to_icrs()
        back = GalacticCoord.from_icrs(icrs)
        
        assert math.isclose(original.l.degrees, back.l.degrees, abs_tol=1e-8)
        assert math.isclose(original.b.degrees, back.b.degrees, abs_tol=1e-8)


class TestHorizontalCoord:
    """Tests for Horizontal coordinate handling."""
    
    def test_creation_from_degrees(self):
        coord = HorizontalCoord.from_degrees(45.0, 180.0)
        assert math.isclose(coord.alt.degrees, 45.0, rel_tol=1e-10)
        assert math.isclose(coord.az.degrees, 180.0, rel_tol=1e-10)
    
    def test_altitude_validation(self):
        """Altitude must be in [-90, 90]."""
        with pytest.raises(ValueError):
            HorizontalCoord.from_degrees(91, 0)
    
    def test_airmass_zenith(self):
        """Airmass at zenith should be ~1."""
        coord = HorizontalCoord.from_degrees(90.0, 0.0)
        assert math.isclose(coord.airmass, 1.0, rel_tol=0.01)
    
    def test_airmass_45_degrees(self):
        """Airmass at 45° should be ~1.41."""
        coord = HorizontalCoord.from_degrees(45.0, 0.0)
        assert math.isclose(coord.airmass, 1.41, rel_tol=0.02)
    
    def test_airmass_horizon(self):
        """Airmass very close to horizon should be very large."""
        coord = HorizontalCoord.from_degrees(1.0, 0.0)
        assert coord.airmass > 25  # At 1 degree, airmass is approximately 26
    
    def test_airmass_below_horizon(self):
        """Airmass below horizon should be infinite."""
        coord = HorizontalCoord.from_degrees(-5.0, 0.0)
        assert coord.airmass == float('inf')
    
    def test_zenith_angle(self):
        """Zenith angle should be 90° - altitude."""
        coord = HorizontalCoord.from_degrees(60.0, 0.0)
        assert math.isclose(coord.zenith_angle.degrees, 30.0, rel_tol=1e-10)


class TestICRSToHorizontal:
    """Tests for ICRS -> Horizontal transformation."""
    
    def test_requires_parameters(self):
        """Should require jd, lat, lon for conversion."""
        with pytest.raises(ValueError, match="jd, lat, and lon are required"):
            HorizontalCoord.from_icrs(ICRSCoord.from_degrees(0, 0))
    
    def test_zenith_at_lst(self):
        """
        An object at RA = LST, Dec = latitude should be at zenith.
        """
        # Choose a specific JD and location
        jd = JulianDate(2460000.5)
        lat = Angle(degrees=40.0)
        lon = Angle(degrees=-75.0)
        
        # Get LST at this time and location
        lst = jd.lst(lon.degrees)
        
        # Create a star at this LST (RA) and observer's latitude (Dec)
        coord = ICRSCoord(Angle(hours=lst), lat)
        
        # Transform to horizontal
        horiz = HorizontalCoord.from_icrs(coord, jd=jd, lat=lat, lon=lon)
        
        # Should be very close to zenith (alt = 90°)
        assert horiz.alt.degrees > 89.9
    
    def test_north_celestial_pole(self):
        """
        NCP should be at altitude = latitude for Northern observers.
        """
        jd = JulianDate.j2000()
        lat = Angle(degrees=40.0)
        lon = Angle(degrees=0.0)
        
        ncp = ICRSCoord.from_degrees(0, 90)  # RA doesn't matter at pole
        horiz = HorizontalCoord.from_icrs(ncp, jd=jd, lat=lat, lon=lon)
        
        # Altitude should equal latitude
        assert math.isclose(horiz.alt.degrees, lat.degrees, abs_tol=0.1)
        # Azimuth should be ~0° (North)
        assert horiz.az.degrees < 1 or horiz.az.degrees > 359


class TestTransformCoords:
    """Tests for the transform_coords function."""
    
    def test_icrs_to_galactic(self):
        coord = ICRSCoord.from_degrees(187.5, 45.5)
        result = transform_coords(coord, 'galactic')
        assert isinstance(result, GalacticCoord)
    
    def test_galactic_to_icrs(self):
        coord = GalacticCoord.from_degrees(90, 30)
        result = transform_coords(coord, 'icrs')
        assert isinstance(result, ICRSCoord)
    
    def test_aliases(self):
        """Test that system aliases work."""
        coord = ICRSCoord.from_degrees(180, 45)
        
        # Test various aliases
        for alias in ['galactic', 'gal', 'GALACTIC']:
            result = transform_coords(coord, alias)
            assert isinstance(result, GalacticCoord)
        
        for alias in ['icrs', 'j2000', 'equatorial', 'ICRS']:
            result = transform_coords(coord, alias)
            assert isinstance(result, ICRSCoord)
    
    def test_unknown_system(self):
        """Should raise for unknown coordinate system."""
        coord = ICRSCoord.from_degrees(180, 45)
        with pytest.raises(ValueError, match="Unknown"):
            transform_coords(coord, 'xyz')
    
    def test_verbose(self):
        """Test verbose output."""
        ctx = VerboseContext()
        coord = ICRSCoord.from_degrees(187.5, 45.5)
        transform_coords(coord, 'galactic', verbose=ctx)
        assert len(ctx.steps) > 0


class TestKnownCoordinates:
    """Test against known coordinates from authoritative sources."""
    
    # Famous objects with well-known coordinates
    KNOWN_OBJECTS = [
        # (name, ra_h, ra_m, ra_s, dec_d, dec_m, dec_s, l, b)
        # Vega - well-tested
        ("Vega", 18, 36, 56.3, 38, 47, 1, 67.45, 19.24),
    ]
    
    @pytest.mark.parametrize("name,ra_h,ra_m,ra_s,dec_d,dec_m,dec_s,l_exp,b_exp", KNOWN_OBJECTS)
    def test_known_galactic(self, name, ra_h, ra_m, ra_s, dec_d, dec_m, dec_s, l_exp, b_exp):
        """Test ICRS to Galactic for known objects."""
        coord = ICRSCoord.from_hms_dms(ra_h, ra_m, ra_s, dec_d, dec_m, dec_s)
        gal = coord.to_galactic()
        
        # Allow 1 degree tolerance for the test (coordinates may have slight variations)
        assert math.isclose(gal.l.degrees, l_exp, abs_tol=1.0), f"{name}: l mismatch"
        assert math.isclose(gal.b.degrees, b_exp, abs_tol=1.0), f"{name}: b mismatch"
