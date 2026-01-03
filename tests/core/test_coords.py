"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           COORDINATE TESTS                                   ║
║                                                                              ║
║  Tests for celestial coordinate systems and transformations.                 ║
║  Supports ICRS, Galactic, and Horizontal coordinate frames.                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
import pytest
from hypothesis import given, strategies as st, settings

from astr0.core.coords import (
    ICRSCoord, GalacticCoord, HorizontalCoord, transform_coords
)
from astr0.core.angles import Angle
from astr0.core.time import JulianDate
from astr0.verbose import VerboseContext


# ═══════════════════════════════════════════════════════════════════════════════
#  ICRS COORDINATES
# ═══════════════════════════════════════════════════════════════════════════════

class TestICRSCoord:
    """
    Tests for the International Celestial Reference System (ICRS).
    
    ICRS is the fundamental celestial reference frame aligned with
    the J2000.0 equator and equinox.
    
    Components:
      - RA (Right Ascension): 0° to 360° (or 0h to 24h)
      - Dec (Declination): -90° to +90°
    """
    
    # ─── Construction ───────────────────────────────────────────────────────
    
    def test_from_degrees(self):
        """Create ICRS coordinate from decimal degrees."""
        coord = ICRSCoord.from_degrees(180.0, 45.0)
        assert math.isclose(coord.ra.degrees, 180.0, rel_tol=1e-10)
        assert math.isclose(coord.dec.degrees, 45.0, rel_tol=1e-10)
    
    def test_from_hms_dms(self):
        """Create ICRS coordinate from HMS/DMS."""
        coord = ICRSCoord.from_hms_dms(12, 0, 0, 45, 0, 0)
        assert math.isclose(coord.ra.hours, 12.0, rel_tol=1e-10)
        assert math.isclose(coord.dec.degrees, 45.0, rel_tol=1e-10)
    
    # ─── Parsing ────────────────────────────────────────────────────────────
    
    def test_parse_hms_dms(self):
        """Parse coordinate from HMS/DMS string."""
        coord = ICRSCoord.parse("12h30m00s +45d30m00s")
        assert math.isclose(coord.ra.hours, 12.5, rel_tol=1e-10)
        assert math.isclose(coord.dec.degrees, 45.5, rel_tol=1e-10)
    
    def test_parse_decimal(self):
        """Parse coordinate from decimal string."""
        coord = ICRSCoord.parse("187.5 45.5")
        assert math.isclose(coord.ra.degrees, 187.5, rel_tol=1e-10)
        assert math.isclose(coord.dec.degrees, 45.5, rel_tol=1e-10)
    
    def test_parse_negative_dec(self):
        """Parse coordinate with negative declination."""
        coord = ICRSCoord.parse("06h45m09s -16d42m58s")
        assert coord.dec.degrees < 0
    
    # ─── Validation ─────────────────────────────────────────────────────────
    
    def test_declination_upper_bound(self):
        """Declination > 90° is invalid."""
        with pytest.raises(ValueError, match="Declination"):
            ICRSCoord.from_degrees(0, 91)
    
    def test_declination_lower_bound(self):
        """Declination < -90° is invalid."""
        with pytest.raises(ValueError, match="Declination"):
            ICRSCoord.from_degrees(0, -91)
    
    @pytest.mark.edge
    def test_declination_at_poles(self):
        """Dec = ±90° is valid."""
        north = ICRSCoord.from_degrees(0, 90)
        south = ICRSCoord.from_degrees(0, -90)
        assert north.dec.degrees == 90
        assert south.dec.degrees == -90
    
    # ─── Identity Transform ─────────────────────────────────────────────────
    
    def test_to_icrs_returns_self(self):
        """Converting ICRS to ICRS returns self."""
        coord = ICRSCoord.from_degrees(180, 45)
        result = coord.to_icrs()
        assert result is coord


# ═══════════════════════════════════════════════════════════════════════════════
#  GALACTIC COORDINATES
# ═══════════════════════════════════════════════════════════════════════════════

