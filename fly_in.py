# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  fly_in.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: stmaire <stmaire@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/05/21 14:06:26 by stmaire         #+#    #+#               #
#  Updated: 2026/05/26 15:01:35 by stmaire         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys
from pydantic import ValidationError
from loader import Loader
from parser import MapParser
from models import MapConfigModel


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
        print(f"Parsed dict\n "
              f"{raw_dict}\n")
        valid_map = MapConfigModel(**raw_dict)
        print(f"Valid Map\n"
              f"{valid_map}")

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
