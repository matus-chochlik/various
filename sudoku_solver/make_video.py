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

		if options.print_frames:
			print(frame)

		if options.use_pango:
			yield u'<tt>%(frame)s</tt>' % {
				"frame": frame
			}, width*10, height*18
		else:
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
		if options.use_pango:
			conv_cmd = [
				"convert",
				"-size", str(width)+"x"+str(height), "-background", "white",
				"-define", "pango:justify=true",
				"-define", "pango:font=Monospace Regular 12",
				"pango:%s" % art_input, "PNG8:-"
			]
			renderer = subprocess.Popen(
				conv_cmd,
				stdout=subprocess.PIPE
			)
			yield RenderThread(renderer, None)
		else:
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
	renderer_queue = collections.deque()
	image_queue = collections.deque()
	image_backlog = int(options.blur_frames*(options.head+options.tail))
	step_frames = 1
	first = True
	image = None

	for renderer in render_images(options):
		renderer_queue.append(renderer)
		if len(renderer_queue) >= options.queue_length:
			image = load_image(renderer_queue.popleft())
			if first:
				for x in xrange(0, int(options.fps*options.head)):
					yield image, 1
				first = False
			image_queue.append(image)

		if len(image_queue) >= image_backlog:
			image = image_queue.popleft()
			if step_frames < options.step_frames:
				step_frames += options.ease_in_out
			yield image, int(step_frames)

	for renderer in renderer_queue:
		image_queue.append(load_image(renderer))
		if len(image_queue) >= image_backlog:
			image = image_queue.popleft()
			if step_frames < options.step_frames:
				step_frames += options.ease_in_out
			yield image, int(step_frames)

	for image in image_queue:
		if step_frames > 1:
			step_frames -= options.ease_in_out
		if step_frames < 1:
			step_frames = 1
		yield image, int(step_frames)

	for x in xrange(0, int(options.fps*options.tail)):
		yield image, 1


def blend_images(options, imgs):
	return functools.reduce(
		lambda x, y:
			cv2.addWeighted(x, options.blend_src, y, options.blend_dst, 0),
		imgs
	)

class BlenderThread(threading.Thread):
	def __init__(self, options, images):
		self._options = options
		self._images = images
		threading.Thread.__init__(self,target=self._run)
		threading.Thread.start(self)

	def _run(self):
		self._blended = blend_images(self._options, self._images)

	def get(self):
		threading.Thread.join(self)
		return self._blended

def blur_images(options):
	group = list()
	for image, step_frames in load_images(options):
		group.append(image);

		if len(group) >= options.blur_frames:
			yield BlenderThread(options, group)
			group = group[step_frames:]

	while len(group) > 0:
		yield BlenderThread(options, group)
		group = group[step_frames:]

def feed_video_frames(options):
	blender_queue = collections.deque()
	for blender in blur_images(options):
		blender_queue.append(blender)

		if len(blender_queue) >= options.blur_threads:
			yield blender_queue.popleft().get()

	for blender in blender_queue:
			yield blender.get()

def make_video(options, size = None):
	fourcc = cv2.VideoWriter_fourcc(*options.fourcc)
	video = None
	for image in feed_video_frames(options):
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

	if video:
		video.release()

class __MakeVideoArgumentParser(argparse.ArgumentParser):
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

		def _norm_weight(x):
			try:
				assert(float(x) >= 0.0 and float(x) <= 1.0)
				return float(x)
			except:
				self.error("`%s' is not a valid weight value" % str(x))

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
			'-P', '--no-print',
			dest='print_frames',
			default=True,
			action='store_false'
		)

		self.add_argument(
			'-p', '--pango',
			dest='use_pango',
			default=False,
			action='store_true'
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
			type=_positive_float,
			default=None
		)

		self.add_argument(
			'-q', '--queue',
			dest='queue_length',
			metavar='FRAME-COUNT',
			nargs='?',
			type=_positive_int,
			default=multiprocessing.cpu_count()*2
		)

		self.add_argument(
			'-b', '--blur',
			dest='blur_frames',
			metavar='FRAME-COUNT',
			nargs='?',
			type=_positive_int,
			default=None
		)

		self.add_argument(
			'-t', '--blur-threads',
			dest='blur_threads',
			metavar='COUNT',
			nargs='?',
			type=_positive_int,
			default=None
		)

		self.add_argument(
			'-s', '--step',
			dest='step_frames',
			metavar='FRAME-COUNT',
			nargs='?',
			type=_positive_int,
			default=None
		)

		self.add_argument(
			'-w', '--blur-weight',
			dest='blur_weight',
			metavar='WEIGHT',
			nargs='?',
			type=_norm_weight,
			default=0.6
		)

		self.add_argument(
			'-E', '--ease',
			dest='ease_in_out',
			metavar='FACTOR',
			nargs='?',
			type=_norm_weight,
			default=0.05
		)

		self.add_argument(
			'-H', '--head',
			metavar='SECONDS',
			nargs='?',
			type=_positive_float,
			default=2
		)

		self.add_argument(
			'-T', '--tail',
			metavar='SECONDS',
			nargs='?',
			type=_positive_float,
			default=3
		)

	def process_parsed_options(self, options):

		if options.fps is None:
			options.fps = 60 if options.rank > 3 else 30

		if options.blur_frames is None:
			options.blur_frames = 16 if options.rank > 3 else 8

		if options.blur_threads is None:
			options.blur_threads = multiprocessing.cpu_count()*2

		if options.step_frames is None:
			options.step_frames = 8 if options.rank > 3 else 2

		if options.input is None:
			options.input = sys.stdin

		if options.output_path is None:
			options.output_path = 'sudoku.avi'
		else:
			if os.path.isdir(options.output_path):
				options.output_path = os.path.join(
					options.output_path,
					'sudoku.avi'
				)

		options.blend_src = options.blur_weight
		options.blend_dst = 1.0 - options.blur_weight

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
