#!/usr/bin/python3 -B
# coding=utf8
# ------------------------------------------------------------------------------
import os
import sys
import math
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
            '-f', '--input-fast',
            metavar='INPUT-FILE',
            dest='input_path_fast',
            nargs='?',
            type=os.path.realpath
        )

        self.add_argument(
            '-s', '--input-slow',
            metavar='INPUT-FILE',
            dest='input_path_slow',
            nargs='?',
            type=os.path.realpath
        )

        self.add_argument(
            '-j', '--jobs',
            metavar='COUNT',
            dest='job_count',
            nargs='?',
            default=1,
            type=self._positive_int
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

    stats_slow = DictObject.loadJson(options.input_path_slow)
    stats_fast = DictObject.loadJson(options.input_path_fast)

    target_stats = {}
    y_interval = 0.0

    invalid = set()
    for kind, stats in [("slow", stats_slow), ("fast", stats_fast)]:
        for run in stats:
            if run.jobs == options.job_count:
                for tgt in run.targets:
                    try:
                        tgt_stat = target_stats[tgt.name]
                    except KeyError:
                        tgt_stat = target_stats[tgt.name] = {}
                    try:
                        stat = tgt_stat[kind]
                    except KeyError:
                        stat = tgt_stat[kind] = {}

                    try:
                        stat["bgn"] = tgt.linking.age
                        stat["end"] = tgt.linked.age
                        y_interval = max(y_interval, tgt.linked.age)
                    except AttributeError:
                        invalid.add(tgt.name)

    for name in invalid:
        del target_stats[name]

    tick_opts = [5,10,15,30,60]
    for t in tick_opts:
        y_tick_maj = t*60
        if y_interval / y_tick_maj < 12:
            break

    gs = lambda s: s["slow"]
    gf = lambda s: s["fast"]
    ge = lambda s: s["end"]
    gi = lambda s: s["idx"]

    x = [i for i in range(len(target_stats))]
    ys = [gs(s) for s in sorted(target_stats.values(), key=lambda s: ge(gs(s)))]
    yf = [gf(s) for s in sorted(target_stats.values(), key=lambda s: ge(gf(s)))]

    for i, ss, sf in zip(x, ys, yf):
        ss["idx"] = i
        sf["idx"] = i

    fig, spl = plt.subplots()

    spl.fill_between(
        x,
        np.array([ge(s) for s in yf]),
        np.array([ge(s) for s in ys]),
        color="orange",
        alpha=0.2
    )

    for s in target_stats.values():
        l = pltlns.Line2D(
            xdata=(gi(gs(s)), gi(gf(s))),
            ydata=(ge(gs(s)), ge(gf(s))),
            color="black",
            alpha=0.3
        )
        spl.add_line(l)

    spl.plot(x, [ge(s) for s in ys], color="red")
    spl.scatter(x, [ge(s) for s in ys], color="red")
    spl.plot(x, [ge(s) for s in yf], color="green")
    spl.scatter(x, [ge(s) for s in yf], color="green")

    spl.xaxis.set_major_locator(pltckr.NullLocator())
    spl.yaxis.set_major_locator(pltckr.MultipleLocator(y_tick_maj))
    spl.yaxis.set_major_formatter(pltckr.FuncFormatter(_format_hhmm))
    spl.set_xlabel("Linked targets", fontsize=18)
    spl.set_ylabel("Link finish time [HH:MM]", fontsize=18)
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
