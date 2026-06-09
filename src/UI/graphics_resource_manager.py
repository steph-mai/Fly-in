"""Management of sprites, textures, and pre-compiled text objects."""

import arcade
from typing import Optional
from src.engine.simulation import Simulation
from src.UI.coordinate_mapper import CoordinateMapper


class GraphicsResourceManager:
    """Handles loading, caching, and initialization of all graphical assets.

    Attributes:
        mapper (CoordinateMapper): Coordinate transformation engine.
        background_list (Optional[arcade.SpriteList]): Background sprites.
        icon_list (arcade.SpriteList): Zone icon sprites.
        drone_list (arcade.SpriteList): Drone sprites.
        map_labels (dict): Pre-compiled zone name labels.
        link_labels (dict): Pre-compiled connection labels.
    """

    def __init__(self, sim: Simulation, mapper: CoordinateMapper) -> None:
        self.sim = sim
        self.mapper = mapper

        self.background_list: Optional[arcade.SpriteList] = None
        self.icon_list: arcade.SpriteList = arcade.SpriteList()
        self.drone_list: arcade.SpriteList = arcade.SpriteList()
        self.map_labels: dict[str, arcade.Text] = {}
        self.link_labels: dict[tuple[str, str], arcade.Text] = {}

        self._init_background(0, 0)
        self._init_labels()
        self._init_sprites()

    def _init_background(self, width: int, height: int) -> None:
        """Load and scale the ocean background sprite."""
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
            print(f"Warning: Unable to load ocean background ({e}).")

    def _init_labels(self) -> None:
        """Pre-generate optimized arcade.Text objects for labels."""
        for zone_name, zone_obj in self.sim.map_graph.zones.items():
            screen_x, screen_y = self.mapper.get_screen_coords(
                zone_obj.x, zone_obj.y)

            radius = self.mapper.get_zone_radius(zone_name)
            text_margin = radius + 1

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
                font_size=self.mapper.dynamic_font,
                anchor_x="center",
                anchor_y=vertical_anchor,
                multiline=True,
                width=self.mapper.dynamic_text_width,
                align="center"
            )
            self.map_labels[zone_name] = text_obj

        displayed_links = set()
        for zone_name in self.sim.map_graph.graph_adj:
            neighbors = self.sim.map_graph.get_neighbors(zone_name)
            zone_from = self.sim.map_graph.zones[zone_name]

            for neighbor_name in neighbors:
                duo_zones = tuple(sorted([zone_name, neighbor_name]))

                if duo_zones not in displayed_links:
                    zone_to = self.sim.map_graph.zones[neighbor_name]
                    start_x, start_y = self.mapper.get_screen_coords(
                        zone_from.x, zone_from.y)
                    end_x, end_y = self.mapper.get_screen_coords(
                        zone_to.x, zone_to.y)

                    mid_x = (start_x + end_x) / 2
                    mid_y = (start_y + end_y) / 2

                    link_text_obj = arcade.Text(
                        text="",
                        x=mid_x,
                        y=mid_y + 15,
                        color=arcade.color.BLACK,
                        font_size=10,
                        anchor_x="center",
                        anchor_y="center"
                    )
                    self.link_labels[duo_zones] = link_text_obj
                    displayed_links.add(duo_zones)

    def _init_sprites(self) -> None:
        """Load all interactive sprites (island icons and drone drones)."""
        try:
            tex_skull = arcade.load_texture("assets/skull.png")
            tex_rock = arcade.load_texture("assets/reef.png")
            tex_treasure = arcade.load_texture("assets/treasure.png")
            tex_palm = arcade.load_texture("assets/palm.png")

            for zone_name, zone_obj in self.sim.map_graph.zones.items():
                screen_x, screen_y = self.mapper.get_screen_coords(
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
                    scale_multiplier = (
                        1.1 if icon.texture in [tex_palm, tex_rock] else 1.4)
                    icon.scale = (
                        self.mapper.base_radius * scale_multiplier) / icon.width
                    self.icon_list.append(icon)

        except Exception as e:
            print(f"Warning: Missing icon sprites in assets/ ({e})")

        try:
            tex_drone = arcade.load_texture("assets/ship.png")

            for drone in self.sim.drones:
                drone_sprite = arcade.Sprite(tex_drone)

                distinct_colors = [
                    arcade.color.BLANCHED_ALMOND,
                    arcade.color.BRILLIANT_LAVENDER,
                    arcade.color.FLAVESCENT,
                    arcade.color.GLITTER,
                    arcade.color.GRANNY_SMITH_APPLE,
                    arcade.color.LIGHT_SALMON
                ]

                start_zone = self.sim.map_graph.zones[drone.current_zone]
                screen_x, screen_y = self.mapper.get_screen_coords(
                    start_zone.x, start_zone.y)
                drone_sprite.center_x = screen_x
                drone_sprite.center_y = screen_y

                target_width = max(30, self.mapper.base_radius * 4)
                drone_sprite.scale = target_width / drone_sprite.width

                drone_sprite.color = distinct_colors[drone.id % len(
                    distinct_colors)]
                drone_sprite.drone_ref = drone

                self.drone_list.append(drone_sprite)

        except Exception as e:
            print(f"Warning: Missing drone sprite in assets/ ({e})")
