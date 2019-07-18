#!/usr/bin/python
# coding: UTF-8
#  Copyright (c) 2017 Matus Chochlik

import os
import sys
import argparse


# ------------------------------------------------------------------------------
class MakeCppResArgumentParser(argparse.ArgumentParser):
	# --------------------------------------------------------------------------
	def __init__(self, **kw):

		def _positive_int(x):
			try:
				assert(int(x) > 0)
				return int(x)
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
			metavar='OUTPUT-FILE',
			nargs='?',
			type=os.path.realpath,
			default=None
		)

		self.add_argument(
			'-l', '--max-line-len',
			dest='max_line_len',
			metavar='COLUMNS',
			nargs='?',
			type=_positive_int,
			default=80
		)

	# --------------------------------------------------------------------------
	def process_parsed_options(self, options):

		if options.input is None:
			options.input = sys.stdin
			options.input_name = 'resources'
		else:
			options.input_name =\
				os.path.basename(options.input.name).split(os.path.extsep)[0]

		if options.output_path is None:
			options.output_path = '%s.inl' % options.input_name
			options.output = sys.stdout
		else:
			if os.path.isdir(options.output_path):
				options.output_path = os.path.join(
					options.output_path,
					'%s.inl' % options.input_name
				)
			options.output = open(options.output_path, "wt")

		return options

	# --------------------------------------------------------------------------
	def parse_args(self):
		return self.process_parsed_options(
			argparse.ArgumentParser.parse_args(self)
		)

# ------------------------------------------------------------------------------
def make_argparser():
	return MakeCppResArgumentParser(
		prog="make_video",
		description="""
		makes a compilable C/C++ source file containing static data from inout
		files.
		"""
	)
# ------------------------------------------------------------------------------
def make_res_inl(options):
	options.output.write(
		"static const unsigned char _res_%s[] = {\n" %
		options.input_name
	)
	linelen = 0
	first = True
	while True:
		byte = options.input.read(1)
		if not byte:
			break

		temp = ""
		if first: first = False
		else: temp += ", "

		temp += "0x%x" % ord(byte)
		
		if linelen > options.max_line_len:
			linelen = 0
			temp += "\n"
		else:
			linelen += len(temp)
		options.output.write(temp)
	options.output.write("};\n")
# ------------------------------------------------------------------------------
def main():
	make_res_inl(make_argparser().parse_args())
	return 0
# ------------------------------------------------------------------------------
if __name__ == "__main__":
	exit(main())
# ------------------------------------------------------------------------------
