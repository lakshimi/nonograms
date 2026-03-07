from nonogram import FILLED, EMPTY, UNKNOWN


class NonogramSolver:
	def __init__(self, puzzle, on_row_update=None, on_col_update=None):
		self.puzzle = puzzle
		self.on_row_update = on_row_update
		self.on_col_update = on_col_update

	# ---- Constraint propagation solver (SolveN from C++) ----

	def solve_constraint(self):
		puzzle = self.puzzle
		total_check = sum(sum(clue) for clue in puzzle.col_clues)
		last_check = 0
		row_check = [0] * puzzle.rownum
		col_check = [0] * puzzle.colnum

		while last_check < total_check:
			checked = 0
			for i in range(puzzle.rownum):
				c = self._check_row(i)
				if c != row_check[i]:
					if self.on_row_update:
						self.on_row_update(i)
					row_check[i] = c
			for i in range(puzzle.colnum):
				c = self._check_col(i)
				if c != col_check[i]:
					if self.on_col_update:
						self.on_col_update(i)
					col_check[i] = c
				checked += c
			if last_check == checked:
				return False
			last_check = checked
		return True

	def _check_row(self, row):
		puzzle = self.puzzle
		result = self._check_line(
			puzzle.row_clues[row], puzzle.colnum, puzzle.board[row])
		return result

	def _check_col(self, col):
		puzzle = self.puzzle
		line = [puzzle.board[i][col] for i in range(puzzle.rownum)]
		result = self._check_line(puzzle.col_clues[col], puzzle.rownum, line)
		for i in range(puzzle.rownum):
			puzzle.board[i][col] = line[i]
		return result

	def _check_line(self, clues, length, line):
		effective = clues if clues != [0] else []
		num_clues = len(effective)
		total = sum(effective)
		s = length - total - num_clues + 1

		r = [0] * length
		u = [0] * (num_clues + 1)
		t = [0] * length
		p = 0
		c = 0

		while True:
			if c == num_clues:
				while p < length:
					t[p] = EMPTY
					p += 1
				u[c] = s
				s = 0

				if all(t[i] & line[i] for i in range(length)):
					for i in range(length):
						r[i] |= t[i]

				while True:
					s += u[c]
					p -= u[c]
					u[c] = 0
					c -= 1
					if c < 0:
						break
					p -= effective[c] + (1 if c != 0 else 0)
					if s > 0:
						break

				if c < 0:
					count = 0
					for i in range(length):
						line[i] = r[i]
						if r[i] == FILLED:
							count += 1
					return count

				p -= u[c]
				u[c] += 1
				s -= 1

			gap = u[c] + (1 if c != 0 else 0)
			for _ in range(gap):
				t[p] = EMPTY
				p += 1
			for _ in range(effective[c]):
				t[p] = FILLED
				p += 1
			c += 1

	# ---- Backtracking solver (Solve from C++) ----

	def solve_backtrack(self):
		puzzle = self.puzzle
		puzzle.reset()
		self._set_first_pattern(0)
		phase = 0

		while True:
			if self._check_pattern(phase):
				if self.on_row_update:
					self.on_row_update(phase)
				phase += 1
				if phase == puzzle.rownum:
					return True
				self._set_first_pattern(phase)
				continue
			while not self._set_next_pattern(phase):
				phase -= 1
				if phase < 0:
					return False

	def _set_first_pattern(self, row):
		puzzle = self.puzzle
		puzzle.board[row] = [EMPTY] * puzzle.colnum
		pos = 0
		for clue in puzzle.row_clues[row]:
			for _ in range(clue):
				puzzle.board[row][pos] = FILLED
				pos += 1
			pos += 1

	def _set_next_pattern(self, row):
		puzzle = self.puzzle
		s = puzzle.board[row]
		clues = puzzle.row_clues[row]
		colnum = puzzle.colnum

		pos = []
		in_block = False
		for i in range(colnum):
			if not in_block and s[i] == FILLED:
				in_block = True
				pos.append(i)
			if s[i] != FILLED:
				in_block = False

		k = len(pos)

		c = -1
		for i in range(k):
			t = pos[i]
			for j in range(i, k):
				t += clues[j] + 1
			if t <= colnum:
				c = i

		if c == -1:
			return False

		for i in range(pos[c], colnum):
			s[i] = EMPTY

		idx = pos[c] + 1
		for ci in range(c, k):
			for _ in range(clues[ci]):
				s[idx] = FILLED
				idx += 1
			idx += 1

		return True

	def _check_pattern(self, row):
		puzzle = self.puzzle
		if row >= puzzle.rownum:
			return False

		for i in range(puzzle.colnum):
			col_clues = puzzle.col_clues[i]
			count = 0
			k = 0
			for j in range(row + 1):
				if puzzle.board[j][i] == FILLED:
					count += 1
				elif count > 0:
					if k >= len(col_clues) or count != col_clues[k]:
						return False
					count = 0
					k += 1

			clue_k = col_clues[k] if k < len(col_clues) else 0

			if row == puzzle.rownum - 1 and count != clue_k:
				return False
			if count > clue_k:
				return False

			needed = row - count
			for ki in range(k, len(col_clues)):
				needed += col_clues[ki] + 1
			if needed > puzzle.rownum:
				return False

		return True
