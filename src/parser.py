# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  parser.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: stmaire <stmaire@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/05/26 17:40:40 by stmaire         #+#    #+#               #
#  Updated: 2026/06/03 10:01:48 by stmaire         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

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
        self.hub_pattern = re.compile(
            r"^\s*(start_hub|end_hub|hub):\s*"
            r"([^\s\-]+)\s+"
            r"(-?\d+)\s+"
            r"(-?\d+)"
            r"(?:\s+\[(.*?)\])?\s*$"
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
    def _clean_lines(raw_text: str) -> list[tuple[int, str]]:
        """
        Removes comments and empty lines, preserving original line numbers.

        Args:
            raw_text (str): The raw text content.

        Returns:
            list[tuple[int, str]]: A list of tuples containing the original
                1-indexed line number and the cleaned string.
        """
        raw_lines = raw_text.split("\n")
        clean_lines = []

        for line_num, line in enumerate(raw_lines, start=1):
            clean_line = line.split("#")[0].strip()
            if clean_line:
                clean_lines.append((line_num, clean_line))

        return clean_lines

    def _get_raw_dict(
            self, clean_lines: list[tuple[int, str]]) -> dict[str, Any]:
        """
        Analyzes valid lines to build the master dictionary structure.

        Args:
            clean_lines (list[tuple[int, str]]): The cleaned lines with their
                original line numbers.

        Returns:
            dict[str, Any]: The fully dictionary representation of the map.

        Raises:
            ValueError: If the file is empty or contains formatting errors.
        """
        if not clean_lines:
            raise ValueError("Line 1: The map file is empty.")

        first_line_num, first_line = clean_lines[0]

        if not first_line.startswith("nb_drones:"):
            raise ValueError(
                f"Line {first_line_num}: The first line must define the "
                "number of drones using nb_drones: <positive_integer>"
            )

        raw_dict: dict[str, Any] = {
            "nb_drones": first_line.split(":")[1].strip(),
            "zones": [],
            "connections": []
        }

        for line_num, clean_line in clean_lines[1:]:

            if clean_line.startswith("connection:"):
                connection_dict = self._parse_connection(clean_line, line_num)
                raw_dict["connections"].append(connection_dict)

            elif clean_line.startswith(("hub:", "start_hub:", "end_hub:")):
                zone_dict = self._parse_zone(clean_line, line_num)
                if zone_dict["is_start"] is True:
                    zone_dict['max_drones'] = raw_dict["nb_drones"]
                raw_dict["zones"].append(zone_dict)

            else:
                raise ValueError(
                    f"Line {line_num}: Invalid key in '{clean_line}'."
                    f"Authorized keys are "
                    f"'start_hub:', 'hub:', 'end_hub:', 'connection:'"
                )

        return raw_dict

    def _parse_connection(self, line: str, line_num: int) -> dict[str, Any]:
        """
        Parses a single line representing a connection and extracts
        its attributes.

        Args:
            line (str): The raw string line starting with 'connection:'.
            line_num (int): The original line number for error reporting.

        Returns:
            dict[str, Any]: A dictionary containing connection data.
        """
        match = self.connection_pattern.match(line)
        if match is None:
            raise ValueError(
                f"Line {line_num}: Syntax error in connection entry '{line}'. "
                "Usage = connection: <name1>-<name2> [metadata]. "
                "Dashes forbidden."
            )

        name1, name2, raw_metadata = match.groups()
        connection_dict = {
            "zone1": name1,
            "zone2": name2,
            "max_link_capacity": 1
        }

        if raw_metadata:
            supposed_metadata = raw_metadata.split()
            if len(supposed_metadata) > 1:
                raise ValueError(f"Line {line_num}: 'max_link_capacity' "
                                 f"is the only valid metadata key")

            connection_pattern = r"^(max_link_capacity)=([\d]+)"
            match_metadata = re.fullmatch(
                connection_pattern, supposed_metadata[0])
            if not match_metadata:
                raise ValueError(
                    f"Line {line_num}: Invalid metadata syntax. "
                    "Usage: 'max_link_capacity=integer'."
                )
            key, value = match_metadata.groups()
            connection_dict[key] = value

        connection_dict["line_num"] = line_num

        return connection_dict

    def _parse_zone(self, line: str, line_num: int) -> dict[str, Any]:
        """
        Parses a single line representing a zone and extracts its data.

        Args:
            line (str): The raw string line starting with a hub keyword.
            line_num (int): The original line number for error reporting.

        Returns:
            dict[str, Any]: A dictionary containing zone data.
        """
        match = self.hub_pattern.match(line)
        if not match:
            raise ValueError(
                f"Line {line_num}: Syntax error in hub entry '{line}'. "
                "Usage = hub: <name> <x> <y> [metadata]."
                "Dashes forbidden."
            )

        hub_type, name, x, y, raw_metadata = match.groups()
        zone_dict = {
            "name": name,
            "x": x,
            "y": y,
            "is_start": hub_type == "start_hub",
            "is_end": hub_type == "end_hub"
        }

        zone_dict['max_drones'] = 1

        if raw_metadata:
            raw__metadata_list = raw_metadata.split()
            authorized_metadata = ["color", "max_drones", "zone"]

            for supposed_metadata in raw__metadata_list:
                match_metadata = self.metadata_pattern.fullmatch(
                    supposed_metadata)
                if not match_metadata:
                    raise ValueError(f"Line {line_num}: Invalid metadata "
                                     F"syntax '{supposed_metadata}' "
                                     f"Usage: 'key=value'")
                key, value = match_metadata.groups()
                if key in authorized_metadata:
                    zone_dict[key] = value
                else:
                    raise ValueError(f"Line {line_num}: "
                                     f"Forbidden metadata key "
                                     f"'{key}'.")

            if "color" in zone_dict:
                clean_color = zone_dict["color"].strip().upper()
                if clean_color == "DARKRED":
                    clean_color = "DARK_RED"
                if clean_color == "RAINBOW":
                    clean_color = "LAVENDER"
                zone_dict["color"] = clean_color

        zone_dict["line_num"] = line_num

        return zone_dict
