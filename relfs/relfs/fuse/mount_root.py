# coding=utf-8
#------------------------------------------------------------------------------#
import os
import time
import fuse
import errno
from .item import RelFuseItem
from .static_dir import StaticDirectory
#------------------------------------------------------------------------------#
class MountRoot(RelFuseItem):
    # --------------------------------------------------------------------------
    def __init__(self):
        RelFuseItem.__init__(self)
        self._mount_time = time.time()
        self._relfs_dir = StaticDirectory()
        self._repos_dir = self._relfs_dir.add("repos", StaticDirectory())

    # --------------------------------------------------------------------------
    def repos_dir(self):
        return self._repos_dir

    # --------------------------------------------------------------------------
    def find_item(self, split_path):
        if not split_path or split_path == ["."]:
            return self
        if split_path[0] == ".relfs":
            return self._relfs_dir.find_item(split_path[1:])

    # --------------------------------------------------------------------------
    def readdir(self, fh):
        yield ".."
        yield "."
        yield ".relfs"

    # --------------------------------------------------------------------------
    def _modify_time(self):
        return self._mount_time

    # --------------------------------------------------------------------------
    def access(self, mode):
        if mode & os.X_OK:
            return 0
        return RelFuseItem.access(self, mode)

    # --------------------------------------------------------------------------
    def _get_mode(self):
        return 0o40550

#------------------------------------------------------------------------------#
