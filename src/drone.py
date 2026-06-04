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

    def display_drone_status(self) -> str:
        # status: str = "arrived" if self.is_arrived else "in flight"
        # cooldown: str = (
        #     f"cooldown = {self.cooldown}") if self.cooldown > 0 else ""
        # return (f"Drone {self.id}: {status} {cooldown}, "
        #         f"current zone = {self.current_zone}")
        return (f"D<{self.id}>-<{self.current_zone}>")
