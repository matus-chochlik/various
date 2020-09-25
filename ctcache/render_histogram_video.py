#!/usr/bin/python3 -B
# coding=utf8
# Copyright (c) 2020 Matus Chochlik
# Renders video from clang-tidy cache server stats json.
# Data from http://ctcache:port/stats/ctcache.json can be used as input.
# ------------------------------------------------------------------------------
import os
import io
import sys
import cv2
import json
import math
import numpy
import argparse
import matplotlib.pyplot as plt
# ------------------------------------------------------------------------------
class ArgParser(argparse.ArgumentParser):
    # --------------------------------------------------------------------------
    def _valid_fps(self, x):
        try:
            f = int(x)
            assert f > 0
            return f
        except:
            self.error("`%s' is not a valid FPS value" % str(x))

    # --------------------------------------------------------------------------
    def _valid_fourcc(self, x):
        try:
            assert len(x) == 4
            return x
        except:
            self.error("`%s' is not a valid FOURCC code" % str(x))


    # --------------------------------------------------------------------------
    def __init__(self, **kw):
        argparse.ArgumentParser.__init__(self, **kw)

        self.add_argument(
            '-i', '--input',
            metavar='INPUT-FILE',
            dest='input_path',
            nargs='?',
            type=os.path.realpath
        )

        self.add_argument(
            '-o', '--output',
            metavar='OUTPUT-FILE',
            dest='output_path',
            nargs='?',
            type=os.path.realpath,
            default="/tmp/ctcache.avi"
        )

        self.add_argument(
            '-f', '--fps',
            metavar='NUMBER',
            dest='fps',
            nargs='?',
            type=self._valid_fps,
            default=20.0
        )

        self.add_argument(
            '-F', '--fourcc',
            metavar='CODE',
            dest='fourcc',
            nargs='?',
            default="FMP4"
        )
    # --------------------------------------------------------------------------
    def make_options(self):
        return self.parse_args()

# ------------------------------------------------------------------------------
def make_argparser():
    return ArgParser(prog=os.path.basename(__file__))
# ------------------------------------------------------------------------------
def render_video(options):
    stats = json.load(open(options.input_path, "rt", encoding="utf8"))
    get_hch = lambda s: s.get("hit_count_histogram", {})
    max_hits = int(max(max(int(k) for k in get_hch(s).keys()) for s in stats)*0.5)
    max_srcs = int(max(max(int(k)*v for k,v in get_hch(s).items()) for s in stats))
    get_fac = lambda i, y: (float(i) / float(max_hits), math.sqrt(3.0*y / float(max_srcs)))
    num_stats = len(stats)
    prog_norm = 100.0/num_stats if num_stats else 0.0
    clamp = lambda t : tuple(max(min(x, 1), 0) for x in t)
    imgbuf = io.BytesIO()

    width = 12
    height = 8

    try:
        plt.style.use('dark_background')
        fig, spl = plt.subplots()
        fig.set_size_inches(width, height)

        video = cv2.VideoWriter(
            options.output_path,
            cv2.VideoWriter_fourcc(*options.fourcc) if options.fourcc else -1,
            options.fps,
            tuple(int(c) for c in fig.get_size_inches()*fig.dpi),
            True
        )
        plt.close(fig)

        x = range(1, max_hits+1)

        row = 0
        for stat in stats:
            hch = get_hch(stat)
            g = [(i, hch.get(str(i), 0)) for i in x]
            y = [i*v for i, v in g]
            c = [clamp((1.0-f+e, f+e, e)) for f, e in (get_fac(i,v) for i,v in g)]

            fig, spl = plt.subplots()
            fig.set_size_inches(width, height)
            spl.bar(x, y, color=c)

            spl.set_xlabel("Number of hits")
            spl.set_xlim(0, max_hits)

            spl.set_ylabel("Number of sources")
            spl.set_ylim(1, max_srcs)
            spl.set_yscale("log")
            spl.grid(axis="y")

            imgbuf.seek(0)
            plt.savefig(imgbuf, format="png")
            plt.close(fig)

            imgbuf.seek(0)
            img = cv2.imdecode(
                numpy.frombuffer(imgbuf.getbuffer(), dtype=numpy.uint8),
                cv2.IMREAD_COLOR
            )

            video.write(img)
            row += 1
            print("%5d/%d: %3.1f%% done" % (row, num_stats, row*prog_norm))

    except KeyboardInterrupt:
        pass
    finally:
        video.release()
        cv2.destroyAllWindows()


# ------------------------------------------------------------------------------
def main():
    render_video(make_argparser().make_options())
    return 0
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    exit(main())
# ------------------------------------------------------------------------------
