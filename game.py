import pygame
import sys
from nonogram import UNKNOWN, FILLED, EMPTY
from hints import render_vertical_numbers, render_horizontal_numbers

CELL_SIZE = 20

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (220, 220, 220)

CELL_COLORS = {
	UNKNOWN: LIGHT_GRAY,
	FILLED: BLACK,
	EMPTY: WHITE,
}


class Game:
	def __init__(self, puzzle):
		pygame.init()
		self.puzzle = puzzle
		self.margin_left = puzzle.max_row_clues * CELL_SIZE
		self.margin_top = puzzle.max_col_clues * CELL_SIZE
		width = self.margin_left + puzzle.colnum * CELL_SIZE
		height = self.margin_top + puzzle.rownum * CELL_SIZE
		self.screen = pygame.display.set_mode((width, height))
		pygame.display.set_caption("Nonogram Puzzle")
		self.running = True

	def draw_grid(self):
		ml, mt = self.margin_left, self.margin_top
		w = self.puzzle.colnum * CELL_SIZE
		h = self.puzzle.rownum * CELL_SIZE
		for i in range(self.puzzle.rownum + 1):
			y = mt + i * CELL_SIZE
			pygame.draw.line(self.screen, BLACK, (ml, y), (ml + w, y))
		for j in range(self.puzzle.colnum + 1):
			x = ml + j * CELL_SIZE
			pygame.draw.line(self.screen, BLACK, (x, mt), (x, mt + h))

	def draw_clues(self):
		ml, mt = self.margin_left, self.margin_top
		num_w, num_h = 15, 9
		cx = (CELL_SIZE - num_w) // 2
		cy = (CELL_SIZE - num_h) // 2

		for i, clues in enumerate(self.puzzle.row_clues):
			x = ml - CELL_SIZE + cx
			y = mt + i * CELL_SIZE + cy
			render_horizontal_numbers(self.screen, x, y, CELL_SIZE, clues)

		for j, clues in enumerate(self.puzzle.col_clues):
			x = ml + j * CELL_SIZE + cx
			y = mt - CELL_SIZE + cy
			render_vertical_numbers(self.screen, x, y, CELL_SIZE, clues)

	def draw_board(self):
		ml, mt = self.margin_left, self.margin_top
		for i in range(self.puzzle.rownum):
			for j in range(self.puzzle.colnum):
				x = ml + j * CELL_SIZE
				y = mt + i * CELL_SIZE
				cell = self.puzzle.board[i][j]
				color = CELL_COLORS.get(cell, WHITE)
				pygame.draw.rect(
					self.screen, color, (x + 1, y + 1, CELL_SIZE - 1, CELL_SIZE - 1))

	def run(self):
		clock = pygame.time.Clock()
		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_q:
						self.running = False

			self.screen.fill(WHITE)
			self.draw_grid()
			self.draw_clues()
			self.draw_board()
			pygame.display.flip()
			clock.tick(30)

		pygame.quit()
		sys.exit()
