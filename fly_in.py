# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  fly_in.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: stmaire <stmaire@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/05/21 14:06:26 by stmaire         #+#    #+#               #
#  Updated: 2026/06/02 17:28:59 by stmaire         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import arcade
import sys
from src.menu_view import MenuView


def main() -> None:
    try:
        print("Launching graphical map viewer...")
        window = arcade.Window(1280, 720, "Fly-in Simulation")
        start_view = MenuView()
        window.show_view(start_view)

        arcade.run()

    except Exception as e:
        print(f"\033[91m[ERROR]\033[0m {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
