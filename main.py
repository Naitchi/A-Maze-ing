from parsing_config import load_config
from maze_generator import Maze
from render import App


def main():
    config = load_config("config.txt")

    maze = Maze(
        config["width"],
        config["height"],
        config["seed"],
        config["entry"],
        config["exit"],
        config["output_file"],
        config["perfect"],
    )
    maze.generate()

    app = App(maze)
    app.run()


if __name__ == "__main__":
    main()
