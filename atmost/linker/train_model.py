# coding: UTF-8
#  Copyright (c) 2019 Matus Chochlik
import os
import sys
import csv
import gzip
import json
import glob
import math
import pandas
import pickle
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
            i = int(x)
            assert(i > 0)
            return i
        except:
            self.error("`%s' is not a positive integer value" % str(x))

    # --------------------------------------------------------------------------
    def _confidence(self, x):
        try:
            c = float(x)
            assert(c > 0.0 and c <= 1.0)
            return c
        except:
            self.error("`%s' is not a valid confidence value" % str(x))

    # --------------------------------------------------------------------------
    def __init__(self, **kw):
        argparse.ArgumentParser.__init__(self, **kw)

        self.add_argument(
            "--output", "-o",
            metavar="OUTPUT-PATH",
            nargs='?',
            dest="output_path",
            default=None,
            help="output file path"
        )

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
            default=1024*1024*256,
            action="store"
        )

        self.add_argument(
            "--min-confidence", "-c",
            nargs='?',
            dest="min_confidence",
            type=self._confidence,
            default=None,
            action="store"
        )

        self.add_argument(
            "--repeat-count", "-R",
            nargs='?',
            dest="repeat_count",
            type=self._positive_int,
            default=12,
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

        if options.output_path is None:
            options.output_path = os.path.realpath("atmost.linker.pickle.gz")

        options.chunk_gib_mult = options.chunk_size/float(1024**3)

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
def load_json_data(options):
    transforms = [
        ("opt", lambda x: float(x)),
        ("pie", lambda x: float(x)),
        ("static_count", lambda x: float(x)),
        ("static_size", lambda x: float(x)),
        ("shared_count", lambda x: float(x)),
        ("shared_size", lambda x: float(x)),
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
def load_dataframes(options):
    for d in load_json_data(options):
        try: yield pandas.DataFrame.from_dict(d)
        except KeyError: pass
        except Exception as error:
            print("error: %s" % error)

# ------------------------------------------------------------------------------
def load_dataframe(options):
    return pandas.concat(load_dataframes(options))

# ------------------------------------------------------------------------------
def single_train_pass(options, model, x, y):
    from sklearn.metrics import accuracy_score

    pdiffs = []
    ndiffs = []

    model.partial_fit(x, y)
    p = model.predict_proba(x)
    for pprobs, yval in zip(p, y):
        ypred = sum(pprob*pval for pprob, pval in zip(pprobs, model.classes_))
        diff = ypred - yval
        if diff > 0.0:
            pdiffs.append(diff)
        else:
            ndiffs.append(diff)
    acc = accuracy_score(model.predict(x), y)

    def _stat(diffs):
        try: return math.sqrt(sum(x*x for x in diffs)/len(diffs))
        except ZeroDivisionError:
            return 0.0

    return (acc, -_stat(ndiffs), +_stat(pdiffs))

# ------------------------------------------------------------------------------
def train_model(options):
    from sklearn.preprocessing import StandardScaler
    from sklearn.neural_network import MLPClassifier

    scaler = StandardScaler()
    model = MLPClassifier(
        hidden_layer_sizes=(55, 34),
        activation="relu"
    )

    data = load_dataframe(options)
    x = data.drop(["memory_size"], axis=1)
    fields = list(x.columns.values)
    y = data["memory_size"]
    scaler.fit(x)
    x = scaler.transform(x)
    model.partial_fit(x, y, xrange(0, 64))

    fmt = "%4.3f|%6.2f|%5.2f|"
    steps = 0

    if options.min_confidence is not None:
        while True:
            result = single_train_pass(options, model, x, y)
            steps += 1
            print(fmt % result)
            if result[0] >= options.min_confidence:
                break
    else:
        for i in xrange(options.repeat_count):
            result = single_train_pass(options, model, x, y)
            steps += 1
            print(fmt % result)

    archive = {
        "fields": fields,
        "steps": steps,
        "model": model,
        "scaler": scaler,
        "confidence": result[0],
        "error_margin": -result[1],
        "chunk_size": options.chunk_size
    }
    pickle.dump(archive, gzip.open(options.output_path, "wb"))
# ------------------------------------------------------------------------------
def main():
    sys.exit(train_model(make_argparser().parse_args()))
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
# ------------------------------------------------------------------------------
