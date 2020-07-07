import logging

LOGGER = logging.getLogger(__name__)


class Dijkstra:
    def __init__(self, grid, start, end):
        self.grid = grid
        try:
            self.rows = len(grid)
            self.cols = len(grid[0])
        except TypeError:
            raise TypeError('Invalid grid for dijkstra(), expect list of lists')
        self.start = start
        self.end = end
        self.finished = False

        self.create_distance_grid()

    # Creates new grid with distance values from self.grid
    # Float('inf') for unvisited, -1 for walls, 0 for start
    def create_distance_grid(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] is None:
                    self.grid[r][c] = float('inf')
                else:
                    self.grid[r][c] = -1

        r, c = self.start
        self.grid[r][c] = 0

    # Finds minimum distance vertex from dist not already in shortest path tree
    def min_distance(self, dist, sptMatrix):
        min_path = float('inf')

        for r in range(self.rows):
            for c in range(self.cols):
                if dist[r][c] < min_path and sptMatrix[r][c] == False:
                    min_path = dist[r][c]
                    min_index = (r, c)

        return min_index

    def dijkstra(self):
        return