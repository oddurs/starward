"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                            OBSERVER TESTS                                    ║
║                                                                              ║
║  Tests for observer location management and geographic calculations.         ║
║  Where we stand shapes everything we see in the sky.                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import pytest

from astr0.core.observer import Observer


# ═══════════════════════════════════════════════════════════════════════════════
#  OBSERVER CREATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestObserverCreation:
    """
    Tests for creating Observer instances.
    """
    
    def test_from_degrees(self):
        """Create observer from decimal degrees."""
        obs = Observer.from_degrees("Test", 51.4772, -0.0005, elevation=62.0)
        
        assert obs.name == "Test"
        assert obs.lat_deg == pytest.approx(51.4772, rel=1e-6)
        assert obs.lon_deg == pytest.approx(-0.0005, rel=1e-6)
        assert obs.elevation == 62.0
    
    def test_with_timezone(self):
        """Create observer with timezone."""
        obs = Observer.from_degrees(
            "LA", 34.05, -118.25,
            timezone="America/Los_Angeles"
        )
        assert obs.timezone == "America/Los_Angeles"
    
    def test_default_elevation(self):
        """Default elevation is 0."""
        obs = Observer.from_degrees("Test", 45.0, 0.0)
        assert obs.elevation == 0.0
    
    def test_high_elevation(self):
        """High elevation observatories."""
        obs = Observer.from_degrees("Mauna Kea", 19.82, -155.47, elevation=4207.0)
        assert obs.elevation == 4207.0


# ═══════════════════════════════════════════════════════════════════════════════
#  LATITUDE VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestLatitudeValidation:
    """
    Tests for latitude bounds checking.
    
    Valid range: -90° (South Pole) to +90° (North Pole)
    """
    
    def test_north_pole(self):
        """Latitude +90° is valid."""
        obs = Observer.from_degrees("North Pole", 90.0, 0.0)
        assert obs.lat_deg == 90.0
    
    def test_south_pole(self):
        """Latitude -90° is valid."""
        obs = Observer.from_degrees("South Pole", -90.0, 0.0)
        assert obs.lat_deg == -90.0
    
    def test_equator(self):
        """Latitude 0° is valid."""
        obs = Observer.from_degrees("Equator", 0.0, 0.0)
        assert obs.lat_deg == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
#  LONGITUDE HANDLING
# ═══════════════════════════════════════════════════════════════════════════════

class TestLongitudeHandling:
    """
    Tests for longitude storage and normalization.
    """
    
    def test_positive_longitude_east(self):
        """Positive longitude = East."""
        obs = Observer.from_degrees("Tokyo", 35.68, 139.77)
        assert obs.lon_deg == pytest.approx(139.77)
    
    def test_negative_longitude_west(self):
        """Negative longitude = West."""
        obs = Observer.from_degrees("NYC", 40.71, -74.01)
        assert obs.lon_deg == pytest.approx(-74.01)
    
    def test_longitude_stored_as_is(self):
        """Longitude is stored without normalization."""
        obs = Observer.from_degrees("Test", 0.0, 361.0)
        assert obs.lon_deg == 361.0


# ═══════════════════════════════════════════════════════════════════════════════
#  STRING REPRESENTATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestObserverString:
    """
    Tests for Observer string representation.
    """
    
    def test_str_includes_name(self):
        """__str__ includes name."""
        obs = Observer.from_degrees("Greenwich", 51.4772, 0.0, elevation=62.0)
        assert "Greenwich" in str(obs)
    
    def test_str_includes_coordinates(self):
        """__str__ includes coordinates."""
        obs = Observer.from_degrees("Test", 51.4772, 0.0)
        s = str(obs)
        assert "51.4772" in s or "51.48" in s  # May be rounded
    
    def test_repr(self):
        """__repr__ is informative."""
        obs = Observer.from_degrees("Test", 45.0, -90.0)
        r = repr(obs)
        assert "Observer" in r or "Test" in r


# ═══════════════════════════════════════════════════════════════════════════════
#  SERIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestObserverSerialization:
    """
    Tests for Observer serialization to dict/TOML.
    """
    
    def test_to_dict(self):
        """Observer converts to dictionary."""
        obs = Observer.from_degrees("Test", 34.05, -118.25, timezone="America/Los_Angeles")
        d = obs.to_dict()
        
        assert d['name'] == "Test"
        assert d['latitude'] == pytest.approx(34.05)
        assert d['longitude'] == pytest.approx(-118.25)
    
    def test_to_dict_includes_elevation(self):
        """to_dict includes elevation."""
        obs = Observer.from_degrees("Test", 0.0, 0.0, elevation=100.0)
        d = obs.to_dict()
        assert d.get('elevation') == 100.0
    
    def test_to_dict_includes_timezone(self):
        """to_dict includes timezone if set."""
        obs = Observer.from_degrees("Test", 0.0, 0.0, timezone="UTC")
        d = obs.to_dict()
        assert 'timezone' in d or d.get('timezone') == 'UTC'


# ═══════════════════════════════════════════════════════════════════════════════
#  WELL-KNOWN LOCATIONS (FIXTURES)
# ═══════════════════════════════════════════════════════════════════════════════

class TestKnownLocations:
    """
    Tests using well-known observatory locations.
    """
    
    def test_greenwich_fixture(self, greenwich):
        """Greenwich fixture is correctly defined."""
        assert greenwich.name == "Greenwich"
        assert 51 < greenwich.lat_deg < 52
        assert -1 < greenwich.lon_deg < 1
    
    def test_mauna_kea_fixture(self, mauna_kea):
        """Mauna Kea fixture is correctly defined."""
        assert mauna_kea.name == "Mauna Kea"
        assert mauna_kea.elevation > 4000
    
    def test_paranal_fixture(self, paranal):
        """Paranal (Chile) fixture is correctly defined."""
        assert paranal.name == "Paranal"
        assert paranal.lat_deg < 0  # Southern hemisphere
    
    def test_north_pole_fixture(self, north_pole):
        """North Pole fixture is at +90° latitude."""
        assert north_pole.lat_deg == 90.0
    
    def test_equator_fixture(self, equator):
        """Equator fixture is at 0° latitude."""
        assert equator.lat_deg == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
#  EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════════

class TestObserverEdgeCases:
    """
    Tests for edge cases in observer handling.
    """
    
    @pytest.mark.edge
    def test_date_line_east(self):
        """Observer at +180° longitude."""
        obs = Observer.from_degrees("Date Line E", 0.0, 180.0)
        assert obs.lon_deg == 180.0
    
    @pytest.mark.edge
    def test_date_line_west(self):
        """Observer at -180° longitude."""
        obs = Observer.from_degrees("Date Line W", 0.0, -180.0)
        assert obs.lon_deg == -180.0
    
    @pytest.mark.edge
    def test_empty_name(self):
        """Observer with empty name."""
        obs = Observer.from_degrees("", 0.0, 0.0)
        assert obs.name == ""
    
    @pytest.mark.edge
    def test_unicode_name(self):
        """Observer with Unicode name."""
        obs = Observer.from_degrees("東京 🔭", 35.68, 139.77)
        assert "東京" in obs.name
