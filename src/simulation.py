from src.map_graph import MapGraph
from src.models import MapConfigModel
from src.drone import Drone
import sys


class Simulation:
    """Manages the global dynamic state of the drone simulation."""

    def __init__(self, map_config: MapConfigModel) -> None:
        self.total_drones: int = map_config.nb_drones
        self.map_graph: MapGraph = MapGraph(map_config)

        # CORRECTION 1 : Initialisation correcte des dictionnaires standards
        self.hub_occupancy: dict[str, int] = {}
        self.connection_occupancy: dict[tuple[str, str], int] = {}

        self._initialize_drones()

    def _initialize_drones(self) -> None:
        """Finds the start hub and places all drones there initially."""
        self.start_zone_name = next(
            zone.name for zone in self.map_graph.zones.values()
            if zone.is_start
        )
        self.end_zone_name = next(
            zone.name for zone in self.map_graph.zones.values()
            if zone.is_end
        )

        self.drones: list[Drone] = []
        for i in range(self.total_drones):
            drone: Drone = Drone(i, self.start_zone_name)
            drone.id = i
            drone.current_zone = self.start_zone_name
            self.drones.append(drone)

        # Initialisation propre des hubs occupés au départ
        self.hub_occupancy[self.start_zone_name] = self.total_drones

        self.distances_map: dict[str, int] = (
            self.map_graph.build_distances_map(self.end_zone_name))

    def get_blocked_zones(self) -> set[str]:
        blocked_zones: set[str] = set()
        for zone_name in self.map_graph.zones:
            if not self._is_enough_place_in_zone(zone_name):
                blocked_zones.add(zone_name)
        return blocked_zones

    def get_blocked_connections(self) -> set[tuple[str, str]]:
        blocked_connections: set[tuple[str, str]] = set()
        for connection in self.connection_occupancy:
            zone1, zone2 = connection
            if not self._is_enough_place_in_connection(zone1, zone2):
                blocked_connections.add((zone1, zone2))
                blocked_connections.add((zone2, zone1))
        return blocked_connections

    def _is_enough_place_in_zone(self, zone_name: str) -> bool:
        zone_infos = self.map_graph.zones[zone_name]
        if zone_infos.is_end or zone_infos.is_start:
            return True
        zone_max_capacity = zone_infos.max_drones
        return self.hub_occupancy.get(zone_name, 0) < zone_max_capacity

    def _is_enough_place_in_connection(self, zone1: str, zone2: str) -> bool:
        """Checks if a bidirectional connection has enough remaining capacity."""
        neighbors = self.map_graph.get_neighbors(zone1)
        max_link_capacity = neighbors.get(zone2, 0)

        current_drones_going = self.connection_occupancy.get((zone1, zone2), 0)
        current_drones_returning = self.connection_occupancy.get((zone2, zone1), 0)
        total_drones_in_flight = current_drones_going + current_drones_returning

        return total_drones_in_flight < max_link_capacity

    def tick(self) -> list[str]:
        self.connection_occupancy.clear()

        # CORRECTION 2 : Utilisation des bons attributs du Drone en cooldown
        for drone in self.drones:
            if not drone.is_arrived and drone.cooldown > 0:
                route = getattr(drone, "incoming_route", (drone.previous_zone, drone.current_zone))
                self.connection_occupancy[route] = self.connection_occupancy.get(route, 0) + 1
        turn_moves: list[str] = []

        blocked_zones: set[str] = self.get_blocked_zones()
        blocked_connections: set[tuple[str, str]] = self.get_blocked_connections()

        # Tri par distance décroissante (aspiration du flux)
        drones_to_moves = sorted(
            self.drones,
            key=lambda d: self.distances_map.get(d.current_zone, float('inf'))
        )

        for drone in drones_to_moves:
            if drone.is_arrived:
                drone.previous_zone = drone.current_zone
                continue

            if drone.cooldown >= 1:
                drone.cooldown -= 1
                connection_name = getattr(
                    drone, "current_connection", f"{drone.previous_zone}_{drone.current_zone}")
                turn_moves.append(f"D{drone.id}-{connection_name}")
                drone.previous_zone = drone.current_zone
                continue

            best_next_zone = None
            min_dist = float('inf')

            # 1. On lit à quelle distance le drone se trouve actuellement
            current_dist = self.distances_map.get(drone.current_zone, float('inf'))

            for neighbor in self.map_graph.get_neighbors(drone.current_zone):
                if neighbor in blocked_zones:
                    continue
                if (drone.current_zone, neighbor) in blocked_connections:
                    continue

                dist = self.distances_map.get(neighbor, float('inf'))

                # 2. LE CORRECTIF : On s'assure que le mouvement nous rapproche (dist < current_dist)
                if dist < min_dist and dist < current_dist:
                    min_dist = dist
                    best_next_zone = neighbor

            if not best_next_zone:
                drone.previous_zone = drone.current_zone
                continue

            next_zone = best_next_zone

            previous_zone = drone.current_zone
            drone.previous_zone = previous_zone
            drone.current_connection = f"{previous_zone}_{next_zone}"

            self.hub_occupancy[next_zone] = self.hub_occupancy.get(next_zone, 0) + 1
            self.hub_occupancy[previous_zone] = self.hub_occupancy.get(previous_zone, 0) - 1
            drone.current_zone = next_zone
            drone.incoming_route = (previous_zone, next_zone)

            turn_moves.append(f"D{drone.id}-{next_zone}")

            if self._is_enough_place_in_zone(previous_zone) and previous_zone in blocked_zones:
                blocked_zones.remove(previous_zone)

            self.connection_occupancy[(previous_zone, next_zone)] = (
                self.connection_occupancy.get((previous_zone, next_zone), 0) + 1
            )

            if next_zone == self.end_zone_name:
                drone.is_arrived = True

            zone_obj = self.map_graph.zones.get(next_zone)
            if zone_obj and zone_obj.zone == "restricted":
                drone.cooldown += 1

            if not self._is_enough_place_in_zone(next_zone):
                blocked_zones.add(next_zone)
            if not self._is_enough_place_in_connection(previous_zone, next_zone):
                blocked_connections.add((previous_zone, next_zone))
                blocked_connections.add((next_zone, previous_zone))

        def _get_drone_id(move_str: str) -> int:
            return int(move_str.split('-')[0][1:])

        turn_moves.sort(key=_get_drone_id)
        return turn_moves

    def is_simulation_running(self) -> bool:
        return any(not drone.is_arrived for drone in self.drones)

    def run_simulation(self) -> None:
        tour = 1
        while self.is_simulation_running():
            moves = self.tick()
            if moves:
                print(" ".join(moves))
            tour += 1

            if tour > 500:
                print("[ERREUR] 500 turns limit reached", file=sys.stderr)
                break

        # Affichage du score masqué pour la moulinette
        print(f"Number of turns: {tour - 1}", file=sys.stderr)
