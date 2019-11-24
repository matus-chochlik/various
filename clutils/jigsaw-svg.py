#!/usr/bin/python3
# coding: UTF-8
#  Copyright (c) 2017-2019 Matus Chochlik

import sys
import numpy
import random
from math import log10

# ------------------------------------------------------------------------------
def get_argument_parser():
	import argparse

	argparser = argparse.ArgumentParser(
		prog="jigsaw-svg"
	)

	argparser.add_argument(
		'outfile',
		nargs='?',
		type=argparse.FileType('w'),
		default=sys.stdout
	)

	argparser.add_argument(
		'--x-cells', '-X',
		type=int,
		action="store",
		default=32
	)

	argparser.add_argument(
		'--y-cells', '-Y',
		type=int,
		action="store",
		default=32
	)

	argparser.add_argument(
		'--width', '-W',
		type=float,
		action="store",
		default=512
	)

	argparser.add_argument(
		'--height', '-H',
		type=float,
		action="store",
		default=512
	)

	argparser.add_argument(
		'--units', '-U',
		action="store",
		default="px"
	)

	argparser.add_argument(
		'--value-low', '-vl',
		type=float,
		action="store",
		default=0.05
	)

	argparser.add_argument(
		'--value-high', '-vh',
		type=float,
		action="store",
		default=0.95
	)

	argparser.add_argument(
		'--cell-z-coord', '-cz',
		type=float,
		action="store",
		default=0.0
	)

	argparser.add_argument(
		'--scale', '-S',
		type=float,
		action="store",
		default=0.9
	)

	argparser.add_argument(
		'--seed', '-rs',
		type=float,
		action="store",
		default=None
	)

	argparser.add_argument(
		'--color-mode', '-M',
		type=str,
		choices=["none", "grayscale", "cell-coord"],
		action="store",
		default="none"
	)

	argparser.add_argument(
		'--verbose', '-v',
		action="store_true",
		default=False
	)

	return argparser
 