class TestGalacticCoord:
    """
    Tests for Galactic coordinate system.
    
    Centered on the Milky Way:
      - l (longitude): 0° toward Galactic center
      - b (latitude): 0° in Galactic plane, ±90° at poles
    """
    
    # ─── Construction ───────────────────────────────────────────────────────
    
    def test_from_degrees(self):
        """Create Galactic coordinate from degrees."""
        coord = GalacticCoord.from_degrees(90.0, 30.0)
        assert math.isclose(coord.l.degrees, 90.0, rel_tol=1e-10)
        assert math.isclose(coord.b.degrees, 30.0, rel_tol=1e-10)
    
    # ─── Validation ─────────────────────────────────────────────────────────
    
    def test_latitude_bounds(self):
        """Galactic latitude must be in [-90, 90]."""
        with pytest.raises(ValueError):
            GalacticCoord.from_degrees(0, 91)
        with pytest.raises(ValueError):
            GalacticCoord.from_degrees(0, -91)


# ═══════════════════════════════════════════════════════════════════════════════
#  ICRS ↔ GALACTIC TRANSFORMATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class TestGalacticICRSTransform:
    """
    Tests for ICRS ↔ Galactic coordinate transformations.
    
    These transforms use the IAU-defined Galactic coordinate system
    with the North Galactic Pole at (RA=192.86°, Dec=27.13°) and
    the ascending node at l=33°.
    """
    
    @pytest.mark.golden
    def test_galactic_center_to_icrs(self):
        """
        Galactic center (l=0°, b=0°) transforms to Sgr A* region.
        
        Expected: RA ≈ 266.4°, Dec ≈ -29°
        """
        gc = GalacticCoord.from_degrees(0.0, 0.0)
        icrs = gc.to_icrs()
        
        assert 265 < icrs.ra.degrees < 268
        assert -30 < icrs.dec.degrees < -28
    
    @pytest.mark.golden
    def test_north_galactic_pole_to_icrs(self):
        """
        North Galactic Pole (l=any, b=90°) transforms to fixed ICRS point.
        
        Expected: RA ≈ 192.86°, Dec ≈ 27.13° (by definition)
        """
        ngp = GalacticCoord.from_degrees(0.0, 90.0)
        icrs = ngp.to_icrs()
        
        assert math.isclose(icrs.ra.degrees, 192.86, abs_tol=0.1)
        assert math.isclose(icrs.dec.degrees, 27.13, abs_tol=0.1)
    
    @pytest.mark.roundtrip
    def test_icrs_to_galactic_roundtrip(self):
        """ICRS → Galactic → ICRS preserves coordinates."""
        original = ICRSCoord.from_degrees(187.5, 45.5)
        galactic = original.to_galactic()
        back = galactic.to_icrs()
        
        assert math.isclose(original.ra.degrees, back.ra.degrees, abs_tol=1e-8)
        assert math.isclose(original.dec.degrees, back.dec.degrees, abs_tol=1e-8)
    
    @pytest.mark.roundtrip
    def test_galactic_to_icrs_roundtrip(self):
        """Galactic → ICRS → Galactic preserves coordinates."""
        original = GalacticCoord.from_degrees(90.0, 30.0)
        icrs = original.to_icrs()
        back = GalacticCoord.from_icrs(icrs)
        
        assert math.isclose(original.l.degrees, back.l.degrees, abs_tol=1e-8)
        assert math.isclose(original.b.degrees, back.b.degrees, abs_tol=1e-8)
    
    @pytest.mark.roundtrip
    @given(
        st.floats(min_value=0, max_value=360, allow_nan=False),
        st.floats(min_value=-89, max_value=89, allow_nan=False)
    )
    @settings(max_examples=100)
    def test_galactic_roundtrip_property(self, lon, lat):
        """Property test: Galactic ↔ ICRS roundtrip for arbitrary coords."""
        original = GalacticCoord.from_degrees(lon, lat)
        back = GalacticCoord.from_icrs(original.to_icrs())
        
        # Normalize for comparison
        orig_l = original.l.degrees % 360
        back_l = back.l.degrees % 360
        
        assert math.isclose(orig_l, back_l, abs_tol=1e-6) or \
               math.isclose(abs(orig_l - back_l), 360, abs_tol=1e-6)
        assert math.isclose(original.b.degrees, back.b.degrees, abs_tol=1e-6)


# ═══════════════════════════════════════════════════════════════════════════════
#  HORIZONTAL COORDINATES
# ═══════════════════════════════════════════════════════════════════════════════

