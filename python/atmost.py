#!/usr/bin/env python
#coding=utf8

from __future__ import print_function

import os
import sys
import argparse
import subprocess
import posix_ipc
import hashlib

# ------------------------------------------------------------------------------
def print_error(error):
    print("atmost error: %s" % (str(error)), file=sys.stderr)
#------------------------------------------------------------------------------#
def which(executable):
    path=os.getenv('PATH')
    for path in path.split(os.path.pathsep):
        path = os.path.join(path,executable)
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
#------------------------------------------------------------------------------#
class __AtMostArgumentParser(argparse.ArgumentParser):

    # --------------------------------------------------------------------------
    def __init__(self, **kw):
        argparse.ArgumentParser.__init__(self, **kw)

        def _positive_int(s):
            try:
                n = int(s)
                assert(n > 0)
                return n
            except:
                self.error("`%s' is not a positive integer value" % str(x))

        self.add_argument(
            '-n', '--limit',
            dest='limit',
            metavar='PROCESS-COUNT',
            nargs='?',
            type=_positive_int,
            default=None
        )

        self.add_argument(
            dest="command_line",
            nargs=argparse.REMAINDER,
            default=list(),
            help="""The command to execute."""
        )

    # --------------------------------------------------------------------------
    def process_parsed_options(self, options):

        if options.limit is None:
            options.limit = 2
            try:
                import multiprocessing
                options.limit = multiprocessing.cpu_count()
            except ModuleNotFoundError: pass
            except ImportError: pass

        return options


    # --------------------------------------------------------------------------
    def parse_args(self):
        return self.process_parsed_options(
            argparse.ArgumentParser.parse_args(self)
        )

# ------------------------------------------------------------------------------
def make_argparser():
    return __AtMostArgumentParser(
        prog="atmost",
        description="""
        Limits the number of cuncurrently running instances of a specific
        executable
        """
    )
# ------------------------------------------------------------------------------
def execute(options):
    try:
        exe_path = which(options.command_line[0])
        if exe_path is None:
            print_error("command '%s' not found" % (options.command_line[0]))
            return 2
    except IndexError as index_error:
        print_error("empty command line given")
        return 1

    sem_name = '/' + hashlib.md5(exe_path.encode()).hexdigest()

    semaphore = posix_ipc.Semaphore(
        name = sem_name,
        flags = posix_ipc.O_CREAT,
        initial_value = options.limit
    )
    semaphore.acquire();

    result = 100
    try:
        result = subprocess.call(options.command_line)
    except Exception as error:
        print_error(error)

    semaphore.release();
    semaphore.close()
    return result
# ------------------------------------------------------------------------------
def main():
    return execute(make_argparser().parse_args())
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    exit(main())
