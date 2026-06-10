import pytest
from pydantic import ValidationError

# Make sure this import matches the name of your file containing the models
from src.parsing.models import MapConfigModel


# ==========================================
# FIXTURE: Valid Map Generator
# ==========================================
@pytest.fixture
def valid_map_data() -> dict:
    """
    Returns a perfectly valid base dictionary representing a parsed map.
    Includes 'line_num' keys to simulate the output of the MapParser.
    """
    return {
        "nb_drones": 5,
        "zones": [
            {
                "name": "start", "x": 0, "y": 0, "is_start": True,
                "is_end": False,
                "max_drones": 10, "line_num": 2
            },
            {
                "name": "relais", "x": 5, "y": 5, "is_start": False,
                "is_end": False,
                "max_drones": 1, "line_num": 3
            },
            {
                "name": "arrivee", "x": 10, "y": 10, "is_start": False,
                "is_end": True,
                "max_drones": 1, "line_num": 4
            }
        ],
        "connections": [
            {"zone1": "start", "zone2": "relais", "max_link_capacity": 2,
             "line_num": 5},
            {"zone1": "relais", "zone2": "arrivee", "max_link_capacity": 2,
             "line_num": 6}
        ]
    }


# ==========================================
# TESTS: Valid Case
# ==========================================
def test_valid_map_config(valid_map_data):
    """Tests that a perfectly valid map configuration raises no errors."""
    model = MapConfigModel(**valid_map_data)
    assert model.nb_drones == 5
    assert len(model.zones) == 3
    assert len(model.connections) == 2


# ==========================================
# TESTS: Zone Edge Cases
# ==========================================
def test_duplicate_zone_names(valid_map_data):
    """Tests rejection if two zones share the exact same name."""
    valid_map_data["zones"][1]["name"] = "start"

    with pytest.raises(
            ValidationError, match="Cannot use the same zone name 'start'"):
        MapConfigModel(**valid_map_data)


def test_duplicate_coordinates(valid_map_data):
    """
    Tests rejection if two zones are placed at the exact same
    coordinates.
    """
    valid_map_data["zones"][1]["x"] = 0
    valid_map_data["zones"][1]["y"] = 0

    with pytest.raises(
            ValidationError, match=(
                "Another zone already exists at these coordinates")):
        MapConfigModel(**valid_map_data)


def test_max_drones_too_low(valid_map_data):
    """Tests rejection if a zone's max_drones capacity is less than 1."""
    valid_map_data["zones"][1]["max_drones"] = 0

    with pytest.raises(ValidationError, match="max_drones must be at least 1"):
        MapConfigModel(**valid_map_data)


# ==========================================
# TESTS: Start / End Hub Edge Cases
# ==========================================
def test_start_hub_capacity_too_low(valid_map_data):
    """
    Tests rejection if the starting hub cannot accommodate
    all the drones."""
    valid_map_data["nb_drones"] = 50
    valid_map_data["zones"][0]["max_drones"] = 10

    with pytest.raises(
        ValidationError, match=(
            "cannot be less than the total number of drones")):
        MapConfigModel(**valid_map_data)


def test_missing_start_hub(valid_map_data):
    """Tests rejection if the map has no start_hub configured."""
    valid_map_data["zones"][0]["is_start"] = False

    with pytest.raises(
            ValidationError, match="There is no start_hub in the map"):
        MapConfigModel(**valid_map_data)


def test_missing_end_hub(valid_map_data):
    """Tests rejection if the map has no end_hub configured."""
    valid_map_data["zones"][2]["is_end"] = False

    with pytest.raises(
            ValidationError, match="There is no end_hub in the map"):
        MapConfigModel(**valid_map_data)


def test_multiple_start_hubs(valid_map_data):
    """Tests rejection if the map contains multiple start_hubs."""
    valid_map_data["zones"][1]["is_start"] = True
    valid_map_data["zones"][1]["max_drones"] = 5

    with pytest.raises(
            ValidationError, match="There must be exactly one start_hub"):
        MapConfigModel(**valid_map_data)


# ==========================================
# TESTS: Connection Edge Cases
# ==========================================
def test_connection_unknown_zone(valid_map_data):
    """Tests rejection if a connection targets a zone that does not exist."""
    valid_map_data["connections"][0]["zone1"] = "narnia"

    with pytest.raises(
            ValidationError, match="'narnia' refers to an unknown zone"):
        MapConfigModel(**valid_map_data)


def test_auto_connection(valid_map_data):
    """Tests rejection if a zone attempts to connect to itself."""
    valid_map_data["connections"][0]["zone2"] = "start"

    with pytest.raises(
            ValidationError, match="A zone cannot connect to itself"):
        MapConfigModel(**valid_map_data)


def test_duplicate_connection_identical(valid_map_data):
    """
    Tests rejection of identically duplicated connections
    (e.g., A-B and A-B).
    """
    valid_map_data["connections"].append(
        valid_map_data["connections"][0].copy())

    with pytest.raises(
            ValidationError, match=(
                "The same connection must not appear more than once")):
        MapConfigModel(**valid_map_data)


def test_duplicate_connection_reversed(valid_map_data):
    """
    Tests rejection of reverse duplicated connections
    (e.g., A-B and B-A).
    """
    valid_map_data["connections"].append({
        "zone1": "relais",
        "zone2": "start",
        "max_link_capacity": 5,
        "line_num": 99})

    with pytest.raises(
            ValidationError, match=(
                "The same connection must not appear more than once")):
        MapConfigModel(**valid_map_data)


def test_max_link_capacity_too_low(valid_map_data):
    """Tests rejection if a connection's max_link_capacity is less than 1."""
    valid_map_data["connections"][0]["max_link_capacity"] = 0

    with pytest.raises(
            ValidationError, match="max_link_capacity must be at least 1"):
        MapConfigModel(**valid_map_data)
