Coord = tuple[int, int]
Direction = tuple[int, int]
Maze = list[list[int]]
ScoreGrid = list[list[int]]


def can_move(
    maze: Maze,
    i: int,
    j: int,
    o: int,
    k: int,
    d_i: int,
    d_j: int,
) -> bool:
    current_cell = maze[i][j]
    next_cell = maze[o][k]

    if d_i == 0 and d_j == 1:
        return ((current_cell >> 1) & 1) == 0 and ((next_cell >> 3) & 1) == 0
    if d_i == 0 and d_j == -1:
        return ((current_cell >> 3) & 1) == 0 and ((next_cell >> 1) & 1) == 0
    if d_i == 1 and d_j == 0:
        return ((current_cell >> 2) & 1) == 0 and ((next_cell >> 0) & 1) == 0
    if d_i == -1 and d_j == 0:
        return ((current_cell >> 0) & 1) == 0 and ((next_cell >> 2) & 1) == 0
    return False


def propagate_scores(maze: Maze, scores: ScoreGrid, i: int, j: int) -> None:
    height = len(maze)
    width = len(maze[0]) if height else 0

    for d_i, d_j in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        o = i + d_i
        k = j + d_j
        if (
            0 <= o < height
            and 0 <= k < width
            and can_move(maze, i, j, o, k, d_i, d_j)
        ):
            new_score = scores[i][j] + 1
            if scores[o][k] == -1 or new_score < scores[o][k]:
                scores[o][k] = new_score
                propagate_scores(maze, scores, o, k)


def get_path(maze: Maze, scores: ScoreGrid, end: Coord) -> str:
    height = len(scores)
    width = len(scores[0]) if height else 0

    ci, cj = end
    if not (0 <= ci < height and 0 <= cj < width):
        return ""
    if scores[ci][cj] == -1:
        return ""

    cur_score = scores[ci][cj]
    if cur_score == 0:
        return ""

    path: list[str] = []
    while cur_score > 0:
        found: bool = False
        for d_i, d_j in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            ni = ci + d_i
            nj = cj + d_j
            if 0 <= ni < height and 0 <= nj < width:
                if scores[ni][nj] == cur_score - 1:
                    md_i = ci - ni
                    md_j = cj - nj
                    if not can_move(maze, ni, nj, ci, cj, md_i, md_j):
                        continue
                    move_i = ci - ni
                    move_j = cj - nj
                    if move_i == -1 and move_j == 0:
                        dir_char = 'N'
                    elif move_i == 1 and move_j == 0:
                        dir_char = 'S'
                    elif move_i == 0 and move_j == 1:
                        dir_char = 'E'
                    elif move_i == 0 and move_j == -1:
                        dir_char = 'W'
                    else:
                        return ""
                    path.append(dir_char)
                    ci, cj = ni, nj
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

    i, j = start
    if not (0 <= i < height and 0 <= j < width):
        raise IndexError(f"start {start} out of maze bounds {(height, width)}")

    scores[i][j] = 0

    propagate_scores(maze, scores, i, j)

    return get_path(maze, scores, end)
