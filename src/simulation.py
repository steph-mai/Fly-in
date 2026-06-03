from src.map_graph import MapGraph
from src.models import MapConfigModel
from collections import defaultdict
from src.drone import Drone


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
        self.hub_occupancy[self.start_zone_name] = self.total_drones

        self.distances_map: dict[str, int] = (
            self.map_graph.build_distances_map(self.end_zone_name))



    def display_status(self) -> None:  # vérifier aue tout est utile
        """Prints the current occupancy of the simulation."""
        # print(f"Total drones: {self.total_drones}\n")

        # print("Hubs occupancy:\n")

        # for zone_name, zone_infos in self.map_graph.zones.items():
        #     max_capacity = zone_infos.max_drones  # TODO live coding
        #     print(f"{zone_name}: {self.hub_occupancy[zone_name]}"
        #           f"/{max_capacity}")
        #     print(f"There is enough place: "
        #           f"{self._is_enough_place_in_zone(zone_name)}")

        # print("\nConnection occupancy:\n")

        displayed_connections = set()
        for zone_name in self.map_graph.graph_adj:
            neighbors = self.map_graph.get_neighbors(zone_name)
            for neighbor_name, max_link_capacity in neighbors.items():
                duo_zones = tuple(sorted([zone_name, neighbor_name]))
                if duo_zones not in displayed_connections:
                    current_drones_going = self.connection_occupancy[
                        (zone_name, neighbor_name)]
                    current_drones_returning = self.connection_occupancy[
                        (neighbor_name, zone_name)]
                    total_drones_in_connection = (
                        current_drones_going + current_drones_returning)
                    displayed_connections.add(duo_zones)
                    # print(f"{duo_zones}: connection occupancy: "
                    #       f"{total_drones_in_connection}/{max_link_capacity}")

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
        return self.hub_occupancy[zone_name] < zone_max_capacity

    def _is_enough_place_in_connection(self, zone1: str, zone2: str) -> bool:
        """
        Checks if a bidirectional connection has enough remaining capacity.

        Takes into account drones flying in both directions
        (zone1->zone2 and zone2->zone1).
        """
        neighbors = self.map_graph.get_neighbors(zone1)
        max_link_capacity = neighbors.get(zone2, 0)

        current_drones_going = self.connection_occupancy[(zone1, zone2)]
        current_drones_returning = self.connection_occupancy[(zone2, zone1)]
        total_drones_in_flight = (
            current_drones_going + current_drones_returning)

        return total_drones_in_flight < max_link_capacity

    def tick(self) -> list[str]:
        self.connection_occupancy.clear()
        for drone in self.drones:
            if not drone.is_arrived and drone.cooldown > 0:
                self.connection_occupancy[(drone.previous_zone, drone.current_zone)] += 1

        turn_moves: list[str] = []

        blocked_zones: set[str] = self.get_blocked_zones()
        blocked_connections: set[tuple[str, str]] = self.get_blocked_connections()

        drones_to_moves = sorted(self.drones, key=lambda d: self.distances_map.get(d.current_zone, float('inf')))

        for drone in drones_to_moves:
            if drone.is_arrived:
                continue

            if drone.cooldown >= 1:
                drone.cooldown -= 1
                connection_name = getattr(
                    drone, "current_connection", f"{drone.previous_zone}_{drone.current_zone}")
                turn_moves.append(f"D{drone.id}-{connection_name}")
                continue

            best_next_zone = None
            min_dist = float('inf')

            for neighbor in self.map_graph.get_neighbors(drone.current_zone):
                if neighbor in blocked_zones:
                    continue
                if (drone.current_zone, neighbor) in blocked_connections:
                    continue

                dist = self.distances_map.get(neighbor, float('inf'))

                if dist < min_dist:
                    min_dist = dist
                    best_next_zone = neighbor

            if not best_next_zone:
                continue

            next_zone = best_next_zone

            previous_zone = drone.current_zone
            drone.previous_zone = previous_zone
            drone.current_connection = f"{previous_zone}_{next_zone}"

            self.hub_occupancy[next_zone] += 1
            self.hub_occupancy[previous_zone] -= 1
            drone.current_zone = next_zone

            turn_moves.append(f"D{drone.id}-{next_zone}")

            if self._is_enough_place_in_zone(previous_zone) and previous_zone in blocked_zones:
                blocked_zones.remove(previous_zone)

            self.connection_occupancy[(previous_zone, next_zone)] += 1

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

        return turn_moves

    def is_simulation_running(self) -> bool:
        is_running = False
        for drone in self.drones:
            if not drone.is_arrived:
                is_running = True
        return is_running

    def run_simulation(self) -> None:

        tour = 1

        while self.is_simulation_running():
            moves = self.tick()

            if moves:
                print(" ".join(moves))

            tour += 1

            if tour > 500:
                import sys
                print("[ERREUR] 500 turns limit reached", file=sys.stderr)
                break
        print(f"Number of turns: {tour}")
    # def run_simulation(self) -> None:
    #     print("\n" + "="*40)
    #     print("STARTING THE SIMULATION IN TERMINAL MODE")
    #     print("="*40)

    #     while self.is_simulation_running():
    #         tour = 1
    #         self.tick()

    #         for drone in self.drones:
    #             print(f"{drone.display_drone_status()}")

    #         # # 4. On affiche l'occupation des hubs et connexions
    #         # print("\n--- INFRASTRUCTURE ---")
    #         self.display_status()

    #         # # 5. PAUSE : Attend que tu appuies sur Entrée pour passer au tour suivant
    #         input("\nAppuyez sur [ENTRÉE] pour passer au tour suivant...")

    #         tour += 1

    #         # Sécurité anti-boucle infinie (edge case : si un drone reste bloqué)
    #         if tour > 100:
    #             print("\n[ERREUR] Limite de 100 tours atteinte. Arrêt de sécurité.")
    #             break

    #     if not self.is_simulation_running():
    #         print("\n" + "="*40)
    #         print(f"🏁 TOUS LES DRONES SONT ARRIVÉS EN {tour - 1} TOURS !")
    #         print("="*40)
