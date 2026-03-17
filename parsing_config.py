from typing import Any, Optional

errors = []


def read_config(file_name: str) -> dict:
    config = {}
    valid_keys = {
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
        "SEED"}

    with open(file_name) as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                errors.append(f"Invalid line {line}")
                continue

            key, sep, value = line.partition("=")
            key = key.strip()
            value = value.strip()

            if key in config:
                errors.append(f"Duplicate key: {key}")
            if key not in valid_keys:
                errors.append(f"Unknown key: {key}")

            config[key] = value

    return config


def width_parsing(config: dict) -> Optional[int]:
    if "WIDTH" not in config:
        errors.append("Missing WIDTH")
        return None

    try:
        width = int(config["WIDTH"])
    except ValueError:
        errors.append("WIDTH must be format WIDTH=x(int)")
        return None

    if width <= 0:
        errors.append("WIDTH must be > 0")
        return None
    return width


def height_parsing(config: dict) -> Optional[int]:
    if "HEIGHT" not in config:
        errors.append("Missing HEIGHT")
        return None

    try:
        height = int(config["HEIGHT"])
    except ValueError:
        errors.append("HEIGHT must be format HEIGHT=x(int)")
        return None

    if height <= 0:
        errors.append("HEIGHT must be > 0")
    return height


def entry_parsing(config: dict) -> Optional[tuple[int, int]]:
    if "ENTRY" not in config:
        errors.append("Missing ENTRY")
        return None

    parts = config["ENTRY"].split(",")

    if len(parts) != 2:
        errors.append("ENTRY must be format ENTRY=x(int), y(int)")
        return None

    try:
        x = int(parts[0])
        y = int(parts[1])
    except ValueError:
        errors.append("ENTRY coordinates must be integers")
        return None

    if x < 0 or y < 0:
        errors.append("ENTRY coordinates must be >= 0")
        return None

    return x, y


def exit_parsing(config: dict) -> Optional[tuple[int, int]]:
    if "EXIT" not in config:
        errors.append("Missing EXIT")
        return None

    parts = config["EXIT"].split(",")

    if len(parts) != 2:
        errors.append("EXIT must be format EXIT=x(int),y(int)")
        return None

    try:
        x = int(parts[0])
        y = int(parts[1])
    except ValueError:
        errors.append("EXIT coordinates must be integers")
        return None

    if x < 0 or y < 0:
        errors.append("EXIT coordinates must be >= 0")
        return None

    return x, y


def output_file_parsing(config: dict) -> Optional[Any]:
    if "OUTPUT_FILE" not in config:
        errors.append("Missing OUTPUT_FILE")
        return None

    output_file = config["OUTPUT_FILE"]

    if not output_file.endswith(".txt"):
        errors.append("OUTPUT_FILE must be format OUTPUT_FILE=name.txt")
        return None

    name = output_file[:-4]
    if not name:
        errors.append("OUTPUT_FILE must contain a file name before .txt")
        return None

    return output_file


def perfect_parsing(config: dict) -> Optional[Any]:
    if "PERFECT" not in config:
        errors.append("Missing PERFECT")
        return None

    perfect = config["PERFECT"]

    if perfect not in ["True", "False"]:
        errors.append("PERFECT must be format PERFECT=False or PERFECT=True")
        return None

    return perfect == "True"


def seed_parsing(config: dict) -> Optional[int]:
    if "SEED" not in config:
        errors.append("Missing SEED")
        return None

    try:
        seed = int(config["SEED"])
    except ValueError:
        errors.append("SEED must be format SEED=x(int)")
        return None

    if seed < 0:
        errors.append("SEED must be >= 0")

    return seed


try:
    config = read_config("config.txt")
except FileNotFoundError:
    print("Config file not found")
    exit(1)

if not config:
    errors.append("Config file is empty")


width = width_parsing(config)
height = height_parsing(config)
entry = entry_parsing(config)
exit_pos = exit_parsing(config)
output_file = output_file_parsing(config)
perfect = perfect_parsing(config)
seed = seed_parsing(config)

data: tuple[Any, Any, Any, Any, Any, Any, Any] = (
    width, height, entry, exit_pos, output_file, perfect, seed)


if entry is not None and width is not None and height is not None:
    x, y = entry
    if not (0 <= x < width and 0 <= y < height):
        errors.append("ENTRY is outside the maze")

if exit_pos is not None and width is not None and height is not None:
    x, y = exit_pos
    if not (0 <= x < width and 0 <= y < height):
        errors.append("EXIT is outside the maze")

if entry is not None and exit_pos is not None and entry == exit_pos:
    errors.append("ENTRY and EXIT cannot be the same")

if errors:
    for error in errors:
        print(error)
    exit(1)
