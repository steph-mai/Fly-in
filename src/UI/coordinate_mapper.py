# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  coordinate_mapper.py                              :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: stmaire <stmaire@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/06/10 15:37:57 by stmaire         #+#    #+#               #
#  Updated: 2026/06/10 15:37:59 by stmaire         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
"""Coordinate mapping and geometric calculations for the map visualization.

Provides CoordinateMapper to convert logical map coordinates to screen pixels
and to compute dynamic drawing sizes used by the UI.
"""
from src.engine.simulation import Simulation


class CoordinateMapper:
    """Perform geometric calculations and coordinate transformations.

    Use this class to obtain screen coordinates, drawing radii
    and dynamic sizes.

    Attributes:
        sim (Simulation): The simulation data model.
        scale_x (float): Horizontal scaling factor.
        scale_y (float): Vertical scaling factor.
        offset_x (float): Horizontal camera offset.
        offset_y (float): Vertical camera offset.
        base_radius (int): Base radius for zone circles.
        dynamic_font (int): Font size for labels.
        dynamic_text_width (int): Text width for multi-line labels.
    """

    def __init__(self, simulation: Simulation, window_width: int,
                 window_height: int) -> None:
        """Initialize the mapper and compute initial scales.

        Args:
            simulation (Simulation): Simulation containing map_graph.
            window_width (int): Window width in pixels.
            window_height (int): Window height in pixels.
        """
        self.sim = simulation
        self.scale_x = 0.0
        self.scale_y = 0.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.base_radius = 0
        self.dynamic_font = 0
        self.dynamic_text_width = 0

        self.calculate_scales(window_width, window_height)

    def calculate_scales(self, width: int, height: int) -> None:
        """Compute scale factors, offsets and dynamic element sizes.

        Centers the map inside the given pixel dimensions and derives base
        sizes used for rendering.

        Args:
            width (int): Available width in pixels.
            height (int): Available height in pixels.
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
        padding_y = 130

        self.scale_x = (width - (padding_x * 2)) / map_width_units
        self.scale_y = (height - (padding_y * 2)) / map_height_units

        map_center_x = (min_x + max_x) / 2
        map_center_y = (min_y + max_y) / 2

        self.offset_x = (width / 2) - (map_center_x * self.scale_x)
        self.offset_y = (height / 2) - (map_center_y * self.scale_y)

        self.base_radius = max(8, min(
            25, int(min(self.scale_x, self.scale_y) / 4)))
        self.dynamic_font = max(7, min(11, int(self.scale_x / 8)))
        self.dynamic_text_width = max(45, int(self.scale_x * 0.9))

    def get_screen_coords(
            self, zone_x: float, zone_y: float) -> tuple[float, float]:
        """Convert logical map coordinates to screen pixel coordinates.

        Args:
            zone_x (float): X coordinate in map units.
            zone_y (float): Y coordinate in map units.

        Returns:
            tuple[float, float]: (screen_x, screen_y) in pixels.
        """
        screen_x = zone_x * self.scale_x + self.offset_x
        screen_y = zone_y * self.scale_y + self.offset_y
        return screen_x, screen_y

    def get_zone_radius(self, zone_name: str) -> int:
        """Return the drawing radius for a named zone.

        Radius is adjusted for special zone types (start/end/blocked/dead).

        Args:
            zone_name (str): Key of the zone in map_graph.zones.

        Returns:
            int: Radius in pixels to use when drawing the zone.
        """
        zone_obj = self.sim.map_graph.zones[zone_name]

        if zone_obj.is_start or zone_obj.is_end:
            return self.base_radius
        elif zone_obj.zone == "blocked" or "dead" in zone_name:
            return int(self.base_radius * 0.7)
        else:
            return int(self.base_radius * 0.8)
