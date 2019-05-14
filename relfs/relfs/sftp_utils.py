#coding utf8
# ------------------------------------------------------------------------------
import os
import sys
import errno
import logging
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
    def __init__(self, parent, options):
        self._ssh_config = paramiko.config.SSHConfig()

        for path in self._ssh_config_paths():
            if os.path.isfile(path):
                with contextlib.closing(open(path,"rt")) as config_file:
                    self._ssh_config.parse(config_file)

        host_options = self._ssh_config.lookup(options.hostname)
        
        self._ssh_client = paramiko.SSHClient()
        self._ssh_client.load_system_host_keys()
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        connect_kwargs = {
            "hostname": host_options.get("hostname", options.hostname),
            "username": host_options.get("user", None),
            "port": int(host_options.get("port", 22)),
            "timeout": 5, # seconds
            "auth_timeout": 15, # seconds
            "allow_agent": options.allow_agent,
            "gss_auth": False,
            "gss_kex": False,
            "look_for_keys": False,
            "compress": True
        }

        
        connected = False
        if not options.password_only:
            try:
                self._ssh_client.connect(
                    key_filename = host_options.get("identityfile", None),
                    **connect_kwargs)
                connected = True
            except paramiko.SSHException:
                for key_file in host_options.get("identityfile", []):
                    try:
                        try:
                            self._ssh_client.connect(
                                pkey = paramiko.RSAKey.from_private_key_file(
                                    key_file),
                                **connect_kwargs)
                        except paramiko.PasswordRequiredException:
                            prm_fmt = "enter passphrase for key file `%s': "
                            prompt = prm_fmt % (key_file)
                            self._ssh_client.connect(
                                pkey = paramiko.RSAKey.from_private_key_file(
                                    key_file,
                                    password = parent.get_password(prompt)),
                                **connect_kwargs)

                        connected = True
                        break
                    except paramiko.AuthenticationException:
                        parent.forget_password()

        if not connected:
            try:
                prm_fmt = "enter password for `%(username)s@%(hostname)s': "
                prompt = prm_fmt % connect_kwargs
                self._ssh_client.connect(
                    password = parent.get_password(prompt),
                    **connect_kwargs)
                connected = True
            except paramiko.AuthenticationException:
                parent.forget_password()

        self._sftp_client = None
        if connected:
            self._sftp_client = self._ssh_client.open_sftp()
            self._sftp_client.chdir(options.remote_prefix)

    # --------------------------------------------------------------------------
    def __del__(self):
        if self._sftp_client:
            self._sftp_client.close()
        self._ssh_client.close()

    # --------------------------------------------------------------------------
    def report_disconnected(self, remote_path):
        raise IOError(errno.ENETRESET)
    # --------------------------------------------------------------------------
    def normal_path(self, remote_path):
        if self._sftp_client:
            return self._sftp_client.normalize(remote_path)
        return self.report_disconnected()
    # --------------------------------------------------------------------------
    def file_size(self, remote_path):
        if self._sftp_client:
            return self._sftp_client.stat(remote_path).st_size
        return self.report_disconnected()
    # --------------------------------------------------------------------------
    def open_file(self, remote_path):
        if self._sftp_client:
            return self._sftp_client.file(remote_path, mode="r")
        return self.report_disconnected()
# ------------------------------------------------------------------------------
class SFTPFileReader(object):
    # --------------------------------------------------------------------------
    def __init__(self, options):
        self._options = options
        self._password = None
        self._sftp_session = None
        self._open_files = dict()
    # --------------------------------------------------------------------------
    def get_password(self, prompt):
        if not self._password:
            try:
                import getpass
                self._password = getpass.getpass(prompt)
            except ImportError:
                pass
        return self._password

    # --------------------------------------------------------------------------
    def forget_password(self):
        self._password = None

    # --------------------------------------------------------------------------
    def _get_session(self, force_new = False):
        if force_new or not self._sftp_session:
            if self._sftp_session is not None:
                del self._sftp_session
            self._sftp_session = SFTPSession(self, self._options)
        return self._sftp_session

    # --------------------------------------------------------------------------
    def _call_session(self, function):
        try:
            return function(self._get_session())
        except:
            return function(self._get_session(force_new = True))

    # --------------------------------------------------------------------------
    def file_size(self, remote_path):
        try:
            return self._open_files[remote_path].stat().st_size
        except:
            return self._call_session(lambda s: s.file_size(remote_path))

    # --------------------------------------------------------------------------
    def open_file(self, remote_path):
        rf = self._call_session(lambda s: s.open_file(remote_path))
        sz = rf.stat().st_size
        rf.prefetch(sz)
        self._open_files[remote_path] = rf
        return remote_path

    # --------------------------------------------------------------------------
    def _do_read_file(self, remote_path, length, offset):
        rf = self._open_files[remote_path]
        rf.seek(offset)
        return rf.read(length)

    # --------------------------------------------------------------------------
    def read_file(self, remote_path, length, offset):
        try:
            return self._do_read_file(remote_path, length, offset)
        except:
            self.open_file(remote_path)
            return self._do_read_file(remote_path, length, offset)

    # --------------------------------------------------------------------------
    def close_file(self, remote_path):
        try:
            del self._open_files[remote_path]
            return True
        except KeyError:
            return False

# ------------------------------------------------------------------------------
