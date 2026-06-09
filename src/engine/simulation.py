from src.engine.map_graph import MapGraph
from src.parsing.models import MapConfigModel
from src.engine.drone import Drone, DroneState
import sys


class SimulationStats:
    """Container for secondary simulation metrics.

    Attributes:
        total_turns: Total number of simulation turns executed.
        moves_per_turn: List of drone moves count for each turn.
        active_turns_per_drone: Dictionary mapping drone ID to active
        turn count.
        total_path_cost: Cumulative cost of all drone movements.
    """

    def __init__(self) -> None:
        """Initialize SimulationStats with default values."""
        self.total_turns: int = 0
        self.moves_per_turn: list[int] = []
        self.active_turns_per_drone: dict[int, int] = {}
        self.total_path_cost: int = 0


class Simulation:
    """Manages the global dynamic state of the drone simulation.

    This class orchestrates the simulation lifecycle, including drone
    placement, movement validation, and state updates through
    discrete time steps.

    Attributes:
        total_drones: Number of drones in the simulation.
        map_graph: Graph representation of the simulation map.
        hub_occupancy: Dictionary tracking drone count at each zone.
        connection_occupancy: Dictionary tracking drone count on each
        connection.
        stats: Statistics container for simulation metrics.
    """

    def __init__(self, map_config: MapConfigModel) -> None:
        """Initialize the simulation and trigger setup.

        Args:
            map_config: Configuration model defining map structure and
            drone count.

        Raises:
            ValueError: If the map topology is invalid or unsolvable.
        """
        self.total_drones = map_config.nb_drones
        self.map_graph = MapGraph(map_config)
        self.hub_occupancy = {}
        self.connection_occupancy = {}
        self.stats = SimulationStats()

        self._setup_simulation()

    def _setup_simulation(self) -> None:
        """Handle all initial configuration logic.

        Initializes drones, builds distance maps, and validates map topology.
        """
        self._initialize_drones()
        self.distances_map = self.map_graph.build_distances_map(
            self.end_zone_name)
        self._validate_topology()

    def _validate_topology(self) -> None:
        """Verify if the map is solvable.

        Raises:
            ValueError: If start/end zones or mandatory zones are unreachable.
        """
        if self.distances_map.get(
                self.start_zone_name, float('inf')) == float('inf'):
            raise ValueError(
                "Map un-solvable: start/end or mandatory zones are blocked.")

    def _initialize_drones(self) -> None:
        """Find the start hub and place all drones there initially.

        Raises:
            ValueError: If start zone, end zone, or mandatory zones
            are blocked.
        """
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
        start_distance = self.distances_map.get(
            self.start_zone_name, float('inf'))
        if start_distance == float('inf'):
            raise ValueError(
                "This map cannot be solved: the start_zone, "
                "end_zone, or a mandatory passage zone may be blocked.")

        self.stats = SimulationStats()
        for drone in self.drones:
            self.stats.active_turns_per_drone[drone.id] = 0

    def get_satured_zones(self) -> set[str]:
        """Identify zones that have reached maximum capacity.

        Returns:
            Set of zone names that are at or above maximum drone capacity.
        """
        satured_zones: set[str] = set()
        for zone_name in self.map_graph.zones:
            if not self._is_enough_place_in_zone(zone_name):
                satured_zones.add(zone_name)
        return satured_zones

    def get_satured_connections(self) -> set[tuple[str, str]]:
        """Identify connections that have reached maximum capacity.

        Returns:
            Set of directional connection tuples at or above maximum capacity.
        """
        satured_connections: set[tuple[str, str]] = set()
        for connection in self.connection_occupancy:
            zone1, zone2 = connection
            if not self._is_enough_place_in_connection(zone1, zone2):
                satured_connections.add((zone1, zone2))
                satured_connections.add((zone2, zone1))
        return satured_connections

    def _is_enough_place_in_zone(self, zone_name: str) -> bool:
        """Check if a zone has available capacity for drones.

        Args:
            zone_name: Name of the zone to check.

        Returns:
            True if zone has available capacity, False otherwise.
        """
        zone_infos = self.map_graph.zones[zone_name]
        if zone_infos.is_end or zone_infos.is_start:
            return True
        zone_max_capacity = zone_infos.max_drones
        return self.hub_occupancy.get(zone_name, 0) < zone_max_capacity

    def _is_enough_place_in_connection(self, zone1: str, zone2: str) -> bool:
        """Check if a bidirectional connection has enough remaining capacity.

        Args:
            zone1: Name of the first zone.
            zone2: Name of the second zone.

        Returns:
            True if connection has available capacity, False otherwise.
        """
        neighbors = self.map_graph.get_neighbors(zone1)
        max_link_capacity = neighbors.get(zone2, 0)

        current_drones_going = self.connection_occupancy.get((zone1, zone2), 0)
        current_drones_returning = self.connection_occupancy.get(
            (zone2, zone1), 0)
        total_drones_in_flight = (
            current_drones_going + current_drones_returning)

        return total_drones_in_flight < max_link_capacity

    def process_turn(self) -> list[str]:
        """Execute a single simulation turn and move all eligible drones.

        Processes drone movements through a multi-pass algorithm that handles
        waiting in transit, saturation, and pathfinding. Handles transitions
        between hub and in-transit states.

        Returns:
            List of movement descriptions for this turn in format
            "D<id>-<destination>".
        """
        self.connection_occupancy.clear()

        for drone in self.drones:
            if drone.state != DroneState.ARRIVED and drone.cooldown > 0:
                route = drone.incoming_route
                self.connection_occupancy[route] = (
                    self.connection_occupancy.get(route, 0) + 1)

        turn_moves: list[str] = []
        satured_zones: set[str] = self.get_satured_zones()
        satured_connections: set[tuple[str, str]] = (
            self.get_satured_connections())
        moves_this_turn = 0

        drones_to_moves = sorted(
            self.drones,
            key=lambda d: self.distances_map.get(d.current_zone, float('inf'))
        )

        drones_to_process = []

        for drone in drones_to_moves:
            if drone.state == DroneState.ARRIVED:
                drone.previous_zone = drone.current_zone
                drone.incoming_route = (drone.current_zone, drone.current_zone)
                continue

            self.stats.active_turns_per_drone[drone.id] += 1

            if drone.cooldown >= 1:
                drone.cooldown -= 1
                connection_name = getattr(
                    drone, "current_connection", (
                        f"{drone.previous_zone}_{drone.current_zone}"))
                turn_moves.append(f"D{drone.id}-{connection_name}")
                moves_this_turn += 1
                self.stats.total_path_cost += 1
                continue

            drones_to_process.append(drone)

        has_freed_space = True

        while has_freed_space:

            has_freed_space = False

            for drone in drones_to_process[:]:

                best_next_zone = None
                current_dist_to_end = self.distances_map.get(
                    drone.current_zone, float('inf'))

                immobility_score = current_dist_to_end + 1.5

                for neighbor in self.map_graph.get_neighbors(
                        drone.current_zone):
                    if neighbor in satured_zones:
                        continue
                    if (drone.current_zone, neighbor) in satured_connections:
                        continue

                    neighbor_obj = self.map_graph.zones.get(neighbor)
                    if neighbor_obj.zone == "blocked":
                        continue

                    if neighbor == drone.previous_zone:
                        continue

                    dist_to_end = (
                        self.distances_map.get(neighbor, float('inf')))

                    move_score = dist_to_end
                    if dist_to_end >= current_dist_to_end:
                        move_score += (dist_to_end - current_dist_to_end + 1)

                    if move_score < immobility_score:
                        best_next_zone = neighbor

                if not best_next_zone:
                    drone.state = DroneState.WAITING
                    drone.incoming_route = (
                        drone.current_zone, drone.current_zone)
                    continue

                next_zone = best_next_zone
                previous_zone = drone.current_zone
                drone.previous_zone = previous_zone
                drone.current_connection = f"{previous_zone}_{next_zone}"

                self.hub_occupancy[next_zone] = (
                    self.hub_occupancy.get(next_zone, 0) + 1)
                self.hub_occupancy[previous_zone] = (
                    self.hub_occupancy.get(previous_zone, 0) - 1)
                drone.current_zone = next_zone
                drone.incoming_route = (previous_zone, next_zone)

                turn_moves.append(f"D{drone.id}-{next_zone}")
                moves_this_turn += 1
                self.stats.total_path_cost += 1

                if self._is_enough_place_in_zone(previous_zone) and (
                        previous_zone in satured_zones):
                    satured_zones.remove(previous_zone)

                self.connection_occupancy[(previous_zone, next_zone)] = (
                    self.connection_occupancy.get(
                        (previous_zone, next_zone), 0) + 1
                )

                if next_zone == self.end_zone_name:
                    drone.state = DroneState.ARRIVED
                    self.hub_occupancy[next_zone] -= 1

                zone_obj = self.map_graph.zones.get(next_zone)
                if zone_obj and zone_obj.zone == "restricted":
                    drone.cooldown += 1
                    drone.state = DroneState.IN_TRANSIT
                elif drone.state != DroneState.ARRIVED:
                    drone.state = DroneState.AT_HUB

                if not self._is_enough_place_in_zone(next_zone):
                    satured_zones.add(next_zone)
                if not self._is_enough_place_in_connection(
                        previous_zone, next_zone):
                    satured_connections.add((previous_zone, next_zone))
                    satured_connections.add((next_zone, previous_zone))

                drones_to_process.remove(drone)

                has_freed_space = True

        self.stats.moves_per_turn.append(moves_this_turn)
        self.stats.total_turns += 1

        return turn_moves

    def is_simulation_running(self) -> bool:
        """Check if simulation has active drones not yet arrived.

        Returns:
            True if any drone has not reached the end zone, False otherwise.
        """
        return any(
            drone.state != DroneState.ARRIVED for drone in self.drones)

    def run_simulation(self) -> None:
        """Execute the simulation until all drones arrive or timeout reached.

        Runs simulation process_turns in a loop, printing moves to stdout.
        Stops after 500 turns to prevent infinite loops on unsolvable maps.
        """
        tour = 1
        while self.is_simulation_running():
            moves = self.process_turn()
            if moves:
                print(" ".join(moves))

            tour += 1

            if tour > 500:
                print("[ERREUR] 500 turns limit reached", file=sys.stderr)
                break
