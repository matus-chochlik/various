#!/usr/bin/env python
# coding=utf-8
#
# requires fusepy
#------------------------------------------------------------------------------#

import os
import sys
import time
import fuse
import errno
import operator
from functools import reduce
#
import relfs

# ------------------------------------------------------------------------------
# RelFs setting
# ------------------------------------------------------------------------------
class RelFsSetting(object):
    # --------------------------------------------------------------------------
    def __init__(self, initial):
        self._setting = initial 

    # --------------------------------------------------------------------------
    def set_value(self, newValue):
        self._setting = type(self._setting)(newValue)

    # --------------------------------------------------------------------------
    def get_value(self):
        return self._setting
# ------------------------------------------------------------------------------
# RelFs readout
# ------------------------------------------------------------------------------
class RelFsReadout(object):
    # --------------------------------------------------------------------------
    def __init__(self, function):
        self._function = function

    # --------------------------------------------------------------------------
    def get_value(self):
        return self._function()
# ------------------------------------------------------------------------------
# RelFs readouts
# ------------------------------------------------------------------------------
class RelFs(object):
    # --------------------------------------------------------------------------
    def __init__(self):
        self._test_value = RelFsSetting(10)

        self._settings = {
            "test": self._test_value
        }

        self._readouts = {
            "test": RelFsReadout(self._test_value.get_value)
        }

        self._items = {
            ".relfs": {
                "settings": self._settings,
                "stats": self._readouts
            }
        }

    # --------------------------------------------------------------------------
    def update(self):
        pass

    # --------------------------------------------------------------------------
    def find_item(self, entries):
        try:
            return reduce(operator.getitem, entries, self._items)
        except KeyError:
            return None

