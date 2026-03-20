import random
import dikjstra

Coord = tuple[int, int]
Direction = tuple[int, int]
Maze = list[list[int]]


class MazeGenerator:
    def __init__(self, width, height, start, end, seed=None):
        self.width = width
        self.start = start
        self.end = end
        self.height = height
        self.in_linking = []
        self.not_linked = []
        self.fortytwo = []
        self.linked = []
        self.maze = []
        self.seed = seed

    def get_available_direction(
        self,
        old_coord: Coord
    ) -> list[Direction] | None:
        """Return available neighbor directions from a cell.

        Args:
            old_coord: Current cell coordinates.
            in_linking: Cells in the current temporary path.
            fortytwo: Forbidden cells that must not be used.

        Returns:
            A list of valid directions, or None if none are possible.
        """

        i, j = old_coord
        directions: list[Direction] = []
        for d_i, d_j in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            o = i + d_i
            k = j + d_j
            if (
                o >= 0
                and o < self.height
                and k >= 0
                and k < self.width
                and (o, k) not in self.fortytwo
                and (o, k) not in self.in_linking
            ):
                directions.append((d_i, d_j))
        if len(directions) == 0:
            return None
        return directions

    def build_fortytwo(self) -> list[Coord]:
        """Build centered coordinates for the forbidden 42 pattern.

        Args:
            height: Maze height in cells.
            width: Maze width in cells.

        Returns:
            The list of forbidden coordinates for the pattern.
        """

        pattern = [
            "1010111",
            "1010001",
            "1110111",
            "0010100",
            "0010111",
        ]

        pattern_height = len(pattern)
        pattern_width = len(pattern[0])
        if self.height < pattern_height + 3 or self.width < pattern_width + 3:
            print("Impossible d'imprimer un 42 au milieu du maze")
            # TODO francais fine ou pas ?
            return []

        start_i = (self.height - pattern_height) // 2
        start_j = (self.width - pattern_width) // 2
        blocked: list[Coord] = []

        for d_i, row in enumerate(pattern):
            for d_j, pixel in enumerate(row):
                if pixel == "1":
                    blocked.append((start_i + d_i, start_j + d_j))
        return blocked

    def create_path(self) -> None:
        """Carve passages along a temporary path and merge it into linked."""

        m = 0
        while m < len(self.in_linking) - 1:
            case1 = self.in_linking[m]
            case2 = self.in_linking[m + 1]
            self.linked.append(case1)
            i, j = case1
            o, k = case2
            d_i = o - i
            d_j = k - j
            if d_i == 0 and d_j == 1:
                self.maze[i][j] &= ~(1 << 1)
                self.maze[o][k] &= ~(1 << 3)
            elif d_i == 0 and d_j == -1:
                self.maze[i][j] &= ~(1 << 3)
                self.maze[o][k] &= ~(1 << 1)
            elif d_i == 1 and d_j == 0:
                self.maze[i][j] &= ~(1 << 2)
                self.maze[o][k] &= ~(1 << 0)
            elif d_i == -1 and d_j == 0:
                self.maze[i][j] &= ~(1 << 0)
                self.maze[o][k] &= ~(1 << 2)
            m += 1

    def advance_path_step(self, i: int, j: int) -> tuple[int, int, bool]:
        """Advance one random step and connect path if it reaches linked.

        Returns:
            New row, new column, and whether the path got connected.
        """

        directions = self.get_available_direction((i, j))
        if directions is None:
            return i, j, False

        d_i, d_j = random.choice(directions)
        i += d_i
        j += d_j

        if (i, j) in self.linked:
            self.in_linking.append((i, j))
            self.create_path()
            for case in self.in_linking[:-1]:
                if case in self.not_linked:
                    self.not_linked.remove(case)
            self.in_linking.clear()
            return i, j, True

        return i, j, False

    def draw_a_path(self) -> None:
        """Draw and connect a random path from an unlinked cell."""

        self.in_linking = []

        i = random.randint(0, self.height - 1)
        j = random.randint(0, self.width - 1)

        if (i, j) not in self.fortytwo and (i, j) not in self.linked:
            while True:
                self.in_linking.append((i, j))
                if (
                    self.get_available_direction((i, j))
                    is None
                ):
                    return
                else:
                    i, j, is_path_connected = self.advance_path_step(i, j)
                    if is_path_connected:
                        return

    def maze_generator(self) -> None:
        """
        Generate and print a maze with an centered 42 forbidden area if
        enough space.

        Args:
            width: Maze width in cells.
            height: Maze height in cells.
            start: Starting cell coordinates.
            seed: Optional random seed.
        """

        maze = [[15 for _ in range(self.width)] for _ in range(self.height)]

        if self.seed is not None:
            random.seed(self.seed)

        self.not_linked: list[Coord] = [
            (i, j) for i in range(self.height) for j in range(self.width)
        ]
        self.linked: list[Coord] = []
        self.fortytwo: list[Coord] = self.build_fortytwo()

        (a, b) = self.start
        self.not_linked.remove((a, b))
        self.linked.append((a, b))

        for case in self.fortytwo:
            if case in self.not_linked:
                self.not_linked.remove(case)

        while len(self.not_linked):
            self.draw_a_path()

        print_maze(maze)

        print(maze)
        dikjstra.dikjstra(maze, (0, 0), (149, 149))

# TODO verifier que ca soit un maze perfect quand demander
# TODO verifier que ca soit un maze imperfect quand demander
# TODO s'assurer qu'il n'y a pas de 3x3 libre


maze_generator = MazeGenerator(30, 30, (0, 0), (29, 29))
maze_generator.maze_generator()


def print_maze(maze: Maze) -> None:
    """Print the maze as ASCII art."""

    for line in maze:
        top = ""
        middle = ""
        bottom = ""

        for case in line:
            haut = (case >> 0) & 1
            droite = (case >> 1) & 1
            bas = (case >> 2) & 1
            gauche = (case >> 3) & 1

            top += " --- " if haut else "     "
            middle += "|" if gauche else " "
            middle += "   "
            middle += "|" if droite else " "
            bottom += " --- " if bas else "     "
        print(top)
        print(middle)
        print(bottom)

# TODO mettre tout dans une classe
