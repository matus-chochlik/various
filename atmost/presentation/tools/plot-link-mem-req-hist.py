#!/usr/bin/python3 -B
# coding=utf8
# ------------------------------------------------------------------------------
import os
import sys
import math
import argparse
import matplotlib.pyplot as plt
import matplotlib.ticker as pltckr
import numpy as np
from statistics import mean

from common import DictObject
# ------------------------------------------------------------------------------
class ArgParser(argparse.ArgumentParser):
    # --------------------------------------------------------------------------
    def _positive_int(self, x):
        try:
            i = int(x)
            assert(i > 0)
            return i
        except:
            self.error("`%s' is not a positive integer value" % str(x))
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
# ------------------------------------------------------------------------------
def make_argparser():
    return ArgParser(prog=os.path.basename(__file__))
# ------------------------------------------------------------------------------
def _format_size(x, pos=None):
    return "%d to %d" % (x-1, x)
# ------------------------------------------------------------------------------
def do_plot(options):

    count = {}
    stats = DictObject.loadJson(options.input_path)
    for run in stats:
        for tgt in run.targets:
            s = max(math.ceil(tgt.linked.actual), 1)
            try: count[s][run.jobs] += 1
            except KeyError:
                try:
                    count[s][run.jobs] = 0
                except KeyError:
                    count[s] = {run.jobs: 0}

    fig, spl = plt.subplots()

    spl.xaxis.set_major_formatter(pltckr.FuncFormatter(_format_size))
    spl.bar(count.keys(), [mean(l.values()) for l in count.values()])
    spl.set_xlabel("Linker memory requirements [GB]", fontsize=18)
    spl.set_ylabel("Number of processes", fontsize=18)
    spl.grid(axis="y")

    plt.show()
# ------------------------------------------------------------------------------
def main():
    do_plot(make_argparser().parse_args())
    return 0
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    exit(main())
# ------------------------------------------------------------------------------
