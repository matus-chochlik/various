# coding=utf-8
#------------------------------------------------------------------------------#
import os
import time
import fuse
import errno
from .item import RelFuseItem
#------------------------------------------------------------------------------#
class Readout(RelFuseItem):
    # --------------------------------------------------------------------------
    def __init__(self, getter):
        RelFuseItem.__init__(self)
        self._getter = getter
        self._content = None

    # --------------------------------------------------------------------------
    def _get_mode(self):
        return 0o100640

    # --------------------------------------------------------------------------
    def open(self, flags):
        self._content = str(self._getter())+'\n'
        return 0

    # --------------------------------------------------------------------------
    def _get_size(self):
        if not self._content:
            self.open(0)
        return len(self._content)

    # --------------------------------------------------------------------------
    def read(self, length, offset):
        return self._content[offset:length]

    # --------------------------------------------------------------------------
    def write(self, buf, offset):
        raise fuse.FuseOSError(errno.EPERM)

    # --------------------------------------------------------------------------
    def truncate(self, length):
        raise fuse.FuseOSError(errno.EPERM)

    # --------------------------------------------------------------------------
    def release(self):
        self._content = None

#------------------------------------------------------------------------------#