# ------------------------------------------------------------------------------
class Options:
    # --------------------------------------------------------------------------
	def grayscale_color_str(self, v):
		c = "%02x" % int(255*v)
		return "#"+3*c

    # --------------------------------------------------------------------------
	def get_rng0(self):
		try:
			return self.rng0
		except:
			self.rng0 = random.Random(self.seed)
			return self.rng0

    # --------------------------------------------------------------------------
	def get_rng(self):
		import random

		if self.seed is None:
			import time
			try: return random.SystemRandom()
			except: return random.Random(time.time())
		else:
			return random.Random(self.get_rng0().randrange(0, sys.maxsize))

    # --------------------------------------------------------------------------
	def gen_random_values(self):

		rc = self.get_rng()

		cell_data = list()
		for y in range(self.ycells):
			r = list()
			for x in range(self.xcells):
				r.append(rc.random())
			cell_data.append(r)
		return cell_data

    # --------------------------------------------------------------------------
	def cell_value(self, x, y):
		cy = (y+self.ycells)%self.ycells
		cx = (x+self.xcells)%self.xcells
		return self.cell_values[cy][cx]


    # --------------------------------------------------------------------------
	def cell_grayscale_color(self, x, y):
		cv = self.cell_value(x, y)
		v = self.value_low + cv*(self.value_high-self.value_low)
		return self.grayscale_color_str(v)

    # --------------------------------------------------------------------------
	def cell_coord_color(self, x, y):
		x = (x + self.xcells) % self.xcells
		y = (y + self.ycells) % self.ycells

		r = int((256*x)/self.xcells)
		g = int((256*y)/self.ycells)
		b = int((256*self.cell_z_coord))

		return "#%02x%02x%02x" % (r, g, b)

    # --------------------------------------------------------------------------
	def full_cell_element_str(self, x, y):

		val = self.cell_value(x, y)

		sig_n = 1 if self.cell_value(x+0, y-1)>val else -1
		sig_e = 1 if self.cell_value(x+1, y+0)>val else -1
		sig_s = 1 if self.cell_value(x+0, y+1)>val else -1 
		sig_w = 1 if self.cell_value(x-1, y+0)>val else -1

		pathstr = "M%(x)d,%(y)d " % {"x": x, "y": y}

		def get_curve(get_coord, s):
			return [
				get_coord( 0,  0*s), get_coord(20, -5*s), get_coord(35,  0*s),
				get_coord( 0,  0*s), get_coord( 5,  0*s), get_coord( 5,  5*s),
				get_coord( 0,  5*s), get_coord(-5,  5*s), get_coord(-5, 15*s),
				get_coord( 0,  5*s), get_coord( 5, 10*s), get_coord(15, 10*s),
				get_coord(10,  0*s), get_coord(15, -5*s), get_coord(15,-10*s),
				get_coord( 0,-10*s), get_coord(-5,-10*s), get_coord(-5,-15*s),
				get_coord( 0, -5*s), get_coord( 5, -5*s), get_coord( 5, -5*s),
				get_coord( 0,  0*s), get_coord(20, -5*s), get_coord(35,  0*s)
			]

		def get_curve_str(get_coord, s):
			scaled = [(0.01*x, 0.01*y) for x,y in get_curve(get_coord, s)]
			return " ".join(["%0.2f,%0.2f" % sc for sc in scaled])

		pathstr+= "c " + get_curve_str(lambda x, y: ( x, y), sig_n)
		pathstr+= "c " + get_curve_str(lambda x, y: (-y, x), sig_e)
		pathstr+= "c " + get_curve_str(lambda x, y: (-x,-y), sig_s)
		pathstr+= "c " + get_curve_str(lambda x, y: ( y,-x), sig_w)

		pathstr+=" Z"

		if self.cell_color is not None:
			return """<path d="%(def)s" fill="%(color)s"/>\n""" % {
				"def": pathstr,
				"color": self.cell_color(x, y)
			}
		else:
			return """<path d="%(def)s"/>\n""" % {
				"def": pathstr
			}

    # --------------------------------------------------------------------------
	def __init__(self):

		useropts = get_argument_parser().parse_args(sys.argv[1:])

		self.verbose = useropts.verbose
		self.color_mode = useropts.color_mode
		self.seed = useropts.seed

		self.output = useropts.outfile
		self.log = sys.stderr

		self.xcells = useropts.x_cells
		self.ycells = useropts.y_cells

		self.width = useropts.width
		self.height = useropts.height

		self.value_low = useropts.value_low
		self.value_high = useropts.value_high
		self.cell_z_coord = useropts.cell_z_coord

		self.scale = useropts.scale

		self.cell_values = self.gen_random_values()

		if self.color_mode == "none":
			self.cell_color = None
		elif self.color_mode == "grayscale":
			self.cell_color = lambda x, y: self.cell_grayscale_color(x, y)
		elif self.color_mode == "cell-coord":
			self.cell_color = lambda x, y: self.cell_coord_color(x, y)

		self.cell_element_str = self.full_cell_element_str

		self.values = dict()
		self.values["xcells"] = self.xcells
		self.values["ycells"] = self.ycells
		self.values["width"] = self.width
		self.values["height"] = self.height
		self.values["wunit"] = useropts.units
		self.values["hunit"] = useropts.units

		self.cell_fmt = "%%%dd %%%dd\n" % (
			int(log10(self.xcells)+1),
			int(log10(self.ycells)+1)
		)

# ------------------------------------------------------------------------------
def cell_value(opts, x, y):
	return opts.get_value(x, y)

# ------------------------------------------------------------------------------
def cell_color(opts, x, y):
	return grayscalestr(
		opts.value_low+
		cell_value(opts, x, y)*
		(opts.value_high-opts.value_low)
	)

# ------------------------------------------------------------------------------
def print_cell(opts, x, y):
	opts.output.write(opts.cell_element_str(x, y))

# ------------------------------------------------------------------------------
def make_cell(opts, x, y):

	if opts.verbose:
		opts.log.write(opts.cell_fmt % (x, y))

	print_cell(opts, x,y)

# ------------------------------------------------------------------------------
def print_svg(opts):
	opts.output.write("""<?xml version="1.0" encoding="utf8"?>\n""")
	opts.output.write("""<svg xmlns="http://www.w3.org/2000/svg"
	xmlns:svg="http://www.w3.org/2000/svg"
	width="%(width)s%(wunit)s" height="%(height)s%(hunit)s"
	viewBox="0 0 %(xcells)s %(ycells)s"
	version="1.1"
	contentScriptType="text/ecmascript"
	contentStyleType="text/css"\n>\n""" % opts.values)
	opts.output.write("""<g class="voronoi" stroke-width="1.0">\n""")

	for y in range(-1, opts.ycells+1):
		for x in range(-1, opts.xcells+1):
			make_cell(opts, x, y)

	opts.output.write("""\n""")

	opts.output.write("""</g>\n""")
	opts.output.write("""</svg>\n""")

# ------------------------------------------------------------------------------
def main():
	opts = Options()

	print_svg(opts)
	
# ------------------------------------------------------------------------------
if __name__ == "__main__": main()

