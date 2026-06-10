# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  map_controller.py                                 :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: stmaire <stmaire@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/06/10 15:38:44 by stmaire         #+#    #+#               #
#  Updated: 2026/06/10 15:55:16 by stmaire         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
"""Map view module for the Fly-In simulation.

Acts as the controller between the simulation data, the UI elements,
and the rendering engine.
"""

import arcade
import arcade.gui
from src.engine.simulation import Simulation
from src.UI.map_visualizer import MapVisualizer


class MapController(arcade.View):
    """View handling the map simulation display and user interface.

    Attributes:
        sim (Simulation): The active simulation instance.
        visualizer (MapVisualizer): The rendering engine for the map visuals.
        manager (arcade.gui.UIManager): The UI manager for interactive buttons.
        elapsed_time_since_last_turn (float): Time elapsed since last turn
            processing (in seconds).
        turn_delay (float): Delay between consecutive turn processing
            (in seconds).
        end_screen_timer (float): Timer for displaying end screen before
            transitioning to stats view (in seconds).
        score_text (arcade.Text): Text object displaying current turn and
            simulation status.
    """

    def __init__(self, sim: Simulation) -> None:
        """Initialize the map view with a pre-loaded simulation.

        Configures the window size based on map dimensions, initializes the
        visualizer and UI manager, and sets up timing parameters for turn
        processing.

        Args:
            sim (Simulation): The active simulation instance to display.
        """
        super().__init__()
        self.sim = sim

        final_width, final_height = self._calculate_window_dimensions()
        if self.window:
            self.window.set_size(final_width, final_height)
            self.window.center_window()

        arcade.set_background_color(arcade.color.CELESTE)

        self.visualizer = MapVisualizer(self.sim, final_width, final_height)
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self._setup_ui()

        self.elapsed_time_since_last_turn: float = 0.0
        self.delay_between_two_turns: float = 1.5
        self.end_screen_timer: float = 0.0

        center_x = self.window.width / 2
        bottom_margin = 30
        self.score_text = arcade.Text(
            text="",
            x=center_x,
            y=bottom_margin,
            color=arcade.color.WHITE,
            font_size=16,
            bold=True,
            anchor_x="center",
            anchor_y="center"
        )

    def _calculate_window_dimensions(self) -> tuple[int, int]:
        """Calculate optimal window dimensions based on map size.

        Computes the required window size to display the map with a fixed
        pixel-to-unit scale, constrained between minimum and maximum limits.

        Returns:
            tuple[int, int]: Tuple of (width, height) in pixels.
        """
        x_coords = [zone.x for zone in self.sim.map_graph.zones.values()]
        y_coords = [zone.y for zone in self.sim.map_graph.zones.values()]

        map_width_units = (
            max(x_coords) if x_coords else 1
        ) - (min(x_coords) if x_coords else 0)
        map_height_units = (
            max(y_coords) if y_coords else 1
        ) - (min(y_coords) if y_coords else 0)

        map_width_units = max(1, map_width_units)
        map_height_units = max(1, map_height_units)

        pixels_per_unit = 120
        target_width = int((map_width_units * pixels_per_unit) + 200)
        target_height = int((map_height_units * pixels_per_unit) + 200)

        min_width, min_height = 800, 600
        max_width, max_height = 1600, 950

        final_width = max(min_width, min(target_width, max_width))
        final_height = max(min_height, min(target_height, max_height))

        return final_width, final_height

    def _setup_ui(self) -> None:
        """Create and anchor UI elements.

        Sets up the UI manager layout and adds the back button to return
        to the main menu.
        """
        self.anchor_layout = arcade.gui.UIAnchorLayout()

        button_style = {
            "normal": {"bg": arcade.color.COOL_GREY, "fg": arcade.color.BLACK},
            "hover": {
                "bg": arcade.color.CORNFLOWER_BLUE, "fg": arcade.color.WHITE},
            "press": {"bg": arcade.color.DARK_BLUE, "fg": arcade.color.WHITE}
        }

        back_button = arcade.gui.UIFlatButton(
            text="<- Menu", width=70, height=30, style=button_style)

        @back_button.event("on_click")
        def on_click(event: arcade.gui.UIEvent) -> None:
            self.go_back_to_menu()

        self.anchor_layout.add(
            child=back_button,
            anchor_x="left",
            anchor_y="top",
            align_x=5,
            align_y=-5)
        self.manager.add(self.anchor_layout)

    def go_back_to_menu(self) -> None:
        """Disable UI and transition back to the main menu view.

        Clears the terminal output, disables the UI manager, and displays
        the main menu view.
        """
        self.manager.disable()

        print("\033[H\033[2J", end="")

        print("========================================")
        print("             MAIN MENU             ")
        print("========================================")
        print("\nAwaiting card selection...\n")

        from src.UI.menu_view import MenuView
        if self.window:
            self.window.show_view(MenuView())

    def on_draw(self) -> None:
        """Render the map view and UI elements.

        Draws the map visualization, updates the status text based on
        simulation state, and renders UI components.
        """
        self.clear()
        self.visualizer.draw_everything()

        is_math_done = not self.sim.is_simulation_running()
        is_anim_done = (
            self.elapsed_time_since_last_turn >= self.delay_between_two_turns
        )
        is_visually_ended = is_math_done and is_anim_done

        nb_turns = self.sim.stats.total_turns

        if is_visually_ended:
            status_msg = "SIMULATION ENDED"
            self.score_text.color = arcade.color.UCLA_BLUE
        elif nb_turns == 0:
            status_msg = "START OF THE SIMULATION"
            self.score_text.color = arcade.color.WHITE
        else:
            status_msg = "SIMULATION RUNNING..."
            self.score_text.color = arcade.color.WHITE

        self.score_text.text = f"TURN : {nb_turns} | {status_msg}"

        self.score_text.draw()
        self.manager.draw()

    def on_update(self, time_since_last_image: float) -> None:
        """Update simulation state and animation progress.

        Processes turn updates at regular intervals (controlled by
        delay_between_two_turns)
        and updates drone animations based on elapsed time. Transitions to
        stats view when simulation ends.

        Args:
            time_since_last_image (float): Delta time since last frame
                (in seconds).
        """
        time_since_last_image = min(time_since_last_image, 0.1)
        self.elapsed_time_since_last_turn += time_since_last_image

        if self.elapsed_time_since_last_turn >= self.delay_between_two_turns:

            if self.sim.is_simulation_running():
                moves = self.sim.process_turn()
                if moves:
                    print(" ".join(moves))
                self.elapsed_time_since_last_turn -= (
                    self.delay_between_two_turns)

            else:
                self.elapsed_time_since_last_turn = (
                    self.delay_between_two_turns)
                self.visualizer.update_drones_animation(1.0)
                self.sim.connection_occupancy.clear()
                self.end_screen_timer += time_since_last_image
                if self.end_screen_timer >= 3:
                    self.manager.disable()

                    from src.UI.stats_view import StatsView
                    stats_view = StatsView(
                        self.sim.stats, self.sim.total_drones)
                    if self.window:
                        self.window.show_view(stats_view)
                return

        progress_rate = (
            self.elapsed_time_since_last_turn / self.delay_between_two_turns)
        progress_rate = min(1.0, progress_rate)
        self.visualizer.update_drones_animation(progress_rate)
