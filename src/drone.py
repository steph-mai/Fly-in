class Drone:
    def __init__(self, drone_id: int, start_zone: str) -> None:
        self.id = drone_id
        self.cooldown: int = 0
        self.current_zone = start_zone
        self.is_arrived: bool = False

    def display_drone_status(self) -> str:
        status: str = "arrived" if self.is_arrived else "in flight"
        cooldown: str = (
            f"cooldown = {self.cooldown}") if self.cooldown > 0 else ""
        return (f"Drone {self.id}: {status} {cooldown}, "
                f"current zone = {self.current_zone}")

