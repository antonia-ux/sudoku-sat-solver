# Sudoku SAT Solver

This project encodes Sudoku puzzles as SAT problems and solves them using DPLL, DP, and Resolution algorithms.

## Usage
```bash
python solve.py --method DPLL --input puzzle.txt
python solve.py --method DP --input puzzle.txt
python solve.py --method Resolution --input puzzle.txt

Compare Methods
python solve.py --compare --input puzzle.txt
