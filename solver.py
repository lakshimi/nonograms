from nonogram import FILLED, EMPTY, UNKNOWN


class NonogramSolver:
	def __init__(self, puzzle, on_row_update=None, on_col_update=None):
		self.puzzle = puzzle
		self.on_row_update = on_row_update
		self.on_col_update = on_col_update

	# ---- Constraint propagation solver (SolveN from C++) ----

	def solve_constraint(self):
		step = None
		for step in self.solve_constraint_steps():
			pass
		return step is not None and step[0] == 'solved'

	def solve_constraint_steps(self):
		puzzle = self.puzzle
		total_check = sum(sum(clue) for clue in puzzle.col_clues)
		last_check = 0
		row_check = [0] * puzzle.rownum
		col_check = [0] * puzzle.colnum

		while last_check < total_check:
			checked = 0
			for i in range(puzzle.rownum):
				c = self._check_row(i)
				changed = c != row_check[i]
				if changed:
					row_check[i] = c
				yield ('row', i, changed)
			for i in range(puzzle.colnum):
				c = self._check_col(i)
				changed = c != col_check[i]
				if changed:
					col_check[i] = c
				checked += c
				yield ('col', i, changed)
			if last_check == checked:
				yield ('failed',)
				return
			last_check = checked
		yield ('solved',)

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

	# ---- Combined solver: constraint propagation + trial backtracking ----

	def solve_full_steps(self):
		puzzle = self.puzzle

		# Phase 1: constraint propagation
		for step in self.solve_constraint_steps():
			if step[0] == 'solved':
				yield step
				return
			if step[0] == 'failed':
				break
			yield step

		# Phase 2: trial backtracking for remaining unknowns
		unknowns = [
			(i, j)
			for i in range(puzzle.rownum)
			for j in range(puzzle.colnum)
			if puzzle.board[i][j] == UNKNOWN
		]
		if not unknowns:
			yield ('solved',)
			return

		if self._trial_backtrack():
			revealed = set()
			for row, col in unknowns:
				if row not in revealed:
					revealed.add(row)
					yield ('row', row, True)
			yield ('solved',)
		else:
			yield ('failed',)

	def _trial_backtrack(self):
		puzzle = self.puzzle
		cell = self._find_unknown()
		if cell is None:
			return True

		row, col = cell
		saved = [r[:] for r in puzzle.board]

		for value in [FILLED, EMPTY]:
			puzzle.board = [r[:] for r in saved]
			puzzle.board[row][col] = value
			if self._propagate_silent():
				if self._trial_backtrack():
					return True

		puzzle.board = [r[:] for r in saved]
		return False

	def _propagate_silent(self):
		puzzle = self.puzzle
		progress = True
		while progress:
			progress = False
			for i in range(puzzle.rownum):
				old = puzzle.board[i][:]
				self._check_row(i)
				if 0 in puzzle.board[i]:
					return False
				if old != puzzle.board[i]:
					progress = True
			for i in range(puzzle.colnum):
				old = [puzzle.board[j][i] for j in range(puzzle.rownum)]
				self._check_col(i)
				new = [puzzle.board[j][i] for j in range(puzzle.rownum)]
				if 0 in new:
					return False
				if old != new:
					progress = True
		return True

	def _find_unknown(self):
		puzzle = self.puzzle
		for i in range(puzzle.rownum):
			for j in range(puzzle.colnum):
				if puzzle.board[i][j] == UNKNOWN:
					return (i, j)
		return None

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
