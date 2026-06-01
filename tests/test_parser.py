import pytest
from src.parser import MapParser  # Adapt the import according to your file name

# ==========================================
# FIXTURES (Initial Configuration)
# ==========================================

@pytest.fixture
def parser():
    """Provides a fresh instance of MapParser for each test."""
    return MapParser()


# ==========================================
# TESTS: Clean Lines
# ==========================================

def test_clean_lines_removes_comments_and_empty_lines(parser):
    """Verifies that comments, trailing spaces, and empty lines are removed."""
    raw_text = """
    # This is a global comment
    nb_drones: 5

    hub: toit1 0 0 # End of line comment
       connection: toit1-toit2
    """
    cleaned = parser._clean_lines(raw_text)
    assert cleaned == [
        "nb_drones: 5",
        "hub: toit1 0 0",
        "connection: toit1-toit2"
    ]


# ==========================================
# TESTS: Valid Cases (Happy Path)
# ==========================================

def test_parse_valid_full_map(parser):
    """Verifies that a complete and valid map is parsed perfectly."""
    raw_text = """nb_drones: 3
    start_hub: depart 0 0 [color=red max_drones=2]
    end_hub: arrivee 10 -10 [zone=priority]
    hub: relais 5 5
    connection: depart-relais
    connection: relais-arrivee [max_link_capacity=4]
    """
    result = parser.parse(raw_text)

    # Global verification
    assert result["nb_drones"] == "3"
    assert len(result["zones"]) == 3
    assert len(result["connections"]) == 2

    # Verification of a Hub with multiple metadata and negative coordinates
    end_hub = result["zones"][1]
    assert end_hub["name"] == "arrivee"
    assert end_hub["y"] == "-10"
    assert end_hub["is_end"] is True
    assert end_hub["zone"] == "priority"

    # Verification of a default vs modified Connection
    assert result["connections"][0]["max_link_capacity"] == 1
    assert result["connections"][1]["max_link_capacity"] == "4"

# ==========================================
# TESTS: Clean Lines
# ==========================================

def test_clean_lines_removes_comments_and_empty_lines(parser):
    """Verifies that comments, trailing spaces, and empty lines are removed."""
    raw_text = """
    # This is a global comment
    nb_drones: 5

    hub: toit1 0 0 # End of line comment
       connection: toit1-toit2
    """
    cleaned = parser._clean_lines(raw_text)

    assert cleaned == [
        (3, "nb_drones: 5"),
        (5, "hub: toit1 0 0"),
        (6, "connection: toit1-toit2")
    ]


def test_empty_file_raises_error(parser):
    """Edge Case: Completely empty file or containing only comments."""
    with pytest.raises(ValueError, match="The map file is empty"):
        parser.parse("# Just a comment\n\n")


def test_missing_nb_drones_first_line(parser):
    """Edge Case: The file does not start with nb_drones."""
    raw_text = "hub: A 0 0\nnb_drones: 5"
    with pytest.raises(ValueError, match="The first line must define"):
        parser.parse(raw_text)


def test_invalid_connection_missing_dash(parser):
    """Edge Case: The user puts a space instead of a dash in the connection."""
    raw_text = "nb_drones: 5\nconnection: A B"
    with pytest.raises(ValueError, match="Syntax error in connection entry"):
        parser.parse(raw_text)


def test_forbidden_metadata_in_connection(parser):
        """Edge Case: An invalid metadata key is inserted into a connection."""
        raw_text = "nb_drones: 5\nconnection: A-B [color=red]"
        with pytest.raises(ValueError, match="Invalid metadata syntax"):
            parser.parse(raw_text)

def test_empty_max_link_capacity_value(parser):
        """Edge Case: The max_link_capacity key is present but empty."""
        raw_text = "nb_drones: 5\nconnection: A-B [max_link_capacity= ]"
        with pytest.raises(ValueError, match="Invalid metadata syntax"):
            parser.parse(raw_text)


def test_invalid_hub_space_in_name(parser):
    """Edge Case: The user puts a space in the zone name."""
    raw_text = "nb_drones: 5\nhub: my hub 0 0"
    with pytest.raises(ValueError, match="Syntax error in hub entry"):
        parser.parse(raw_text)


def test_forbidden_metadata_in_hub(parser):
    """Edge Case: The user invents a metadata key for a zone."""
    raw_text = "nb_drones: 5\nhub: A 0 0 [power=magic]"
    with pytest.raises(ValueError, match="Forbidden metadata key 'power'"):
        parser.parse(raw_text)


def test_unknown_line_key(parser):
    """Edge Case: A line starts with an unknown keyword."""
    raw_text = "nb_drones: 5\ncarbage: A-B"
    with pytest.raises(ValueError, match="Invalid key"):
        parser.parse(raw_text)
