#!/usr/bin/python
# coding: UTF-8
#  Copyright (c) 2016 Matus Chochlik

import sys, numpy
from math import atan2
from math import log10

def get_argument_parser():
	import argparse, time

	argparser = argparse.ArgumentParser(
		prog="voronoi-svg"
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
		default=0.80
	)

	argparser.add_argument(
		'--value-high', '-vh',
		type=float,
		action="store",
		default=0.95
	)

	argparser.add_argument(
		'--seed', '-s',
		type=float,
		action="store",
		default=time.time()
	)

	argparser.add_argument(
		'--verbose', '-v',
		action="store_true",
		default=False
	)

	return argparser
 
class options:
	def gen_random_data(self):
		import random

		random.seed(self.seed)

		cell_data = list()
		for y in xrange(self.ycells):
			r = list()
			for x in xrange(self.xcells):
				r.append((
					random.random(),
					random.random(),
					random.random()
				))
			cell_data.append(r)
		return cell_data

	def __init__(self):

		useropts = get_argument_parser().parse_args(sys.argv[1:])

		self.verbose = useropts.verbose

		self.output = useropts.outfile
		self.log = sys.stderr

		self.xcells = useropts.x_cells
		self.ycells = useropts.y_cells

		self.width = useropts.width
		self.height = useropts.height

		self.value_low = useropts.value_low
		self.value_high = useropts.value_high

		self.seed = useropts.seed

		self.cell_data = self.gen_random_data()

		self.values = dict()
		self.values["width"] = self.width
		self.values["height"] = self.height
		self.values["wunit"] = useropts.units
		self.values["hunit"] = useropts.units

		self.cell_fmt = "%%%dd %%%dd\n" % (
			int(log10(self.xcells)+1),
			int(log10(self.ycells)+1)
		)

def grayscalestr(v):
	c = "%02x" % (255*v)
	return "#"+3*c

def find_cell(opts, x, y):
	return opts.cell_data[(y+opts.ycells)%opts.ycells][(x+opts.xcells)%opts.xcells]

def cell_world_coord(opts, x, y):

	c = find_cell(opts, x, y)
	return numpy.array([
		(x+c[0])*(opts.width/opts.xcells),
		(y+c[1])*(opts.height/opts.ycells)
	])

def cell_value(opts, x, y):
	return find_cell(opts, x, y)[2]

def cell_color(opts, x, y):
	return grayscalestr(
		opts.value_low+
		cell_value(opts, x, y)*
		(opts.value_high-opts.value_low)
	)

def offs_cell_world_coord(opts, x, y, o):
	return cell_world_coord(opts, x+o[0], y+o[1])

def perpendicular(v1):
	v2 = numpy.empty_like(v1)
	v2[0] = -v1[1]
	v2[1] =  v1[0]
	return v2

def segment_midpoint(p1, p2):
	return (p1+p2)*0.5

def segment_normal(p1, p2):
	return perpendicular(p2-p1)

def line_intersect_param(l1, l2):
	d1 = l1[1]
	d2 = l2[1]
	dp = l2[0]-l1[0]
	d2p = perpendicular(d2)

	num = numpy.dot(d2p, dp)
	den = numpy.dot(d2p, d1)

	if abs(den) > 0.00001: return num / den
	else: return None


def print_cell(opts, x, y):

	if opts.verbose:
		opts.log.write(opts.cell_fmt % (x, y))

	owc = cell_world_coord(opts, x, y)

	#opts.output.write("""
	#<ellipse cx="%f" cy="%f" rx="1.7" ry="2.7" fill="black"/>""" % (owc[0], owc[1]))

	offsets = []

	for j in xrange(-3, 3):
		for i in xrange(-3, 3):
			if j != 0 or i != 0:
				offsets.append((i, j))

	cuts = []

	for o in offsets:
		cwc = offs_cell_world_coord(opts, x, y, o)

		#opts.output.write("""
		#<ellipse cx="%f" cy="%f" rx="2.7" ry="1.7" fill="black"/>""" % (cwc[0], cwc[1]))
		sm = segment_midpoint(owc, cwc)
		sn = segment_normal(owc, cwc)
		cuts.append((sm, sn))

		p1 = sm-sn*100
		p2 = sm+sn*100

		#opts.output.write("""
		#<line x1="%f" y1="%f" x2="%f" y2="%f"/>""" % (p1[0], p1[1], p2[0], p2[1]))

	intersections = []

	for cj in xrange(len(cuts)):
		for ci in xrange(cj+1, len(cuts)):
			t = line_intersect_param(cuts[cj], cuts[ci])
			if t is not None:
				intersections.append(cuts[cj][0]+cuts[cj][1]*t)

	corners = []

	for isc in intersections:
		seg = (owc, isc-owc)
		eps = 0.001
		skip = False

		for cut in cuts:
			t = line_intersect_param(seg, cut)
			if t is not None and t > 0 and t < 1-eps:
				skip = True
				break

		#opts.output.write("""
		#<ellipse cx="%f" cy="%f" rx="0.5" ry="0.5" fill="black"/>""" % (isc[0], isc[1]))

		if not skip:
			corners.append(isc)
			#opts.output.write("""
			#<ellipse cx="%f" cy="%f" rx="1" ry="1" fill="black"/>""" % (isc[0], isc[1]))
			

	def corner_angle(p):
		v = p - owc
		return atan2(v[1], v[0])
		

	corners = sorted(corners, key=corner_angle)

	pathstr = "M"+" L".join(["%.3f %.3f" % (c[0], c[1]) for c in corners])+" Z"
	opts.output.write("""
	<path d="%s" fill="%s"/>""" % (pathstr, cell_color(opts, x, y)))
	

def print_svg(opts):
	opts.output.write("""<?xml version="1.0" encoding="utf8"?>\n""")
	opts.output.write("""<svg xmlns="http://www.w3.org/2000/svg"
	xmlns:svg="http://www.w3.org/2000/svg"
	width="%(width)s%(wunit)s" height="%(height)s%(hunit)s"
	viewBox="0 0 %(width)s %(height)s"
	version="1.1"
	contentScriptType="text/ecmascript"
	contentStyleType="text/css"\n>\n""" % opts.values)
	#opts.output.write("""<g class="voronoi" stroke="black" stroke-width="0.1">\n""")
	opts.output.write("""<g class="voronoi">\n""")

	for y in xrange(-1, opts.ycells+1):
		for x in xrange(-1, opts.xcells+1):
			print_cell(opts, x, y)

	opts.output.write("""\n""")

	opts.output.write("""</g>\n""")
	opts.output.write("""</svg>\n""")

def main():
	opts = options()

	print_svg(opts)
	

if __name__ == "__main__": main()

