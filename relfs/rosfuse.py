#!/usr/bin/env python
#coding utf8
# ------------------------------------------------------------------------------
import os
import sys
import time
import fuse
import errno
import logging
import argparse
import contextlib
import paramiko # pip install paramiko
# ------------------------------------------------------------------------------
class SFTPSession(object):
    # --------------------------------------------------------------------------
    @staticmethod
    def _ssh_config_paths():
        return [
            os.path.join(os.path.expanduser("~"), ".ssh", "config"),
            "/etc/ssh/ssh_config"
        ]

    # --------------------------------------------------------------------------
    def __init__(self, options):
        self._ssh_config = paramiko.config.SSHConfig()

        for path in self._ssh_config_paths():
            if os.path.isfile(path):
                with contextlib.closing(open(path,"rt")) as config_file:
                    self._ssh_config.parse(config_file)

        host_options = self._ssh_config.lookup(options.hostname)

        self._ssh_client = paramiko.SSHClient()
        self._ssh_client.load_system_host_keys()
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        kwargs = {
            "hostname": host_options.get("hostname", options.hostname),
            "username": host_options.get("user", None),
            "port": int(host_options.get("port", 22)),
            "timeout": 5, # seconds
            "auth_timeout": 15, # seconds
            "allow_agent": options.allow_agent,
            "gss_auth": False,
            "gss_kex": False,
            "look_for_keys": False,
            "compress": False
        }


        connected = False
        if not options.password_only:
            try:
                self._ssh_client.connect(
                    key_filename = host_options.get("identityfile", None),
                    **kwargs)
                connected = True
            except paramiko.SSHException:
                for key_file in host_options.get("identityfile", []):
                    try:
                        self._ssh_client.connect(
                            pkey = paramiko.RSAKey.from_private_key_file(
                                key_file),
                            **kwargs)
                        connected = True
                        break
                    except paramiko.AuthenticationException:
                        pass

        if not connected:
            try:
                import getpass
                fmt = "enter password for `%(username)s@%(hostname)s': "
                self._ssh_client.connect(
                    password = getpass.getpass(fmt % kwargs),
                    **kwargs)
                connected = True
            except paramiko.AuthenticationException:
                pass
            except ImportError:
                pass

        self._sftp_client = None
        if connected:
            self._sftp_client = self._ssh_client.open_sftp()
            self._sftp_client.chdir(options.remote_prefix)

    # --------------------------------------------------------------------------
    def __del__(self):
        self._ssh_client.close()

    # --------------------------------------------------------------------------
    def normal_path(self, remote_path):
        if self._sftp_client:
            return self._sftp_client.normalize(remote_path)

    # --------------------------------------------------------------------------
    def stat_remote(self, remote_path):
        if self._sftp_client:
            return self._sftp_client.stat(remote_path)

    # --------------------------------------------------------------------------
    def open_remote(self, remote_path):
        if self._sftp_client:
            return self._sftp_client.file(remote_path, mode="r")

# ------------------------------------------------------------------------------
class SFTPSessionManager(object):
    # --------------------------------------------------------------------------
    def __init__(self, options):
        self._options = options
        self._sftp_session = None
    # --------------------------------------------------------------------------
    def get_session(self):
        if not self._sftp_session:
            self._sftp_session = SFTPSession(self._options)
        return self._sftp_session

    # --------------------------------------------------------------------------
    def cleanup_sessions(self):
        del self._sftp_session
        self._sftp_session = None

# ------------------------------------------------------------------------------
class RoSFuseItem(object):
    # --------------------------------------------------------------------------
    def __init__(self):
        pass
    # --------------------------------------------------------------------------
    def find_item(self, split_path):
        if not split_path or split_path == ["."]:
            return self
# ------------------------------------------------------------------------------
class RoSFuseFile(object):
    # --------------------------------------------------------------------------
    def __init__(self, parent, split_path):
        self._parent = parent
        self._session = parent.get_session()
        self._path = self._session.normal_path(os.path.join(*split_path))
        self._stat = self._session.stat_remote(self._path)
        self._file = self._session.open_remote(self._path)
        self._file.prefetch()

    # --------------------------------------------------------------------------
    def __del__(self):
        try:
            self._file.close()
        except AttributeError:
            pass

    # --------------------------------------------------------------------------
    def mode(self):
        return 0o100440
    # --------------------------------------------------------------------------
    def size(self):
        return self._stat.st_size
    # --------------------------------------------------------------------------
    def read(self, length, offset):
        self._file.seek(offset);
        return self._file.read(length)

