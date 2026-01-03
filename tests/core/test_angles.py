"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              ANGLE TESTS                                     ║
║                                                                              ║
║  Tests for angular arithmetic, parsing, conversions, and trigonometry.       ║
║  Angles are the fundamental building block of celestial mechanics.           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
import pytest
from hypothesis import given, strategies as st, settings

from astr0.core.angles import Angle, angular_separation, position_angle
from astr0.verbose import VerboseContext


# ═══════════════════════════════════════════════════════════════════════════════
#  CONSTRUCTION & INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestAngleConstruction:
    """
    Tests for creating Angle instances from various units.
    
    An Angle can be constructed from:
      - degrees (default astronomical unit)
      - radians (mathematical standard)
      - hours (right ascension, 24h = 360°)
      - arcminutes (1° = 60')
      - arcseconds (1° = 3600")
    """
    
    # ─── From Degrees ───────────────────────────────────────────────────────
    
    def test_from_degrees_positive(self):
        """Create angle from positive degrees."""
        a = Angle(degrees=45.5)
        assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)
    
    def test_from_degrees_negative(self):
        """Create angle from negative degrees."""
        a = Angle(degrees=-45.5)
        assert math.isclose(a.degrees, -45.5, rel_tol=1e-10)
    
    def test_from_degrees_zero(self):
        """Create zero angle."""
        a = Angle(degrees=0)
        assert a.degrees == 0
    
    @pytest.mark.edge
    def test_from_degrees_large(self):
        """Create angle larger than 360°."""
        a = Angle(degrees=720.5)
        assert math.isclose(a.degrees, 720.5, rel_tol=1e-10)
    
    # ─── From Radians ───────────────────────────────────────────────────────
    
    def test_from_radians(self):
        """Create angle from radians."""
        a = Angle(radians=math.pi / 4)
        assert math.isclose(a.degrees, 45.0, rel_tol=1e-10)
    
    def test_from_radians_pi(self):
        """π radians = 180°."""
        a = Angle(radians=math.pi)
        assert math.isclose(a.degrees, 180.0, rel_tol=1e-10)
    
    def test_from_radians_2pi(self):
        """2π radians = 360°."""
        a = Angle(radians=2 * math.pi)
        assert math.isclose(a.degrees, 360.0, rel_tol=1e-10)
    
    # ─── From Hours (Right Ascension) ───────────────────────────────────────
    
    def test_from_hours(self):
        """Create angle from hours."""
        a = Angle(hours=12.0)
        assert math.isclose(a.degrees, 180.0, rel_tol=1e-10)
    
    def test_from_hours_24(self):
        """24 hours = 360°."""
        a = Angle(hours=24.0)
        assert math.isclose(a.degrees, 360.0, rel_tol=1e-10)
    
    def test_from_hours_6(self):
        """6 hours = 90°."""
        a = Angle(hours=6.0)
        assert math.isclose(a.degrees, 90.0, rel_tol=1e-10)
    
    # ─── From Arcminutes ────────────────────────────────────────────────────
    
    def test_from_arcminutes(self):
        """Create angle from arcminutes."""
        a = Angle(arcminutes=60.0)
        assert math.isclose(a.degrees, 1.0, rel_tol=1e-10)
    
    def test_from_arcminutes_90(self):
        """90 arcminutes = 1.5°."""
        a = Angle(arcminutes=90.0)
        assert math.isclose(a.degrees, 1.5, rel_tol=1e-10)
    
    # ─── From Arcseconds ────────────────────────────────────────────────────
    
    def test_from_arcseconds(self):
        """Create angle from arcseconds."""
        a = Angle(arcseconds=3600.0)
        assert math.isclose(a.degrees, 1.0, rel_tol=1e-10)
    
    def test_from_arcseconds_small(self):
        """Very small angle: 1 arcsecond."""
        a = Angle(arcseconds=1.0)
        assert math.isclose(a.degrees, 1.0 / 3600.0, rel_tol=1e-10)
    
    # ─── From DMS (Degrees, Minutes, Seconds) ───────────────────────────────
    
    def test_from_dms(self):
        """Create angle from d°m′s″."""
        a = Angle.from_dms(45, 30, 0)
        assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)
    
    def test_from_dms_with_seconds(self):
        """Create angle with non-zero seconds."""
        a = Angle.from_dms(45, 30, 30)
        expected = 45 + 30/60 + 30/3600
        assert math.isclose(a.degrees, expected, rel_tol=1e-10)
    
    def test_from_dms_negative(self):
        """Create negative angle from DMS."""
        a = Angle.from_dms(-45, 30, 0)
        assert math.isclose(a.degrees, -45.5, rel_tol=1e-10)
    
    @pytest.mark.edge
    def test_from_dms_edge_zero_degrees(self):
        """Edge case: negative angle with zero degrees component."""
        a = Angle.from_dms(0, -30, 0)  # -0°30'
        assert math.isclose(a.degrees, -0.5, rel_tol=1e-10)
    
    # ─── From HMS (Hours, Minutes, Seconds) ─────────────────────────────────
    
    def test_from_hms(self):
        """Create angle from h:m:s."""
        a = Angle.from_hms(12, 30, 0)
        assert math.isclose(a.hours, 12.5, rel_tol=1e-10)
    
    def test_from_hms_sidereal_day(self):
        """24h = 360°."""
        a = Angle.from_hms(24, 0, 0)
        assert math.isclose(a.degrees, 360.0, rel_tol=1e-10)
    
    # ─── Validation ─────────────────────────────────────────────────────────
    
    def test_requires_exactly_one_unit(self):
        """Must specify exactly one unit."""
        with pytest.raises(ValueError, match="Exactly one"):
            Angle()
    
    def test_rejects_multiple_units(self):
        """Cannot specify multiple units."""
        with pytest.raises(ValueError, match="Exactly one"):
            Angle(degrees=45, radians=0.5)


