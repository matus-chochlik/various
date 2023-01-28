#!/usr/bin/env python3
# coding=utf-8
# Copyright Matus Chochlik.
# Distributed under the Boost Software License, Version 1.0.
# See accompanying file LICENSE_1_0.txt or copy at
#  http://www.boost.org/LICENSE_1_0.txt
#
import os
import sys
import math
import argparse

# ------------------------------------------------------------------------------
class ArgumentParser(argparse.ArgumentParser):
    # -------------------------------------------------------------------------
    def __init__(self, **kw):
        argparse.ArgumentParser.__init__(self, **kw)

        self.add_argument(
            "--input", "-i",
            metavar='INPUT-FILE',
            dest='input_path',
            nargs='?',
            type=os.path.realpath,
            default=None
        )

        self.add_argument(
            "--output", "-o",
            metavar='OUTPUT-FILE',
            dest='output_path',
            nargs='?',
            type=os.path.realpath,
            default=None
        )

        self.add_argument(
            "--saturated-red", "-r",
            dest='saturated_red',
            default=64.0,
            type=float
        )

        self.add_argument(
            "--saturated-green", "-g",
            dest='saturated_green',
            default=8.0,
            type=float
        )

        self.add_argument(
            "--saturated-blue", "-b",
            dest='saturated_blue',
            default=8.0,
            type=float
        )

        self.add_argument(
            "--saturated-x", "-x",
            dest='saturated_x',
            default=None,
            type=int
        )

        self.add_argument(
            "--saturated-y", "-y",
            dest='saturated_y',
            default=None,
            type=int
        )

        self.add_argument(
            "--flip-y", "-Y",
            dest='flip_y',
            default=False,
            action='store_true'
        )

        self.add_argument(
            "--saturation-factor", "-S",
            dest='saturation_factor',
            default=24.0,
            type=float
        )

        self.add_argument(
            "--adjust-value", "-V",
            dest='adjust_value',
            default=False,
            action='store_true'
        )

        self.add_argument(
            "--show", "-D",
            dest='show_image',
            default=False,
            action='store_true'
        )

    # -------------------------------------------------------------------------
    def processParsedOptions(self, options):
        return options

    # -------------------------------------------------------------------------
    def parseArgs(self):
        return self.processParsedOptions(
            argparse.ArgumentParser.parse_args(self)
        )

# ------------------------------------------------------------------------------
def getArgumentParser():
    return ArgumentParser(
        prog=os.path.basename(__file__),
        description="""
            Desaturates an image except for a specific color
        """
    )
# ------------------------------------------------------------------------------
def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))
# ------------------------------------------------------------------------------
def do_desaturate_rgb(options, img, channels):
    import colorsys
    sr = options.saturated_red
    sg = options.saturated_green
    sb = options.saturated_blue

    huedist = lambda x, y: min(math.fabs(x - y), math.fabs(1 + x - y))
    blend = lambda x, y, a: x * (1.0 - a) + y * a

    pixs = img.load()
    if options.saturated_x is not None and options.saturated_y is not None:
        x = options.saturated_x
        y = options.saturated_y
        if options.flip_y:
            y = img.height - y
        sr, sg, sb = pixs[x, y]

    sh, ss, sv = colorsys.rgb_to_hsv(sr, sg, sb)

    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixs[x, y]
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            hd = huedist(h, sh)
            v = v / 255.0
            s = blend(0.0, s, math.exp(-hd * options.saturation_factor))
            if options.adjust_value:
                v = blend(math.pow(v, 2.0), v, math.exp(-hd))
            v = v * 255.0
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            pixs[x, y] = (int(r), int(g), int(b))

    return img

# ------------------------------------------------------------------------------
def desaturate(options):
    import PIL.Image
    img = PIL.Image.open(options.input_path)
    if img.mode == "RGB":
        img = do_desaturate_rgb(options, img, 3)
    elif img.mode == "RGBA":
        img = do_desaturate_rgb(options, img, 4)

    if options.show_image:
        img.show()
    if options.output_path is not None:
        img.save(options.output_path)

# ------------------------------------------------------------------------------
def main():
    try:
        options = getArgumentParser().parseArgs()
        desaturate(options)
        return 0
    except Exception as error:
        print(type(error), error)
        try: os.remove(options.output_path)
        except: pass
        raise
        return 1

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    sys.exit(main())

