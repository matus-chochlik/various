#!/usr/bin/python
# coding: UTF-8
#  Copyright (c) 2017 Matus Chochlik
from __future__ import print_function

import os
import sys
import cv2
import numpy
import argparse
import subprocess
import functools
import collections
import threading
import multiprocessing

def read_frames(options):
	table = unicode()
	for line in options.input:
		utf8line = line.decode('utf-8')
		table = table + utf8line
		if u"┛" in utf8line:
			yield table
			table = str()

def make_asciiart(options):
	width = None
	height = None
	for frame in read_frames(options):
		lines = frame.split('\n')
		if width is None: width = len(lines[0])
		if height is None: height = len(lines)

		print(frame)
		yield u'text %(width)d, %(height)d "%(frame)s"' % {
				"width": width,
				"height": len(lines),
				"frame": frame
			}, width*10, height*17

class RenderThread(threading.Thread):
	def __init__(self, renderer, art_input):
		self._renderer = renderer
		self._input = art_input
		threading.Thread.__init__(self,target=self._run)
		threading.Thread.start(self)

	def _run(self):
		self._value = bytearray(self._renderer.communicate(self._input)[0])

	def get(self):
		threading.Thread.join(self)
		return self._value

def render_images(options):
	for art_input, width, height in make_asciiart(options):
		conv_cmd = [
			"convert",
			"-size", str(width)+"x"+str(height), "xc:white",
			"-font", "DejaVu-Sans-Mono", "-pointsize", "14",
			"-fill", "black",
			"-draw", "@-", "PNG8:-"
		]
		renderer = subprocess.Popen(
			conv_cmd,
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE
		)

		yield RenderThread(renderer, art_input.encode('utf-8'))

def load_image(future_img_data):
	return cv2.imdecode(
		numpy.asarray(future_img_data.get(), dtype=numpy.uint8),
		cv2.IMREAD_UNCHANGED
	)

def load_images(options):
	queue = collections.deque()
	backlog = multiprocessing.cpu_count()*2
	for renderer in render_images(options):
		if len(queue) < backlog:
			queue.append(renderer)
		if len(queue) >= backlog:
			yield load_image(queue.popleft())

	for renderer in queue:
		yield load_image(renderer)


def blend_images(options, imgs):
	return functools.reduce(
		lambda x, y: cv2.addWeighted(x, 0.6, y, 0.4, 0),
		imgs
	)

def blur_images(options):
	group = list()
	for image in load_images(options):
		if len(group) < options.blur_frames:
			group.append(image);

		if len(group) >= options.blur_frames:
			yield blend_images(options, group)
			group = group[options.step_frames:]

	while len(group) > 0:
		yield blend_images(options, group)
		group = group[options.step_frames:]
	yield image

def make_video(options, size = None):
	fourcc = cv2.VideoWriter_fourcc(*options.fourcc)
	video = None
	for image in blur_images(options):
		if image is not None:
			if size is None:
				size = image.shape[1], image.shape[0]
			if video is None:
				video = cv2.VideoWriter(
					options.output_path,
					fourcc,
					float(options.fps),
					size,
					True
				)
			if size[0] != image.shape[1] and size[1] != image.shape[0]:
				image = resize(image, size)
			video.write(image)

	for f in xrange(0, int(options.fps*options.tail)):
		video.write(image)
	video.release()

class __MakeVideoArgumentParser(argparse.ArgumentParser):
	def __init__(self, **kw):
		def _rank_value(x):
			if x < 2:
				self.error("`%d' is not a valid rank" % x)
			return x

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
			default='sudoku.avi'
		)

		self.add_argument(
			'-r', '--rank',
			metavar='RANK',
			nargs='?',
			type=_rank_value,
			default=3
		)

		self.add_argument(
			'-F', '--fourcc',
			metavar='FOURCC',
			nargs='?',
			type=str,
			default="DIV4"
		)

		self.add_argument(
			'-f', '--fps',
			metavar='FPS',
			nargs='?',
			type=float,
			default=None
		)

		self.add_argument(
			'-b', '--blur',
			dest='blur_frames',
			metavar='FRAME-COUNT',
			nargs='?',
			type=int,
			default=None
		)

		self.add_argument(
			'-s', '--step',
			dest='step_frames',
			metavar='FRAME-COUNT',
			nargs='?',
			type=int,
			default=None
		)

		self.add_argument(
			'-t', '--tail',
			metavar='SECONDS',
			nargs='?',
			type=float,
			default=2
		)

	def process_parsed_options(self, options):

		if options.fps is None:
			options.fps = 60 if options.rank > 3 else 30

		if options.blur_frames is None:
			options.blur_frames = 16 if options.rank > 3 else 8

		if options.step_frames is None:
			options.step_frames = 8 if options.rank > 3 else 2

		if options.input is None:
			options.input = sys.stdin

		return options

	def parse_args(self):
		return self.process_parsed_options(
			argparse.ArgumentParser.parse_args(self)
		)



def make_argparser():
	return __MakeVideoArgumentParser(
		prog="make_video",
		description="makes videos from the output of the sudoku_solver script"
	)

def main():
	make_video(make_argparser().parse_args())
	return 0

if __name__ == "__main__":
	exit(main())