# ------------------------------------------------------------------------------
# Filesystem driver
# ------------------------------------------------------------------------------
class RelFsFuse(fuse.Operations):

    # --------------------------------------------------------------------------
    def __init__(self, options):
        self._relfs = RelFs()
        self._mount_time = time.time()
        self._open_files = dict()

    # --------------------------------------------------------------------------
    def _find_dir_entry(self, path):
        path_entries = filter(bool, path.lstrip(os.sep).split(os.sep))
        item = self._relfs.find_item(path_entries)
        if item is not None:
            return item
        raise fuse.FuseOSError(errno.ENOENT)

    # --------------------------------------------------------------------------
    def _update(self):
        self._relfs.update()

    # --------------------------------------------------------------------------
    # Filesystem methods
    # --------------------------------------------------------------------------
    def access(self, path, mode):
        self._update()
        item = self._find_dir_entry(path)
        if mode & os.R_OK:
            return 0
        if mode & os.W_OK:
            if type(item) is RelFsSetting:
                return 0
        if mode & os.X_OK:
            if type(item) is dict:
                return 0
        raise fuse.FuseOSError(errno.EACCES)

    # --------------------------------------------------------------------------
    def chmod(self, path, mode):
        self._update()
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def chown(self, path, uid, gid):
        self._update()
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def _getMode(self, item):
        if type(item) is RelFsSetting:
            return 0o100640
        if type(item) is RelFsReadout:
            return 0o100440
        return 0o40550

    # --------------------------------------------------------------------------
    def _getSize(self, item):
        if type(item) is RelFsSetting:
            return len(str(item.get_value()))
        if type(item) is RelFsReadout:
            return len(str(item.get_value()))+1
        return 0

    # --------------------------------------------------------------------------
    def getattr(self, path, fh=None):
        self._update()
        item = self._find_dir_entry(path)
        return {
            "st_size": self._getSize(item),
            "st_mode": self._getMode(item),
            "st_uid": os.getuid(),
            "st_gid": os.getgid(),
            "st_nlink": 1,
            "st_atime": time.time(),
            "st_mtime": time.time(),
            "st_ctime": self._mount_time}

    # --------------------------------------------------------------------------
    def readdir(self, path, fh):
        self._update()
        yield "."
        yield ".."

        for name in self._find_dir_entry(path):
            yield name

    # --------------------------------------------------------------------------
    def readlink(self, path):
        self._update()
        raise fuse.FuseOSError(errno.EINVAL)

    # --------------------------------------------------------------------------
    def mknod(self, path, mode, dev):
        self._update()
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def rmdir(self, path):
        self._update()
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def mkdir(self, path, mode):
        self._update()
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def statfs(self, path):
        self._update()
        return {
            'f_bsize': 32,
            'f_frsize': 32,
            'f_bavail': 0,
            'f_favail': 0,
            'f_bfree': 0,
            'f_ffree': 0,
            'f_blocks': 0,
            'f_files': 0,
            'f_flag': 4096,
            'f_namemax': 255}

    # --------------------------------------------------------------------------
    def unlink(self, path):
        self._update()
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def symlink(self, name, target):
        self._update()
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def rename(self, old, new):
        self._update()
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def link(self, target, name):
        self._update()
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def utimens(self, path, times=None):
        self._update()
        return time.time()

    # --------------------------------------------------------------------------
    # File methods
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    class OpenFileInfo(object):
        # ----------------------------------------------------------------------
        def __init__(self, item):
            self.item = item
            self.dirty = False
            if type(item) is RelFsSetting:
                self.content = str(item.get_value())
            elif type(item) is RelFsReadout:
                self.content = str(item.get_value())+'\n'
            else:
                self.content = None

    # --------------------------------------------------------------------------
    def _get_free_fd(self):
        try:
            return max(self._open_files, key=self._open_files.get)
        except ValueError:
            return 3
    # --------------------------------------------------------------------------
    def _get_open_file(self, fh):
        try:
            return self._open_files[fh]
        except KeyError:
            raise fuse.FuseOSError(errno.EBADF)
    # --------------------------------------------------------------------------
    def _remove_open_file(self, fh):
        del self._open_files[fh]

    # --------------------------------------------------------------------------
    def open(self, path, flags):
        self._update()
        item = self._find_dir_entry(path)

        if type(item) is dict:
            raise fuse.FuseOSError(errno.EISDIR)

        fd = self._get_free_fd()
        self._open_files[fd] = self.OpenFileInfo(item)
        return fd

    # --------------------------------------------------------------------------
    def create(self, path, mode, fi=None):
        self._update()
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def read(self, path, length, offset, fh):
        self._update()
        return self._get_open_file(fh).content[offset:offset+length]

    # --------------------------------------------------------------------------
    def write(self, path, buf, offset, fh):
        self._update()
        fileInfo = self._get_open_file(fh)
        if type(fileInfo.item) is RelFsSetting:
            fileInfo.dirty = True
            fileInfo.content = fileInfo.content[0:offset] + buf
            return len(buf)
        raise fuse.FuseOSError(errno.EPERM)

    # --------------------------------------------------------------------------
    def truncate(self, path, length, fh=None):
        self._update()
        if fh is None:
            fh = self.open(path, 0)

        fileInfo = self._get_open_file(fh)
        if type(fileInfo.item) is RelFsSetting:
            fileInfo.dirty = True
            fileInfo.content = fileInfo.content[0:length]
        else:
            raise fuse.FuseOSError(errno.EPERM)

    # --------------------------------------------------------------------------
    def release(self, path, fh):
        self._update()
        fileInfo = self._get_open_file(fh)
        if type(fileInfo.item) is RelFsSetting:
            if fileInfo.dirty:
                try:
                    fileInfo.item.set_value(fileInfo.content)
                except ValueError:
                    raise fuse.FuseOSError(errno.EINVAL)
        self._remove_open_file(fh)

    # --------------------------------------------------------------------------
    def flush(self, path, fh):
        self._update()
        fileInfo = self._get_open_file(fh)
        if type(fileInfo.item) is RelFsSetting:
            if fileInfo.dirty and len(fileInfo.content) > 0:
                try:
                    fileInfo.item.set_value(fileInfo.content)
                    fileInfo.dirty = False
                except ValueError:
                    raise fuse.FuseOSError(errno.EINVAL)

    # --------------------------------------------------------------------------
    def fsync(self, path, fdatasync, fh):
        self._update()

# ------------------------------------------------------------------------------
def make_arg_parser():

    arg_setup = relfs.ArgumentSetup()
    arg_setup.with_repo_names = True
    arg_setup.existing_repos = True
    arg_setup.at_least_one_repo = True
    arg_setup.with_mount_point = True

    parser = relfs.make_argument_parser(
        os.path.basename(__file__),
        'relfs fuse filesystem driver',
        arg_setup
    )
    return parser

# ------------------------------------------------------------------------------
def main():
    options = make_arg_parser().parse_args()
    fuse.FUSE(
        RelFsFuse(options),
        options.mount_point,
        nothreads=True,
        nonempty=True,
        foreground=True)

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
# ------------------------------------------------------------------------------
