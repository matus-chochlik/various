#!/usr/bin/python3 -B
# coding: UTF-8
#  Copyright (c) 2019 Matus Chochlik
import os
import sys
import csv
import gzip
import json
import glob
import math
import queue
import pandas
import pickle
import argparse
import threading
import multiprocessing

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
            "--input-chunk-size", "-S",
            nargs='?',
            dest="input_chunk_size",
            type=self._size_bytes,
            default=1024*8,
            action="store"
        )

        self.add_argument(
            "--output-chunk-size", "-C",
            nargs='?',
            dest="output_chunk_size",
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

        self.add_argument(
            "--load-threads", "-L",
            nargs='?',
            dest="load_threads",
            type=self._positive_int,
            default=multiprocessing.cpu_count()+1,
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

        options.chunk_gib_mult = options.output_chunk_size/float(1024**3)

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
class LoadThread(threading.Thread):
    def __init__(self, transforms, tid, input_queue, output_queue):
        self._transforms = transforms
        self._id = tid
        self._input = input_queue
        self._output = output_queue
        threading.Thread.__init__(self,target=self._run)
        threading.Thread.start(self)

    # ----------------------------------------------------------------------
    def _open_json(self, filepath):
        try: return gzip.open(filepath, mode="rt")
        except: return open(filepath, mode="rt")

    # ----------------------------------------------------------------------
    def _transform_attrib(self, dataset, name, transf):
        for row in dataset:
            try: yield transf(row[name])
            except KeyError: pass
            except TypeError: pass

    # ----------------------------------------------------------------------
    def _load_json_data(self, filepath):
        try:
            with self._open_json(filepath) as jsonfile:
                dataset = json.load(jsonfile)
                result = dict()
                for name, transf in self._transforms:
                    result[name] = [
                        val for val in self._transform_attrib(
                            dataset,
                            name,
                            transf
                        )
                    ]
                return result
        except Exception as error:
            print("error: %s" % error)

    # ----------------------------------------------------------------------
    def _load_dataframes(self, filepath):
        d = self._load_json_data(filepath)
        try: yield pandas.DataFrame.from_dict(d)
        except KeyError: pass
        except Exception as error:
            print("error: %s" % error)

    # ----------------------------------------------------------------------
    def _process_input(self, filepath):
        return pandas.concat(self._load_dataframes(filepath))

    # ----------------------------------------------------------------------
    def _run(self):
        while True:
            filepath = self._input.get()
            if filepath is None:
                self._output.put(None)
                break
            self._output.put(self._process_input(filepath))

# ------------------------------------------------------------------------------
def load_dataframes(options, transforms):
    input_paths = queue.Queue()
    output_frames = queue.Queue()
    load_threads = [
        LoadThread(transforms, tid, input_paths, output_frames)
        for tid in range(options.load_threads)
    ]

    for filepath in options.input_paths:
        input_paths.put(filepath)

    for lt in load_threads:
        input_paths.put(None)

    remaining = options.load_threads

    while remaining:
        dataframe = output_frames.get()
        if dataframe is None:
            remaining -= 1
        else: 
            yield dataframe

    for lt in load_threads:
        lt.join()

# ------------------------------------------------------------------------------
def load_dataframe(options, transforms):
    return pandas.concat(load_dataframes(options, transforms))

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
        hidden_layer_sizes=(85, 65, 45),
        activation="relu"
    )

    transforms = [
        ("opt", lambda x: float(x)),
        ("pie", lambda x: float(x)),
        ("no_mmap_whole_files", lambda x: float(x)),
        ("no_mmap_output_file", lambda x: float(x)),
        ("static_count", lambda x: float(x)),
        ("static_size", lambda x: math.ceil(float(x)/options.input_chunk_size)),
        ("shared_count", lambda x: float(x)),
        ("shared_size", lambda x: math.ceil(float(x)/options.input_chunk_size)),
        ("memory_size", lambda x: int(math.ceil(float(x) / options.output_chunk_size)))
    ]

    data = load_dataframe(options, transforms).drop_duplicates()
    x = data.drop(["memory_size"], axis=1)
    fields = list(x.columns.values)
    y = data["memory_size"]
    scaler.fit(x)
    x = scaler.transform(x)
    model.partial_fit(x, y, range(0, 64))

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
        "input_chunk_size": options.input_chunk_size,
        "output_chunk_size": options.output_chunk_size
    }
    pickle.dump(archive, gzip.open(options.output_path, "wb"))
# ------------------------------------------------------------------------------
def main():
    sys.exit(train_model(make_argparser().parse_args()))
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
# ------------------------------------------------------------------------------
