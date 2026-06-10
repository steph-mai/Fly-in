# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  menu_view.py                                      :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: stmaire <stmaire@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/06/10 15:40:09 by stmaire         #+#    #+#               #
#  Updated: 2026/06/10 15:41:06 by stmaire         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
"""
Menu view module for the Fly-In simulation.

Provides the graphical user interface for selecting map difficulties
and specific map files using the Arcade GUI system.
"""

from pathlib import Path
import arcade
import arcade.gui
from src.UI.map_controller import MapController
from src.parsing.simulation_factory import SimulationFactory
from typing import Optional, Any, cast
from src.parsing.errors import FlyInError
import sys


class MenuView(arcade.View):
    """
    Main menu view handling user navigation before starting the simulation.

    Attributes:
        background_list (arcade.SpriteList): Layer containing the background
        image.
        manager (arcade.gui.UIManager): The main UI event and widget handler.
        anchor_layout (arcade.gui.UIAnchorLayout): Global layout container for
        UI scaling.
        button_style (dict): Style dictionary defining colors for button
        states.
    """

    def __init__(self) -> None:
        """
        Initialize the menu view, set up the UI manager, and display the
        main menu.
        """
        super().__init__()

        self.background_list: Optional[arcade.SpriteList[arcade.Sprite]] = None

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.anchor_layout = arcade.gui.UIAnchorLayout()
        self.manager.add(self.anchor_layout)

        self.button_style = {
            "normal": {
                "bg": arcade.color.ANTIQUE_BRASS,
                "fg": arcade.color.BLACK,
            },
            "hover": {
                "bg": arcade.color.BRONZE,
                "fg": arcade.color.BLACK,
            },
            "press": {
                "bg": arcade.color.BROWN_NOSE,
                "fg": arcade.color.WHITE,
            }
        }
        self.show_main_menu()

    def on_show_view(self) -> None:
        """
        Handle logic when the view is switched to this menu.

        Loads the background image texture dynamically and fits it
        to the window bounds.
        """
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        if self.window:
            self.window.set_size(1280, 720)
            self.window.center_window()

        self.title_text = arcade.Text(
            text="Fly-In",
            x=80,
            y=self.window.height - 140,
            color=arcade.color.WHITE,
            font_size=80,
            anchor_x="left",
            bold=True,
            font_name=("Garamond", "Palatino", "serif")
        )

        try:
            bg_sprite = arcade.Sprite("assets/menu_background.jpeg")
            bg_sprite.center_x = self.window.width / 2
            bg_sprite.center_y = self.window.height / 2
            bg_sprite.width = self.window.width
            bg_sprite.height = self.window.height

            self.background_list = arcade.SpriteList()
            self.background_list.append(bg_sprite)
        except Exception as e:
            print(f"Warning: Unable to load the menu background ({e}).")
            self.background_list = None

    def show_main_menu(self) -> None:
        """
        Clear the current layout and populate it with difficulty selection
        buttons.
        """
        cast(Any, self.anchor_layout).clear()
        horizontal_box = arcade.gui.UIBoxLayout(
            vertical=False, space_between=20)
        difficulties = ["easy", "medium", "hard", "challenger"]

        for diff in difficulties:
            button = arcade.gui.UIFlatButton(
                text=diff.capitalize(),
                width=180,
                height=50,
                style=self.button_style)

            @button.event("on_click")
            def on_click_diff(
                event: arcade.gui.UIEvent,
                d: str = diff
            ) -> None:
                self.show_submenu(d)
            horizontal_box.add(button)

        self.anchor_layout.add(
            child=horizontal_box,
            anchor_x="center_x",
            anchor_y="bottom",
            align_y=60)

        exit_style = {
            "normal": {
                "bg": arcade.color.PERSIAN_PLUM, "fg": arcade.color.WHITE},
            "hover": {
                "bg": arcade.color.PERSIAN_RED, "fg": arcade.color.WHITE},
            "press": {
                "bg": arcade.color.PERSIAN_ORANGE, "fg": arcade.color.WHITE}
        }

        exit_button = arcade.gui.UIFlatButton(
            text="EXIT", width=150, height=45, style=exit_style
        )

        @exit_button.event("on_click")
        def on_click_quit(event: arcade.gui.UIEvent) -> None:
            import sys
            print(
                "\n\033[93m[INFO] End of game. Program closing...\033[0m",
                file=sys.stderr)
            arcade.close_window()
            sys.exit(0)
        self.anchor_layout.add(
            child=exit_button,
            anchor_x="right",
            anchor_y="top",
            align_x=-20,
            align_y=-20
        )

    def show_submenu(self, difficulty: str) -> None:
        """
        Scan the corresponding difficulty folder and list all available maps.

        Args:
            difficulty (str): The folder name to scan within the 'maps'
            directory.
        """
        cast(Any, self.anchor_layout).clear()
        h_box = arcade.gui.UIBoxLayout(vertical=False, space_between=15)

        map_dir = Path("maps") / difficulty
        map_files = [
            f for f in map_dir.iterdir() if not f.name.startswith(".")
            ] if map_dir.exists() else []

        if not map_files:
            label = arcade.gui.UILabel(
                text="No card found",
                font_size=16,
                text_color=arcade.color.WHITE)
            h_box.add(label)
        else:
            for map_path in sorted(map_files):
                button = arcade.gui.UIFlatButton(
                    text=map_path.stem,
                    width=180,
                    height=45,
                    style=self.button_style)

                @button.event("on_click")
                def on_click_map(
                    event: arcade.gui.UIEvent,
                    p: Path = map_path
                ) -> None:
                    self.start_simulation(p)

                h_box.add(button)

        back_style = {
            "normal": {"bg": (190, 40, 40), "fg": arcade.color.WHITE},
            "hover": {"bg": (255, 60, 60), "fg": arcade.color.WHITE},
            "press": {"bg": (100, 20, 20), "fg": arcade.color.WHITE}
        }

        back_button = arcade.gui.UIFlatButton(
            text="<- Return", width=150, height=45, style=back_style
        )

        @back_button.event("on_click")
        def on_click_back(event: arcade.gui.UIEvent) -> None:
            self.show_main_menu()

        h_box.add(back_button)

        self.anchor_layout.add(
            child=h_box, anchor_x="center_x", anchor_y="bottom", align_y=60)

    def start_simulation(self, map_path: Path) -> None:
        """
        Disable the UI manager components and transition to the map simulation
        view.

        Args:
            map_path (Path): The explicit path to the selected map file.
        """
        try:
            sim = SimulationFactory.build_from_file(map_path)
            print("\033[H\033[2J\n")

            self.manager.disable()
            simulation_view = MapController(sim=sim)

            if self.window:
                self.window.show_view(simulation_view)

        except FlyInError as e:
            print(f"\n\033[91m{e}\033[0m")
            self.manager.enable()
            self.show_main_menu()

        except Exception as e:
            print(f"\n\033[91m[CRITICAL ERROR]\033[0m An unexpected error "
                  f"has occurred.: {e}")
            if arcade.get_window():
                arcade.close_window()
            sys.exit(1)

    def on_draw(self) -> None:
        """Render the background sprite, the cinematic title, and all UI
        widgets."""
        self.clear()

        if self.background_list:
            self.background_list.draw()

        if hasattr(self, "title_text"):
            self.title_text.draw()

        self.manager.draw()
