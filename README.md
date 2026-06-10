*This project has been created as part of the 42 curriculum by stmaire*
<div align="center">
<br>
  <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTQPzuYKu7n0cWUYa5Kbg0_LrlEQAIURWeo9A&s" alt="42 Logo" width="400" />

  <br>
</div>

# Fly-in
![Language](https://img.shields.io/badge/Language-python-blue)
![Static Badge](https://img.shields.io/badge/parsing-pink)

A 42 school project: Design and implement an efficient drone routing system that navigates multiple autonomous drones from a central base to a target location through a dynamic network.

## 🔵 Description

### ✳️ Goal
Develop an intelligent drone routing system that efficiently manages multiple autonomous drones navigating through a dynamic network of zones. The system must optimize pathfinding while respecting zone constraints (priority zones, restricted zones, blocked zones) and managing concurrent drone movements.

### ✳️ Overview
The Fly-in project simulates a multi-agent pathfinding system where drones must navigate from a starting zone to a target zone through an interconnected network. The system uses an inverted Dijkstra algorithm to pre-calculate optimal paths and implements a turn-based movement system that handles zone capacities, movement penalties, and priority-based drone ordering.

## 🔵 Instructions

### ✳️ Prerequisites

- Python 3.10 or later.
- uv (high-performance Python package manager).

### ✳️ Installation

The project uses uv for dependency management and isolation. To set up the environment and install necessary packages (arcade, pydantic, flake8, mypy, pytest):

```Bash
# Install dependencies and create virtual environment
uv sync
```
Using the Makefile:
```bash
make install
```
### ✳️ Execution

* ### Using the Makefile (Recommended)
```Bash
# Run with default paths (data/input/ and data/output/)
make run
```
Clean cache and temporary files (__pycache__, .mypy_cache, etc.)

```
make clean
```

* ### Manual Execution via uv
**1. Default execution**
```Bash
uv run python -m src
```

**2. Development & Quality Control**
In accordance with the 42 curriculum standards, the project adheres to strict coding rules:

Linting: Both flake8 and mypy are used to ensure PEP 8 compliance and strict type safety.

```Bash
make lint        # Standard check
make lint-strict # Enhanced strict checking
```

**3. Debugging**
To run the script in debug mode with pdb:

```Bash
make debug
```

**4. Testing**
While not graded, a suite of tests is included to verify the constrained decoding logic:

```Bash
make test
```

## 🔵 Resources

### ✳️ References
- Dijkstra's Algorithm: Classic pathfinding in weighted graphs
- Multi-agent pathfinding systems and conflict resolution
- Graph theory and network topology optimization
- Heap-based priority queues (Python heapq)

### ✳️ AI Usage
AI was used to:
- **Debugging**: Problem analysis for edge cases in drone movement logic
- **Documentation**: Assistance in clarifying algorithm explanations and README structure
- **Testing**: Generation of unit test cases for the Dijkstra implementation

## 🔵 Algorithm Explanation

### ✳️ Inverted Dijkstra's Algorithm for Distance Calculation
The simulation engine uses an inverted Dijkstra implementation to pre-calculate network topology. By performing exploration from the destination node (end_zone_name), the algorithm generates a distances_map. Each zone is assigned the minimal cost to reach the exit. Zone costs are weighted: 'priority' zones cost 0.5, 'restricted' zones cost 2.0, other zones cost 1.0, and 'blocked' zones are skipped entirely.

This approach enables real-time decision-making for each drone, transforming complex pathfinding into simple local distance comparisons at each turn.

**Complexity Analysis:**
- **Time Complexity**: $O(Z \log Z + E)$ where $Z$ is the number of zones and $E$ is the number of connections
- **Space Complexity**: $O(Z)$ for storing zone distances

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

### ✳️ Visual Representation Features
The project includes arcade-based visualization that enhances user experience by:
- **Real-time rendering** of drone movements through the network
- **Color-coded zones** indicating zone type (priority, restricted, blocked, normal)
- **Animated drone transitions** showing pathfinding decisions
- **Statistics overlay** displaying turn count, arrived drones, and network status


