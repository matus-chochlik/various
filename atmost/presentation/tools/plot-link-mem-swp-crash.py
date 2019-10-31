#!/usr/bin/python3 -B
# coding=utf8
# ------------------------------------------------------------------------------
import os
import sys
import argparse
import matplotlib.pyplot as plt
import matplotlib.ticker as pltckr
import matplotlib.collections as collections
import numpy as np

from statistics import mean

from common import DictObject
from common import reduce_by
# ------------------------------------------------------------------------------
def _format_hhmm(s, pos=None):
    h = int(s/3600)
    s -= h*3600
    m = int(s/60)
    return "%d:%02d" % (h, m)
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
def do_plot(options):

    _1G = 1024.0**3

    age = []
    mem_avail = []
    swap_used = []
    ld_count = []

    stats = DictObject.loadJson(options.input_path)
    for ent in stats:
        age.append(ent.age)
        mem_avail.append(ent.mem_avail / _1G)
        swap_used.append(ent.swap_used / _1G)
        ld_count.append(ent.linker)

    x_interval = max(age)
    y_interval = max(max(swap_used), max(mem_avail))

    tick_opts = [5,10,15,30,60]
    for t in tick_opts:
        x_tick_maj = t*60
        if x_interval / x_tick_maj < 15:
            break

    red = 20
    age = reduce_by(age, red)
    mem_avail = np.array(reduce_by(mem_avail, red))
    swap_used = np.array(reduce_by(swap_used, red))
    ld_count = np.array(reduce_by(ld_count, red))

    age_fl = [2*age[-1]-age[-1-i] for i in range(20)]
    mem_avail_fl = [mem_avail[-1] for x in age_fl]

    trashing = []
    for ag, ma, su in zip(age, mem_avail, swap_used):
        if ma < su:
            trashing.append((ag, (ma+su)*0.5))

    plt.xkcd()
    fig, spl = plt.subplots()
    spl.set_ylabel("Byte size [GB]", fontsize=20)
    spl.set_xlabel("Build progress time [HH:MM]", fontsize=18)
    spl.xaxis.set_major_locator(pltckr.MultipleLocator(x_tick_maj))
    spl.xaxis.set_major_formatter(pltckr.FuncFormatter(_format_hhmm))

    for i in range(4):
        spl.add_collection(
            collections.BrokenBarHCollection.span_where(
                age,
                ymin=0,
                ymax=y_interval,
                where=ld_count > i,
                facecolor='black',
                alpha=0.04
            )
        )

    spl.fill_between(
        age, mem_avail, swap_used,
        where=swap_used > mem_avail,
        hatch="/",
        color="red",
        alpha=0.1
    )

    spl.plot(
        age, mem_avail,
        label="Available memory",
        color="blue"
    )
    spl.plot(
        age_fl, mem_avail_fl,
        linestyle="--",
        color="blue"
    )

    spl.plot(
        age, swap_used,
        label="Swap space used",
        color="red"
    )

    if trashing:
        spl.annotate(
            "Trashing",
            xy=(mean(x for x,y in trashing), min(y for x,y in trashing)),
            xytext=(
                min(x for x,y in trashing)-x_interval*0.05,
                max(y for x,y in trashing)+y_interval*0.10
            ),
            arrowprops=dict(facecolor="black", shrink=0.05),
            horizontalalignment="right",
            fontsize=18
        )

    spl.annotate(
        "Out of\nmemory",
        xy=(age[-1], mem_avail[-1]),
        xytext=(
            age[-1]-x_interval*0.15,
            mem_avail[-1]-y_interval*0.01
        ),
        arrowprops=dict(facecolor="black", shrink=0.05),
        horizontalalignment="right",
        fontsize=18
    )

    spl.annotate(
        "REBOOT\n:-(",
        xy=(age[-1], swap_used[-1]),
        xytext=(
            age[-1]+x_interval*0.05,
            swap_used[-1]+y_interval*0.15
        ),
        arrowprops=dict(facecolor="black", shrink=0.05),
        horizontalalignment="left",
        fontsize=22
    )


    spl.legend()

    plt.show()
# ------------------------------------------------------------------------------
def main():
    do_plot(make_argparser().parse_args())
    return 0
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    exit(main())
# ------------------------------------------------------------------------------
