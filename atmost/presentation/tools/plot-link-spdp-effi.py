#!/usr/bin/python3 -B
# coding=utf8
# ------------------------------------------------------------------------------
import os
import sys
import math
import random
import argparse
import matplotlib.pyplot as plt
import matplotlib.ticker as pltckr
import matplotlib.lines as pltlns
import numpy as np
from statistics import mean

from common import DictObject
# ------------------------------------------------------------------------------
class ArgParser(argparse.ArgumentParser):
    # --------------------------------------------------------------------------
    def __init__(self, **kw):
        argparse.ArgumentParser.__init__(self, **kw)

        self.add_argument(
            '-i', '--input-path',
            metavar='INPUT-FILE',
            dest='input_path',
            nargs='?',
            type=os.path.realpath,
            action="append"
        )
# ------------------------------------------------------------------------------
def make_argparser():
    return ArgParser(prog=os.path.basename(__file__))
# ------------------------------------------------------------------------------
def _format_hhmm(s, pos=None):
    h = int(s/3600)
    s -= h*3600
    m = int(s/60)
    return "%d:%02d" % (h, m)
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

    fig, spls = plt.subplots(2, 1)

    speedup = spls[0]
    speedup.xaxis.set_ticks_position("top")
    speedup.set_ylabel("Speedup", fontsize=18)
    speedup.grid()

    effcncy = spls[1]
    effcncy.set_xlabel("Number of jobs", fontsize=18)
    effcncy.set_ylabel("Efficiency", fontsize=18)
    effcncy.grid()

    for p in options.input_path:
        d = data[p]
        sd = sorted(d.items())
        speedup.plot(
            *zip(*[(j,d[1]/v) for j,v in sd]),
            label=p
        )
        effcncy.plot(
            *zip(*[(j,(d[1]/v)/j) for j,v in sd]),
            label=p
        )

    plt.show()
# ------------------------------------------------------------------------------
def main():
    do_plot(make_argparser().parse_args())
    return 0
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    exit(main())
# ------------------------------------------------------------------------------
