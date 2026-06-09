"""Module defining drone primitives for the simulation.

Provides DroneState enum and Drone class used by the engine.
"""
from enum import Enum, auto


class DroneState(Enum):
    """Enumeration of possible drone states."""
    AT_HUB = auto()
    IN_TRANSIT = auto()
    WAITING = auto()
    ARRIVED = auto()


class Drone:
    """Representation of a drone within the simulation.

    Attributes:
        state (DroneState): Current state of the drone.
        id (int): Unique identifier for the drone.
        cooldown (int): Cooldown counter before next action.
        previous_zone (str): Name of the last zone visited.
        current_zone (str): Name of the current zone.
        current_connection (str): Identifier for the active connection.
        incoming_route (tuple[str, str]): Tuple of (from_zone, to_zone).
    """
    def __init__(self, drone_id: int, start_zone: str) -> None:
        """Initialize a Drone instance.

        Args:
            drone_id (int): The ID of the drone.
            start_zone (str): The name of the start zone.
        """
        self.state = DroneState.AT_HUB
        self.id = drone_id
        self.cooldown: int = 0
        self.previous_zone = start_zone
        self.current_zone = start_zone
        self.current_connection = ""
        self.incoming_route: tuple[str, str] = (start_zone, start_zone)
