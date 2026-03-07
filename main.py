import sys
from nonogram import Nonogram
from solver import NonogramSolver
from game import Game


if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = input("puzzle name: ")

	puzzle = Nonogram()
	puzzle.load(filename)

	solver = NonogramSolver(puzzle)
	solved = solver.solve_constraint()

	if not solved:
		print("Constraint propagation failed, trying backtracking...")
		solved = solver.solve_backtrack()

	if solved:
		print("Solved!")
	else:
		print("Could not solve.")

	game = Game(puzzle)
	game.run()
