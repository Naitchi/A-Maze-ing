Coord = tuple[int, int]
Direction = tuple[int, int]
Maze = list[list[int]]
ScoreGrid = list[list[int]]


def can_move(
    maze: Maze,
    x: int,
    y: int,
    nx: int,
    ny: int,
    d_x: int,
    d_y: int,
) -> bool:
    current_cell = maze[y][x]
    next_cell = maze[ny][nx]

    if d_x == 1 and d_y == 0:
        return ((current_cell >> 1) & 1) == 0 and ((next_cell >> 3) & 1) == 0
    if d_x == -1 and d_y == 0:
        return ((current_cell >> 3) & 1) == 0 and ((next_cell >> 1) & 1) == 0
    if d_x == 0 and d_y == 1:
        return ((current_cell >> 2) & 1) == 0 and ((next_cell >> 0) & 1) == 0
    if d_x == 0 and d_y == -1:
        return ((current_cell >> 0) & 1) == 0 and ((next_cell >> 2) & 1) == 0
    return False


def propagate_scores(maze: Maze, scores: ScoreGrid, x: int, y: int) -> None:
    height = len(maze)
    width = len(maze[0]) if height else 0

    for d_x, d_y in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nx = x + d_x
        ny = y + d_y
        if (
            0 <= nx < width
            and 0 <= ny < height
            and can_move(maze, x, y, nx, ny, d_x, d_y)
        ):
            new_score = scores[y][x] + 1
            if scores[ny][nx] == -1 or new_score < scores[ny][nx]:
                scores[ny][nx] = new_score
                propagate_scores(maze, scores, nx, ny)


def get_path(maze: Maze, scores: ScoreGrid, end: Coord) -> str:
    height = len(scores)
    width = len(scores[0]) if height else 0

    cx, cy = end
    if not (0 <= cx < width and 0 <= cy < height):
        return ""
    if scores[cy][cx] == -1:
        return ""

    cur_score = scores[cy][cx]
    if cur_score == 0:
        return ""

    path: list[str] = []
    while cur_score > 0:
        found: bool = False
        for d_x, d_y in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx = cx + d_x
            ny = cy + d_y
            if 0 <= nx < width and 0 <= ny < height:
                if scores[ny][nx] == cur_score - 1:
                    md_x = cx - nx
                    md_y = cy - ny
                    if not can_move(maze, nx, ny, cx, cy, md_x, md_y):
                        continue
                    move_x = cx - nx
                    move_y = cy - ny
                    if move_x == 1 and move_y == 0:
                        dir_char = 'E'
                    elif move_x == -1 and move_y == 0:
                        dir_char = 'W'
                    elif move_x == 0 and move_y == 1:
                        dir_char = 'S'
                    elif move_x == 0 and move_y == -1:
                        dir_char = 'N'
                    else:
                        return ""
                    path.append(dir_char)
                    cx, cy = nx, ny
                    cur_score -= 1
                    found = True
                    break
        if not found:
            return ""

    path.reverse()
    return ''.join(path)


def dikjstra(maze: Maze, start: Coord, end: Coord) -> str:
    """Compute distance scores from `start` over `maze`.

    Width and height are derived from `maze` to avoid mismatches that
    can cause IndexError when accessing `scores`.
    """
    height = len(maze)
    width = len(maze[0]) if height else 0

    scores: ScoreGrid = [[-1 for _ in range(width)] for _ in range(height)]

    x, y = start
    if not (0 <= x < width and 0 <= y < height):
        raise IndexError(f"start {start} out of maze bounds {(height, width)}")

    scores[y][x] = 0

    propagate_scores(maze, scores, x, y)

    return get_path(maze, scores, end)
