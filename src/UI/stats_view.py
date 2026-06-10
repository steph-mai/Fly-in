# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  stats_view.py                                     :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: stmaire <stmaire@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/06/10 15:41:23 by stmaire         #+#    #+#               #
#  Updated: 2026/06/10 17:28:04 by stmaire         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
import arcade
import arcade.gui
from src.engine.simulation import SimulationStats


class StatsView(arcade.View):
    """View displaying simulation statistics.

    Attributes:
        stats (SimulationStats): Statistics produced by the simulation.
        nb_drones (int): Total number of drones (used for averages).
        manager (arcade.gui.UIManager): UI manager for interactive widgets.
        v_box (arcade.gui.UIBoxLayout): Vertical layout for menu button.
        title_text (arcade.Text): Precomputed title text object.
        subtitle_text (arcade.Text): Precomputed subtitle text object.
        stats_text_obj (arcade.Text): Precomputed statistics text object.
    """

    def __init__(self, stats: SimulationStats, nb_drones: int):
        """Initialize the stats view.

        Args:
            stats (SimulationStats): Object containing aggregated simulation
            metrics.
            nb_drones (int): Total number of drones (used to compute averages).
        """
        super().__init__()
        self.stats = stats
        self.nb_drones = max(1, nb_drones)

        total_moves = sum(self.stats.moves_per_turn)
        self.avg_moves_per_turn = total_moves / max(1, self.stats.total_turns)

        total_active_turns = sum(self.stats.active_turns_per_drone.values())
        self.avg_turns_per_drone = total_active_turns / self.nb_drones

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.v_box = arcade.gui.UIBoxLayout()
        menu_button = arcade.gui.UIFlatButton(text="<- RETURN", width=150)
        self.v_box.add(menu_button)

        @menu_button.event("on_click")
        def on_click_menu(event: arcade.gui.UIEvent) -> None:
            self.manager.disable()

            print("\033[H\033[2J", end="")
            print("========================================")
            print("               MAIN MENU                ")
            print("========================================\n")

            from src.UI.menu_view import MenuView
            self.window.show_view(MenuView())

        anchor_layout = arcade.gui.UIAnchorLayout()

        anchor_layout.add(
            child=self.v_box,
            anchor_x="left",
            anchor_y="top",
            align_x=20,
            align_y=-20
        )
        self.manager.add(anchor_layout)

    def on_show_view(self) -> None:
        """Called when the view is shown.

        Precompute arcade.Text objects used for rendering static UI elements.
        """
        arcade.set_background_color(arcade.color.CATALINA_BLUE)

        center_x = self.window.width / 2
        start_y = self.window.height - 120

        self.title_text = arcade.Text(
            text="MISSION REPORT",
            x=center_x,
            y=start_y,
            color=arcade.color.CARIBBEAN_GREEN,
            font_size=40,
            anchor_x="center",
            bold=True
        )

        self.subtitle_text = arcade.Text(
            text="Simulation completed successfully.",
            x=center_x,
            y=start_y - 60,
            color=arcade.color.LIGHT_GRAY,
            font_size=18,
            anchor_x="center"
        )

        stats_string = (
            f"Final score (total number of turns): "
            f"{self.stats.total_turns}\n\n"
            f"Number of drones : {self.nb_drones}\n"
            f"Total path cost : {self.stats.total_path_cost}\n\n"
            f"Number of drones moved per turn : "
            f"{self.avg_moves_per_turn:.2f}\n"
            f"Average number of turns per drone : "
            f"{self.avg_turns_per_drone:.2f}"
        )

        self.stats_text_obj = arcade.Text(
            text=stats_string,
            x=center_x,
            y=start_y - 200,
            color=arcade.color.CELESTE,
            font_size=22,
            anchor_x="center",
            align="center",
            multiline=True,
            width=600
        )

    def on_draw(self) -> None:
        """Draw the view contents.

        This method is called at the window's draw rate (typically 60 FPS).
        """
        self.clear()

        self.title_text.draw()
        self.subtitle_text.draw()
        self.stats_text_obj.draw()

        self.manager.draw()
