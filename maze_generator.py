import random


def print_maze(maze):
    for line in maze:
        top = ""
        middle = ""
        bottom = ""

        for case in line:
            haut = (case >> 3) & 1
            droite = (case >> 2) & 1
            bas = (case >> 1) & 1
            gauche = case & 1

            top += " --- " if haut else "     "
            middle += "|" if gauche else " "
            middle += "   "
            middle += "|" if droite else " "
            bottom += " --- " if bas else "     "
        print(top)
        print(middle)
        print(bottom)


def get_available_direction(old_coord, in_linking, fortytwo, height, width):
    i, j = old_coord
    directions = []
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


def build_fortytwo(height, width):
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
        return []

    start_i = (height - pattern_height) // 2
    start_j = (width - pattern_width) // 2
    blocked = []

    for d_i, row in enumerate(pattern):
        for d_j, pixel in enumerate(row):
            if pixel == "1":
                blocked.append((start_i + d_i, start_j + d_j))
    return blocked


def create_path(maze, in_linking, linked):
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
            maze[i][j] &= ~(1 << 2)
            maze[o][k] &= ~(1 << 0)
        elif d_i == 0 and d_j == -1:
            maze[i][j] &= ~(1 << 0)
            maze[o][k] &= ~(1 << 2)
        elif d_i == 1 and d_j == 0:
            maze[i][j] &= ~(1 << 1)
            maze[o][k] &= ~(1 << 3)
        elif d_i == -1 and d_j == 0:
            maze[i][j] &= ~(1 << 3)
            maze[o][k] &= ~(1 << 1)
        m += 1


def advance_path_step(
    i,
    j,
    maze,
    in_linking,
    linked,
    not_linked,
    fortytwo,
    height,
    width,
):
    d_i, d_j = random.choice(
        get_available_direction((i, j), in_linking, fortytwo, height, width)
    )
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


def draw_a_path(maze, not_linked, linked, fortytwo, height, width):
    in_linking = []

    i = random.randint(0, height - 1)
    j = random.randint(0, width - 1)

    if (i, j) not in fortytwo and (i, j) not in linked:
        while 1:
            in_linking.append((i, j))
            if (
                get_available_direction(
                    (i, j), in_linking, fortytwo, height, width)
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


def maze_generator(width, height, start, seed=None):
    maze = [[15 for _ in range(width)] for _ in range(height)]

    if seed is not None:
        random.seed(seed)

    not_linked = [(i, j) for i in range(height) for j in range(width)]
    linked = []
    fortytwo = build_fortytwo(height, width)

    (a, b) = start
    not_linked.remove((a, b))
    linked.append((a, b))

    for case in fortytwo:
        if case in not_linked:
            not_linked.remove(case)

    while len(not_linked):
        draw_a_path(maze, not_linked, linked, fortytwo, height, width)

    print_maze(maze)


maze_generator(15, 15, (0, 0), None)
