"""
Factory module to build a Simulation instance from a map file.
Handles the entire data pipeline and formats specific error messages.
"""

from pathlib import Path
from pydantic import ValidationError
from src.parser import MapSyntaxError
from src.loader import Loader
from src.parser import MapParser
from src.models import MapConfigModel
from src.simulation import Simulation


class SimulationFactory:
    """Factory class to safely instantiate a Simulation."""

    @staticmethod
    def build_from_file(map_path: Path) -> tuple[Simulation | None, str | None]:
        """
        Attempts to load a map and build a Simulation.

        Returns:
            A tuple (Simulation, None) if successful.
            A tuple (None, error_message) if it fails.
        """
        try:
            loader = Loader()
            parser = MapParser()

            raw_input = loader.load_file(str(map_path))
            raw_dict = parser.parse(raw_input)

            valid_map = MapConfigModel(**raw_dict)

            sim = Simulation(valid_map)
            return sim, None

        except MapSyntaxError as e:
            return None, f"\033[91m[SYNTAX ERROR]\033[0m {e}"
        except ValidationError as e:
            error = e.errors()[0]
            raw_message = error["msg"]
            clean_message = raw_message.replace("Value error,", "")
            return None, f"\033[91m[VALIDATION ERROR]\033[0m {clean_message}"
        except ValueError as e:
            return None, f"\033[91m[VALUE ERROR]\033[0m {e}"
        except Exception as e:
            return None, f"\033[91m[ERROR]\033[0m {e}"
