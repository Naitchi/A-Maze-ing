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
        self.img = img
        self.maze = maze
        self.rend_data = rend_data
        self.set_ppc()

    def set_ppc(self):
        img_size = min(self.img.width, self.img.height)
        maze_size = max(self.maze.width, self.maze.height)
        self.rend_data.ppc = img_size // maze_size

    def put_pixel(self, offset, color) -> None:
        self.img.data[offset: offset + 4] = color.to_bytes(4, 'little')

    def offset_finder(self, x, y):
        return (y * self.img.sl + x * self.img.bpp) // 8

    def clear_image(self):
        self.img.data[:] = b'\x00' * len(self.img.data)

    def render_cell(self, col, row, color):
        ppc = self.rend_data.ppc
        for dy in range(ppc):
            for dx in range(ppc):
                offset = self.offset_finder(col * ppc + dx, row * ppc + dy)
                self.put_pixel(offset, color)

    def render_maze(self):
        for row in range(self.maze.height):
            for col in range(self.maze.width):
                cell = self.maze.grid[row][col]
                if cell.is_wall:
                    color = self.rend_data.color
                elif cell.is_entry:
                    color = self.rend_data.entry_color
                elif cell.is_exit:
                    color = self.rend_data.exit_color
                else:
                    color = 0xFF000000
                self.render_cell(col, row, color)

    def render_path(self):
        if not self.rend_data.show_path:
            return
        for cell in self.maze.path:
            self.render_cell(cell.col, cell.row, self.rend_data.path_color)

    def push(self, window_width: int) -> None:
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
        self.push(self.img.width)
