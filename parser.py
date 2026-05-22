from pathlib import Path
from typing import Any
from loader import Loader
import re


class MapParser:
    def __init__(self):
        self.connection_pattern = re.compile(r"^\s*connection:\s*([^\s\-]+)-([^\s\-]+)(?:\s+\[(.*?)\])?\s*$")
        # ?) (avec le point d'interrogation) :
        #  moteur devient paresseux. Il va avancer caractère par caractère
        #  s'arrêter au tout premier crochet fermant qu'il trouve.
        self.metadata_pattern = re.compile(r"([a-z_]+)=([a-zA-Z_0-9]+)")

    def parse(self, raw_input: str) -> dict[str, Any]:
        clean_lines = self._clean_lines(raw_input)
        return self._get_raw_dict(clean_lines)

    @staticmethod
    def _clean_lines(raw_text: str) -> list[str]:
        raw_lines = raw_text.split("\n")
        clean_lines = []
        for line in raw_lines:
            clean_line = line.split("#")[0].strip()
            if clean_line:
                clean_lines.append(clean_line)
        return clean_lines

    def _get_raw_dict(self, clean_lines: list[str]) -> dict[str, Any]:
        raw_dict = {
            "nb_drones": 0,
            "zones": [],
            "connections": []
        }
        for clean_line in clean_lines:
            if clean_line.startswith("nb_drones"):
                raw_dict["nb_drones"] = clean_line.split(":")[1].strip()
            elif clean_line.startswith("connection"):
                match = re.match(self.connection_pattern, clean_line)
                if match is None:
                    raise ValueError("Syntax error: Invalid connection entry."
                                     "Usage = <name1>-<name2> [metadata]. "
                                     "Dashes forbidden")
                else:
                    name1, name2, metadata = match.groups()
                    connection_dict = {
                        "name1": name1,
                        "name2": name2,
                        "max_link_capacity": 1
                    }
                    raw_dict["connections"].append(connection_dict)
                    if metadata:
                        if "max_link_capacity" in metadata:
                            max_link_capacity_value = metadata.split("=")[1]
                            if not max_link_capacity_value:
                                raise ValueError(
                                    "Invalid value for max_link_capacity."
                                    "Usage = integer >= 1"
                                    )
                            connection_dict["max_link_capacity"] = (
                                max_link_capacity_value)
        return raw_dict






        return raw_dict








