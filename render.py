from mlx import Mlx
from typing import Any
from mazegen import Maze


class ImgData:
    def __init__(self) -> None:
        self.img = None
        self.width = 0
        self.height = 0
        self.data: bytearray = bytearray()
        self.bpp = 0
        self.sl = 0


class RenderConfig:
    def __init__(self):
        self.color = 0xffffff
        self.ppc = 0
        self.show_path = False
        self.entry_color = 0xFF00FF00
        self.exit_color = 0xFFFF0000
        self.path_color = 0xFFE0E0E0
        self.menu_color = 0xFF2C3E50

    def change_color(self):
        colors = [
            0xFFFF0000,
            0xFF00FF00,
            0xFF0000FF,
            0xFFFFFF00,
            0xFFFF00FF,
            0xFF00FFFF,
            0xFFFF8800,
            0xFF88FF00,
            0xFF0088FF,
            0xFFFFFFFF
        ]
        i = colors.index(self.color)
        self.color = colors[(i + 1) % len(colors)]


class Display:
    def __init__(self,
                 mlx: Mlx,
                 mlx_ptr: Any,
                 window: Any,
                 img: ImgData,
                 maze: Maze,
                 rend_data: RenderConfig) -> None:
        self.mlx = mlx
        self.mlx_ptr = mlx_ptr
        self.window = window
        self.img: ImgData = img
        self.maze = maze
        self.rend_data = rend_data
        self.set_ppc()

    def set_ppc(self):  # Calcul le nombre de pixel qu'on a par cellule du maze
        img_size = min(self.img.width, self.img.height)
        maze_size = max(self.maze.width, self.maze.height)
        self.rend_data.ppc = img_size // maze_size

    def put_pixel(self, offset, color) -> None:  # Ecrit chaque octet du pixel
        self.img.data[offset: offset + 4] = color.to_bytes(4, 'little')

    # Trouve le pixel exacte qu'on doit print -> on skip chaque ligne + chaque
    # pixel dans la ligne
    def offset_finder(self, x, y):
        return (y * self.img.sl + x * self.img.bpp) // 8

    def clear_image(self):  # Mets chaque pixel en noir pour clear l'image
        self.img.data[:] = b'\x00' * len(self.img.data)

    # Va recuperer la base qui est le debut de notre cellule en haut a gauche,
    # puis va regarder la valeur envoyer depuis la grille du maze et regarder
    # le binaire pour savoir quel mur doit etre rempli ou non
    def render_walls(self, col, row, value):
        ppc = self.rend_data.ppc
        color = self.rend_data.color
        opp = self.img.bpp // 8

        base = self.offset_finder(col * ppc, row * ppc)

        if value & 1:  # North
            for dx in range(ppc):
                self.put_pixel(base + dx * opp, color)
        if value & 2:  # East
            for dy in range(ppc):
                self.put_pixel(base + dy * self.img.sl +
                               (ppc - 1) * opp, color)

        if value & 4:  # South
            for dx in range(ppc):
                self.put_pixel(base + (ppc - 1) *
                               self.img.sl + dx * opp, color)
        if value & 8:  # West
            for dy in range(ppc):
                self.put_pixel(base + dy * self.img.sl, color)

    # Si une valeur dans la grille est de 15 tu remplis toute la cellule (42
    # pattern)
    def render_cell(self, col, row, color):

        ppc = self.rend_data.ppc
        for dy in range(ppc):
            for dx in range(ppc):
                offset = self.offset_finder(col * ppc + dx, row * ppc + dy)
                self.put_pixel(offset, color)

    # On va recuperer chaque valeur de la grille, recuperer sa position dans
    # le maze et appeller la fonction qui va print les murs
    def render_maze(self):
        for i, value in enumerate(self.maze.grid):
            col = i % self.maze.width
            row = i // self.maze.width
            if value == 15:
                self.render_cell(col, row, self.rend_data.color)
            else:
                self.render_walls(col, row, value)

    # Fonction qui va print le chemin de solution sur l'image
    def render_path(self):
        if not self.rend_data.show_path:
            return
        current = self.maze.entry
        for direction in self.maze.path[:-1]:
            current = self.next_step(direction, current)
            self.render_cell(current[0], current[1], self.rend_data.path_color)

    # Va recup la position ou on est + la direction ou on va
    def next_step(direction: str, current: tuple) -> tuple:
        x, y = current
        moves = {
            "E": (x + 1, y),
            "S": (x, y + 1),
            "W": (x - 1, y),
            "N": (x, y - 1)
        }
        return moves[direction]

    def image_to_window(self, window_width: int) -> None:
        # Calcul la marge entre coin et debut du maze
        pos_x = (window_width - self.rend_data.ppc * self.maze.width) // 2

        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr,
            self.window,
            self.img.img,
            pos_x,
            50
        )

    def draw_entry_exit(self) -> None:
        entry_x, entry_y = self.maze.entry
        self.render_cell(entry_x, entry_y, self.rend_data.entry_color)

        exit_x, exit_y = self.maze.exit
        self.render_cell(exit_x, exit_y, self.rend_data.exit_color)

    def draw_all(self) -> None:
        self.clear_image()
        self.render_maze()
        self.draw_entry_exit()
        if self.rend_data.show_path:
            self.render_path()
        self.image_to_window(self.img.width)
