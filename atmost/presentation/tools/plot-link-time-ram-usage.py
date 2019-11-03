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
def _format_mmss(s, pos=None):
    m = int(s/60)
    s -= m*60
    return "%2d:%02d" % (m, s)
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

    y_interval = max(data["exec_time"])
    x_interval = max(data["age"])

    fig, spls = plt.subplots(2, 1)

    tick_opts = [5,10,15,30,60]
    x_tick_maj = tick_opts[0]*60
    for t in tick_opts:
        x_tick_min = x_tick_maj
        x_tick_maj = t*60
        if x_interval / x_tick_maj < 15:
            break
    y_tick_maj = tick_opts[0]
    for t in tick_opts:
        y_tick_min = y_tick_maj
        y_tick_maj = t
        if y_interval / y_tick_maj < 12:
            break


    tdr = spls[0]
    tdr.set_ylabel("Link time [MM:SS]")
    tdr.scatter(
        x="age",
        y="exec_time",
        c="hash",
        s="mem_size",
        data=data,
        label="Link memory usage"
    )

    tdr.xaxis.set_ticks_position("top")
    tdr.xaxis.set_minor_locator(pltckr.MultipleLocator(x_tick_min))
    tdr.xaxis.set_major_locator(pltckr.MultipleLocator(x_tick_maj))
    tdr.xaxis.set_major_formatter(pltckr.FuncFormatter(_format_hhmm))
    tdr.yaxis.set_major_locator(pltckr.MultipleLocator(y_tick_maj))
    tdr.yaxis.set_major_formatter(pltckr.FuncFormatter(_format_mmss))
    tdr.grid(which="both", axis="both")
    tdr.legend()

    trd = spls[1]
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
