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

        self._add_single_input_arg()
# ------------------------------------------------------------------------------
def make_argparser():
    return ArgParser(prog=os.path.basename(__file__))
# ------------------------------------------------------------------------------
def _format_mmss(s, pos=None):
    m = int(s/60)
    s -= m*60
    return "%2d:%02d" % (m, s)
# ------------------------------------------------------------------------------
def do_plot(options):

    stats = DictObject.loadJson(options.input_path)
    y_interval = max(max(run.time for run in setup.runs) for setup in stats)

    tick_opts = [5,10,15,30,60]
    y_tick_maj = tick_opts[0]
    for t in tick_opts:
        y_tick_maj = t*60
        if y_interval / y_tick_maj < 8:
            break

    data = {
        True: {},
        False: {}
    }

    for setup in stats:
        l = data[setup.ccache][setup.compile_cores] = []
        prev_time = None
        for run in sorted(setup.runs, key=lambda r: r.max_n):
            l.append((run.max_n, run.time, prev_time if prev_time else run.time))
            prev_time = run.time

    fig, spls = plt.subplots(2, 2)
    options.initialize(plt, fig)

    cche = ["no ccache", "ccached"]
    lpos = ["left", "right"]

    for i in [0, 1]: 
        ttime = spls[0][i]
        ttime.xaxis.set_ticks_position("top")
        ttime.xaxis.set_major_locator(pltckr.MultipleLocator(2))
        ttime.yaxis.set_label_position(lpos[i])
        ttime.set_ylabel("Speedup")
        ttime.set_xlabel("# of parallel processes")
        ttime.grid()

        tmsup = spls[1][i]
        tmsup.xaxis.set_major_locator(pltckr.MultipleLocator(2))
        tmsup.yaxis.set_label_position(lpos[i])
        tmsup.set_ylabel("Marginal speedup")
        tmsup.set_xlabel(cche[i])
        tmsup.grid()

        for cores, setups in data[bool(i)].items():
            t1 = None
            ns = []
            ts = []
            ds = []
            for max_n, time, prev_time in setups:
                if max_n == 1: t1 = time
                ns.append(max_n)
                ts.append(time)
                ds.append(prev_time / time)

            lbl = "%d build cores" % cores
            ttime.plot(ns, [t1 / t for t in ts], label=lbl)
            tmsup.plot(ns, [d for d in ds], label=lbl)

        ttime.legend()
        tmsup.legend()

    options.finalize(plt)
# ------------------------------------------------------------------------------
def main():
    do_plot(make_argparser().make_options())
    return 0
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    exit(main())
# ------------------------------------------------------------------------------
