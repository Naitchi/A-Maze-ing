from typing import Optional


def read_config(file_name: str) -> tuple[dict[str, str], list[str]]:
    """Read raw key=value pairs from config file."""

    valid_keys = {
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
        "SEED",
    }

    config: dict[str, str] = {}
    errors: list[str] = []

    try:
        with open(file_name, "r", encoding="utf-8") as file:
            for line_number, raw_line in enumerate(file, start=1):
                line = raw_line.strip()

                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    errors.append(
                        f"Line {line_number} is invalid: '{line}' "
                        f"(expected format: KEY=value)"
                    )
                    continue

                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()

                if not key:
                    errors.append(f"Line {line_number} is invalid: empty key")
                    continue

                if key in config:
                    errors.append(f"Duplicate key: {key}")
                    continue

                if key not in valid_keys:
                    errors.append(f"Unknown key: {key}")
                    continue

                if value == "":
                    errors.append(f"Empty value for key: {key}")
                    continue

                config[key] = value

    except FileNotFoundError:
        return {}, [f"Configuration file not found: {file_name}"]

    return config, errors


def parse_positive_int(
    config: dict[str, str],
    key: str,
    errors: list[str],
) -> Optional[int]:
    """Parse a strictly positive integer."""

    if key not in config:
        errors.append(f"Missing key: {key}")
        return None

    try:
        value = int(config[key])
    except ValueError:
        errors.append(f"{key} must be an integer")
        return None

    if value <= 0:
        errors.append(f"{key} must be > 0")
        return None

    return value


def parse_non_negative_int(
    config: dict[str, str],
    key: str,
    errors: list[str],
) -> Optional[int]:
    """Parse a non-negative integer."""

    if key not in config:
        errors.append(f"Missing key: {key}")
        return None

    try:
        value = int(config[key])
    except ValueError:
        errors.append(f"{key} must be an integer")
        return None

    if value < 0:
        errors.append(f"{key} must be >= 0")
        return None

    return value


def parse_coord(
    config: dict[str, str],
    key: str,
    errors: list[str],
) -> Optional[tuple[int, int]]:
    """Parse coordinates formatted as x,y."""

    if key not in config:
        errors.append(f"Missing key: {key}")
        return None

    raw_value = config[key]
    parts = raw_value.split(",")

    if len(parts) != 2:
        errors.append(f"{key} must be in x,y format")
        return None

    try:
        x = int(parts[0].strip())
        y = int(parts[1].strip())
    except ValueError:
        errors.append(f"{key} must contain two integers")
        return None

    if x < 0 or y < 0:
        errors.append(f"{key} must contain coordinates >= 0")
        return None

    return (x, y)


def parse_output_file(
    config: dict[str, str],
    errors: list[str],
) -> Optional[str]:
    """Parse output file name."""

    key = "OUTPUT_FILE"

    if key not in config:
        errors.append(f"Missing key: {key}")
        return None

    output_file = config[key].strip()

    if not output_file.endswith(".txt"):
        errors.append("OUTPUT_FILE must end with .txt")
        return None

    if output_file == ".txt":
        errors.append("OUTPUT_FILE must contain a name before .txt")
        return None

    return output_file


def parse_bool(
    config: dict[str, str],
    key: str,
    errors: list[str],
) -> Optional[bool]:
    """Parse boolean written as True or False."""

    if key not in config:
        errors.append(f"Missing key: {key}")
        return None

    value = config[key].strip()

    if value == "True":
        return True
    if value == "False":
        return False

    errors.append(f"{key} must be True or False")
    return None


def validate_coordinates(
    width: Optional[int],
    height: Optional[int],
    entry: Optional[tuple[int, int]],
    exit_pos: Optional[tuple[int, int]],
    errors: list[str],
) -> None:
    """Validate ENTRY and EXIT positions against maze dimensions."""

    if width is None or height is None:
        return

    if entry is not None:
        x, y = entry
        if not (0 <= x < width and 0 <= y < height):
            errors.append("ENTRY is outside the maze")

    if exit_pos is not None:
        x, y = exit_pos
        if not (0 <= x < width and 0 <= y < height):
            errors.append("EXIT is outside the maze")

    if entry is not None and exit_pos is not None and entry == exit_pos:
        errors.append("ENTRY and EXIT cannot be identical")

    if width >= 101 or height >= 101:
        errors.append(
            "WIDTH and HEIGHT can't be more"
            "than a 100 for technical perfomance")


def load_config(file_name: str = "config.txt") -> dict:
    """
    Load, parse and validate config file.

    Returns:
        A dictionary containing validated config values.

    Raises:
        ValueError: If the config contains invalid or missing values.
    """

    config, errors = read_config(file_name)

    if not config and not errors:
        errors.append("The configuration file is empty")

    width = parse_positive_int(config, "WIDTH", errors)
    height = parse_positive_int(config, "HEIGHT", errors)
    entry = parse_coord(config, "ENTRY", errors)
    exit_pos = parse_coord(config, "EXIT", errors)
    output_file = parse_output_file(config, errors)
    perfect = parse_bool(config, "PERFECT", errors)
    seed = parse_non_negative_int(config, "SEED", errors)

    validate_coordinates(width, height, entry, exit_pos, errors)

    if errors:
        raise ValueError("\n".join(errors))

    return {
        "width": width,
        "height": height,
        "entry": entry,
        "exit": exit_pos,
        "output_file": output_file,
        "perfect": perfect,
        "seed": seed,
    }
