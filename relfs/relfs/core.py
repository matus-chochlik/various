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
from .database import open_database
from .error import RelFsError
from .metadata import add_file_metadata
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
            "local_db": options.db_host is None,
            "db_user" : options.db_user or getpass.getuser(),
            "db_host" : options.db_host or "localhost",
            "db_port" : options.db_port or 5432,
            "database": options.database or "relfs",
            "schema": options.schema or "relfs"
        }
    #--------------------------------------------------------------------------#
    @staticmethod
    def initialize(config_type, name, os_path, options):
        if os.path.exists(os_path):
            if os.path.isdir(os_path):
                if len(os.listdir(os_path)) > 0:
                    raise RelFsError("repository directory '%s' is not empty" % os_path)
            else:
                raise RelFsError("file '%s' exists and is not a directory" % os_path)
        else:
            _mkdir_p(os_path)

        with open(os.path.join(os_path, "config"), "wt") as config_file:
            json.dump(Repository.make_default_config(name, options), config_file)

        global_config = load_config(config_type)
        global_config.repositories[name] = {"path": os_path}
        save_config(config_type, global_config)
    #--------------------------------------------------------------------------#
    def __init__(self, name, config):
        self._name = name
        self._user = getpass.getuser()
        try: self._metadata = config.repositories[name]
        except KeyError:
            raise RelFsError("'%s' is not a relfs repository" % name)
        self._repo_config = self.load_config()
        self._database = open_database(self._repo_config)

    #--------------------------------------------------------------------------#
    def __repr__(self):
        return "<relfs://%(path)s>" % {"path": self._metadata.path}
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
    def db_query(self, select_statement):
        cursor = self._db_conn.cursor()
        cursor.execute(select_statement)
        row = cursor.fetchone()
        while row:
            yield row
            row = cursor.fetchone()
        cursor.close()
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

            new_obj = self._database.set_object(obj_hash)
            new_obj.file.date = datetime.date.fromtimestamp(file_stat.st_mtime)
            new_obj.file.size = file_stat.st_size
            new_obj.file.display_name = display_name
            new_obj.file.extensions = extensions
            new_obj.apply()

            add_file_metadata(new_obj, os_path, obj_path, obj_hash)

            # return the object
            return RepositoryFileObject(self, obj_hash)
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
    #--------------------------------------------------------------------------#
    def refill_database(self):
        for obj_hash, obj_path in self.all_objects():
            file_stat = os.stat(obj_path)

            db_obj = self._database.set_object(obj_hash)
            db_obj.file.hash = obj_hash
            db_obj.file.size = file_stat.st_size
            db_obj.file.date = datetime.date.fromtimestamp(file_stat.st_mtime)
            db_obj.apply()

            add_file_metadata(db_obj, obj_path, obj_path, obj_hash)


    #--------------------------------------------------------------------------#
    def object_display_name(self, obj_hash):
        return obj_hash #TODO
    #--------------------------------------------------------------------------#
    def set_object_display_name(self, obj_hash, display_name):
        db_obj = self._database.set_object(obj_hash)
        db_obj.file.display_name = display_name
        db_obj.apply()
    #--------------------------------------------------------------------------#
    def add_object_tags(self, obj_hash, tag_list):
        pass
#------------------------------------------------------------------------------#
def open_repository(repo_name, config = __config()):
    return Repository(repo_name, config)
#------------------------------------------------------------------------------#
class RepositoryFileObject(object):
    #--------------------------------------------------------------------------#
    def __init__(self, repo, obj_hash):
        self._repo = repo
        self._obj_hash = obj_hash
    #--------------------------------------------------------------------------#
    def __repr__(self):
        return "<relfs://%(repo)s/%(hash)s>" % {
            "repo": self._repo.objects_dir_path(),
            "hash": self._obj_hash
        }
    #--------------------------------------------------------------------------#
    def __str__(self):
        return "<relfs:%(repo)s/%(name)s>" % {
            "repo": self._repo.name(),
            "name": self.display_name()
        }
    #--------------------------------------------------------------------------#
    def path_in_repository(self):
        return self._repo.object_file_path(self._obj_hash)
    #--------------------------------------------------------------------------#
    def display_name(self):
        return self._repo.object_display_name(self._obj_hash)
    #--------------------------------------------------------------------------#
    def set_display_name(self, name):
        self._repo.set_object_display_name(self._obj_hash, name)
    #--------------------------------------------------------------------------#
    def add_tags(self, tag_list):
        self._repo.add_object_tags(self._obj_hash, tag_list)
#------------------------------------------------------------------------------#
