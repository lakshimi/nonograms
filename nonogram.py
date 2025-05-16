import pygame
import sys
import time
from hints import *

#----- definitions -----
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
CELL_SIZE = 20

#----- NemoLogic class -----
class NemoLogic:
	def __init__(self, filename):
		self.board = []
		self.row_clues = []
		self.col_clues = []
		self.load_puzzle(filename)

	def load_puzzle(self, filename):
		with open(filename, "r") as file:
			lines = file.readlines()
		
		self.colnum = int(lines[0].split()[0])
		self.rownum = int(lines[0].split()[1])

		self.col_clues = [list(map(int, line.split())) for line in lines[1:self.colnum+1]]
		self.row_clues = [list(map(int, line.split())) for line in lines[self.colnum+1:self.colnum+self.rownum+1]]
		
		self.board = [[None for _ in range(self.colnum)] for _ in range(self.rownum)]  # 빈 보드

	def solve(self):
		""" 간단한 백트래킹 알고리즘을 사용하여 네모로직 풀이 """
		# 현재는 빈 보드를 무조건 다 채우는 예제이므로, 실제 로직을 적용하려면 더 복잡한 알고리즘 필요
		for i in range(self.rownum):
			for j in range(self.colnum):
				self.board[i][j] = 1  # 임시로 모든 셀을 채움

#----- Game class -----
class Game:
	def __init__(self, puzzle):
		pygame.init()
		self.nemo = puzzle
		width = puzzle.colnum*CELL_SIZE
		height = puzzle.rownum*CELL_SIZE
		self.screen = pygame.display.set_mode((width, height))
		pygame.display.set_caption("NemoLogic Puzzle")
		self.running = True
		self.font = pygame.font.Font(None, 24)

	def draw_grid(self):
		for i in range(self.nemo.rownum + 1):
			pygame.draw.line(self.screen, BLACK, (50, 50 + i * CELL_SIZE), 
				(50 + self.nemo.colnum * CELL_SIZE, 50 + i * CELL_SIZE))
		for j in range(self.nemo.colnum + 1):
			pygame.draw.line(self.screen, BLACK, (50 + j * CELL_SIZE, 50), 
				(50 + j * CELL_SIZE, 50 + self.nemo.rownum * CELL_SIZE))

	def draw_clues(self):
		for i, clues in enumerate(self.nemo.row_clues):
			clue_text = " ".join(map(str, clues))
			text_surface = self.font.render(clue_text, True, BLACK)
			self.screen.blit(text_surface, (5, 50 + i * CELL_SIZE + 10))
		
		for j, clues in enumerate(self.nemo.col_clues):
			clue_text = " ".join(map(str, clues))
			text_surface = self.font.render(clue_text, True, BLACK)
			self.screen.blit(text_surface, (55 + j * CELL_SIZE, 5))

	def draw_board(self):
		for i in range(self.nemo.rownum):
			for j in range(self.nemo.colnum):
				x, y = 50 + j * CELL_SIZE, 50 + i * CELL_SIZE
				if self.nemo.board[i][j] == 1:
					pygame.draw.rect(self.screen, DARK_GRAY, (x, y, CELL_SIZE, CELL_SIZE))
				pygame.draw.rect(self.screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1)

	def run(self):
		while self.running:
			self.screen.fill(WHITE)
			self.draw_grid()
			self.draw_clues()
			self.draw_board()

			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False

		pygame.quit()
		sys.exit()

#----- main -----
if __name__ == "__main__":
	if len(sys.argv) > 1:
		puzzle_name = sys.argv[1]
	else:
		puzzle_name = input("puzzle name: ")
	puzzle = NemoLogic(puzzle_name)
	game = Game(puzzle)
	game.run()
