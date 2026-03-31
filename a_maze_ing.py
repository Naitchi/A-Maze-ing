from parsing_config import load_config
from mazegen import MazeGenerator
from render import App
import sys


def main() -> None:
    try:
        if len(sys.argv) == 2:
            config = load_config(sys.argv[1])
        else:
            config = load_config("default_config.txt")

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
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
