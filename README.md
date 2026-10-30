# Queens Game

A Python implementation of the LinkedIn Queens puzzle game with step-by-step solver visualization and interactive play mode. This is a student project implementing both a playable game UI and an educational algorithm visualization.

## Game Rules

Place one queen per row, column, and coloured region. No two queens can be adjacent, including diagonally (8-way adjacency check).

## Features

- **Interactive Play Mode**: manually solve puzzles with undo, redo, and conflict detection
- **Solver Visualization**: watch a backtracking algorithm solve puzzles step-by-step
- **Default Puzzle**: one built-in hand-crafted level
- **Visual Feedback**: coloured regions, conflict highlighting in red, timer
- **Win Detection**: automatic puzzle completion recognition

## Installation

```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python main.py
```

This launches the pygame window with the built-in puzzle.

## Controls

### Play Mode
- **Left click** on cell: cycle through empty → X mark → queen → empty
- **Right click** on cell: toggle X mark (to mark cells you've ruled out)
- **Undo** button: revert the last move
- **Solve** button: watch the solver visualization
- **Menu** button: return to level selection

### Solver Visualization
- **Next** button: advance one solving step
- **Play/Pause** button: auto-play through all steps or pause
- **Reset** button: restart the solver from the beginning
- **Back** button: return to menu

## Algorithm

### Solver (Backtracking)

Complexity: exponential worst-case, but heavily pruned by constraints.

### Default Puzzle

The game uses one hand-crafted 5x5 puzzle defined by `get_default_level()` in
`queens/board.py`. The solver can verify that it is solvable.
