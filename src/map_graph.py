from src.models import MapConfigModel, Zone
from collections import defaultdict
import heapq


class MapGraph:
    """
    Represents the topography of the map.
    Handles the adjacency dictionary.

    Attributes:
        zones (dict[str, Zone]): A dictionary mapping zone names to their
            Pydantic validated Zone objects.
        graph_adj (dict[str, dict[str, int]]): A bidirectional adjacency
            dictionary mapping each zone to its connected neighbors and their
            maximum capacities.
    """
    def __init__(self, map_config: MapConfigModel) -> None:
        """
        Initializes the zones dictionary and the graph dictionary.

        Args:
            map_config (MapConfigModel): The Pydantic validated map
            configuration.
        """
        self.zones: dict[str, Zone] = {
            zone.name: zone for zone in map_config.zones
            }
        self.graph_adj = self._build_graph(map_config)

    def _build_graph(
            self, map_config: MapConfigModel
            ) -> dict[str, dict[str, int]]:
        """
        Build the bidirectional adjacency graph from the map configuration.

        Args:
            map_config (MapConfigModel): The Pydantic validated map
            configuration.

        Returns:
            dict[str, dict[str, int]]: A dictionary mapping each zone to its
                neighbors and their link capacities.
        """
        graph_adjacency: dict[str, dict[str, int]] = defaultdict(dict)
        for connection in map_config.connections:
            graph_adjacency[connection.zone1][connection.zone2] = (
                connection.max_link_capacity)
            graph_adjacency[connection.zone2][connection.zone1] = (
                connection.max_link_capacity)
        return dict(graph_adjacency)

    def get_neighbors(self, zone_name: str) -> dict[str, int]:
        """
        Get the neighbors and link capacities for a specific zone.

        Args:
            zone_name (str): The name of the zone to look up.

        Returns:
            dict[str, int]: A dictionary of neighboring zone names mapping
                to their maximum link capacity.
        """
        neighbors = self.graph_adj.get(zone_name, {})
        return neighbors

    def get_zone_infos(self, zone_name: str) -> Zone | None:
        """
        Get metadata information about a specific zone.

        Args:
            zone_name (str): The name of the zone to look up.

        Returns:
            Zone | None: The Zone object containing coordinates and capacities,
                or None if the zone does not exist.
        """
        infos_zone = self.zones.get(zone_name)
        return infos_zone

    def build_distances_map(self, end_zone_name: str) -> dict[str, int]:
        distances_dict = {}
        distances_dict[end_zone_name] = 0

        queue: list[str] = [end_zone_name]

        while queue:
            current_zone = queue.pop()
            current_distance = distances_dict[current_zone]

            neighbors = self.get_neighbors(current_zone)
            for neighbor in neighbors:
                if neighbor not in distances_dict:
                    current_distance += 1
                    distances_dict[neighbor] = current_distance
                    queue.append(neighbor)
        return distances_dict

    def find_best_path(
            self,
            start_name: str,
            end_name: str,
            blocked_zones: set[str],
            blocked_connections: set[tuple[str, str]]
    ) -> list[str]:
        """
        Find the best path using a Dijkstra algorithm

        Args:
            start_name(str): The name of the start zone.
            end_name(str): The name of the end zone.
            blocked_zones(set[str]): includes the names of the inaccessible
            zones.

        Return:
            list[str]; The best path from start_zone to end_zone.
        """
        if not blocked_zones:
            blocked_zones: set = set()
        if not blocked_connections:
            blocked_connections: set = set()

        if start_name == end_name:
            return [start_name]

        if end_name in blocked_zones:
            return []

        priority_queue: list[tuple[int, list[str]]] = [(0, [start_name])]
        best_times: dict[str, int] = {start_name: 0}

        while priority_queue:
            current_cost, current_path = heapq.heappop(priority_queue)
            current_zone = current_path[-1]

            if current_zone == end_name:
                return current_path

            if current_cost > best_times.get(current_zone, float('inf')):
                continue

            dico_neighbors = self.graph_adj[current_zone]
            for neighbor, link_capacity in dico_neighbors.items():
                if (
                    link_capacity == 0 or
                    neighbor in blocked_zones or
                    (current_zone, neighbor) in blocked_connections
                ):
                    continue

                neighbor_obj = self.zones[neighbor]
                if neighbor_obj.zone == "restricted":
                    new_cost = current_cost + 2
                else:
                    new_cost = current_cost + 1

                if new_cost < best_times.get(neighbor, float('inf')):
                    best_times[neighbor] = new_cost
                    new_path = list(current_path)
                    new_path.append(neighbor)
                    heapq.heappush(priority_queue, (new_cost, new_path))
        return []
