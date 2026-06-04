class Drone:
    """
    Represents a drone within the simulation.
    """

    def __init__(self, drone_id: int, start_zone: str) -> None:
        """Initialize the drone with its ID and its starting location."""
        self.id = drone_id
        self.cooldown: int = 0
        self.previous_zone = start_zone
        self.current_zone = start_zone
        self.is_arrived: bool = False
        self.current_connection = ""
