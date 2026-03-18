def can_move(maze, i, j, o, k, d_i, d_j):
    current_cell = maze[i][j]
    next_cell = maze[o][k]

    if d_i == 0 and d_j == 1:
        return ((current_cell >> 2) & 1) == 0 and ((next_cell >> 0) & 1) == 0
    if d_i == 0 and d_j == -1:
        return ((current_cell >> 0) & 1) == 0 and ((next_cell >> 2) & 1) == 0
    if d_i == 1 and d_j == 0:
        return ((current_cell >> 1) & 1) == 0 and ((next_cell >> 3) & 1) == 0
    if d_i == -1 and d_j == 0:
        return ((current_cell >> 3) & 1) == 0 and ((next_cell >> 1) & 1) == 0
    return False


def propagate_scores(maze, scores, i, j):
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


def dikjstra(maze, start, width, height):
    scores = [[-1 for _ in range(width)] for _ in range(height)]
    i, j = start
    scores[i][j] = 0

    propagate_scores(maze, scores, i, j)

    print("Scores:")
    for line in scores:
        print(line)
