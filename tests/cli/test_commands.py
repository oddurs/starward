"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         CLI COMMAND TESTS                                    ║
║                                                                              ║
║  Integration tests for the astr0 command-line interface.                     ║
║  Verifying the bridge between algorithms and astronomers.                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from astr0.cli import main


# ═══════════════════════════════════════════════════════════════════════════════
#  TEST FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN COMMAND
# ═══════════════════════════════════════════════════════════════════════════════

class TestMainCommand:
    """
    Tests for the main astr0 command entry point.
    """
    
    def test_help(self, runner):
        """--help displays usage information."""
        result = runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert 'astr0' in result.output.lower() or 'usage' in result.output.lower()
    
    def test_version(self, runner):
        """--version displays version string."""
        result = runner.invoke(main, ['--version'])
        assert result.exit_code == 0
        assert '0.' in result.output  # Version number


# ═══════════════════════════════════════════════════════════════════════════════
#  TIME COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

class TestTimeCommands:
    """
    Tests for time-related CLI commands.
    """
    
    def test_time_now(self, runner):
        """time now displays current time."""
        result = runner.invoke(main, ['time', 'now'])
        assert result.exit_code == 0
        assert 'JD' in result.output or 'UTC' in result.output
    
    def test_time_convert_jd(self, runner):
        """time convert handles Julian Date."""
        result = runner.invoke(main, ['time', 'convert', '2451545.0'])
        assert result.exit_code == 0
        assert '2000' in result.output  # J2000.0 = 2000-01-01
    
    def test_time_gmst(self, runner):
        """time gmst calculates sidereal time."""
        result = runner.invoke(main, ['time', 'gmst', '2451545.0'])
        assert result.exit_code == 0
    
    def test_time_lst(self, runner):
        """time lst calculates local sidereal time."""
        result = runner.invoke(main, ['time', 'lst', '2451545.0', '-75.0'])
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  ANGLE COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

class TestAngleCommands:
    """
    Tests for angle-related CLI commands.
    """
    
    def test_angle_convert_degrees(self, runner):
        """angle convert displays conversions."""
        result = runner.invoke(main, ['angle', 'convert', '45.5'])
        assert result.exit_code == 0
        assert '45' in result.output
    
    def test_angle_convert_dms(self, runner):
        """angle convert handles DMS input."""
        result = runner.invoke(main, ['angle', 'convert', '45d30m00s'])
        assert result.exit_code == 0
    
    def test_angle_convert_hms(self, runner):
        """angle convert handles HMS input."""
        result = runner.invoke(main, ['angle', 'convert', '12h30m00s'])
        assert result.exit_code == 0
    
    def test_angle_sep(self, runner):
        """angle sep calculates angular separation."""
        result = runner.invoke(main, [
            'angle', 'sep',
            '10h00m00s', '+20d00m00s',
            '10h10m00s', '+21d00m00s'
        ])
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  COORDINATE COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCoordCommands:
    """
    Tests for coordinate-related CLI commands.
    """
    
    def test_coord_convert_to_galactic(self, runner):
        """coord convert transforms to Galactic."""
        result = runner.invoke(main, [
            'coord', 'convert',
            '12h00m00s', '+45d00m00s',
            'galactic'
        ])
        assert result.exit_code == 0
        assert 'l' in result.output.lower() or 'galactic' in result.output.lower()
    
    def test_coord_convert_to_icrs(self, runner):
        """coord convert transforms to ICRS."""
        result = runner.invoke(main, [
            'coord', 'convert',
            '180.0', '45.0',
            'icrs'
        ])
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

class TestConstantsCommands:
    """
    Tests for constants-related CLI commands.
    """
    
    def test_const_list(self, runner):
        """const list displays all constants."""
        result = runner.invoke(main, ['const', 'list'])
        assert result.exit_code == 0
        assert 'AU' in result.output or 'Solar' in result.output
    
    def test_const_search(self, runner):
        """const search finds matching constants."""
        result = runner.invoke(main, ['const', 'search', 'solar'])
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  SUN COMMANDS (v0.2)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSunCommands:
    """
    Tests for Sun-related CLI commands.
    """
    
    def test_sun_position(self, runner):
        """sun position displays solar coordinates."""
        result = runner.invoke(main, ['sun', 'position'])
        assert result.exit_code == 0
        # Should show RA/Dec or ecliptic coordinates
    
    def test_sun_rise(self, runner):
        """sun rise calculates sunrise."""
        result = runner.invoke(main, [
            'sun', 'rise',
            '--lat', '51.5',
            '--lon', '0.0'
        ])
        assert result.exit_code == 0
    
    def test_sun_set(self, runner):
        """sun set calculates sunset."""
        result = runner.invoke(main, [
            'sun', 'set',
            '--lat', '51.5',
            '--lon', '0.0'
        ])
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  MOON COMMANDS (v0.2)
# ═══════════════════════════════════════════════════════════════════════════════

