"""
Map view module for the Fly-In simulation.

Acts as the controller between the simulation data, the UI elements,
and the rendering engine.
"""

from pathlib import Path
import arcade
import arcade.gui
from src.loader import Loader
from src.parser import MapParser
from src.models import MapConfigModel
from src.simulation import Simulation
from src.map_visualizer import MapVisualizer


class MapController(arcade.View):
    """
    View handling the map simulation display and user interface.

    Attributes:
        map_file_path (Path): The path to the selected map configuration file.
        sim (Simulation): The active simulation instance.
        visualizer (MapVisualizer): The rendering engine for the map visuals.
        manager (arcade.gui.UIManager): The UI manager for interactive buttons.
    """

    def __init__(self, map_file_path: Path) -> None:
        """
        Initialize the map view, load the simulation, and configure the window.
        """
        super().__init__()
        self.map_file_path = map_file_path

        loader = Loader()
        parser = MapParser()
        raw_input = loader.load_file(str(self.map_file_path))
        raw_dict = parser.parse(raw_input)
        valid_map = MapConfigModel(**raw_dict)

        self.sim = Simulation(valid_map)
        self.sim.display_status()

        x_coords = [zone.x for zone in self.sim.map_graph.zones.values()]
        y_coords = [zone.y for zone in self.sim.map_graph.zones.values()]

        map_width_units = (
            max(
                x_coords) if x_coords else 1) - (
                    min(x_coords) if x_coords else 0)
        map_height_units = (
            max(y_coords) if y_coords else 1) - (
                min(y_coords) if y_coords else 0)

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

    def _setup_ui(self) -> None:
        """Create and anchor the UI elements, including the return button."""
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
        def on_click(
            event: arcade.gui.UIEvent
        ) -> None:
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
        self.window.show_view(MenuView())

    def on_draw(self) -> None:
        """Render the map graphics and the UI overlay at 60 FPS."""
        self.clear()

        self.visualizer.draw_everything()

        self.manager.draw()
