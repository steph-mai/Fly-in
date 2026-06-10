*This project has been created as part of the 42 curriculum by stmaire*
<div align="center">
<br>
  <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTQPzuYKu7n0cWUYa5Kbg0_LrlEQAIURWeo9A&s" alt="42 Logo" width="400" />

  <br>
</div>

# Fly-in
![Language](https://img.shields.io/badge/Language-python-blue)
![Static Badge](https://img.shields.io/badge/Rigor-pink)
![Static Badge](https://img.shields.io/badge/Algorithms_&_IA-pink)
![Static Badge](https://img.shields.io/badge/Graphics-pink)


## 🔵 Description

### ✳️ Goal
Design and implement an efficient multi-agent drone routing system that navigates autonomous drones from a central base to a target location through a dynamic network, optimizing for minimal simulation turns while handling real-world constraints.

### ✳️ Overview
The Fly-in project simulates a turn-based multi-agent pathfinding system where drones navigate interconnected zones from start to destination. The system leverages an **inverted Dijkstra algorithm** to pre-calculate optimal distances, enabling real-time decision-making through simple local comparisons. Each turn processes drone movements while respecting zone capacities, movement penalties, priority-based ordering, and restricted zone logic—demonstrating practical solutions to concurrent pathfinding challenges.

### ✳️ Key Features
- **Pre-calculated pathfinding**: Inverted Dijkstra from destination
- **Multi-agent coordination**: Priority-based sorting
- **Network constraints**: Zone capacities, movement penalties, blocked/restricted zones
- **Real-time visualization**: Arcade-based interface

## 🔵 Instructions

### ✳️ Prerequisites

- Python 3.10 or later
- uv (high-performance Python package manager)

### ✳️ Installation

The project uses uv for dependency management and isolation. To set up the environment and install necessary packages (arcade, pydantic, flake8, mypy, pytest):

```bash
# Install dependencies and create virtual environment
uv sync
```

Or using the Makefile:

```bash
make install
```

### ✳️ Execution

**1. Run the Simulation (Recommended)**

```bash
make run
```

**2. Manual Execution via uv**

```bash
uv run python fly_in.py
```

**3. Code Quality & Linting**

In accordance with the 42 curriculum standards, the project adheres to strict coding rules using flake8 and mypy for PEP 8 compliance and type safety.

```bash
# Standard linting
make lint

# Strict type checking
make lint-strict
```

**4. Debugging**

Run with Python debugger (pdb):

```bash
make debug
```

**5. Testing**

Run the test suite (not graded but verifies core logic):

```bash
make test
```

**6. Cleanup**

Remove cache and temporary files:

```bash
make clean
```

## 🔵 Algorithm Explanation

### ✳️ Inverted Dijkstra's Algorithm for Distance Calculation
The simulation engine uses an inverted Dijkstra implementation to pre-calculate network topology. By performing exploration from the destination node (end_zone_name), the algorithm generates a distances_map. Each zone is assigned the minimal cost to reach the exit. Zone costs are weighted: 'priority' zones cost 0.5, 'restricted' zones cost 2.0, other zones cost 1.0, and 'blocked' zones are skipped entirely.

This approach enables real-time decision-making for each drone, transforming complex pathfinding into simple local distance comparisons at each turn.

**Complexity Analysis:**
- $O(Z \log Z + C)$ where $Z$ is the number of zones and $C$ is the number of connections


### ✳️ Turn Processing Algorithm

Each simulation turn follows this process:

1. **Update drone counts** per connection (excluding arrived drones and those waiting in restricted zones)
2. **Sort drones** by weighted distance to destination using `distances_map.get()`
3. **Identify movable drones** ("drones_to_process"):
   - Exclude arrived drones and restricted zone waiters
   - Iterate while space becomes available and drones can move
4. **For each drone, find optimal moves**:
   - Search neighboring zones closer to destination
   - Apply penalties: inactivity penalty encourages movement; lateral (non-progressive) moves are penalized
   - Evaluate feasible zones (not saturated, not blocked, closer to exit)
5. **Execute moves**: Update zone counts and drone states; handle restricted zone entry logic
6. **Update statistics** and return movement list for display

**Complexity Analysis:**
- Let D = number of drones, V = average connections per zone
- Drone sorting: $O(D \log D)$
- Movement loop: $O(D \cdot V)$
- Dictionary operations: $O(1)$
- **Overall**: $O(D \log D + D \cdot V)$


## 🔵 Visual Representation Features
The project includes arcade-based visualization that enhances user experience by:
- **Dynamic Scaling:** Automatic coordinate mapping to fit any window size.
 - **Drone animation:** smooth interpolation between zones, small offsets to avoid overlaps, fade-out on arrival; restricted zones show extended traversal visually.-
 - **Zone display:** color-coded circles with icons (start/end/blocked/restricted) and live counts (current / max).
- **Connections:** lines with real-time occupancy / capacity labels shown on links.
- **Statistics overlay** displaying turn count, arrived drones, and network status

These visuals provide immediate feedback on congestion, bottlenecks and routing decisions, improving usability and analysis.

## 🔵 Resources

### ✳️ References
- Dijkstra's Algorithm: Classic pathfinding in weighted graphs
    - https://www.w3schools.com/dsa/dsa_algo_graphs_dijkstra.php
    - https://www.maths-cours.fr/methode/algorithme-de-dijkstra-etape-par-etape#google_vignette
- Graph theory and network topology optimization
    - https://fr.wikipedia.org/wiki/Th%C3%A9orie_des_graphes
    - https://www.apprendre-en-ligne.net/graphes/graphes.pdf
- Heap-based priority queues (Python heapq)
    - https://docs.python.org/3/library/heapq.html

### ✳️ AI Usage
Artificial Intelligence was used as a support tool to improve documentation and code quality.

- **Refactoring:** helped simplify class structure and improve modularity.
- **Algorithm description:** clarified graph theory and pathfinding concepts.
- **Debugging:** helped detect edge cases and potential issues in drone movement.
- **Writing:** helped translate this readme into English.

