UNKNOWN = 3
FILLED = 1
EMPTY = 2


class Nonogram:
	def __init__(self):
		self.colnum = 0
		self.rownum = 0
		self.col_clues = []
		self.row_clues = []
		self.max_col_clues = 1
		self.max_row_clues = 1
		self.board = []

	def load(self, filename):
		with open(filename, "r") as f:
			lines = f.readlines()

		self.colnum, self.rownum = map(int, lines[0].split())
		self.col_clues = []
		self.row_clues = []
		self.max_col_clues = 1
		self.max_row_clues = 1

		for i in range(1, self.colnum + 1):
			c = list(map(int, lines[i].split()))
			self.col_clues.append(c)
			self.max_col_clues = max(self.max_col_clues, len(c))

		for i in range(self.colnum + 1, self.colnum + self.rownum + 1):
			c = list(map(int, lines[i].split()))
			self.row_clues.append(c)
			self.max_row_clues = max(self.max_row_clues, len(c))

		self.board = [[UNKNOWN] * self.colnum for _ in range(self.rownum)]

	def reset(self):
		self.board = [[UNKNOWN] * self.colnum for _ in range(self.rownum)]
