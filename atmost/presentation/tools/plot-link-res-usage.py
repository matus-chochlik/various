#!/usr/bin/python3 -B
# coding=utf8
# ------------------------------------------------------------------------------
import os
import sys
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as pltckr
import matplotlib.collections as collections
import numpy as np

from statistics import mean

from common import DictObject, PresArgParser
from common import reduce_by
# ------------------------------------------------------------------------------
def _format_hhmm(s, pos=None):
    h = int(s/3600)
    s -= h*3600
    m = int(s/60)
    return "%d:%02d" % (h, m)
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
    p_interval = max(max(linker_count),max(distcc_count))

    for t in [5,10,15,30,60]:
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

    for p in [1,2,3,4,5]:
        p_tick_maj = p
        if p_interval / p_tick_maj < 4:
            break

    fig, spls = plt.subplots(3, 1)
    options.initialize(plt, fig)

    cld = spls[0]
    cld.set_ylabel("CPU load [percent]")
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
    cld.grid()
    cld.legend()

    prc = spls[1]
    prc.set_ylabel("Process count")
    prc.yaxis.set_major_locator(pltckr.MultipleLocator(p_tick_maj))
    prc.xaxis.set_major_locator(pltckr.MultipleLocator(x_tick_maj))
    prc.xaxis.set_major_formatter(pltckr.FuncFormatter(lambda x, p: ""))
    prc.yaxis.set_label_position("right")

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
                    age[-1]-x_interval*0.1,
                    distcc_count[-1]-1
                ),
                arrowprops=dict(facecolor="black", shrink=0.05),
                horizontalalignment="right"
            )
    except AttributeError: pass
    prc.grid()
    prc.legend()

    rsw = spls[2]
    rsw.set_ylabel("Byte size [GB]")
    rsw.set_xlabel("Build progress time [HH:MM]")
    rsw.xaxis.set_major_locator(pltckr.MultipleLocator(x_tick_maj))
    rsw.xaxis.set_major_formatter(pltckr.FuncFormatter(_format_hhmm))
    rsw.xaxis.set_ticks_position("bottom")

    rsw.fill_between(
        age, mem_avail, swap_used,
        where=swap_used > mem_avail,
        hatch="/",
        color="red",
        alpha=0.2
    )
    rsw.plot(
        age, mem_avail,
        label="Available memory"
    )
    rsw.plot(
        age, swap_used,
        label="Swap space used"
    )
    rsw.grid()
    rsw.legend()

    options.finalize(plt)
# ------------------------------------------------------------------------------
def main():
    do_plot(make_argparser().make_options())
    return 0
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    exit(main())
# ------------------------------------------------------------------------------
