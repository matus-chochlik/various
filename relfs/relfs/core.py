# coding=utf-8
#------------------------------------------------------------------------------#
import os
import sys
import json
import shutil
import hashlib
import resource
import datetime
import getpass
#------------------------------------------------------------------------------#
from .config import load_config, save_config, __config
from .objects import init_database, open_database
from .error import RelFsError
#------------------------------------------------------------------------------#
_version_numbers= (0,1,0)
#------------------------------------------------------------------------------#
def _mkdir_p(os_path):
    try: os.makedirs(os_path)
    except OSError as os_error:
        if not(os_error.errno == os.errno.EEXIST and os.path.isdir(os_path)):
            raise
#------------------------------------------------------------------------------#
def make_file_hash(file_path):
    hash_obj = hashlib.sha256()
    chunk_size = resource.getpagesize()
    with open(file_path, "rb") as hashed:
        for chunk in iter(lambda: hashed.read(chunk_size), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()
#------------------------------------------------------------------------------#
class Repository(object):
    #--------------------------------------------------------------------------#
    @staticmethod
    def make_default_config(name, options):
        return {
            "compress": options.compress
        }
    #--------------------------------------------------------------------------#
    @staticmethod
    def initialize(config_type, name, os_path, options):
        if os.path.exists(os_path):
            if os.path.isdir(os_path):
                if len(os.listdir(os_path)) > 0:
                    raise RelFsError(
                        "repository directory '%s' is not empty" %
                        os_path)
            else:
                raise RelFsError(
                        "file '%s' exists and is not a directory" %
                        os_path)
        else:
            _mkdir_p(os_path)

        repo_config = Repository.make_default_config(name, options)

        with open(os.path.join(os_path, "config"), "wt") as config_file:
            json.dump(repo_config, config_file)

        init_database(os_path, repo_config)

        global_config = load_config(config_type)
        global_config.repositories[name] = {"path": os_path}
        save_config(config_type, global_config)

    #--------------------------------------------------------------------------#
    def __init__(self, name, config, read_only):
        self._name = name
        self._user = getpass.getuser()
        try: self._metadata = config.repositories[name]
        except KeyError:
            raise RelFsError("'%s' is not a relfs repository" % name)

        self._repo_config = self.load_config()
        self._database = open_database(
            self._metadata["path"],
            self._repo_config,
            read_only)

    #--------------------------------------------------------------------------#
    def __repr__(self):
        return "<relfs://%(path)s>" % {"path": self._metadata["path"]}
    #--------------------------------------------------------------------------#
    def __str__(self):
        return "<relfs:%(name)s>" % {"name": self._name}
    #--------------------------------------------------------------------------#
    def name(self):
        return self._name
    #--------------------------------------------------------------------------#
    def prefix(self):
        return self._metadata["path"]
    #--------------------------------------------------------------------------#
    def config_file_path(self):
        return os.path.join(self.prefix(), "config")
    #--------------------------------------------------------------------------#
    def open_config(self):
        return open(self.config_file_path(), "rt")
    #--------------------------------------------------------------------------#
    def load_config(self):
        with self.open_config() as config_file:
            return json.load(config_file)
    #--------------------------------------------------------------------------#
    def objects_dir_path(self):
        return os.path.join(self.prefix(), "objects")
    #--------------------------------------------------------------------------#
    def object_dir_path(self, obj_hash):
        return os.path.join(self.objects_dir_path(), obj_hash[:3])
    #--------------------------------------------------------------------------#
    def object_file_name(self, obj_hash):
        return obj_hash[3:]
    #--------------------------------------------------------------------------#
    def object_file_path(self, obj_hash):
        return os.path.join(
            self.object_dir_path(obj_hash),
            self.object_file_name(obj_hash)
        )

    #--------------------------------------------------------------------------#
    @staticmethod
    def obj_hash_regex():
        import re
        return re.compile("^\s*([0-9a-f]+)\s*$")
    #--------------------------------------------------------------------------#
    def valid_object_hash(self, something):
        try:
            _regex = self._obj_hash_reg_ex
        except AttributeError:
            _regex = self._obj_hash_reg_ex = self.obj_hash_regex()

        match = _regex.match(something)
        if match:
            return match.group(1)
    #--------------------------------------------------------------------------#
    def context(self):
        return self._database.context()

    #--------------------------------------------------------------------------#
    def commit(self):
        self._database.commit()

    #--------------------------------------------------------------------------#
    def checkin_file(self, os_path, display_name=None):
        name_parts = os.path.splitext(os.path.basename(os_path))

        if not display_name:
            display_name = name_parts[0]

        extensions = '.'.join(name_parts[1:])

        try:
            obj_hash = make_file_hash(os_path)
            dir_path = self.object_dir_path(obj_hash)
            _mkdir_p(dir_path)
            obj_path = os.path.join(dir_path, self.object_file_name(obj_hash))

            # copy the file into the repo.
            shutil.copyfile(os_path, obj_path)

            # insert intial information
            file_stat = os.stat(obj_path)

            new_obj = self.context().add_file_object_info(
                obj_hash,
                display_name,
                extensions)

            return new_obj

        except IOError as io_error:
            raise RelFsError(str(io_error))

    #--------------------------------------------------------------------------#
    def all_objects(self):
        obj_dir = self.objects_dir_path()
        for prefix, dirs, files in os.walk(obj_dir):
            for file_name in files:
                file_path = os.path.join(prefix, file_name)
                if os.path.isfile(file_path):
                    rel_path = os.path.relpath(file_path, obj_dir)
                    yield (
                        str().join(rel_path.split('/')),
                        file_path
                    )

#------------------------------------------------------------------------------#
def open_repository(repo_name, config = __config()):
    return Repository(repo_name, config, read_only=False)
#-------------------------------------------------------------------------------
def read_repository(repo_name, config = __config()):
    return Repository(repo_name, config, read_only=True)
#------------------------------------------------------------------------------#
