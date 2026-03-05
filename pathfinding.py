from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

Pos = Tuple[int, int]  # (row, col)
Grid = List[List[str]]


EXAMPLE_MAP_1 = """
##########
#S..#....#
#..##.##.#
#...#...G#
##########
""".strip("\n")

EXAMPLE_MAP_2 = """
############
#S.....#...#
###.##.#.#.#
#...#..#.#G#
#.###..#...#
#......###.#
############
""".strip("\n")

EXAMPLE_MAP_3 = """
#########
#S.....G#
#.#####.#
#.......#
#########
""".strip("\n")

MONSTER_MAP = """
############
#P...#....G#
#.#.#.##.#.#
#.#...#..#.#
#.###.#.##.#
#...#...M..#
############
""".strip("\n")


@dataclass
class GameState:
    grid: Grid
    player: Pos
    monster: Pos
    goal: Optional[Pos]


def parse_grid(text: str) -> Tuple[Grid, Pos, Pos]:
    """
    Convert a multiline string map into a grid plus start and goal positions.

    Map legend:
    '#' wall
    '.' floor
    'S' start (exactly one)
    'G' goal (exactly one)
    """
    rows = [list(line) for line in text.splitlines() if line.strip()]
    if not rows:
        raise ValueError("Grid cannot be empty")

    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("Grid must be rectangular")

    start: Optional[Pos] = None
    goal: Optional[Pos] = None

    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "S":
                if start is not None:
                    raise ValueError("Grid must contain exactly one S")
                start = (r, c)
            elif ch == "G":
                if goal is not None:
                    raise ValueError("Grid must contain exactly one G")
                goal = (r, c)
            elif ch not in {"#", "."}:
                raise ValueError(f"Invalid tile '{ch}' in grid")

    if start is None or goal is None:
        raise ValueError("Grid must contain exactly one S and one G")

    return rows, start, goal


def neighbors(grid: Grid, node: Pos) -> List[Pos]:
    """Return valid 4-direction neighbors that are not walls."""
    r, c = node
    out: List[Pos] = []
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != "#":
            out.append((nr, nc))
    return out


def reconstruct_path(parent: Dict[Pos, Pos], start: Pos, goal: Pos) -> Optional[List[Pos]]:
    """Reconstruct path from start->goal using parent pointers. Return None if goal unreachable."""
    if start == goal:
        return [start]
    if goal not in parent:
        return None

    cur = goal
    path = [cur]
    while cur != start:
        cur = parent[cur]
        path.append(cur)
    path.reverse()
    return path


def bfs_path(grid: Grid, start: Pos, goal: Pos) -> Tuple[Optional[List[Pos]], Set[Pos]]:
    """
    Queue-based BFS.
    Return (path, visited).
    - path is a list of positions from start to goal (inclusive), or None.
    - visited contains all explored/seen nodes.
    """
    q = deque([start])
    visited: Set[Pos] = {start}
    parent: Dict[Pos, Pos] = {}

    while q:
        cur = q.popleft()
        if cur == goal:
            break
        for nxt in neighbors(grid, cur):
            if nxt in visited:
                continue
            visited.add(nxt)
            parent[nxt] = cur
            q.append(nxt)

    return reconstruct_path(parent, start, goal), visited


def dfs_path(grid: Grid, start: Pos, goal: Pos) -> Tuple[Optional[List[Pos]], Set[Pos]]:
    """
    Stack-based DFS (iterative, no recursion).
    Return (path, visited).
    """
    stack: List[Pos] = [start]
    visited: Set[Pos] = {start}
    parent: Dict[Pos, Pos] = {}

    while stack:
        cur = stack.pop()
        if cur == goal:
            break
        for nxt in neighbors(grid, cur):
            if nxt in visited:
                continue
            visited.add(nxt)
            parent[nxt] = cur
            stack.append(nxt)

    return reconstruct_path(parent, start, goal), visited


