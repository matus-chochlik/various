#!/usr/bin/env python3
# coding=utf-8
# Copyright Matus Chochlik.
# Distributed under the Boost Software License, Version 1.0.
# See accompanying file LICENSE_1_0.txt or copy at
#  http://www.boost.org/LICENSE_1_0.txt
#
import os
import sys
from PIL import Image as pilImage
from PIL import UnidentifiedImageError
import pathlib
import zipfile
import argparse

# ------------------------------------------------------------------------------
#  Argument parser
# ------------------------------------------------------------------------------
class ArgumentParser(argparse.ArgumentParser):
    # -------------------------------------------------------------------------
    def __init__(self, **kw):
        argparse.ArgumentParser.__init__(self, **kw)

        self.add_argument(
            "--input", "-i",
            metavar='INPUT-FILE',
            dest='input_path',
            nargs='?',
            type=os.path.realpath,
            default=None
        )

        self.add_argument(
            "--output", "-o",
            metavar='OUTPUT-FILE',
            dest='output_path',
            nargs='?',
            type=os.path.realpath,
            default=None
        )

    # -------------------------------------------------------------------------
    def processParsedOptions(self, options):
        if options.output_path is None:
            options.output_path =\
                pathlib.Path(options.input_path).with_suffix(".cbz")
        return options

    # -------------------------------------------------------------------------
    def parseArgs(self):
        return self.processParsedOptions(
            argparse.ArgumentParser.parse_args(self)
        )

# ------------------------------------------------------------------------------
def getArgumentParser():
    return ArgumentParser(
        prog=os.path.basename(__file__),
        description="""
        Extracts images from an .epub archive and re-packs them into a .cbz archive
        """
    )
# ------------------------------------------------------------------------------
def findImages(options):
    with zipfile.ZipFile(options.input_path, "r") as source:
        for name in source.namelist():
            if name.startswith("EPUB/"):
                try:
                    with source.open(name) as zipped:
                        with pilImage.open(zipped) as image:
                            pass
                        zipped.seek(0)
                        print(name)
                        yield name, zipped.read()
                except UnidentifiedImageError:
                    pass

# ------------------------------------------------------------------------------
def convert(options):
    with zipfile.ZipFile(options.output_path, "w", zipfile.ZIP_DEFLATED) as destination:
        for name, data in findImages(options):
            destination.writestr(os.path.basename(name), data)
        for zfile in destination.filelist:
            zfile.create_system = 0 

# ------------------------------------------------------------------------------
#  main
# ------------------------------------------------------------------------------
def main():
    debug = False
    try:
        options = getArgumentParser().parseArgs()
        convert(options)
        return 0
    except Exception as error:
        try: os.remove(options.output_path)
        except: pass
        if debug:
            raise
        else:
            print(type(error), error)
        return 1

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    sys.exit(main())

