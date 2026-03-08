import sys
from nonogram import Nonogram
from solver import NonogramSolver
from game import Game, select_puzzle

PUZZLE_DIR = "./puzzles"


if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = select_puzzle(PUZZLE_DIR)
		if filename is None:
			print(f"No .txt files found in {PUZZLE_DIR}/")
			sys.exit(1)

	puzzle = Nonogram()
	puzzle.load(filename)

	solver = NonogramSolver(puzzle)
	game = Game(puzzle, solver)
	game.run()
