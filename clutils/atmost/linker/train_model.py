# coding: UTF-8
#  Copyright (c) 2019 Matus Chochlik
import os
import sys
import csv
import json
import glob
import math
import pandas
import argparse

# ------------------------------------------------------------------------------
class TrainModelArgumentParser(argparse.ArgumentParser):
    # --------------------------------------------------------------------------
    def _size_bytes(self, x):
        try:
            return long(x)
        except ValueError:
            self.error("invalid size in bytes '%s'" % x)

    # --------------------------------------------------------------------------
    def _positive_int(self, x):
        try:
            assert(int(x) > 0)
            return int(x)
        except:
            self.error("`%s' is not a positive integer value" % str(x))

    # --------------------------------------------------------------------------
    def __init__(self, **kw):
        argparse.ArgumentParser.__init__(self, **kw)

        self.add_argument(
            "--input", "-i",
            metavar='INPUT-PATH',
            nargs='?',
            dest="input_args",
            default=list(),
            action="append"
        )

        self.add_argument(
            "arguments",
            metavar="INPUT-PATH",
            nargs='*',
            type=str,
            help="input JSON files"
        )

        self.add_argument(
            "--chunk-size", "-C",
            nargs='?',
            dest="chunk_size",
            type=self._size_bytes,
            default=1024*1024*1024,
            action="store"
        )

        self.add_argument(
            "--repeat-count", "-R",
            nargs='?',
            dest="repeat_count",
            type=self._positive_int,
            default=24,
            action="store"
        )

    # --------------------------------------------------------------------------
    def process_parsed_options(self, options):
        options.input_paths = list()

        _not_file_fmt = "'%s' is not a file path or pattern"
        for arg in options.input_args + options.arguments:
            if os.path.isfile(arg):
                options.input_paths.append(arg)
            else:
                for path in glob.glob(arg):
                    if os.path.isfile(path):
                        options.input_paths.append(path)
                    else:
                        self.error(_not_file_fmt % (path,))

        options.input_paths =\
            list(set(os.path.realpath(x) for x in options.input_paths))

        del options.__dict__["input_args"]
        del options.__dict__["arguments"]

        return options

    # --------------------------------------------------------------------------
    def parse_args(self):
        return self.process_parsed_options(
            argparse.ArgumentParser.parse_args(self)
        )

# ------------------------------------------------------------------------------
def make_argparser():
    return TrainModelArgumentParser(
        prog="train_model",
        description="""
        Trains a ML model for the atmost linker callbacks script.
        """
    )

# ------------------------------------------------------------------------------
def get_json_data(options):
    transforms = [
        ("opt", lambda x: x),
        ("pie", lambda x: x),
        ("static_count", lambda x: x),
        ("static_size", lambda x: x),
        ("shared_count", lambda x: x),
        ("shared_size", lambda x: x),
        ("memory_size", lambda x: int(math.ceil(float(x) / options.chunk_size)))
    ]
    for filepath in options.input_paths:
        try:
            with open(filepath, mode="rt") as jsonfile:
                for row in json.load(jsonfile):
                    try:
                        yield dict(
                            (name, [transf(row[name])]) \
                            for name, transf in transforms
                        )
                    except KeyError: pass
                    except TypeError: pass
        except Exception as error:
            print(error)

# ------------------------------------------------------------------------------
def train_model(options):
    from sklearn.preprocessing import StandardScaler
    from sklearn.neural_network import MLPClassifier
    from sklearn.metrics import accuracy_score

    model = MLPClassifier()
    scaler = StandardScaler()

    for d in get_json_data(options):
        try:
            df = pandas.DataFrame.from_dict(d)
            x = df.drop(["memory_size"], axis=1)
            scaler.partial_fit(x)
        except: pass

    _1GiB = 1024.0*1024.0*1024.0
    rng = 64
    cls = xrange(rng);

    ssum = 0.0
    scnt = 1.0
    maxd = 0
    mind = 0

    for i in xrange(options.repeat_count):
        print(
            "run: %5d (%1.3f, %7.3f, %7.3f)" % (
                i,
                ssum/scnt,
                mind*options.chunk_size/_1GiB,
                maxd*options.chunk_size/_1GiB
            ))
        ssum = 0.0
        scnt = 1.0
        maxd = -rng
        mind = +rng

        for d in get_json_data(options):
            df = pandas.DataFrame.from_dict(d)
            try:
                x = df.drop(["memory_size"], axis=1)
                y = df["memory_size"]
                x = scaler.transform(x)

                p = 0
                try:
                    p = model.predict(x)
                    ssum += accuracy_score(y, p);
                    scnt += 1.0
                except: pass

                diff = p - y[0]
                maxd = max(maxd, diff)
                mind = min(mind, diff)

                model.partial_fit(x, y, classes = cls)

            except KeyError as err:
                print(err)
# ------------------------------------------------------------------------------
def main():
    sys.exit(train_model(make_argparser().parse_args()))
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
# ------------------------------------------------------------------------------
