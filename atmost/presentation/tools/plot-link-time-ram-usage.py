#!/usr/bin/python3 -B
# coding=utf8
# ------------------------------------------------------------------------------
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as pltckr
import numpy as np

from common import DictObject, PresArgParser
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
        self._add_jobs_arg()
# ------------------------------------------------------------------------------
def make_argparser():
    return ArgParser(prog=os.path.basename(__file__))
# ------------------------------------------------------------------------------
def do_plot(options):

    data = {
        "age": [],
        "exec_time": [],
        "wait_time": [],
        "mem_used": [],
        "mem_size": [],
        "hash": []
    }

    stats = DictObject.loadJson(options.input_path)
    for run in stats:
        if run.jobs == options.job_count:
            l = len(run.targets)
            for tgt in run.targets:
                data["age"].append(tgt.linking.age)
                data["wait_time"].append(tgt.linking.age-tgt.arrived.age)
                data["exec_time"].append(tgt.linked.age-tgt.linking.age)
                data["mem_used"].append(tgt.linked.actual)
                data["mem_size"].append(tgt.linked.actual*64)
                data["hash"].append(hash(tgt) % l)

    x_interval = max(data["age"])

    fig, trd = plt.subplots()
    options.initialize(plt, fig)

    tick_opts = [5,10,15,30,60]
    x_tick_maj = tick_opts[0]*60
    for t in tick_opts:
        x_tick_min = x_tick_maj
        x_tick_maj = t*60
        if x_interval / x_tick_maj < 15:
            break


    trd.set_ylabel("Link RAM usage [GB]")
    trd.set_xlabel("Build progress time [HH:MM]")
    trd.scatter(
        x="age",
        y="mem_used",
        c="hash",
        s="exec_time",
        data=data,
        label="Link time"
    )

    trd.xaxis.set_ticks_position("bottom")
    trd.xaxis.set_minor_locator(pltckr.MultipleLocator(x_tick_min))
    trd.xaxis.set_major_locator(pltckr.MultipleLocator(x_tick_maj))
    trd.xaxis.set_major_formatter(pltckr.FuncFormatter(_format_hhmm))
    trd.grid(which="both", axis="both")
    trd.legend()

    options.finalize(plt)
# ------------------------------------------------------------------------------
def main():
    do_plot(make_argparser().make_options())
    return 0
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    exit(main())
# ------------------------------------------------------------------------------
