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


def maze_generator(width, height, start, end, seed=None):
    # TODO faire une verification si y'a la place de mettre un 42 ou non (si non kick une erreur dans la console)
    maze = [[15 for _ in range(width)] for _ in range(height)]

    if seed:
        random.seed(seed)

    not_linked = [(i, j) for i in range(width) for j in range(height)]
    in_linking = []
    linked = []
    fortytwo = []

    (a, b) = start
    maze[a][b] = 0

    while len(not_linked):  # tant qu'on a pas check toutes les cases
        i = random.randint(0, height)
        j = random.randint(0, width)
        if (i, j) in not_linked:
            # tant qu'on est sur une case qu'on a pas visite
            in_linking.append((i, j))
            d_i, d_j = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            i += d_i
            j += d_j
            if i >= 0 and i <= height and j >= 0 and j <= width and (i, j) not in fortytwo:
                if (a, b) in not_linked:
                    
            else:
                i -= d_i
                j -= d_j

    print_maze(maze)


maze_generator(4, 4, (0, 0), (4, 4))