# ═══════════════════════════════════════════════════════════════════════════════
#  PARSING
# ═══════════════════════════════════════════════════════════════════════════════

class TestAngleParsing:
    """
    Tests for parsing angle strings in various formats.
    
    Supported formats:
      - Decimal: "45.5", "45.5d"
      - DMS: "45d30m00s", "45°30′00″", "45:30:00"
      - HMS: "12h30m00s"
      - Space-separated: "45 30 00"
    """
    
    # ─── Decimal Formats ────────────────────────────────────────────────────
    
    def test_parse_decimal_plain(self):
        """Parse plain decimal degrees."""
        a = Angle.parse("45.5")
        assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)
    
    def test_parse_decimal_with_d(self):
        """Parse decimal with 'd' suffix."""
        a = Angle.parse("45.5d")
        assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)
    
    def test_parse_integer(self):
        """Parse integer degrees."""
        a = Angle.parse("45")
        assert math.isclose(a.degrees, 45.0, rel_tol=1e-10)
    
    def test_parse_negative_decimal(self):
        """Parse negative decimal degrees."""
        a = Angle.parse("-45.5")
        assert math.isclose(a.degrees, -45.5, rel_tol=1e-10)
    
    # ─── DMS Formats ────────────────────────────────────────────────────────
    
    def test_parse_dms_letters(self):
        """Parse DMS with letter separators."""
        a = Angle.parse("45d30m00s")
        assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)
    
    def test_parse_dms_unicode(self):
        """Parse DMS with Unicode symbols."""
        a = Angle.parse("45°30′00″")
        assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)
    
    def test_parse_dms_colons(self):
        """Parse DMS with colon separators."""
        a = Angle.parse("45:30:00")
        assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)
    
    def test_parse_dms_spaces(self):
        """Parse DMS with space separators."""
        a = Angle.parse("45 30 00")
        assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)
    
    def test_parse_dms_negative(self):
        """Parse negative DMS."""
        a = Angle.parse("-45d30m00s")
        assert math.isclose(a.degrees, -45.5, rel_tol=1e-10)
    
    # ─── HMS Formats ────────────────────────────────────────────────────────
    
    def test_parse_hms(self):
        """Parse HMS format."""
        a = Angle.parse("12h30m00s")
        assert math.isclose(a.hours, 12.5, rel_tol=1e-10)
    
    # ─── Error Handling ─────────────────────────────────────────────────────
    
    def test_parse_invalid_raises(self):
        """Invalid string raises ValueError."""
        with pytest.raises(ValueError, match="Cannot parse"):
            Angle.parse("not an angle")
    
    def test_parse_empty_raises(self):
        """Empty string raises ValueError."""
        with pytest.raises(ValueError):
            Angle.parse("")


