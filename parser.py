from typing import Any
import re


class MapParser:
    """
    Parses a drone delivery map configuration file.

    This class reads raw map data, extracts entities (drones, zones, and
    connections) using regular expressions, and structures them into a
    dictionary ready for validation.
    """
    def __init__(self) -> None:
        """Initializes the MapParser with pre-compiled regular expressions."""
        self.hub_pattern = re.compile(
            r"^\s*(start_hub|end_hub|hub):\s*"
            r"([^\s\-]+)\s+(-?\d+)\s+"
            r"(-?\d+)(?:\s+\[(.*?)\])?\s*$"
            )
        self.connection_pattern = re.compile(
            r"^\s*connection:\s*"
            r"([^\s\-]+)-([^\s\-]+)"
            r"(?:\s+\[(.*?)\])?\s*$"
            )
        # ?) (avec le point d'interrogation) :
        #  moteur devient paresseux. Il va avancer caractère par caractère
        #  s'arrêter au tout premier crochet fermant qu'il trouve.
        self.metadata_pattern = re.compile(r"([a-z_]+)=([a-zA-Z_0-9]+)")

    def parse(self, raw_input: str) -> dict[str, Any]:
        """
        Main entry point to parse the raw map string.

        Args:
            raw_input (str): The complete, raw text content of the map file.

        Returns:
            dict[str, Any]: A structured dictionary containing 'nb_drones',
                a list of 'zones', and a list of 'connections'.
        """
        clean_lines = self._clean_lines(raw_input)
        return self._get_raw_dict(clean_lines)

    @staticmethod
    def _clean_lines(raw_text: str) -> list[str]:
        """
        Removes comments and empty lines from the raw text.

        Args:
            raw_text (str): The raw text content.

        Returns:
            list[str]: A list of valid strings stripped of whitespace
            and comments.
        """
        raw_lines = raw_text.split("\n")
        clean_lines = []
        for line in raw_lines:
            clean_line = line.split("#")[0].strip()
            if clean_line:
                clean_lines.append(clean_line)
        return clean_lines

    def _get_raw_dict(self, clean_lines: list[str]) -> dict[str, Any]:
        """
        Analyzes valid lines to build the master dictionary structure.

        Iterates through the cleaned lines, matches them against the expected
        syntax patterns for map definitions, and extracts metadata.

        Args:
            clean_lines (list[str]): The cleaned lines to process.

        Returns:
            dict[str, Any]: The fully populated dictionary representation
            of the map.

        Raises:
            ValueError: If the file is empty, misses the 'nb_drones' header,
                contains syntax errors, or includes forbidden metadata keys.
        """
        raw_dict = {
            "nb_drones": 0,
            "zones": [],
            "connections": []
        }
        if not clean_lines:
            raise ValueError("The map file is empty.")

        first_line = clean_lines[0]
        if not first_line.startswith("nb_drones:"):
            raise ValueError(
                "The first line must define the number of drones "
                "using nb_drones: <positive_integer>"
            )

        raw_dict: dict[str, Any] = {
            "nb_drones": first_line.split(":")[1].strip(),
            "zones": [],
            "connections": []
        }

        for clean_line in clean_lines[1:]:
            if clean_line.startswith("connection:"):
                connection_dict = self._parse_connection(clean_line)
                raw_dict["connections"].append(connection_dict)

            elif clean_line.startswith(("hub:", "start_hub:", "end_hub:")):
                zone_dict = self._parse_zone(clean_line)
                raw_dict["zones"].append(zone_dict)

            else:
                raise ValueError(
                    f"Invalid key on line '{clean_line}'. Authorized keys are "
                    "'start_hub:', 'hub:', 'end_hub:', 'connection:'"
                )

        return raw_dict

    def _parse_connection(self, line: str) -> dict[str, Any]:
        """
        Parses a single line representing a connection
        and extracts its attributes.

        Args:
            line (str): The raw string line starting with 'connection:'.

        Returns:
            dict[str, Any]: A dictionary containing 'zone1', 'zone2', and
                'max_link_capacity' (defaulting to 1 if not specified).

        Raises:
            ValueError: If the connection syntax is invalid,
            if the max_link_capacity is empty or invalid,
            or if forbidden metadata keys are present.
        """
        match = self.connection_pattern.match(line)
        if match is None:
            raise ValueError(
                f"Syntax error: Invalid connection entry '{line}'. "
                "Usage = connection: <name1>-<name2> [metadata]. "
                "Dashes forbidden in names."
            )

        name1, name2, raw_metadata = match.groups()
        connection_dict = {
            "zone1": name1,
            "zone2": name2,
            "max_link_capacity": 1
        }

        if raw_metadata:
            if "max_link_capacity" in raw_metadata:
                max_cap = raw_metadata.split("=")[1].strip()
                if not max_cap:
                    raise ValueError("Invalid value for max_link_capacity.")
                connection_dict["max_link_capacity"] = max_cap
            else:
                raise ValueError(
                    "Forbidden key in connection metadata. "
                    "Authorized key: 'max_link_capacity'"
                )

        return connection_dict

    def _parse_zone(self, line: str) -> dict[str, Any]:
        """
        Parses a single line representing a zone and extracts its coordinates
        and metadata.

        Args:
            line (str): The raw string line starting with 'hub:', 'start_hub:',
                or 'end_hub:'.

        Returns:
            dict[str, Any]:A dictionary containing the zone's 'name', 'x' and
            'y' coordinates, 'is_start' and 'is_end' boolean flags, along with
            any authorized metadata (e.g., 'color', 'max_drones', 'zone').

        Raises:
            ValueError: If the zone syntax is invalid, or if forbidden metadata
                keys are included in the definition.
        """
        match = self.hub_pattern.match(line)
        if not match:
            raise ValueError(
                f"Syntax error: Invalid hub entry '{line}'. "
                "Usage = hub: <name> <x> <y> [metadata]. "
                "Dashes forbidden in name."
            )

        hub_type, name, x, y, raw_metadata = match.groups()
        zone_dict = {
            "name": name,
            "x": x,
            "y": y,
            "is_start": hub_type == "start_hub",
            "is_end": hub_type == "end_hub"
        }

        if raw_metadata:
            metadata_list = self.metadata_pattern.findall(raw_metadata)
            authorized_metadata = ["color", "max_drones", "zone"]
            for key, value in metadata_list:
                if key in authorized_metadata:
                    zone_dict[key] = value
                else:
                    raise ValueError(
                        f"Forbidden metadata key '{key}' in zone.")

        return zone_dict
