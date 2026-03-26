from parsing_config import load_config
from maze_generator import MazeGenerator
from render import App


def main():
    config = load_config("config.txt")

    maze = MazeGenerator(
        config["width"],
        config["height"],
        config["entry"],
        config["exit"],
        config["output_file"],
        config["perfect"],
        config["seed"],
    )

    app = App(maze)
    app.run()


if __name__ == "__main__":
    main()
