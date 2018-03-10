#!/usr/bin/env python
# coding: UTF-8
#  Copyright (c) 2017-2018 Matus Chochlik
from __future__ import print_function

import os
import sys
import json
import argparse
import collections

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

		self.add_argument(
			'-b', '--min-blur',
			dest='min_blur_frames',
			metavar='FRAME-COUNT',
			nargs='?',
			type=_positive_int,
			default=1
		)

		self.add_argument(
			'-B', '--max-blur',
			dest='max_blur_frames',
			metavar='FRAME-COUNT',
			nargs='?',
			type=_positive_int,
			default=None
		)

		self.add_argument(
			'-s', '--min-step',
			dest='min_step_frames',
			metavar='FRAME-COUNT',
			nargs='?',
			type=_positive_int,
			default=1
		)

		self.add_argument(
			'-S', '--max-step',
			dest='max_step_frames',
			metavar='FRAME-COUNT',
			nargs='?',
			type=_positive_int,
			default=None
		)

		self.add_argument(
			'-e', '--ease-frames',
			dest='ease_frames',
			metavar='FRAME-COUNT',
			nargs='?',
			type=_positive_int,
			default=1
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

		if not options.max_blur_frames or options.max_blur_frames < options.min_blur_frames:
			options.max_blur_frames = options.min_blur_frames*2

		if not options.max_step_frames or options.max_step_frames < options.min_step_frames:
			options.max_step_frames = options.min_step_frames*2

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

def get_blur_frames(options, frame_number):
	if frame_number <= options.ease_frames:
		beta = float(frame_number)/float(options.ease_frames)
		alpha = 1.0 - beta
		return int(alpha*options.min_blur_frames + beta*options.max_blur_frames)
	else:
		return options.max_blur_frames

def get_step_frames(options, frame_number):
	if frame_number <= options.ease_frames:
		beta = float(frame_number)/float(options.ease_frames)
		alpha = 1.0 - beta
		return int(alpha*options.min_step_frames + beta*options.max_step_frames)
	else:
		return options.max_step_frames

def format_frames(options):
	frame_queue = collections.deque()
	frame_number = 0

	for board, rank in get_board_and_rank(options):
		output_options = dict()
		if frame_number == 0:
			output_options["rank"] = rank

		output_options["blur_frames"] = get_blur_frames(options, frame_number)
		output_options["step_frames"] = get_step_frames(options, frame_number)

		frame_number += 1

		frame_queue.append((board, rank, output_options))

		if len(frame_queue) > options.ease_frames:
			board, rank, output_options = frame_queue.popleft()
			json.dump(output_options, options.output, ensure_ascii=False)
			options.output.write('\n')
			print_board(board, rank, options)

	frame_number = options.ease_frames

	for board, rank, output_options in frame_queue:
		output_options = dict()
		output_options["blur_frames"] = get_blur_frames(options, frame_number)
		output_options["step_frames"] = get_step_frames(options, frame_number)

		frame_number -= 1

		json.dump(output_options, options.output, ensure_ascii=False)
		options.output.write('\n')
		print_board(board, rank, options)

def main():
	format_frames(make_argparser().parse_args())
	return 0

if __name__ == "__main__":
	exit(main())
