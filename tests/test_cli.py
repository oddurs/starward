"""
CLI integration tests.
"""

import json
import pytest
from click.testing import CliRunner

from astr0.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestCLIBasics:
    """Basic CLI functionality tests."""
    
    def test_help(self, runner):
        result = runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert 'astr0' in result.output.lower()
    
    def test_version(self, runner):
        result = runner.invoke(main, ['--version'])
        assert result.exit_code == 0
        assert '0.1.0' in result.output
    
    def test_about(self, runner):
        result = runner.invoke(main, ['about'])
        assert result.exit_code == 0
        assert 'Astronomy' in result.output or 'astronomy' in result.output.lower()


class TestTimeCommands:
    """Tests for time-related CLI commands."""
    
    def test_time_now(self, runner):
        result = runner.invoke(main, ['time', 'now'])
        assert result.exit_code == 0
        assert 'Julian Date' in result.output
    
    def test_time_now_json(self, runner):
        result = runner.invoke(main, ['-o', 'json', 'time', 'now'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'julian_date' in data
        assert 'utc' in data
    
    def test_time_convert(self, runner):
        result = runner.invoke(main, ['time', 'convert', '2451545.0'])
        assert result.exit_code == 0
        assert '2000' in result.output
    
    def test_time_jd(self, runner):
        result = runner.invoke(main, ['time', 'jd', '2000', '1', '1', '12', '0', '0'])
        assert result.exit_code == 0
        assert '2451545' in result.output
    
    def test_time_lst(self, runner):
        result = runner.invoke(main, ['time', 'lst', '0'])
        assert result.exit_code == 0
        assert 'LST' in result.output
    
    def test_time_alias(self, runner):
        """Test 't' alias for 'time'."""
        result = runner.invoke(main, ['t', 'now'])
        assert result.exit_code == 0


class TestCoordsCommands:
    """Tests for coordinate-related CLI commands."""
    
    def test_coords_parse(self, runner):
        result = runner.invoke(main, ['coords', 'parse', '12h30m00s +45d30m00s'])
        assert result.exit_code == 0
        assert 'Right Ascension' in result.output
        assert 'Declination' in result.output
    
    def test_coords_transform_galactic(self, runner):
        result = runner.invoke(main, ['coords', 'transform', '12h30m +45d', '--to', 'galactic'])
        assert result.exit_code == 0
        assert 'Galactic' in result.output
    
    def test_coords_transform_altaz_requires_location(self, runner):
        result = runner.invoke(main, ['coords', 'transform', '12h +45d', '--to', 'altaz'])
        assert result.exit_code != 0
        assert 'lat' in result.output.lower() or 'lon' in result.output.lower()
    
    def test_coords_transform_altaz(self, runner):
        result = runner.invoke(main, [
            'coords', 'transform', '12h +45d',
            '--to', 'altaz',
            '--lat', '40',
            '--lon', '-75'
        ])
        assert result.exit_code == 0
        assert 'Alt' in result.output
    
    def test_coords_json(self, runner):
        result = runner.invoke(main, ['-o', 'json', 'coords', 'parse', '12h +45d'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'ra' in data
        assert 'dec' in data
    
    def test_coords_alias(self, runner):
        """Test 'c' alias for 'coords'."""
        result = runner.invoke(main, ['c', 'parse', '12h +45d'])
        assert result.exit_code == 0


class TestAnglesCommands:
    """Tests for angle-related CLI commands."""
    
    def test_angles_sep(self, runner):
        result = runner.invoke(main, ['angles', 'sep', '12h +45d', '12h30m +46d'])
        assert result.exit_code == 0
        assert 'Separation' in result.output
    
    def test_angles_pa(self, runner):
        result = runner.invoke(main, ['angles', 'pa', '12h +45d', '12h30m +46d'])
        assert result.exit_code == 0
        assert 'Position Angle' in result.output
    
    def test_angles_convert(self, runner):
        result = runner.invoke(main, ['angles', 'convert', '45.5'])
        assert result.exit_code == 0
        assert 'Degrees' in result.output
        assert 'Radians' in result.output
    
    def test_angles_convert_radians(self, runner):
        result = runner.invoke(main, ['angles', 'convert', '1.5708', '--unit', 'rad'])
        assert result.exit_code == 0
        assert '90' in result.output  # Should be close to 90 degrees
    
    def test_angles_json(self, runner):
        result = runner.invoke(main, ['-o', 'json', 'angles', 'convert', '45'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'degrees' in data
        assert 'radians' in data
    
    def test_angles_alias(self, runner):
        """Test 'a' alias for 'angles'."""
        result = runner.invoke(main, ['a', 'convert', '45'])
        assert result.exit_code == 0


class TestConstantsCommands:
    """Tests for constants-related CLI commands."""
    
    def test_constants_list(self, runner):
        result = runner.invoke(main, ['constants', 'list'])
        assert result.exit_code == 0
        assert 'Speed of light' in result.output
    
    def test_constants_search(self, runner):
        result = runner.invoke(main, ['constants', 'search', 'solar'])
        assert result.exit_code == 0
        assert 'Solar' in result.output
    
    def test_constants_show(self, runner):
        result = runner.invoke(main, ['constants', 'show', 'AU'])
        assert result.exit_code == 0
        assert 'Astronomical Unit' in result.output
    
    def test_constants_json(self, runner):
        result = runner.invoke(main, ['-o', 'json', 'constants', 'show', 'AU'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'value' in data
    
    def test_constants_alias(self, runner):
        """Test 'const' alias for 'constants'."""
        result = runner.invoke(main, ['const', 'list'])
        assert result.exit_code == 0


class TestVerboseMode:
    """Tests for verbose output mode."""
    
    def test_verbose_time(self, runner):
        result = runner.invoke(main, ['--verbose', 'time', 'now'])
        assert result.exit_code == 0
        # Should have more output with verbose
        assert '─' in result.output  # Box drawing chars from verbose output
    
    def test_verbose_coords(self, runner):
        result = runner.invoke(main, ['--verbose', 'coords', 'transform', '12h +45d', '--to', 'galactic'])
        assert result.exit_code == 0
        assert '─' in result.output
    
    def test_verbose_angles(self, runner):
        result = runner.invoke(main, ['--verbose', 'angles', 'sep', '12h +45d', '13h +46d'])
        assert result.exit_code == 0
        assert '─' in result.output
