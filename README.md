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

## Project Structure

```
queens/
  __init__.py
  board.py           Core board model: Level (regions), BoardState (queens/marks), conflict detection
  solver.py          Backtracking solver with step-by-step generation
  game.py            GameSession: player interaction, undo/redo, timer
  ui/
    __init__.py
    app.py           Main pygame application and event loop
    renderer.py      Drawing logic: board, queens, marks, regions, UI elements
    scenes.py        Scene classes: Menu, Play, Solver visualization, Win screen

tests/
  test_board.py      28 tests for Level and BoardState
  test_solver.py     18 tests for Solver and step generation
  test_game.py       21 tests for GameSession

main.py             Entry point for the game
requirements.txt    Dependencies (pygame)
README.md           This file
CLAUDE.md           Project documentation and development guidelines
```

## Testing

Run all tests:
```bash
python -m unittest discover tests
```

Run a specific test module:
```bash
python -m unittest tests.test_board
```

Total: 106 unit tests covering all core components.

## Algorithm

### Solver (Backtracking)

The solver implements row-by-row backtracking with constraint-based pruning:

1. **Row-by-row processing**: tries to place one queen in each row
2. **Constraint checking**: before placing, verifies:
   - Column not already occupied
   - Region doesn't already have a queen
   - No adjacent queens (8-way: orthogonal + diagonal)
3. **Backtracking**: if a row has no valid placements, undoes the previous placement and tries alternatives
4. **Step generation**: each placement or backtrack is recorded as a `Step` for visualization

Complexity: exponential worst-case, but heavily pruned by constraints.

### Default Puzzle

The game uses one hand-crafted 5x5 puzzle defined by `get_default_level()` in
`queens/board.py`. The solver can verify that it is solvable.