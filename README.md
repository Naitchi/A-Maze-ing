*This project has been created as part of the 42 curriculum by ndi-tull, bclairot.*

# A-Maze-ing

## Description

This project implements a maze generator in Python. It reads a configuration file,
generates a maze (optionally perfect, with a single path between entry and exit), and
writes it to a file using a hexadecimal wall representation. It also provides a visual
renderer and keeps the generation logic reusable.

## Instructions

### Installation

```bash
make setup      # Create the venv
make install    # Install dependencies
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

We used **Recursive Backtracking** (Depth-First Search) to generate the maze.

### How it works

Recursive Backtracking is a carving algorithm that starts from a cell and randomly explores neighboring unvisited cells. When it reaches a dead-end, it backtracks to the last cell with unvisited neighbors and continues exploring. This creates a continuous path through all cells without creating loops, resulting in a perfect maze (if enabled).

### Why this algorithm?

Recursive Backtracking was chosen because:
- **Perfect Mazes**: Generates mazes without loops, guaranteeing a unique solution path
- **Simple Implementation**: Straightforward to understand and implement with random choices
- **Flexibility**: Easily adaptable for creating non-perfect mazes by removing random interior walls
- **Visual Quality**: Creates visually interesting mazes with good aesthetic properties

## Maze Pathfinding Algorithm

We implemented Dijkstra's algorithm to solve the maze and find the shortest path from the entry to the exit.

### How it works

Dijkstra's algorithm assigns a distance score to each cell in the maze, starting from the entry point with a score of 0. It then explores neighboring cells, updating their distances as it discovers shorter paths. The algorithm continues until it reaches the exit, guaranteeing the shortest path in the process.

### Why this algorithm?

Dijkstra's algorithm was chosen because:
- **Optimality**: It guarantees the shortest path solution
- **Efficiency**: Performs well on mazes with uniform step costs
- **Simplicity**: Straightforward to implement and understand
- **Reliability**: Well-tested and proven for pathfinding problems


## Reusable Code

The reusable part of this project is the `MazeGenerator` class, which can be imported and used in other Python projects to generate mazes and compute a shortest path between two points.

### Installation

No extra installation is required when using the project source directly.

### Import

```python
from maze_generator import MazeGenerator
```

### Example

```python
from maze_generator import MazeGenerator

maze = MazeGenerator(
	width=20,
	height=15,
	start=(0, 0),
	end=(19, 14),
	output_file="maze.txt",
	perfect=True,
	seed=42,
)

print(maze.maze)  # hexadecimal grid
print(maze.path)  # shortest path
```

---

## Team & Project Management

### Roles

| Member | Role |
|--------|------|
| `<bclairot>` | Implemented maze generation (Recursive Backtracking), shortest-path solving (Dijkstra), and algorithm integration with exported output |
| `<ndi-tull>` | Implemented configuration parsing/validation, file I/O flow, and rendering/display pipeline with MLX |

### Planning

We split the work to move faster and keep responsibilities clear: one focused on configuration parsing and rendering, while the other implemented the maze generation and pathfinding algorithms. We coordinated regularly to align interfaces and integrate both parts smoothly.

### What worked well

- Clear task split between algorithm development and parsing/rendering
- Regular communication helped with integration and reduced blockers
- Incremental testing made debugging easier during implementation
- Type hints improved readability and maintenance

### What could be improved

- Add more automated tests (unit and integration)
- Improve error handling and user-facing messages
- Refactor some modules to reduce coupling
- Expand documentation with architecture and design decisions

### Tools used

Yes, we used several specific tools during the project:

- **Python 3** for implementation
- **Makefile** commands (`make setup`, `make install`, `make run`, `make debug`)
- **MLX (`mlx` wheel)** for maze rendering
- **flake8** for style checks
- **mypy** for static type checking
- **Git/GitHub** for version control and collaboration
- **AI assistant tools** for README writing support and type hint improvements

---

## Resources

### Maze Generation
- Jamis Buck, *Mazes for Programmers* (Pragmatic Bookshelf)
- HandWiki: Recursive Backtracker — https://handwiki.org/wiki/Maze_generation_algorithm
- Wikipedia: Maze generation algorithm — https://en.wikipedia.org/wiki/Maze_generation_algorithm

### Documentation
- Python docs (typing) — https://docs.python.org/3/library/typing.html
- Python docs (random) — https://docs.python.org/3/library/random.html
- MiniLibX Python wheel (`mlx`) reference — https://pypi.org/project/mlx/

### AI Usage

AI tools were used to improve the README and add type hints.