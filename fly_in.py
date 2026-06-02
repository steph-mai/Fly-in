# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  fly_in.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: stmaire <stmaire@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/05/21 14:06:26 by stmaire         #+#    #+#               #
#  Updated: 2026/06/02 09:51:09 by stmaire         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import arcade
import sys
from src.menu_view import MenuView
from pydantic import ValidationError


def main() -> None:
    try:
        print("Launching graphical map viewer...")
        window = arcade.Window(1280, 720, "Fly-in Simulation")
        start_view = MenuView()
        window.show_view(start_view)

        # 3. On lance la boucle de jeu
        arcade.run()

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
