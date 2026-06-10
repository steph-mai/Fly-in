# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  simulation_factory.py                             :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: stmaire <stmaire@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/06/10 15:37:25 by stmaire         #+#    #+#               #
#  Updated: 2026/06/10 15:37:42 by stmaire         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
"""Module responsible for building the Simulation instance from map files."""

from pathlib import Path
from pydantic import ValidationError
from src.parsing.loader import Loader
from src.parsing.parser import MapParser
from src.parsing.models import MapConfigModel
from src.engine.simulation import Simulation
from src.parsing.errors import FlyInError, MapLogicalError, MapSyntaxError


class SimulationFactory:
    """Factory class to safely instantiate a Simulation."""

    @staticmethod
    def build_from_file(map_path: Path) -> Simulation:
        """
        Builds a Simulation instance from a specified map file.

        This method orchestrates the loading, parsing, and validation process.
        It converts technical system or validation errors into domain-specific
        FlyInError exceptions.

        Args:
            map_path: The file system path to the map configuration file.

        Returns:
            A fully initialized Simulation object.

        Raises:
            MapSyntaxError: If the file format is invalid.
            MapLogicalError: If the configuration violates business rules.
            FlyInError: For any other unexpected system or processing error.
        """
        try:
            loader = Loader()
            parser = MapParser()

            raw_input = loader.load_file(str(map_path))
            raw_dict = parser.parse(raw_input)

            valid_map = MapConfigModel(**raw_dict)

            sim = Simulation(valid_map)
            return sim

        except MapSyntaxError:
            raise
        except ValidationError as e:
            error = e.errors()[0]
            clean_message: str = str(
                error["msg"]).replace("Value error,", "").strip()
            raise MapLogicalError(clean_message)
        except ValueError as e:
            raise MapLogicalError(str(e))
        except Exception as e:
            raise FlyInError(f"Unexpected system error: {e}")
