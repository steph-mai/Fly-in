from src.models import MapConfigModel, Zone
from collections import defaultdict


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

    def get_neighbours(self, zone_name: str) -> dict[str, int]:
        """
        Get the neighbors and link capacities for a specific zone.

        Args:
            zone_name (str): The name of the zone to look up.

        Returns:
            dict[str, int]: A dictionary of neighboring zone names mapping
                to their maximum link capacity.
        """
        neighbours = self.graph_adj.get(zone_name, {})
        return neighbours

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

    def find_best_path(self, start_name: str, end_name: str, blocked_zones)
