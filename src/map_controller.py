"""
Map view module for the Fly-In simulation.

Acts as the controller between the simulation data, the UI elements,
and the rendering engine.
"""

import arcade
import arcade.gui
from src.simulation import Simulation
from src.map_visualizer import MapVisualizer
import math


class MapController(arcade.View):
    """
    View handling the map simulation display and user interface.

    Attributes:
        sim (Simulation): The active simulation instance.
        visualizer (MapVisualizer): The rendering engine for the map visuals.
        manager (arcade.gui.UIManager): The UI manager for interactive buttons.
    """

    def __init__(self, sim: Simulation) -> None:
        """
        Initialize the map view with a pre-loaded simulation and configure the window.
        """
        super().__init__()

        # 1. On reçoit la simulation déjà chargée et validée !
        self.sim = sim

        # 2. Le reste de ta logique de calcul de taille d'écran ne change pas
        x_coords = [zone.x for zone in self.sim.map_graph.zones.values()]
        y_coords = [zone.y for zone in self.sim.map_graph.zones.values()]

        map_width_units = (
            max(x_coords) if x_coords else 1) - (min(x_coords) if x_coords else 0)
        map_height_units = (
            max(y_coords) if y_coords else 1) - (min(y_coords) if y_coords else 0)

        map_width_units = max(1, map_width_units)
        map_height_units = max(1, map_height_units)

        pixels_per_unit = 120
        target_width = int((map_width_units * pixels_per_unit) + 200)
        target_height = int((map_height_units * pixels_per_unit) + 200)

        MIN_WIDTH, MIN_HEIGHT = 800, 600
        MAX_WIDTH, MAX_HEIGHT = 1600, 950

        final_width = max(MIN_WIDTH, min(target_width, MAX_WIDTH))
        final_height = max(MIN_HEIGHT, min(target_height, MAX_HEIGHT))

        if self.window:
            self.window.set_size(final_width, final_height)
            self.window.center_window()

        arcade.set_background_color(arcade.color.CELESTE)

        self.visualizer = MapVisualizer(self.sim, final_width, final_height)

        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self._setup_ui()

        self.time_since_last_tick: float = 0.0
        self.tick_rate: float = 1.5

        self.score_text = arcade.Text(
            text="Turn: 1 | IN PROGRESS...",
            x=self.window.width // 2 - 100,  # 'x' au lieu de 'start_x'
            y=20,                            # 'y' au lieu de 'start_y'
            color=arcade.color.WHITE,
            font_size=16,
            bold=True
        )

    def _setup_ui(self) -> None:
        """Create and anchor the UI elements, including the return button."""
        self.anchor_layout = arcade.gui.UIAnchorLayout()

        button_style = {
            "normal": {"bg": arcade.color.COOL_GREY, "fg": arcade.color.BLACK},
            "hover": {"bg": arcade.color.CORNFLOWER_BLUE, "fg": arcade.color.WHITE},
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
        """Disable the UI and transition back to the main menu view."""
        self.manager.disable()

        # Local import to prevent circular dependency issues
        from src.menu_view import MenuView
        if self.window:
            self.window.show_view(MenuView())

    def on_draw(self) -> None:
        """Render the map graphics and the UI overlay at 60 FPS."""
        self.clear()
        self.visualizer.draw_everything()

        status_msg = "IN PROGRESS..." if self.sim.is_simulation_running() else "Simulation ended"

        nb_turns = self.sim.stats.total_turns

        # On actualise les données de l'objet
        self.score_text.text = f"Tour : {nb_turns} | {status_msg}"
        self.score_text.color = arcade.color.WHITE if self.sim.is_simulation_running() else arcade.color.GOLD

        # On le dessine
        self.score_text.draw()

        self.manager.draw()

    def on_update(self, delta_time: float) -> None:
        """
        Gère l'écoulement du temps et l'avancement de la simulation.
        Appelé environ 60 fois par seconde par Arcade.
        """
        self.time_since_last_tick += delta_time

        # Quand le chronomètre atteint la limite (ex: 0.6s)
        if self.time_since_last_tick >= self.tick_rate:

            # S'il reste des bateaux en jeu
            if self.sim.is_simulation_running():

                # --- 1. RÉCUPÉRATION DES MOUVEMENTS ---
                # On stocke ce que le moteur mathématique vient de calculer
                moves = self.sim.tick()

                # --- 2. AFFICHAGE SYNCHRONISÉ DANS LE TERMINAL ---
                # S'il y a eu au moins un mouvement ce tour-ci, on l'affiche
                if moves:
                    # Affichage au format strict demandé : "D1-roof1 D2-corridorA"
                    print(" ".join(moves))

                self.time_since_last_tick -= self.tick_rate
            else:
                # La simulation est finie, on fige la dernière image
                self.time_since_last_tick = self.tick_rate
                self.visualizer.update_ships_animation(1.0)
                return

        # 3. Calcul de l'interpolation (Lerp) pour l'animation à l'écran
        progress = self.time_since_last_tick / self.tick_rate
        progress = min(1.0, progress)
        self.visualizer.update_ships_animation(progress)
