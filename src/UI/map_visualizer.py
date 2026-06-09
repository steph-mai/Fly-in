"""Map rendering orchestrator."""

import arcade
import math
from src.engine.simulation import Simulation
from src.engine.drone import DroneState
from src.UI.coordinate_mapper import CoordinateMapper
from src.UI.graphics_resource_manager import GraphicsResourceManager


class MapVisualizer:
    """Orchestrates rendering using mapper and resource manager.

    Attributes:
        sim (Simulation): The active simulation.
        mapper (CoordinateMapper): Geometric calculations.
        resources (GraphicsResourceManager): Graphics assets.
    """

    def __init__(self, simulation: Simulation, window_width: int,
                 window_height: int) -> None:
        self.sim = simulation
        self.geometric_mapper = CoordinateMapper(
            simulation, window_width, window_height)
        self.graphical_resources = GraphicsResourceManager(
            simulation, self.geometric_mapper)

    def draw_everything(self) -> None:
        """Execute the full rendering pipeline."""
        if self.graphical_resources.background_list:
            self.graphical_resources.background_list.draw()

        self._draw_connections()
        self._draw_zones()
        self.graphical_resources.icon_list.draw()
        self.graphical_resources.drone_list.draw()

    def _draw_connections(self) -> None:
        """Render connection lines and occupancy labels."""
        displayed_links = set()
        for zone_name in self.sim.map_graph.graph_adj:
            neighbors = self.sim.map_graph.get_neighbors(zone_name)
            zone_from = self.sim.map_graph.zones[zone_name]

            for neighbor_name in neighbors:
                duo_zones = tuple(sorted([zone_name, neighbor_name]))
                if duo_zones not in displayed_links:
                    zone_to = self.sim.map_graph.zones[neighbor_name]
                    start_x, start_y = self.geometric_mapper.get_screen_coords(
                        zone_from.x, zone_from.y)
                    end_x, end_y = self.geometric_mapper.get_screen_coords(
                        zone_to.x, zone_to.y)

                    arcade.draw_line(
                        start_x, start_y, end_x, end_y,
                        arcade.color.STEEL_BLUE, line_width=3
                    )

                    connection_occupancy = (
                        self.sim.connection_occupancy.get(
                            (zone_name, neighbor_name), 0) +
                        self.sim.connection_occupancy.get(
                            (neighbor_name, zone_name), 0))
                    max_capacities = self.sim.map_graph.graph_adj.get(
                        zone_name)
                    max_link_capacity = max_capacities.get(neighbor_name)

                    text_obj = self.graphical_resources.link_labels[duo_zones]
                    text_obj.text = (
                        f"{connection_occupancy}/{max_link_capacity}")
                    text_obj.draw()

                    displayed_links.add(duo_zones)

    def _draw_zones(self) -> None:
        """Render zone circles, labels, and drone counts."""
        for zone_name, zone_obj in self.sim.map_graph.zones.items():
            screen_x, screen_y = self.geometric_mapper.get_screen_coords(
                zone_obj.x, zone_obj.y)
            radius = self.geometric_mapper.get_zone_radius(zone_name)

            zone_color_name = getattr(zone_obj, "color", None)
            color = getattr(
                arcade.color, str(zone_color_name), None
                ) if zone_color_name else None

            if color is None:
                color = arcade.color.WHITE

            arcade.draw_circle_filled(screen_x, screen_y, radius, color)
            arcade.draw_circle_outline(
                screen_x, screen_y, radius, arcade.color.DIM_GRAY, 2)

            current_drones_in_zone = self._count_drones_in_zone(
                screen_x, screen_y, radius)
            max_drones_in_zone = zone_obj.max_drones

            display_zone_name = zone_name.replace('_', '\n')

            if "dead" in zone_name or zone_obj.zone == "blocked":
                label_text = f"{display_zone_name}"
            else:
                label_text = (
                    f"{display_zone_name}\n({current_drones_in_zone}/"
                    f"{max_drones_in_zone})")

            text_obj = self.graphical_resources.map_labels[zone_name]
            text_obj.text = label_text
            text_obj.draw()

    def _count_drones_in_zone(self, screen_x: float, screen_y: float,
                              radius: int) -> int:
        """Count visible drones within a zone."""
        count = 0
        for drone_sprite in self.graphical_resources.drone_list:
            if drone_sprite.alpha == 0:
                continue
            dist = math.hypot(
                drone_sprite.center_x - screen_x,
                drone_sprite.center_y - screen_y)
            if dist <= radius + (self.geometric_mapper.base_radius * 0.5):
                count += 1
        return count

    def update_drones_animation(self, process_rate: float) -> None:
        """Update drone sprite positions and opacity.

        Interpolates drone positions between source and destination zones,
        accounting for restricted zones which require two turns to traverse.
        Applies per-drone offsets (jitter) for visual clarity and fades drones
        as they reach their final destination.

        Args:
            process_rate (float): Animation progress between 0.0 (turn start)
                and 1.0 (turn end).
        """

        for drone_sprite in self.graphical_resources.drone_list:
            drone = drone_sprite.drone_ref

            route_start, route_end = getattr(
                drone, "incoming_route",
                (drone.previous_zone, drone.current_zone))

            start_zone_obj = self.sim.map_graph.zones[route_start]
            end_zone_obj = self.sim.map_graph.zones[route_end]

            start_x, start_y = self.geometric_mapper.get_screen_coords(
                start_zone_obj.x, start_zone_obj.y)
            end_x, end_y = self.geometric_mapper.get_screen_coords(
                end_zone_obj.x, end_zone_obj.y)

            actual_progress = process_rate
            if end_zone_obj.zone == "restricted":
                if drone.cooldown == 1:
                    actual_progress = process_rate * 0.5
                else:
                    actual_progress = 0.5 + (process_rate * 0.5)

            # Linear interpolation (Lerp) between start and end positions
            current_x = start_x + (end_x - start_x) * actual_progress
            current_y = start_y + (end_y - start_y) * actual_progress

            # Apply per-drone jitter for visual clarity in swarms
            offset_x = (drone.id % 3 - 1) * (self.geometric_mapper.base_radius * 0.4)
            offset_y = (
                (drone.id // 3) % 3 - 1) * (
                    self.geometric_mapper.base_radius * 0.4)

            drone_sprite.center_x = current_x + offset_x
            drone_sprite.center_y = current_y + offset_y

            if drone.state == DroneState.ARRIVED:
                if drone.previous_zone == drone.current_zone:
                    drone_sprite.alpha = 0
                else:
                    drone_sprite.alpha = max(
                        0, int(255 * (1.0 - process_rate)))
            else:
                drone_sprite.alpha = 255
