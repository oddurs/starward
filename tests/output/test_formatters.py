"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          FORMATTER TESTS                                     ║
║                                                                              ║
║  Tests for output formatters - plain text, JSON, and LaTeX.                  ║
║  Beautiful presentation of celestial calculations.                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import json
import pytest

from astr0.output.formatters import (
    PlainFormatter, JSONFormatter, LaTeXFormatter
)


# ═══════════════════════════════════════════════════════════════════════════════
#  PLAIN FORMATTER
# ═══════════════════════════════════════════════════════════════════════════════

class TestPlainFormatter:
    """
    Tests for plain text output formatting.
    """
    
    def test_format_angle_degrees(self):
        """Format angle in degrees."""
        formatter = PlainFormatter()
        result = formatter.format_angle(45.5, 'degrees')
        assert '45' in result
    
    def test_format_angle_dms(self):
        """Format angle in DMS."""
        formatter = PlainFormatter()
        result = formatter.format_angle(45.5, 'dms')
        assert '45' in result and '30' in result
    
    def test_format_angle_hms(self):
        """Format angle in HMS."""
        formatter = PlainFormatter()
        result = formatter.format_angle(180.0, 'hms')
        assert '12' in result  # 180° = 12h


class TestPlainFormatterTime:
    """
    Tests for plain formatter time output.
    """
    
    def test_format_jd(self):
        """Format Julian Date."""
        formatter = PlainFormatter()
        result = formatter.format_jd(2451545.0)
        assert '2451545' in result


# ═══════════════════════════════════════════════════════════════════════════════
#  JSON FORMATTER
# ═══════════════════════════════════════════════════════════════════════════════

class TestJSONFormatter:
    """
    Tests for JSON output formatting.
    """
    
    def test_output_is_valid_json(self):
        """Output is valid JSON."""
        formatter = JSONFormatter()
        result = formatter.format({'key': 'value'})
        
        # Should parse without error
        parsed = json.loads(result)
        assert parsed['key'] == 'value'
    
    def test_pretty_print(self):
        """JSON is pretty-printed."""
        formatter = JSONFormatter(pretty=True)
        result = formatter.format({'key': 'value'})
        
        # Pretty print has newlines
        assert '\n' in result


# ═══════════════════════════════════════════════════════════════════════════════
#  LATEX FORMATTER
# ═══════════════════════════════════════════════════════════════════════════════

class TestLaTeXFormatter:
    """
    Tests for LaTeX output formatting.
    
    Added in v0.2 for publication-ready output.
    """
    
    def test_format_angle_degrees(self):
        """Format angle with degree symbol."""
        formatter = LaTeXFormatter()
        result = formatter.format_angle(45.5, 'degrees')
        assert '45' in result
        assert r'\degree' in result or '°' in result
    
    def test_format_angle_dms(self):
        """Format angle in DMS with proper symbols."""
        formatter = LaTeXFormatter()
        result = formatter.format_angle(45.5, 'dms')
        # Should have degree/arcmin/arcsec symbols
        assert '45' in result
    
    def test_format_coordinates(self):
        """Format celestial coordinates."""
        formatter = LaTeXFormatter()
        result = formatter.format_coord(187.5, 45.5, 'icrs')
        assert 'RA' in result or 'α' in result or '187' in result
    
    def test_format_table(self):
        """Format data as LaTeX table."""
        formatter = LaTeXFormatter()
        data = [
            {'name': 'Sirius', 'ra': '06h45m'},
            {'name': 'Vega', 'ra': '18h37m'}
        ]
        result = formatter.format_table(data)
        assert 'tabular' in result or 'begin' in result