def render(grid: Grid, path: Optional[List[Pos]] = None, visited: Optional[Set[Pos]] = None) -> str:
    """
    Render the grid as text.
    Overlay rules (recommended):
    - path tiles shown as '*'
    - visited tiles shown as '·' (middle dot) or '+'
    - preserve 'S' and 'G'
    """
    canvas = [row[:] for row in grid]
    visited = visited or set()
    path = path or []

    for r, c in visited:
        if canvas[r][c] == ".":
            canvas[r][c] = "+"

    for r, c in path:
        if canvas[r][c] in {".", "+"}:
            canvas[r][c] = "*"

    return "\n".join("".join(row) for row in canvas)


def run_one(label: str, grid_text: str) -> None:
    grid, start, goal = parse_grid(grid_text)

    print("=" * 60)
    print(label)
    print("- Raw map")
    print(render(grid))

    path_bfs, visited_bfs = bfs_path(grid, start, goal)
    print("\n- BFS")
    print(f"found={path_bfs is not None} path_len={(len(path_bfs) if path_bfs else None)} visited={len(visited_bfs)}")
    print(render(grid, path=path_bfs, visited=visited_bfs))

    path_dfs, visited_dfs = dfs_path(grid, start, goal)
    print("\n- DFS")
    print(f"found={path_dfs is not None} path_len={(len(path_dfs) if path_dfs else None)} visited={len(visited_dfs)}")
    print(render(grid, path=path_dfs, visited=visited_dfs))


def parse_monster_map(text: str) -> GameState:
    rows = [list(line) for line in text.splitlines() if line.strip()]
    player = monster = goal = None
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "P":
                player = (r, c)
                rows[r][c] = "."
            elif ch == "M":
                monster = (r, c)
                rows[r][c] = "."
            elif ch == "G":
                goal = (r, c)
    if player is None or monster is None:
        raise ValueError("Monster map needs P and M")
    return GameState(rows, player, monster, goal)


def game_loop(mode: str = "BFS") -> None:
    """Turn-based monster chase demo. Player uses WASD, monster uses BFS/DFS path each turn."""
    state = parse_monster_map(MONSTER_MAP)
    moves = {"w": (-1, 0), "a": (0, -1), "s": (1, 0), "d": (0, 1)}
    finder = bfs_path if mode.upper() == "BFS" else dfs_path

    print("\n" + "=" * 60)
    print(f"Monster Chase Mode: {mode.upper()}")
    print("Move with WASD, q to quit.")

    while True:
        display = [row[:] for row in state.grid]
        pr, pc = state.player
        mr, mc = state.monster
        display[pr][pc] = "P"
        display[mr][mc] = "M"
        print(render(display))

        if state.goal and state.player == state.goal:
            print("You reached the exit. You win!")
            return
        if state.player == state.monster:
            print("The monster caught you. Game over.")
            return

        cmd = input("Your move (W/A/S/D, q=quit): ").strip().lower()
        if cmd == "q":
            print("Quit game.")
            return
        if cmd not in moves:
            print("Invalid move.")
            continue

        dr, dc = moves[cmd]
        nr, nc = state.player[0] + dr, state.player[1] + dc
        if 0 <= nr < len(state.grid) and 0 <= nc < len(state.grid[0]) and state.grid[nr][nc] != "#":
            state.player = (nr, nc)

        path_to_player, _ = finder(state.grid, state.monster, state.player)
        if path_to_player and len(path_to_player) > 1:
            state.monster = path_to_player[1]


def main() -> None:
    run_one("Example Map 1", EXAMPLE_MAP_1)
    run_one("Example Map 2", EXAMPLE_MAP_2)
    run_one("Example Map 3 (DFS longer than BFS)", EXAMPLE_MAP_3)
    print("\nTip: run game_loop('BFS') or game_loop('DFS') from a Python shell for Monster Chase.")


if __name__ == "__main__":
    main()
