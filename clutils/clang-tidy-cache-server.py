#!/usr/bin/env python3
# coding: UTF-8
# Copyright (c) 2020 Matus Chochlik

import os
import re
import json
import time
import gzip
import flask
import argparse 

# ------------------------------------------------------------------------------
class ArgumentParser(argparse.ArgumentParser):
    # -------------------------------------------------------------------------
    def __init__(self, **kw):
        argparse.ArgumentParser.__init__(self, **kw)

        def save_interval(x):
            try:
                p = float(x)
                if (p > 10.0):
                    return p
                self.error("'%f' is not a valid save interval" % (p))
            except TypeError:
                self.error("save interval must be a numeric value" )

        def port_number(x):
            try:
                p = int(x)
                if (p > 1) and (p < 2**16):
                    return p
                self.error("'%d' is not a valid port number" % (p))
            except TypeError:
                self.error("port number must be an integer value" )

        self.add_argument(
            "--port", "-P",
            dest="port_number",
            metavar="NUMBER",
            type=port_number,
            default=None,
            help="""
            Specifies the port number (5000) by default.
            """ 
        )

        self.add_argument(
            "--save-path", "-S",
            dest="save_path",
            metavar="NUMBER",
            type=os.path.realpath,
            default=os.path.join(os.path.expanduser("~"), ".ctcache_db"),
            help="""
            Specifies the path to the persistent save file.
            """ 
        )

        self.add_argument(
            "--save-interval", "-I",
            dest="save_interval",
            metavar="NUMBER",
            type=save_interval,
            default=600,
            help="""
            Specifies the save time interval.
            """ 
        )

    # -------------------------------------------------------------------------
    def process_parsed_options(self, options):
        return options

    # -------------------------------------------------------------------------
    def parse_args(self):
        return self.process_parsed_options(
            argparse.ArgumentParser.parse_args(self)
        )

# ------------------------------------------------------------------------------
def get_argument_parser():
    return ArgumentParser(
        prog=os.path.basename(__file__),
        description="""server maintaining cached values for clang-tidy-cache"""
    )
# ------------------------------------------------------------------------------
class ClangTidyCache(object):
    # --------------------------------------------------------------------------
    def __init__(self, options):
        self._hits_count = 0
        self._miss_count = 0
        self._cached = dict()
        self._save_path = options.save_path
        self._save_interval = options.save_interval
        self._save_time = time.time()
        #
        self._hash_re = re.compile(r'^[0-9a-fA-F]{40}$')
        #
        self.do_load()

    # --------------------------------------------------------------------------
    def maintain(self):
        if self.saved_seconds_ago() > self._save_interval:
            self.do_save()
            self._save_time = time.time()

    # --------------------------------------------------------------------------
    def do_load(self):
        try:
            with gzip.open(self._save_path, 'rt', encoding="utf8") as dbf:
                for hashstr, data in json.load(dbf).items():
                    if self.is_valid_hash(hashstr):
                        try:
                            info = self._cached[hashstr] = dict()
                            info["hits"] = data["hits"]
                            info["insert_time"] = data["insert_time"]
                            info["access_time"] = data["access_time"]
                        except KeyError:
                            pass
        except Exception as err:
            pass

    # --------------------------------------------------------------------------
    def do_save(self):
        try:
            with gzip.open(self._save_path, 'wt', encoding="utf8") as dbf:
                json.dump(self._cached, dbf)
        except:
            pass

    # --------------------------------------------------------------------------
    def is_valid_hash(self, hashstr):
        return self._hash_re.match(hashstr)

    # --------------------------------------------------------------------------
    def cache(self, hashstr):
        try:
            info = self._cached[hashstr]
            info["access_time"] = time.time()
            info["hits"] += 1
        except KeyError:
            self._cached[hashstr] = {
                "insert_time": time.time(),
                "access_time": time.time(),
                "hits": 1,
            }
            self.maintain()

    # --------------------------------------------------------------------------
    def is_cached(self, hashstr):
        try:
            self._cached[hashstr]["hits"] += 1
            self._hits_count += 1
            return True
        except KeyError:
            self._miss_count += 1
            return False

    # --------------------------------------------------------------------------
    def saved_seconds_ago(self):
        return time.time() - self._save_time

    # --------------------------------------------------------------------------
    def cached_count(self):
        return len(self._cached)

    # --------------------------------------------------------------------------
    def hit_count(self):
        return self._hits_count

    # --------------------------------------------------------------------------
    def miss_count(self):
        return self._miss_count

    # --------------------------------------------------------------------------
    def hit_rate(self):
        try:
            return self._hits_count / (self._hits_count + self._miss_count)
        except ZeroDivisionError:
            return None

    # --------------------------------------------------------------------------
    def miss_rate(self):
        try:
            return self._miss_count / (self._hits_count + self._miss_count)
        except ZeroDivisionError:
            return None

# ------------------------------------------------------------------------------
clang_tidy_cache = None
ctcache_app = flask.Flask("clang-tidy-cache")
# ------------------------------------------------------------------------------
@ctcache_app.route("/cache/<hashstr>")
def ctc_cache(hashstr):
    if clang_tidy_cache.is_valid_hash(hashstr):
        clang_tidy_cache.cache(hashstr)
        return "true"
    else:
        return "invalid hash"
# ------------------------------------------------------------------------------
@ctcache_app.route("/is_cached/<hashstr>")
def ctc_is_cached(hashstr):
    return "true" if clang_tidy_cache.is_cached(hashstr) else "false"
# ------------------------------------------------------------------------------
@ctcache_app.route("/stats/cached_count")
def ctc_status_cached_count():
    return str(clang_tidy_cache.cached_count())
# ------------------------------------------------------------------------------
@ctcache_app.route("/stats/hit_count")
def ctc_status_hit_count():
    return str(clang_tidy_cache.hit_count())
# ------------------------------------------------------------------------------
@ctcache_app.route("/stats/miss_count")
def ctc_status_miss_count():
    return str(clang_tidy_cache.miss_count())
# ------------------------------------------------------------------------------
@ctcache_app.route("/stats/hit_rate")
def ctc_status_hit_rate():
    return str(clang_tidy_cache.hit_rate())
# ------------------------------------------------------------------------------
@ctcache_app.route("/stats/miss_rate")
def ctc_status_miss_rate():
    return str(clang_tidy_cache.miss_rate())
# ------------------------------------------------------------------------------
@ctcache_app.route("/stats")
def ctc_status():
    stat_getters = {
        "saved_seconds_ago": clang_tidy_cache.saved_seconds_ago,
        "hit_count": clang_tidy_cache.hit_count,
        "hit_rate": clang_tidy_cache.hit_rate,
        "miss_count": clang_tidy_cache.miss_count,
        "miss_rate": clang_tidy_cache.miss_rate,
        "cached_count": clang_tidy_cache.cached_count
    }
    stat_values = {}
    for key, getter in stat_getters.items():
        try: value = getter()
        except: value = None

        if value is None:
            stat_values[key] = "N/A"
        else:
            stat_values[key] = value

    return json.dumps(stat_values)
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    argparser = get_argument_parser()
    options = argparser.parse_args()
    clang_tidy_cache = ClangTidyCache(options)
    ctcache_app.run(debug=False, port=options.port_number)
# ------------------------------------------------------------------------------
