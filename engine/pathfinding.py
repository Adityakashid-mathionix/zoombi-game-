"""
BFS Pathfinding for Zombie maze navigation.
Computes optimal grid steps towards the player while avoiding obstacles and closed doors.
"""
from collections import deque


class PathFinding:
    def __init__(self, game):
        self.game = game
        self.ways = [-1, 0], [0, -1], [1, 0], [0, 1], [-1, -1], [1, -1], [1, 1], [-1, 1]
        self.graph = {}
        self.build_graph()

    def build_graph(self):
        """Construct adjacency graph of walkable tiles."""
        self.graph = {}
        rows = self.game.level_map.rows
        cols = self.game.level_map.cols

        for y in range(rows):
            for x in range(cols):
                if not self.game.level_map.is_wall(x, y):
                    self.graph[(x, y)] = self.graph.get((x, y), []) + self.get_neighbors(x, y)

    def get_neighbors(self, x, y):
        neighbors = []
        for dx, dy in self.ways:
            nx, ny = x + dx, y + dy
            if not self.game.level_map.is_wall(nx, ny):
                # Diagonal obstacle check to prevent cutting corners through walls
                if dx != 0 and dy != 0:
                    if self.game.level_map.is_wall(x + dx, y) or self.game.level_map.is_wall(x, y + dy):
                        continue
                neighbors.append((nx, ny))
        return neighbors

    def bfs(self, start, goal):
        """Breadth-first search finding shortest path from start to goal."""
        queue = deque([start])
        visited = {start: None}

        while queue:
            cur = queue.popleft()
            if cur == goal:
                break
            # Get neighbors from graph or dynamic check
            for nxt in self.get_neighbors(cur[0], cur[1]):
                if nxt not in visited:
                    queue.append(nxt)
                    visited[nxt] = cur
        return visited

    def get_next_step(self, start, goal):
        """Returns the immediate next (x, y) tile along the path from start to goal."""
        if start == goal:
            return start
        visited = self.bfs(start, goal)
        if goal not in visited:
            return start
        # Trace path back from goal
        step = goal
        while visited.get(step) and visited[step] != start:
            step = visited[step]
        return step if step != goal else start
