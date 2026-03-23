*This project has been created as part of the 42 curriculum by ndi-tull, bclairot.*

# A-Maze-ing

## Description

<!-- Présente le projet, son objectif et un aperçu général -->

## Instructions

### Requirements

<!-- Liste des dépendances nécessaires -->

### Installation

```bash
make setup      # Crée l'environnement virtuel
make install    # Installe les dépendances
```

### Usage

```bash
make run FILE=config.txt
```

### Debug

```bash
make debug FILE=config.txt
```

---

## Configuration File Format

<!-- Structure complète et format du fichier de config -->

The configuration file must contain one `KEY=VALUE` pair per line.
Lines starting with `#` are comments and are ignored.

| Key | Description | Example |
|-----|-------------|---------|
| WIDTH | Maze width (number of cells) | `WIDTH=20` |
| HEIGHT | Maze height | `HEIGHT=15` |
| ENTRY | Entry coordinates (x,y) | `ENTRY=0,0` |
| EXIT | Exit coordinates (x,y) | `EXIT=19,14` |
| OUTPUT_FILE | Output filename | `OUTPUT_FILE=maze.txt` |
| PERFECT | Is the maze perfect? | `PERFECT=True` |

Example config file:
```
# Maze configuration
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
```

---

## Maze Generation Algorithm

<!-- Nom de l'algorithme choisi -->

### Why this algorithm?

<!-- Pourquoi vous avez choisi cet algorithme -->

---

## Reusable Code

<!-- Quelle partie du code est réutilisable et comment -->

### Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Example

```python
from mazegen import Maze

maze = Maze(width=20, height=15, seed=42, entry=(0,0), exit=(19,14))
maze.generate()

print(maze.grid)    # grille de valeurs hex
print(maze.path)    # chemin solution
```

---

## Team & Project Management

### Roles

| Member | Role |
|--------|------|
| `<login1>` | <!-- rôle --> |
| `<login2>` | <!-- rôle --> |

### Planning

<!-- Planning prévu et comment il a évolué -->

### What worked well

<!-- Ce qui a bien fonctionné -->

### What could be improved

<!-- Ce qui pourrait être amélioré -->

### Tools used

<!-- Outils spécifiques utilisés -->

---

## Resources

<!-- Références classiques liées au sujet -->

### Maze Generation
-
-

### Documentation
-
-

### AI Usage

<!-- Comment l'IA a été utilisée, pour quelles tâches et quelles parties du projet -->