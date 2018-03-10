#!/usr/bin/env python
# coding: UTF-8
#  Copyright (c) 2017-2018 Matus Chochlik
from __future__ import print_function

import os
import sys
import json
import argparse

def get_line_and_rank(options):
	rank = None
	counter = 0
	for line in options.input:
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

def get_board_and_rank(options):
	board = []
	for line, rank in get_line_and_rank(options):
		if not line:
			if board:
				yield board, rank
			board = []
		else:
			board.append(line.split(' '))


def print_board(board, rank, options):
	d = rank*rank

	for c in xrange(0, d):
		if c == 0:
			options.output.write("┏━━")
		elif (c + 1) == d:
			options.output.write("━┓")
		elif (c + 1) % rank == 0:
			options.output.write("━┯")
		else:
			options.output.write("━━")
	options.output.write('\n')

	for r in xrange(0, d):
		if (r > 0) and (r % rank == 0):
			options.output.write("┠")
			for c in xrange(0, d):
				if (c + 1) == d:
					if (r + 1) == d:
						options.output.write("━┛")
					else:
						options.output.write("─┨")
				elif (c + 1) % rank == 0:
					options.output.write("─┼")
				else:
					options.output.write("──")
			options.output.write('\n')

		options.output.write("┃")

		for c in xrange(0, d):

			cl = board[r][c]

			if cl not in ['?', '.']:
					options.output.write(cl)
			elif cl == '?':
					options.output.write("×")
			else:
				if ((r + c) % 2) == 0:
					options.output.write("∴")
				else:
					options.output.write("∵")

			if (c + 1) < d:
				if (c + 1) % rank == 0:
					options.output.write("│")
				else:
					options.output.write(" ")
			else:
				options.output.write("┃\n")

	for c in xrange(0, d):
		if c == 0:
			options.output.write("┗━━");
		elif (c + 1) == d:
			options.output.write("━┛\n");
		elif (c + 1) % rank == 0:
			options.output.write("━┷");
		else:
			options.output.write("━━");

class __FormatSudokuArgumentParser(argparse.ArgumentParser):
	def __init__(self, **kw):
		def _rank_value(x):
			try:
				assert(int(x) >= 2)
				return int(x)
			except:
				self.error("`%d' is not a valid rank" % x)

		def _positive_int(x):
			try:
				assert(int(x) > 0)
				return int(x)
			except:
				self.error("`%s' is not a positive integer value" % str(x))

		def _positive_float(x):
			try:
				assert(float(x) > 0)
				return float(x)
			except:
				self.error("`%s' is not a positive integer value" % str(x))

		argparse.ArgumentParser.__init__(self, **kw)

		self.add_argument(
			'-i', '--input',
			metavar='INPUT-FILE',
			nargs='?',
			type=argparse.FileType('r'),
			default=None
		)

		self.add_argument(
			'-o', '--output',
			dest='output_path',
			metavar='INPUT-FILE',
			nargs='?',
			type=os.path.realpath,
			default=None
		)

	def process_parsed_options(self, options):

		if options.input is None:
			options.input = sys.stdin

		if options.output_path is None:
			options.output = sys.stdout
		else:
			if os.path.isdir(options.output_path):
				options.output = open(os.path.join(
					options.output_path,
					'sudoku.txt'
				))
		return options

	def parse_args(self):
		return self.process_parsed_options(
			argparse.ArgumentParser.parse_args(self)
		)

def make_argparser():
	return __FormatSudokuArgumentParser(
		prog="format_sudoku",
		description="re-formats the output output of the sudoku_solver script"
	)

def format_frames(options):
	first_frame = True
	for board, rank in get_board_and_rank(options):
		output_options = dict()
		if first_frame:
			output_options["rank"] = rank
			first_frame = False
		json.dump(output_options, options.output, ensure_ascii=False)
		options.output.write('\n')
		print_board(board, rank, options)

def main():
	format_frames(make_argparser().parse_args())
	return 0

if __name__ == "__main__":
	exit(main())
