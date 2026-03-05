# BFS + DFS Pathfinding (Python Console)

## Run
```bash
python pathfinding.py
```

## What to look for
- BFS returns a shortest path in this unweighted 4-direction grid.
- DFS is valid for reachability, but it does **not** guarantee shortest path.
- The output includes:
  - `found` (whether path exists)
  - `path_len`
  - `visited` count
  - rendered map (`*` for path, `+` for visited cells)

## Monster Chase (Turn-Based)
Implemented in `pathfinding.py` as `game_loop(mode="BFS")`.

Rules:
- `P` = player, `M` = monster, `#` = wall, `.` = floor, `G` = optional exit.
- Player moves with `W/A/S/D`.
- Monster recomputes path to player every turn using selected mode:
  - `mode="BFS"` (shortest-path hunter)
  - `mode="DFS"` (often less direct)
- Monster moves exactly one step along the computed path each turn.
- Lose if monster reaches player. Win if player reaches `G`.

To play from a Python shell:
MAKE SURE YOU RUN "python" BEFORE SO IT IS A PYTHON SHELL
```python
import pathfinding
pathfinding.game_loop("BFS")
# or
pathfinding.game_loop("DFS")
```

## Reflection
### 1) A case where DFS path is longer than BFS
On the provided built-in maps, BFS and DFS can both find a path, but DFS may take a longer route depending on stack ordering and corridor structure. BFS explores by layers (distance 0, then 1, then 2, ...), so the first time it reaches `G`, that route has minimum step count. DFS commits deep into one branch first, so it can hit `G` via a detour before trying a shorter branch.

### 2) Compare visited counts
Visited counts depend on map layout and neighbor order. BFS may visit a broader frontier near the start, while DFS can tunnel deeply and sometimes visit fewer nodes before finding `G`; in other layouts, DFS can also wander into dead ends and visit more. The script prints visited totals so you can compare map-by-map.

### 3) Why BFS guarantees shortest path here, DFS does not
This grid is an unweighted graph: each legal move costs the same (one step). BFS is equivalent to shortest-path search in unweighted graphs because queue order ensures nondecreasing distance from `S`. DFS uses LIFO order and ignores global distance; it is complete for finite graphs with cycle checks but not optimal for path length.
