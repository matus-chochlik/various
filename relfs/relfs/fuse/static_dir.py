# coding=utf-8
#------------------------------------------------------------------------------#
import os
import time
import fuse
import errno
from .item import RelFuseItem
#------------------------------------------------------------------------------#
class StaticDirectory(RelFuseItem):
    # --------------------------------------------------------------------------
    def __init__(self):
        RelFuseItem.__init__(self)
        self._items = dict()

    # --------------------------------------------------------------------------
    def add(self, name, item):
        self._items[name] = item
        return item

    # --------------------------------------------------------------------------
    def find_item(self, split_path):
        if not split_path or split_path == ["."]:
            return self
        try:
            return self._items[split_path[0]].find_item(split_path[1:])
        except KeyError:
            pass

    # --------------------------------------------------------------------------
    def readdir(self, fh):
        yield ".."
        yield "."
        for name in self._items:
            yield name

    # --------------------------------------------------------------------------
    def access(self, mode):
        if mode & os.X_OK:
            return 0
        return RelFuseItem.access(self, mode)

    # --------------------------------------------------------------------------
    def _get_mode(self):
        return 0o40550

# ------------------------------------------------------------------------------

