"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          PRECISION TESTS                                     ║
║                                                                              ║
║  Tests for the precision configuration system.                               ║
║  Accuracy is never sacrificed — only display precision is configurable.      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import pytest
import os

from astr0.core.precision import (
    PrecisionConfig,
    PrecisionLevel,
    get_precision,
    set_precision,
    precision_context,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  PRECISION LEVELS
# ═══════════════════════════════════════════════════════════════════════════════

class TestPrecisionLevel:
    """Tests for PrecisionLevel enum."""
    
    def test_level_values(self):
        """Precision levels have correct decimal counts."""
        assert PrecisionLevel.COMPACT.value == 2
        assert PrecisionLevel.DISPLAY.value == 4
        assert PrecisionLevel.STANDARD.value == 6
        assert PrecisionLevel.HIGH.value == 10
        assert PrecisionLevel.FULL.value == 15
    
    def test_from_string_names(self):
        """Can parse level from string name."""
        assert PrecisionLevel.from_string('compact') == PrecisionLevel.COMPACT
        assert PrecisionLevel.from_string('FULL') == PrecisionLevel.FULL
        assert PrecisionLevel.from_string('Standard') == PrecisionLevel.STANDARD
    
    def test_from_string_integer(self):
        """Can parse level from integer string."""
        assert PrecisionLevel.from_string('6') == PrecisionLevel.STANDARD
        assert PrecisionLevel.from_string('10') == PrecisionLevel.HIGH
        # Non-standard integer returns the integer
        result = PrecisionLevel.from_string('8')
        assert result == 8
    
    def test_from_string_invalid(self):
        """Invalid string raises ValueError."""
        with pytest.raises(ValueError):
            PrecisionLevel.from_string('invalid')


# ═══════════════════════════════════════════════════════════════════════════════
#  PRECISION CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

class TestPrecisionConfig:
    """Tests for PrecisionConfig dataclass."""
    
    def test_default_values(self):
        """Default config has standard values."""
        config = PrecisionConfig()
        assert config.decimals == 6
        assert config.angle_arcsec == 2
        assert config.time_seconds == 2
        assert config.coordinates == 6
    
    def test_from_level(self):
        """Can create config from precision level."""
        config = PrecisionConfig.from_level(PrecisionLevel.FULL)
        assert config.decimals == 15
        
        config = PrecisionConfig.from_level(PrecisionLevel.COMPACT)
        assert config.decimals == 2
    
    def test_from_integer(self):
        """Can create config from integer."""
        config = PrecisionConfig.from_level(8)
        assert config.decimals == 8
    
    def test_factory_methods(self):
        """Factory methods create correct configs."""
        assert PrecisionConfig.compact().decimals == 2
        assert PrecisionConfig.display().decimals == 4
        assert PrecisionConfig.standard().decimals == 6
        assert PrecisionConfig.high().decimals == 10
        assert PrecisionConfig.full().decimals == 15
    
    def test_format_float(self):
        """format_float respects precision setting."""
        config = PrecisionConfig(decimals=4)
        assert config.format_float(3.14159265) == '3.1416'
        
        config = PrecisionConfig(decimals=2)
        assert config.format_float(3.14159265) == '3.14'
    
    def test_format_float_scientific(self):
        """format_float uses scientific notation for large/small numbers."""
        config = PrecisionConfig(decimals=4, scientific_threshold=3)
        # Large number
        result = config.format_float(1234567.89)
        assert 'e' in result.lower()
        # Small number
        result = config.format_float(0.000001234)
        assert 'e' in result.lower()
    
    def test_format_radians(self):
        """format_radians uses radians precision."""
        config = PrecisionConfig(radians=12)
        result = config.format_radians(3.141592653589793)
        assert len(result.split('.')[1]) == 12


# ═══════════════════════════════════════════════════════════════════════════════
#  GLOBAL PRECISION
# ═══════════════════════════════════════════════════════════════════════════════

class TestGlobalPrecision:
    """Tests for global precision get/set functions."""
    
    def test_get_precision_returns_config(self):
        """get_precision returns a PrecisionConfig."""
        prec = get_precision()
        assert isinstance(prec, PrecisionConfig)
    
    def test_set_precision_with_config(self):
        """Can set precision with PrecisionConfig."""
        original = get_precision()
        try:
            config = PrecisionConfig(decimals=12)
            set_precision(config)
            assert get_precision().decimals == 12
        finally:
            set_precision(original)
    
    def test_set_precision_with_level(self):
        """Can set precision with PrecisionLevel."""
        original = get_precision()
        try:
            set_precision(PrecisionLevel.HIGH)
            assert get_precision().decimals == 10
        finally:
            set_precision(original)
    
    def test_set_precision_with_integer(self):
        """Can set precision with integer."""
        original = get_precision()
        try:
            set_precision(8)
            assert get_precision().decimals == 8
        finally:
            set_precision(original)
    
    def test_set_precision_with_string(self):
        """Can set precision with string."""
        original = get_precision()
        try:
            set_precision('full')
            assert get_precision().decimals == 15
        finally:
            set_precision(original)


# ═══════════════════════════════════════════════════════════════════════════════
#  PRECISION CONTEXT
# ═══════════════════════════════════════════════════════════════════════════════

class TestPrecisionContext:
    """Tests for precision_context context manager."""
    
    def test_context_changes_precision(self):
        """Context manager changes precision inside block."""
        original = get_precision()
        try:
            set_precision(PrecisionLevel.STANDARD)
            
            with precision_context(PrecisionLevel.FULL):
                assert get_precision().decimals == 15
            
            # Restored after context
            assert get_precision().decimals == 6
        finally:
            set_precision(original)
    
    def test_context_restores_on_exception(self):
        """Context manager restores precision even on exception."""
        original = get_precision()
        try:
            set_precision(PrecisionLevel.STANDARD)
            
            try:
                with precision_context(PrecisionLevel.FULL):
                    assert get_precision().decimals == 15
                    raise ValueError("test")
            except ValueError:
                pass
            
            # Still restored
            assert get_precision().decimals == 6
        finally:
            set_precision(original)
    
    def test_context_with_string(self):
        """Context manager accepts string precision."""
        original = get_precision()
        try:
            with precision_context('compact'):
                assert get_precision().decimals == 2
        finally:
            set_precision(original)
    
    def test_context_with_integer(self):
        """Context manager accepts integer precision."""
        original = get_precision()
        try:
            with precision_context(7):
                assert get_precision().decimals == 7
        finally:
            set_precision(original)


# ═══════════════════════════════════════════════════════════════════════════════
#  INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestPrecisionIntegration:
    """Integration tests for precision system."""
    
    def test_precision_affects_formatting(self):
        """Different precision levels produce different output."""
        value = 3.14159265358979
        
        compact = PrecisionConfig.compact()
        standard = PrecisionConfig.standard()
        full = PrecisionConfig.full()
        
        compact_str = compact.format_float(value)
        standard_str = standard.format_float(value)
        full_str = full.format_float(value)
        
        # All represent the same value but with different precision
        assert len(compact_str) < len(standard_str) < len(full_str)
        assert float(compact_str) == pytest.approx(value, rel=0.01)
        assert float(standard_str) == pytest.approx(value, rel=1e-6)
        assert float(full_str) == pytest.approx(value, rel=1e-15)
    
    def test_internal_precision_preserved(self):
        """Setting display precision doesn't affect internal calculations."""
        # The actual float value maintains full precision regardless
        # of display settings
        value = 3.14159265358979323846
        
        set_precision(PrecisionLevel.COMPACT)
        # The value itself is unchanged
        assert value == 3.14159265358979323846
        
        # Only display is affected
        prec = get_precision()
        displayed = prec.format_float(value)
        assert displayed == '3.14'  # Compact shows 2 decimals
        
        # But we can always get full precision back
        set_precision(PrecisionLevel.FULL)
        prec = get_precision()
        displayed = prec.format_float(value)
        assert len(displayed.split('.')[1]) == 15
