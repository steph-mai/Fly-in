# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  fly_in.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: stmaire <stmaire@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/05/21 14:06:26 by stmaire         #+#    #+#               #
#  Updated: 2026/06/10 15:51:24 by stmaire         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import arcade
import sys
from src.UI.menu_view import MenuView
from src.parsing.errors import FlyInError


def main() -> None:
    print("--- STARTING THE PROGRAM ---")
    print("Please select a card in the Arcade window...")

    try:
        window = arcade.Window(1280, 720, "Fly-in Simulation")

        start_view = MenuView()
        window.show_view(start_view)

        arcade.run()

        print("\n--- PROGRAM CLOSING ---")

    except KeyboardInterrupt:
        print("\n\033[93m[INFO] User interrupt "
              "(Ctrl+C). Program closing...\033[0m", file=sys.stderr)

        if arcade.get_window():
            arcade.close_window()
        sys.exit(0)

    except FlyInError as e:
        print(f"\n\033[91m{e}\033[0m")
        if arcade.get_window():
            arcade.close_window()
        sys.exit(1)

    except Exception as e:
        print(f"\033[91m[FATAL ERROR]\033[0m {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
