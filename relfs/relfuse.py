#!/usr/bin/env python
# coding=utf-8
#
# requires fusepy
#------------------------------------------------------------------------------#

import os
import time
import fuse
import errno
import logging
import operator
from functools import reduce
#
import relfs.fuse as relfuse
from relfs import open_repository, RelFsError, print_error
from relfs.arguments import ArgumentSetup, make_argument_parser

# ------------------------------------------------------------------------------
# Wrapped RelFuse repository
# ------------------------------------------------------------------------------
class RelFuseRepo(object):
    # --------------------------------------------------------------------------
    def __init__(self, repos_dir, repo_name):
        self._repository = open_repository(repo_name)

        repo_dir = repos_dir.add(
            repo_name,
            relfuse.StaticDirectory())

        repo_dir.add(
            "object_count",
            relfuse.Readout(self._repository.context().object_count))

        repo_dir.add(
            "storage",
            relfuse.Symlink(self._repository.prefix))

        repo_dir.add(
            "config",
            relfuse.FileView(self._repository.config_file_path))

# ------------------------------------------------------------------------------
class RelFuse(object):
    # --------------------------------------------------------------------------
    def __init__(self, options):

        self._root = relfuse.MountRoot()
        self._repos = dict()
        for repo_name in options.repositories:
            try:
                self._repos[repo_name] = RelFuseRepo(
                    self._root.repos_dir(),
                    repo_name)
            except RelFsError as relfs_error:
                print_error(relfs_error)

    # --------------------------------------------------------------------------
    def find_item(self, split_path):
        return self._root.find_item(split_path)

# ------------------------------------------------------------------------------
# Filesystem driver
# ------------------------------------------------------------------------------
class RelFuseDriver(fuse.Operations):

    # --------------------------------------------------------------------------
    def __init__(self, options):
        self._relfs = RelFuse(options)
        self._open_files = dict()

    # --------------------------------------------------------------------------
    def _find_dir_entry(self, path):
        path_entries = filter(bool, path.lstrip(os.sep).split(os.sep))
        item = self._relfs.find_item(path_entries)
        if item is not None:
            return item
        raise fuse.FuseOSError(errno.ENOENT)

    # --------------------------------------------------------------------------
    # Filesystem methods
    # --------------------------------------------------------------------------
    def access(self, path, mode):
        return self._find_dir_entry(path).access(mode)

    # --------------------------------------------------------------------------
    def chmod(self, path, mode):
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def chown(self, path, uid, gid):
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def getattr(self, path, fh=None):
        return self._find_dir_entry(path).getattr(fh)

    # --------------------------------------------------------------------------
    def readdir(self, path, fh):
        for item in self._find_dir_entry(path).readdir(fh):
            yield item

    # --------------------------------------------------------------------------
    def readlink(self, path):
        return self._find_dir_entry(path).readlink()

    # --------------------------------------------------------------------------
    def mknod(self, path, mode, dev):
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def rmdir(self, path):
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def mkdir(self, path, mode):
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
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def symlink(self, name, target):
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def rename(self, old, new):
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def link(self, target, name):
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def utimens(self, path, times=None):
        return time.time()

    # --------------------------------------------------------------------------
    # File methods
    # --------------------------------------------------------------------------
    class OpenFileInfo(object):
        # ---------------------------------------------------------------------
        def __init__(self, item):
            self._item = item

        # ---------------------------------------------------------------------
        def __del__(self):
            self._item.release()

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
        try:
            del self._open_files[fh]
        except:
            raise fuse.FuseOSError(errno.EBADF)

    # --------------------------------------------------------------------------
    def create(self, path, mode, fi=None):
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def open(self, path, flags):
        item = self._find_dir_entry(path)
        item.open(flags)
        fd = self._get_free_fd()
        self._open_files[fd] = self.OpenFileInfo(item)
        return fd

    # --------------------------------------------------------------------------
    def read(self, path, length, offset, fh):
        return self._get_open_file(fh)._item.read(length, offset)

    # --------------------------------------------------------------------------
    def write(self, path, buf, offset, fh):
        return self._get_open_file(fh)._item.write(buf, offset)

    # --------------------------------------------------------------------------
    def truncate(self, path, length, fh=None):
        return self._get_open_file(fh)._item.truncate(length)

    # --------------------------------------------------------------------------
    def flush(self, path, fh):
        return self._get_open_file(fh)._item.flush()

    # --------------------------------------------------------------------------
    def fsync(self, path, fdatasync, fh):
        return self._get_open_file(fh)._item.fsync()

    # --------------------------------------------------------------------------
    def release(self, path, fh):
        return self._remove_open_file(fh)

# ------------------------------------------------------------------------------
def make_arg_parser():

    arg_setup = ArgumentSetup()
    arg_setup.with_repo_names = True
    arg_setup.existing_repos = True
    arg_setup.at_least_one_repo = True
    arg_setup.with_mount_source = True
    arg_setup.with_mount_point = True

    parser = make_argument_parser(
        os.path.basename(__file__),
        'relfs fuse filesystem driver',
        arg_setup
    )
    return parser

# ------------------------------------------------------------------------------
def main():
    logging.basicConfig()
    options = make_arg_parser().parse_args()
    fuse.FUSE(
        RelFuseDriver(options),
        options.mount_point,
        nothreads=True,
        nonempty=True,
        foreground=True)

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
# ------------------------------------------------------------------------------
