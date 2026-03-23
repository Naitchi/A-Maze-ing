from maze_generator import Maze
from typing import Any
from mlx import Mlx


class ImgData:
    def __init__(self) -> None:
        self.real_img = None
        self.width = 0
        self.height = 0
        self.data: bytearray = bytearray()
        self.bpp = 0
        self.sl = 0


class RenderConfig:
    def __init__(self):
        self.color = 0xFFFFFFFF
        self.ppc = 0
        self.show_path = False
        self.entry_color = 0xFF00FF00
        self.exit_color = 0xFFFF0000
        self.path_color = 0xFF800080
        self.menu_color = 0xFFFFFFFF

    def next_color(self):
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


class Create_Img:
    def __init__(self,
                 mlx: Mlx,
                 mlx_ptr: Any,
                 window: Any,
                 img: ImgData,
                 maze: Maze,
                 render_config_data: RenderConfig) -> None:
        self.mlx = mlx
        self.mlx_ptr = mlx_ptr
        self.window = window
        self.img: ImgData = img
        self.maze = maze
        self.render_config_data = render_config_data
        self.get_ppc()

    def get_ppc(self):  # Calcul le nombre de pixel qu'on a par cellule du maze
        img_size = min(self.img.width, self.img.height)
        maze_size = max(self.maze.width, self.maze.height)
        self.render_config_data.ppc = img_size // maze_size

    def put_pixel(self, offset, color) -> None:  # Ecrit chaque octet du pixel
        self.img.data[offset: offset + 4] = color.to_bytes(4, 'little')

    # Trouve le pixel exacte qu'on doit print -> on skip chaque ligne + chaque
    # pixel dans la ligne
    def offset_finder(self, x, y):
        return (y * self.img.sl + x * self.img.bpp // 8)

    def clear_image(self):  # Mets chaque pixel en noir pour clear l'image
        self.img.data[:] = b'\x00' * (len(self.img.data))

    # Va recuperer la base qui est le debut de notre cellule en haut a gauche,
    # puis va regarder la valeur envoyer depuis la grille du maze et regarder
    # le binaire pour savoir quel mur doit etre rempli ou non
    def render_walls(self, col, row, value):
        ppc = self.render_config_data.ppc
        color = self.render_config_data.color
        opp = self.img.bpp // 8
        sl = self.img.sl

        base = self.offset_finder(col * ppc, row * ppc)

        if value & 1:  # North
            for dx in range(ppc):
                self.put_pixel(base + dx * opp, color)
        if value & 2:  # East
            for dy in range(ppc):
                self.put_pixel(base + dy * sl +
                               (ppc - 1) * opp, color)

        if value & 4:  # South
            for dx in range(ppc):
                self.put_pixel(base + (ppc - 1) *
                               sl + dx * opp, color)
        if value & 8:  # West
            for dy in range(ppc):
                self.put_pixel(base + dy * sl, color)

    # Si une valeur dans la grille est de 15 tu remplis toute la cellule (42
    # pattern)
    def render_cell(self, col, row, color):
        ppc = self.render_config_data.ppc
        for dy in range(ppc):
            for dx in range(ppc):
                offset = self.offset_finder(col * ppc + dx, row * ppc + dy)
                self.put_pixel(offset, color)

    # On va recuperer chaque valeur de la grille, recuperer sa position dans
    # le maze et appeller la fonction qui va print les murs
    def print_maze(self):
        for row in range(self.maze.height):
            for col in range(self.maze.width):
                value = self.maze.grid[row][col]
                if value == 15:
                    self.render_cell(
                        col, row, self.render_config_data.color)
                else:
                    self.render_walls(col, row, value)

    # Fonction qui va print le chemin de solution sur l'image
    def render_path(self):
        if not self.render_config_data.show_path:
            return
        x, y = self.maze.entry
        for direction in self.maze.path[:-1]:
            x, y = self.next_direction(direction, (x, y))
            if 0 <= x < self.maze.width and 0 <= y < self.maze.height:
                self.render_cell(
                    x, y, self.render_config_data.path_color)

    # Va recup la position ou on est + la direction ou on va
    @staticmethod
    def next_direction(direction: str, current: tuple) -> tuple:
        x, y = current
        moves = {
            "E": (x + 1, y),
            "S": (x, y + 1),
            "W": (x - 1, y),
            "N": (x, y - 1)
        }
        return moves[direction]

    def image_to_window(self, window_width: int) -> None:
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr,
            self.window,
            self.img.real_img,
            100,
            150
        )

    def draw_entry_exit(self) -> None:
        entry_y, entry_x = self.maze.entry
        self.render_cell(
            entry_y,
            entry_x,
            self.render_config_data.entry_color)

        exit_y, exit_x = self.maze.exit
        self.render_cell(
            exit_y,
            exit_x,
            self.render_config_data.exit_color)

    def draw_all(self) -> None:
        self.clear_image()
        self.draw_entry_exit()
        if self.render_config_data.show_path:
            self.render_path()
        self.print_maze()
        self.image_to_window(self.img.width)


