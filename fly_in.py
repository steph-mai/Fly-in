# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  fly_in.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: stephanie <stephanie@student.42.fr>       +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/05/21 14:06:26 by stmaire         #+#    #+#               #
#  Updated: 2026/06/04 09:51:09 by stephanie       ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import arcade
import sys
import traceback
from src.menu_view import MenuView

def main() -> None:
    print("--- DÉMARRAGE DU PROGRAMME ---")
    print("Veuillez sélectionner une carte dans la fenêtre Arcade...")

    try:
        # On ouvre la fenêtre une seule fois pour tout le jeu
        window = arcade.Window(1280, 720, "Fly-in Simulation")

        # On instancie et on affiche le menu principal
        start_view = MenuView()
        window.show_view(start_view)

        # On donne le contrôle total à Arcade
        arcade.run()

        print("\n--- FERMETURE DU PROGRAMME ---")

    except Exception as e:
        print(f"\033[91m[FATAL ERROR]\033[0m {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
