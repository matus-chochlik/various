#!/usr/bin/python3 -B
# coding=utf8
# ------------------------------------------------------------------------------
import os
import sys
import math
import random
import matplotlib.pyplot as plt
import matplotlib.ticker as pltckr
import matplotlib.lines as pltlns
import numpy as np
from statistics import mean

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
    def _age(t):
        try: return t.linked.age
        except AttributeError: return t.linking.age

    data = {}
    for p in options.input_path:
        stats = DictObject.loadJson(p)
        data[p] = {}

        for run in stats:
            data[p][run.jobs] = max(_age(t) for t in run.targets)

    fig, spls = plt.subplots(3, 1)
    options.initialize(plt, fig)

    speedup = spls[0]
    speedup.xaxis.set_ticks_position("top")
    speedup.xaxis.set_major_locator(pltckr.MultipleLocator(2))
    speedup.set_ylabel("Speedup")
    speedup.grid()

    margsup = spls[1]
    margsup.xaxis.set_ticks_position("top")
    margsup.xaxis.set_major_locator(pltckr.MultipleLocator(2))
    margsup.xaxis.set_major_formatter(pltckr.NullFormatter())
    margsup.yaxis.set_label_position("right")
    margsup.set_ylabel("Marginal speedup")
    margsup.grid()

    effcncy = spls[2]
    effcncy.xaxis.set_major_locator(pltckr.MultipleLocator(2))
    effcncy.set_xlabel("Number of jobs")
    effcncy.set_ylabel("Efficiency")
    effcncy.grid()

    for p in options.input_path:
        d = data[p]
        sd = []
        w = None
        for j, v in sorted(d.items()):
            sd.append((j,v,w))
            w = v

        speedup.plot(
            *zip(*[(j,d[1]/v) for j,v,w in sd]),
            label=p
        )

        x = [j for j,v,w in sd]
        y = np.array([(w if w else v)/v for j,v,w in sd])
        z = np.array([1.0 for t in sd])
        margsup.fill_between(
            x, y, z,
            where=(y >= z),
            interpolate=True,
            color="green",
            alpha=0.1
        )
        margsup.fill_between(
            x, y, z,
            where=(y <= z),
            interpolate=True,
            color="red",
            alpha=0.2
        )
        margsup.plot(
            *zip(*[(j,(w if w else v)/v) for j,v,w in sd]),
            label=p
        )
        effcncy.plot(
            *zip(*[(j,(d[1]/v)/j) for j,v,w in sd]),
            label=p
        )

    options.finalize(plt)
# ------------------------------------------------------------------------------
def main():
    do_plot(make_argparser().make_options())
    return 0
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    exit(main())
# ------------------------------------------------------------------------------
