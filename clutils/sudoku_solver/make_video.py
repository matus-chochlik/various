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
	table = str()
	for line in fileinput.input():
		table = table + line
		if "┛" in line:
			yield table
			table = str()

def make_asciiart():
	for frame in read_frames():
		print(frame)
		yield 'text %(width)d, %(height)d "%(frame)s"' % {
				"width": 40,
				"height": len(frame.split('\n')),
				"frame": frame
			}

def render_images():
	for asciiart in make_asciiart():
		with tempfile.NamedTemporaryFile('w',delete=False) as art_file:
			art_file.write(asciiart)

		conv_cmd = [
			"convert",
			"-size", "290x330", "xc:white",
			"-font", "DejaVu-Sans-Mono", "-pointsize", "12",
			"-fill", "black",
			"-draw", "@"+art_file.name, art_file.name+".png"
		]
		yield subprocess.Popen(conv_cmd), art_file

def load_images():
	for renderer, art_file in render_images():
		renderer.wait()
		image_path = art_file.name+".png"
		yield cv2.imread(image_path)
		os.remove(art_file.name)
		os.remove(image_path)

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
	video.release()

def main():
	make_video("bla.avi")
	return 0

if __name__ == "__main__":
	exit(main())
