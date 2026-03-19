import random
import dikjstra

Coord = tuple[int, int]
Direction = tuple[int, int]
Maze = list[list[int]]


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


def get_available_direction(
    old_coord: Coord,
    in_linking: list[Coord],
    fortytwo: list[Coord],
    height: int,
    width: int,
) -> list[Direction] | None:
    """Return available neighbor directions from a cell.

    Args:
        old_coord: Current cell coordinates.
        in_linking: Cells in the current temporary path.
        fortytwo: Forbidden cells that must not be used.
        height: Maze height in cells.
        width: Maze width in cells.

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
            and o < height
            and k >= 0
            and k < width
            and (o, k) not in fortytwo
            and (o, k) not in in_linking
        ):
            directions.append((d_i, d_j))
    if len(directions) == 0:
        return None
    return directions


def build_fortytwo(height: int, width: int) -> list[Coord]:
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
    if height < pattern_height + 3 or width < pattern_width + 3:
        return []  # TODO faut que je mette un message d'erreur pour ça

    start_i = (height - pattern_height) // 2
    start_j = (width - pattern_width) // 2
    blocked: list[Coord] = []

    for d_i, row in enumerate(pattern):
        for d_j, pixel in enumerate(row):
            if pixel == "1":
                blocked.append((start_i + d_i, start_j + d_j))
    return blocked


def create_path(
    maze: Maze,
    in_linking: list[Coord],
    linked: list[Coord],
) -> None:
    """Carve passages along a temporary path and merge it into linked."""

    m = 0
    while m < len(in_linking) - 1:
        case1 = in_linking[m]
        case2 = in_linking[m + 1]
        linked.append(case1)
        i, j = case1
        o, k = case2
        d_i = o - i
        d_j = k - j
        if d_i == 0 and d_j == 1:
            maze[i][j] &= ~(1 << 1)
            maze[o][k] &= ~(1 << 3)
        elif d_i == 0 and d_j == -1:
            maze[i][j] &= ~(1 << 3)
            maze[o][k] &= ~(1 << 1)
        elif d_i == 1 and d_j == 0:
            maze[i][j] &= ~(1 << 2)
            maze[o][k] &= ~(1 << 0)
        elif d_i == -1 and d_j == 0:
            maze[i][j] &= ~(1 << 0)
            maze[o][k] &= ~(1 << 2)
        m += 1


def advance_path_step(
    i: int,
    j: int,
    maze: Maze,
    in_linking: list[Coord],
    linked: list[Coord],
    not_linked: list[Coord],
    fortytwo: list[Coord],
    height: int,
    width: int,
) -> tuple[int, int, bool]:
    """Advance one random step and connect path if it reaches linked.

    Returns:
        New row, new column, and whether the path got connected.
    """

    directions = get_available_direction(
        (i, j),
        in_linking,
        fortytwo,
        height,
        width,
    )
    if directions is None:
        return i, j, False

    d_i, d_j = random.choice(directions)
    i += d_i
    j += d_j

    if (i, j) in linked:
        in_linking.append((i, j))
        create_path(maze, in_linking, linked)
        for case in in_linking[:-1]:
            if case in not_linked:
                not_linked.remove(case)
        in_linking.clear()
        return i, j, True

    return i, j, False


def draw_a_path(
    maze: Maze,
    not_linked: list[Coord],
    linked: list[Coord],
    fortytwo: list[Coord],
    height: int,
    width: int,
) -> None:
    """Draw and connect a random path from an unlinked non-forbidden cell."""

    in_linking: list[Coord] = []

    i = random.randint(0, height - 1)
    j = random.randint(0, width - 1)

    if (i, j) not in fortytwo and (i, j) not in linked:
        while True:
            in_linking.append((i, j))
            if (
                get_available_direction(
                    (i, j),
                    in_linking,
                    fortytwo,
                    height,
                    width,
                )
                is None
            ):
                return
            else:
                i, j, is_path_connected = advance_path_step(
                    i,
                    j,
                    maze,
                    in_linking,
                    linked,
                    not_linked,
                    fortytwo,
                    height,
                    width,
                )
                if is_path_connected:
                    return


def maze_generator(
    width: int,
    height: int,
    start: Coord,
    seed: int | None = None,
) -> None:
    """Generate and print a maze with an optional centered 42 forbidden area.

    Args:
        width: Maze width in cells.
        height: Maze height in cells.
        start: Starting cell coordinates.
        seed: Optional random seed.
    """

    maze = [[15 for _ in range(width)] for _ in range(height)]

    if seed is not None:
        random.seed(seed)

    not_linked: list[Coord] = [
        (i, j) for i in range(height) for j in range(width)
    ]
    linked: list[Coord] = []
    fortytwo: list[Coord] = build_fortytwo(height, width)

    (a, b) = start
    not_linked.remove((a, b))
    linked.append((a, b))

    for case in fortytwo:
        if case in not_linked:
            not_linked.remove(case)

    while len(not_linked):
        draw_a_path(maze, not_linked, linked, fortytwo, height, width)

    print_maze(maze)

    print(maze)
    dikjstra.dikjstra(maze, (0, 0), 15, 15)

# TODO verifier que ca soit un maze perfect quand demander
# TODO verifier que ca soit un maze imperfect quand demander
# TODO s'assurer qu'il n'y a pas de 3x3 libre


maze_generator(15, 15, (0, 0), 42)
