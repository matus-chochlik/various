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

        self._add_multi_input_arg()
# ------------------------------------------------------------------------------
def make_argparser():
    return ArgParser(prog=os.path.basename(__file__))
# ------------------------------------------------------------------------------
def do_plot(options):

    data = {}
    error = 0.0
    for p in options.input_path:
        stats = DictObject.loadJson(p)
        for run in stats:
            for tgt in run.targets:
                try:
                    data[tgt.name]["predicted"].append(tgt.linked.predicted)
                    data[tgt.name]["actual"].append(tgt.linked.actual)
                    error = max(error, tgt.linked.error)
                except KeyError:
                    data[tgt.name] = {"predicted": [], "actual": []}
                except AttributeError:
                    pass

    sortfunc = lambda d: mean(d["actual"])-mean(d["predicted"])
    values = sorted(data.values(), key=sortfunc)

    x = range(len(values))
    y = np.array([sortfunc(d) for d in values])
    a = np.array([mean(d["actual"]) for d in values])
    e = np.array([error for i in values])
    z = np.array([0.0 for i in values])

    fig, spls = plt.subplots(2, 1)

    avp = spls[0]
    avp.xaxis.set_major_locator(pltckr.NullLocator())
    avp.set_xlabel("Link targets", fontsize=18)
    avp.set_ylabel("(Actual - Predicted) memory usage [GB]", fontsize=18)
    avp.grid()

    act = spls[1]
    act.xaxis.set_major_locator(pltckr.NullLocator())
    act.set_xlabel("Link targets", fontsize=18)
    act.set_ylabel("Actual memory usage [GB]", fontsize=18)
    act.grid()

    avp.fill_between(
        x, y, e,
        where=(e <= y),
        interpolate=True,
        color="red",
        alpha=0.7
    )
    avp.fill_between(
        x, y, e,
        where=(y < e),
        interpolate=True,
        color="green",
        alpha=0.3
    )
    avp.plot(x, y, color="black")
    avp.scatter(x, y, color="black")
    avp.plot(x, e, color="red")
    avp.plot(x, z, color="black")

    act.plot(x, a, color="black")
    act.scatter(x, a, color="black")

    options.finalize(plt)
# ------------------------------------------------------------------------------
def main():
    do_plot(make_argparser().make_options())
    return 0
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    exit(main())
# ------------------------------------------------------------------------------
