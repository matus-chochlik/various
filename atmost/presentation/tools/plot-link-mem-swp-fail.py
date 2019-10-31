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
    cpu_load_1 = []
    cpu_load_5 = []
    cpu_load_15 = []
    distcc_count = []
    linker_count = []

    stats = DictObject.loadJson(options.input_path)
    for ent in stats:
        age.append(ent.age)
        mem_avail.append(ent.mem_avail / _1G)
        swap_used.append(ent.swap_used / _1G)
        cpu_load_1.append(ent.cpu_load_1)
        cpu_load_5.append(ent.cpu_load_5)
        cpu_load_15.append(ent.cpu_load_15)
        distcc_count.append(ent.distcc)
        linker_count.append(ent.linker)

    x_interval = max(age)
    y_interval = max(max(swap_used), max(mem_avail))

    tick_opts = [5,10,15,30,60]
    for t in tick_opts:
        x_tick_maj = t*60
        if x_interval / x_tick_maj < 15:
            break

    red = (len(age)/500)+1
    age = reduce_by(age, red)
    mem_avail = np.array(reduce_by(mem_avail, red, min))
    swap_used = np.array(reduce_by(swap_used, red, max))
    cpu_load_1 = reduce_by(cpu_load_1, red)
    cpu_load_5 = reduce_by(cpu_load_5, red)
    cpu_load_15 = reduce_by(cpu_load_15, red)
    distcc_count = reduce_by(distcc_count, red, max)
    linker_count = reduce_by(linker_count, red, max)

    plt.xkcd()
    fig, spls = plt.subplots(3, 1)
    cld = spls[0]
    cld.set_ylabel("CPU load [percent]", fontsize=20)
    cld.xaxis.set_major_locator(pltckr.MultipleLocator(x_tick_maj))
    cld.xaxis.set_major_formatter(pltckr.FuncFormatter(_format_hhmm))
    cld.xaxis.set_ticks_position("top")

    cld.plot(
        age, cpu_load_1,
        label="1 min. load avg."
    )
    cld.plot(
        age, cpu_load_5,
        label="5 min. load avg."
    )
    cld.plot(
        age, cpu_load_15,
        label="15 min. load avg."
    )
    cld.legend()

    prc = spls[1]
    prc.set_ylabel("Process count", fontsize=20)
    prc.xaxis.set_major_locator(pltckr.NullLocator())

    prc.plot(
        age, distcc_count,
        label="distcc"
    )
    prc.plot(
        age, linker_count,
        label="linker"
    )
    try:
        if stats[-1].failed:
            prc.annotate(
                "Build\nfailed",
                xy=(age[-1], distcc_count[-1]),
                xytext=(
                    age[-1],
                    distcc_count[-1]+y_interval*0.15
                ),
                arrowprops=dict(facecolor="black", shrink=0.05),
                horizontalalignment="center",
                fontsize=22
            )
    except AttributeError: pass
    prc.legend()

    rsw = spls[2]
    rsw.set_ylabel("Byte size [GB]", fontsize=20)
    rsw.set_xlabel("Build progress time [HH:MM]", fontsize=18)
    rsw.xaxis.set_major_locator(pltckr.MultipleLocator(x_tick_maj))
    rsw.xaxis.set_major_formatter(pltckr.FuncFormatter(_format_hhmm))
    rsw.xaxis.set_ticks_position("bottom")

    rsw.fill_between(
        age, mem_avail, swap_used,
        where=swap_used > mem_avail,
        hatch="/",
        color="red",
        alpha=0.1
    )
    rsw.plot(
        age, mem_avail,
        label="Available memory"
    )
    rsw.plot(
        age, swap_used,
        label="Swap space used"
    )
    rsw.legend()

    plt.show()
# ------------------------------------------------------------------------------
def main():
    do_plot(make_argparser().parse_args())
    return 0
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    exit(main())
# ------------------------------------------------------------------------------
