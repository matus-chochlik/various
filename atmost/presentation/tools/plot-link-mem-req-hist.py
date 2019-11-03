#!/usr/bin/python3 -B
# coding=utf8
# ------------------------------------------------------------------------------
import os
import sys
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as pltckr
import numpy as np
from statistics import mean

from common import DictObject, PresArgParser
# ------------------------------------------------------------------------------
class ArgParser(PresArgParser):
    # --------------------------------------------------------------------------
    def __init__(self, **kw):
        PresArgParser.__init__(self, **kw)

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
            try:
                s = max(math.ceil(tgt.linked.actual), 1)
                count[s][run.jobs] += 1
            except KeyError:
                try:
                    count[s][run.jobs] = 0
                except KeyError:
                    count[s] = {run.jobs: 0}
            except AttributeError:
                pass

    fig, spl = plt.subplots()

    bins = {k: sum(l.values()) for k, l in count.items()}
    total = sum(bins.values())

    spl.xaxis.set_major_formatter(pltckr.FuncFormatter(_format_size))
    spl.bar(bins.keys(), [(100.0*v)/total for v in bins.values()])
    spl.set_xlabel("Linker memory requirements [GB]", fontsize=18)
    spl.set_ylabel("Percent of processes", fontsize=18)
    spl.grid(axis="y")

    options.finalize(plt)
# ------------------------------------------------------------------------------
def main():
    do_plot(make_argparser().make_options())
    return 0
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    exit(main())
# ------------------------------------------------------------------------------
