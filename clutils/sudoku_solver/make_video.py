#!/usr/bin/python
# coding: UTF-8
#  Copyright (c) 2017 Matus Chochlik
from __future__ import print_function

import os
import cv2
import subprocess
import fileinput
import tempfile

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

def render_images():
	for asciiart, width, height in make_asciiart():
		with tempfile.NamedTemporaryFile('w', delete=False) as art_file:
			art_file.write(asciiart.encode('utf-8'))

		conv_cmd = [
			"convert",
			"-size", str(width)+"x"+str(height), "xc:white",
			"-font", "DejaVu-Sans-Mono", "-pointsize", "14",
			"-fill", "black",
			"-draw", "@"+art_file.name, art_file.name+".png"
		]
		yield subprocess.Popen(conv_cmd), art_file.name, art_file.name+".png"

def load_images():
	for renderer, art_path, img_path in render_images():
		renderer.wait()
		yield cv2.imread(img_path)
		os.remove(art_path)
		os.remove(img_path)

def make_video(out_path, fps = 60, size = None, video_format = "DIV4"):
	fourcc = cv2.VideoWriter_fourcc(*video_format)
	video = None
	for image in load_images():
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
	make_video("bla.avi")
	return 0

if __name__ == "__main__":
	exit(main())