class TestMoonCommands:
    """
    Tests for Moon-related CLI commands.
    """
    
    def test_moon_position(self, runner):
        """moon position displays lunar coordinates."""
        result = runner.invoke(main, ['moon', 'position'])
        assert result.exit_code == 0
    
    def test_moon_phase(self, runner):
        """moon phase displays current phase."""
        result = runner.invoke(main, ['moon', 'phase'])
        assert result.exit_code == 0
        # Should include phase name
    
    def test_moon_next(self, runner):
        """moon next finds next phase."""
        result = runner.invoke(main, ['moon', 'next', 'full'])
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  OBSERVER COMMANDS (v0.2)
# ═══════════════════════════════════════════════════════════════════════════════

class TestObserverCommands:
    """
    Tests for observer management CLI commands.
    """
    
    def test_observer_list(self, runner):
        """observer list shows saved observers."""
        result = runner.invoke(main, ['observer', 'list'])
        # May return empty list or saved observers
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  VISIBILITY COMMANDS (v0.2)
# ═══════════════════════════════════════════════════════════════════════════════

class TestVisibilityCommands:
    """
    Tests for visibility-related CLI commands.
    """
    
    def test_vis_altitude(self, runner):
        """vis altitude calculates target altitude."""
        result = runner.invoke(main, [
            'vis', 'altitude',
            '12h00m00s', '+45d00m00s',
            '--lat', '51.5',
            '--lon', '0.0'
        ])
        assert result.exit_code == 0
    
    def test_vis_airmass(self, runner):
        """vis airmass calculates airmass."""
        result = runner.invoke(main, [
            'vis', 'airmass',
            '12h00m00s', '+45d00m00s',
            '--lat', '51.5',
            '--lon', '0.0'
        ])
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  OUTPUT FORMAT OPTIONS
# ═══════════════════════════════════════════════════════════════════════════════

class TestOutputFormats:
    """
    Tests for output format options.
    """
    
    def test_json_output(self, runner):
        """--json outputs JSON format."""
        result = runner.invoke(main, ['time', 'now', '--json'])
        assert result.exit_code == 0
        assert '{' in result.output  # JSON object
    
    def test_verbose_output(self, runner):
        """--verbose shows calculation steps."""
        result = runner.invoke(main, ['angle', 'sep',
            '10h00m00s', '+20d00m00s',
            '10h10m00s', '+21d00m00s',
            '--verbose'
        ])
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  COMMAND ALIASES
# ═══════════════════════════════════════════════════════════════════════════════

class TestCommandAliases:
    """
    Tests for command shorthand aliases.
    """
    
    def test_t_alias_for_time(self, runner):
        """'t' is alias for 'time'."""
        result = runner.invoke(main, ['t', 'now'])
        assert result.exit_code == 0
    
    def test_a_alias_for_angle(self, runner):
        """'a' is alias for 'angle'."""
        result = runner.invoke(main, ['a', 'convert', '45'])
        assert result.exit_code == 0
    
    def test_c_alias_for_coord(self, runner):
        """'c' is alias for 'coord'."""
        result = runner.invoke(main, ['c', 'convert', '180', '45', 'galactic'])
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  ERROR HANDLING
# ═══════════════════════════════════════════════════════════════════════════════

class TestErrorHandling:
    """
    Tests for CLI error handling.
    """
    
    def test_invalid_angle(self, runner):
        """Invalid angle input shows error."""
        result = runner.invoke(main, ['angle', 'convert', 'not_an_angle'])
        assert result.exit_code != 0 or 'error' in result.output.lower()
    
    def test_unknown_command(self, runner):
        """Unknown command shows error."""
        result = runner.invoke(main, ['nonexistent'])
        assert result.exit_code != 0
    
    def test_missing_argument(self, runner):
        """Missing required argument shows error."""
        result = runner.invoke(main, ['angle', 'sep', '10h00m00s'])
        assert result.exit_code != 0
