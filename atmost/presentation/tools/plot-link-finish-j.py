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
            '-i', '--input',
            metavar='INPUT-FILE',
            dest='input_path',
            nargs='?',
            type=os.path.realpath
        )

        self.add_argument(
            '-j', '--jobs',
            metavar='COUNT',
            dest='job_counts',
            nargs='?',
            type=self._positive_int,
            default=[],
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

    stats = DictObject.loadJson(options.input_path)

    target_stats = {}
    y_interval = 0.0

    jobs = sorted(options.job_counts)
    invalid = set()
    for run in stats:
        if run.jobs in jobs:
            for tgt in run.targets:
                try:
                    tgt_stat = target_stats[tgt.name]
                except KeyError:
                    tgt_stat = target_stats[tgt.name] = {}
                try:
                    stat = tgt_stat[run.jobs]
                except KeyError:
                    stat = tgt_stat[run.jobs] = {}

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

    ge = lambda s: s["end"]
    gi = lambda s: s["idx"]

    x = [i for i in range(len(target_stats))]
    ys = {}
    for j in jobs:
        ys[j] = [
            s[j] for s in sorted(
                target_stats.values(),
                key=lambda s: ge(s[j])
            )
        ]

    for j in jobs:
        for i, y in zip(x, ys[j]):
            y["idx"] = i

    fig, spl = plt.subplots()

    for i in range(1, len(jobs)):
        for s in target_stats.values():
            l = pltlns.Line2D(
                xdata=(gi(s[jobs[i-1]]), gi(s[jobs[i]])),
                ydata=(ge(s[jobs[i-1]]), ge(s[jobs[i]])),
                color="black",
                alpha=0.1
            )
            spl.add_line(l)


    for j in jobs:
        spl.plot(x, [ge(s) for s in ys[j]], label="%d jobs" % j)
        spl.scatter(x, [ge(s) for s in ys[j]])

    spl.xaxis.set_major_locator(pltckr.NullLocator())
    spl.yaxis.set_major_locator(pltckr.MultipleLocator(y_tick_maj))
    spl.yaxis.set_major_formatter(pltckr.FuncFormatter(_format_hhmm))
    spl.set_xlabel("Linked targets", fontsize=18)
    spl.set_ylabel("Link finish time [HH:MM]", fontsize=18)
    spl.legend()
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
