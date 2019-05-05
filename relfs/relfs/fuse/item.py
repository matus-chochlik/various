# coding=utf-8
#------------------------------------------------------------------------------#
import os
import time
import fuse
import errno
#------------------------------------------------------------------------------#
class RelFuseItem(object):
    # --------------------------------------------------------------------------
    def __init__(self):
        pass

    # --------------------------------------------------------------------------
    def find_item(self, split_path):
        if not split_path:
            return self
        return None

    # --------------------------------------------------------------------------
    def access(self, mode):
        if mode & os.R_OK:
            return 0
        raise fuse.FuseOSError(errno.EACCES)

    # --------------------------------------------------------------------------
    def chmod(self, mode):
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def chown(self, uid, gid):
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def _get_size(self):
        return 0

    # --------------------------------------------------------------------------
    def _get_mode(self):
        return 0o100000

    # --------------------------------------------------------------------------
    def _count_links(self):
        return 1

    # --------------------------------------------------------------------------
    def _access_time(self):
        return time.time()

    # --------------------------------------------------------------------------
    def _modify_time(self):
        return time.time()

    # --------------------------------------------------------------------------
    def _change_time(self):
        return time.time()
    
    # --------------------------------------------------------------------------
    def getattr(self, fh=None):
        return {
            "st_size": self._get_size(),
            "st_mode": self._get_mode(),
            "st_uid": os.getuid(),
            "st_gid": os.getgid(),
            "st_nlink": self._count_links(),
            "st_atime": self._access_time(),
            "st_mtime": self._modify_time(),
            "st_ctime": self._change_time()}

    # --------------------------------------------------------------------------
    def readdir(self, fh):
        pass

    # --------------------------------------------------------------------------
    def mkdir(self, name, mode):
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def removable(self):
        return False

    # --------------------------------------------------------------------------
    def unlink(self, name):
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def open(self, flags):
        raise fuse.FuseOSError(errno.EINVAL)

    # --------------------------------------------------------------------------
    def read(self, length, offset):
        raise fuse.FuseOSError(errno.EINVAL)

    # --------------------------------------------------------------------------
    def write(self, buf, offset):
        raise fuse.FuseOSError(errno.EINVAL)

    # --------------------------------------------------------------------------
    def truncate(self, length):
        raise fuse.FuseOSError(errno.EINVAL)

    # --------------------------------------------------------------------------
    def release(self):
        pass

    # --------------------------------------------------------------------------
    def flush(self):
        pass

    # --------------------------------------------------------------------------
    def fsync(self, fdatasync):
        pass
#------------------------------------------------------------------------------#