# ═══════════════════════════════════════════════════════════════════════════════
#  UNIT CONVERSIONS
# ═══════════════════════════════════════════════════════════════════════════════

class TestAngleConversions:
    """
    Tests for converting between angle units.
    
    All conversions should be mathematically exact and
    round-trip back to the original value.
    """
    
    # ─── To DMS ─────────────────────────────────────────────────────────────
    
    def test_to_dms_positive(self):
        """Convert positive angle to DMS."""
        a = Angle(degrees=45.5)
        d, m, s = a.to_dms()
        assert d == 45
        assert m == 30
        assert math.isclose(s, 0.0, abs_tol=1e-10)
    
    def test_to_dms_negative(self):
        """Convert negative angle to DMS."""
        a = Angle(degrees=-45.5)
        d, m, s = a.to_dms()
        assert d == -45
        assert m == 30
        assert math.isclose(s, 0.0, abs_tol=1e-10)
    
    def test_to_dms_with_seconds(self):
        """Convert angle with fractional minutes."""
        a = Angle(degrees=45.5083333)  # 45°30'30"
        d, m, s = a.to_dms()
        assert d == 45
        assert m == 30
        assert math.isclose(s, 30.0, abs_tol=0.01)
    
    # ─── To HMS ─────────────────────────────────────────────────────────────
    
    def test_to_hms(self):
        """Convert angle to HMS."""
        a = Angle(hours=12.5)
        h, m, s = a.to_hms()
        assert h == 12
        assert m == 30
        assert math.isclose(s, 0.0, abs_tol=1e-10)
    
    # ─── Property Accessors ─────────────────────────────────────────────────
    
    def test_radians_property(self):
        """Radians accessor."""
        a = Angle(degrees=180)
        assert math.isclose(a.radians, math.pi, rel_tol=1e-10)
    
    def test_hours_property(self):
        """Hours accessor."""
        a = Angle(degrees=180)
        assert math.isclose(a.hours, 12.0, rel_tol=1e-10)
    
    def test_arcminutes_property(self):
        """Arcminutes accessor."""
        a = Angle(degrees=1)
        assert math.isclose(a.arcminutes, 60.0, rel_tol=1e-10)
    
    def test_arcseconds_property(self):
        """Arcseconds accessor."""
        a = Angle(degrees=1)
        assert math.isclose(a.arcseconds, 3600.0, rel_tol=1e-10)
    
    # ─── Round-Trip Conversions ─────────────────────────────────────────────
    
    @pytest.mark.roundtrip
    @given(st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_degrees_radians_roundtrip(self, deg):
        """degrees → radians → degrees is identity."""
        a = Angle(degrees=deg)
        b = Angle(radians=a.radians)
        assert math.isclose(a.degrees, b.degrees, rel_tol=1e-10)
    
    @pytest.mark.roundtrip
    @given(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_degrees_hours_roundtrip(self, deg):
        """degrees → hours → degrees is identity."""
        a = Angle(degrees=deg)
        b = Angle(hours=a.hours)
        assert math.isclose(a.degrees, b.degrees, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  ARITHMETIC OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class TestAngleArithmetic:
    """
    Tests for angle arithmetic operations.
    
    Angles support standard arithmetic:
      - Addition (Angle + Angle)
      - Subtraction (Angle - Angle)
      - Multiplication (Angle * scalar)
      - Division (Angle / scalar)
      - Negation (-Angle)
      - Absolute value (abs(Angle))
    """
    
    # ─── Addition ───────────────────────────────────────────────────────────
    
    def test_add_angles(self):
        """Add two angles."""
        a = Angle(degrees=45)
        b = Angle(degrees=30)
        c = a + b
        assert math.isclose(c.degrees, 75, rel_tol=1e-10)
    
    def test_add_negative(self):
        """Add a negative angle."""
        a = Angle(degrees=45)
        b = Angle(degrees=-30)
        c = a + b
        assert math.isclose(c.degrees, 15, rel_tol=1e-10)
    
    # ─── Subtraction ────────────────────────────────────────────────────────
    
    def test_subtract_angles(self):
        """Subtract two angles."""
        a = Angle(degrees=45)
        b = Angle(degrees=30)
        c = a - b
        assert math.isclose(c.degrees, 15, rel_tol=1e-10)
    
    def test_subtract_to_negative(self):
        """Subtraction resulting in negative angle."""
        a = Angle(degrees=30)
        b = Angle(degrees=45)
        c = a - b
        assert math.isclose(c.degrees, -15, rel_tol=1e-10)
    
    # ─── Multiplication ─────────────────────────────────────────────────────
    
    def test_multiply_by_scalar(self):
        """Multiply angle by scalar."""
        a = Angle(degrees=45)
        c = a * 2
        assert math.isclose(c.degrees, 90, rel_tol=1e-10)
    
    def test_multiply_scalar_by_angle(self):
        """Multiply scalar by angle (reverse)."""
        a = Angle(degrees=45)
        c = 2 * a
        assert math.isclose(c.degrees, 90, rel_tol=1e-10)
    
    def test_multiply_by_fraction(self):
        """Multiply by fraction."""
        a = Angle(degrees=90)
        c = a * 0.5
        assert math.isclose(c.degrees, 45, rel_tol=1e-10)
    
    # ─── Division ───────────────────────────────────────────────────────────
    
    def test_divide_by_scalar(self):
        """Divide angle by scalar."""
        a = Angle(degrees=90)
        c = a / 2
        assert math.isclose(c.degrees, 45, rel_tol=1e-10)
    
    @pytest.mark.edge
    def test_divide_by_zero(self):
        """Division by zero raises."""
        a = Angle(degrees=90)
        with pytest.raises(ZeroDivisionError):
            _ = a / 0
    
    # ─── Negation ───────────────────────────────────────────────────────────
    
    def test_negate(self):
        """Negate angle."""
        a = Angle(degrees=45)
        c = -a
        assert math.isclose(c.degrees, -45, rel_tol=1e-10)
    
    def test_negate_negative(self):
        """Negate negative angle."""
        a = Angle(degrees=-45)
        c = -a
        assert math.isclose(c.degrees, 45, rel_tol=1e-10)
    
    # ─── Absolute Value ─────────────────────────────────────────────────────
    
    def test_abs_negative(self):
        """Absolute value of negative angle."""
        a = Angle(degrees=-45)
        c = abs(a)
        assert math.isclose(c.degrees, 45, rel_tol=1e-10)
    
    def test_abs_positive(self):
        """Absolute value of positive angle."""
        a = Angle(degrees=45)
        c = abs(a)
        assert math.isclose(c.degrees, 45, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  NORMALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestAngleNormalization:
    """
    Tests for angle normalization to standard ranges.
    
    Default normalization: [0°, 360°)
    Centered at 0: (-180°, 180°]
    """
    
    def test_normalize_positive_overflow(self):
        """Normalize angle > 360°."""
        a = Angle(degrees=450)
        n = a.normalize()
        assert math.isclose(n.degrees, 90, rel_tol=1e-10)
    
    def test_normalize_negative(self):
        """Normalize negative angle to [0, 360)."""
        a = Angle(degrees=-90)
        n = a.normalize()
        assert math.isclose(n.degrees, 270, rel_tol=1e-10)
    
    def test_normalize_large_negative(self):
        """Normalize very negative angle."""
        a = Angle(degrees=-450)
        n = a.normalize()
        assert math.isclose(n.degrees, 270, rel_tol=1e-10)
    
    def test_normalize_centered_positive(self):
        """Normalize to (-180, 180] - positive case."""
        a = Angle(degrees=270)
        n = a.normalize(center=0)
        assert math.isclose(n.degrees, -90, rel_tol=1e-10)
    
    def test_normalize_centered_at_180(self):
        """180° stays at 180° when centered at 0."""
        a = Angle(degrees=180)
        n = a.normalize(center=0)
        assert math.isclose(abs(n.degrees), 180, rel_tol=1e-10)
    
    @pytest.mark.edge
    def test_normalize_at_boundary(self):
        """Test normalization at exact boundary."""
        a = Angle(degrees=360)
        n = a.normalize()
        assert math.isclose(n.degrees, 0, abs_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  TRIGONOMETRY
# ═══════════════════════════════════════════════════════════════════════════════

class TestAngleTrigonometry:
    """
    Tests for trigonometric functions on angles.
    
    These methods work directly on the angle's value,
    converting to radians internally.
    """
    
    # ─── Sine ───────────────────────────────────────────────────────────────
    
    def test_sin_90(self):
        """sin(90°) = 1."""
        a = Angle(degrees=90)
        assert math.isclose(a.sin(), 1.0, rel_tol=1e-10)
    
    def test_sin_0(self):
        """sin(0°) = 0."""
        a = Angle(degrees=0)
        assert math.isclose(a.sin(), 0.0, abs_tol=1e-10)
    
    def test_sin_30(self):
        """sin(30°) = 0.5."""
        a = Angle(degrees=30)
        assert math.isclose(a.sin(), 0.5, rel_tol=1e-10)
    
    # ─── Cosine ─────────────────────────────────────────────────────────────
    
    def test_cos_0(self):
        """cos(0°) = 1."""
        a = Angle(degrees=0)
        assert math.isclose(a.cos(), 1.0, rel_tol=1e-10)
    
    def test_cos_90(self):
        """cos(90°) = 0."""
        a = Angle(degrees=90)
        assert math.isclose(a.cos(), 0.0, abs_tol=1e-10)
    
    def test_cos_60(self):
        """cos(60°) = 0.5."""
        a = Angle(degrees=60)
        assert math.isclose(a.cos(), 0.5, rel_tol=1e-10)
    
    # ─── Tangent ────────────────────────────────────────────────────────────
    
    def test_tan_45(self):
        """tan(45°) = 1."""
        a = Angle(degrees=45)
        assert math.isclose(a.tan(), 1.0, rel_tol=1e-10)
    
    def test_tan_0(self):
        """tan(0°) = 0."""
        a = Angle(degrees=0)
        assert math.isclose(a.tan(), 0.0, abs_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  ANGULAR SEPARATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestAngularSeparation:
    """
    Tests for calculating angular separation between celestial coordinates.
    
    Uses the Vincenty formula for numerical stability at all separations.
    """
    
    def test_same_point_zero_separation(self):
        """Separation of a point with itself is zero."""
        ra = Angle(hours=12)
        dec = Angle(degrees=45)
        sep = angular_separation(ra, dec, ra, dec)
        assert math.isclose(sep.degrees, 0, abs_tol=1e-10)
    
    def test_pole_to_pole_180_degrees(self):
        """North to South pole is 180°."""
        ra = Angle(hours=0)
        sep = angular_separation(
            ra, Angle(degrees=90),
            ra, Angle(degrees=-90)
        )
        assert math.isclose(sep.degrees, 180, rel_tol=1e-10)
    
    def test_equator_90_degrees_apart(self):
        """6 hours apart on equator is 90°."""
        dec = Angle(degrees=0)
        sep = angular_separation(
            Angle(hours=0), dec,
            Angle(hours=6), dec
        )
        assert math.isclose(sep.degrees, 90, rel_tol=1e-10)
    
    def test_equator_180_degrees_apart(self):
        """12 hours apart on equator is 180°."""
        dec = Angle(degrees=0)
        sep = angular_separation(
            Angle(hours=0), dec,
            Angle(hours=12), dec
        )
        assert math.isclose(sep.degrees, 180, rel_tol=1e-10)
    
    @pytest.mark.golden
    def test_sirius_betelgeuse_separation(self):
        """
        Known separation: Sirius to Betelgeuse ≈ 27°.
        
        Sirius: RA 6h45m, Dec -16°43'
        Betelgeuse: RA 5h55m, Dec +7°24'
        """
        sirius_ra = Angle.from_hms(6, 45, 0)
        sirius_dec = Angle.from_dms(-16, 43, 0)
        betel_ra = Angle.from_hms(5, 55, 0)
        betel_dec = Angle.from_dms(7, 24, 0)
        
        sep = angular_separation(sirius_ra, sirius_dec, betel_ra, betel_dec)
        assert 26 < sep.degrees < 28
    
    @pytest.mark.verbose
    def test_verbose_output(self):
        """Verbose mode produces calculation steps."""
        ctx = VerboseContext()
        angular_separation(
            Angle(hours=12), Angle(degrees=45),
            Angle(hours=13), Angle(degrees=46),
            verbose=ctx
        )
        assert len(ctx.steps) > 0


# ═══════════════════════════════════════════════════════════════════════════════
#  POSITION ANGLE
# ═══════════════════════════════════════════════════════════════════════════════

class TestPositionAngle:
    """
    Tests for calculating position angle between celestial coordinates.
    
    Position angle is measured N through E:
      - 0° = North
      - 90° = East
      - 180° = South
      - 270° = West
    """
    
    def test_due_north_is_0(self):
        """Point due north has PA = 0°."""
        ra = Angle(hours=12)
        pa = position_angle(
            ra, Angle(degrees=45),
            ra, Angle(degrees=46)
        )
        assert math.isclose(pa.degrees, 0, abs_tol=0.1)
    
    def test_due_south_is_180(self):
        """Point due south has PA = 180°."""
        ra = Angle(hours=12)
        pa = position_angle(
            ra, Angle(degrees=45),
            ra, Angle(degrees=44)
        )
        assert math.isclose(pa.degrees, 180, abs_tol=0.1)
    
    def test_due_east_is_90(self):
        """Point due east has PA ≈ 90°."""
        dec = Angle(degrees=0)
        pa = position_angle(
            Angle(hours=12), dec,
            Angle(hours=12.1), dec
        )
        assert math.isclose(pa.degrees, 90, abs_tol=1)
    
    def test_due_west_is_270(self):
        """Point due west has PA ≈ 270°."""
        dec = Angle(degrees=0)
        pa = position_angle(
            Angle(hours=12), dec,
            Angle(hours=11.9), dec
        )
        assert math.isclose(pa.degrees, 270, abs_tol=1)


# ═══════════════════════════════════════════════════════════════════════════════
#  PROPERTY-BASED TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestAngleProperties:
    """
    Property-based tests using Hypothesis.
    
    These tests verify invariants that should hold for all angles.
    """
    
    @given(st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False))
    @settings(max_examples=200)
    def test_normalize_always_in_range(self, deg):
        """Normalized angle is always in [0, 360)."""
        a = Angle(degrees=deg)
        n = a.normalize()
        assert 0 <= n.degrees < 360
    
    @given(st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False))
    @settings(max_examples=200)
    def test_sin_squared_plus_cos_squared_is_one(self, deg):
        """sin²(θ) + cos²(θ) = 1."""
        a = Angle(degrees=deg)
        identity = a.sin()**2 + a.cos()**2
        assert math.isclose(identity, 1.0, rel_tol=1e-10)
    
    @given(st.floats(min_value=-10000, max_value=10000, allow_nan=False, allow_infinity=False),
           st.floats(min_value=-10000, max_value=10000, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_add_is_commutative(self, deg1, deg2):
        """a + b = b + a."""
        a = Angle(degrees=deg1)
        b = Angle(degrees=deg2)
        assert math.isclose((a + b).degrees, (b + a).degrees, rel_tol=1e-10)
