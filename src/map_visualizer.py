"""
Map rendering module for the Fly-In simulation.

Handles all visual mathematics, coordinate mapping, and drawing operations
for the simulation map.
"""

import arcade
from src.simulation import Simulation
from typing import Optional


class MapVisualizer:
    """
    Engine responsible for rendering the map, routes, zones, and sprites.

    Attributes:
        sim (Simulation): The active simulation data to render.
        scale_x (float): Horizontal scaling factor.
        scale_y (float): Vertical scaling factor.
        offset_x (float): Horizontal camera offset for centering.
        offset_y (float): Vertical camera offset for centering.
    """

    def __init__(
            self,
            simulation: Simulation,
            window_width: int,
            window_height: int) -> None:
        """
        Initialize the rendering engine and pre-calculate all visual assets.

        Args:
            simulation (Simulation): The active simulation data model.
            window_width (int): The current physical width of the application
            window.
            window_height (int): The current physical height of the
            application window.
        """
        self.sim = simulation

        self.base_radius = 0
        self.dynamic_font = 0
        self.dynamic_text_width = 0

        self.background_list: Optional[arcade.SpriteList[arcade.Sprite]] = None
        self.icon_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
        self.ship_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
        self.map_labels: dict[str, arcade.Text] = {}

        self._calculate_scales(window_width, window_height)
        self._init_background(window_width, window_height)
        self._init_labels()
        self._init_sprites()

    def _calculate_scales(self, width: int, height: int) -> None:
        """
        Calculate drawing scales, offsets, and dynamic element sizes.

        Args:
            width (int): The width of the physical screen area.
            height (int): The height of the physical screen area.
        """
        x_coords = [zone.x for zone in self.sim.map_graph.zones.values()]
        y_coords = [zone.y for zone in self.sim.map_graph.zones.values()]

        min_x = min(x_coords) if x_coords else 0
        max_x = max(x_coords) if x_coords else 1
        min_y = min(y_coords) if y_coords else 0
        max_y = max(y_coords) if y_coords else 1

        map_width_units = max(1, max_x - min_x)
        map_height_units = max(1, max_y - min_y)

        padding_x = 100
        padding_y = 100

        self.scale_x = (width - (padding_x * 2)) / map_width_units
        self.scale_y = (height - (padding_y * 2)) / map_height_units

        map_center_x = (min_x + max_x) / 2
        map_center_y = (min_y + max_y) / 2

        self.offset_x = (width / 2) - (map_center_x * self.scale_x)
        self.offset_y = (height / 2) - (map_center_y * self.scale_y)

        self.base_radius = max(8, min(
            25, int(min(self.scale_x, self.scale_y) / 4)))
        self.dynamic_font = max(7, min(12, int(self.scale_x / 8)))
        self.dynamic_text_width = max(45, int(self.scale_x * 0.9))

    def _init_background(self, width: int, height: int) -> None:
        """
        Load and scale the ocean background sprite.

        Args:
            width (int): The target width to scale the background image.
            height (int): The target height to scale the background image.
        """
        try:
            bg_sprite = arcade.Sprite("assets/ocean.jpg")
            bg_sprite.center_x = width / 2
            bg_sprite.center_y = height / 2
            bg_sprite.width = width
            bg_sprite.height = height
            bg_sprite.alpha = 70

            self.background_list = arcade.SpriteList()
            self.background_list.append(bg_sprite)
        except Exception as e:
            print(f"Warning: Unable to load the ocean background ({e}).")

    def _init_labels(self) -> None:
        """Pre-generate optimized arcade.Text objects for map labels."""
        for zone_name, zone_obj in self.sim.map_graph.zones.items():
            screen_x, screen_y = self.get_screen_coords(zone_obj.x, zone_obj.y)

            if zone_obj.is_start or zone_obj.is_end:
                radius = self.base_radius
                # les zones de start et de end dont les plus grosses
            elif zone_obj.zone == "blocked" or "dead" in zone_name:
                radius = int(self.base_radius * 0.7)
                # on diminue le rayon des iles bloquees
                # int force car arcade ne gere pas les demi-pixels
            else:
                # iles standard un peu + grandes
                radius = int(self.base_radius * 0.8)

            text_margin = radius + 6
            if int(zone_obj.x) % 2 == 0:
                text_y = screen_y + text_margin
                vertical_anchor = "bottom"
            else:
                text_y = screen_y - text_margin
                vertical_anchor = "top"

            text_obj = arcade.Text(
                text="",
                x=screen_x,
                y=text_y,
                color=arcade.color.DARK_SLATE_GRAY,
                font_size=self.dynamic_font,
                anchor_x="center",
                anchor_y=vertical_anchor,
                multiline=True,
                width=self.dynamic_text_width,
                align="center"
            )
            self.map_labels[zone_name] = text_obj

    def _init_sprites(self) -> None:
        """Load all interactive sprites (islands, icons, ships)."""
        try:
            tex_skull = arcade.load_texture("assets/skull.png")
            tex_rock = arcade.load_texture("assets/reef.png")
            tex_treasure = arcade.load_texture("assets/treasure.png")
            tex_palm = arcade.load_texture("assets/palm.png")

            for zone_name, zone_obj in self.sim.map_graph.zones.items():
                screen_x, screen_y = self.get_screen_coords(
                    zone_obj.x, zone_obj.y)
                icon = None

                if zone_obj.is_end:
                    icon = arcade.Sprite(tex_treasure)
                elif zone_obj.zone == "blocked" or "dead" in zone_name:
                    icon = arcade.Sprite(tex_skull)
                    icon.color = arcade.color.DIM_GRAY
                elif zone_obj.zone == "restricted":
                    icon = arcade.Sprite(tex_rock)
                elif not zone_obj.is_start:
                    icon = arcade.Sprite(tex_palm)

                if icon:
                    icon.center_x = screen_x
                    icon.center_y = screen_y
                    scale_multiplier = 1.1 if icon.texture == tex_palm else 1.4
                    icon.scale = (
                        self.base_radius * scale_multiplier) / icon.width
                    self.icon_list.append(icon)

        except Exception as e:
            print(f"Warning: Missing icon sprites in assets/ ({e})")

        try:
            tex_ship = arcade.load_texture("assets/ship.png")
            for zone_name, zone_obj in self.sim.map_graph.zones.items():
                if zone_obj.is_start:
                    screen_x, screen_y = self.get_screen_coords(
                        zone_obj.x, zone_obj.y)
                    ship = arcade.Sprite(tex_ship)
                    ship.center_x = screen_x
                    ship.center_y = screen_y
                    target_width = max(55, self.base_radius * 6)
                    ship.scale = target_width / ship.width
                    self.ship_list.append(ship)
                    break
        except Exception as e:
            print(f"Warning: Missing ship sprite in assets/ ({e})")

    def get_screen_coords(
            self, zone_x: float, zone_y: float) -> tuple[float, float]:
        """
        Convert logical map coordinates to physical screen pixels.

        Args:
            zone_x (float): The abstract X coordinate from the map graph.
            zone_y (float): The abstract Y coordinate from the map graph.

        Returns:
            tuple[float, float]: A tuple containing the physical (x, y)
            pixel coordinates.
        """
        screen_x = zone_x * self.scale_x + self.offset_x
        screen_y = zone_y * self.scale_y + self.offset_y
        return screen_x, screen_y

    def draw_everything(self) -> None:
        """Execute the full rendering pipeline for the map."""

        if self.background_list:
            self.background_list.draw()

        # on cree un set pour eviter de tracer les routes deux fois, ce qui
        # fait ramer la carte graphique
        displayed_links = set()
        for zone_name in self.sim.map_graph.graph_adj:
            neighbors = self.sim.map_graph.get_neighbours(zone_name)
            zone_from = self.sim.map_graph.zones[zone_name]

            for neighbor_name in neighbors:
                duo_zones = tuple(sorted([zone_name, neighbor_name]))
                if duo_zones not in displayed_links:
                    zone_to = self.sim.map_graph.zones[neighbor_name]
                    start_x, start_y = self.get_screen_coords(
                        zone_from.x, zone_from.y)
                    end_x, end_y = self.get_screen_coords(
                        zone_to.x, zone_to.y)

                    arcade.draw_line(
                        start_x, start_y, end_x, end_y,
                        arcade.color.STEEL_BLUE, line_width=3
                    )
                    displayed_links.add(duo_zones)

        for zone_name, zone_obj in self.sim.map_graph.zones.items():
            screen_x, screen_y = self.get_screen_coords(zone_obj.x, zone_obj.y)

            if zone_obj.is_start:
                color = arcade.color.LAVENDER_PINK
                radius = self.base_radius
            elif zone_obj.is_end:
                color = arcade.color.GREEN_YELLOW
                radius = self.base_radius
            elif zone_obj.zone == "blocked" or "dead" in zone_name:
                color = arcade.color.LIGHT_SLATE_GRAY
                radius = int(self.base_radius * 0.7)
            elif zone_obj.zone == "restricted":
                color = arcade.color.CADET_GREY
                radius = int(self.base_radius * 0.8)
            elif zone_obj.zone == "priority":
                color = arcade.color.AQUAMARINE
                radius = int(self.base_radius * 0.8)
            else:
                color = arcade.color.WHEAT
                radius = int(self.base_radius * 0.8)

            arcade.draw_circle_filled(screen_x, screen_y, radius, color)
            arcade.draw_circle_outline(
                screen_x, screen_y, radius, arcade.color.DIM_GRAY, 2)

            current_ships = self.sim.hub_occupancy[zone_name]
            display_name = zone_name.replace('_', '\n')

            if "dead" in zone_name or zone_obj.zone == "blocked":
                label_text = f"{display_name}"
            else:
                label_text = f"{display_name}\n({current_ships}s)"

            text_obj = self.map_labels[zone_name]
            text_obj.text = label_text
            text_obj.draw()

        self.icon_list.draw()

        self.ship_list.draw()
