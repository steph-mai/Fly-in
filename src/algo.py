import heapq

class MapGraph
    def find_fastest_path(self, start_name: str, end_name: str, blocked_zones: set[str] = None) -> list[str]:
        if blocked_zones is None: blocked_zones = set()
        if start_name == end_name: return [start_name]
        if end_name in blocked_zones: return []

        priority_queue = [(0, [start_name])]

        best_times = {start_name: 0}

        while priority_queue:
            current_cost, current_path = heapq.heappop(priority_queue)
            current_zone = current_path[-1]

            if current_zone == end_name:
                return current_path

            if current_cost > best_times.get(current_zone, float('inf')):
                continue

            for neighbor_name in self.get_neighbours(current_zone):
                if neighbor_name in blocked_zones:
                    continue

                neighbor_obj = self.zones[neighbor_name]
                step_cost = 2 if neighbor_obj.zone == "restricted" else 1

                new_cost = current_cost + step_cost

                if new_cost < best_times.get(neighbor_name, float('inf')):
                    best_times[neighbor_name] = new_cost
                    new_path = list(current_path)
                    new_path.append(neighbor_name)
                    heapq.heappush(priority_queue, (new_cost, new_path))

        return []
