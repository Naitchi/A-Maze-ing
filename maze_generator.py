import random
from dikjstra import dikjstra

Coord = tuple[int, int]
Direction = tuple[int, int]
Maze = list[[int]]


class MazeGenerator:
    def __init__(
        self,
        width: int,
        height: int,
        start: Coord,
        end: Coord,
        output_file: str,
        perfect: bool,
        seed: int | None = None,
    ) -> None:
        self.width: int = width
        self.height: int = height
        self.start: Coord = start
        print(self.start)
        self.end: Coord = end
        print(self.end)
        self.output_file = output_file
        self.perfect = perfect
        self.seed: int | None = seed
        self.in_linking: list[Coord] = []
        self.not_linked: list[Coord] = []
        self.fortytwo: list[Coord] = []
        self.linked: list[Coord] = []
        self.maze: Maze = [[15 for _ in range(width)] for _ in range(height)]
        self.maze_generator()
        self.path: str = dikjstra(self.maze, self.start, self.end)

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

        pattern_height: int = len(pattern)
        pattern_width: int = len(pattern[0])
        if self.height < pattern_height + 3 or self.width < pattern_width + 3:
            print("Impossible d'imprimer un 42 au milieu du maze")
            return []

        start_i: int = (self.height - pattern_height) // 2
        start_j: int = (self.width - pattern_width) // 2
        blocked: list[Coord] = []

        for d_i, row in enumerate(pattern):
            for d_j, pixel in enumerate(row):
                if pixel == "1":
                    blocked.append((start_i + d_i, start_j + d_j))
        return blocked

    def create_path(self) -> None:
        """Carve passages along a temporary path and merge it into linked."""

        m: int = 0
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

    def wall_bits_between(
        self,
        case1: Coord,
        case2: Coord,
    ) -> tuple[int, int] | None:
        """Return wall bits for two orthogonal adjacent cells."""

        i, j = case1
        o, k = case2
        direction_to_bits: dict[Direction, tuple[int, int]] = {
            (0, 1): (1, 3),
            (0, -1): (3, 1),
            (1, 0): (2, 0),
            (-1, 0): (0, 2),
        }
        return direction_to_bits.get((o - i, k - j))

    def remove_wall_between(self, case1: Coord, case2: Coord) -> bool:
        """Remove the shared wall if it exists and cells are adjacent."""

        bits = self.wall_bits_between(case1, case2)
        if bits is None:
            return False

        i, j = case1
        o, k = case2
        bit_1, bit_2 = bits
        if not (self.maze[i][j] & (1 << bit_1)):
            return False

        self.maze[i][j] &= ~(1 << bit_1)
        self.maze[o][k] &= ~(1 << bit_2)
        return True

    def is_open_3x3_at(self, top_i: int, top_j: int) -> bool:
        """Return True if the 3x3 block at top-left is fully opened."""

        right_open = all(
            not (self.maze[i][j] & (1 << 1))
            for i in range(top_i, top_i + 3)
            for j in range(top_j, top_j + 2)
        )
        down_open = all(
            not (self.maze[i][j] & (1 << 2))
            for i in range(top_i, top_i + 2)
            for j in range(top_j, top_j + 3)
        )
        return right_open and down_open

    def has_open_3x3_space(self) -> bool:
        """Return True if at least one fully open 3x3 block exists."""

        return any(
            self.is_open_3x3_at(top_i, top_j)
            for top_i in range(self.height - 2)
            for top_j in range(self.width - 2)
        )

    def can_remove_wall_without_3x3(self, case1: Coord, case2: Coord) -> bool:
        """Check if wall removal would avoid creating an open 3x3."""

        i, j = case1
        o, k = case2
        old_case1 = self.maze[i][j]
        old_case2 = self.maze[o][k]

        if not self.remove_wall_between(case1, case2):
            return False

        creates_3x3 = self.has_open_3x3_space()
        self.maze[i][j] = old_case1
        self.maze[o][k] = old_case2
        return not creates_3x3

    def is_inner_non_fortytwo(self, case: Coord) -> bool:
        """Return True if case is inside borders and outside fortytwo."""

        i, j = case
        return (
            0 < i < self.height - 1
            and 0 < j < self.width - 1
            and case not in self.fortytwo
        )

    def get_inner_wall_candidates(self) -> list[tuple[Coord, Coord]]:
        """List unique interior neighboring pairs eligible for removal."""

        candidates: list[tuple[Coord, Coord]] = []
        for i in range(1, self.height - 1):
            for j in range(1, self.width - 1):
                case1 = (i, j)
                if not self.is_inner_non_fortytwo(case1):
                    continue

                for case2 in ((i, j + 1), (i + 1, j)):
                    if self.is_inner_non_fortytwo(case2):
                        candidates.append((case1, case2))

        return candidates

    def remove_random_inner_walls(self, wall_count: int) -> int:
        """Remove random interior walls without fortytwo and open 3x3."""

        if wall_count <= 0:
            return 0

        candidates = self.get_inner_wall_candidates()
        random.shuffle(candidates)

        removed = 0
        for case1, case2 in candidates:
            if removed >= wall_count:
                break

            if not self.can_remove_wall_without_3x3(case1, case2):
                continue

            if self.remove_wall_between(case1, case2):
                removed += 1

        return removed

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

    def parsing_start_end_in_forty_two(self):
        print(self.fortytwo)
        print(self.start)
        if self.start in self.fortytwo or self.end in self.fortytwo:
            print("error")

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

        if self.seed is not None:
            random.seed(self.seed)

        self.not_linked: list[Coord] = [
            (i, j) for i in range(self.height) for j in range(self.width)
        ]
        self.linked: list[Coord] = []
        self.fortytwo: list[Coord] = self.build_fortytwo()
        self.parsing_start_end_in_forty_two()

        (a, b) = self.start
        self.not_linked.remove((a, b))
        self.linked.append((a, b))

        for case in self.fortytwo:
            if case in self.not_linked:
                self.not_linked.remove(case)

        while len(self.not_linked):
            self.draw_a_path()

        if not self.perfect:
            self.remove_random_inner_walls((self.width * self.height) / 10)