# ------------------------------------------------------------------------------
class RoSFuseRoot(RoSFuseItem, SFTPSessionManager):
    # --------------------------------------------------------------------------
    def __init__(self, options):
        RoSFuseItem.__init__(self)
        SFTPSessionManager.__init__(self, options)
    # --------------------------------------------------------------------------
    def find_item(self, split_path):
        if not split_path or split_path == ["."]:
            return self

        try:
            return RoSFuseFile(self, split_path)
        except IOError:
            pass

    # --------------------------------------------------------------------------
    def mode(self):
        return 0o40440
    # --------------------------------------------------------------------------
    def size(self):
        return 0
    # --------------------------------------------------------------------------
    def read(self, length, offset):
        return str()

# ------------------------------------------------------------------------------
class RoSFuse(fuse.Operations):
    # --------------------------------------------------------------------------
    def __init__(self, options):
        self._options = options
        self._mount_time = time.time()
        self._root = RoSFuseRoot(options)
        self._open_files = dict()

    # --------------------------------------------------------------------------
    def _update(self):
        pass

    # --------------------------------------------------------------------------
    def find_entry(self, path):
        split_path = filter(bool, path.lstrip(os.sep).split(os.sep))
        item = self._root.find_item(split_path)
        if item is not None:
            return item
        raise fuse.FuseOSError(errno.ENOENT)

    # --------------------------------------------------------------------------
    def access(self, path, mode):
        self._update()
        if mode & os.R_OK:
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
    def getattr(self, path, fh=None):
        self._update()
        item = self.find_entry(path)
        return {
            "st_size": item.size(),
            "st_mode": item.mode(),
            "st_uid": os.getuid(),
            "st_gid": os.getgid(),
            "st_nlink": 1,
            "st_atime": time.time(),
            "st_mtime": time.time(),
            "st_ctime": self._mount_time
        }

    # --------------------------------------------------------------------------
    def readdir(self, path, fh):
        self._update()
        yield "."
        yield ".."

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
    def _get_free_fd(self):
        try:
            return max(self._open_files, key=self._open_files.get)
        except ValueError:
            return 3

    # --------------------------------------------------------------------------
    def open(self, path, flags):
        self._update()
        item = self.find_entry(path)

        fd = self._get_free_fd()
        self._open_files[fd] = item
        return fd

    # --------------------------------------------------------------------------
    def create(self, path, mode, fi=None):
        self._update()
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def read(self, path, length, offset, fh):
        self._update()
        try:
            return self._open_files[fh].read(length, offset)
        except KeyError:
            raise fuse.FuseOSError(errno.EBADF)

    # --------------------------------------------------------------------------
    def write(self, path, buf, offset, fh):
        self._update()
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def truncate(self, path, length, fh=None):
        self._update()
        raise fuse.FuseOSError(errno.EROFS)

    # --------------------------------------------------------------------------
    def release(self, path, fh):
        self._update()
        del self._open_files[fh]

    # --------------------------------------------------------------------------
    def flush(self, path, fh):
        self._update()

    # --------------------------------------------------------------------------
    def fsync(self, path, fdatasync, fh):
        self._update()

# ------------------------------------------------------------------------------
class RoSFuseArgParser(argparse.ArgumentParser):
    # --------------------------------------------------------------------------
    @staticmethod
    def _mountable_directory(arg):
        if not os.path.isdir(arg):
            msg = "'%s' is not a directory path" % (arg)
            raise argparse.ArgumentTypeError(msg)
        return os.path.realpath(arg)

    # --------------------------------------------------------------------------
    def __init__(self):
        argparse.ArgumentParser.__init__(
            self,
            prog="rosfusetp",
            description="""
                Read-only FUSE file-system driver,
                allowing to read known files over SFTP
            """
        )
        self.add_argument(
            "--mount-point", "-m",
            dest="mount_point",
            type=self._mountable_directory,
            default=None,
            action="store",
            help="""Specifies the file-system mount-point path."""
        )

        self.add_argument(
            "--host", "-H",
            dest="hostname",
            type=str,
            default=None,
            action="store",
            help="""Specifies the remote host; can be SSH host config entry."""
        )

        self.add_argument(
            "--allow-agent", "-A",
            dest="allow_agent",
            default=False,
            action="store_true",
            help="""Use the SSH key agent."""
        )

        self.add_argument(
            "--password-only", "-P",
            dest="password_only",
            default=True, # TODO: False
            action="store_true",
            help="""Try only password authentication."""
        )

        self.add_argument(
            "--prefix", "-p",
            dest="remote_prefix",
            type=str,
            default=None,
            action="store",
            help="""The remote host directory prefix"""
        )

# ------------------------------------------------------------------------------
def main():
    logging.basicConfig()
    options = RoSFuseArgParser().parse_args()
    fuse.FUSE(
        RoSFuse(options),
        options.mount_point,
        nothreads=True,
        foreground=True
    )
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
# ------------------------------------------------------------------------------
