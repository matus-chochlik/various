# coding=utf-8
#------------------------------------------------------------------------------#
import os
import time
import fuse
import errno
from .item import RelFuseItem
#------------------------------------------------------------------------------#
class MountedDirRepoItem(RelFuseItem):
    # --------------------------------------------------------------------------
    def __init__(self, item_source_path):
        RelFuseItem.__init__(self)
        self._source_path = item_source_path

    # --------------------------------------------------------------------------
    def find_item(self, split_path):
        if not split_path or split_path == ["."]:
            return self
        sub_path = os.path.join(self._source_path, split_path[0])
        if os.path.isdir(sub_path):
            return MountedDirRepoItem(sub_path).find_item(split_path[1:])

    # --------------------------------------------------------------------------
    def readdir(self, fh):
        yield ".."
        yield "."
        for name in os.listdir(self._source_path):
            if os.path.isdir(os.path.join(self._source_path, name)):
                if not name.startswith('.'):
                    yield name

    # --------------------------------------------------------------------------
    def access(self, mode):
        if mode & os.X_OK:
            return 0
        return RelFuseItem.access(self, mode)

    # --------------------------------------------------------------------------
    def _get_mode(self):
        return 0o40550

#------------------------------------------------------------------------------#
class MountedDirRepo(MountedDirRepoItem):
    # --------------------------------------------------------------------------
    def __init__(self, mount_source_path):
        MountedDirRepoItem.__init__(self, mount_source_path)
#------------------------------------------------------------------------------#
