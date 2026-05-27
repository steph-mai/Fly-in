# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  fly_in.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: stmaire <stmaire@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/05/21 14:06:26 by stmaire         #+#    #+#               #
#  Updated: 2026/05/27 13:54:52 by stmaire         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys
from pydantic import ValidationError
from loader import Loader
from parser import MapParser
from models import MapConfigModel
from map_graph import MapGraph
from simulation import Simulation


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 fly_in.py <maps/map_file>")
        sys.exit(1)

    map_file = sys.argv[1]

    loader = Loader()
    parser = MapParser()

    try:
        raw_input = loader.load_file(map_file)
        raw_dict = parser.parse(raw_input)
        valid_map = MapConfigModel(**raw_dict)
        print(f"Valid Map\n"
              f"{valid_map}")
        graph_adj = MapGraph(valid_map)
        for zone in valid_map.zones:
            print(f"{zone.name} neighbours:\n {graph_adj.get_neighbours(
                zone.name)}")
            infos = graph_adj.get_zone_infos(zone.name)
            if infos is not None:
                print(f"{zone.name} infos:\n x = {infos.x}")
        simulation = Simulation(valid_map)
        simulation.display_status()

    except (FileNotFoundError, IsADirectoryError) as e:
        print(f"\033[91m[FILE ERROR]\033[0m {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"\033[91m[PERMISSION ERROR]\033[0m {e}")
        sys.exit(1)
    except ValidationError as e:
        error = e.errors()[0]
        raw_message = error["msg"]
        clean_message = raw_message.replace("Value error,", "")
        print(f"\033[91m[VALUE ERROR]\033[0m {clean_message}")
        sys.exit(1)
    except ValueError as e:
        print(f"\033[91m[VALUE ERROR]\033[0m {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\033[91m[ERROR]\033[0m {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
