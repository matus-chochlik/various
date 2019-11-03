#!/usr/bin/python3 -B
# coding=utf8
# ------------------------------------------------------------------------------
import os
import sys
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as pltckr
import numpy as np

from common import DictObject, PresArgParser
# ------------------------------------------------------------------------------
class ArgParser(PresArgParser):
    # --------------------------------------------------------------------------
    def __init__(self, **kw):
        PresArgParser.__init__(self, **kw)

        self._add_multi_input_arg()
# ------------------------------------------------------------------------------
def make_argparser():
    return ArgParser(prog=os.path.basename(__file__))
# ------------------------------------------------------------------------------
def do_plot(options):
    data = []
    for p in options.input_path:
        stats = DictObject.loadJson(p)
        for run in stats:
            for tgt in run.targets:
                try:
                    data.append((tgt.linked.predicted, tgt.linked.actual))
                except AttributeError:
                    pass

    fig, spl = plt.subplots()

    spl.set_xlabel("Actual memory usage [GB]", fontsize=18)
    spl.set_ylabel("(Actual - Predicted) memory usage [GB]", fontsize=18)

    x = [a for p, a in data]
    y = [a-p for p, a in data]

    maxx = max(x)
    minx = min(x)
    maxy = max(y)
    miny = min(y)
    pn = 1.0/maxy
    nn = -1.0/min(y)

    spl.broken_barh(
        xranges=[(minx, maxx-minx)],
        yrange=(0.0, maxy),
        color="red",
        alpha=0.1
    )

    spl.broken_barh(
        xranges=[(minx, maxx-minx)],
        yrange=(miny, -miny),
        color="blue",
        alpha=0.1
    )

    mix = lambda a, b, f: (1.0-f)*a + f*b

    spl.scatter(
        x, y,
        color = [(
            mix(0.6, 1.0, max(v, 0.0)*pn),
            mix(0.6, 0.0, max(max(v, 0.0)*pn, -min(0.0, v)*nn)),
            mix(0.6, 1.0, -min(0.0, v)*nn),
        ) for v in y]
    )

    spl.grid(which="both", axis="both")

    options.finalize(plt)
# ------------------------------------------------------------------------------
def main():
    do_plot(make_argparser().make_options())
    return 0
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    exit(main())
# ------------------------------------------------------------------------------
