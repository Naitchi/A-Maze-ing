from typing import Optional


VALID_KEYS = {
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
    "SEED",
}


def read_config(file_name: str) -> tuple[dict[str, str], list[str]]:
    """Read raw key=value pairs from config file."""

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
                        f"Ligne {line_number} invalide : '{line}' "
                        f"(format attendu : KEY=value)"
                    )
                    continue

                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()

                if not key:
                    errors.append(f"Ligne {line_number} invalide : clé vide")
                    continue

                if key in config:
                    errors.append(f"Clé dupliquée : {key}")
                    continue

                if key not in VALID_KEYS:
                    errors.append(f"Clé inconnue : {key}")
                    continue

                if value == "":
                    errors.append(f"Valeur vide pour la clé : {key}")
                    continue

                config[key] = value

    except FileNotFoundError:
        return {}, [f"Fichier de configuration introuvable : {file_name}"]

    return config, errors


def parse_positive_int(
    config: dict[str, str],
    key: str,
    errors: list[str],
) -> Optional[int]:
    """Parse a strictly positive integer."""

    if key not in config:
        errors.append(f"Clé manquante : {key}")
        return None

    try:
        value = int(config[key])
    except ValueError:
        errors.append(f"{key} doit être un entier")
        return None

    if value <= 0:
        errors.append(f"{key} doit être > 0")
        return None

    return value


def parse_non_negative_int(
    config: dict[str, str],
    key: str,
    errors: list[str],
) -> Optional[int]:
    """Parse a non-negative integer."""

    if key not in config:
        errors.append(f"Clé manquante : {key}")
        return None

    try:
        value = int(config[key])
    except ValueError:
        errors.append(f"{key} doit être un entier")
        return None

    if value < 0:
        errors.append(f"{key} doit être >= 0")
        return None

    return value


def parse_coord(
    config: dict[str, str],
    key: str,
    errors: list[str],
) -> Optional[tuple[int, int]]:
    """Parse coordinates formatted as x,y."""

    if key not in config:
        errors.append(f"Clé manquante : {key}")
        return None

    raw_value = config[key]
    parts = raw_value.split(",")

    if len(parts) != 2:
        errors.append(f"{key} doit être au format x,y")
        return None

    try:
        x = int(parts[0].strip())
        y = int(parts[1].strip())
    except ValueError:
        errors.append(f"{key} doit contenir deux entiers")
        return None

    if x < 0 or y < 0:
        errors.append(f"{key} doit contenir des coordonnées >= 0")
        return None

    return (x, y)


def parse_output_file(
    config: dict[str, str],
    errors: list[str],
) -> Optional[str]:
    """Parse output file name."""

    key = "OUTPUT_FILE"

    if key not in config:
        errors.append(f"Clé manquante : {key}")
        return None

    output_file = config[key].strip()

    if not output_file.endswith(".txt"):
        errors.append("OUTPUT_FILE doit se terminer par .txt")
        return None

    if output_file == ".txt":
        errors.append("OUTPUT_FILE doit contenir un nom avant .txt")
        return None

    return output_file


def parse_bool(
    config: dict[str, str],
    key: str,
    errors: list[str],
) -> Optional[bool]:
    """Parse boolean written as True or False."""

    if key not in config:
        errors.append(f"Clé manquante : {key}")
        return None

    value = config[key].strip()

    if value == "True":
        return True
    if value == "False":
        return False

    errors.append(f"{key} doit valoir True ou False")
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
            errors.append("ENTRY est en dehors du labyrinthe")

    if exit_pos is not None:
        x, y = exit_pos
        if not (0 <= x < width and 0 <= y < height):
            errors.append("EXIT est en dehors du labyrinthe")

    if entry is not None and exit_pos is not None and entry == exit_pos:
        errors.append("ENTRY et EXIT ne peuvent pas être identiques")


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
        errors.append("Le fichier de configuration est vide")

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
