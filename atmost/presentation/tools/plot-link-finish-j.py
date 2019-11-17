#!/usr/bin/python3 -B
# coding=utf8
# ------------------------------------------------------------------------------
import os
import sys
import math
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
    options.initialize(plt, fig)

    for i in range(1, len(jobs)):
        ya = np.array([ge(s) for s in ys[jobs[i-1]]])
        yb = np.array([ge(s) for s in ys[jobs[i-0]]])
        spl.fill_between(
            x, ya, yb,
            color="gray",
            alpha=0.2
        )

    for i in range(1, len(jobs)):
        for s in target_stats.values():
            l = pltlns.Line2D(
                xdata=(gi(s[jobs[i-1]]), gi(s[jobs[i]])),
                ydata=(ge(s[jobs[i-1]]), ge(s[jobs[i]])),
                color="black",
                alpha=0.2
            )
            spl.add_line(l)


    for j in jobs:
        spl.plot(x, [ge(s) for s in ys[j]], label="%d jobs" % j)
        spl.scatter(x, [ge(s) for s in ys[j]])

    dur = [max(ge(s) for s in ys[j]) for j in jobs]
    ds = max(dur)
    df = min(dur)
    su = ds / df
    yp = df*0.1 if (df > (ds-df)) else (ds+df)*0.5

    spl.annotate(
        "%.1f×\nfaster" % su,
        xy=(x[-1], df),
        xytext=(x[-1], yp),
        arrowprops=dict(facecolor="black", shrink=0.05),
        horizontalalignment="center"
    )

    spl.xaxis.set_major_locator(pltckr.NullLocator())
    spl.yaxis.set_major_locator(pltckr.MultipleLocator(y_tick_maj))
    spl.yaxis.set_major_formatter(pltckr.FuncFormatter(_format_hhmm))
    spl.set_xlabel("Linked targets")
    spl.set_ylabel("Link finish time [HH:MM]")
    spl.legend()
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
