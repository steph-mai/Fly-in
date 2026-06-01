from src.map_graph import MapGraph
from src.models import MapConfigModel
from collections import defaultdict


class Simulation:
    """Manages the global dynamic state of the drone simulation."""

    def __init__(self, map_config: MapConfigModel) -> None:
        self.total_drones: int = map_config.nb_drones
        self.map_graph: MapGraph = MapGraph(map_config)

        self.hub_occupancy: dict[str, int] = defaultdict(int)
        self.connection_occupancy: dict[tuple[str, str], int] = (
            defaultdict(int))

        self._initialize_drones()

    def _initialize_drones(self) -> None:
        """Finds the start hub and places all drones there initially."""
        start_zone_name = next(
            zone.name for zone in self.map_graph.zones.values()
            if zone.is_start
        )
        self.hub_occupancy[start_zone_name] = self.total_drones

    def display_status(self) -> None:  # vérifier aue tout est utile
        """Prints the current occupancy of the simulation."""
        print(f"Total drones: {self.total_drones}\n")

        print("Hubs occupancy:\n")

        for zone_name, zone_infos in self.map_graph.zones.items():
            max_capacity = zone_infos.max_drones  # TODO live coding
            print(f"{zone_name}: {self.hub_occupancy[zone_name]}"
                  f"/{max_capacity}")
            print(f"There is enough place: "
                  f"{self.is_enough_place_in_zone(zone_name)}")

        print("\nConnection occupancy:\n")

        displayed_connections = set()
        for zone_name in self.map_graph.graph_adj:
            neighbours = self.map_graph.get_neighbours(zone_name)
            for neighbour_name, max_link_capacity in neighbours.items():
                duo_zones = tuple(sorted([zone_name, neighbour_name]))
                if duo_zones not in displayed_connections:
                    current_drones_going = self.connection_occupancy[
                        (zone_name, neighbour_name)]
                    current_drones_returning = self.connection_occupancy[
                        (neighbour_name, zone_name)]
                    total_drones_in_connection = (
                        current_drones_going + current_drones_returning)
                    displayed_connections.add(duo_zones)
                    print(f"{duo_zones}: connection occupancy: "
                          f"{total_drones_in_connection}/{max_link_capacity}")

    def is_enough_place_in_zone(self, zone_name: str) -> bool:
        zone_infos = self.map_graph.zones[zone_name]
        if zone_infos.is_end is True:
            return True
        zone_max_capacity = zone_infos.max_drones
        return self.hub_occupancy[zone_name] <= zone_max_capacity

    def is_enough_place_in_connection(self, zone1: str, zone2: str) -> bool:
        """
        Checks if a bidirectional connection has enough remaining capacity.

        Takes into account drones flying in both directions
        (zone1->zone2 and zone2->zone1).
        """
        neighbours = self.map_graph.get_neighbours(zone1)
        max_link_capacity = neighbours.get(zone2, 0)

        current_drones_going = self.connection_occupancy[(zone1, zone2)]
        current_drones_returning = self.connection_occupancy[(zone2, zone1)]
        total_drones_in_flight = (
            current_drones_going + current_drones_returning)

        return total_drones_in_flight < max_link_capacity