class App:
    def __init__(self, maze):
        self.maze = maze
        self.render_config = RenderConfig()
        self.img = ImgData()
        self.m = Mlx()
        self.mlx_ptr = self.m.mlx_init()

        size = max(maze.width, maze.height) * 40
        if size > 1500:
            self.img.height = 1500
            self.img.width = 1500
        else:
            self.img.height = size
            self.img.width = size
        self.img.real_img = self.m.mlx_new_image(
            self.mlx_ptr, self.img.width, self.img.height)
        self.img.data, self.img.bpp, self.img.sl, self.img.iformat = \
            self.m.mlx_get_data_addr(self.img.real_img)

        self.win = self.m.mlx_new_window(
            self.mlx_ptr,
            self.img.width + 200,
            self.img.height + 200,
            "A_Maze_Ing")

        self.renderer = Create_Img(
            self.m, self.mlx_ptr, self.win,
            self.img, self.maze, self.render_config)

    def run(self):
        self.renderer.draw_all()
        self.menu()
        self.m.mlx_key_hook(self.win, self.on_key, self)
        self.m.mlx_loop(self.mlx_ptr)

    def on_key(self, keycode, _):
        actions = {
            49: self.quit,
            50: self.cycle_color,
            51: self.toggle_path,
            52: self.regenerate,
        }
        if keycode in actions:
            actions[keycode]()

    def quit(self):
        self.m.mlx_loop_exit(self.mlx_ptr)

    def menu(self):
        text = "| 1: Close | 2: Color | 3: Path | 4: Regen |"
        text_width = len(text) * 8      # 8px par caractère approximatif
        win_width = self.img.width + 200
        x = (win_width - text_width) // 2
        y = 75
        self.m.mlx_string_put(
            self.mlx_ptr,
            self.win,
            x,
            y,
            self.render_config.menu_color,
            text)

    def cycle_color(self, ):
        self.renderer.clear_image()
        self.render_config.next_color()
        self.renderer.draw_all()

    def toggle_path(self):
        self.render_config.show_path = not self.render_config.show_path
        self.m.mlx_clear_window(self.mlx_ptr, self.win)
        self.menu()
        self.renderer.draw_all()

    def regenerate(self):
        self.maze = Maze(
            self.maze.width,
            self.maze.height,
            None,
            self.maze.entry,
            self.maze.exit,
            self.maze.output_file,
            self.maze.perfect
        )
        self.maze.generatore()
        self.renderer.maze = self.maze
        self.renderer.get_ppc()
        self.m.mlx_clear_window(self.mlx_ptr, self.win)
        self.renderer.draw_all()
        self.menu()


if __name__ == '__main__':
    App(Maze()).run()
