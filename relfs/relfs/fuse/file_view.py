# coding=utf-8
#------------------------------------------------------------------------------#
import os
import time
import fuse
import errno
from .item import RelFuseItem
#------------------------------------------------------------------------------#
class FileView(RelFuseItem):
    # --------------------------------------------------------------------------
    def __init__(self, path_getter):
        RelFuseItem.__init__(self)
        self._path_getter = path_getter
        self._fd = None

    # --------------------------------------------------------------------------
    def _get_mode(self):
        return 0o100440

    # --------------------------------------------------------------------------
    def _get_size(self):
        if not self._fd:
            return os.stat(self._path_getter()).st_size
        return os.fstat(self._fd).st_size

    # --------------------------------------------------------------------------
    def open(self, flags):
        if flags & (os.O_CREAT | os.O_WRONLY | os.O_APPEND | os.O_TRUNC):
            raise fuse.FuseOSError(errno.EACCES)

        self._fd = os.open(self._path_getter(), (os.O_RDONLY | flags))
        return self._fd

    # --------------------------------------------------------------------------
    def read(self, length, offset):
        if not self._fd:
            raise fuse.FuseOSError(errno.EBADFD)

        os.lseek(self._fd, offset, os.SEEK_SET)
        return os.read(self._fd, length)

    # --------------------------------------------------------------------------
    def release(self):
        fd = self._fd
        self._fd = None
        return os.close(fd)

#------------------------------------------------------------------------------#
