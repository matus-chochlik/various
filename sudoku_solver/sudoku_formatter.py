#!/usr/bin/env python
# coding: UTF-8
#  Copyright (c) 2017-2018 Matus Chochlik
from __future__ import print_function

import sys
import fileinput

def get_line_and_rank():
	rank = None
	counter = 0
	for line in fileinput.input():
		if line.strip():
			counter += 1
			row = list()
			if not rank:
				rank = line.count('|') + line.count('+') + 1
				yield line.replace('|', ' ').rstrip(), rank
			else:
				if counter % (rank + 1) == 0:
					assert(line.count('+') + 1 == rank)
				else:
					assert(line.count('|') + 1 == rank)
					yield line.replace('|', ' ').rstrip(), rank
			if counter == (rank*rank + rank - 1):
				counter = 0
				yield None, rank

def get_board_and_rank():
	board = []
	for line, rank in get_line_and_rank():
		if not line:
			if board:
				yield board, rank
			board = []
		else:
			board.append(line.split(' '))

def print_board(board, rank, out):
	d = rank*rank

	for c in xrange(0, d):
		if c == 0:
			out.write("┏━━")
		elif (c + 1) == d:
			out.write("━┓")
		elif (c + 1) % rank == 0:
			out.write("━┯")
		else:
			out.write("━━")
	out.write('\n')

	for r in xrange(0, d):
		if (r > 0) and (r % rank == 0):
			out.write("┠")
			for c in xrange(0, d):
				if (c + 1) == d:
					if (r + 1) == d:
						out.write("━┛")
					else:
						out.write("─┨")
				elif (c + 1) % rank == 0:
					out.write("─┼")
				else:
					out.write("──")
			out.write('\n')

		out.write("┃")

		for c in xrange(0, d):

			cl = board[r][c]

			if cl not in ['?', '.']:
					out.write(cl)
			elif cl == '?':
					out.write("×")
			else:
				if ((r + c) % 2) == 0:
					out.write("∴")
				else:
					out.write("∵")

			if (c + 1) < d:
				if (c + 1) % rank == 0:
					out.write("│")
				else:
					out.write(" ")
			else:
				out.write("┃\n")

	for c in xrange(0, d):
		if c == 0:
			out.write("┗━━");
		elif (c + 1) == d:
			out.write("━┛\n");
		elif (c + 1) % rank == 0:
			out.write("━┷");
		else:
			out.write("━━");

for board, rank in get_board_and_rank():
	print_board(board, rank, sys.stdout)



