#!/usr/bin/python
# coding: UTF-8
#  Copyright (c) 2016 Matus Chochlik

import sys, numpy
from math import atan2
from math import log10
from itertools import izip

def perpendicular(v1):
	v2 = numpy.empty_like(v1)
	v2[0] = -v1[1]
	v2[1] =  v1[0]
	return v2

def set_center(points):
	return sum(points)/len(points)

def segment_point(p1, p2, c):
	return (1-c)*p1 + c*p2;

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

def get_argument_parser():
	import argparse

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
		choices=["grayscale", "cell-coord"],
		action="store",
		default="grayscale"
	)

	argparser.add_argument(
		'--cell-mode', '-C',
		type=str,
		choices=["full", "scaled", "flagstone","pebble"],
		action="store",
		default="full"
	)

	argparser.add_argument(
		'--verbose', '-v',
		action="store_true",
		default=False
	)

	return argparser
 
class options:
	def grayscale_color_str(self, v):
		c = "%02x" % (255*v)
		return "#"+3*c

	def get_rng0(self):
		try:
			return self.rng0
		except:
			self.rng0 = random.Random(self.seed)
			return self.rng0

	def get_rng(self):
		import random

		if self.seed is None:
			import time
			try: return random.SystemRandom()
			except: return random.Random(time.time())
		else:
			return random.Random(get_rng0().randomint(sys.maxsize))

	def gen_random_values(self):

		rc = self.get_rng()

		cell_data = list()
		for y in xrange(self.ycells):
			r = list()
			for x in xrange(self.xcells):
				r.append(rc.random())
			cell_data.append(r)
		return cell_data

	def gen_random_offsets(self):

		rx = self.get_rng()
		ry = self.get_rng()

		cell_data = list()
		for y in xrange(self.ycells):
			r = list()
			for x in xrange(self.xcells):
				r.append((rx.random(), ry.random()))
			cell_data.append(r)
		return cell_data

	def cell_offset(self, x, y):
		cy = (y+self.ycells)%self.ycells
		cx = (x+self.xcells)%self.xcells
		return self.cell_offsets[cy][cx]

	def cell_value(self, x, y):
		cy = (y+self.ycells)%self.ycells
		cx = (x+self.xcells)%self.xcells
		return self.cell_values[cy][cx]


	def cell_grayscale_color(self, x, y):
		cv = self.cell_value(x, y)
		v = self.value_low + cv*(self.value_high-self.value_low)
		return self.grayscale_color_str(v)

	def cell_coord_color(self, x, y):
		x = (x + self.xcells) % self.xcells
		y = (y + self.ycells) % self.ycells

		r = (256*x)/self.xcells
		g = (256*y)/self.ycells
		b = (256*self.cell_z_coord)

		return "#%02x%02x%02x" % (r, g, b)

	def full_cell_element_str(self, x, y, unused, corners):
		clist = ["%.3f %.3f" % (c[0], c[1]) for c in corners]
		pathstr = "M"+" L".join(clist)+" Z"
		return """
		<path d="%(def)s" stroke="%(color)s" fill="%(color)s"/>""" % {
			"def": pathstr,
			"color": self.cell_color(x, y)
		}

	def scaled_cell_element_str(self, x, y, center, corners):
		m = set_center(corners)
		newcorners = [segment_point(m, c, self.scale) for c in corners]
		return self.full_cell_element_str(x, y, center, newcorners);

	def flagstone_cell_element_str(self, x, y, center, corners):
		zcorners = izip(corners, corners[1:] + [corners[0]])
		c = self.cell_value(x, y)
		newcorners = [segment_point(a, b, c) for (a, b) in zcorners]
		return self.scaled_cell_element_str(x, y, center, newcorners);

	def pebble_cell_element_str(self, x, y, center, corners):
		m = set_center(corners)
		apoints = [segment_point(m, c, self.scale) for c in corners]
		bpoints = apoints[1:] + [apoints[0]]
		c = self.cell_value(x, y)
		zpoints = izip(apoints, bpoints)
		cpoints = [segment_point(a, b, c) for (a, b) in zpoints]
		dpoints = cpoints[1:] + [cpoints[0]]

		zpoints = izip(bpoints, dpoints)

		cfmt = lambda c : "%.3f %.3f" % (c[0], c[1])

		clist = ["%s, %s" % (cfmt(b), cfmt(d)) for (b, d) in zpoints]
		pathstr = "M%s Q" % cfmt(cpoints[0])+" Q".join(clist)+" Z"
		return """
		<path d="%(def)s" stroke="%(color)s" fill="%(color)s"/>""" % {
			"def": pathstr,
			"color": self.cell_color(x, y)
		}


	def __init__(self):

		useropts = get_argument_parser().parse_args(sys.argv[1:])

		self.verbose = useropts.verbose
		self.cell_mode = useropts.cell_mode
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

		if self.color_mode == "grayscale":
			self.cell_color = lambda x, y: self.cell_grayscale_color(x, y)
		elif self.color_mode == "cell-coord":
			self.cell_color = lambda x, y: self.cell_coord_color(x, y)

		if self.cell_mode == "full":
			self.cell_element_str = self.full_cell_element_str
		elif self.cell_mode == "scaled":
			self.cell_element_str = self.scaled_cell_element_str
		elif self.cell_mode == "flagstone":
			self.cell_element_str = self.flagstone_cell_element_str
		elif self.cell_mode == "pebble":
			self.cell_element_str = self.pebble_cell_element_str

		self.cell_offsets = self.gen_random_offsets()

		self.values = dict()
		self.values["width"] = self.width
		self.values["height"] = self.height
		self.values["wunit"] = useropts.units
		self.values["hunit"] = useropts.units

		self.cell_fmt = "%%%dd %%%dd\n" % (
			int(log10(self.xcells)+1),
			int(log10(self.ycells)+1)
		)

def cell_world_coord(opts, x, y):

	c = opts.cell_offset(x, y)
	return numpy.array([
		(x+c[0])*(opts.width/opts.xcells),
		(y+c[1])*(opts.height/opts.ycells)
	])

def cell_value(opts, x, y):
	return opts.get_value(x, y)

def cell_color(opts, x, y):
	return grayscalestr(
		opts.value_low+
		cell_value(opts, x, y)*
		(opts.value_high-opts.value_low)
	)

def offs_cell_world_coord(opts, x, y, o):
	return cell_world_coord(opts, x+o[0], y+o[1])

def print_cell(opts, x, y, center, corners):
	opts.output.write(opts.cell_element_str(x, y, center, corners))

def make_cell(opts, x, y):

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
		

	print_cell(opts, x,y, owc, sorted(corners, key=corner_angle))

	

def print_svg(opts):
	opts.output.write("""<?xml version="1.0" encoding="utf8"?>\n""")
	opts.output.write("""<svg xmlns="http://www.w3.org/2000/svg"
	xmlns:svg="http://www.w3.org/2000/svg"
	width="%(width)s%(wunit)s" height="%(height)s%(hunit)s"
	viewBox="0 0 %(width)s %(height)s"
	version="1.1"
	contentScriptType="text/ecmascript"
	contentStyleType="text/css"\n>\n""" % opts.values)
	opts.output.write("""<g class="voronoi" stroke-width="1.0">\n""")

	for y in xrange(-1, opts.ycells+1):
		for x in xrange(-1, opts.xcells+1):
			make_cell(opts, x, y)

	opts.output.write("""\n""")

	opts.output.write("""</g>\n""")
	opts.output.write("""</svg>\n""")

def main():
	opts = options()

	print_svg(opts)
	

if __name__ == "__main__": main()

