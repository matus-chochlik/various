#!/usr/bin/python
# coding: UTF-8
#  Copyright (c) 2017 Matus Chochlik
from __future__ import print_function

import os
import cv2
import numpy
import subprocess
import fileinput
import functools
import collections
import threading
import multiprocessing

def read_frames():
	table = unicode()
	for line in fileinput.input():
		utf8line = line.decode('utf-8')
		table = table + utf8line
		if u"┛" in utf8line:
			yield table
			table = str()

def make_asciiart():
	width = None
	height = None
	for frame in read_frames():
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

def render_images():
	for art_input, width, height in make_asciiart():
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

def load_images():
	queue = collections.deque()
	backlog = multiprocessing.cpu_count()*2
	for renderer in render_images():
		if len(queue) < backlog:
			queue.append(renderer)
		if len(queue) >= backlog:
			yield load_image(queue.popleft())

	for renderer in queue:
		yield load_image(renderer)


def blend_images(imgs):
	return functools.reduce(lambda x, y: cv2.addWeighted(x, 0.6, y, 0.4, 0), imgs)

def blur_images(count, step):
	group = list()
	for image in load_images():
		if len(group) < count:
			group.append(image);

		if len(group) >= count:
			yield blend_images(group)
			group = group[step:]

	while len(group) > 0:
		yield blend_images(group)
		group = group[step:]
	yield image

def make_video(out_path, fps = 60, size = None, video_format = "DIV4"):
	fourcc = cv2.VideoWriter_fourcc(*video_format)
	video = None
	for image in blur_images(count=16, step=8):
		if image is not None:
			if size is None:
				size = image.shape[1], image.shape[0]
			if video is None:
				video = cv2.VideoWriter(out_path, fourcc, float(fps), size, True)
			if size[0] != image.shape[1] and size[1] != image.shape[0]:
				image = resize(image, size)
			video.write(image)

	for f in xrange(0, fps*2):
		video.write(image)
	video.release()

def main():
	make_video("sudoku.avi")
	return 0

if __name__ == "__main__":
	exit(main())
