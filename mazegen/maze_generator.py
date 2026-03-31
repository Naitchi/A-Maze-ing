import random
from .dikjstra import dikjstra

Coord = tuple[int, int]
Direction = tuple[int, int]
Maze = list[list[int]]


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
        self.end: Coord = end
        self.output_file = output_file
        self.perfect = perfect
        self.seed: int | None = seed
        self.in_linking: list[Coord] = []
        self.not_linked: list[Coord] = [
            (x, y) for y in range(self.height) for x in range(self.width)
        ]
        self.fortytwo: list[Coord] = self.build_fortytwo()
        self.linked: list[Coord] = []
        self.maze: Maze = [[15 for _ in range(width)] for _ in range(height)]
        self.maze_generator()
        self.path: str = dikjstra(self.maze, self.start, self.end)
        self.write_maze_to_file()

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

        x, y = old_coord
        directions: list[Direction] = []
        for d_x, d_y in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            o = x + d_x
            k = y + d_y
            if (
                o >= 0
                and o < self.width
                and k >= 0
                and k < self.height
                and (o, k) not in self.fortytwo
                and (o, k) not in self.in_linking
            ):
                directions.append((d_x, d_y))
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
            print("Error: Impossible to print "
                  "42 logo in the middle of the maze.")
            return []

        start_x: int = (self.width - pattern_width) // 2
        start_y: int = (self.height - pattern_height) // 2
        blocked: list[Coord] = []

        for d_y, row in enumerate(pattern):
            for d_x, pixel in enumerate(row):
                if pixel == "1":
                    blocked.append((start_x + d_x, start_y + d_y))
        return blocked

    def create_path(self) -> None:
        """Carve passages along a temporary path and merge it into linked."""

        m: int = 0
        while m < len(self.in_linking) - 1:
            case1 = self.in_linking[m]
            case2 = self.in_linking[m + 1]
            self.linked.append(case1)
            x, y = case1
            o, k = case2
            d_x = o - x
            d_y = k - y
            if d_x == 1 and d_y == 0:
                self.maze[y][x] &= ~(1 << 1)
                self.maze[k][o] &= ~(1 << 3)
            elif d_x == -1 and d_y == 0:
                self.maze[y][x] &= ~(1 << 3)
                self.maze[k][o] &= ~(1 << 1)
            elif d_x == 0 and d_y == 1:
                self.maze[y][x] &= ~(1 << 2)
                self.maze[k][o] &= ~(1 << 0)
            elif d_x == 0 and d_y == -1:
                self.maze[y][x] &= ~(1 << 0)
                self.maze[k][o] &= ~(1 << 2)
            m += 1

    def advance_path_step(self, x: int, y: int) -> tuple[int, int, bool]:
        """Advance one random step and connect path if it reaches linked.

        Returns:
            New row, new column, and whether the path got connected.
        """

        directions = self.get_available_direction((x, y))
        if directions is None:
            return x, y, False

        d_x, d_y = random.choice(directions)
        x += d_x
        y += d_y

        if (x, y) in self.linked:
            self.in_linking.append((x, y))
            self.create_path()
            for case in self.in_linking[:-1]:
                if case in self.not_linked:
                    self.not_linked.remove(case)
            self.in_linking.clear()
            return x, y, True

        return x, y, False

    def wall_bits_between(
        self,
        case1: Coord,
        case2: Coord,
    ) -> tuple[int, int] | None:
        """Return wall bits for two orthogonal adjacent cells."""

        x, y = case1
        o, k = case2
        direction_to_bits: dict[Direction, tuple[int, int]] = {
            (1, 0): (1, 3),
            (-1, 0): (3, 1),
            (0, 1): (2, 0),
            (0, -1): (0, 2),
        }
        return direction_to_bits.get((o - x, k - y))

    def remove_wall_between(self, case1: Coord, case2: Coord) -> bool:
        """Remove the shared wall if it exists and cells are adjacent."""

        bits = self.wall_bits_between(case1, case2)
        if bits is None:
            return False

        x, y = case1
        o, k = case2
        bit_1, bit_2 = bits
        if not (self.maze[y][x] & (1 << bit_1)):
            return False

        self.maze[y][x] &= ~(1 << bit_1)
        self.maze[k][o] &= ~(1 << bit_2)
        return True

    def is_open_3x3_at(self, top_x: int, top_y: int) -> bool:
        """Return True if the 3x3 block at top-left is fully opened."""

        right_open = all(
            not (self.maze[y][x] & (1 << 1))
            for y in range(top_y, top_y + 3)
            for x in range(top_x, top_x + 2)
        )
        down_open = all(
            not (self.maze[y][x] & (1 << 2))
            for y in range(top_y, top_y + 2)
            for x in range(top_x, top_x + 3)
        )
        return right_open and down_open

    def has_open_3x3_space(self) -> bool:
        """Return True if at least one fully open 3x3 block exists."""

        return any(
            self.is_open_3x3_at(top_x, top_y)
            for top_y in range(self.height - 2)
            for top_x in range(self.width - 2)
        )

    def can_remove_wall_without_3x3(self, case1: Coord, case2: Coord) -> bool:
        """Check if wall removal would avoid creating an open 3x3."""

        x, y = case1
        o, k = case2
        old_case1 = self.maze[y][x]
        old_case2 = self.maze[k][o]

        if not self.remove_wall_between(case1, case2):
            return False

        creates_3x3 = self.has_open_3x3_space()
        self.maze[y][x] = old_case1
        self.maze[k][o] = old_case2
        return not creates_3x3

    def is_inner_non_fortytwo(self, case: Coord) -> bool:
        """Return True if case is inside borders and outside fortytwo."""

        x, y = case
        return (
            0 < x < self.width - 1
            and 0 < y < self.height - 1
            and case not in self.fortytwo
        )

    def get_inner_wall_candidates(self) -> list[tuple[Coord, Coord]]:
        """List unique interior neighboring pairs eligible for removal."""

        candidates: list[tuple[Coord, Coord]] = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                case1 = (x, y)
                if not self.is_inner_non_fortytwo(case1):
                    continue

                for case2 in ((x + 1, y), (x, y + 1)):
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

        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)

        if (x, y) not in self.fortytwo and (x, y) not in self.linked:
            while True:
                self.in_linking.append((x, y))
                if (
                    self.get_available_direction((x, y))
                    is None
                ):
                    return
                else:
                    x, y, is_path_connected = self.advance_path_step(x, y)
                    if is_path_connected:
                        return

    def parsing_start_end_in_forty_two(self) -> None:
        if self.start in self.fortytwo or self.end in self.fortytwo:
            raise ValueError("Error: start or end is inside the 42 logo.")

    def maze_generator(self) -> None:
        """
        Generate a maze with a centered forbidden 42 area when there is
        enough space.

        Args:
            width: Maze width in cells.
            height: Maze height in cells.
            start: Starting cell coordinates.
            seed: Optional random seed.
        """

        if self.seed is not None:
            random.seed(self.seed)

        try:
            self.parsing_start_end_in_forty_two()
        except ValueError as e:
            print(e)
            exit()

        (a, b) = self.start
        self.not_linked.remove((a, b))
        self.linked.append((a, b))

        for case in self.fortytwo:
            if case in self.not_linked:
                self.not_linked.remove(case)

        while len(self.not_linked):
            self.draw_a_path()

        if not self.perfect:
            self.remove_random_inner_walls(
                int((self.width * self.height) / 10)
            )

    def write_maze_to_file(self) -> None:
        with open(self.output_file, "w") as f:
            for row in self.maze:
                line = "".join(format(cell, "X") for cell in row)
                f.write(line + "\n")
            f.write("\n")
            f.write(f"{self.start[0]},{self.start[1]}\n")
            f.write(f"{self.end[0]},{self.end[1]}\n")
            f.write(self.path + "\n")
