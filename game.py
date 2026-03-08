import os
import pygame
import sys
from nonogram import UNKNOWN, FILLED, EMPTY
from hints import render_vertical_numbers, render_horizontal_numbers

CELL_SIZE = 20

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
LIGHT_GRAY = (220, 220, 220)
HOVER_COLOR = (230, 240, 255)

SOLVED_COLOR = (0, 128, 80)

CELL_COLORS = {
	UNKNOWN: LIGHT_GRAY,
	FILLED: BLACK,
	EMPTY: WHITE,
}


def select_puzzle(puzzle_dir):
	files = sorted(f for f in os.listdir(puzzle_dir) if f.endswith(".txt"))
	if not files:
		return None

	pygame.init()
	item_height = 36
	padding = 20
	title_height = 50
	width = 400
	height = title_height + len(files) * item_height + padding * 2
	screen = pygame.display.set_mode((width, height))
	pygame.display.set_caption("Select Puzzle")
	font = pygame.font.SysFont(None, 28)
	title_font = pygame.font.SysFont(None, 34)
	clock = pygame.time.Clock()

	selected = None
	while selected is None:
		mouse_pos = pygame.mouse.get_pos()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				for i in range(len(files)):
					y = title_height + padding + i * item_height
					if y <= mouse_pos[1] < y + item_height:
						selected = os.path.join(puzzle_dir, files[i])

		screen.fill(WHITE)
		title = title_font.render("Select Puzzle", True, BLACK)
		screen.blit(title, (width // 2 - title.get_width() // 2, 12))
		pygame.draw.line(screen, GRAY, (0, title_height - 2), (width, title_height - 2))

		for i, f in enumerate(files):
			y = title_height + padding + i * item_height
			rect = pygame.Rect(0, y, width, item_height)
			if rect.collidepoint(mouse_pos):
				pygame.draw.rect(screen, HOVER_COLOR, rect)
			label = font.render(f"  {i + 1}. {os.path.splitext(f)[0]}", True, BLACK)
			screen.blit(label, (padding, y + (item_height - label.get_height()) // 2))

		pygame.display.flip()
		clock.tick(30)

	return selected


class Game:
	def __init__(self, puzzle, solver=None):
		pygame.init()
		self.puzzle = puzzle
		self.solver = solver
		self.margin_left = puzzle.max_row_clues * CELL_SIZE
		self.margin_top = puzzle.max_col_clues * CELL_SIZE
		width = self.margin_left + puzzle.colnum * CELL_SIZE
		height = self.margin_top + puzzle.rownum * CELL_SIZE
		self.screen = pygame.display.set_mode((width, height))
		pygame.display.set_caption("Nonogram Puzzle")
		self.running = True
		self.solver_gen = None
		self.solving = False
		self.solved = False
		self.step_interval = 100
		self.last_step_time = 0

	def start_solving(self):
		if self.solver:
			self.puzzle.reset()
			self.solver_gen = self.solver.solve_full_steps()
			self.solving = True
			self.solved = False
			self.last_step_time = pygame.time.get_ticks()

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
				if self.solved and cell == FILLED:
					color = SOLVED_COLOR
				else:
					color = CELL_COLORS.get(cell, WHITE)
				pygame.draw.rect(
					self.screen, color, (x + 1, y + 1, CELL_SIZE - 1, CELL_SIZE - 1))

	def run(self):
		clock = pygame.time.Clock()
		self.start_solving()

		while self.running:
			now = pygame.time.get_ticks()

			if self.solving and now - self.last_step_time >= self.step_interval:
				try:
					while True:
						step = next(self.solver_gen)
						if step[0] in ('solved', 'failed'):
							self.solving = False
							self.solved = (step[0] == 'solved')
							break
						if step[2]:
							break
				except StopIteration:
					self.solving = False
				self.last_step_time = now

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_q:
						self.running = False
					elif event.key == pygame.K_r:
						self.start_solving()

			self.screen.fill(WHITE)
			self.draw_grid()
			self.draw_clues()
			self.draw_board()
			pygame.display.flip()
			clock.tick(60)

		pygame.quit()
		sys.exit()
