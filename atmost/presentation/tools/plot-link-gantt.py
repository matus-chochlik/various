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
        self._add_jobs_arg()
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
def intersecting(b0, e0, b1, e1):
    if (b0 < b1) and (b1 < e0): return True
    if (b0 < e1) and (e1 < e0): return True
    if (b1 < b0) and (b0 < e1): return True
    if (b1 < e0) and (e0 < e1): return True
    return False
# ------------------------------------------------------------------------------
def do_plot(options):

    stats = DictObject.loadJson(options.input_path)

    lanes = {0: []}
    for run in stats:
        if run.jobs == options.job_count:
            for tgt in sorted(run.targets, key=lambda t: t.arrived.age):
                lanes[0].append((
                    tgt.name,
                    tgt.arrived.age,
                    tgt.linking.age,
                    tgt.linked.age,
                ))

    x_interval = max(t[3] for t in lanes[0])

    tick_opts = [5,10,15,30,60]
    for t in tick_opts:
        x_tick_maj = t*60
        if x_interval / x_tick_maj < 15:
            break

    l = 0
    while len(lanes[l]) > 0:
        lanes[l+1] = []
        for i0 in range(len(lanes[l])):
            n0,a0,b0,e0 = lanes[l][i0]
            for i1 in range(i0+1, len(lanes[l])):
                n1,a1,b1,e1 = lanes[l][i1]
                if intersecting(a0, e0, a1, e1):
                    lanes[l+1].append((n0,a0,b0,e0))
                    lanes[l+0][i0] = None
                    break
        lanes[l] = [t for t in lanes[l] if t is not None]
        l += 1

    n = len(lanes)
    for l in range(n-1):
        li = n-l-1
        for i0 in range(len(lanes[li])):
            n0,a0,b0,e0 = lanes[li][i0]
            for k in range(l+1, n):
                ki = n-k-1
                intersect = False
                for i1 in range(len(lanes[ki])):
                    n1,a1,b1,e1 = lanes[ki][i1]
                    if intersecting(a0, e0, a1, e1):
                        intersect = True
                        break
                if not intersect:
                    lanes[ki].append((n0,a0,b0,e0))
                    lanes[li][i0] = None
                    break
        lanes[li] = [t for t in lanes[li] if t is not None]

    lanes = {k:v for k,v in lanes.items() if len(v) > 0}

    q = [len(l) for l in lanes.values()]

    fig, spl = plt.subplots()

    for idx, lane in zip(range(len(lanes)), lanes.values()):
        for n,a,b,e, in lane:
            spl.add_line(
                pltlns.Line2D(
                    xdata=(e, e),
                    ydata=(idx, idx+1),
                    color="black",
                    alpha=0.5
                )
            )
        spl.broken_barh(
            xranges=[(a,b-a) for n,a,b,e in lane],
            yrange=(idx+0.15,0.70),
            facecolors=[(0.7+random.random()*0.3, 0.3, 0.3) for i in range(len(lane))]
        )
        spl.broken_barh(
            xranges=[(b,e-b) for n,a,b,e in lane],
            yrange=(idx+0.15,0.70),
            facecolors=[(0.3, 0.7+random.random()*0.3, 0.3) for i in range(len(lane))]
        )

    spl.xaxis.set_major_locator(pltckr.MultipleLocator(x_tick_maj))
    spl.xaxis.set_major_formatter(pltckr.FuncFormatter(_format_hhmm))
    spl.yaxis.set_major_locator(pltckr.MultipleLocator(1))
    spl.set_xlabel("Build progress time [HH:MM]", fontsize=18)
    spl.set_ylabel("Parallel jobs", fontsize=18)
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
