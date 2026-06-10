"""Map graph utilities for the simulation.

Provides a MapGraph class that represents zones and their bidirectional
connections with capacities, and utilities to compute shortest-distance
maps to a target zone using weighted steps depending on zone types.
"""
from src.parsing.models import MapConfigModel, Zone
from collections import defaultdict
import heapq


class MapGraph:
    """Representation of the map topology and adjacency.

    The MapGraph holds a mapping of zone names to validated Zone objects
    and constructs a bidirectional adjacency mapping between zones with
    their maximum link capacities.

    Args:
        map_config (MapConfigModel): Pydantic-validated map configuration
            containing zones and connections.

    Attributes:
        zones (dict[str, Zone]): Mapping from zone name to Zone object.
        graph_adj (dict[str, dict[str, int]]): Adjacency mapping where each
            zone name maps to a dict of neighbor zone names and their
            maximum link capacities.
    """
    def __init__(self, map_config: MapConfigModel) -> None:
        """Initialize the MapGraph.

        Builds the zones mapping and the adjacency graph from the provided
        map configuration.

        Args:
            map_config (MapConfigModel): The map configuration model.
        """
        self.zones: dict[str, Zone] = {
            zone.name: zone for zone in map_config.zones
            }
        self.graph_adj = self._build_graph(map_config)

    def _build_graph(
            self, map_config: MapConfigModel
            ) -> dict[str, dict[str, int]]:
        """Build a bidirectional adjacency graph from map configuration.

        Each connection in the configuration is inserted in both directions
        with the connection's max_link_capacity.

        Args:
            map_config (MapConfigModel): The map configuration containing
                connection definitions.

        Returns:
            dict[str, dict[str, int]]: Adjacency mapping of zone ->
            (neighbor -> max_link_capacity).
        """
        graph_adjacency: dict[str, dict[str, int]] = defaultdict(dict)
        for connection in map_config.connections:
            graph_adjacency[connection.zone1][connection.zone2] = (
                connection.max_link_capacity)
            graph_adjacency[connection.zone2][connection.zone1] = (
                connection.max_link_capacity)
        return dict(graph_adjacency)

    def get_neighbors(self, zone_name: str) -> dict[str, int]:
        """Return neighbors and their capacities for a given zone.

        Args:
            zone_name (str): Zone name to query.

        Returns:
            dict[str, int]: Mapping of neighbor zone names to their maximum
                link capacity. Returns an empty dict if the zone is unknown.
        """
        neighbors = self.graph_adj.get(zone_name, {})
        return neighbors

    def build_distances_map(self, end_zone_name: str) -> dict[str, float]:
        """Compute weighted distances from every reachable zone to end_zone.

        Uses a Dijkstra-like approach (min-heap) starting from the end zone
        and propagating outward. Step costs depend on the zone type:
        - 'priority' zones cost 0.5
        - 'restricted' zones cost 2.0
        - other zones cost 1.0
        Zones whose type is 'blocked' are skipped.

        Args:
            end_zone_name (str): Name of the destination zone to compute
                distances to.

        Returns:
            dict[str, float]: Mapping of zone name to the minimal computed
                distance (float) to reach end_zone_name.
        """
        distances_to_end_dict: dict[str, float] = {}

        queue: list[tuple[float, str]] = [(0.0, end_zone_name)]

        while queue:
            current_distance_to_end, current_zone = heapq.heappop(queue)

            if current_zone in distances_to_end_dict:
                continue

            distances_to_end_dict[current_zone] = current_distance_to_end

            current_zone_obj = self.zones.get(current_zone)

            if current_zone_obj is None:
                continue

            if current_zone_obj.zone == 'priority':
                step_cost = 0.5
            elif current_zone_obj.zone == 'restricted':
                step_cost = 2.0
            else:
                step_cost = 1.0

            neighbors = self.get_neighbors(current_zone)
            for neighbor in neighbors:
                neighbor_obj = self.zones.get(neighbor)

                if neighbor_obj is None:
                    continue
                if neighbor_obj.zone == 'blocked':
                    continue

                if neighbor not in distances_to_end_dict:
                    new_distance_to_end = current_distance_to_end + step_cost
                    heapq.heappush(queue, (new_distance_to_end, neighbor))

        return distances_to_end_dict