class TestHorizontalCoord:
    """
    Tests for horizontal (alt-az) coordinate system.
    
    Observer-dependent coordinate system:
      - Alt (Altitude): -90° (nadir) to +90° (zenith)
      - Az (Azimuth): 0° = North, 90° = East, 180° = South, 270° = West
    """
    
    # ─── Construction ───────────────────────────────────────────────────────
    
    def test_from_degrees(self):
        """Create horizontal coordinate from degrees."""
        coord = HorizontalCoord.from_degrees(45.0, 180.0)
        assert math.isclose(coord.alt.degrees, 45.0, rel_tol=1e-10)
        assert math.isclose(coord.az.degrees, 180.0, rel_tol=1e-10)
    
    # ─── Validation ─────────────────────────────────────────────────────────
    
    def test_altitude_bounds(self):
        """Altitude must be in [-90, 90]."""
        with pytest.raises(ValueError):
            HorizontalCoord.from_degrees(91, 0)
        with pytest.raises(ValueError):
            HorizontalCoord.from_degrees(-91, 0)
    
    # ─── Airmass ────────────────────────────────────────────────────────────
    
    @pytest.mark.golden
    def test_airmass_at_zenith(self):
        """Airmass at zenith is 1.0."""
        coord = HorizontalCoord.from_degrees(90.0, 0.0)
        assert math.isclose(coord.airmass, 1.0, rel_tol=0.01)
    
    @pytest.mark.golden
    def test_airmass_at_45_degrees(self):
        """Airmass at 45° ≈ √2 ≈ 1.41."""
        coord = HorizontalCoord.from_degrees(45.0, 0.0)
        assert math.isclose(coord.airmass, 1.41, rel_tol=0.02)
    
    def test_airmass_at_horizon(self):
        """Airmass near horizon is very large."""
        coord = HorizontalCoord.from_degrees(1.0, 0.0)
        assert coord.airmass > 25
    
    def test_airmass_below_horizon(self):
        """Airmass below horizon is infinite."""
        coord = HorizontalCoord.from_degrees(-5.0, 0.0)
        assert coord.airmass == float('inf')
    
    # ─── Zenith Angle ───────────────────────────────────────────────────────
    
    def test_zenith_angle(self):
        """Zenith angle = 90° - altitude."""
        coord = HorizontalCoord.from_degrees(60.0, 0.0)
        assert math.isclose(coord.zenith_angle.degrees, 30.0, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  ICRS → HORIZONTAL TRANSFORMATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class TestICRSToHorizontal:
    """
    Tests for ICRS → Horizontal coordinate transformation.
    
    This transform requires:
      - Julian Date (for sidereal time)
      - Observer latitude
      - Observer longitude
    """
    
    def test_requires_parameters(self):
        """Must provide jd, lat, lon for transformation."""
        with pytest.raises(ValueError, match="jd, lat, and lon are required"):
            HorizontalCoord.from_icrs(ICRSCoord.from_degrees(0, 0))
    
    @pytest.mark.golden
    def test_zenith_at_lst(self):
        """Object at RA=LST, Dec=lat is at zenith."""
        jd = JulianDate(2460000.5)
        lat = Angle(degrees=40.0)
        lon = Angle(degrees=-75.0)
        
        # Get LST and create star at that RA
        lst = jd.lst(lon.degrees)
        coord = ICRSCoord(Angle(hours=lst), lat)
        
        horiz = HorizontalCoord.from_icrs(coord, jd=jd, lat=lat, lon=lon)
        assert horiz.alt.degrees > 89.9
    
    @pytest.mark.golden
    def test_ncp_altitude_equals_latitude(self):
        """North Celestial Pole altitude = observer latitude."""
        jd = JulianDate.j2000()
        lat = Angle(degrees=40.0)
        lon = Angle(degrees=0.0)
        
        ncp = ICRSCoord.from_degrees(0, 90)
        horiz = HorizontalCoord.from_icrs(ncp, jd=jd, lat=lat, lon=lon)
        
        assert math.isclose(horiz.alt.degrees, lat.degrees, abs_tol=0.1)
    
    def test_ncp_azimuth_is_north(self):
        """NCP azimuth is ~0° (North)."""
        jd = JulianDate.j2000()
        lat = Angle(degrees=40.0)
        lon = Angle(degrees=0.0)
        
        ncp = ICRSCoord.from_degrees(0, 90)
        horiz = HorizontalCoord.from_icrs(ncp, jd=jd, lat=lat, lon=lon)
        
        assert horiz.az.degrees < 1 or horiz.az.degrees > 359


# ═══════════════════════════════════════════════════════════════════════════════
#  TRANSFORM_COORDS INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

class TestTransformCoords:
    """
    Tests for the unified transform_coords() function.
    
    Provides a consistent interface for coordinate system conversions.
    """
    
    def test_icrs_to_galactic(self):
        """Transform ICRS to Galactic via function."""
        coord = ICRSCoord.from_degrees(187.5, 45.5)
        result = transform_coords(coord, 'galactic')
        assert isinstance(result, GalacticCoord)
    
    def test_galactic_to_icrs(self):
        """Transform Galactic to ICRS via function."""
        coord = GalacticCoord.from_degrees(90, 30)
        result = transform_coords(coord, 'icrs')
        assert isinstance(result, ICRSCoord)
    
    def test_system_aliases(self):
        """Various system aliases work correctly."""
        coord = ICRSCoord.from_degrees(180, 45)
        
        for alias in ['galactic', 'gal', 'GALACTIC']:
            result = transform_coords(coord, alias)
            assert isinstance(result, GalacticCoord)
        
        for alias in ['icrs', 'j2000', 'equatorial', 'ICRS']:
            result = transform_coords(coord, alias)
            assert isinstance(result, ICRSCoord)
    
    def test_unknown_system_raises(self):
        """Unknown coordinate system raises ValueError."""
        coord = ICRSCoord.from_degrees(180, 45)
        with pytest.raises(ValueError, match="Unknown"):
            transform_coords(coord, 'xyz')
    
    @pytest.mark.verbose
    def test_verbose_output(self):
        """Verbose mode produces steps."""
        ctx = VerboseContext()
        coord = ICRSCoord.from_degrees(187.5, 45.5)
        transform_coords(coord, 'galactic', verbose=ctx)
        assert len(ctx.steps) > 0


# ═══════════════════════════════════════════════════════════════════════════════
#  KNOWN ASTRONOMICAL OBJECTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestKnownObjects:
    """
    Tests against authoritative coordinates of well-known objects.
    
    Sources: SIMBAD, Hipparcos catalog
    """
    
    @pytest.mark.golden
    @pytest.mark.parametrize("name,ra_h,ra_m,ra_s,dec_d,dec_m,dec_s,l_exp,b_exp", [
        ("Vega", 18, 36, 56, 38, 47, 1, 67.45, 19.24),
        ("Polaris", 2, 31, 49, 89, 15, 51, 123.28, 26.46),
    ])
    def test_star_galactic_coords(self, name, ra_h, ra_m, ra_s, 
                                    dec_d, dec_m, dec_s, l_exp, b_exp):
        """Verify ICRS → Galactic for known stars."""
        coord = ICRSCoord.from_hms_dms(ra_h, ra_m, ra_s, dec_d, dec_m, dec_s)
        gal = coord.to_galactic()
        
        assert math.isclose(gal.l.degrees, l_exp, abs_tol=1.0), f"{name}: l mismatch"
        assert math.isclose(gal.b.degrees, b_exp, abs_tol=1.0), f"{name}: b mismatch"
    
    def test_sirius_coordinates(self, famous_stars):
        """Verify Sirius coordinates from fixture."""
        sirius = famous_stars['sirius']
        assert 6 < sirius.ra.hours < 7
        assert -17 < sirius.dec.degrees < -16
    
    def test_m31_coordinates(self, messier_objects):
        """Verify M31 (Andromeda) coordinates from fixture."""
        m31 = messier_objects['M31']
        assert 0 < m31.ra.hours < 1
        assert 41 < m31.dec.degrees < 42


# ═══════════════════════════════════════════════════════════════════════════════
#  EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════════

class TestCoordEdgeCases:
    """
    Tests for coordinate edge cases and boundary conditions.
    """
    
    @pytest.mark.edge
    def test_celestial_pole_ra_indeterminate(self):
        """At celestial poles, RA is indeterminate but transform works."""
        # Multiple RAs should give same pole
        pole1 = ICRSCoord.from_degrees(0, 90)
        pole2 = ICRSCoord.from_degrees(180, 90)
        
        # Both should be at North pole
        assert pole1.dec.degrees == pole2.dec.degrees == 90
    
    @pytest.mark.edge
    def test_ra_wrap_around(self):
        """RA wraps at 0h/24h boundary."""
        coord1 = ICRSCoord.from_degrees(359.9, 0)
        coord2 = ICRSCoord.from_degrees(0.1, 0)
        
        # These should be very close
        from astr0.core.angles import angular_separation
        sep = angular_separation(coord1.ra, coord1.dec, coord2.ra, coord2.dec)
        assert sep.degrees < 0.3
