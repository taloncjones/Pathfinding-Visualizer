import logging
import copy

LOGGER = logging.getLogger(__name__)


class Dijkstra:
    def __init__(self, grid, start, end):
        self.grid = copy.deepcopy(grid)
        try:
            self.rows = len(grid)
            self.cols = len(grid[0])
        except TypeError:
            raise TypeError(
                'Invalid grid for dijkstra(), expect list of lists')
        self.start = start
        self.end = end
        self.finished = False

        self.create_distance_grid()

    # Converts self.grid into a distance grid
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
        r, c = self.end
        self.grid[r][c] = float('inf')

    # Finds minimum distance vertex from dist not already in shortest path tree
    def min_distance(self, sptMatrix):
        min_path = float('inf')

        for r in range(self.rows):
            for c in range(self.cols):
                if 0 <= self.grid[r][c] < min_path and sptMatrix[r][c] == False:
                    min_path = self.grid[r][c]
                    min_index = (r, c)

        return min_index

    # Main function for finding shortest path
    def dijkstra(self):
        sptMatrix = [[False for _ in range(self.cols)]
                     for _ in range(self.rows)]

        for _ in range(self.rows * self.cols):
            min_r, min_c = self.min_distance(sptMatrix)
            # LOGGER.debug('New Minimum. R: {}\tC: {}'.format(min_r, min_c))

            if (min_r, min_c) == self.end:
                self.finished = True
                LOGGER.debug('Finished!')
                return

            sptMatrix[min_r][min_c] = True

            for r, c in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                test_r, test_c = min_r + r, min_c + c

                # Check if test indexes are out of bounds
                if not (0 <= test_r < self.rows) or not (0 <= test_c < self.cols):
                    continue

                if self.grid[test_r][test_c] > 0 and \
                        not sptMatrix[test_r][test_c] and \
                        self.grid[test_r][test_c] > self.grid[min_r][min_c] + 1:
                    self.grid[test_r][test_c] = self.grid[min_r][min_c] + 1

        return
